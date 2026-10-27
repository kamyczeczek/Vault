"""answer-layer pilot: dump top-8 chunks verbatim per question.

Dump only — no grading, no model calls. One file per question under
handoff/pilot-answer-layer-2026-10-18/dumps/. Verification is done by the
parent session using eval/gold_set_extended.json topics (input-stage check).
"""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Tier 3 (production): hybrid RRF only, no cross-encoder reranker.
# full_retrieve = Tier 4 (RRF(40) + reranker, ~9 s/query) — excluded from production.
from scripts.recall_hybrid import get_chunks_meta, retrieve  # noqa: E402

GOLD = ROOT / "eval" / "gold_set_extended.json"
OUT = ROOT / "handoff" / "pilot-answer-layer-2026-10-18" / "dumps"


def main() -> None:
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    questions = gold["questions"]
    answerable = [q for q in questions if not q["id"].startswith("u")]
    unanswerable = [q for q in questions if q["id"].startswith("u")]
    sample = answerable[:15] + unanswerable
    OUT.mkdir(parents=True, exist_ok=True)

    summary = []
    latencies = []
    for q in sample:
        t0 = time.perf_counter()
        ids = retrieve(q["question"], top_k=8)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        latencies.append(dt_ms)
        top = get_chunks_meta(ids)
        gold_topics = set(q["topics"])
        hit = any(c["topic"] in gold_topics for c in top)
        record = {
            "id": q["id"],
            "question": q["question"],
            "type": q["type"],
            "header": q["header"],
            "gold_topics": q["topics"],
            "input_stage_hit": hit,
            "chunks": [
                {
                    "topic": c["topic"],
                    "topic_title": c["topic_title"],
                    "chapter": c["chapter"],
                    "page_book": c["page_book"],
                    "text": c["text"],
                }
                for c in top
            ],
        }
        (OUT / f"{q['id']}.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        topics_in_top = [c["topic"] for c in top]
        summary.append(f"{q['id']} hit={hit} {dt_ms:.1f} ms top8topics={topics_in_top}")

    source = [q for q in sample if q["id"] == "q003"][0]
    t0 = time.perf_counter()
    ids_src = retrieve(source["question"], top_k=8)
    src_ms = (time.perf_counter() - t0) * 1000.0
    latencies.append(src_ms)
    top_src = get_chunks_meta(ids_src)

    print("\n".join(summary))

    # canary: q001's question (DRY) with top-8 of the most distant sample
    src = [q for q in sample if q["id"] == "q003"][0]
    canary = {
        "id": "canary",
        "question": [q for q in answerable if q["id"] == "q001"][0]["question"],
        "type": "canary",
        "header": "canary (q001 question text + q003 top-8 chunks)",
        "gold_topics": [c["topic"] for c in top_src],
        "input_stage_hit": None,
        "chunks": [
            {
                "topic": c["topic"],
                "topic_title": c["topic_title"],
                "chapter": c["chapter"],
                "page_book": c["page_book"],
                "text": c["text"],
            }
            for c in top_src
        ],
    }
    (OUT / "canary.json").write_text(
        json.dumps(canary, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("canary chunks topics:", [c["topic"] for c in top_src])

    lat_sorted = sorted(latencies)
    med = statistics.median(lat_sorted)
    p95 = lat_sorted[int(0.95 * (len(lat_sorted) - 1))]
    total = sum(latencies)
    print(f"\ninterpreter: {sys.executable}")
    print(f"latency: n={len(latencies)} p50={med:.1f} ms p95={p95:.1f} ms total={total:.1f} ms")
    if med > 500.0:
        print("STOP GATE: median > 500 ms — dumps leaked Tier 4 (reranker). Not cold-cache improvisation.")
        sys.exit(1)
    timing_path = ROOT / "handoff" / "pilot-answer-layer-2026-10-18" / "dump-timing.txt"
    timing_path.write_text(
        f"interpreter: {sys.executable}\n"
        f"n={len(latencies)} p50={med:.1f} ms p95={p95:.1f} ms total={total:.1f} ms\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
