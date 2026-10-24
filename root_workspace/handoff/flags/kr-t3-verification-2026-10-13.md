---
flag: kr-t3-verification-2026-10-13
since: 2026-10-13
owner: mateusz
agent: opencode
model: gemini/gemini-flash-lite-latest
origin: session-close
---

`kr-t3-verification-2026-10-13` — 2026-10-13: rozstrzygnięto rozbieżność T3 (`in_db=False` w toolcallu vs „oracle istnieje" w raporcie). Przyczyna: T3 sprawdzał pusty `graph.db` (0 bajtów); właściwa baza `fixtures/graph_vec.db` (10 373 węzły) zawiera wszystkie 18 oracles (TOTAL_EXISTS=18/18). Werdykt: Scenariusz A z adnotacją — T3 confirmed closed (nie retired), hipoteza „embedding mismatch" wątpliwa. Defect class 4 potwierdzony (family match: AI-modern-approach 1123 warianty, PAIP 828, PRML 736, BSE 647, SICP 518, MAS 510). Dodano S63 do SCARS.md i T13 do mapy (weryfikacja gold IDs vs re-ingest). Bramki G1+G2: ALL MET.

not checked: `pilots/graphrag/eval/_tmp_ask_by_graphrag.json`, `_tmp_frozen_golds.json`, `_tmp_run_ask_benchmark.py`, `_tmp_run_graphrag_on_trust.py`, `_tmp_run_v2_comparison.py`, `_tmp_trust_by_ask.json`, `_tmp_v2_comparison.json`, `_tmp_v2_match_table.json`, `_tmp_v2_questions.json` (9 plików roboczych z eval/); `scripts/_scratch/GATES.md`, `scripts/_scratch/check_oracles.py`, `scripts/_scratch/check_oracles_v2.py` (gitignore — artefakty robocze); R19: świadomy dług (retired w T10).
