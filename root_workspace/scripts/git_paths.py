"""Path bases for a repo whose root is not the workspace root (ADR-006).

`git status --porcelain` and any `git ... --name-only` print paths relative to
the **repository** root, while `git ls-files` and pathspecs are relative to the
**current working directory**. While `ROOT` was the repo root the two bases
coincided, so scripts could compare git output with a workspace-relative path
directly. After the vault becomes the repo root (`ROOT` = `<vault>/root_workspace`)
they no longer do, and that comparison fails silently: `M scripts/x.py` arrives as
`M root_workspace/scripts/x.py`.

Every such comparison goes through `repo_rel()`.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def repo_prefix(root: Path) -> str:
    """`git rev-parse --show-prefix` run in `root`: `""` at the repo root.

    Anything else (e.g. `"root_workspace/"`) is the prefix git prepends to paths
    it prints, because it prints them relative to the repo root, not to `root`.
    """
    p = subprocess.run(["git", "rev-parse", "--show-prefix"],
                       capture_output=True, text=True, cwd=str(root))
    return p.stdout.strip() if p.returncode == 0 else ""


def repo_rel(path: str, prefix: str) -> str | None:
    """Map a repo-relative path to a `root`-relative path.

    Returns `None` when the path lies outside `root` (a vault-level file while
    `root` is the workspace). Rename lines (`old -> new`) resolve to the
    destination, which is the path that lands. Quoted paths are unquoted.
    """
    path = path.strip().strip('"')
    if " -> " in path:
        path = path.split(" -> ")[-1].strip().strip('"')
    if not prefix:
        return path
    if path.startswith(prefix):
        return path[len(prefix):]
    return None
