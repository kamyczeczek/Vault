#!/usr/bin/env python3
"""debug.py — the door onto the workspace's past.

Thin, single-command wrapper over scripts/memory_index.py for the
"unfamiliar error / has this broken before?" trigger. It removes the decision
cost of the survey-then-drill pair so the right move stays the cheap move:

  python.exe scripts/debug.py "<error string>"
        -> extract 2-3 high-signal tokens, run an FTS5 survey, print the
           candidates, and record a 'gap'/'hit' line to the loan log.

  python.exe scripts/debug.py get <chunk_id>
        -> pay for the one hit worth reading (drill).

  python.exe scripts/debug.py record helped|wrong|gap "<error string>"
        -> close the loop on a query you already ran: did the past help?

The index and its full CLI live in scripts/memory_index.py (ingest / query /
get / stats / freshness). This file only adds: automatic token extraction and
outcome logging. Run with the Windows interpreter (python.exe), never the WSL
python3 — under this repo's MSYS shell python3 sees no agent store.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import memory_index as mi  # noqa: E402

# Function words to drop from a query; error-domain words (failed, error,
# unavailable) are kept on purpose — they are the type signal.
_STOP = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "of",
    "is", "are", "was", "were", "be", "been", "not", "no", "yes", "do",
    "does", "did", "when", "after", "before", "because", "for", "with",
    "from", "into", "this", "that", "it", "its", "you", "your", "we",
}

# CamelCase or snake_case identifier: the strongest FTS5 signal in a stack trace.
_ID_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*[A-Za-z])\b")
# Hex codes / opaque numeric codes (STATUS_DLL_INIT_FAILED-style, 0xC0000142, 404, 503).
_CODE_RE = re.compile(r"\b(0x[0-9a-fA-F]{3,}|\b\d{4,6}\b)")
# File / path fragments with a dot: cordis.patch.yml, node_modules, .dsh
_PATH_RE = re.compile(r"\b([A-Za-z0-9_.\-]+\.[A-Za-z0-9]{1,10}\b)")


def _has_signal(tok: str) -> int:
    """Heuristic signal score for one candidate token."""
    low = tok.lower()
    score = 0
    # camelCase boundary or internal underscore -> strong identifier signal
    if re.search(r"[a-z][A-Z]", tok) or "_" in low:
        score += 3
    if re.fullmatch(r"0x[0-9a-fA-F]{3,}", low):
        score += 3
    if re.fullmatch(r"\d{4,6}", low):
        score += 2
    if "." in low:
        score += 2
    if low not in _STOP and len(low) >= 3:
        score += 1
    return score


def extract_tokens(text: str, cap: int = 3) -> List[str]:
    """Return up to `cap` highest-signal tokens from an error string."""
    seen: set[str] = set()
    scored: List[tuple[int, int, str]] = []  # (score, position, token)
    pos = 0
    for match in re.finditer(r"[\w./\\\\-]+", text):
        tok = match.group(0).rstrip("/\\")
        if not tok or tok.lower() in _STOP:
            pos += 1
            continue
        # keep dotted path fragments as-is; split bare words normally
        candidates = [tok] if "." in tok else [tok]
        for cand in candidates:
            if cand in seen:
                continue
            seen.add(cand)
            scored.append((_has_signal(cand), pos, cand))
            pos += 1
    scored.sort(key=lambda t: t[0], reverse=True)  # stable: position breaks ties
    kept: List[str] = []
    for _score, _pos, tok in scored:
        if _score <= 0:
            continue
        kept.append(tok)
        if len(kept) >= cap:
            break
    if not kept:
        # fall back to the first non-stopword words so the query is never empty
        for word in text.split():
            w = word.strip().strip("\"'")
            if w and w.lower() not in _STOP and len(w) >= 3:
                kept.append(w)
                if len(kept) >= cap:
                    break
    return kept


def _format_hit(hit: dict) -> str:
    heading = (hit.get("heading") or "").replace("\n", " ").strip()
    if len(heading) > 60:
        heading = heading[:60] + "…"
    return f"  {hit['chunk_id']}  {hit.get('session_date','')}  [{hit.get('chunk_type','')}]  {heading}"


def cmd_run(args: argparse.Namespace) -> int:
    tokens = extract_tokens(args.error, cap=args.tokens)
    query_text = " ".join(tokens) or args.error
    con = mi.open_db()
    try:
        # The door opts into the curated-shelf promotion: when no type filter
        # is set, recalled curated lessons (SCARS/DECISIONS/flags) pin to the
        # front of the page. A `--type error` run keeps pure error ranking.
        results = mi.query_memory(
            con,
            query_text,
            limit=args.limit,
            chunk_type_filter=args.type,
            boost_curated=(args.type is None),
        )
    finally:
        con.close()

    print(f"[memory] tokens: {' '.join(tokens)}")
    print(f"[memory] query:  {query_text!r}  type={args.type or 'all'}")
    if not results:
        print("[memory] 0 hits -> outcome recorded as 'gap' (index has no knowledge for this)")
        mi.log_usage({
            "cmd": "debug", "query": query_text, "type": args.type,
            "hits": 0, "outcome": "gap",
        })
        print("[memory] if R14 (freshness) is failing, this is a STALE index, "
              "not 'nobody hit this' — run ingest, then re-query once.")
        return 0

    print(f"[memory] {len(results)} hit(s):")
    for hit in results:
        print(_format_hit(hit))
    print("\n[memory] drill one worth reading:")
    for hit in results[:2]:
        print(f"  python.exe scripts/memory_index.py get {hit['chunk_id']}")
    print("close the loop with:  python.exe scripts/debug.py record helped|wrong|gap "
          + json.dumps(args.error))

    mi.log_usage({
        "cmd": "debug", "query": query_text, "type": args.type,
        "hits": len(results), "outcome": "hit",
        "top_ids": [h["chunk_id"] for h in results],
    })
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    con = mi.open_db()
    try:
        row = con.execute(
            "SELECT chunk_id, agent, session_id, session_title, session_date, raw_path, chunk_type, heading, body "
            "FROM memory_fts WHERE chunk_id=?", (args.chunk_id,),
        ).fetchone()
    finally:
        con.close()
    if not row:
        print(f"Chunk not found: {args.chunk_id}")
        mi.log_usage({"cmd": "debug-get", "chunk_id": args.chunk_id, "found": False, "outcome": "gap"})
        return 1
    print(f"chunk_id: {row[0]}")
    print(f"agent: {row[1]}\nsession: {row[2]}  {row[3]}  {row[4]}")
    print(f"type: {row[6]}\nheading: {row[7]}\n")
    print(row[8])
    mi.log_usage({"cmd": "debug-get", "chunk_id": args.chunk_id, "found": True, "outcome": args.outcome})
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    if args.outcome not in ("helped", "wrong", "gap"):
        print("outcome must be one of: helped, wrong, gap")
        return 2
    mi.log_usage({"cmd": "debug-record", "query": " ".join(args.error) if args.error else "",
                  "outcome": args.outcome})
    print(f"[memory] recorded outcome '{args.outcome}' to the loan log "
          f"({mi.TELEMETRY_PATH.name})")
    return 0


_SUBCOMMANDS = {"run", "get", "record", "-h", "--help"}


def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="debug.py",
                                 description="Query the session-memory index for a past root cause of an unfamiliar error.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Extract tokens, survey the index, record the run")
    p_run.add_argument("error", help="The error string or failure description")
    p_run.add_argument("--limit", type=int, default=5, help="Max candidates (default 5)")
    p_run.add_argument("--tokens", type=int, default=3, help="How many tokens to keep (default 3)")
    p_run.add_argument("--type", dest="type", default=None,
                       choices=["error", "decision", "tool", "content", "curated"],
                       help="Filter by chunk type (default: all)")
    p_run.set_defaults(func=cmd_run)

    p_get = sub.add_parser("get", help="Print one chunk in full (drill)")
    p_get.add_argument("chunk_id", help="e.g. droid::<id>::31")
    p_get.add_argument("--outcome", default=None,
                       choices=["helped", "wrong", "gap"],
                       help="Close the loop on this drill")
    p_get.set_defaults(func=cmd_get)

    p_rec = sub.add_parser("record", help="Record whether a past hit actually helped")
    p_rec.add_argument("outcome", choices=["helped", "wrong", "gap"])
    p_rec.add_argument("error", nargs="*", help="The original error string (for the log)")
    p_rec.set_defaults(func=cmd_record)
    return ap


def main() -> int:
    ap = _build_parser()
    # Bare form: `debug.py "<error string>"` -> the cheapest default path,
    # so the run subcommand does not have to be typed.
    if len(sys.argv) > 1 and sys.argv[1] not in _SUBCOMMANDS:
        sys.argv = [sys.argv[0], "run"] + sys.argv[1:]
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
