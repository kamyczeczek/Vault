#!/usr/bin/env python3
"""Cost ledger: price shipped insights end-to-end. Ledger, not a metric.

Reads `reflection/cost_ledger.csv` (one row per shipped insight), validates
the schema, and prints derived costs per row. Derived columns are computed,
never stored — the CSV holds inputs and provenance only.

Conventions, enforced here:
- Empty numeric fields mean UNLOGGED, never zero. A blank token_cost_usd
  does not make the insight free; it makes the total uncomputable, and the
  summary says so instead of printing a number.
- `basis` must start with `provisional-` until a second independent row of
  the same insight class exists. n=1 is labeled, not averaged.
- total = token + eval_compute + human (all must be present).
- cost_per_metric_point = total / abs(delta); per_closed_issue = total /
  issues_closed. Both blank when inputs are blank.

This script adds no metric. It divides the ones the gates already produce
by the money and time they cost, once those are logged.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "reflection" / "cost_ledger.csv"

REQUIRED = [
    "insight_id", "phase", "insight_class", "model", "input_tokens", "output_tokens",
    "cached_tokens", "token_cost_usd", "eval_compute_usd", "human_minutes",
    "human_cost_usd", "turns", "llm_calls", "tool_calls", "retrieval_calls",
    "dry_retrievals", "orphan_decisions", "repairs", "eval_runs", "gate_id",
    "metric_before", "metric_after", "delta", "issues_closed", "basis",
    "notes",
]


def num(row: dict, key: str):
    raw = (row.get(key) or "").strip()
    if not raw or raw.startswith("~"):
        return None, ("estimated" if raw.startswith("~") else "missing")
    try:
        return float(raw), "measured"
    except ValueError:
        return None, "invalid"


def summarize(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        total_parts = []
        for k in ("token_cost_usd", "eval_compute_usd", "human_cost_usd"):
            v, _ = num(r, k)
            if v is not None:
                total_parts.append(v)
        total = sum(total_parts) if len(total_parts) == 3 else None
        delta, _ = num(r, "delta")
        issues, _ = num(r, "issues_closed")
        out.append({
            "insight_id": r["insight_id"],
            "insight_class": r.get("insight_class", ""),
            "basis": r["basis"],
            "total_cost_usd": round(total, 2) if total is not None else "UNCOMPUTABLE (unlogged inputs)",
            "cost_per_metric_point": (
                round(total / abs(delta), 2)
                if total is not None and delta else "n/a"
            ),
            "cost_per_closed_issue": (
                round(total / issues, 2)
                if total is not None and issues else "n/a"
            ),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ledger", type=Path, default=LEDGER)
    args = ap.parse_args()
    if not args.ledger.exists():
        print(f"ledger missing: {args.ledger}", file=sys.stderr)
        return 1
    with args.ledger.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("ledger empty: no priced insights yet")
        return 0
    header = rows[0].keys()
    missing = [c for c in REQUIRED if c not in header]
    if missing:
        print(f"schema drift, missing columns: {missing}", file=sys.stderr)
        return 1
    import json
    print(json.dumps(summarize(rows), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
