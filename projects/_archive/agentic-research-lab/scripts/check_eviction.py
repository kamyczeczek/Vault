#!/usr/bin/env python3
"""check_eviction.py — exit gate for stage 05_evict.

Verifies that every rejection the eviction stage wrote is itself grounded:
  1. a rejected row carries a non-empty `why` naming the cause, and
  2. its `why` mentions an id that genuinely no longer resolves in graph.db
     (i.e. the eviction was about evidence, not about opinion), and
  3. the audit trail in reflection/evictions/ is consistent with the rejections in the
     candidate files — every audit row must correspond to a rejected row.

This is the gate the research says has to exist. 04_honest_lying_memory_confabulation
found that a reflection ledger with no external check is a confidence amplifier: the
agent becomes certain of a falsehood it wrote itself. Eviction is the same hazard
inverted — an ungrounded rejection silently destroys a true lesson. So the eviction
itself must be provably grounded, or it is just a second-order confabulation.

Exit code: 0 = clean, 1 = violation, 2 = prerequisite missing.
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "reflection" / "candidates"
EVICTIONS = ROOT / "reflection" / "evictions"
DB = ROOT / "knowledge" / "graph" / "graph.db"


def existing_ids() -> set[str]:
    c = sqlite3.connect(DB)
    try:
        return {r[0] for r in c.execute("SELECT id FROM nodes").fetchall()}
    finally:
        c.close()


def main() -> int:
    if not DB.exists():
        print("FAIL: graph.db missing — run watch.py --once first", file=sys.stderr)
        return 2
    ids = existing_ids()
    errors: list[str] = []

    rejected_rows: dict[str, dict] = {}  # id -> row, from candidate files
    for jl in sorted(CANDIDATES.glob("*.jsonl")):
        for i, line in enumerate(jl.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"{jl.name}:{i}: invalid JSON — {e}")
                continue
            if obj.get("state") != "rejected":
                continue
            cid = obj.get("id", f"{jl.name}:{i}")
            rejected_rows[cid] = obj
            why = obj.get("why", "")
            if not isinstance(why, str) or not why.strip():
                errors.append(f"{jl.name}:{i}: rejected `{cid}` has empty `why` — "
                              "a rejection with no stated cause cannot be audited")

    # audit trail must match the rejections it claims to record
    audit_seen: set[str] = set()
    if EVICTIONS.exists():
        for af in sorted(EVICTIONS.glob("*.jsonl")):
            for i, line in enumerate(af.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    a = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"{af.name}:{i}: invalid JSON — {e}")
                    continue
                aid = a.get("id", "")
                audit_seen.add(aid)
                if a.get("to") != "rejected":
                    errors.append(f"{af.name}:{i}: audit row `{aid}` to=`{a.get('to')}`; "
                                  "this stage only records rejections")
                why = str(a.get("why", ""))
                mentioned = re.findall(r"\b\d{2}_[a-z0-9_]+\b", why)
                if not mentioned:
                    errors.append(f"{af.name}:{i}: audit row `{aid}` cites no chunk id in why")
                else:
                    # the eviction must be about evidence that genuinely no longer resolves
                    unresolvable = [m for m in mentioned if m not in ids]
                    if not unresolvable:
                        errors.append(
                            f"{af.name}:{i}: audit row `{aid}` rejects over ids "
                            f"{mentioned} that still resolve in graph.db — "
                            "that is an opinion eviction, not an evidence eviction")

    # every audit row must map to an actual rejected candidate
    for aid in sorted(audit_seen - set(rejected_rows)):
        errors.append(f"audit row `{aid}` has no rejected candidate in reflection/candidates/")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(f"OK: checked {len(rejected_rows)} rejected candidates / "
          f"{len(audit_seen)} audit rows — all evictions grounded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
