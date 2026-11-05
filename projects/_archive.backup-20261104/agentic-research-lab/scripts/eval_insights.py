#!/usr/bin/env python3
"""Insight-trajectory harness: score how insights form, span by span.

The unit under test is the brain-to-improvement pipeline, decomposed the way
agent-eval frameworks decompose trajectories (DeepEval trajectory vs
component metrics; TRAIL span-level verdicts; ClawTrack per-turn rubrics):

- trace-level: did the hint ship behind green gates?
- span-level: query / retrieve / map / implement / verify, each pass,
  partial, or fail, with evidence — plus whether the span was deterministic
  (script-checkable) or judgment (a decision only a reader could make).

Three measurements, all deterministic:

A. Recorded trajectories (`reflection/insight_trajectories.jsonl`,
   reconstructed ground truth, labeled as such): span pass rates split by
   deterministic vs judgment kind, repairs per trace, partial rate.
B. Fix linkage (EXG `fixed_by` analog): share of quarantined ledger entries
   carrying a repair action, and of stale generations with any recorded fix.
   A warning case that points nowhere is a pointer, not a correction edge.
C. Warning-source coverage: fixed probe tasks through `warn.py`; which of
   the four sources supply top warnings, and how redundant they are.

Fails loud when trajectory log or ledger is missing. Prints JSON.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import warn  # noqa: E402

TRAJECTORIES = ROOT / "reflection" / "insight_trajectories.jsonl"
LEDGER = ROOT / "reflection" / "repair_ledger.jsonl"
STALE = ROOT / "reflection" / "stale"

PROBES = [
    "repair quarantined graph defect evidence",
    "agent evaluation workflow reflection",
    "benchmark retrieval metric annotation",
    "skill routing catalog workflow",
    "memory compaction context retention",
]


def score_trajectories() -> dict:
    if not TRAJECTORIES.exists():
        raise FileNotFoundError(f"{TRAJECTORIES} missing")
    traces = [
        json.loads(line)
        for line in TRAJECTORIES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_kind: dict[str, Counter] = {"deterministic": Counter(), "judgment": Counter()}
    repairs = []
    names = []
    for t in traces:
        names.append(t["trace"])
        repairs.append(sum(s.get("repairs", 0) for s in t["spans"]))
        for s in t["spans"]:
            by_kind[s["kind"]][s["verdict"]] += 1
    det = by_kind["deterministic"]
    jud = by_kind["judgment"]
    return {
        "traces": len(traces),
        "deterministic_spans": {
            "pass_rate": round(det["pass"] / max(1, sum(det.values())), 3),
            "counts": dict(det),
        },
        "judgment_spans": {
            "pass_rate": round(jud["pass"] / max(1, sum(jud.values())), 3),
            "partial_rate": round(jud["partial"] / max(1, sum(jud.values())), 3),
            "counts": dict(jud),
        },
        "mean_repairs_per_trace": round(sum(repairs) / max(1, len(repairs)), 2),
        "traces_shipped": len(names),
    }


def fix_linkage() -> dict:
    if not LEDGER.exists():
        raise FileNotFoundError(f"{LEDGER} missing")
    events = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    quarantined = [e for e in events if e.get("state") == "quarantined"]
    with_repair = sum(
        1 for e in quarantined
        for i in e.get("issues", []) if i.get("repair")
    )
    linked_ids = {
        p.get("resolves") for p in events
        if p.get("type") == "RepairProposal" and p.get("state") == "accepted"
    }
    stale_gens = sorted(p.name for p in STALE.iterdir() if p.is_dir()) if STALE.exists() else []
    edge_linked = sum(1 for e in quarantined if e.get("id") in linked_ids)
    stale_linked = sum(1 for g in stale_gens if f"stale:{g}" in linked_ids)
    return {
        "quarantined_entries": len(quarantined),
        "with_repair_action": with_repair,
        "fix_linkage_rate": round(with_repair / max(1, len(quarantined)), 3),
        "edge_linked_entries": edge_linked,
        "edge_linkage_rate": round(edge_linked / max(1, len(quarantined)), 3),
        "stale_generations": len(stale_gens),
        "stale_with_recorded_fix": stale_linked,
    }


def source_coverage() -> dict:
    per_source: Counter = Counter()
    seen_ids: dict[str, int] = {}
    for probe in PROBES:
        for w in warn.warnings_for(probe, limit=3):
            per_source[w["source"].split(":")[0]] += 1
            seen_ids[w["id"]] = seen_ids.get(w["id"], 0) + 1
    total = sum(per_source.values())
    repeat = sum(1 for c in seen_ids.values() if c > 1)
    return {
        "probes": len(PROBES),
        "warnings": total,
        "coverage": {s: round(c / max(1, total), 3) for s, c in sorted(per_source.items())},
        "distinct_ids": len(seen_ids),
        "ids_recurring_across_probes": repeat,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()
    out = {
        "A_trajectories": score_trajectories(),
        "B_fix_linkage": fix_linkage(),
        "C_source_coverage": source_coverage(),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
