#!/usr/bin/env python3
"""check_state_freshness.py — block commits when workspace state is stale.

Implements the "measured liveness" insight: a workspace whose state file
is older than 24h is silently decaying. The AI never guesses; the state
carries a date. If the date is old, the state is untrusted.
"""
from __future__ import annotations

import argparse
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "CONTEXT.md"

# Regex: YYYY-MM-DD HH:MM — session owner bullets
HANDOFF_RE = re.compile(r"^###\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s+—", re.MULTILINE)


def parse_handoff_dates(text: str) -> list[datetime]:
    dates = []
    for m in HANDOFF_RE.finditer(text):
        try:
            dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            dates.append(dt)
        except ValueError:
            continue
    return dates


def check_state_freshness(max_age_hours: int = 24) -> bool:
    if not CONTEXT.exists():
        print(f"FAIL: {CONTEXT} missing — no workspace state to verify")
        return False

    text = CONTEXT.read_text(encoding="utf-8")
    dates = parse_handoff_dates(text)
    if not dates:
        print("FAIL: CONTEXT.md has no daily handoff entries (format: YYYY-MM-DD HH:MM — ...)")
        return False

    latest = max(dates)
    now = datetime.now(timezone.utc)
    age = now - latest
    max_age = timedelta(hours=max_age_hours)

    if age > max_age:
        print(f"FAIL: workspace state is stale — last handoff entry is {latest.isoformat()} ({age.total_seconds() / 3600:.1f}h old)")
        print(f"      Update CONTEXT.md daily handoff and re-run quality_check.py")
        return False

    print(f"OK: workspace state is fresh — last handoff {latest.isoformat()} ({age.total_seconds() / 3600:.1f}h old)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify workspace state freshness")
    parser.add_argument("--max-age-hours", type=int, default=24, help="Max age of latest handoff entry (default: 24h)")
    args = parser.parse_args()

    if check_state_freshness(args.max_age_hours):
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
