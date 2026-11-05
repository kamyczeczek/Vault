#!/usr/bin/env python3
"""Restore the derived corpus into a fresh clone, then rebuild the graph.

Why this exists
---------------
`knowledge/corpus/` was deliberately untracked in c8a5f8a ("Untrack
knowledge/corpus: a derived projection is not source"). That is the right
call: the corpus is a projection of `knowledge/raw/`, not hand-authored
source, and tracking it made every re-ingest a 10,000-file diff.

But the consequence is that a fresh clone has NO corpus, so
`build_graph.py` produces `nodes 0 edges 0` and the graph tests fail with
`sqlite3.OperationalError: no such table: nodes`. Measured on 2026-09-29: a
fresh clone fails 2 of 200 tests until the corpus is restored.

This script finds the most recent commit whose tree still *contains* the
corpus and checks it back out, then rebuilds the graph. The commit is
DISCOVERED, not hardcoded: if the corpus is ever re-tracked and untracked
again, this keeps working.

What it does NOT do
-------------------
It does not re-ingest from `knowledge/raw/`. The corpus chunks carry
provenance (source, trust tier, tags) that the raw files do not, and
re-deriving them would produce a *different* corpus, not the committed one.
The committed projection is the thing under test, so it is restored exactly.

Run:  python scripts/restore_corpus.py [--check] [--force]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_REL = "knowledge/corpus"
EXPECTED_MIN_FILES = 100  # a real corpus is thousands; a stray file is not


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def corpus_file_count(path: Path) -> int:
    return len(list(path.glob("*.md"))) if path.is_dir() else 0


def last_commit_holding_corpus() -> tuple[str | None, int]:
    """Newest commit whose tree still contains corpus files.

    Walks history newest-first and returns the first commit with a non-empty
    corpus tree. The untracking commit itself has zero, so it is skipped
    automatically -- no assumption about which commit removed it.
    """
    revs = git("rev-list", "HEAD", "--", CORPUS_REL).stdout.split()
    if not revs:
        return None, 0
    for sha in revs:
        tree = git("ls-tree", "-r", "--name-only", sha, "--", CORPUS_REL).stdout
        count = len([line for line in tree.splitlines() if line.strip()])
        if count >= EXPECTED_MIN_FILES:
            subject = git("log", "-1", "--format=%s", sha).stdout.strip()
            return sha, count
    return None, 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report status only; restore nothing")
    ap.add_argument("--force", action="store_true",
                    help="re-checkout even if a corpus is already present")
    args = ap.parse_args()

    present = corpus_file_count(ROOT / CORPUS_REL)
    print(f"corpus on disk: {present} file(s)")

    if present >= EXPECTED_MIN_FILES and not args.force:
        print("OK: corpus already present; nothing to restore.")
        print("     (use --force to re-checkout the committed projection)")
        return 0

    sha, count = last_commit_holding_corpus()
    if sha is None:
        print("FAIL: no commit in history holds the corpus. The projection "
              "cannot be restored from git.", file=sys.stderr)
        print("      Re-derive it from knowledge/raw/ instead, and see "
              "ADR-0003.", file=sys.stderr)
        return 1

    subject = git("log", "-1", "--format=%s", sha).stdout.strip()
    print(f"restoring from {sha[:8]} ({count} files) — {subject}")

    if args.check:
        print("--check: nothing written.")
        return 0

    checkout = git("checkout", sha, "--", CORPUS_REL)
    if checkout.returncode:
        print(f"FAIL: git checkout failed: {checkout.stderr.strip()}",
              file=sys.stderr)
        return 1

    now = corpus_file_count(ROOT / CORPUS_REL)
    if now < EXPECTED_MIN_FILES:
        print(f"FAIL: checkout left only {now} file(s); expected a full corpus.",
              file=sys.stderr)
        return 1
    print(f"restored {now} corpus file(s)")

    print("rebuilding the graph from the restored corpus...")
    build = subprocess.run(
        [sys.executable, str(ROOT / "knowledge" / "graph" / "build_graph.py")],
        cwd=ROOT, capture_output=True, text=True)
    sys.stdout.write(build.stdout)
    sys.stderr.write(build.stderr)
    if build.returncode:
        print(f"FAIL: build_graph.py exited {build.returncode}", file=sys.stderr)
        return build.returncode

    print("\nDone. Verify with:  python -m pytest tests/test_graph_integrity.py -q")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
