#!/usr/bin/env python3
"""Verify every chunk-id citation resolves, and resolves to the intended content.

## Why this exists

Chunk ids are `NN_<slug of filename>`. Re-ingesting a book therefore regenerates the
*same* ids pointing at *different text*. During the C-6 corpus repair this silently
invalidated four benchmark golds — the ids still existed, every "does this id resolve?"
check passed, and the gold had quietly become a different chunk.

A citation that resolves is therefore not sufficient. This gate checks both halves:

1. **Resolution** — every cited id exists in `graph.db`.
2. **Concept support** — for benchmark golds, every `required_concepts` term actually
   occurs in the cited chunk's body. This is what caught the drift, and it is a property
   of the citation rather than of the corpus, so it survives any re-ingest.

Together they answer the question the fingerprint cannot: *is this citation still saying
what its author meant?*
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "knowledge" / "graph"
BENCHMARK = GRAPH / "retrieval_benchmark.json"
DIGESTS = ROOT / "reflection" / "digests"
CANDIDATES = ROOT / "reflection" / "candidates"
CHUNK_LINE_RE = re.compile(r"Chunk id:\s*`([0-9]{2}_[a-z0-9_]+)`")
EVIDENCE_RE = re.compile(r"`([0-9]{2}_[a-z0-9_]+)`")


def known_ids() -> set[str]:
    conn = sqlite3.connect(GRAPH / "graph.db")
    try:
        return {r[0] for r in conn.execute("SELECT id FROM nodes")}
    finally:
        conn.close()


def check_benchmark(known: set[str], conn: sqlite3.Connection) -> list[str]:
    """Every gold must exist and support every required concept."""
    problems: list[str] = []
    if not BENCHMARK.exists():
        return [f"{BENCHMARK.name} missing"]
    data = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    for case in data.get("cases", []):
        cid = case.get("id", "?")
        golds = case.get("gold_sources") or []
        if not golds:
            problems.append(f"benchmark {cid}: no gold_sources")
            continue
        concepts = [c.lower() for c in (case.get("required_concepts") or [])]
        for gold in golds:
            if gold not in known:
                problems.append(f"benchmark {cid}: gold {gold} absent from graph.db")
                continue
            row = conn.execute("SELECT body FROM nodes WHERE id=?", (gold,)).fetchone()
            body = (row[0] or "").lower() if row else ""
            missing = [c for c in concepts if c not in body]
            if missing:
                # This is the id-reuse signature: the id resolves, the content moved.
                problems.append(
                    f"benchmark {cid}: gold {gold} does not contain "
                    f"{missing} — id likely reused across re-ingest")
    return problems


def check_digests(known: set[str]) -> list[str]:
    """Load-bearing `Chunk id:` lines must resolve. Prose references need not."""
    problems: list[str] = []
    if not DIGESTS.is_dir():
        return problems
    for path in sorted(DIGESTS.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for cid in CHUNK_LINE_RE.findall(text):
            if cid not in known:
                problems.append(f"{path.name}: Chunk id `{cid}` absent from graph.db")
    return problems


def check_candidates(known: set[str]) -> list[str]:
    """Evidence fields in candidates must resolve."""
    problems: list[str] = []
    if not CANDIDATES.is_dir():
        return problems
    decoder = json.JSONDecoder()
    for path in sorted(CANDIDATES.glob("*.jsonl")):
        text = path.read_text(encoding="utf-8", errors="replace")
        idx = 0
        while idx < len(text):
            while idx < len(text) and text[idx].isspace():
                idx += 1
            if idx >= len(text):
                break
            try:
                record, idx = decoder.raw_decode(text, idx)
            except json.JSONDecodeError:
                break
            if not isinstance(record, dict):
                continue
            evidence = record.get("Evidence") or record.get("evidence") or ""
            if not isinstance(evidence, str):
                continue
            for cid in EVIDENCE_RE.findall(evidence):
                if cid not in known:
                    problems.append(
                        f"{path.name}: evidence `{cid}` absent from graph.db")
    return problems


def main() -> int:
    if not (GRAPH / "graph.db").exists():
        print("FAIL: graph.db missing — run build_graph.py first")
        return 1

    known = known_ids()
    conn = sqlite3.connect(GRAPH / "graph.db")
    try:
        problems: list[str] = []
        problems += check_benchmark(known, conn)
        problems += check_digests(known)
        problems += check_candidates(known)
    finally:
        conn.close()

    if problems:
        print(f"FAIL: {len(problems)} citation problem(s)")
        for p in problems[:20]:
            print(f"  {p}")
        if len(problems) > 20:
            print(f"  ... and {len(problems) - 20} more")
        print("  An id that resolves is not enough: ids are derived from filenames, so "
              "re-ingest reuses them for new text.")
        return 1

    print(f"OK: every chunk-id citation resolves and supports its claim "
          f"({len(known)} nodes indexed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
