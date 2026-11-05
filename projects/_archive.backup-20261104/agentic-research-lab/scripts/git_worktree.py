#!/usr/bin/env python3
"""Create and remove agent worktrees without touching the main working tree."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=check,
    )


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def repo_root() -> Path:
    return Path(run(["git", "rev-parse", "--show-toplevel"]).stdout.strip()).resolve()


def dirty_paths(cwd: Path) -> list[str]:
    result = run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=cwd, check=False)
    if result.returncode:
        raise RuntimeError(f"git status failed in {cwd}: {result.stderr.strip()}")
    return [line[3:] for line in result.stdout.splitlines() if line]


def require_clean(cwd: Path) -> None:
    dirty = dirty_paths(cwd)
    if dirty:
        raise RuntimeError(f"working tree must be clean before this operation: {', '.join(dirty[:8])}")


def branch_exists(root: Path, branch: str) -> bool:
    result = run(["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=root, check=False)
    return result.returncode == 0


def default_path(root: Path, name: str) -> Path:
    return root / ".worktrees" / name


def create(args: argparse.Namespace) -> int:
    root = repo_root()
    if not NAME_RE.fullmatch(args.name):
        return fail("name must contain only letters, digits, dots, underscores, or hyphens")
    branch = f"agent/{args.name}"
    path = Path(args.path).resolve() if args.path else default_path(root, args.name)
    try:
        require_clean(root)
        if path.exists():
            return fail(f"worktree path already exists: {path}")
        if branch_exists(root, branch):
            return fail(f"branch already exists: {branch}")
        path.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "worktree", "add", "-b", branch, str(path), "HEAD"], cwd=root)
    except (RuntimeError, subprocess.CalledProcessError) as error:
        return fail(str(error))
    print(f"created worktree {path} on {branch}")
    return 0


def list_worktrees(_: argparse.Namespace) -> int:
    try:
        result = run(["git", "worktree", "list", "--porcelain"])
    except subprocess.CalledProcessError as error:
        return fail(error.stderr.strip() or "could not list worktrees")
    print(result.stdout, end="")
    return 0


def remove(args: argparse.Namespace) -> int:
    root = repo_root()
    path = Path(args.path).resolve() if args.path else default_path(root, args.name)
    branch = f"agent/{args.name}"
    try:
        require_clean(path)
        run(["git", "worktree", "remove", str(path)], cwd=root)
    except (RuntimeError, subprocess.CalledProcessError) as error:
        return fail(str(error))

    merged = run(["git", "branch", "--merged", "HEAD", "--list", branch], cwd=root)
    if branch in {line.strip() for line in merged.stdout.splitlines()}:
        deleted = run(["git", "branch", "-d", branch], cwd=root, check=False)
        if deleted.returncode:
            print(f"removed worktree; retained unmerged branch {branch}")
        else:
            print(f"removed worktree and merged branch {branch}")
    else:
        print(f"removed worktree; retained branch {branch}")
    return 0


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    subcommands = command.add_subparsers(dest="command", required=True)

    create_parser = subcommands.add_parser("create", help="create an isolated agent worktree")
    create_parser.add_argument("--name", required=True)
    create_parser.add_argument("--path", help="override the default .worktrees/<name> path")
    create_parser.set_defaults(function=create)

    list_parser = subcommands.add_parser("list", help="list registered worktrees")
    list_parser.set_defaults(function=list_worktrees)

    remove_parser = subcommands.add_parser("remove", help="remove a clean agent worktree")
    remove_parser.add_argument("--name", required=True)
    remove_parser.add_argument("--path", help="use a custom worktree path")
    remove_parser.set_defaults(function=remove)
    return command


def main() -> int:
    args = parser().parse_args()
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
