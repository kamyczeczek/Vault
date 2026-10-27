#!/usr/bin/env python3
"""Create a gate-verified Git checkpoint from explicitly staged files."""
from __future__ import annotations

import argparse
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPE_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
FORBIDDEN_STAGED = re.compile(
    r"(^|/)(\.env(?:\.|$)|\.pem$|\.key$|id_rsa(?:\.|$)|"
    r"graph\.db$|graph_index\.json$|events\.jsonl$|"
    r"__pycache__(?:/|$)|\.pytest_cache(?:/|$)|"
    r"[^/]+\.(?:log|tmp|swp|swo)$)"
)


def run(command: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        input=input_text,
        capture_output=True,
    )


def git(*args: str, check: bool = True, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    result = run(["git", *args], input_text=input_text)
    if check and result.returncode:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({result.returncode}):\n"
            f"{result.stdout}{result.stderr}"
        )
    return result


def git_paths(*args: str) -> list[str]:
    output = git(*args).stdout
    return [
        item.decode("utf-8", errors="surrogateescape")
        for item in output.encode("utf-8", errors="surrogateescape").split(b"\0")
        if item
    ]


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def unstage(paths: list[str]) -> None:
    """Undo this run's own `git add` (index left as found).

    Measured defect 2026-10-05: a failed run left the explicitly staged
    files in the index, and the next unrelated raw `git commit` shipped
    them by accident. Every pre-commit failure rolls back its own
    staging first; pre-existing staged work of other sessions is
    untouched.
    """
    git("reset", "-q", "HEAD", "--", *paths, check=False)


def validate_stage_path(raw_path: str) -> str:
    if not raw_path or raw_path in {".", "./", "..", "../"}:
        raise ValueError(f"unsafe staging path: {raw_path!r}")
    if Path(raw_path).is_absolute():
        raise ValueError(f"staging path must be relative: {raw_path!r}")
    if any(character in raw_path for character in "*?[]"):
        raise ValueError(f"glob staging is not allowed: {raw_path!r}")

    path = Path(raw_path)
    if path.is_dir():
        raise ValueError(f"stage individual files, not directories: {raw_path!r}")
    deleted = git("ls-files", "--deleted", "--", raw_path, check=False)
    if not path.exists() and deleted.returncode != 0:
        raise ValueError(f"staging path does not exist or is not tracked as deleted: {raw_path!r}")

    ignored = git("check-ignore", "--quiet", "--", raw_path, check=False)
    if ignored.returncode == 0:
        raise ValueError(f"refusing to stage ignored runtime artifact: {raw_path!r}")
    if FORBIDDEN_STAGED.search(raw_path.replace("\\", "/")):
        raise ValueError(f"refusing to stage sensitive or transient path: {raw_path!r}")
    return raw_path.replace("\\", "/")


def working_tree_has_untracked() -> list[str]:
    status = git("status", "--porcelain", "--untracked-files=all", check=False)
    if status.returncode:
        raise RuntimeError(f"git status failed ({status.returncode}):\n{status.stderr}")
    return [line[3:] for line in status.stdout.splitlines() if line.startswith("?? ")]


def graph_metrics() -> tuple[str, int | None, int | None, int | None]:
    fingerprint_path = ROOT / "knowledge" / "graph" / ".graph_fingerprint"
    fingerprint = fingerprint_path.read_text(encoding="utf-8").strip() if fingerprint_path.exists() else "none"
    database = ROOT / "knowledge" / "graph" / "graph.db"
    if not database.exists():
        return fingerprint, None, None, None
    try:
        connection = sqlite3.connect(database)
        try:
            nodes = connection.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
            edges = connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        finally:
            connection.close()
        chunks = len(list((ROOT / "knowledge" / "corpus").glob("*.md")))
        return fingerprint, chunks, nodes, edges
    except sqlite3.Error:
        return fingerprint, None, None, None


def build_message(scope: str, summary: str, trigger: str, artifacts: list[str], metrics: tuple[str, int | None, int | None, int | None]) -> str:
    fingerprint, chunks, nodes, edges = metrics
    metrics_text = f"fingerprint {fingerprint}"
    if chunks is not None:
        metrics_text += f"; chunks {chunks}"
    if nodes is not None:
        metrics_text += f"; nodes {nodes}"
    if edges is not None:
        metrics_text += f"; edges {edges}"
    artifact_text = ", ".join(artifacts)
    return (
        f"[{scope}] {summary}\n\n"
        f"- Trigger: {trigger}\n"
        f"- Artifacts: {artifact_text}\n"
        "- Verification: python scripts/quality_check.py (PASS)\n"
        f"- State Metrics: {metrics_text}\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", required=True, help="phase or artifact scope, e.g. 03_graph")
    parser.add_argument("--message", required=True, help="imperative commit summary")
    parser.add_argument("--trigger", help="event or input artifact that caused this checkpoint")
    parser.add_argument("--stage", nargs="+", required=True, metavar="PATH", help="individual files to stage")
    parser.add_argument("--dry-run", action="store_true", help="validate and print the commit without committing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not SCOPE_RE.fullmatch(args.scope):
        return fail("scope must match ^[a-z0-9][a-z0-9_-]*$")
    if not args.message.strip() or "\n" in args.message:
        return fail("message must be one non-empty imperative line")

    try:
        paths = [validate_stage_path(path) for path in args.stage]
    except (RuntimeError, ValueError) as error:
        return fail(str(error))

    try:
        git("add", "--", *paths)
        staged = git_paths("diff", "--cached", "--name-only", "-z")
    except RuntimeError as error:
        return fail(str(error))
    if not staged:
        return fail("the requested paths produced no staged changes")

    # Every failure from here on rolls back this run's own `git add` so the
    # index is left exactly as found. Pre-existing staged work of other
    # sessions is never touched; if the caller had pre-staged one of these
    # very paths, it is unstaged too — the run failed, and residue is the
    # defect this guard exists to prevent.
    def rollback_fail(message: str) -> int:
        unstage(paths)
        return fail(message)

    untracked = working_tree_has_untracked()
    if untracked:
        return rollback_fail("untracked files remain outside the explicit stage: "
                             + ", ".join(untracked[:8]))

    # Only paths actually being ADDED to the index may not be ignored files.
    # An untracking (`git rm --cached` of a file that is now in .gitignore)
    # also appears in `diff --cached --name-only`, but as a deletion.
    # Refusing that would make it impossible to ever move a file from
    # tracked to generated: the index holds the deletion, .gitignore matches
    # the path, and a naive check calls it "an ignored file entered the
    # index" — blocking exactly the operation the caller intended.
    # --diff-filter=ACMR restricts the check to adds, copies, modifications
    # and renames, which is what "entered the index" means.
    added = set(git_paths("diff", "--cached", "--name-only", "-z",
                       "--diff-filter=ACMR"))
    ignored_added = [path for path in staged
                     if path in added
                     and git("check-ignore", "--quiet", "--",
                              path, check=False).returncode == 0]
    if ignored_added:
        return rollback_fail("ignored files entered the index: "
                              + ", ".join(ignored_added[:8]))
    forbidden = [path for path in staged if FORBIDDEN_STAGED.search(path)]
    if forbidden:
        return rollback_fail("sensitive or transient files entered the index: " + ", ".join(forbidden[:8]))

    whitespace = git("diff", "--cached", "--check", check=False)
    # Imported corpus/raw artifacts preserve source formatting. Their whitespace
    # is content, not executable-code hygiene; enforce this gate on project
    # source and workflow files only. The same holds for .dgc-evidence/ run
    # dumps (fetched HTML/pages land with trailing whitespace by nature;
    # byte fidelity matters for evidence audit, so they are exempt too).
    checked_paths = [path for path in staged if not path.replace("\\", "/").startswith(("knowledge/corpus/", "knowledge/raw/", ".dgc-evidence/"))]
    if checked_paths:
        patch = git("diff", "--cached", "--check", "--", *checked_paths, check=False)
        if patch.returncode:
            return rollback_fail(f"staged whitespace errors:\n{patch.stdout}{patch.stderr}")

    gate = run([sys.executable, str(ROOT / "scripts" / "quality_check.py")])
    if gate.returncode:
        print(gate.stdout, end="")
        print(gate.stderr, end="", file=sys.stderr)
        return rollback_fail(f"quality gate failed with exit {gate.returncode}")

    trigger = args.trigger or f"checkpoint requested for {args.scope}"
    metrics = graph_metrics()
    message = build_message(args.scope, args.message.strip(), trigger, staged, metrics)
    if args.dry_run:
        print("DRY RUN: gate passed; commit would contain:")
        print("\n".join(f"  {path}" for path in staged))
        print("\nCommit message:\n" + message)
        return 0

    commit = git("commit", "--no-edit", "-F", "-", input_text=message, check=False)
    if commit.returncode:
        print(commit.stdout, end="")
        print(commit.stderr, end="", file=sys.stderr)
        return fail(f"git commit failed with exit {commit.returncode}")
    print(commit.stdout, end="")
    print("Checkpoint commit created after the full quality gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
