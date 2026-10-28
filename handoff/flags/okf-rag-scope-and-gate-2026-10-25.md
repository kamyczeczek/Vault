---
flag: okf-rag-scope-and-gate-2026-10-25
since: 2026-10-28
owner: mateusz
agent: opencode
model: omniroute/agy/gemini-3.8-flash-high
origin: session-close
---

`okf-rag-scope-and-gate-2026-10-25` — 2026-10-28: commit 2 OKF-rag wdrożony — zmigrowano 5 notatek kuratorskich (`DECISION-minimalny-przeplyw-wiedzy.md`, `DECISION-kontrakt-odpowiedzi-retrieval.md`, `EXPERIMENT-benchmark-scope-2026-10-25.md`, `EXPERIMENT-retrieval-benchmark-20-2026-10-25.md`, `EXPERIMENT-retrieval-answer-contract-2026-10-25.md`) do formatu `sources: [{file, lines}]` z precyzyjnymi zakresami linii. Skill `retrieval-two-stage` istnieje w `skills/retrieval-two-stage/SKILL.md` (commit `653f87d`). Wszystkie 5 notatek zweryfikowane deterministycznym gate'em `scripts/gate_checks.py --gate g7-okf-sources` (PASS). Next: tryb `scoped` w runnerze benchmarku, gate cytowań i adnotacje `related`.

not checked: tryb `scoped` w `scripts/run_okf_rag_benchmark.py`; gate cytowań w integrity; adnotacje `related` dla pytań Q01–Q20.
