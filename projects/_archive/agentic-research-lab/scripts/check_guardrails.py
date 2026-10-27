#!/usr/bin/env python3
"""Regression checks for action, side-effect, and budget guardrails."""
from __future__ import annotations
import hashlib, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
GUARD = [sys.executable, "scripts/guard_action.py"]

def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(GUARD + list(args), cwd=ROOT, capture_output=True, text=True)

def main() -> int:
    cases = [("git add .", 1), ("rm -rf /", 1), ("git push", 2), ("python -m py_compile x.py", 0)]
    for command, expected in cases:
        result = run("check-command", "--command", command)
        if result.returncode != expected:
            print(f"FAIL: {command!r}: expected {expected}, got {result.returncode}", file=sys.stderr); return 1
    for steps, limit, expected in [(2, 3, 0), (4, 3, 1)]:
        result = run("check-budget", "--steps", str(steps), "--max-steps", str(limit))
        if result.returncode != expected:
            print(f"FAIL: budget {steps}/{limit}: expected {expected}, got {result.returncode}", file=sys.stderr); return 1
    target = ROOT / "scripts" / "guard_action.py"
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    result = run("verify-file", "--path", "scripts/guard_action.py", "--sha256", digest)
    if result.returncode != 0:
        print("FAIL: known-good side-effect verification failed", file=sys.stderr); return 1
    result = run("verify-file", "--path", "scripts/guard_action.py", "--sha256", "0" * 64)
    if result.returncode == 0:
        print("FAIL: known-bad side-effect verification passed", file=sys.stderr); return 1
    print("OK: action, side-effect, and budget guardrails verified")
    return 0
if __name__ == "__main__": raise SystemExit(main())
