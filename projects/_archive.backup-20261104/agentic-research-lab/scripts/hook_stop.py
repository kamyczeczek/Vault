#!/usr/bin/env python3
"""Stop hook: prevent completion when deterministic quality gates fail.

Exit 0 permits termination; exit 2 requests another agent turn. The hook is
intentionally fail-closed when the quality suite itself cannot start.
"""
from __future__ import annotations
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    result = subprocess.run(
        [sys.executable, "scripts/quality_check.py"],
        cwd=ROOT, capture_output=True, text=True, timeout=110,
    )
    if result.returncode == 0:
        return 0
    detail = (result.stdout + "\n" + result.stderr)[-3000:]
    print("STOP BLOCKED: quality gates failed; repair before completing.\n" + detail, file=sys.stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
