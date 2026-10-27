"""Build the pilot's mini-graph fixture (D-002, Phase 5 backend).

Deterministic SQLite fixture holding the session-05 example triples:
Produkt X -[STWORZYŁ]-> Firma Y -[ZARZĄDZA]-> Jan Kowalski
(spec: session `goose 20261008_3`, transcript lines 122-146).

Schema mirrors the archived graph.db `nodes`/`edges` tables column-for-
column (subset: no node_tags/fts — the Phase 5 seed is a stub; those
tables revive only if an archive grounding proof happens). Tools written
against these two tables run unchanged on the archive.

    python fixtures/build_mini_graph.py      # build + verify
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "mini_graph.db"

NODES: list[tuple] = [
    ("01_produkt_x", "Produkt X", "fixtures/mini_graph.md",
     "produkt", "", "Produkt X zostal stworzony przez Firme Y.",
     "Produkt", "fixture", "goose 20261008_3", 0, None),
    ("02_firma_y", "Firma Y", "fixtures/mini_graph.md",
     "firma", "", "Firma Y stworzyla Produkt X. Firma Y jest zarzadzana przez Jana Kowalskiego.",
     "Firma", "fixture", "goose 20261008_3", 0, None),
    ("03_jan_kowalski", "Jan Kowalski", "fixtures/mini_graph.md",
     "osoba", "", "Jan Kowalski zarzadza Firma Y.",
     "Osoba", "fixture", "goose 20261008_3", 0, None),
]

EDGES: list[tuple] = [
    ("01_produkt_x", "02_firma_y", "STWORZYŁ", 1.0, "fixture"),
    ("02_firma_y", "03_jan_kowalski", "ZARZĄDZA", 1.0, "fixture"),
]


def build() -> None:
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    try:
        conn.execute(
            "CREATE TABLE nodes (id TEXT, title TEXT, path TEXT, tags TEXT,"
            " headings TEXT, body TEXT, node_type TEXT, source_family TEXT,"
            " source TEXT, trust_tier INTEGER, semantic_edges TEXT)"
        )
        conn.execute(
            "CREATE TABLE edges (src TEXT, dst TEXT, kind TEXT,"
            " conf REAL, tag TEXT)"
        )
        conn.executemany("INSERT INTO nodes VALUES (?,?,?,?,?,?,?,?,?,?,?)", NODES)
        conn.executemany("INSERT INTO edges VALUES (?,?,?,?,?)", EDGES)
        conn.commit()
    finally:
        conn.close()


def verify() -> int:
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        nn = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        ne = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        triples = conn.execute(
            "SELECT src, kind, dst FROM edges ORDER BY src, dst").fetchall()
    finally:
        conn.close()
    ok = (
        nn == len(NODES)
        and ne == len(EDGES)
        and [tuple(t) for t in triples] == [(s, k, d) for s, d, k, _, _ in EDGES]
    )
    print(f"nodes: {nn}/{len(NODES)}, edges: {ne}/{len(EDGES)}")
    for s, k, d in triples:
        print(f"  ({s}, {k}, {d})")
    print("mini_graph: PASS" if ok else "mini_graph: FAIL")
    return 0 if ok else 1


def main() -> int:
    build()
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
