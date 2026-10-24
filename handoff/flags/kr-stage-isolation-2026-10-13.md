---
flag: kr-stage-isolation-2026-10-13
since: 2026-10-13
owner: mateusz
agent: opencode
model: gemini/gemini-flash-lite-latest
origin: session-close
---

`kr-stage-isolation-2026-10-13` — 2026-10-13: baseline Recall@10=0.515, FTS5-only Recall@10=0.182, vectors-only Recall@10=0.500. Wąskie gardło: FTS5 (czysty FTS5 ma Recall@10=0.182, wektory dostarczają 0.500). Boundary: 5/10 (50%) przepuszcza przez słowa kluczowe.
not checked: pliki tymczasowe _tmp_* w scripts/_scratch/ (krok1_results.json, run_stage_isolation_krok1.py, inspect_boundary.py); ręczna kwalifikacja 18 pytań ZAWODNE.
To jest sesja badawcza, nie governance. Zero zmian w kodzie produkcyjnym.
