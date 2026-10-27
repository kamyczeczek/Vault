#!/usr/bin/env python3
"""Verify the accepted-rule invocation path is executable and observable."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "reflection" / "events.jsonl"


def main() -> int:
    proc = subprocess.run(
        [sys.executable, "scripts/apply_rules.py", "--task", "research source analysis", "--format", "json", "--no-log"],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    if proc.returncode != 0:
        print(f"FAIL: apply_rules.py exited {proc.returncode}: {proc.stderr.strip()}", file=sys.stderr)
        return 1
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        print(f"FAIL: apply_rules.py emitted invalid JSON: {exc}", file=sys.stderr)
        return 1
    if not result.get("matched_rules"):
        print("FAIL: representative research task matched no accepted rules", file=sys.stderr)
        return 1
    if not EVENTS.exists():
        print("FAIL: reflection/events.jsonl missing; invocation telemetry is not observable", file=sys.stderr)
        return 1
    print(f"OK: heuristic binding returned {result['count']} rule(s); telemetry log exists")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
