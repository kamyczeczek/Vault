#!/usr/bin/env python3
"""Weekly workspace audit — read-only scorecard.

Produces a ranked pass/fail report covering:
- map/state freshness and routing
- stage contract validity
- graph digest consistency
- INBOX/manifest hygiene
- reflection candidate health
- eviction audit trail

Usage:
    python scripts/audit_workspace.py
    python scripts/audit_workspace.py --json
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parent.parent
NOW = datetime.now(timezone.utc).isoformat()


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""
    rank: int = 1


@dataclass
class Scorecard:
    checks: List[Check] = field(default_factory=list)
    generated_at: str = NOW
    workspace: str = str(ROOT)

    def add(self, name: str, passed: bool, detail: str = "", rank: int = 1) -> None:
        self.checks.append(Check(name=name, passed=passed, detail=detail, rank=rank))

    def summary(self) -> str:
        lines = [
            "# Workspace audit scorecard",
            f"- generated: {self.generated_at}",
            f"- workspace: {self.workspace}",
            "",
        ]
        failed = [c for c in self.checks if not c.passed]
        if not failed:
            lines.append("You are not crazy. All checks passed.")
        else:
            lines.append(
                f"A little drift is back. {len(failed)} of {len(self.checks)} checks failed."
            )
        lines.append("")
        lines.append("| Rank | Check | Status | Detail |")
        lines.append("|------|-------|--------|--------|")
        for c in sorted(self.checks, key=lambda x: (x.rank, x.name)):
            status = "PASS" if c.passed else "FAIL"
            lines.append(f"| {c.rank} | {c.name} | {status} | {c.detail} |")
        lines.append("")
        if failed:
            lines.append("Ranked fixes (not applied):")
            for i, c in enumerate(sorted(failed, key=lambda x: (x.rank, x.name)), 1):
                lines.append(f"{i}. {c.name} — {c.detail}")
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps(
            {
                "generated_at": self.generated_at,
                "workspace": self.workspace,
                "checks": [
                    {
                        "name": c.name,
                        "passed": c.passed,
                        "detail": c.detail,
                        "rank": c.rank,
                    }
                    for c in sorted(self.checks, key=lambda x: (x.rank, x.name))
                ],
            },
            indent=2,
        )


def run(cmd: List[str], cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        shell=False,
    )


def exists(path: str) -> bool:
    return Path(path).exists() or Path(ROOT, path).exists()


def file_contains(path: str, needle: str) -> bool:
    p = Path(path)
    if not p.exists() and not (ROOT / path).exists():
        return False
    target = p if p.exists() else ROOT / path
    return needle in target.read_text(encoding="utf-8", errors="ignore")


def audit_map_state(card: Scorecard) -> None:
    claude = "CLAUDE.md"
    context = "CONTEXT.md"
    card.add(
        "Map exists",
        exists(claude),
        "CLAUDE.md present" if exists(claude) else "CLAUDE.md missing",
        rank=1,
    )
    card.add(
        "State exists",
        exists(context),
        "CONTEXT.md present" if exists(context) else "CONTEXT.md missing",
        rank=1,
    )
    card.add(
        "Map routes by intent",
        file_contains(claude, "Intent") and file_contains(claude, "Where It Routes"),
        "Route table present" if file_contains(claude, "Intent") else "Route table missing",
        rank=1,
    )
    card.add(
        "State has embedded date",
        file_contains(context, "## Daily handoff"),
        "Daily handoff block present" if file_contains(context, "## Daily handoff") else "Daily handoff missing",
        rank=1,
    )


def audit_stage_contracts(card: Scorecard) -> None:
    res = run(["python", "scripts/check_stage_contracts.py"])
    passed = res.returncode == 0
    detail = (res.stdout or res.stderr).strip().splitlines()[0] if (res.stdout or res.stderr) else ""
    card.add("Stage contracts valid", passed, detail or f"exit={res.returncode}", rank=2)


def audit_graph_consistency(card: Scorecard) -> None:
    res = run(["python", "knowledge/graph/watch.py", "--once"])
    passed = res.returncode == 0
    detail = (res.stdout or res.stderr).strip().splitlines()[0] if (res.stdout or res.stderr) else ""
    card.add("Graph consistency", passed, detail or f"exit={res.returncode}", rank=2)


def audit_reflection(card: Scorecard) -> None:
    res = run(["python", "scripts/check_reflection.py"])
    passed = res.returncode == 0
    detail = (res.stdout or res.stderr).strip().splitlines()[0] if (res.stdout or res.stderr) else ""
    card.add("Reflection checks", passed, detail or f"exit={res.returncode}", rank=2)


def audit_eviction(card: Scorecard) -> None:
    res = run(["python", "scripts/check_eviction.py"])
    passed = res.returncode == 0
    detail = (res.stdout or res.stderr).strip().splitlines()[0] if (res.stdout or res.stderr) else ""
    card.add("Eviction checks", passed, detail or f"exit={res.returncode}", rank=3)


def audit_manifest(card: Scorecard) -> None:
    res = run(["python", "scripts/check_manifest.py"])
    passed = res.returncode == 0
    detail = (res.stdout or res.stderr).strip().splitlines()[0] if (res.stdout or res.stderr) else ""
    card.add("Manifest/corpus hygiene", passed, detail or f"exit={res.returncode}", rank=3)


def audit_frontier(card: Scorecard) -> None:
    res = run(["python", "scripts/check_frontier.py"])
    passed = res.returncode == 0
    detail = (res.stdout or res.stderr).strip().splitlines()[0] if (res.stdout or res.stderr) else ""
    card.add("Frontier ledger integrity", passed, detail or f"exit={res.returncode}", rank=3)


def audit_inbox(card: Scorecard) -> None:
    inbox = ROOT / "INBOX"
    files = []
    if inbox.exists():
        files = [p.name for p in inbox.iterdir() if p.is_file()]
    passed = len(files) == 0
    detail = f"{len(files)} file(s) remaining" if files else "INBOX empty"
    card.add("INBOX empty", passed, detail, rank=3)


def audit_topic_coverage(card: Scorecard) -> None:
    res = run(["python", "scripts/check_topic_coverage.py"])
    passed = res.returncode == 0
    detail = (res.stdout or res.stderr).strip().splitlines()[0] if (res.stdout or res.stderr) else ""
    card.add("Topic coverage", passed, detail or f"exit={res.returncode}", rank=3)

def main() -> int:
    card = Scorecard()
    audit_map_state(card)
    audit_stage_contracts(card)
    audit_graph_consistency(card)
    audit_reflection(card)
    audit_eviction(card)
    audit_manifest(card)
    audit_frontier(card)
    audit_inbox(card)
    audit_topic_coverage(card)

    as_json = "--json" in sys.argv or "-j" in sys.argv
    if as_json:
        print(card.to_json())
    else:
        print(card.summary())

    return 0 if all(c.passed for c in card.checks) else 2


if __name__ == "__main__":
    raise SystemExit(main())
