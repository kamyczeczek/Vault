---
type: Concept
flag: graphrag-d002-minigraph
since: 2026-10-10
owner: Mateusz
agent: opencode
model: muse-spark-1.3-contributor-free
origin: user "mini-graf" 2026-10-10 (rozstrzygnięcie D-002)
title: graphrag-d002-minigraph
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`graphrag-d002-minigraph` — 2026-10-10: D-002 RESOLVED. Backend Fazy 5 to
mini-graf (`pilots/graphrag/fixtures/mini_graph.db`, `mini_graph: PASS` —
3 nodes, 2 edges, triple z przykładu sesji 05). Schemat zwierciadlany vs
archiwum; `fixtures/.gitignore` trzyma `*.db` poza repo. Archiwum opcją na
Fazę 6. D-001/D-003 zawężone (relacje ze speca + stub LIKE wystarczą na
dowód formatu). Faza 5 `in_progress` w task_plan.

Bramy: MAP zregenowana (4 moduły), `diff --check` czysty, KR preflight
READY. Root integrity FAIL tylko na znanym stanie zastanym (6 śmieci root
+ lag R14). W repo KR wiszą niezacommitowane zmiany z wcześniejszych sesji
(CLAUDE.md, GATES.md, defect-classes.md, preflight.py untracked) — nie moje,
nie tykam, nie commituję bez polecenia.

Next: 8 narzędzi jako deterministyczny moduł na mini-grafie (seed = jawny
stub LIKE, Krok 2 = relacje ze speca), potem dowód Fazy 5 na pytaniu
"Kto zarządza firmą, która stworzyła produkt X?".
