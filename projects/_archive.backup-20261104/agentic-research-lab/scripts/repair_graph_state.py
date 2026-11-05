#!/usr/bin/env python3
"""Diagnose and repair derived graph/reflection state without hand-editing artifacts.

Authoritative inputs are the corpus and workflow. Graph and reflections are derived.
This command is intentionally conservative: stale or non-replayable artifacts are
quarantined instead of being cosmetically restamped.
"""
from __future__ import annotations
import json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "knowledge" / "graph"
GENERATION = GRAPH / "generation.json"
DIGESTS = ROOT / "reflection" / "digests"
CANDIDATES = ROOT / "reflection" / "candidates"
STALE = ROOT / "reflection" / "stale"
LEDGER = ROOT / "reflection" / "repair_ledger.jsonl"


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run([sys.executable, *cmd], cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def generation_id() -> str:
    if GENERATION.exists():
        try:
            return str(json.loads(GENERATION.read_text(encoding="utf-8"))["generation_id"])
        except (ValueError, KeyError):
            pass
    return (GRAPH / ".graph_fingerprint").read_text(encoding="utf-8").strip()


def artifact_fp(path: Path) -> str | None:
    try:
        if path.suffix == ".jsonl":
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    return (json.loads(line).get("provenance") or {}).get("fingerprint")
        import re
        match = re.search(r"fingerprint\s*[:=]\s*([0-9a-f]{12})", path.read_text(encoding="utf-8"), re.I)
        return match.group(1) if match else None
    except (OSError, ValueError):
        return None


def log(event: dict) -> None:
    """Record an operational event as a schema-valid ledger record.

    Previously wrote bare dicts (timestamp/classification/action) that fail
    `repair_ledger.py --validate` — 65 legacy rows predate this fix and are
    grandfathered there, not rewritten. Mapping preserves the old meaning:
    quarantine actions become quarantined FailureEvents (the scar tissue
    `warn.py` retrieves), completed verifications become accepted
    ValidationRuns, unresolved failures stay proposed until linked via
    `link_repair.py`.
    """
    from repair_ledger import append as ledger_append

    action = event.get("action")
    generation = event.get("generation", "")
    if action == "quarantined":
        ledger_append("FailureEvent", {
            "layer": "harness",
            "validation_boundary": f"repair_graph_state for generation {generation}",
            "category": event.get("classification", ""),
            "issues": [{
                "kind": event.get("classification", ""),
                "repair": "quarantine",
                "target": event.get("artifact", ""),
            }],
            "detail": str(event.get("detail", ""))[:500],
        }, state="quarantined")
    elif event.get("classification") == "repair_complete":
        ledger_append("ValidationRun", {
            "generation": generation,
            "quarantined": event.get("quarantined", 0),
            "detail": "repair pass verified",
        }, state="accepted")
    else:
        ledger_append("FailureEvent", {
            "layer": "harness",
            "validation_boundary": f"repair_graph_state for generation {generation}",
            "category": event.get("classification", ""),
            "issues": [{
                "kind": event.get("classification", ""),
                "repair": "unresolved",
                "target": event.get("artifact", ""),
            }],
            "detail": str(event.get("detail", ""))[:500],
        }, state="proposed")


def main() -> int:
    current = generation_id()
    if not current:
        print("FAIL: graph generation is unavailable", file=sys.stderr)
        return 2
    print(f"[repair] generation={current}")
    code, output = run(["knowledge/graph/watch.py", "--once"])
    if code:
        print("[repair] graph stale or inconsistent, rebuilding from corpus")
        code, output = run(["knowledge/graph/build_graph.py"])
        print(output)
        if code:
            log({"classification": "graph_rebuild", "action": "failed", "detail": output[-2000:]})
            return code
        current = generation_id()
        code, output = run(["knowledge/graph/watch.py", "--once"])
        if code:
            print(output, file=sys.stderr)
            log({"classification": "graph_rebuild", "action": "verification_failed", "generation": current})
            return code

    STALE.mkdir(parents=True, exist_ok=True)
    moved = 0
    for directory in (DIGESTS, CANDIDATES):
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if path.suffix not in {".md", ".jsonl"}:
                continue
            fp = artifact_fp(path)
            if fp and fp != current:
                target_dir = STALE / current
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / path.name
                shutil.move(str(path), str(target))
                log({"artifact": str(path.relative_to(ROOT)), "classification": "stale_provenance", "action": "quarantined", "generation": current})
                moved += 1

    code, output = run(["scripts/check_reflection.py"])
    print(output)
    if code:
        # Validation is fail-closed. Move known invalid or orphaned artifacts as a
        # unit, preserving evidence for later regeneration rather than editing JSON.
        names = set()
        for line in output.splitlines():
            if line.startswith("FAIL: ") and ".md:" in line:
                names.add(line.split("FAIL: ", 1)[1].split(".md:", 1)[0] + ".md")
        if names:
            target_dir = STALE / current
            target_dir.mkdir(parents=True, exist_ok=True)
            for name in sorted(names):
                stem = Path(name).stem
                for candidate in (DIGESTS / name, CANDIDATES / (stem + ".jsonl")):
                    if candidate.exists():
                        target = target_dir / candidate.name
                        if not target.exists():
                            shutil.move(str(candidate), str(target))
                            log({"artifact": str(candidate.relative_to(ROOT)), "classification": "invalid_route_or_orphan", "action": "quarantined", "generation": current})
                            moved += 1
            code, output = run(["scripts/check_reflection.py"])
            print(output)
        if code:
            log({"classification": "reflection_validation", "action": "blocked", "generation": current, "detail": output[-2000:]})
            return code
    print(f"[repair] complete: quarantined={moved}")
    log({"classification": "repair_complete", "action": "verified", "generation": current, "quarantined": moved})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
