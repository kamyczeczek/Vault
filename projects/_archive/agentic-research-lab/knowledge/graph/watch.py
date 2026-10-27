#!/usr/bin/env python3
"""watch.py — Phase 3 gate: verify graph.db matches corpus.

Exits 0 when graph.db node count equals corpus chunk count and the live
fingerprint matches the stored fingerprint. Auto-builds graph.db if missing.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "knowledge" / "graph" / "graph.db"
CORPUS = ROOT / "knowledge" / "corpus"
FINGERPRINT = ROOT / "knowledge" / "graph" / ".graph_fingerprint"


def corpus_fingerprint() -> str:
    if not CORPUS.exists():
        return ""
    h = hashlib.sha256()
    for path in sorted(CORPUS.glob("*.md")):
        h.update(path.read_bytes())
    return h.hexdigest()[:12]


def stored_fingerprint() -> str:
    if FINGERPRINT.exists():
        return FINGERPRINT.read_text(encoding="utf-8").strip()
    return ""


def corpus_count() -> int:
    if not CORPUS.exists():
        return 0
    return len(list(CORPUS.glob("*.md")))


def graph_node_count() -> int:
    if not DB.exists():
        return 0
    conn = sqlite3.connect(DB)
    try:
        row = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def check_once() -> int:
    if not DB.exists():
        print("[watch] graph.db missing — auto-building graph...", file=sys.stderr)
        try:
            import build_graph
            build_graph.build()
        except Exception as e:
            print(f"FAIL: failed to auto-build graph: {e}", file=sys.stderr)
            return 1

    live_fp = corpus_fingerprint()
    stored_fp = stored_fingerprint()
    cc = corpus_count()
    gc = graph_node_count()

    ok = True
    if live_fp != stored_fp:
        print(f"FAIL: corpus fingerprint mismatch — live={live_fp} stored={stored_fp}", file=sys.stderr)
        ok = False
    if cc != gc:
        print(f"FAIL: graph.db nodes ({gc}) != corpus chunks ({cc})", file=sys.stderr)
        ok = False

    if ok:
        print(f"OK: graph.db matches corpus ({gc} nodes, fingerprint={live_fp})")
        return 0
    return 1


def main() -> int:
    if "--once" in sys.argv:
        return check_once()
    print("Usage: python knowledge/graph/watch.py --once", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
