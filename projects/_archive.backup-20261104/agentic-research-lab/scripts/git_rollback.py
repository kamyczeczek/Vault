#!/usr/bin/env python3
"""Revert one commit without rewriting history or cleaning the working tree."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True)


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def dirty_paths(cwd: Path) -> list[str]:
    result = run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=cwd)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git status failed")
    return [line[3:] for line in result.stdout.splitlines() if line]


def revert(args: argparse.Namespace) -> int:
    try:
        resolved = run(["git", "rev-parse", "--verify", f"{args.commit}^{{commit}}"])
    except subprocess.CalledProcessError as error:
        return fail(f"commit does not resolve: {args.commit}")
    commit = resolved.stdout.strip().splitlines()[0]
    try:
        dirty = dirty_paths(Path(args.worktree).resolve())
    except RuntimeError as error:
        return fail(str(error))
    if dirty:
        return fail(f"worktree must be clean before revert: {', '.join(dirty[:8])}")

    result = run(["git", "revert", "--no-edit", commit], cwd=Path(args.worktree).resolve())
    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
    if result.returncode:
        return fail(f"revert stopped before creating a commit (exit {result.returncode}); resolve conflicts or run git revert --abort")
    print(f"created a history-preserving revert of {commit}")
    return 0


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    subcommands = command.add_subparsers(dest="command", required=True)
    revert_parser = subcommands.add_parser("revert", help="revert one commit with a new commit")
    revert_parser.add_argument("--commit", required=True, help="commit hash or ref to revert")
    revert_parser.add_argument("--worktree", default=str(ROOT), help="worktree to revert in")
    revert_parser.set_defaults(function=revert)
    return command


def main() -> int:
    args = parser().parse_args()
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
