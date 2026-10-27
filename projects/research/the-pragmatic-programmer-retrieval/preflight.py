"""Standalone preflight for the-pragmatic-programmer-retrieval.

Answer for a cold agent: can work start here, in this tree, right now?
Checks local hard dependencies.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CHECKS: list[tuple[str, Path, str]] = [
    ("hard", ROOT / "CLAUDE.md", "entry file; cannot route without it"),
    ("hard", ROOT / "CONTEXT.md", "contract; open work, phases, metrics"),
    ("hard", ROOT / "pragmatic-programmer.pdf", "monograph PDF input"),
    ("hard", ROOT / "starter/plan_retrieval_z_ksiazki.txt", "step-by-step master plan"),
    ("hard", ROOT / "starter/pragmatic_programmer_gold_set.txt", "gold set starter source"),
    ("hard", ROOT / "starter/graph-memory-starter.txt", "graph memory starter source"),
]


def main() -> int:
    missing = 0
    for severity, path, why in CHECKS:
        ok = path.exists()
        print(f"  [{'ok' if ok else 'MISSING'}] {path.name} ({why})")
        if not ok and severity == "hard":
            missing += 1
    verdict = "NOT READY" if missing else "READY"
    print(f"the-pragmatic-programmer-retrieval preflight: {verdict} ({missing} hard missing)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
