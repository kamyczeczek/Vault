#!/usr/bin/env python3
"""Validate the live-frontier ledger and its compacted manifest."""
from __future__ import annotations

import argparse
from pathlib import Path

from frontier_state import (DEFAULT_FRONTIER, DEFAULT_OPEN_TURN_BOUND, FrontierError,
                            inspect_frontier, status)


ROOT = Path(__file__).resolve().parents[1]


def check_frontier(frontier_dir: Path = DEFAULT_FRONTIER, *, require_ledger: bool = False,
                   bound: int = DEFAULT_OPEN_TURN_BOUND) -> list[str]:
    ledger = frontier_dir / "ledger.jsonl"
    manifest_file = frontier_dir / "manifest.json"
    if not ledger.exists() and not manifest_file.exists():
        return ["frontier is empty"] if not require_ledger else ["frontier ledger is missing"]
    try:
        view = inspect_frontier(frontier_dir, bound)
    except FrontierError as error:
        return [str(error)]
    errors = list(view["errors"])
    records = view["records"]
    if len({record.get("turn_id") for record in records if record.get("record_type") == "turn"}) != sum(
            record.get("record_type") == "turn" for record in records):
        errors.append("turn IDs are not unique")
    if not errors:
        try:
            state = status(frontier_dir, bound)
        except FrontierError as error:
            errors.append(str(error))
        else:
            if state["open_turn_count"] > bound:
                errors.append("open-turn bound exceeded")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier-dir", type=Path, default=DEFAULT_FRONTIER)
    parser.add_argument("--open-turn-bound", type=int, default=DEFAULT_OPEN_TURN_BOUND)
    parser.add_argument("--require-ledger", action="store_true")
    args = parser.parse_args(argv)
    errors = check_frontier(args.frontier_dir, require_ledger=args.require_ledger, bound=args.open_turn_bound)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("frontier ledger valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
