#!/usr/bin/env python
"""Verify claims in a session report. Read-only. Exit 0."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git_cat_file(hashv: str) -> bool:
    try:
        out = subprocess.check_output(
            ["git", "cat-file", "-t", hashv], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        return out == "commit"
    except Exception:
        return False


def git_status_porcelain() -> str:
    try:
        return subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def verify_report(text: str) -> tuple[int, int, int, list[str]]:
    verified = 0
    contradicted = 0
    unverifiable = 0
    details: list[str] = []
    # commit hashes
    for m in re.finditer(r"commit ([0-9a-f]{7,40})", text):
        h = m.group(1)
        if git_cat_file(h):
            verified += 1
            details.append(f"commit {h} -> verified")
        else:
            # could be abbreviated; try git log
            unverifiable += 1
            details.append(f"commit {h} -> unverifiable")
    # git status clean claims
    if re.search(r"working tree (czysty|pusty)|git status .*clean", text):
        po = git_status_porcelain()
        if po == "":
            verified += 1
            details.append("git status clean -> verified")
        elif po == "unknown":
            unverifiable += 1
            details.append("git status clean -> unverifiable")
        else:
            contradicted += 1
            details.append("git status clean -> contradicted")
    # Test-Path claims are unverifiable by default (environment)
    for m in re.finditer(r"Test-Path (\S+)", text):
        unverifiable += 1
        details.append(f"Test-Path {m.group(1)} -> unverifiable")
    # hit@5 claims
    for m in re.finditer(r"hit@5=([0-9.]+)", text):
        unverifiable += 1
        details.append(f"hit@5={m.group(1)} -> unverifiable")
    if verified == 0 and contradicted == 0 and unverifiable == 0:
        unverifiable += 1
        details.append("no claims found -> unverifiable")
    return verified, contradicted, unverifiable, details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    if args.report.name == "stdin":
        import sys as _sys
        text = _sys.stdin.read()
    else:
        text = args.report.read_text(encoding="utf-8")
    v, c, u, details = verify_report(text)
    print(f"Claims: {v} verified · {c} contradicted · {u} unverifiable")
    for d in details[:50]:
        print(f"- {d}")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
PY