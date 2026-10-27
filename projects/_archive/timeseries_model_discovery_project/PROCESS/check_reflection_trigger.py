#!/usr/bin/env python3
"""
check_reflection_trigger.py — Determine if a reflection is required.

Evaluates REFLECTION_RULES.md R1 triggers against task artifacts.
Exit 0 = reflection required; exit 1 = no reflection needed.

Usage:
    python PROCESS/check_reflection_trigger.py --task-dir <path>
    python PROCESS/check_reflection_trigger.py --status complete --problem-ids P1,P2
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REFLECTION_DIR = Path(__file__).resolve().parent.parent / "MONITORING" / "reflection"


def has_reflection_file() -> bool:
    return any(REFLECTION_DIR.glob("*.md"))


def has_schema_reflection() -> bool:
    for p in REFLECTION_DIR.glob("*.md"):
        if p.name in ("REFLECTION_RULES.md", "_template.md", "CONTEXT.md"):
            continue
        text = p.read_text(encoding="utf-8")
        if "## work_summary" in text and "## problems" in text:
            return True
    return False


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="check_reflection_trigger")
    ap.add_argument("--task-dir", type=Path, help="task artifact directory")
    ap.add_argument("--status", choices=["complete", "yielded-partial", "blocked"], help="task status")
    ap.add_argument("--problem-ids", help="comma-separated problem ids")
    ap.add_argument("--contract-changed", action="store_true", help="contract/routing changed")
    ap.add_argument("--user-requested", action="store_true", help="user explicitly requested reflection")
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    if args.user_requested:
        print("trigger=T4 user-requested reflection required=yes")
        return 0

    if args.contract_changed:
        print("trigger=T5 contract-changed reflection required=yes")
        return 0

    if args.status == "complete":
        print("trigger=T1 task-complete reflection required=yes")
        return 0

    if args.status in ("yielded-partial", "blocked"):
        print(f"trigger=T2 task-{args.status} reflection required=yes")
        return 0

    if args.problem_ids:
        ids = [x.strip() for x in args.problem_ids.split(",") if x.strip()]
        if ids:
            print(f"trigger=T3 problems-solved reflection required=yes ids={ids}")
            return 0

    # T6: problem lifecycle event — checked by caller via problem file state

    if has_schema_reflection():
        print("reflection-required=no existing-reflection-found")
        return 1

    print("reflection-required=no triggers-met")
    return 1


if __name__ == "__main__":
    sys.exit(main())
