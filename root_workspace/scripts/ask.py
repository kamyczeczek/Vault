#!/usr/bin/env python3
"""Root shim for Knowledge Graph queries.

Delegates to projects/_archive/agentic-research-lab/knowledge/graph/ask.py.
Adds --selftest for workspace integrity validation.

Usage: python scripts/ask.py "<question>" [--limit N] [--raw] [--selftest]
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure agentic-research-lab knowledge graph module is reachable
ARL_GRAPH_DIR = Path(__file__).resolve().parents[0] / "projects" / "_archive" / "agentic-research-lab" / "knowledge" / "graph"
# Wait, Path(__file__) is scripts/ask.py, so parents[0] is scripts/ -> root is parents[1]!
ROOT = Path(__file__).resolve().parents[1]
ARL_GRAPH_PATH = ROOT / "projects" / "_archive" / "agentic-research-lab" / "knowledge" / "graph"

sys.path.insert(0, str(ARL_GRAPH_PATH))

try:
    import ask as arl_ask
except ImportError as e:
    print(f"Error: Could not import graph query module from {ARL_GRAPH_PATH}: {e}", file=sys.stderr)
    sys.exit(1)


def selftest() -> int:
    db_path = ARL_GRAPH_PATH / "graph.db"
    print(f"[selftest] Checking graph DB at {db_path}...")
    if not db_path.exists():
        print(f"[selftest] ERROR: graph.db not found at {db_path}", file=sys.stderr)
        return 1

    print("[selftest] Running sample query 'agent' (must return >= 1 result)...")
    try:
        results = arl_ask.query("agent", limit=3)
        print(f"[selftest] Query returned {len(results)} result(s).")
        if not results:
            print("[selftest] ERROR: expected >= 1 result for 'agent'", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"[selftest] ERROR during query execution: {e}", file=sys.stderr)
        return 1

    print("[selftest] Running non-existent query test 'xyzzyplugh_nonexistent' (must return 0 results)...")
    try:
        none_results = arl_ask.query("xyzzyplugh_nonexistent", limit=3)
        print(f"[selftest] Non-existent query returned {len(none_results)} result(s).")
        if len(none_results) > 0:
            print("[selftest] ERROR: expected 0 results for non-existent term", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"[selftest] ERROR during non-existent query: {e}", file=sys.stderr)
        return 1

    print("[selftest] Running empty query test...")
    try:
        empty_results = arl_ask.query("", limit=3)
        print(f"[selftest] Empty query handled successfully ({len(empty_results)} results).")
    except Exception as e:
        print(f"[selftest] ERROR during empty query: {e}", file=sys.stderr)
        return 1

    print("[selftest] SUCCESS: All checks passed.")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        sys.argv.remove("--selftest")
        return selftest()

    # Delegate directly to ARL ask main or handle arguments
    # We can patch arl_ask.DB if needed, or let arl_ask use its own __file__.
    # Since ARL ask uses Path(__file__).with_name("graph.db"), it will correctly pick up graph.db in ARL knowledge/graph/
    return arl_ask.main()

if __name__ == "__main__":
    sys.exit(main())
