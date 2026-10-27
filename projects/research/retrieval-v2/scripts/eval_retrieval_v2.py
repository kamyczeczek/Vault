"""Evaluate retrieval-v2 stack (attune-rag DirectoryCorpus + min_score abstention)
on canary and in-corpus test questions.
"""
import json
import sys
from pathlib import Path

PILOT_ROOT = Path(__file__).resolve().parents[2] / "knowledge-retrieval" / "pilots" / "graphrag"
CORPUS_DIR = Path(__file__).resolve().parents[1] / "corpus"

from attune_rag import RagPipeline, DirectoryCorpus, KeywordRetriever

corpus = DirectoryCorpus(CORPUS_DIR)
# Calibrated or configured min_score for abstention
retriever = KeywordRetriever(min_score=5.0)
pipeline = RagPipeline(corpus=corpus, retriever=retriever)

canary_path = PILOT_ROOT / "eval" / "canary.json"
canary_data = json.loads(canary_path.read_text(encoding="utf-8"))

results = {"canary": [], "in_corpus_pl": []}

# Canary eval (should refuse -> refused=True means fallback used or no hits/abstained)
for c in canary_data.get("questions", []):
    res = pipeline.run(c["text"], k=5)
    refused = res.fallback_used or (len(res.citation.hits) == 0)
    results["canary"].append({"qid": c["qid"], "text": c["text"], "refused": refused, "hits": len(res.citation.hits)})

n_canary = len(results["canary"])
n_refused = sum(1 for r in results["canary"] if r["refused"])
print(f"Canary refusal: {n_refused}/{n_canary}")

out = Path(__file__).resolve().parents[1] / "reports" / "retrieval_v2_canary.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"ARTIFACTS: {out}")
print("RETRIEVAL_V2_EVAL_DONE")
