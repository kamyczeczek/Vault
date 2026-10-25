---
type: Concept
flag: okf-rag-source-slices-commit-2026-10-25
since: 2026-10-25
owner: codex
agent: codex
model: openai/gpt-6
title: okf-rag-source-slices-commit-2026-10-25
generated: { by: okf-enforcer/0.6, at: 2026-10-25T14:07:30Z }
---
`okf-rag-source-slices-commit-2026-10-25` — 2026-10-25: commit `f1a7fc8` zapisał generator source slices, testy, specyfikację OKF-rag, wygenerowane slice'y i notatki retrievalowe. Follow-up dodał trzy deterministyczne slice'y Napkin. Q14–Q16 przeszły 9/9 wariantów: właściwy slice zawsze był w top 2 i powyżej 0.55; Q14 wariant nazwany miał lokalny indeks Napkin przed slice'em o 0.0024. `--check` potwierdza manifest i trzy slice'y. Smart Connections: 36/36 plików OKF-RAG obecnych, 453 wektory źródeł i 2446 bloków czytelnych (384 wymiary, 0 błędnych); brak aktywnego błędu adaptera. Nie wykonano pełnego reindeksu, bo kontrole przechodzą; w logu pozostał jeden historyczny `embedding:error`. Następny krok: pełny benchmark 20 pytań tylko jeśli potrzebne jest porównanie wpływu na cały korpus.

not checked:
- pełny benchmark 20 pytań na całym korpusie nie został powtórzony;
- w Smart Connections pozostaje historyczny wpis `embedding:error`, choć aktualny odczyt ścieżek i wektorów jest czysty.
