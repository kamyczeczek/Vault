#!/usr/bin/env python3
"""Run deterministic retrieval benchmark against graph/ask.py's SQLite index."""
import json
import sqlite3
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ask

ROOT = Path(__file__).resolve().parents[2]
DB = Path(__file__).with_name("graph.db")
SPEC = Path(__file__).with_name("retrieval_benchmark.json")

def tokens(text):
    return {x.lower() for x in text.replace("-", " ").split() if len(x) > 2}

def family(identifier):
    import re
    return re.sub(r"^\d+_", "", identifier)


sys.path.insert(0, str(ROOT / "scripts"))
from check_corpus_health import scan_corpus  # noqa: E402


def verdict() -> dict:
    """Stamp whether these numbers may be used as a baseline.

    Damaged chunks cannot tokenize every query term, so if they compete for
    ranking they cap retrieval quality from above.  They are now excluded at
    query time by `knowledge/graph/quarantine.json`, so the measurement is
    sound over the searchable corpus — but only if the quarantine actually
    covers every damaged chunk.  An uncovered chunk means a damaged chunk is
    still competing, so the artifact is stamped VOID rather than quietly
    publishing a defective baseline.
    """
    offenders, artifacts = scan_corpus(ROOT / "knowledge" / "corpus")
    if not offenders:
        return {"status": "VALID", "corpus_artifacts": 0}

    quarantined = set()
    quarantine_path = ROOT / "knowledge" / "graph" / "quarantine.json"
    if quarantine_path.exists():
        quarantined = set(json.loads(
            quarantine_path.read_text(encoding="utf-8")).get("chunk_ids", {}))
    # Offender keys are chunk file stems; quarantine keys are chunk ids.
    uncovered = set()
    for name in offenders:
        chunk_id = name[:-3] if name.endswith(".md") else name
        if chunk_id not in quarantined:
            uncovered.add(chunk_id)
    if not uncovered:
        return {
            "status": ("VALID — measured over the searchable corpus; "
                       f"{len(quarantined)} damaged chunks excluded at query time"),
            "corpus_artifacts_quarantined": artifacts,
            "corpus_chunks_quarantined": len(quarantined),
        }
    return {
        "status": ("VOID — damaged chunks are not fully excluded from ranking, "
                   "so these numbers are capped; do not use as a baseline"),
        "corpus_artifacts": artifacts,
        "corpus_chunks_affected": len(offenders),
        "corpus_chunks_uncovered": len(uncovered),
        "void_reason": (
            f"{len(offenders)} corpus chunks carry run-together words and "
            f"{len(uncovered)} of them are not covered by "
 "knowledge/graph/quarantine.json, so damaged text still competes for ranking. "
            "Re-run scripts/build_quarantine.py. See "
            "subprojects/vera/experiments/runs/C1_corpus_whitespace_defect.md"
        ),
    }

def main():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    conn = sqlite3.connect(DB)
    rows = []
    for case in spec["cases"]:
        start = time.perf_counter()
        results = ask.query(case["query"], limit=5, recall=True)
        elapsed_ms = (time.perf_counter() - start) * 1000
        hit_ids = [r["id"] for r in results]
        hit_text = " ".join((r.get("title", "") + " " + r.get("body", "")).lower() for r in results)
        gold = set(case["gold_sources"])
        retrieved = set(hit_ids)
        gold_families = {family(x) for x in gold}
        retrieved_families = {family(x) for x in retrieved}
        exact_tp = len(gold & retrieved)
        family_tp = len(gold_families & retrieved_families)
        exact_precision = exact_tp / len(retrieved) if retrieved else 0.0
        exact_recall = exact_tp / len(gold) if gold else 0.0
        family_precision = family_tp / len(retrieved_families) if retrieved_families else 0.0
        family_recall = family_tp / len(gold_families) if gold_families else 0.0
        concept_coverage = sum(1 for c in case["required_concepts"] if c.lower() in hit_text) / len(case["required_concepts"])
        rows.append({"id":case["id"], "hits":hit_ids, "gold_sources":list(gold), "exact_precision":round(exact_precision,3), "exact_recall":round(exact_recall,3), "family_precision":round(family_precision,3), "family_recall":round(family_recall,3), "concept_coverage":round(concept_coverage,3), "latency_ms":round(elapsed_ms,3)})
    conn.close()
    summary = {"cases":len(rows), "mean_exact_precision":round(sum(x["exact_precision"] for x in rows)/len(rows),3), "mean_exact_recall":round(sum(x["exact_recall"] for x in rows)/len(rows),3), "mean_family_precision":round(sum(x["family_precision"] for x in rows)/len(rows),3), "mean_family_recall":round(sum(x["family_recall"] for x in rows)/len(rows),3), "mean_concept_coverage":round(sum(x["concept_coverage"] for x in rows)/len(rows),3), "mean_latency_ms":round(sum(x["latency_ms"] for x in rows)/len(rows),3)}
    out = Path(__file__).with_name("retrieval_benchmark_results.json")
    output = {"benchmark":"retrieval_quality_v1", "graph_fingerprint":Path(Path(__file__).with_name('.graph_fingerprint')).read_text().strip(), "summary":summary, "results":rows}
    output.update(verdict())
    out.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__": main()
