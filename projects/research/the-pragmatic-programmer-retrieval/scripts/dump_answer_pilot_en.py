"""Session 6: dump top-8 chunks (Tier 3 retrieve(), NOT full_retrieve) for EN answer-layer pilot.

Sample: 15 answerable (q001-q015) + 8 unanswerable (u001-u008) + 1 canary (q001 question + q003 chunks).
Timing per question. Output: handoff/session-6/dumps/*.json + input-stage topics report.
Frozen pre-registration: retrieve() = Tier 3, top_k=8, chunks verbatim, no filtering.
"""
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.recall_hybrid import retrieve, get_chunks_meta  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GOLD = ROOT / "eval" / "gold_set_extended_en.json"
OUT = ROOT / "handoff" / "session-6" / "dumps"
TOP_K = 8


def main() -> None:
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    qs = {q["id"]: q for q in gold["questions"]}
    answerable = [f"q{i:03d}" for i in range(1, 16)]
    unanswerable = [f"u{i:03d}" for i in range(1, 9)]
    OUT.mkdir(parents=True, exist_ok=True)

    index = {}
    report = []
    for qid in answerable + unanswerable:
        q = qs[qid]
        t0 = time.perf_counter()
        ids = retrieve(q["question"], top_k=TOP_K)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        meta = get_chunks_meta(ids)
        index[qid] = {
            "id": qid,
            "question": q["question"],
            "gold_topics": q.get("topics", []),
            "top8ids": ids,
            "top8topics": [m["topic"] for m in meta],
            "dt_ms": round(dt_ms, 2),
            "chunks": meta,
        }
        report.append({"id": qid, "dt_ms": round(dt_ms, 2), "top8topics": [m["topic"] for m in meta]})

    canary_chunks = index["q003"]["chunks"]
    index["canary"] = {
        "id": "canary",
        "question": index["q001"]["question"],
        "gold_topics": index["q001"]["gold_topics"],
        "top8ids": [m["id"] for m in canary_chunks],
        "top8topics": [m["topic"] for m in canary_chunks],
        "dt_ms": 0.0,
        "chunks": canary_chunks,
    }
    report.append({"id": "canary", "dt_ms": 0.0, "top8topics": index["canary"]["top8topics"]})

    times = [r["dt_ms"] for r in report if r["id"] != "canary"]
    times.sort()
    n = len(times)
    summary = {
        "tier": "3 (retrieve, RRF, no reranker)",
        "model": "opencode/glm-5.3-flash-free",
        "n_queries": n,
        "p50_ms": round(statistics.median(times), 2),
        "p95_ms": round(times[int(round(0.95 * (n - 1)))], 2),
        "sanity1_median_lt_500ms": statistics.median(times) < 500,
    }
    (OUT / "dump.json").write_text(
        json.dumps({"summary": summary, "index": index}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=1))
    for r in report:
        print(f'{r["id"]}\t{r["dt_ms"]} ms\ttopics={r["top8topics"]}')


if __name__ == "__main__":
    main()
