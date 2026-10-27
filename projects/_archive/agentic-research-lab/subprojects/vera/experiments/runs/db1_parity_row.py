"""DB-1 parity row (item c): Q5/Q6 through the fixed gateway with B0.2 pinned pools.

Runs each pinned query (as recorded in benchmark/QUESTIONS.md) through
context_gateway.context_packet() in fast + default modes and reports pool-level
seed recall (union of corpus ids across the pool). No corpus file reads.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "knowledge" / "graph"))
from context_gateway import context_packet  # noqa: E402

# B0.2 pinned queries, frozen in benchmark/QUESTIONS.md
SEEDS = {
    "Q5": ["00_reflection_retrieval_dominates_write",
           "00_reflection_reorientation_cost",
           "00_agent_memory_hierarchies",
           "reflection_rule_of_scars"],
    "Q6": ["00_karpathy_minimalist_agentic_coding_harnesses",
           "02_00_software_factory_isolate_build_prove_ship"],
}
PINNED = {
    # Q5 v3 pool (workspace seed reflection/memory.md arrives as a lesson
    # item, not corpus kind — outside pool-level corpus recall)
    "Q5": ["reflection accepted rule candidates",
           "agent memory hierarchies",
           "retrieval dominates write"],
    "Q6": ["karpathy minimalist agentic coding harnesses",
           "software factory machine gate proof receipt merge gate"],
}


def main():
    out = {}
    for qid in ("Q5", "Q6"):
        out[qid] = {}
        for mode in ("fast", "default"):
            pool_ids, rows = [], []
            for q in PINNED[qid]:
                pkt = context_packet(q, mode=mode, limit=5)
                ids = [it.get("id", "") for it in pkt.get("items", [])
                       if it.get("kind") == "corpus"]
                pool_ids.extend(ids)
                rows.append({
                    "query": q,
                    "budget_tokens": pkt.get("token_budget"),
                    "estimated_tokens": pkt.get("estimated_tokens"),
                    "truncated": pkt.get("truncated"),
                    "corpus_ids": ids,
                })
            union = set(pool_ids)
            hit = sorted(union & set(SEEDS[qid]))
            out[qid][mode] = {
                "pool_level_seed_recall": f"{len(hit)}/{len(SEEDS[qid])}",
                "seeds_hit": hit,
                "full_file_reads": 0,
                "packets": rows,
            }
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
