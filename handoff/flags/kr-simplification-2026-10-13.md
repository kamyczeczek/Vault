---
flag: kr-simplification-2026-10-13
since: 2026-10-13
owner: mateusz
agent: opencode
model: gemini/gemini-flash-lite-latest
origin: session-close
---

`kr-simplification-2026-10-13` — 2026-10-13: vectors-only MRR@5=0.334 + rerank BAAI/bge-reranker-base MRR@5=0.376, metadata filtering MRR@5=0.400, age decay BLOKADA (brak pola daty). Docelowy szkielet: vectors + metadata pre-filtering + cross-encoder reranking, bez FTS5.
To jest sesja refaktoryzacyjna, nie badawcza.
not checked: pliki tymczasowe _tmp_* w scripts/_scratch/ (krok1_results.json, run_stage_isolation_krok1.py, run_rerank.py, run_metadata_filter.py, krok2_rerank_results.json, krok3_meta_results.json, inspect_metadata.py, inspect_date.py, check_db_schema.py); R19.
