#!/usr/bin/env python3
"""Verify active registered topics are represented in the graph vocabulary."""
from __future__ import annotations
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ROOT / "knowledge" / "topics.md"
DB = ROOT / "knowledge" / "graph" / "graph.db"


def main() -> int:
    if not TOPICS.exists() or not DB.exists():
        print("FAIL: topics.md or graph.db missing", file=sys.stderr)
        return 2
    topics: set[str] = set()
    for line in TOPICS.read_text(encoding="utf-8").splitlines():
        if line.strip().lower() == "## planned topics":
            break
        if line.strip().startswith("- "):
            topics.add(line.strip()[2:].strip())
    conn = sqlite3.connect(DB)
    graph_tags = {tag for (raw,) in conn.execute("SELECT tags FROM nodes") for tag in json.loads(raw)}
    conn.close()
    missing = sorted(topics - graph_tags)
    if missing:
        print("FAIL: registered topics have no corpus coverage: " + ", ".join(missing), file=sys.stderr)
        return 1
    print(f"OK: {len(topics)} active topics have graph coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
