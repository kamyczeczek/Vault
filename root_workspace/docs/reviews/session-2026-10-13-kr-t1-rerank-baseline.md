# Session Review: T1 — Rerank Baseline Verification (Vectors + BAAI/bge-reranker-base)

- **Date:** 2026-10-13
- **Ticket:** T1
- **Status:** Closed / Verified
- **Target:** Verify whether vectors + CrossEncoder (`BAAI/bge-reranker-base`) still achieves MRR@5 = 0.376 on the Trust Set.

## 1. Execution & Measurement

Ran `scripts/_scratch/run_rerank.py` over the Trust Set (`n=33`) using embedding model `paraphrase-multilingual-MiniLM-L12-v2` and cross-encoder `BAAI/bge-reranker-base`.

Result from `scripts/_scratch/krok2_rerank_results.json`:
```json
[
  {
    "mode": "VECTORS_RERANK_BAAI/bge-reranker-base",
    "r1": 0.30303030303030304,
    "r3": 0.4090909090909091,
    "r5": 0.4696969696969697,
    "r10": 0.5303030303030303,
    "mrr5": 0.37575757575757573,
    "mrr10": 0.38383838383838376
  }
]
```

## 2. Findings & Conclusion

- **MRR@5:** **0.376** (0.375757...)
- **Recall@5:** 0.470
- **Recall@10:** 0.530
- **Recall@1:** 0.303
- **Conclusion:** The baseline vectors + rerank pipeline (`BAAI/bge-reranker-base`) is fully stable and reproduces the historical 0.376 MRR@5 exactly.
