---
flag: state-export-levels
since: 2026-10-13
owner: mateusz
agent: opencode
model: oc/claude-3-5-sonnet
origin: session-close
---

`state-export-levels` — 2026-10-13: folder eksportów po (target × poziom). Workspace L0/L1/L2, projekt L0/L1. Root repomix.config.json usunięty. Driver run_exports.py.

not checked:
- T18-FIX (graphrag.py, measure_trust_set.py, trust_set_results.json) — poza zakresem sesji.
- eval/_tmp_ask_by_graphrag.json, eval/_tmp_frozen_golds.json, eval/_tmp_run_ask_benchmark.py, eval/_tmp_run_graphrag_on_trust.py, eval/_tmp_run_v2_comparison.py, eval/_tmp_trust_by_ask.json, eval/_tmp_v2_comparison.json, eval/_tmp_v2_match_table.json, eval/_tmp_v2_questions.json — z poprzednich prób eksperymentalnych T18.
