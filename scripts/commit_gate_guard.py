"""Commit Gate Guard — requires explicit approval token (.commit-approved) or interactive prompt before commit.

Selftest: python scripts/commit_gate_guard.py --selftest
Hook check: python scripts/commit_gate_guard.py --check
"""
from __future__ import annotations
import sys
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent.parent
APPROVAL_TOKEN = ROOT / ".commit-approved"

def check_commit_authorized(max_age_seconds: int = 300) -> bool:
    if not APPROVAL_TOKEN.exists():
        return False
    mtime = APPROVAL_TOKEN.stat().st_mtime
    age = time.time() - mtime
    return age <= max_age_seconds

def check_authorized() -> int:
    """Exit code for the pre-commit hook: 0 when a fresh token exists, 1 otherwise.

    A stale token does not authorize: the token is minted by scripts/close.py
    immediately before its own commit, so anything older than max_age_seconds
    is a leftover from an earlier, already-finished session.
    """
    if check_commit_authorized():
        return 0
    print("commit_gate_guard: no fresh .commit-approved token — commit blocked.",
          file=sys.stderr)
    print("Mint one by closing the session through scripts/close.py (it writes "
          ".commit-approved after validation and before its commit), or create "
          "it explicitly if you are committing outside close.py.", file=sys.stderr)
    return 1


def selftest():
    print("Running Commit Gate Guard selftest...")
    if APPROVAL_TOKEN.exists():
        APPROVAL_TOKEN.unlink()
    assert not check_commit_authorized(), "Authorized without token!"

    APPROVAL_TOKEN.write_text("approved", encoding="utf-8")
    assert check_commit_authorized(), "Failed to authorize with fresh token!"

    APPROVAL_TOKEN.unlink()
    print("Commit Gate Guard selftest PASSED.")
    return True

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--check" in sys.argv:
        sys.exit(check_authorized())
    else:
        print("Usage: python scripts/commit_gate_guard.py [--selftest|--check]")
