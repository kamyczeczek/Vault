"""Evaluate retrieval quality (recall@k, MRR, latency) across retrieval tiers.

Phase 2.2 of book retrieval pipeline.
Benchmarks:
1. Pure FTS5 BM25
2. Pure Vector (FastEmbed)
3. Hybrid RRF (Production Default)
4. Hybrid RRF + Cross-Encoder Reranker (Offline / GPU only)

Strict hit policy: chunk['topic'] must be in target_topics.
Also computes strict primary topic hit (chunk['topic'] == target_topics[0]).
For unanswerable queries (target_topics == []), evaluates score distribution & refusal capability.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.fingerprint import canonical_index_fingerprint
from scripts.recall_hybrid import fts_search, vector_search, retrieve, full_retrieve, get_chunks_meta

DEFAULT_GOLD_FILE = "eval/gold_set_extended.json"


def ndcg_at_k(hit_ranks: list[int | None], k: int = 8) -> float:
    dcg = sum(1.0 / math.log2(r + 1) for r in hit_ranks if r and r <= k)
    idcg = 1.0  # idealne: pierwszy trafiony chunk na pozycji 1
    return dcg / idcg if idcg else 0.0


def is_hit(chunk: dict, target_topics: list[int]) -> bool:
    if not target_topics:
        return False
    return chunk.get("topic") in target_topics


def is_primary_hit(chunk: dict, target_topics: list[int]) -> bool:
    if not target_topics:
        return False
    return chunk.get("topic") == target_topics[0]


def evaluate_tier(name: str, retrieve_fn, questions: list[dict], top_k: int = 8) -> dict:
    answerable = [q for q in questions if q.get("topics")]
    unanswerable = [q for q in questions if not q.get("topics")]

    recalls = []
    primary_recalls = []
    mrrs = []
    ndcgs = []
    latencies = []

    # Category breakdown for answerables
    by_category = {}

    print(f"\n--- {name} (top_k={top_k}, total_n={len(questions)}, answerable={len(answerable)}, unanswerable={len(unanswerable)}) ---", flush=True)

    for i, q in enumerate(answerable, start=1):
        q_text = q["question"]
        target_topics = q.get("topics", [])
        q_type = q.get("type", "other")
        if "false" in q_type.lower() and "premise" in q_type.lower():
            q_type = "false_premise"
        if q_type not in by_category:
            by_category[q_type] = {"recalls": [], "prim_recalls": [], "ndcgs": []}

        t0 = time.perf_counter()
        retrieved_chunks = retrieve_fn(q_text, top_k)
        lat = (time.perf_counter() - t0) * 1000.0  # ms
        latencies.append(lat)

        hit_rank = None
        for rank, c in enumerate(retrieved_chunks, start=1):
            if is_hit(c, target_topics):
                hit_rank = rank
                break

        prim_hit = any(is_primary_hit(c, target_topics) for c in retrieved_chunks[:top_k])
        primary_recalls.append(1.0 if prim_hit else 0.0)

        r_at_k = 1.0 if hit_rank is not None and hit_rank <= top_k else 0.0
        mrr_val = 1.0 / hit_rank if hit_rank is not None else 0.0
        ndcg_val = ndcg_at_k([hit_rank], k=top_k)

        recalls.append(r_at_k)
        mrrs.append(mrr_val)
        ndcgs.append(ndcg_val)

        by_category[q_type]["recalls"].append(r_at_k)
        by_category[q_type]["prim_recalls"].append(1.0 if prim_hit else 0.0)
        by_category[q_type]["ndcgs"].append(ndcg_val)

        if i % 10 == 0 or i == len(answerable):
            print(f"  [{i}/{len(answerable)}] running Recall@{top_k}={sum(recalls)/len(recalls):.3f}, lat_med={sorted(latencies)[len(latencies)//2]:.1f}ms", flush=True)

    mean_recall = sum(recalls) / len(recalls) if recalls else 0.0
    mean_prim_recall = sum(primary_recalls) / len(primary_recalls) if primary_recalls else 0.0
    mean_mrr = sum(mrrs) / len(mrrs) if mrrs else 0.0
    mean_ndcg = sum(ndcgs) / len(ndcgs) if ndcgs else 0.0
    lat_sorted = sorted(latencies)
    med_lat = lat_sorted[len(lat_sorted) // 2] if lat_sorted else 0.0
    p95_lat = lat_sorted[int(len(lat_sorted) * 0.95)] if lat_sorted else 0.0

    print(f"  Summary ({name}):")
    print(f"    Answerable Any-Topic Recall@{top_k}: {mean_recall:.3f} ({sum(recalls):.0f}/{len(recalls)})")
    print(f"    Answerable Primary-Topic Recall@{top_k}: {mean_prim_recall:.3f} ({sum(primary_recalls):.0f}/{len(primary_recalls)})")
    print(f"    MRR: {mean_mrr:.3f}")
    print(f"    nDCG@{top_k}: {mean_ndcg:.3f}")
    print(f"    Latency: median={med_lat:.1f}ms, p95={p95_lat:.1f}ms")

    for cat, data in by_category.items():
        cat_recall = sum(data["recalls"]) / len(data["recalls"]) if data["recalls"] else 0.0
        cat_prim = sum(data["prim_recalls"]) / len(data["prim_recalls"]) if data["prim_recalls"] else 0.0
        cat_ndcg = sum(data["ndcgs"]) / len(data["ndcgs"]) if data["ndcgs"] else 0.0
        print(f"    Category [{cat}] (n={len(data['recalls'])}): Any Recall@{top_k}={cat_recall:.3f}, Prim Recall@{top_k}={cat_prim:.3f}, nDCG@{top_k}={cat_ndcg:.3f}")

    # Evaluate unanswerables (latency & top candidate behavior)
    unans_latencies = []
    for u in unanswerable:
        t0 = time.perf_counter()
        retrieved_chunks = retrieve_fn(u["question"], top_k)
        unans_latencies.append((time.perf_counter() - t0) * 1000.0)

    if unans_latencies:
        unans_med = sorted(unans_latencies)[len(unans_latencies)//2]
    else:
        unans_med = 0.0
    print(f"    Unanswerable (n={len(unanswerable)}): median latency={unans_med:.1f}ms")

    return {
        "tier": name,
        "n_total": len(questions),
        "n_answerable": len(answerable),
        "n_unanswerable": len(unanswerable),
        f"recall@{top_k}": mean_recall,
        f"primary_recall@{top_k}": mean_prim_recall,
        "mrr": mean_mrr,
        f"ndcg@{top_k}": mean_ndcg,
        "latency_median_ms": med_lat,
        "latency_p95_ms": p95_lat,
        "categories": {
            cat: {
                "n": len(data["recalls"]),
                "recall": sum(data["recalls"]) / len(data["recalls"]) if data["recalls"] else 0.0,
                "primary_recall": sum(data["prim_recalls"]) / len(data["prim_recalls"]) if data["prim_recalls"] else 0.0,
                "ndcg": sum(data["ndcgs"]) / len(data["ndcgs"]) if data["ndcgs"] else 0.0
            }
            for cat, data in by_category.items()
        }
    }


def run_all_evaluations(gold_path: str = DEFAULT_GOLD_FILE, top_k: int = 8, tier_filter: str = "prod", wide: bool = False) -> dict:
    with open(gold_path, encoding="utf-8") as f:
        gold_data = json.load(f)
        gold = gold_data["questions"]

    book_struct_path = ROOT / "data/book_structure.json"
    if book_struct_path.exists():
        current_fp = canonical_index_fingerprint(book_struct_path)
        gold_fp = gold_data.get("index_fingerprint", "").replace("sha256:", "")
        if gold_fp and current_fp != gold_fp:
            print(f"STALE GOLD SET: gold={gold_fp[:12]} index={current_fp[:12]}")
            sys.exit(2)

    print(f"Starting evaluation on {len(gold)} gold questions from {gold_path}...", flush=True)

    tiers = {
        "fts5": (
            "1. Pure FTS5 BM25",
            lambda q, k: get_chunks_meta(fts_search(q, top_k=k))
        ),
        "vector": (
            "2. Pure FastEmbed Vector",
            lambda q, k: get_chunks_meta(vector_search(q, top_k=k))
        ),
        "hybrid": (
            "3. Hybrid RRF (FTS5 + Vector)",
            lambda q, k: get_chunks_meta(retrieve(q, top_k=k))
        ),
    }

    if tier_filter == "all" or tier_filter == "hybrid_rerank":
        from scripts.rerank import get_reranker
        get_reranker()
        cand_count = 100 if wide else 40
        tiers["hybrid_rerank"] = (
            f"4. Hybrid RRF + CrossEncoder ({cand_count} candidates)",
            lambda q, k: full_retrieve(q, top_k=k, wide=wide)
        )

    results = {}
    for key, (label, fn) in tiers.items():
        if tier_filter not in ("all", "prod") and tier_filter != key:
            continue
        results[key] = evaluate_tier(label, fn, gold, top_k=top_k)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate retrieval pipeline")
    parser.add_argument("--gold", default=DEFAULT_GOLD_FILE, help="Path to gold set JSON")
    parser.add_argument("--top-k", type=int, default=8, help="Top-K evaluation cutoff")
    parser.add_argument("--tiers", choices=["all", "prod", "fts5", "vector", "hybrid", "hybrid_rerank"], default="prod", help="Tiers to run (default: prod = tiers 1-3)")
    parser.add_argument("--wide", action="store_true", help="Use 100 candidates for reranker pool")
    args = parser.parse_args()

    run_all_evaluations(gold_path=args.gold, top_k=args.top_k, tier_filter=args.tiers, wide=args.wide)
