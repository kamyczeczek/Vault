# Session Review: T1 Closure & Debt Resolution (2026-10-13)

## Summary
- **Cel A**: Checked mtime of `scripts/_scratch/krok2_rerank_results.json` (`2026-10-13T00:34:46.112Z` -> cached from `kr-simplification`). Executed fresh `run_rerank.py` with sufficient timeout. Fresh run output: `[VECTORS_RERANK (BAAI/bge-reranker-base)] n=33: Recall@1=0.303, Recall@3=0.409, Recall@5=0.470, Recall@10=0.530, MRR@5=0.376, MRR@10=0.384`. T1 is **confirmed**.
- **Cel B**: Added S62 to `SCARS.md` („Bramka przepisana po niepowodzeniu = fabrykacja przechodzenia").
- **Cel C**: Updated wayfinder retrieval map with confirmed status for T1.

## Lessons for future sessions
1. **`--timeout 900`** for ML model evaluation gates (`run_rerank.py` loads two HF models taking 3-5 minutes on cold start).
2. **CWD of gate = GATES.md directory**. Always set explicit `CWD:` in gates.
3. **Use `--scope scripts/_scratch`** with unlazy checks to prevent `.unlazy/` from landing in root (which violates workspace integrity R1).
4. **Never rewrite a failing gate** into a weaker check or adjust `EXPECT` after observing results (S62).
