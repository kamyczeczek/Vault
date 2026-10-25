---
type: Concept
flag: okf-rag-scope-and-gate-2026-10-25
since: 2026-10-25
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: Notes/OKF-rag/EXPERIMENT-benchmark-scope-2026-10-25.md
title: okf-rag-scope-and-gate-2026-10-25
generated: { by: opencode, at: 2026-10-25T00:00:00Z }
---

`okf-rag-scope-and-gate-2026-10-25` — 2026-10-25: ustalono, że `Notes/OKF-rag`
zostaje poza kontraktem projektu (ADR `handoff/decisions/notes-okf-rag-outside-project-contract.md`),
maszyneria idzie do root `scripts/`, a gate do `check_workspace_integrity.py`
jako advisory do czasu migracji. Dodano słownik artefaktów `Notes/OKF-rag/CONTEXT.md`,
wiersz kontekstu w `CONTEXT-MAP.md` i pre-registered
`EXPERIMENT-benchmark-scope-2026-10-25.md` z realnym przypadkiem adwersaryjnym
(Q15: blok `napkin.md:3985–3998` zalicza `related`, choć nie zawiera
odpowiedzi). Plan: 3 commity — (1) te artefakty, (2) migracja 5 notatek
kuratorskich do strukturalnego `sources: [{file, lines}]` + allowlista 2 decyzji,
(3) skill `retrieval-two-stage` + check w integrity. Next: dodać tryb `scoped`
do `scripts/run_okf_rag_benchmark.py`, bo bez niego reguła scope jest
niemierzalna i eksperyment nie jest uruchamialny jedną komendą.

not checked: nie zmierzono przebiegu ze scope (brak trybu `scoped`); nie
zmigrowano frontmattera żadnej notatki; gate cytowań nie istnieje; skill
`retrieval-two-stage` nie istnieje; Q02 i Q20 nadal bez `exact`/`related`.
