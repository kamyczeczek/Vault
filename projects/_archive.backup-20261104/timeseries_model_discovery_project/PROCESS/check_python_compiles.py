#!/usr/bin/env python3
"""check_python_compiles.py — compile gate for every staged .py file.

WHY THIS GATE EXISTS (the defect it is named for)

This session produced seven edit-tool placement errors. A recurring subclass:
an edit that *succeeds* while destroying an adjacent line, leaving the file
syntactically broken:

    ap.add_argument("--verbose", ...)     # overwritten by the next PUT
    args = ap.parse_args()                # dropped by a PUT N.=M
    ledger_age = (...)                    # dropped by a PUT N.=M

Each was discovered late, by a negative control crashing with NameError —
never by the edit tool, never by ast.parse run in isolation, and never by
any existing gate.

`ast.parse` after each edit caught *some* of them, which created a false
confidence: it validates the region I think I edited, not the file I
actually wrote. Two of the seven dropped lines parsed perfectly and were
invisible until the code ran. That asymmetry is the hazard: the mitigation
that felt sufficient covered the wrong class.

The distinguishing property of the remaining errors is that they are
SILENT — no tool error, no non-zero exit — so no observer can see them.
The only place they become visible is at the moment the code is used. This
gate moves that moment as early as the tooling allows: the commit.

WHAT IT ASSERTS

Every .py file staged in the commit compiles. Nothing more. It does not
lint, does not run tests, does not check behaviour — the gates already in
run_gates.py own those. It is deliberately the narrowest possible check on
the one thing that is cheap to verify and was not verified at all.

SCOPE AND FAIL-SAFE

- Staged files only (git diff --cached): the commit is the boundary being
  protected. Unstaged edits are not the commit's business.
- A file that no longer exists on disk (staged as deleted) is skipped, not
  failed — it cannot be broken.
- A file whose *staged* bytes are broken but whose working-tree copy is fine
  is caught, which is the point: the commit is what ships.
- If git is unavailable or lists nothing, the gate passes. It is a compile
  check, not a substitute for the gate suite.
- `py_compile` compiles to the __pycache__ of the source dir. That is a
  side effect on disk but not on the commit; it never stages anything.

WHAT IT DELIBERATELY DOES NOT CATCH

A line dropped while the file still parses (e.g. a lost
`args = ap.parse_args()`) passes this gate. That class is not detectable by
compilation at all — only by executing the code. The honest invariant for
that class is therefore "edited Python is executed before the session
yields", which is behaviour, not machinery, and is not what this gate is.
"""
from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def staged_py_files() -> list[Path]:
    """Staged .py paths (added/copied/modified/renamed), skipped on git failure."""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        # No git, or not a repo: nothing to verify against.
        return []
    return [REPO / p for p in out.stdout.split("\0") if p and p.endswith(".py")]


def main() -> int:
    files = staged_py_files()
    if not files:
        print("OK: no staged .py files to compile")
        return 0

    broken: list[tuple[str, str]] = []
    for path in files:
        # A staged deletion has no on-disk target to compile.
        if not path.is_file():
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            # First line of the compiler's message is the file:line — enough
            # to name the offending edit without dumping a traceback.
            first = str(exc).strip().splitlines()[0]
            broken.append((str(path.relative_to(REPO)), first))

    if broken:
        print(f"FAIL: {len(broken)} staged .py file(s) do not compile:", file=sys.stderr)
        for rel, msg in broken:
            print(f"  - {rel}: {msg}", file=sys.stderr)
        print("  An edit landed outside its intended range. Fix the file and "
              "re-commit.", file=sys.stderr)
        return 1

    print(f"OK: {len(files)} staged .py file(s) compile")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
