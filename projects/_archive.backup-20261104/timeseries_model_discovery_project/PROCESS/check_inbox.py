#!/usr/bin/env python
"""check_inbox.py — Rule-5 enforcement gate (INBOX cleanliness at commit time).

Root workspace law (AGENTS.md Rule 5): INBOX is a transient intake folder —
processed and PURGED every session; nothing lives here. Problem
`2026-09-07_inbox-purge-lapse` found the failure mode this gate closes: a
finished session archived an ingested document byte-equal into RESEARCH/
sources/ but never purged the INBOX original — and COMMITTED it, making the
leftover durable, invisible to `git status`, and undetectable by any existing
gate (the ledger blocks on OPEN entries; check_problems cross-checks the
problem corpus; nothing looked at INBOX).

Deterministic commit-time checks (what the git index can prove):
  1. TRACKED INBOX content must be exactly the standing stub `INBOX/issues.md`
     — any other tracked file is a durable leftover (the lapse class).
  2. If `INBOX/issues.md` is staged, its staged content must carry NO entry
     below the append marker — committing an unpurged entry makes it durable.
     Unstaged below-line entries are work-in-progress, not violations.

Untracked raw drops are legal mid-session intake (visible in `git status`,
caught by the session-close census) and are NOT violations.

Exit codes: 0 = clean, 1 = violation (fail loud, with the offending items
named). Red-path validated: R1 fake tracked leftover (staged) blocked;
R2 staged below-line entry blocked; restore re-verified green.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "INBOX"
STUB = "INBOX/issues.md"
APPEND_MARKER = re.compile(r"^\s*<!--\s*Append entries below this line", re.IGNORECASE)


def git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed rc={proc.returncode}: {proc.stderr.strip()}"
        )
    return proc.stdout


def main() -> int:
    # --- check 1: tracked INBOX content = exactly the stub -------------------
    # Line-wise consumption (round-7 invariant): filenames with spaces must
    # not be whitespace-tokenized.
    tracked = [line for line in git(["ls-files", "INBOX"]).splitlines() if line]
    bad_tracked = [p for p in tracked if p.replace("\\", "/") != STUB]
    if bad_tracked:
        print("[check_inbox] FAIL: tracked non-stub content in INBOX (Rule 5):")
        for p in bad_tracked:
            print(f"  TRACKED-LEFTOVER  {p}")
        print(
            "[check_inbox] INBOX material must be purged (git rm) in the commit\n"
            "[check_inbox] that establishes its durable home — see problem\n"
            "[check_inbox] 2026-09-07_inbox-purge-lapse."
        )
        return 1

    # --- check 2: staged issues.md must have no below-line entry --------------
    staged_files = [
        line for line in git(["diff", "--cached", "--name-only"]).splitlines() if line
    ]
    if STUB in staged_files:
        staged_content = git(["show", f":{STUB}"])
        lines = staged_content.splitlines()
        marker_idx = next(
            (i for i, ln in enumerate(lines) if APPEND_MARKER.match(ln)), None
        )
        # The append marker is a multi-line HTML comment: the below-line
        # region starts after the comment CLOSES (the line containing '-->'),
        # not after the marker's first line — else the standing note's own
        # comment tail is false-flagged as an entry (caught in R2 red-path).
        if marker_idx is not None:
            close_idx = next(
                (i for i, ln in enumerate(lines[marker_idx:], start=marker_idx) if "-->" in ln),
                marker_idx,
            )
            below = [ln for ln in lines[close_idx + 1 :] if ln.strip()]
        else:
            below = []
        if below:
            print("[check_inbox] FAIL: staged INBOX/issues.md carries an unpurged")
            print("[check_inbox] entry below the append marker:")
            for ln in below:
                print(f"  UNPURGED  {ln[:100]}")
            print(
                "[check_inbox] Process the entry (problem file / RESEARCH record),\n"
                "[check_inbox] then remove it from issues.md before committing\n"
                "[check_inbox] (AGENTS.md Rule 5)."
            )
            return 1

    print(
        f"[check_inbox] OK — INBOX clean at commit time "
        f"(tracked: {len(tracked)} stub; no staged below-line entries)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
