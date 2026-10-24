#!/usr/bin/env python3
"""Run the checked-in brain-layer retrieval evaluation set.

The brain layer (`brain/brain.db`, rebuilt by `scripts/ingest_brain.py`) is what the
door `scripts/brain.py` answers "what is the rule / scar / decision about X?" from.

Every answerable case names an exact `table:id`, so a pass means *that row* came
back, not merely that something did. Cases with `"expect": null` are the refusals —
a question outside the corpus; a retrieval change that buys recall by answering
everything is caught here, not by the recall number.

`--check` is the regression gate used by `check_workspace_integrity.py` R21: it
fails when a measured number falls *below* the recorded baseline, or when the row
named by an `expect` no longer matches its recorded `expect_hash` (B7 content-hash
anchor), and prints the baseline's `known_gaps` so they stay visible instead of
quietly accepted.

Usage: python.exe scripts/memory/eval_brain.py [--limit 5] [--verbose] [--check]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from memory import retrieval_v1  # noqa: E402
from ingest_brain import _row_fingerprint  # noqa: E402

CASES = ROOT / "scripts" / "memory" / "brain_eval.json"
ANCHOR_TABLES = {"lessons", "decisions", "problems"}


def verify_anchors(cases: list[dict]) -> list[str]:
    """Fail-loud when a row under `expect` no longer matches its `expect_hash` (B7).

    `expect` is `table:id`; `expect_hash` is the `ingest_brain.py::_row_fingerprint`
    of that row in `brain.db` — the same fingerprint `ingest_brain.py --check`
    uses, so there is one definition of "a row". Without this the eval checks only
    *numbers*: an unnamed scar inserted into `SCARS.md` re-targets every
    `problems:10XX` anchor, the metrics stay green, and the gate silently measures
    a different row. Each mismatch names the case, its `table:id`, and both hashes.
    """
    failures: list[str] = []
    conn = retrieval_v1.connect()
    try:
        cur = conn.cursor()
        for case in cases:
            expect = case.get("expect")
            if expect is None:
                continue  # refusal: no row to anchor (empty hits is its own gate)
            want = case.get("expect_hash")
            if not want:
                failures.append(
                    f"{case['name']} ({expect}): no `expect_hash` recorded — an "
                    "unanchored answerable case can drift unseen")
                continue
            table, _, sid = expect.partition(":")
            if table not in ANCHOR_TABLES or not sid.isdigit():
                failures.append(f"{case['name']}: malformed `expect` {expect!r}")
                continue
            cur.execute(f"SELECT * FROM {table} WHERE id = ?", (int(sid),))
            row = cur.fetchone()
            if row is None:
                failures.append(
                    f"{case['name']} ({expect}): row gone from brain.db — recorded {want}")
                continue
            keys = [d[0] for d in cur.description]
            actual = _row_fingerprint(table, dict(zip(keys, row)))
            if actual != want:
                failures.append(
                    f"{case['name']} ({expect}): row content changed — expected "
                    f"{want}, got {actual}")
    finally:
        conn.close()
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(prog="eval_brain")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--verbose", action="store_true",
                        help="print the top-k ids for passing cases too")
    parser.add_argument("--check", action="store_true",
                        help="fail only on a regression below the recorded baseline")
    args = parser.parse_args()

    data = json.loads(CASES.read_text(encoding="utf-8"))
    baseline = data.get("baseline") or {}
    cases = data["cases"] if isinstance(data, dict) else data

    answerable = refusals = answerable_ok = refusal_ok = 0
    reciprocal_ranks: list[float] = []
    regressed: list[str] = []
    for case in cases:
        hits = retrieval_v1.search(case["query"], limit=args.limit)["hits"]
        ids = [f"{h['table']}:{h['id']}" for h in hits]
        if case["expect"] is None:
            refusals += 1
            ok = not hits
            refusal_ok += ok
            detail = "refused (no evidence)" if ok else f"ANSWERED with [{', '.join(ids)}]"
        else:
            answerable += 1
            ranks = [i for i, rid in enumerate(ids, 1) if rid == case["expect"]]
            reciprocal_ranks.append(1.0 / ranks[0] if ranks else 0.0)
            ok = bool(ranks)
            answerable_ok += ok
            detail = (f"rank {ranks[0]} of {args.limit}" if ok
                      else f"want {case['expect']}, got [{', '.join(ids)}]")
        known = not ok and case["name"] in (baseline.get("known_gaps") or {})
        if not ok and not known:
            regressed.append(case["name"])
        if ok and not args.verbose and not args.check:
            print(f"PASS {case['name']}: {detail}")
        elif known:
            print(f"KNOWN-GAP {case['name']}: {detail}")
        else:
            print(f"{'PASS' if ok else 'FAIL'} {case['name']}: {detail}")
            if args.verbose:
                print(f"      top-{args.limit}: [{', '.join(ids)}]")

    mrr = sum(reciprocal_ranks) / answerable if answerable else 0.0
    print(f"\nbrain_eval: hit@{args.limit}={answerable_ok}/{answerable} "
          f"refusal={refusal_ok}/{refusals} MRR={mrr:.3f}")

    if not args.check:
        if known_gaps := (baseline.get("known_gaps") or {}):
            print(f"known gaps (recorded in brain_eval.json, not failures): {', '.join(known_gaps)}")
        return 1 if regressed else 0

    if not baseline:
        print("FAIL: --check needs a 'baseline' block in brain_eval.json")
        return 1
    below = [
        f"hit@{args.limit} {answerable_ok}/{answerable} < baseline "
        f"{baseline['hit_ok']}/{baseline['answerable']}" if answerable_ok < baseline["hit_ok"] else None,
        f"refusal {refusal_ok}/{refusals} < baseline "
        f"{baseline['refusal_ok']}/{baseline['refusals']}" if refusal_ok < baseline["refusal_ok"] else None,
    ]
    below = [b for b in below if b]
    for gap, why in (baseline.get("known_gaps") or {}).items():
        print(f"known gap — {gap}: {why.split('.')[0]}.")
    anchor_failures = verify_anchors(cases)
    for f in anchor_failures:
        print(f"FAIL: brain eval anchor drifted — {f}")
    if below or regressed or anchor_failures:
        for b in below:
            print(f"FAIL: brain retrieval regressed — {b}")
        for name in regressed:
            print(f"FAIL: brain retrieval regressed — {name} newly misses (was not a recorded gap)")
        print("Fix the retrieval or the row; do not lower the baseline to pass.")
        return 1
    print(f"OK — brain retrieval is at or above the baseline recorded {baseline.get('recorded')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
