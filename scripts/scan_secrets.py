#!/usr/bin/env python3
"""Scan files for secret/API-key patterns. Never prints key values.

Usage:
    python scripts/scan_secrets.py [--staged] [path ...]

Output per hit:  <path>:<line> [<pattern_name>]  (no values).
Exit 0 + SECRETS_CLEAN when clean, exit 1 + SECRETS_FOUND=N otherwise.
Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PATTERNS: list[tuple[str, re.Pattern]] = [
    ("sk-ant", re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}")),
    ("sk-proj", re.compile(r"sk-proj-[A-Za-z0-9_-]{8,}")),
    ("sk-orca", re.compile(r"sk-orca-[A-Za-z0-9_-]{8,}")),
    ("sk-nry", re.compile(r"sk-nry-[A-Za-z0-9_-]{8,}")),
    ("sk-XUOx", re.compile(r"sk-XUOx[A-Za-z0-9_-]{8,}")),
    ("sk-AuZF", re.compile(r"sk-AuZF[A-Za-z0-9_-]{8,}")),
    ("sk-03Jv", re.compile(r"sk-03Jv[A-Za-z0-9_-]{8,}")),
    ("sk-1e5fa", re.compile(r"sk-1e5fa[A-Za-z0-9_-]{8,}")),
    ("thk_live", re.compile(r"thk_live_[A-Za-z0-9_-]{8,}")),
    ("google-AQ", re.compile(r"AQ\.[A-Za-z0-9_-]{30,}")),
    ("github-ghp", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("github-gho", re.compile(r"gho_[A-Za-z0-9]{20,}")),
    ("github-ghs", re.compile(r"ghs_[A-Za-z0-9]{20,}")),
    ("bearer", re.compile(r"Bearer [A-Za-z0-9._\-]{20,}")),
    ("pem-private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

SKIP_SUFFIXES = {".db", ".pyc", ".so", ".dll", ".png", ".jpg", ".zip", ".jsonl"}
MAX_BYTES = 10 * 1024 * 1024


def staged_files() -> list[str]:
    p = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True,
    )
    return [l.strip() for l in p.stdout.splitlines() if l.strip()]


def scan_file(path: Path, explicit: bool) -> list[str]:
    hits: list[str] = []
    if not explicit and path.suffix.lower() in SKIP_SUFFIXES:
        return hits
    try:
        if path.stat().st_size > MAX_BYTES:
            return hits
    except OSError:
        return hits
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeDecodeError):
        return hits  # binary or unreadable — skip
    for lineno, line in enumerate(text.splitlines(), 1):
        for name, rx in PATTERNS:
            if rx.search(line):
                hits.append(f"{path.as_posix()}:{lineno} [{name}]")
                break  # one hit per line is enough
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(prog="scan_secrets.py")
    ap.add_argument("--staged", action="store_true",
                    help="scan files from `git diff --cached --name-only`")
    ap.add_argument("paths", nargs="*", help="files to scan")
    a = ap.parse_args()
    targets = list(a.paths)
    if a.staged:
        targets.extend(staged_files())
    if not targets:
        print("SECRETS_CLEAN")
        return 0
    total = 0
    for t in targets:
        p = Path(t)
        if not p.is_file():
            continue
        hits = scan_file(p, explicit=(not a.staged))
        for h in hits:
            print(h)
        total += len(hits)
    if total:
        print(f"SECRETS_FOUND={total}")
        return 1
    print("SECRETS_CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
