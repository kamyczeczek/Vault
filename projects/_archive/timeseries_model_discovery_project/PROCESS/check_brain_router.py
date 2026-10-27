#!/usr/bin/env python3
"""
check_brain_router.py — LIVENESS gate for the brain router.

Every other gate in this workspace verifies internal consistency (catalogs
match disk, invariants hold, inboxes empty). None of them verify that the
thing being maintained is actually reachable. This one does.

AUDIT-2026-09-16 Finding 2: `python ask.py --self-test` exited 1 for an
unknown period while nothing ran it — the router silently misrouted
queries to skills_brain, and 3/5 test queries passed only by default
fallback because icm_brain happened to be first in brain_router.md.

Contract (fail-loud):
  exit 0  router self-test passes (all queries route to the expected brain
          AND dispatch to that brain returns exit 0)
  exit 1  self-test failed — routing is broken, answers would be wrong
  exit 2  the router or its table is missing/unrunnable (hard failure)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ASK = REPO_ROOT / "ask.py"


def main() -> int:
    if not ASK.is_file():
        print("[brain_router] FAIL: ask.py missing at", ASK, file=sys.stderr)
        return 2

    # Run the router's own self-test as a subprocess — exactly as a caller
    # would. The self-test covers: routing table parseable, each canned
    # query matches the expected brain by keyword score (not default
    # fallback), and dispatch to icm_brain returns exit 0.
    r = subprocess.run(
        [sys.executable, str(ASK), "--self-test"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=120,
    )
    if r.returncode != 0:
        print(f"[brain_router] FAIL: ask.py --self-test exit={r.returncode}",
              file=sys.stderr)
        for line in (r.stdout + r.stderr).strip().splitlines():
            print(f"    {line}", file=sys.stderr)
        return 1

    print("[brain_router] OK — router self-test passes, all brains reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
