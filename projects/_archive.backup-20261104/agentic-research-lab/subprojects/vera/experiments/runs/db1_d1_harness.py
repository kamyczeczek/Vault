"""DB-1 D1 arm harness: single-graph read path via context_gateway only.

No file reads of corpus allowed — everything flows through context_packet().
Logs per-question: token budget used, chunk matches, whether seeds were in the pool.
"""
import sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "knowledge" / "graph"))
from context_gateway import context_packet  # noqa: E402

SEEDS = {
    "Q1": ["00_okf_methodology_research"],
    "Q5": ["00_agent_memory_hierarchies", "reflection_rule_of_scars",
            "00_reflection_retrieval_dominates_write", "00_reflection_reorientation_cost"],
}
QUESTIONS = {
    "Q1": "What trust tiers does this lab use for evidence, and what does tier 3 mean?",
    "Q5": "How do the lab's accepted principles jointly constrain what a research agent may promote?",
}

def main():
    out = {}
    for qid, q in QUESTIONS.items():
        for mode in ("fast", "default"):
            pkt = context_packet(q, mode=mode, limit=5)
            ids = [it.get("id", "") for it in pkt.get("items", []) if it.get("kind") == "corpus"]
            out.setdefault(qid, {})[mode] = {
                "budget_tokens": pkt.get("token_budget"),
                "estimated_tokens": pkt.get("estimated_tokens"),
                "truncated": pkt.get("truncated"),
                "kinds": [it.get("kind") for it in pkt.get("items", [])],
                "corpus_ids": ids,
                "seed_recall": (len(set(ids) & set(SEEDS[qid])) / len(SEEDS[qid])) if SEEDS[qid] else None,
            }
    print(json.dumps(out, indent=2, default=str))

if __name__ == "__main__":
    main()
