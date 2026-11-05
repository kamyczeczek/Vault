#!/usr/bin/env python3
"""Trace-eval harness: score execution traces deterministically.

Rung 4 of the eval-maturity ladder (tool & trace eval): instead of judging
candidate prose, measure the shape of runs recorded in
`reflection/trace/events.jsonl`. Per run id:

- decisions: `graph_decision` events with use_graph true/false/required;
- retrieval: `retrieval` events following a decision;
- artifacts: `artifact` events; failures: `failure` events.

Reported per run and in aggregate: orphan decisions (use_graph=true with no
retrieval after it), dry retrievals (no artifact downstream), failure rate,
and runs with no decision at all. All ordering is file order; output is JSON
to stdout and `reflection/trace/eval_latest.json`. A trace that cannot be
scored (missing file) fails loud.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "reflection" / "trace" / "events.jsonl"
OUT = ROOT / "reflection" / "trace" / "eval_latest.json"


def load() -> list[dict]:
    if not TRACE.exists():
        raise FileNotFoundError(f"{TRACE} missing — no traces to score")
    rows = []
    for line in TRACE.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def score(rows: list[dict]) -> dict:
    by_run: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_run[str(r.get("run_id", "?"))].append(r)
    runs = {}
    for rid, evs in by_run.items():
        kinds = [e.get("kind") for e in evs]
        decisions = [e for e in evs if e.get("kind") == "graph_decision"]
        retrievals = [e for e in evs if e.get("kind") == "retrieval"]
        artifacts = [e for e in evs if e.get("kind") == "artifact"]
        failures = [e for e in evs if e.get("status") == "failed"]
        need_retrieval = sum(
            1 for d in decisions if (d.get("decision") or {}).get("use_graph")
        )
        orphan_decisions = max(0, need_retrieval - len(retrievals))
        dry_retrievals = max(0, len(retrievals) - len(artifacts) - len(failures))
        runs[rid] = {
            "events": len(evs),
            "decisions": len(decisions),
            "retrievals": len(retrievals),
            "artifacts": len(artifacts),
            "failures": len(failures),
            "orphan_decisions": orphan_decisions,
            "dry_retrievals": dry_retrievals,
            "no_decision": not decisions and bool(retrievals or artifacts),
        }
    agg = {
        "runs": len(runs),
        "events": len(rows),
        "orphan_decision_rate": round(
            sum(v["orphan_decisions"] for v in runs.values())
            / max(1, sum(v["decisions"] for v in runs.values())),
            3,
        ),
        "dry_retrieval_rate": round(
            sum(v["dry_retrievals"] for v in runs.values())
            / max(1, sum(v["retrievals"] for v in runs.values())),
            3,
        ),
        "failure_rate": round(
            sum(v["failures"] for v in runs.values()) / max(1, len(rows)), 3
        ),
        "runs_without_decision": sum(1 for v in runs.values() if v["no_decision"]),
    }
    return {"aggregate": agg, "runs": runs}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", default=None, help="score one run id only")
    args = ap.parse_args()
    rows = load()
    if args.run:
        rows = [r for r in rows if str(r.get("run_id")) == args.run]
        if not rows:
            print(f"no events for run {args.run}")
            return 1
    out = score(rows)
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out["aggregate"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
