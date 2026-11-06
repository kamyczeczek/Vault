---
flag: decisions-dedup-and-renumber-2026-11-05
since: 2026-11-05
owner: mateusz
agent: omp
model: omniroute/agy/gemini-3.8-flash-low
origin: user-requested-continuation
---

`decisions-dedup-and-renumber-2026-11-05` — 2026-11-05: usunięto kolizję numeracji w `DECISIONS.md`. Dwie decyzje z nagłówka (`D16 — tool chunks` i `D17 — workspace gate`) przeniesiono na koniec jako D26 i D27; odchudzono D13 usuwając redundantną listę 6 reguł z `AGENTS.md`/`CONTEXT-MAP.md`. Baza `brain.db` po `scripts/ingest_brain.py` ma teraz kompletne 27 decyzji (zamiast 25 z cichym nadpisywaniem).

Weryfikacja: `python scripts/ingest_brain.py --check` OK (27 decisions); `python scripts/memory/eval_brain.py --check` OK (hit@5=9/10, refusal=3/4, MRR=0.900); `git diff --check` OK; `python scripts/check_workspace_integrity.py` OK.

not checked: brak.
