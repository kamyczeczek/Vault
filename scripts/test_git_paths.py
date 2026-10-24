#!/usr/bin/env python3
"""Tests for scripts/git_paths.py — the repo-root vs workspace-root path base.

The live case is the one that motivated ADR-006: a repo whose root is one level
above the directory the script runs in. It is built in a temp dir, so the test
does not depend on this workspace's own layout.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from git_paths import repo_prefix, repo_rel  # noqa: E402


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert p.returncode == 0, f"git {' '.join(args)} failed: {p.stderr}"
    return p.stdout


def _init(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "test")
    (repo / "rootfile.txt").write_text("x", encoding="utf-8")
    (repo / "sub").mkdir()
    (repo / "sub" / "inner.txt").write_text("x", encoding="utf-8")


def test_prefix_is_empty_at_repo_root() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        _init(repo)
        assert repo_prefix(repo) == ""
        assert repo_rel("scripts/x.py", "") == "scripts/x.py"


def test_status_is_repo_relative_ls_files_is_cwd_relative() -> None:
    """The asymmetry that broke close.py and R19 after the vault move."""
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        _init(repo)
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm", "init")
        (repo / "rootfile.txt").write_text("y", encoding="utf-8")
        (repo / "sub" / "inner.txt").write_text("y", encoding="utf-8")

        status = _git(repo / "sub", "status", "--porcelain").splitlines()
        raw = [line[3:] for line in status]
        # Both lines are REPO-relative, including the file that sits outside `sub`.
        assert sorted(raw) == ["rootfile.txt", "sub/inner.txt"], raw

        prefix = repo_prefix(repo / "sub")
        assert prefix == "sub/"
        mapped = [repo_rel(line[3:], prefix) for line in status]
        assert "inner.txt" in mapped
        assert None in mapped  # rootfile.txt is above `sub`, not this close's business

        listed = _git(repo / "sub", "ls-files").split()
        assert listed == ["inner.txt"]  # cwd-relative

        assert repo_rel("rootfile.txt", prefix) is None


def test_rename_and_quoted_paths() -> None:
    prefix = "root_workspace/"
    assert repo_rel('root_workspace/a b.md', prefix) == "a b.md"
    assert repo_rel('"root_workspace/a b.md"', prefix) == "a b.md"
    assert repo_rel("root_workspace/old.md -> root_workspace/new.md", prefix) == "new.md"


def test_find_strays_dir_prefix_and_allow_all() -> None:
    """`--include <dir>` covers its contents; `--include .` covers the workspace.

    Imported late: close.py is a script, not a library, but its stray predicate
    is the part that decides whether a commit may proceed.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import close  # noqa: E402

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        _init(repo)
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm", "init")
        (repo / "rootfile.txt").write_text("y", encoding="utf-8")
        (repo / "sub" / "inner.txt").write_text("y", encoding="utf-8")

        assert len(close.find_strays(repo, set())) == 2
        assert close.find_strays(repo, {"."}) == []
        only_sub = close.find_strays(repo, {"sub"})
        assert len(only_sub) == 1 and "rootfile.txt" in only_sub[0], only_sub


def main() -> int:
    test_prefix_is_empty_at_repo_root()
    test_status_is_repo_relative_ls_files_is_cwd_relative()
    test_rename_and_quoted_paths()
    test_find_strays_dir_prefix_and_allow_all()
    print("PASS: git_paths — prefix, status/ls-files asymmetry, rename/quoted paths, stray prefixes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
