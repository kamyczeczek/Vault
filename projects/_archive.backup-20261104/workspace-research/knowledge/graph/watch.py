#!/usr/bin/env python3
"""workspace-research graph watcher.

Rebuild the knowledge graph if any corpus file changed since the last build
(hash-gated). Safe to call from a git post-commit hook on every commit — no-op
when nothing changed.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "knowledge" / "corpus"
STATE = Path(__file__).with_name(".graph_fingerprint")


def current_fingerprint() -> str:
    h = hashlib.sha256()
    for p in sorted(CORPUS.glob("*.md")):
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--once", action="store_true", help="rebuild only if changed, then exit")
    args = ap.parse_args()

    fp = current_fingerprint()
    if STATE.exists() and STATE.read_text().strip() == fp:
        if args.once:
            print("[watch] no change — graph fresh")
            return 0

    import importlib.util
    spec = importlib.util.spec_from_file_location("build_graph", Path(__file__).with_name("build_graph.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        mod.build()
    except Exception as exc:
        print(f"[watch] REBUILD FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print("[watch] graph rebuilt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
