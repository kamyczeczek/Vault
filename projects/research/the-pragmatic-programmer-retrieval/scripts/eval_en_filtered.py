#!/usr/bin/env python3
"""Session 5 FAZA 3: filtered retrieval EN (variant D), pre-registered.

PRE-REGISTERED THRESHOLDS (S56 — frozen BEFORE run, do not change after):
  F >= 0.961 (= B - 0.02) -> 0.981 real; junk chunks not contaminating; EN enters prod without filter.
  F <  0.931 (= B - 0.05) -> 0.981 partly rests on junk chunks; filter needed; session 6 = filter + answer-layer EN.
  F <  0.90               -> 0.981 heavily contaminated; session 6 = blind re-translation.
Method: PRE-RETRIEVAL filter — retrieve(query, top_k=40) candidate pool, filter to
exclude_types ['related-sections','heading-only','code-listing'] (prose + challenge kept),
take first 8. Same retrieve() (Tier 3), same index, same gold set EN, same interpreter.
Sanity 1: median < 500 ms. Sanity 2: q012 top-8 has no related-sections AND final len == 8
(if < 8 after filter -> STOP, do NOT backfill from rejected).
"""
import json
import statistics
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "scripts"))
from recall_hybrid import retrieve  # noqa: E402

OUT = PROJECT / "handoff" / "session-5-results.json"
CLASSES = PROJECT / "data" / "chunks_classified.json"
GOLD_EN = PROJECT / "eval" / "gold_set_extended_en.json"

EXCLUDE = ["related-sections", "heading-only", "code-listing"]
CANDIDATE_POOL = 40
TOP_K = 8


def category(q: dict) -> str:
    qid = q["id"]
    if qid.startswith("fp"):
        return "false_premise"
    if qid.startswith("u"):
        return "unanswerable"
    t = q.get("type", "")
    for cat in ("factual", "comparison", "reasoning", "relational"):
        if t.startswith(cat):
            return cat
    return "other"


def main() -> int:
    cls_by_id = {c["id"]: c["class"] for c in json.loads(CLASSES.read_text(encoding="utf-8"))}
    gold = json.loads(GOLD_EN.read_text(encoding="utf-8"))
    qs = gold["questions"]
    answerable = [q for q in qs if not q["id"].startswith("u")]
    unans = [q for q in qs if q["id"].startswith("u")]

    rows, stop = [], False
    for q in qs:
        t0 = time.perf_counter()
        cand = retrieve(q["question"], top_k=CANDIDATE_POOL)
        kept = [cid for cid in cand if cls_by_id.get(cid, "prose") not in EXCLUDE]
        final = kept[:TOP_K]
        filtered_out = len(cand) - len(kept)
        dt_ms = (time.perf_counter() - t0) * 1000
        meta_rows = _meta(final)
        hit = any(int(r["topic"]) in q["topics"] for r in meta_rows)
        row = {
            "id": q["id"], "type": q.get("type"), "category": category(q),
            "gold_topics": q["topics"], "top8topics": [r["topic"] for r in meta_rows],
            "top8ids": final, "hit": hit,
            "hit_rank": (next((i + 1 for i, r in enumerate(meta_rows)
                               if int(r["topic"]) in q["topics"]), None)),
            "dt_ms": round(dt_ms, 2), "filtered_out_count": filtered_out,
            "final_len": len(final),
        }
        rows.append(row)
        if len(final) < TOP_K:
            stop = True
            print(f"STOP trigger: {q['id']} final_len={len(final)} < 8", file=sys.stderr)
    if stop:
        print("STOP: filtered pool < 8 for at least one query. Not backfilling.", file=sys.stderr)
        return 1

    ans_rows = [r for r in rows if not r["id"].startswith("u")]
    hits = [r for r in ans_rows if r["hit"]]
    recall = len(hits) / len(ans_rows)
    mrr = sum((1 / r["hit_rank"] if r["hit_rank"] else 0) for r in ans_rows) / len(ans_rows)
    dts = sorted(r["dt_ms"] for r in rows)
    p50 = statistics.median(dts)
    p95 = dts[int(round(0.95 * len(dts))) - 1]
    misses = [r["id"] for r in ans_rows if not r["hit"]]

    print(f"F (filtered EN Recall@8 any) = {recall:.4f} ({len(hits)}/{len(ans_rows)})")
    print(f"MRR = {mrr:.3f}")
    print(f"latency ms: p50 = {p50:.1f}, p95 = {p95:.1f}, median<500: {p50 < 500}")
    print(f"misses ({len(misses)}): {misses}")
    per_cat = {}
    for cat in ["factual", "comparison", "reasoning", "relational", "false_premise"]:
        sub = [r for r in ans_rows if r["category"] == cat]
        per_cat[cat] = {"n": len(sub), "hits": sum(r["hit"] for r in sub)}
        print(f"category {cat}: {per_cat[cat]['hits']}/{len(sub)}")
    B = 0.981
    print(f"delta F - B = {recall - B:+.4f}")
    q012 = next(r for r in rows if r["id"] == "q012")
    junk_in_top8 = any(cls_by_id.get(cid) in EXCLUDE for cid in q012["top8ids"])
    print(f"q012 top8topics = {q012['top8topics']} (dictum: 3x Estimating expected signature may shift)")
    print(f"q012 top-8 contains excluded-class chunk: {junk_in_top8}")
    fo_total = sum(r["filtered_out_count"] for r in rows)
    print(f"filtered_out total across 60 queries: {fo_total} (avg {fo_total/len(rows):.2f}/query)")

    OUT.write_text(json.dumps({
        "prereg": {"thresholds": {"real": 0.961, "partly": 0.931, "heavily": 0.90},
                   "exclude_types": EXCLUDE, "candidate_pool": CANDIDATE_POOL,
                   "final_top_k": TOP_K, "B_from_session4": B},
        "timestamp": "2026-10-18", "variant": "D (pre-retrieval filtered EN)",
        "F_recall": round(recall, 4), "mrr": round(mrr, 4),
        "p50_ms": round(p50, 1), "p95_ms": round(p95, 1),
        "misses": misses, "per_category": per_cat,
        "q012_top8topics": q012["top8topics"], "q012_sign_check": junk_in_top8,
        "rows": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"saved {OUT}")
    print("sanity1 PASS" if p50 < 500 else "sanity1 FAIL")
    print("sanity2 PASS" if not junk_in_top8 and all(r["final_len"] == 8 for r in rows) else "sanity2 FAIL")
    return 0


def _meta(ids):
    from recall_hybrid import get_chunks_meta
    return get_chunks_meta(ids)


if __name__ == "__main__":
    raise SystemExit(main())
