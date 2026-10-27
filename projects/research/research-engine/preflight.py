"""Standalone preflight for this project.

Answer for a cold agent: can work start here, in this tree, right now?
Checks local hard dependencies, then sibling links this project's docs
point at. Siblings live under ``$WORKSPACE_ROOT`` (default: this
project's parent directory, i.e. ``projects/research/``). Missing optional
siblings degrade the project; missing hard files block it.

    python preflight.py              # report + exit code
    WORKSPACE_ROOT=... preflight.py  # point at a different siblings tree
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIBLINGS = Path(os.environ.get("WORKSPACE_ROOT", ROOT.parent))

# (severity, path, why it matters). Only "hard" counts toward the exit code.
CHECKS: list[tuple[str, Path, str]] = [
    # Local — hard
    ("hard", ROOT / "CLAUDE.md", "entry file; cannot route without it"),
    ("hard", ROOT / "CONTEXT.md", "contract; mutation cycle, leakage rules, promotion criteria"),
    ("hard", ROOT / "research_engine.py", "ModelDiscoveryEngine + AntiLeakageHarness"),
    ("hard", ROOT / "mutation_engine.py", "heuristic model mutation, emits proposals"),
    ("hard", ROOT / "kg.py", "knowledge-graph query surface; the loop's index entry point"),
    # Sibling — optional (these tools degrade without them)
    ("optional", SIBLINGS / "agentic-research-lab/knowledge/graph/graph.db",
     "query tools (kg.py, query_*.py, check_tables.py) point at it and degrade"),
    ("optional", SIBLINGS / "agentic-research-lab/knowledge/graph/build_graph.py",
     "run_s47_suite.py shells out to it; the suite degrades"),
    ("optional", SIBLINGS / "benchmark-core/members",
     "s47_ref/rolling_arm.py loads the incumbent members from here"),
    ("optional", SIBLINGS.parent / "_archive/datasets/data/ETTh1_h1.csv",
     "the s47 ETTh1 task runs on this series"),
]


def _shown(path: Path) -> str:
    for base in (ROOT, SIBLINGS, SIBLINGS.parent):
        if path.is_relative_to(base):
            return str(path.relative_to(base))
    return str(path)


def main() -> int:
    missing = 0
    for severity, path, why in CHECKS:
        ok = path.exists()
        base = "local" if path.is_relative_to(ROOT) else "ext  "
        print(f"  [{'ok' if ok else 'MISSING'}] {base} {_shown(path)}  ({why})")
        if not ok and severity == "hard":
            missing += 1
    verdict = "NOT READY" if missing else "READY"
    print(f"research-engine preflight: {verdict} ({missing} hard missing)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
