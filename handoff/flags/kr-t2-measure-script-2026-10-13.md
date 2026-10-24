---
flag: kr-t2-measure-script-2026-10-13
since: 2026-10-13
owner: mateusz
agent: opencode
model: gemini/gemini-flash-lite-latest
origin: session-close
---

`kr-t2-measure-script-2026-10-13` — 2026-10-13: ustalono, że measure_trust_set.py mierzy hybrydę, T2 zamknięty, T1 gotowy.

- **Cel**: Rozwiązanie ticketu T2 (co mierzy `measure_trust_set.py`).
- **Wynik**: `measure_trust_set.py` mierzy hybrydę (FTS5 + wektory), ponieważ linia 34 w `projects/research/knowledge-retrieval/pilots/graphrag/eval/measure_trust_set.py` ustawia `plan.uzyj_wektorow = True` oraz skrypt nie zawiera `CrossEncoder`.
- **Artefakt**: `docs/reviews/session-2026-10-13-kr-t2-measure-script.md`.
- **Mapa**: Zaktualizowano `docs/wayfinder-retrieval-map.md` (T2 closed, T1 READY).
- **R19**: R19: świadomy dług — flaga workflow-verification-2026-10-13.md pozostaje untracked; retired w T10.

not checked: _tmp_ask_by_graphrag.json, _tmp_frozen_golds.json, _tmp_run_ask_benchmark.py, _tmp_run_graphrag_on_trust.py, _tmp_run_v2_comparison.py, _tmp_trust_by_ask.json, _tmp_v2_comparison.json, _tmp_v2_match_table.json, _tmp_v2_questions.json
