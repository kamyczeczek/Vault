#!/usr/bin/env python3
"""Gate: the knowledge layer lives in `kb/`, and nothing live still points at the old root paths.

ADR-008 replaces ADR-006. `Desktop\\vault` stays the git root and the agent
workspace; the knowledge layer Obsidian reads (`.obsidian`, `.smart-env`,
`Notes`, `library`) moves into the `kb/` subfolder. That is a path contract, and
a path contract with no executable check decays into prose the first time
someone writes `Notes/OKF-rag` in a new script.

Subcommands:

  --layout    `kb/` holds the four knowledge dirs, the root does not, and the
              Obsidian vault root is therefore `kb/.obsidian`.
  --stale     no *live surface* names the old unprefixed paths. History is not a
              live surface: `handoff/`, `docs/`, `brain/decisions/` and the ADR
              record what was true when it was written, and rewriting a record to
              match today's layout would destroy the evidence that the move
              happened.
  --selftest  negative control: the stale matcher must flag a known positive.
              Without it, a broken matcher and a clean tree look identical.

Exit 0 and a single success marker only when every assertion in the requested
mode passes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The four knowledge dirs and a file inside each that proves the move carried
# content, not an empty directory shell.
KB_CONTENT = {
    ".obsidian": ".obsidian/app.json",
    ".smart-env": ".smart-env/smart_env.json",
    "Notes": "Notes/OKF-rag/okf-rag.md",
    "library": "library/index.json",
}

# Paths the agent reads or executes on every session. A stale path here is a
# live bug; everywhere else it is history.
LIVE_GLOBS = (
    "scripts/**/*.py",
    "tools/**/*.py",
    "hooks/*",
    "skills/**/*.py",
    "skills/**/*.md",
    "skills/**/*.bat",
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "CONTEXT-MAP.md",
    ".gitignore",
)

# A reference is stale when it names one of the moved dirs at the workspace root
# (`Notes/x`, `` `library/` ``, `ROOT / ".smart-env"`) without the `kb/` prefix.
STALE_CASES: tuple[tuple[str, re.Pattern[str]], ...] = (
    # A path segment beginning at the repo root: `Notes/`, `library/`, `README`
    # followed by a slash. `kb/Notes/` is fine because the segment start is `kb`.
    (
        "root-relative segment",
        re.compile(r"(?<![\w./-])(?:Notes|library)/(?![\w-]*\.\.)"),
    ),
    # A Path join against ROOT/root that was not updated.
    (
        "ROOT join",
        re.compile(r"ROOT\s*/\s*[\"'](?:Notes|library|\.obsidian|\.smart-env)[\"']"),
    ),
    # A bare hidden-dir mention (config files, docs describing the vault root).
    (
        "hidden dir",
        re.compile(r"(?<![\w./-])(?:\.obsidian|\.smart-env)/"),
    ),
)


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _iter_live() -> list[Path]:
    seen: dict[Path, None] = {}
    for pattern in LIVE_GLOBS:
        for path in ROOT.glob(pattern):
            if not path.is_file():
                continue
            rel = _rel(path)
            if rel.startswith(("scripts/_scratch/", "kb/")):
                continue
            # This file is the oracle: its docstring and STALE_CASES name the old
            # spellings on purpose, so scanning it would make it flag itself.
            if rel == "scripts/check_kb_layout.py":
                continue
            seen[path] = None
    return sorted(seen)


def check_layout() -> list[str]:
    fails: list[str] = []
    for name, needle in KB_CONTENT.items():
        if not (ROOT / "kb" / needle).is_file():
            fails.append(f"kb/{needle} is missing — kb/{name}/ did not move with its content")
        if (ROOT / name).exists():
            fails.append(f"{name}/ still exists at the workspace root (expected only under kb/)")
    if not (ROOT / "kb" / ".obsidian" / "workspace.json").exists():
        # Obsidian writes this on first open of a vault. Its absence is a WARN in
        # the report, not a failure: the file is per-device and gitignored, so a
        # fresh clone legitimately has none until the app opens kb/.
        print("  note: kb/.obsidian/workspace.json absent — Obsidian has not opened kb/ on this clone yet")
    return fails


def check_stale() -> list[str]:
    fails: list[str] = []
    for path in _iter_live():
        rel = _rel(path)
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for label, pattern in STALE_CASES:
                match = pattern.search(line)
                if match is None:
                    continue
                # An explicit kb/ prefix is the post-move spelling.
                start = max(0, match.start() - 3)
                if line[start : match.start()].endswith("kb/"):
                    continue
                fails.append(f"{rel}:{lineno}: stale {label} {match.group(0)!r} — use kb/{match.group(0)}")
    return fails


def selftest() -> int:
    """The stale matcher must catch a known positive and pass a known negative."""
    positive = 'NOTES = ROOT / "Notes" / "OKF-rag"'
    negative = 'NOTES = ROOT / "kb" / "Notes" / "OKF-rag"'
    caught = any(p.search(positive) for _, p in STALE_CASES)
    false_alarm = any(p.search(negative) for _, p in STALE_CASES)
    print(f"selftest: positive caught={caught} negative clean={not false_alarm}")
    if caught and not false_alarm:
        print("KB-SELFTEST OK")
        return 0
    print("KB-SELFTEST FAIL")
    return 1


def main(argv: list[str]) -> int:
    modes = [arg for arg in argv[1:] if arg.startswith("--")]
    if not modes:
        print("usage: check_kb_layout.py --layout | --stale | --selftest")
        return 2
    if "--selftest" in modes:
        return selftest()

    fails: list[str] = []
    marker: list[str] = []
    if "--layout" in modes:
        fails.extend(check_layout())
        marker.append("KB-LAYOUT OK")
    if "--stale" in modes:
        fails.extend(check_stale())
        marker.append("KB-STALE OK")

    if fails:
        print("KB CHECK FAIL:")
        for line in fails:
            print(f"  - {line}")
        return 1
    print(" · ".join(marker))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
