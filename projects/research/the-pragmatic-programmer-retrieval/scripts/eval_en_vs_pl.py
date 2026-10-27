"""EN vs PL query experiment on Tier 3 (session 4, 2026-10-18).

Pre-registered before run (S56):
- Threshold: B >= A + 0.02 -> EN enters pipeline; A <= B < A + 0.02 -> noise (n=52), owner decision.
- RED FLAG: A < 0.827 - 0.02 = 0.807 -> baseline changed, STOP.
- Sanity gate: median latency < 500 ms per run; q012 signature = 3x Estimating (15) in top-8.
- Same index (db/rag.db), same retrieve() (Tier 3, RRF, no reranker), same top_k=8,
  same interpreter, same cwd. No re-build, no reranker, no HyDE, no query expansion.

Variants:
  A: PL gold set (eval/gold_set_extended.json), PL queries
  B: EN gold set (eval/gold_set_extended_en.json), EN queries
  C (optional): rrf_fuse([PL, EN]) top_k=8 against both gold sets (union - hit if either language set hits)

Per-question output: id, query_lang, top8topics, hit, dt_ms.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.fingerprint import canonical_index_fingerprint
from scripts.recall_hybrid import retrieve, rrf_fuse, get_chunks_meta

TOP_K = 8
GOLD_PL = "eval/gold_set_extended.json"
GOLD_EN = "eval/gold_set_extended_en.json"

PREREG = {
    "threshold_delta": 0.02,
    "redflag_baseline_floor": 0.807,
    "sanity_median_ms": 500,
}


def load_gold(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    cur_fp = canonical_index_fingerprint(ROOT / "data/book_structure.json")
    gold_fp = data.get("index_fingerprint", "").replace("sha256:", "")
    if gold_fp and cur_fp != gold_fp:
        print(f"STALE GOLD SET: gold={gold_fp[:12]} index={cur_fp[:12]}", file=sys.stderr)
        sys.exit(2)
    return data["questions"]


def run_variant(name: str, questions: list[dict], lang: str) -> list[dict]:
    rows = []
    answerable = [q for q in questions if q.get("topics")]
    for q in answerable:
        t0 = time.perf_counter()
        ids = retrieve(q["question"], TOP_K)
        chunks = get_chunks_meta(ids)
        dt = (time.perf_counter() - t0) * 1000.0
        topics8 = [c["topic"] for c in chunks]
        hit = any(t in q["topics"] for t in topics8)
        hit_rank = next((r for r, t in enumerate(topics8, 1) if t in q["topics"]), None)
        rows.append({
            "id": q["id"],
            "query_lang": lang,
            "type": q.get("type", ""),
            "gold_topics": q["topics"],
            "top8topics": topics8,
            "hit": hit,
            "hit_rank": hit_rank,
            "dt_ms": round(dt, 2),
        })
    lat = sorted(r["dt_ms"] for r in rows)
    p50 = lat[len(lat) // 2]
    p95 = lat[max(0, int(len(lat) * 0.95) - 1)]
    recall = sum(r["hit"] for r in rows) / len(rows)
    mrr = sum((1.0 / r["hit_rank"]) if r["hit_rank"] else 0.0 for r in rows) / len(rows)
    print(f"\n=== Variant {name} ({lang}, n={len(rows)}) ===", flush=True)
    print(f"Recall@8 any-topic = {recall:.3f} ({sum(r['hit'] for r in rows)}/{len(rows)})")
    print(f"MRR@8 = {mrr:.3f}")
    print(f"latency p50 = {p50:.1f} ms, p95 = {p95:.1f} ms, total = {sum(lat):.1f} ms")
    cats: dict[str, list[dict]] = {}
    for r in rows:
        key = r["type"].split()[0] if "/" not in r["type"] else r["type"].split()[0]
        if "premise" in r["type"]:
            key = "false_premise"
        elif key == "comparison":
            key = "comparison"
        elif key == "relational":
            key = "relational"
        elif key == "reasoning":
            key = "reasoning"
        elif key in ("factual", "procedural"):
            key = key
        else:
            key = "other"
        cats.setdefault(key, []).append(r)
    for key, rs in sorted(cats.items()):
        c_rec = sum(r["hit"] for r in rs) / len(rs)
        print(f"  [{key}] n={len(rs)} Recall@8={c_rec:.3f} ({sum(r['hit'] for r in rs)}/{len(rs)})")
    misses = [r["id"] for r in rows if not r["hit"]]
    print(f"  misses: {misses}")
    sanity = "PASS" if p50 < PREREG["sanity_median_ms"] else "FAIL"
    print(f"  sanity gate median<500ms: {sanity}")
    return rows


def run_variant_c(questions_pl: list[dict], questions_en: list[dict]) -> list[dict]:
    qpl = {q["id"]: q for q in questions_pl if q.get("topics")}
    qen = {q["id"]: q for q in questions_en if q.get("topics")}
    assert set(qpl) == set(qen)
    rows = []
    for qid in qpl:
        t0 = time.perf_counter()
        fts = None
        vec = None
        from scripts.recall_hybrid import fts_search, vector_search
        fts_pl = fts_search(qpl[qid]["question"], TOP_K)
        vec_pl = vector_search(qpl[qid]["question"], TOP_K)
        fts_en = fts_search(qen[qid]["question"], TOP_K)
        vec_en = vector_search(qen[qid]["question"], TOP_K)
        fused = rrf_fuse([fts_pl, vec_pl, fts_en, vec_en])[:TOP_K]
        chunks = get_chunks_meta(fused)
        dt = (time.perf_counter() - t0) * 1000.0
        topics8 = [c["topic"] for c in chunks]
        gold = qpl[qid]["topics"]
        hit = any(t in gold for t in topics8)
        hit_rank = next((r for r, t in enumerate(topics8, 1) if t in gold), None)
        rows.append({
            "id": qid,
            "query_lang": "pl+en",
            "gold_topics": gold,
            "top8topics": topics8,
            "hit": hit,
            "hit_rank": hit_rank,
            "dt_ms": round(dt, 2),
        })
    lat = sorted(r["dt_ms"] for r in rows)
    p50 = lat[len(lat) // 2]
    p95 = lat[max(0, int(len(lat) * 0.95) - 1)]
    recall = sum(r["hit"] for r in rows) / len(rows)
    mrr = sum((1.0 / r["hit_rank"]) if r["hit_rank"] else 0.0 for r in rows) / len(rows)
    print(f"\n=== Variant C (pl+en fused, n={len(rows)}) ===", flush=True)
    print(f"Recall@8 any-topic = {recall:.3f} ({sum(r['hit'] for r in rows)}/{len(rows)})")
    print(f"MRR@8 = {mrr:.3f}")
    print(f"latency p50 = {p50:.1f} ms, p95 = {p95:.1f} ms, total = {sum(lat):.1f} ms")
    misses = [r["id"] for r in rows if not r["hit"]]
    print(f"  misses: {misses}")
    sanity = "PASS" if p50 < PREREG["sanity_median_ms"] else "FAIL"
    print(f"  sanity gate median<500ms: {sanity}")
    return rows


def main() -> None:
    gold_pl = load_gold(GOLD_PL)
    gold_en = load_gold(GOLD_EN)
    assert len(gold_pl) == 60 and len(gold_en) == 60

    rows_a = run_variant("A (baseline PL)", gold_pl, "pl")
    # q012 Tier-3 signature check
    q12 = next(r for r in rows_a if r["id"] == "q012")
    n15 = q12["top8topics"].count(15)
    print(f"q012 signature: top8={q12['top8topics']} (Estimating(15) x{n15}) -> {'PASS' if n15 == 3 else 'FAIL'}")

    rows_b = run_variant("B (EN)", gold_en, "en")

    rec_a = sum(r["hit"] for r in rows_a) / len(rows_a)
    rec_b = sum(r["hit"] for r in rows_b) / len(rows_b)
    delta = rec_b - rec_a
    print("\n=== Pre-registered verdict ===")
    print(f"A = {rec_a:.3f}, B = {rec_b:.3f}, delta = {delta:+.3f}, threshold = +{PREREG['threshold_delta']}")
    if rec_a < PREREG["redflag_baseline_floor"]:
        verdict = "RED FLAG: baseline PL below 0.807 - index/model/cache changed, STOP"
    elif rec_b >= rec_a + PREREG["threshold_delta"]:
        verdict = "EN enters pipeline (answer-layer EN in session 5)"
    elif rec_b >= rec_a:
        verdict = "noise band (n=52) - owner decision"
    else:
        verdict = "PL stays in search; problem was answer-layer, not language"
    print(f"verdict: {verdict}")

    rows_c = run_variant_c(gold_pl, gold_en)
    rec_c = sum(r["hit"] for r in rows_c) / len(rows_c)
    print(f"C - A = {rec_c - rec_a:+.3f}")

    out = {
        "prereg": PREREG,
        "timestamp": "2026-10-18",
        "verdict": verdict,
        "A": {"recall": round(rec_a, 4), "rows": rows_a},
        "B": {"recall": round(rec_b, 4), "rows": rows_b},
        "C": {"recall": round(rec_c, 4), "rows": rows_c},
        "delta_B_minus_A": round(delta, 4),
        "delta_C_minus_A": round(rec_c - rec_a, 4),
    }
    out_path = ROOT / "handoff" / "en-vs-pl-tier3-2026-10-18" / "results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved -> {out_path}")


if __name__ == "__main__":
    main()
