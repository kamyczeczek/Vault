#!/usr/bin/env python3
"""Run the workspace quality gates in dependency order with evidence recording."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    # Q0 looks two levels up, at the workspace root. Every other gate resolves
    # ROOT to this repository, so a file created at the workspace root is
    # invisible to all of them — not hypothetical: it happened during the
    # restructure that produced this entry. It runs first so a dirty root costs
    # one second instead of the whole chain.
    {"id": "Q0", "name": "workspace_root_integrity",
     "cmd": [sys.executable, str(ROOT.parents[2] / "scripts" / "check_workspace_integrity.py")]},
    {"id": "Q1", "name": "state_freshness", "cmd": [sys.executable, "scripts/check_state_freshness.py"]},
    {"id": "Q2", "name": "wiring", "cmd": [sys.executable, "scripts/check_wiring.py"]},
    {"id": "Q3", "name": "manifest", "cmd": [sys.executable, "scripts/check_manifest.py"]},
    {"id": "Q4", "name": "stage_contracts", "cmd": [sys.executable, "scripts/check_stage_contracts.py"]},
    {"id": "Q5", "name": "graph_watch", "cmd": [sys.executable, "knowledge/graph/watch.py", "--once"]},
    {"id": "Q6", "name": "topic_coverage", "cmd": [sys.executable, "scripts/check_topic_coverage.py"]},
    {"id": "Q7", "name": "reflection", "cmd": [sys.executable, "scripts/check_reflection.py"]},
    {"id": "Q8", "name": "slop", "cmd": [sys.executable, "scripts/check_slop.py"]},
    {"id": "Q9", "name": "reachability", "cmd": [sys.executable, "scripts/check_reachability.py"]},
    {"id": "Q10", "name": "promotion", "cmd": [sys.executable, "scripts/check_promotion.py"]},
    {"id": "Q11", "name": "eviction", "cmd": [sys.executable, "scripts/check_eviction.py"]},
    {"id": "Q12", "name": "research_quality", "cmd": [sys.executable, "scripts/check_research_quality.py"], "warn_exit": 2},
    {"id": "Q13", "name": "heuristic_usage", "cmd": [sys.executable, "scripts/check_heuristic_usage.py"]},
    {"id": "Q14", "name": "guardrails", "cmd": [sys.executable, "scripts/check_guardrails.py"]},
    {"id": "Q15", "name": "frontier", "cmd": [sys.executable, "scripts/check_frontier.py"]},
    {"id": "Q16", "name": "citation_integrity",
     "cmd": [sys.executable, "scripts/check_citation_integrity.py"]},
    {"id": "Q17", "name": "graph_determinism",
     "cmd": [sys.executable, "scripts/check_graph_determinism.py"]},
    {"id": "Q18", "name": "dead_code",
     "cmd": [sys.executable, "scripts/check_dead_code.py"]},
    # Hard failure, promoted 2026-09-28 once the count reached zero. It began at
    # warn_exit=2 with 6,544 unbuildable chunks; the loss was recovered into
    # `library/` and the remainder proved to be hand-written chunks that were
    # never derived from a file. A recurrence is now a real regression: a
    # source that becomes unbuildable again, or an ingest that stops staging
    # what it archives. Never silence it by deleting chunks — for an authored
    # source the chunk is the only record.
    {"id": "Q19", "name": "entropy",
     "cmd": [sys.executable, "scripts/check_entropy.py"]},
    # Architectural layering (stages/ -> no ingest, graph/ -> no stage deps).
    # A checker nobody runs is documentation with a shebang; wired 2026-09-28.
    {"id": "Q20", "name": "ast_boundaries",
     "cmd": [sys.executable, "scripts/check_ast_boundaries.py"]},
]

def fingerprint_output(stdout: str, stderr: str) -> str:
    combined = (stdout + stderr).encode("utf-8", errors="replace")
    return hashlib.sha256(combined).hexdigest()[:16] + str(len(combined))


def run_gate(gate: dict) -> dict:
    cmd = gate["cmd"]
    print(f"\n$ {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return {
            "id": gate["id"],
            "name": gate["name"],
            "exit": -1,
            "stdout": "",
            "stderr": "timeout",
            "fingerprint": "timeout",
            "passed": False,
        }

    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    fp = fingerprint_output(proc.stdout, proc.stderr)

    # Treat configured warn_exit as warning, not hard failure
    warn_exit = gate.get("warn_exit")
    passed = proc.returncode == 0 or (warn_exit is not None and proc.returncode == warn_exit)

    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    return {
        "id": gate["id"],
        "name": gate["name"],
        "exit": proc.returncode,
        "stdout": stdout[:500],
        "stderr": stderr[:500],
        "fingerprint": fp,
        "passed": passed,
    }


def write_evidence(results: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gates": [
            {
                "id": r["id"],
                "name": r["name"],
                "exit": r["exit"],
                "fingerprint": r["fingerprint"],
                "passed": r["passed"],
            }
            for r in results
        ],
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"]),
        },
    }
    path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run quality gates with evidence recording")
    parser.add_argument("--json", action="store_true", help="Output machine-readable evidence")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / ".unlazy" / "evidence",
                        help="Where to write evidence files")
    args = parser.parse_args()

    results = []
    for gate in COMMANDS:
        result = run_gate(gate)
        results.append(result)
        if not result["passed"]:
            print(f"FAILED: {gate['name']} exit {result['exit']}", file=sys.stderr)
            if args.json:
                write_evidence(results, args.evidence_dir / "latest.json")
            return result["exit"]

    passed = sum(1 for r in results if r["passed"])
    print(f"\nQUALITY PASS: {passed}/{len(results)} gates passed")

    if args.json:
        write_evidence(results, args.evidence_dir / "latest.json")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
