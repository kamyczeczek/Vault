#!/usr/bin/env python3
"""Run the checked-in session-memory retrieval evaluation set.

Usage: python.exe scripts/eval_memory_retrieval.py [--limit 5]
Exit 0 only when every query has an expected session in its top-k results.
The window counts DISTINCT sessions: query_memory returns chunks, and without
per-session dedup the same session can occupy several ranks, shrinking the
number of candidate sessions below the window (12/15 on the 2026-10-20 corpus
until dedup; with dedup the same corpus measures 15/15).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import memory_index as mi  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--type", choices=["error", "decision", "tool", "content"], default=None,
                        help="Override chunk type for every case")
    parser.add_argument("--raw", action="store_true",
                        help="Ignore per-case type filters and measure unfiltered retrieval")
    args = parser.parse_args()
    cases = json.loads((ROOT / "scripts" / "memory" / "eval_queries.json").read_text(encoding="utf-8"))
    con = mi.open_db()
    reciprocal_ranks: list[float] = []
    failures = 0
    try:
        for case in cases:
            chunk_type = None if args.raw else case.get("type", args.type)
            excluded = case.get("exclude_session_ids", [])
            # Fetch a buffer so that excluded sessions cannot steal the case's
            # top-k window; the excluded session still ranks normally for
            # unexcluded cases, so this never widens or narrows the gate.
            results = mi.query_memory(con, case["query"], limit=args.limit + len(excluded),
                                      chunk_type_filter=chunk_type)
            if excluded:
                results = [r for r in results
                           if not any(r["session_id"].startswith(e) for e in excluded)]
            # The window is over sessions, not chunks: collapse same-session
            # chunks before slicing, then re-fetch if dedup shrank the buffer
            # below the window (corpus growth can put one session's chunks in
            # several top ranks).
            seen, distinct = set(), []
            for r in results:
                if r["session_id"] not in seen:
                    seen.add(r["session_id"])
                    distinct.append(r)
            if len(distinct) < args.limit:
                results = mi.query_memory(con, case["query"],
                                          limit=(args.limit + len(excluded) + args.limit) * 3,
                                          chunk_type_filter=chunk_type)
                results = [r for r in results
                           if not any(r["session_id"].startswith(e) for e in excluded)]
                seen, distinct = set(), []
                for r in results:
                    if r["session_id"] not in seen:
                        seen.add(r["session_id"])
                        distinct.append(r)
            results = distinct[:args.limit]
            expected = set(case["expected_session_ids"])
            # Session stores use long opaque IDs; the eval file deliberately keeps
            # stable prefixes so it remains readable across loader formatting changes.
            ranks = [
                i for i, result in enumerate(results, 1)
                if any(result["session_id"].startswith(prefix) for prefix in expected)
            ]
            if ranks:
                reciprocal_ranks.append(1.0 / ranks[0])
                status = "PASS"
            else:
                reciprocal_ranks.append(0.0)
                failures += 1
                status = "FAIL"
            ids = ", ".join(result["session_id"] for result in results)
            note = f" (excluded {len(excluded)})" if excluded else ""
            print(f"{status} {case['name']}: top-{args.limit} [{ids}]{note}")
    finally:
        con.close()
    total = len(cases)
    hit_rate = (total - failures) / total if total else 0.0
    mrr = sum(reciprocal_ranks) / total if total else 0.0
    print(f"\nretrieval_eval: hit@{args.limit}={hit_rate:.3f} MRR={mrr:.3f} ({total - failures}/{total})")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
