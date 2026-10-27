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
    ("hard", ROOT / "CONTEXT.md", "contract; the H720 protocol, gates, and kill budget"),
    ("hard", ROOT / "_workspace_paths.py",
     "the only place data path and cross-project imports are set"),
    ("hard", ROOT / "members/h2k.py", "incumbent specialist the H720 suite runs"),
    ("hard", ROOT / "members/sab_l.py", "incumbent specialist the H720 suite runs"),
    ("hard", ROOT / "members/amr_24_168.py", "incumbent specialist the H720 suite runs"),
    # Sibling — hard
    ("hard", SIBLINGS / "benchmark-core/members/big_dict_elm.py",
     "h2k.py and sab_l.py import BigDictELM from here (namespace package, not vendored)"),
    ("hard", SIBLINGS / "benchmark-core/members/knn_feature_forecaster.py",
     "h2k.py and sab_l.py import KNNFeatureForecaster from here (namespace package, not vendored)"),
    ("hard", SIBLINGS.parent / "_archive/datasets/data/ETTh1_h1.csv",
     "the only copy of the series; _workspace_paths.data_csv() fails closed without it"),
    # Sibling — optional (recovery)
    ("optional", SIBLINGS.parent / "_archive/datasets/fetch_etth1.py",
     "recovery step: re-fetch ETTh1_h1.csv if the archived copy is missing"),
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
    print(f"etth1-h720 preflight: {verdict} ({missing} hard missing)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
