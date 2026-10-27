"""Single place where this project's entry points learn where things are.

Every runner here used to hardcode two things that no longer exist in this
project: a `data/ETTh1_h1.csv` and a `members/` package complete enough to
import. The only copy of the data is `_archive/datasets/data/`, and the
members other than `h2k`, `sab_l` and `amr_24_168` live only in
`benchmark-core/members/` — both resolved against the sibling root, which is
the directory that holds all the projects. Default: this project's parent
(`projects/research/`). Override with the `WORKSPACE_ROOT` environment variable when
the siblings live somewhere else; the preflight check (`preflight.py`) uses
the same rule.

`members` is a namespace package in both projects, so putting both project
roots on `sys.path` resolves `members.h2k` here and `members.big_dict_elm`
there without either project vendoring a file. Do not add `__init__.py` to
either `members/` directory — that would hide one project's modules from the
other and break exactly the imports this module exists to fix.

Import this before any `members.*` import:

    import _workspace_paths  # noqa: F401
"""
from __future__ import annotations

import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
# Sibling root: the directory that holds all the projects. `WORKSPACE_ROOT`
# overrides it; the default (this project's parent) is the usual layout.
SIBLINGS = pathlib.Path(os.environ.get("WORKSPACE_ROOT", str(ROOT.parent)))
BENCHMARK_CORE = SIBLINGS / "benchmark-core"
ARCHIVED_DATA = SIBLINGS.parent / "_archive" / "datasets"
DATA_CSV = ARCHIVED_DATA / "data" / "ETTh1_h1.csv"
RESULTS_DIR = ROOT / "results"


def bootstrap() -> None:
    """Put this project and `benchmark-core` on sys.path; create results/."""
    for path in (ROOT, BENCHMARK_CORE):
        if path.is_dir() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
    RESULTS_DIR.mkdir(exist_ok=True)


def data_csv() -> pathlib.Path:
    """Absolute path to ETTh1_h1.csv, or fail with the fetch step named.

    Failing closed here is deliberate: an H720 number computed on the wrong
    series is not a number worth having.
    """
    if not DATA_CSV.is_file():
        raise SystemExit(
            f"ETTh1_h1.csv not found at {DATA_CSV}. "
            "It is archived, not vendored; re-fetch with "
            f"`python {ARCHIVED_DATA / 'fetch_etth1.py'}`."
        )
    return DATA_CSV


bootstrap()
