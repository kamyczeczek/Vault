#!/usr/bin/env python3
"""PreToolUse guard: refuse destructive commands against graded evidence.

Prose rules in CLAUDE.md are necessary and not sufficient. Under pressure — a
gate just failed and the fastest way to a green report is to remove the failure
— a rule is a thing the agent remembers, and remembering is exactly what fails
in the moment it matters. A hook is not remembering. It runs on every attempt.

This is the enforcement point for "a gate-flagged artifact is evidence". It
blocks deletion of files under the graded reflection directories, and flags
`rm -rf` on them as needing explicit user confirmation.

It deliberately does NOT block writes. The agent produces these artifacts; a
guard that stops it writing would just stop the pipeline. The thing that must
not happen is the artifacts *disappearing* after a gate has judged them.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Directories whose contents are graded evidence — deletion is blocked outright.
GUARDED = ("reflection/digests", "reflection/candidates", "reflection/.snapshots")

# Project source-of-truth dirs. Recursive or globbed deletion of these is
# catastrophic: you lose the gate, the corpus, and the pipeline all at once.
# Single-file deletions here are still allowed (a .pyc, a .orig, a .tmp is
# normal build output), but `rm -rf scripts/` or `rm -rf knowledge/` is not.
CRITICAL = ("scripts", "knowledge", "pipeline", "stages", "INBOX", "reflection/trace")

# Destructive verbs: a command whose whole purpose is to make a path go away.
DESTRUCTIVE = re.compile(
    r"(?<![\w.-])(rm|rmdir|del|erase|unlink|shred|trash|truncate)\b"
    r"|Remove-Item\b|Remove-ItemWithError\b|Clear-Content\b|Set-Content\b|Out-File\b",
    re.IGNORECASE,
)
# Recursive or glob flags: the shape that turns one path into many.
# rm: -r, -R, -rf, -fr, -Rf, -fR (r/R must be in the flag, not inside -Force)
# PowerShell: -Recurse
# glob: *
RECURSIVE = re.compile(
    r"(?<![\w-])-{1,2}(?:[a-zA-Z]*r|[a-zA-Z]*R)(?:[a-zA-Z]*f)?\b"  # -r, -R, -rf, -fr, -Rf, -fR
    r"|-Recurse\b"
    r"|\*",
)


def referenced_paths(command: str) -> list[str]:
    """Best-effort extraction of filesystem paths a shell command touches."""
    out: list[str] = []
    # Quoted forms first, then bare tokens: paths in this repo contain no spaces
    # in any graded directory, so a whitespace split is sufficient here.
    for token in re.findall(r'"([^"]+)"|\'([^\']+)\'', command):
        out.append(token[0] or token[1])
    for token in command.split():
        cleaned = token.strip("\"';|&()<>")
        if "/" in cleaned or "\\" in cleaned:
            out.append(cleaned)
    return out


def touches_guarded(command: str) -> list[str]:
    hits: list[str] = []
    for path in referenced_paths(command):
        norm = path.replace("\\", "/")
        for guarded in GUARDED:
            if guarded in norm:
                hits.append(f"{path} -> {guarded}/")
                break
    return hits


def touches_critical_recursive(command: str) -> list[str]:
    """Flag recursive/globbed deletion of source-of-truth directories.

    A single-file delete of `scripts/foo.pyc` is harmless. `rm -rf scripts/`
    is not — it removes every gate, every tool, and every check in one command.
    This check is narrower than the guarded one: it requires both a recursive
    flag AND a critical dir, because a bare `rm scripts/foo.py` is still
    legitimate (the file is tracked, git can restore it).
    """
    if not RECURSIVE.search(command):
        return []
    hits: list[str] = []
    for path in referenced_paths(command):
        norm = path.replace("\\", "/")
        for critical in CRITICAL:
            # Match the top-level directory only, not a subpath of it.
            # `scripts/_scratch/foo` should not trip the guard — only a
            # recursive delete of `scripts/` itself should.
            base = norm.rstrip("/").split("/")[-1]
            if base == critical or critical in norm:
                hits.append(f"recursive delete of {critical}/ ({path})")
                break
    return hits


def main() -> int:
    try:
        raw = sys.stdin.read(64_000)
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # never block on a parse problem

    tool = payload.get("tool_name") or payload.get("tool") or ""
    if tool not in ("Bash", "bash", "Shell", "PowerShell", "powershell"):
        return 0

    tool_input = payload.get("tool_input") or payload.get("input") or {}
    command = tool_input.get("command") or tool_input.get("script") or ""
    if not isinstance(command, str) or not command:
        return 0

    if not DESTRUCTIVE.search(command):
        return 0

    hits = touches_guarded(command)
    if hits:
        recursive = bool(RECURSIVE.search(command))
        detail = ", ".join(sorted(set(hits)))
        reason = (
            f"BLOCKED: this command targets graded reflection evidence ({detail}). "
            "An artifact a gate flagged is evidence, not debris: it is the only record "
            "of what the gate saw. Do not delete it."
        )
        if recursive:
            reason += (
                " This looks recursive/globbed. Recursive removal of graded artifacts "
                "requires explicit user confirmation obtained in-conversation, not agent-initiated."
            )
        reason += (
            " If the artifacts are genuinely superseded, re-run the run that produced them, "
            "or mark the run `failed` and leave the artifacts in place. "
            "Recoverable copies already exist under reflection/.snapshots/."
        )
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))
        return 0

    critical_hits = touches_critical_recursive(command)
    if critical_hits:
        detail = ", ".join(sorted(set(critical_hits)))
        reason = (
            f"BLOCKED: recursive deletion of source-of-truth directories ({detail}). "
            "This removes every gate, tool, and check in one command. If you need to "
            "rebuild or clean up, do it file by file or via `git clean -f` on tracked paths, "
            "never with a recursive glob against a project dir."
        )
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
