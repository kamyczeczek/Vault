"""Standalone preflight for retrieval-v2.

Answer for a cold agent: can work start here, in this tree, right now?
Checks local hard dependencies and sibling links. Siblings live under
``$WORKSPACE_ROOT`` (default: this project's parent directory, i.e.
``projects/research/``). Missing optional siblings degrade the project;
missing hard files block it.

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
    ("hard", ROOT / "scripts", "evaluation scripts directory"),
    ("hard", ROOT / "requirements.txt", "dependency list; needed before running any eval"),
    # Local — optional
    ("optional", ROOT / "reports", "evaluation results; missing means no run completed yet"),
    ("optional", ROOT / "corpus", "exported corpus; missing means eval cannot run"),
    # Sibling — optional
    ("optional", SIBLINGS / "knowledge-retrieval/CLAUDE.md",
     "upstream retrieval-quality project; routing context"),
]


def _shown(path: Path) -> str:
    for base in (ROOT, SIBLINGS, SIBLINGS.parent):
        try:
            if path.is_relative_to(base):
                return str(path.relative_to(base))
        except ValueError:
            pass
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
    print(f"retrieval-v2 preflight: {verdict} ({missing} hard missing)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
