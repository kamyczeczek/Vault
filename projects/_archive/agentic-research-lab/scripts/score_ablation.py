"""Deterministic scorer for the Phase 2 KG ablation (hypothesis B).

Reads blind arm transcripts (arm_A.json / arm_B.json — labels only, no
ON/OFF mapping) and computes the pre-registered flag metrics:

  * solved: answer cites >=1 oracle chunk id AND every citation resolves
  * resolve rate: resolved / cited, only over tasks with >=3 citations
    (tasks below the threshold are excluded and counted separately)
  * concentration (definition A with fallback): (citations to the arm's
    top-3 cited chunks) / (all citations); tasks with 0 citations are
    excluded from the denominator and counted separately
  * dead-route rate: dead harness queries / all harness queries (ON arm)

Stdlib only. No LLM, no network, no mapping file access.
"""

import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from check_citation_integrity import CHUNK_LINE_RE  # noqa: E402

MIN_CITES_FOR_RESOLVE = 3


def extract_citations(text: str) -> list[str]:
    """Chunk ids cited in `Chunk id: `NN_slug`` form, in order of appearance."""
    return CHUNK_LINE_RE.findall(text or "")


def score_answer(answer: str, oracle_ids: set[str], known: set[str]) -> dict:
    """Score one answer. Pure function of (answer, oracle, known ids)."""
    cites = extract_citations(answer)
    resolved = [c for c in cites if c in known]
    unresolved = [c for c in cites if c not in known]
    return {
        "n_cites": len(cites),
        "n_resolved": len(resolved),
        "unresolved": unresolved,
        "solved": bool(set(cites) & set(oracle_ids)) and not unresolved,
        "resolve_eligible": len(cites) >= MIN_CITES_FOR_RESOLVE,
    }


def score_arm(records: list[dict], tasks: dict[str, dict], known: set[str]) -> dict:
    """Aggregate one blind arm. Returns metrics + exclusion counts."""
    per_task = []
    top_counter: collections.Counter = collections.Counter()
    total_cites = 0
    for rec in records:
        task = tasks[rec["task_id"]]
        s = score_answer(rec.get("answer", ""), set(task["oracle_ids"]), known)
        s["task_id"] = rec["task_id"]
        per_task.append(s)
        cites = extract_citations(rec.get("answer", ""))
        top_counter.update(cites)
        total_cites += len(cites)
    eligible = [s for s in per_task if s["resolve_eligible"]]
    micro_resolved = sum(s["n_resolved"] for s in eligible)
    micro_cited = sum(s["n_cites"] for s in eligible)
    top3 = {cid for cid, _ in top_counter.most_common(3)}
    top3_hits = sum(n for cid, n in top_counter.items() if cid in top3)
    dead = sum(1 for r in records for q in r.get("queries", []) if q.get("dead"))
    nq = sum(len(r.get("queries", [])) for r in records)
    return {
        "n_tasks": len(records),
        "n_solved": sum(1 for s in per_task if s["solved"]),
        "resolve_rate": (micro_resolved / micro_cited) if micro_cited else None,
        "resolve_excluded_tasks": len(per_task) - len(eligible),
        "concentration": (top3_hits / total_cites) if total_cites else None,
        "concentration_excluded_zero_cite": sum(1 for s in per_task if s["n_cites"] == 0),
        "dead_route_rate": (dead / nq) if nq else None,
        "per_task": per_task,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score blind ablation arms.")
    parser.add_argument("arms", nargs="+", help="arm transcript JSON files")
    parser.add_argument("--tasks", default=str(ROOT / "benchmark" / "tasks.json"))
    args = parser.parse_args(argv)
    with open(args.tasks, encoding="utf-8") as fh:
        tasks = {t["id"]: t for t in json.load(fh)["tasks"]}
    from check_citation_integrity import known_ids

    known = known_ids()
    for path in args.arms:
        with open(path, encoding="utf-8") as fh:
            records = json.load(fh)
        agg = score_arm(records, tasks, known)
        per = agg.pop("per_task")
        print(f"== {Path(path).stem} ==")
        print(json.dumps(agg, indent=2, sort_keys=True))
        for s in per:
            print(f"   {s['task_id']}: solved={s['solved']} "
                  f"cites={s['n_cites']} resolved={s['n_resolved']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
