#!/usr/bin/env python3
"""
ask.py — Query the FTS5 knowledge graph of this project (.brain/graph/graph.db).
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / ".brain" / "graph" / "graph.db"

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Search query or keyword")
    parser.add_argument("--limit", type=int, default=5, help="Max results")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"ERROR: Graph database not found at {DB_PATH}. Run scripts/ingest.py first.", file=sys.stderr)
        return 1

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clean query for FTS5 syntax safety or fallback to LIKE
    # Escape quotes and special FTS5 operators if needed, or wrap in quotes for phrase search
    cleaned_query = args.query.replace('"', '""')
    sql = "SELECT id, title, tags, path, snippet(nodes, 2, '[MATCH:', ']', '...', 16) FROM nodes WHERE nodes MATCH ? ORDER BY rank LIMIT ?"

    try:
        cursor.execute(sql, (cleaned_query, args.limit))
        rows = cursor.fetchall()
        fallback_used = False
    except Exception as e:
        # Visible fallback: LIKE path must appear in the return, not just console.
        print(f"NOTICE: FTS5 query failed ({e}); falling back to LIKE search.", file=sys.stderr)
        fallback_sql = "SELECT id, title, tags, path, content FROM nodes WHERE content LIKE ? OR title LIKE ? LIMIT ?"
        like_q = f"%{args.query}%"
        cursor.execute(fallback_sql, (like_q, like_q, args.limit))
        rows = [(r[0], r[1], r[2], r[3], r[4][:200] + "...") for r in cursor.fetchall()]
        fallback_used = True


    if not rows:
        print(f"No results found for query: {args.query}")
        return 0

    print(f"Found {len(rows)} result(s) for '{args.query}':\n")
    if fallback_used:
        print("NOTICE: results below come from LIKE fallback, not FTS5.\n")
    for r in rows:
        rid, title, tags, path, snippet = r
        print(f"[{rid}] {title}")
        print(f"  Tags: {tags}")
        print(f"  Source: {path}")
        print(f"  Snippet: {snippet.strip()}")
        print("-" * 60)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
