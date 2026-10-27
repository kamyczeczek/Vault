#!/usr/bin/env python3
"""Verify the knowledge graph is a deterministic function of the corpus.

## Why this exists

`check_reflection.py` verifies `.graph_fingerprint`, which proves the graph was built
from the corpus currently on disk. It cannot prove the graph was built *correctly*, and
it cannot prove the build is deterministic — a fingerprint check is satisfied by any
self-consistent graph, including one that silently varies run to run.

That class of bug is invisible by construction: set iteration order, dict ordering, or a
timestamp leaking into a stored column all produce a self-consistent result every time.
Rebuilding and diffing is the only check that catches it.

## The contract

`build_graph.build()` must be a pure function of `knowledge/corpus/`. Build twice into
separate databases and require the derived content to be identical:

* node rows, ordered by id
* edge rows, ordered by (src, kind, dst)
* FTS row content, ordered by rowid

The fingerprint itself is excluded because it is compared separately and is the input to
the comparison, not the thing under test.

Non-determinism here is not a cosmetic issue. Every downstream artifact — reflection
digests, candidates, the retrieval benchmark — is stamped with the fingerprint and
assumes the graph behind it is reproducible. If the build is not reproducible, those
stamps attest to nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "knowledge" / "graph"))

import build_graph  # noqa: E402


def _digest_db(path: Path) -> dict[str, str]:
    """Content hash of every derived table, order-independent per table."""
    conn = sqlite3.connect(path)
    out: dict[str, str] = {}
    try:
        h = hashlib.sha256()
        for row in conn.execute(
            "SELECT id, title, path, tags, headings, body, node_type, "
            "source_family, source, trust_tier, semantic_edges "
            "FROM nodes ORDER BY id"
        ):
            h.update(repr(row).encode("utf-8"))
        out["nodes"] = h.hexdigest()

        h = hashlib.sha256()
        for row in conn.execute(
            "SELECT src, dst, kind, conf, tag FROM edges ORDER BY src, kind, dst, conf"
        ):
            h.update(repr(row).encode("utf-8"))
        out["edges"] = h.hexdigest()

        h = hashlib.sha256()
        for row in conn.execute(
            "SELECT node_id, tag FROM node_tags ORDER BY node_id, tag"
        ):
            h.update(repr(row).encode("utf-8"))
        out["node_tags"] = h.hexdigest()

        h = hashlib.sha256()
        for row in conn.execute("SELECT id, title, body, source_family FROM fts ORDER BY id"):
            h.update(repr(row).encode("utf-8"))
        out["fts"] = h.hexdigest()

        for name, sql in (("nodes", "SELECT COUNT(*) FROM nodes"),
                          ("edges", "SELECT COUNT(*) FROM edges"),
                          ("node_tags", "SELECT COUNT(*) FROM node_tags"),
                          ("fts", "SELECT COUNT(*) FROM fts")):
            out[f"{name}_count"] = str(conn.execute(sql).fetchone()[0])
    finally:
        conn.close()
    return out

def _schema_sig(path: Path) -> str:
    """Hash of the SQLite schema (tables, indexes, triggers, views).

    The atomic-replace build path and the locked-DB in-place rebuild path
    must converge on the same schema — e.g. an index created in one path
    but not the other is a real determinism bug that row content alone
    would not catch.
    """
    conn = sqlite3.connect(path)
    try:
        h = hashlib.sha256()
        for row in conn.execute(
            "SELECT type, name, sql FROM sqlite_master "
            "ORDER BY type, name, sql"
        ):
            h.update(repr(row).encode("utf-8"))
        return h.hexdigest()
    finally:
        conn.close()


_TS_RE = re.compile(rb'("created_at"\s*:\s*)[0-9.]+')


def _strip_timestamp(data: bytes) -> bytes:
    """generation.json embeds a wall-clock time; blank it before comparing."""
    return _TS_RE.sub(rb'\g<1>0', data)



def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--keep-going", action="store_true",
                    help="report differences but exit 0")
    args = ap.parse_args()

    live = build_graph.DB
    if not live.exists():
        print("FAIL: graph.db missing — run build_graph.py first")
        return 1

    # build() writes five artifacts. Snapshot every one of them, not just the DB:
    # an earlier version of this gate restored graph.db only, which left
    # generation.json dirty after every run — a verification step must not be
    # the thing that dirties the tree.
    outputs = [build_graph.DB, build_graph.DIGEST, build_graph.INDEX,
               build_graph.GENERATION,
               build_graph.Path(build_graph.__file__).with_name(".graph_fingerprint")]

    with tempfile.TemporaryDirectory() as tmp:
        saved = {}
        for i, path in enumerate(outputs):
            if path.exists():
                backup = Path(tmp) / f"{i}-{path.name}"
                shutil.copy2(path, backup)
                saved[path] = backup
        first_db_digest = _digest_db(build_graph.DB)
        first_schema = _schema_sig(build_graph.DB)
        first_bytes = {p: b.read_bytes() for p, b in saved.items()}
        try:
            build_graph.build()
            second_db_digest = _digest_db(build_graph.DB)
            second_schema = _schema_sig(build_graph.DB)
            second_bytes = {p: p.read_bytes() for p in saved}
        finally:
            for path, backup in saved.items():
                shutil.copy2(backup, path)

    # created_at in generation.json is a wall-clock timestamp, so that file is
    # compared by everything-except-the-timestamp rather than byte-for-byte.
    #
    # graph.db is compared by derived content + schema, NOT by file bytes.
    # The documented contract above is content identity (node rows, edge rows,
    # FTS row content), and two byte-identical SQLite files are not required
    # for that: when the live DB is locked open (Windows cannot replace an
    # open file), build() falls back to an in-place DELETE + re-INSERT, whose
    # page layout and freelist legitimately differ from a fresh atomic build
    # while every row is identical. Byte-comparing graph.db therefore failed
    # the gate on every locked machine despite a deterministic build.
    volatile = {p.name for p in saved if p.name == "generation.json"}
    byte_compared = [p for p in saved if p != build_graph.DB]
    drifted = []
    for path in byte_compared:
        if path.name in volatile:
            a, b = first_bytes[path], second_bytes[path]
            if a != b and _strip_timestamp(a) != _strip_timestamp(b):
                drifted.append(path.name)
        elif first_bytes[path] != second_bytes[path]:
            drifted.append(path.name)

    db_ok = first_db_digest == second_db_digest and first_schema == second_schema
    if db_ok and not drifted:
        print("OK: graph is a deterministic function of the corpus "
              f"(nodes={first_db_digest['nodes_count']}, "
              f"edges={first_db_digest['edges_count']}, "
              f"fts={first_db_digest['fts_count']}); "
              f"{len(saved)} build output(s) reproduced, none left modified")
        return 0

    print("FAIL: rebuild from an unchanged corpus did not reproduce the graph")
    if first_schema != second_schema:
        print(f"  db.schema: {first_schema[:12]} -> {second_schema[:12]}")
    if first_db_digest != second_db_digest:
        for key in sorted(set(first_db_digest) | set(second_db_digest)):
            if first_db_digest.get(key) != second_db_digest.get(key):
                print(f"  db.{key}: {first_db_digest.get(key)} -> {second_db_digest.get(key)}")
    for name in drifted:
        print(f"  output differs: {name}")
    print("  Derived artifacts stamped with the fingerprint cannot be trusted until "
          "this is deterministic: set/dict iteration order or a stored timestamp is "
          "leaking into the build.")
    return 0 if args.keep_going else 1


if __name__ == "__main__":
    raise SystemExit(main())
