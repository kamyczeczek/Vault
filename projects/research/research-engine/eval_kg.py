#!/usr/bin/env python3
"""Deterministic eval harness for the `kg.py` query surface.

Harness and tool are separate: this file never queries the graph directly,
only through `kg.resolve`, `kg.expand`, and `kg.like_baseline`. Each case
names a seed substring and the source family a good answer must come from.

Arms per case: `resolve` (no look-ahead), `resolve_and_expand` (1 hop),
`resolve_and_expand` (2 hops), and the `like_baseline` dumb reference.

Metrics per arm: family hit rate (expected family present), family coverage
(distinct families returned — breadth of context), consistency (3 repeats,
fraction with identical id sets), mean latency.

Results append to `evals/kg_eval.jsonl` (one row per case-arm-repeat) and the
printed summary goes to `evals/kg_eval_latest.json`. Preflight fails loud if
the graph is missing — a harness that silently scores nothing is worse than
no harness.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import kg

ROOT = Path(__file__).resolve().parent
EVALS = ROOT / "evals"

CASES = [
    ("multiagent", "multiagent_systems_algorithmic_game_theoretic_an"),
    ("graph databases", "graph_databases_new_opportunities_for_connected"),
    ("book of why", "the_book_of_why_the_new_science_of_cause_and_eff"),
    ("automated machine learning", "automated_machine_learning_methods_systems_chall"),
    ("building llms for production", "building_llms_for_production_enhancing_llm_abili"),
    ("ai scientist", "seed_ai_scientist"),
    ("plan compliance", "plan_compliance_runtime_verification_web_researc"),
]

REPEATS = 3
LIMIT = 5


def run_arm(substring: str, arm: str) -> tuple[list[dict], float]:
    start = time.perf_counter()
    if arm == "resolve":
        rows = kg.resolve(substring, limit=LIMIT)
    elif arm == "expand1":
        rows = kg.resolve_and_expand(substring, steps=1, limit=LIMIT)
    elif arm == "expand2":
        rows = kg.resolve_and_expand(substring, steps=2, limit=LIMIT)
    elif arm == "like":
        rows = kg.like_baseline(substring, limit=LIMIT)
    else:
        raise ValueError(f"unknown arm {arm}")
    return rows, (time.perf_counter() - start) * 1000


def main() -> int:
    try:
        kg._connect().close()
    except FileNotFoundError as e:
        print(f"PREFLIGHT FAIL: {e}")
        return 1

    EVALS.mkdir(exist_ok=True)
    arms = ["resolve", "expand1", "expand2", "like"]
    summary: dict[str, dict] = {a: {"hits": 0, "cases": 0} for a in arms}
    detail: dict[str, dict] = {}

    for substring, family in CASES:
        for arm in arms:
            id_sets = []
            lat = []
            fams: set[str] = set()
            for _ in range(REPEATS):
                rows, ms = run_arm(substring, arm)
                lat.append(ms)
                id_sets.append(tuple(r["id"] for r in rows))
                fams.update(r.get("source_family", "") for r in rows)
                EVALS.joinpath("kg_eval.jsonl").open("a", encoding="utf-8").write(
                    json.dumps(
                        {
                            "ts": datetime.now(timezone.utc).isoformat(),
                            "case": substring,
                            "arm": arm,
                            "hit_ids": list(id_sets[-1]),
                            "latency_ms": round(ms, 1),
                        }
                    )
                    + "\n"
                )
            hit = family in fams
            consistent = sum(1 for s in id_sets if s == id_sets[0]) / REPEATS
            summary[arm]["hits"] += hit
            summary[arm]["cases"] += 1
            detail.setdefault(substring, {})[arm] = {
                "hit": hit,
                "families": len(fams),
                "consistency": round(consistent, 2),
                "mean_latency_ms": round(sum(lat) / len(lat), 1),
            }

    out = {
        "cases": len(CASES),
        "arms": {
            a: {
                "family_hit_rate": round(summary[a]["hits"] / summary[a]["cases"], 3),
                "mean_consistency": round(
                    sum(detail[c][a]["consistency"] for c in detail) / len(detail), 3
                ),
                "mean_latency_ms": round(
                    sum(detail[c][a]["mean_latency_ms"] for c in detail) / len(detail), 1
                ),
            }
            for a in arms
        },
        "cases_detail": detail,
    }
    EVALS.joinpath("kg_eval_latest.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print(json.dumps(out["arms"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
