#!/usr/bin/env python3
"""Structured knowledge-graph query surface (resolve / expand).

Replaces eight dead one-off scripts (`query_graph_db.py`,
`query_graph_nodes.py`, `query_kg.py`, `verify_with_kg.py`,
`investigate_methodology.py`, `check_schema.py`, `read_kg_reflections.py`,
`test_kg_query.py`), which pointed at a `.brain` database that does not exist
or at tables/columns that are not in the schema. This module is the only query
surface: three functions, one read-only database, deterministic ordering.

- `resolve(substring)` — find nodes whose id or title contains a substring.
- `expand(node_id, steps)` — walk the edge graph N steps out (the look-ahead
  knob; the caller decides N). Neighbours order by edge kind, confidence, id.
- `resolve_and_expand(substring, steps)` — resolve, then expand each hit.

The index lives in `../agentic-research-lab/knowledge/graph/graph.db` and is
opened read-only: a query tool must never be able to dirty the graph.
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT.parent / "agentic-research-lab" / "knowledge" / "graph" / "graph.db"

KIND_ORDER = (
    "CASE e.kind"
    " WHEN 'REFERS_TO' THEN 0"
    " WHEN 'DERIVES_FROM' THEN 1"
    " WHEN 'SCARRED_FROM' AND e.tag='hard-gate' THEN 2"
    " WHEN 'SUPPORTS' THEN 3"
    " WHEN 'REFUTES' THEN 4"
    " WHEN 'CONTRADICTS' THEN 5"
    " WHEN 'EXTENDS' THEN 6"
    " WHEN 'PART_OF' THEN 7"
    " WHEN 'SEQUENCE' THEN 8"
    " WHEN 'SCARRED_FROM' THEN 9"
    " ELSE 10 END"
)


def _connect() -> sqlite3.Connection:
    if not DB.exists():
        raise FileNotFoundError(
            f"knowledge graph not found at {DB} — rebuild it from "
            "agentic-research-lab before querying"
        )
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def resolve(substring: str, limit: int = 5) -> list[dict]:
    """Return nodes whose id or title contains the query words in order.

    Words match across separators, so "graph databases" finds
    `graph_databases_...` ids and titles alike. Case-insensitive,
    deterministic id order.
    """
    words = [w for w in substring.lower().split() if w]
    if not words:
        return []
    pattern = "%" + "%".join(words) + "%"
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, title, path, tags, source_family FROM nodes "
            "WHERE lower(id) LIKE ? OR lower(title) LIKE ? "
            "ORDER BY id LIMIT ?",
            (pattern, pattern, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def expand(node_id: str, steps: int = 1, limit: int = 5) -> list[dict]:
    """Walk the edge graph outward from `node_id` up to `steps` hops.

    Breadth-first, one ordered neighbour page per frontier node. Deterministic:
    kind order, then confidence descending, then id.
    """
    conn = _connect()
    try:
        seen = {node_id}
        frontier = [node_id]
        out: list[dict] = []
        for _ in range(max(steps, 0)):
            nxt: list[str] = []
            for nid in frontier:
                rows = conn.execute(
                    f"SELECT n.id, n.title, n.path, n.tags, n.source_family,"
                    f" e.kind, e.conf FROM edges e"
                    f" JOIN nodes n ON n.id ="
                    f" (CASE WHEN e.src = ? THEN e.dst ELSE e.src END)"
                    f" WHERE e.src = ? OR e.dst = ?"
                    f" ORDER BY {KIND_ORDER}, e.conf DESC, n.id LIMIT ?",
                    (nid, nid, nid, limit),
                ).fetchall()
                for r in rows:
                    if r["id"] not in seen:
                        seen.add(r["id"])
                        nxt.append(r["id"])
                        out.append(dict(r))
            frontier = nxt
            if not frontier:
                break
        return out
    finally:
        conn.close()


def resolve_and_expand(
    substring: str, steps: int = 1, limit: int = 5
) -> list[dict]:
    """Resolve a substring to nodes, then expand each hit `steps` hops out."""
    hits = resolve(substring, limit=limit)
    seen = {h["id"] for h in hits}
    out = list(hits)
    for hit in hits:
        for nbr in expand(hit["id"], steps=steps, limit=limit):
            if nbr["id"] not in seen:
                seen.add(nbr["id"])
                out.append(nbr)
    return out


def like_baseline(substring: str, limit: int = 5) -> list[dict]:
    """Dumb reference arm for the eval harness: raw LIKE over bodies.

    This is the Bash of the comparison — sharp substring matching, no ranking,
    no graph, no determinism beyond row order. The harness must beat it on
    family coverage and consistency, not on raw hit count.
    """
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, title, path, tags, source_family FROM nodes "
            "WHERE body LIKE '%' || ? || '%' ORDER BY id LIMIT ?",
            (substring, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("resolve", help="substring -> nodes")
    p.add_argument("substring")
    p.add_argument("--limit", type=int, default=5)
    p = sub.add_parser("expand", help="node -> N-hop neighbours")
    p.add_argument("node_id")
    p.add_argument("--steps", type=int, default=1)
    p.add_argument("--limit", type=int, default=5)
    p = sub.add_parser("resolve_and_expand", help="both")
    p.add_argument("substring")
    p.add_argument("--steps", type=int, default=1)
    p.add_argument("--limit", type=int, default=5)
    args = ap.parse_args()

    if args.cmd == "resolve":
        rows = resolve(args.substring, limit=args.limit)
    elif args.cmd == "expand":
        rows = expand(args.node_id, steps=args.steps, limit=args.limit)
    else:
        rows = resolve_and_expand(
            args.substring, steps=args.steps, limit=args.limit
        )
    for r in rows:
        extra = f" [{r.get('kind')}]" if r.get("kind") else ""
        print(f"- {r['id']}{extra} | {r['title'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
