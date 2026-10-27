"""Make this project's tests importable without a manual sys.path dance.

The test modules import `members.h2k` / `members.sab_l` (here) and
`members.big_dict_elm` / `members.amr_fbs` (in `../benchmark-core`). `members`
is a namespace package in both, so putting both project roots on sys.path
resolves every one of them. See `_workspace_paths.py` for why there is no
`__init__.py` in either `members/`.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for _path in (ROOT, ROOT.parent / "benchmark-core"):
    if _path.is_dir() and str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
