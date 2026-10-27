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
    ("hard", ROOT / "CONTEXT.md", "contract; the retrieval-quality problem, its metrics, its gates"),
    ("hard", ROOT / "references/defect-classes.md", "the failure taxonomy; every gate names a class"),
    ("hard", ROOT / "references/measurements.md", "standing numbers: recall, precision, latency"),
    # Sibling — optional (every measurement command degrades without ARL)
    ("optional", SIBLINGS / "agentic-research-lab/knowledge/graph/run_retrieval_benchmark.py",
     "the measurement surface for retrieval quality"),
    ("optional", SIBLINGS / "agentic-research-lab/knowledge/graph/ask.py",
     "the query surface under measurement"),
    ("optional", SIBLINGS / "agentic-research-lab/scripts/build_quarantine.py",
     "excludes damaged chunks before a measurement round"),
    ("optional", SIBLINGS / "agentic-research-lab/subprojects/vera/benchmark/QUESTIONS.md",
     "the question set benchmark rounds are scored on"),
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
    print(f"knowledge-retrieval preflight: {verdict} ({missing} hard missing)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
