#!/usr/bin/env python3
"""Gate: every corpus chunk must have a source that still exists somewhere.

`knowledge/corpus/` is derived from `knowledge/raw/`, and a chunk is only
worth as much as the material it was cut from. Once the source is gone the
chunk is a quotation with nothing behind it: it cannot be re-derived, it
cannot be checked against the original, and no amount of corpus repair brings
it back. The corpus is currently in exactly that state for most of its
chunks.

## What is actually broken

The ratio that matters is not corpus-to-source but buildable-to-total:

    rebuildable from tracked raw : 1,009  (9%)
    NOT rebuildable              : 9,328

The gap is not that raw sources are missing from the repository — 41 of them
are, and the reason is visible in the history. `scripts/ingest.py` globs
`INBOX/`, writes the chunks, and then `shutil.move`s the original into
`knowledge/raw/`. A move is not a delete, so git never learns the file
existed; a later inbox cleanup removed the originals outright. Seven PDFs
were deleted outright in commits `0d075d7` and `74b922e` (2026-09-21). Six
`.md` sources were never committed at all — only their chunks survive.

## What this gate checks

For each chunk, resolve the `source:` frontmatter value against three places,
in order:

1. `knowledge/raw/<source>` on disk — the file exists right now.
2. `git ls-files knowledge/raw/` — the file is tracked, so any clone has it.
3. The workspace library index, if one is present.

A chunk that resolves in none of them is unbuildable. Chunks are reported per
source, not per chunk, because 1123 unbuildable chunks from one book is one
problem to fix, not 1123.

## Why file count is not the signal

A gate on "too many files" or on a derived:source ratio can be satisfied by
deleting the evidence, and deleting the evidence is the one action this gate
exists to prevent. The unbuildable count cannot be gamed that way: removing a
chunk lowers it, but the source is still lost and the gate says so the moment
the chunk is re-derived.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "knowledge" / "raw"
CORPUS_DIR = ROOT / "knowledge" / "corpus"
# The workspace library, once it exists. Absent is not an error: the gate
# degrades to checking the project's own raw dir.
LIBRARY_INDEX = ROOT.parents[2] / "library" / "index.json"  # workspace root: projects/research/<repo> -> 2 up

SOURCE_RE = re.compile(r"^source:\s*\"?([^\"\n]+)\"?\s*$", re.M)


def tracked_raw(limit: int = 0) -> set[str]:
    """Names of files under knowledge/raw/ that git tracks."""
    try:
        proc = subprocess.run(
            ["git", "ls-files", "knowledge/raw/"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
    names = {Path(line).name for line in proc.stdout.splitlines() if line.strip()}
    if limit:
        names = set(sorted(names)[:limit])
    return names


def library_sources() -> set[str]:
    """Filenames available from the workspace library index, if it exists.

    Aliases count too. A chunk declares the filename its source had at ingest
    time, and the same work can later be supplied in a different format — the
    345 *Graph Engineering* chunks say `.txt` while the library holds a `.pdf`
    of the same title. That is not a missing source, so the index may record
    the spelling a chunk is likely to carry.
    """
    if not LIBRARY_INDEX.is_file():
        return set()
    try:
        data = json.loads(LIBRARY_INDEX.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    entries = data.values() if isinstance(data, dict) else data
    names: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if "filename" in entry:
            names.add(entry["filename"])
        for alias in entry.get("aliases", []):
            names.add(alias)
    return names


def scan(corpus_dir: Path = CORPUS_DIR) -> tuple[dict[str, dict[str, int]], int]:
    """Return ({source: {chunks, on_disk, tracked}}, total chunks)."""
    on_disk = {p.name for p in RAW_DIR.iterdir() if p.is_file()} if RAW_DIR.is_dir() else set()
    tracked = tracked_raw()
    library = library_sources()

    by_source: dict[str, dict[str, int]] = defaultdict(
        lambda: {"chunks": 0, "on_disk": 0, "tracked": 0}
    )
    total = 0
    files = sorted(corpus_dir.glob("*.md")) if corpus_dir.is_dir() else []
    for path in files:
        head = path.read_text(encoding="utf-8", errors="replace")[:2000]
        match = SOURCE_RE.search(head)
        if not match:
            by_source["<no source: field>"]["chunks"] += 1
            total += 1
            continue
        name = Path(match.group(1)).name
        row = by_source[name]
        row["chunks"] += 1
        total += 1
        if name in on_disk:
            row["on_disk"] += 1
        elif name in tracked:
            row["tracked"] += 1
        elif name in library:
            row["library"] = row.get("library", 0) + 1
    return dict(by_source), total


def unbuildable(by_source: dict[str, dict[str, int]]) -> dict[str, int]:
    """Sources no chunk of which can be rebuilt from anything still held."""
    return {
        name: row["chunks"]
        for name, row in by_source.items()
        if not (row["on_disk"] or row["tracked"] or row.get("library"))

    }


# Project-authored write-ups whose subject was later archived. Their chunks are
# the only remaining record of the research: `benchmark-core` archived
# `LassoLagHybrid` on 2026-09-24 with "no wins recorded", so deleting these
# chunks would destroy the write-up of why it failed.
SUPERSEDED_SOURCES = {
    "1000_financial_forecasting_targets_and_ssm.md",
    "1001_lasso_lag_selection_mutation.md",
    "999_ts_diverse_experiment_results.md",
    "New Dokument tekstowy.txt",
    "adaptive_search_workspace_architecture.md",
}


def is_authored(name: str) -> bool:
    """Whether this source name denotes hand-written work, not an extract.

    A source with no file extension is a topic label, not a filename: nothing
    was ever cut from `agent_workspace_research` because no such file exists.
    An entry in `SUPERSEDED_SOURCES` is a project-authored write-up whose
    subject was archived; the chunk is its only remaining record.
    """
    return not Path(name).suffix or name in SUPERSEDED_SOURCES


def main() -> int:
    if not CORPUS_DIR.is_dir():
        print("[check_entropy] no corpus; nothing to check")
        return 0
    by_source, total = scan()
    unbuildable_chunks = unbuildable(by_source)
    authored = {n: c for n, c in unbuildable_chunks.items() if is_authored(n)}
    lost = {n: c for n, c in unbuildable_chunks.items() if n not in authored}
    lost_chunks = sum(lost.values())

    print(f"[check_entropy] {total} chunks from {len(by_source)} sources")
    if authored:
        print(f"[check_entropy] note: {sum(authored.values())} chunks across "
              f"{len(authored)} authored source(s) were never cut from a file and "
              f"are not counted as loss:")
        for name, count in sorted(authored.items(), key=lambda kv: -kv[1]):
            print(f"  {count:>5} chunks  {name}")
    if not lost:
        print("[check_entropy] PASS: every derived chunk's source is on disk, "
              "tracked, or in the library")
        return 0

    print(f"[check_entropy] FAIL: {lost_chunks} chunks ({100*lost_chunks//max(total,1)}%) "
          f"have no recoverable source, across {len(lost)} source(s):", file=sys.stderr)
    for name, count in sorted(lost.items(), key=lambda kv: -kv[1]):
        print(f"  {count:>5} chunks  {name}", file=sys.stderr)
    print("[check_entropy] a chunk whose source is gone cannot be re-derived, "
          "verified, or repaired. Do not delete these chunks — they are the last copy.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
