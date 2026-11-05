#!/usr/bin/env python3
"""Query the Workspace-Research knowledge graph (graph.db, FTS5).

Usage: python knowledge/graph/ask.py "<question>" [--limit N] [--raw]
Returns ranked chunk ids with titles, paths, tags, and a matched snippet.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = Path(__file__).with_name("graph.db")


def query(question: str, limit: int = 5, tags: list[str] | None = None) -> list[dict]:
    if not DB.exists():
        print("Error: graph.db missing — run build_graph.py", file=sys.stderr)
        return []
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    words = [w.lower() for w in question.replace("/", " ").split() if len(w) > 2]
    if not words:
        words = [question.lower()] if question.strip() else []

    tag_sql, tag_params = "", []
    if tags:
        tag_sql = " AND ".join(["n.tags LIKE ?" for _ in tags])
        tag_params = [f'%"{t}"%' for t in tags]

    if tags and not words:
        # Deterministic tag-intersection routing: order by id for reproducibility.
        sql = (f"SELECT n.id, n.title, n.path, n.tags, n.body, NULL AS snip, 0 AS rank "
               f"FROM nodes n WHERE {tag_sql} ORDER BY n.id LIMIT ?")
        rows = conn.execute(sql, (*tag_params, limit)).fetchall()
    else:
        match = " AND ".join(words) if words else "id:*"
        where = "WHERE fts MATCH ?"
        params: list = [match]
        if tag_sql:
            where += f" AND ({tag_sql})"
            params.extend(tag_params)
        sql = (f"SELECT n.id, n.title, n.path, n.tags, n.body, "
               f"snippet(fts, 3, '⟦', '⟧', '...', 12) AS snip, bm25(fts) AS rank "
               f"FROM fts JOIN nodes n ON n.id = fts.id {where} ORDER BY rank LIMIT ?")
        params.append(limit)
        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError:
            if not words or match == "id:*":
                rows = []
            else:
                parts, lparams = [], []
                for w in words:
                    parts.append("(LOWER(n.title) LIKE ? OR LOWER(n.tags) LIKE ? OR LOWER(n.body) LIKE ?)")
                    lparams.extend([f"%{w}%", f"%{w}%", f"%{w}%"])
                if tag_sql:
                    lparams.extend(tag_params)
                sql = (f"SELECT n.id, n.title, n.path, n.tags, n.body, NULL AS snip, 0 AS rank "
                       f"FROM nodes n WHERE {' OR '.join(parts)}")
                if tag_sql:
                    sql += f" AND {tag_sql}"
                rows = conn.execute(sql + " LIMIT ?", (*lparams, limit)).fetchall()

    conn.close()
    out = []
    for r in rows:
        out.append({
            "id": r["id"], "title": r["title"], "path": r["path"],
            "tags": r["tags"], "snippet": r["snip"] or "",
            "body": r["body"] or "",
        })
    return out


def get_neighbors(node_id: str, limit: int = 5) -> list[dict]:
    """Retrieve graph neighbors connected via REFERS_TO or SHARES_TAG."""
    if not DB.exists():
        return []
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    sql = """
        SELECT n.id, n.title, n.path, e.kind, e.tag
        FROM edges e
        JOIN nodes n ON n.id = (CASE WHEN e.src = ? THEN e.dst ELSE e.src END)
        WHERE e.src = ? OR e.dst = ?
        ORDER BY (CASE WHEN e.kind = 'REFERS_TO' THEN 0 ELSE 1 END), n.id
        LIMIT ?
    """
    rows = conn.execute(sql, (node_id, node_id, node_id, limit)).fetchall()
    conn.close()
    return [{"id": r["id"], "title": r["title"], "path": r["path"], "kind": r["kind"], "tag": r["tag"]} for r in rows]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("question", nargs="?", default="")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--raw", action="store_true", help="print full body of each match")
    ap.add_argument("--tag", action="append", default=[], help="require tag (repeatable; intersection)")
    ap.add_argument("--neighbors", action="store_true", help="explore 1-hop graph neighbors for each match")
    args = ap.parse_args()
    results = query(args.question, args.limit, args.tag)
    for r in results:
        print(f"\n# {r['id']} | {r['title']}")
        print(f"  path: {r['path']}")
        print(f"  tags: {r['tags']}")
        if args.raw:
            print(f"  ---\n{r['body']}")
        elif r["snippet"]:
            print(f"  match: {r['snippet']}")
        if args.neighbors:
            nbrs = get_neighbors(r["id"])
            if nbrs:
                print("  neighbors:")
                for n in nbrs:
                    tag_info = f" [{n['tag']}]" if n["tag"] else ""
                    print(f"    - {n['kind']}{tag_info} -> {n['id']} ({n['title']})")
    # A --tag intersection that matches nothing is a dead routing key: the prompt
    # author asked for a vocabulary term the corpus does not carry. Returning 0 with
    # no output made that silently mean "no principles apply" instead of "typo/stale
    # tag", so an audit prompt routed on a tag absent from knowledge/topics.md for
    # two sessions before anyone noticed (W-AUDIT-4). Fail loud instead.
    if args.tag and not results:
        print(f"Error: tag intersection {args.tag} matched no chunks — a requested tag "
              f"is absent from the corpus vocabulary (see knowledge/topics.md)",
              file=sys.stderr)
        return 2
    if not args.tag and not results and args.question:
        print(f"Error: no chunks matched the question {args.question!r}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
