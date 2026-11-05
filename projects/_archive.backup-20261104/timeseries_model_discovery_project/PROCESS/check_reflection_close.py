#!/usr/bin/env python3
"""
check_reflection_close.py — Reflection close gate.

Validates that the most recent reflection file is schema-complete and that
brain/verify_sync.py exits 0.

Exit 0: reflection complete and brain in sync.
Exit 1: reflection missing, schema incomplete, or brain out of sync.

Usage:
    python PROCESS/check_reflection_close.py
    python PROCESS/check_reflection_close.py --quiet
"""
from __future__ import annotations

import argparse
import io
import runpy
import sys
import contextlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REFLECTION_DIR = REPO_ROOT / "MONITORING" / "reflection"
VERIFY_SYNC = REPO_ROOT / "brain" / "verify_sync.py"
TRIGGER_CHECK = REPO_ROOT / "PROCESS" / "check_reflection_trigger.py"

REQUIRED_FIELDS = [
    "work_summary",
    "problems",
    "solutions",
    "prevention_rules",
    "next_action_routing_changes",
    "open_risks",
]


def latest_reflection() -> Path | None:
    candidates = [
        p for p in REFLECTION_DIR.glob("*.md")
        if p.name not in ("REFLECTION_RULES.md", "_template.md", "CONTEXT.md")
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def schema_complete(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return all(f"## {f}" in text for f in REQUIRED_FIELDS)


def run_in_process(script: Path, argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    old_argv, old_exit = sys.argv, sys.exit
    sys.argv = [str(script)] + argv
    sys.exit = lambda code=0: (_ for _ in ()).throw(SystemExit(code))
    gate_dir = str(script.parent)
    sys.path.insert(0, gate_dir)
    modules_before = set(sys.modules)
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            runpy.run_path(str(script), run_name="__main__")
        code = 0
    except SystemExit as e:
        code = int(e.code) if e.code is not None else 0
    except Exception as e:
        code = 2
        buf.write(f"[run_gates] FAIL: {type(e).__name__}: {e}\n")
    finally:
        sys.argv = old_argv
        sys.exit = old_exit
        sys.path.remove(gate_dir)
        for name in list(sys.modules):
            if name not in modules_before and (name.startswith("verify_sync") or name.startswith("check_reflection_trigger")):
                del sys.modules[name]
    return code, buf.getvalue()


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="check_reflection_close")
    ap.add_argument("--quiet", action="store_true", help="suppress PASS output")
    ap.add_argument("--task-dir", type=Path, help="task artifact directory")
    ap.add_argument("--status", choices=["complete", "yielded-partial", "blocked"])
    ap.add_argument("--problem-ids", help="comma-separated problem ids")
    ap.add_argument("--contract-changed", action="store_true")
    ap.add_argument("--user-requested", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    # Check if reflection is required by trigger
    trigger_argv = []
    if args.task_dir:
        trigger_argv += ["--task-dir", str(args.task_dir)]
    if args.status:
        trigger_argv += ["--status", args.status]
    if args.problem_ids:
        trigger_argv += ["--problem-ids", args.problem_ids]
    if args.contract_changed:
        trigger_argv.append("--contract-changed")
    if args.user_requested:
        trigger_argv.append("--user-requested")

    trigger_code, trigger_output = run_in_process(TRIGGER_CHECK, trigger_argv)

    if trigger_code != 0:
        if not args.quiet:
            print("reflection_close: ok — no reflection trigger fired")
        return 0

    # Reflection is required; verify it exists and is schema-complete
    ref = latest_reflection()
    if ref is None:
        print("reflection_close: FAIL — trigger fired but no reflection file in MONITORING/reflection/")
        print(trigger_output)
        return 1

    if not schema_complete(ref):
        print(f"reflection_close: FAIL — schema incomplete in {ref.name}")
        return 1

    if not args.quiet:
        print(f"reflection_close: ok — {ref.name}")

    verify_argv = ["--quiet"] if args.quiet else []
    code, output = run_in_process(VERIFY_SYNC, verify_argv)
    if code != 0:
        print(f"reflection_close: FAIL — verify_sync exit {code}")
        print(output)
        return 1

    if not args.quiet:
        print("reflection_close: ok — brain/verify_sync.py --quiet exit 0")

    return 0


if __name__ == "__main__":
    sys.exit(main())
