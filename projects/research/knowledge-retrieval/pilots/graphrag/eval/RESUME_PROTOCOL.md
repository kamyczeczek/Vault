---
type: Concept
title: RESUME_PROTOCOL
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# RESUME_PROTOCOL — jak domknąć pętlę ręcznie

## Stan bieżący (2026-10-11)
- v1 pomiar: WYKONANY (baseline_measurements/graphrag_baseline.json)
- v2 pomiar: NIE WYKONANY (shell zablokowany dla agenta)
- Commit: NIE WYKONANY (shell zablokowany)
- Pliki gotowe do uruchomienia: frozen_eval_sets_v2.py, measure_baseline_v2.py

## Krok 1 — Uruchom pomiar v2 (manualnie)

Otwórz terminal (PowerShell, poza sesją agenta):

    cd C:\Users\Mateusz\Desktop\root_worksapce
    projects\research\retrieval-v2\.venv\Scripts\python.exe projects\research\knowledge-retrieval\pilots\graphrag\eval\measure_baseline_v2.py

Oczekiwany wynik:
- stdout: linie `in_corpus_pl: n=10 refused=? MRR=? Recall=?` itd.
- plik: `projects/research/knowledge-retrieval/pilots/graphrag/eval/baseline_measurements_v2/graphrag_baseline_v2.json`

Jeśli skrypt się wywali — zapisz pełny traceback. NIE improwizuj.

## Krok 2 — Porównaj v1 vs v2

Odczytaj oba JSON-y i wypełnij tabelę:

| Grupa | v1 (12/8) | v2 (10/10) | Δ |
|-------|-----------|------------|---|
| in_corpus_pl refusal | 5/12 | ?/10 | ? |
| in_corpus_pl MRR@5 | 0.507 | ? | ? |
| in_corpus_en refusal | 0/8 | ?/10 | ? |
| in_corpus_en MRR@5 | 0.771 | ? | ? |
| ooc_pl refusal | 5/5 | 5/5 (oczekiwane bez zmian) | 0 |
| canary refusal | 5/5 | 5/5 (oczekiwane bez zmian) | 0 |

**Interpretacja:**
- refusal PL v2 < 5/10 → częściowo artefakt złego podziału (Q1, Q2 były EN, nie PL)
- refusal PL v2 = 5/10 → realny problem pilota na pytaniach PL
- refusal PL v2 > 5/10 → pogorszenie, STOP i analiza

## Krok 3 — Decyzja o commitach

Zdecyduj, które pliki commitować. Kandydaci:
- `frozen_eval_sets_v2.py` (narzędzie)
- `measure_baseline_v2.py` (narzędzie)
- `BASELINE.md` (z korektą)
- `retrieval_v2_final_outcome.md` (z korektą)
- `baseline_measurements_v2/graphrag_baseline_v2.json` (pomiar)
- `RESUME_PROTOCOL.md` (ten plik)

Sprawdź, gdzie należą:
    git -C projects/research/knowledge-retrieval rev-parse --show-toplevel
    git -C projects/research/retrieval-v2 rev-parse --show-toplevel

**Nie używaj `git add -A` ani `git add .`.** Wymień pliki jawnie.

## Krok 4 — Napraw blocker sandboxa (opcjonalnie)

Jeśli chcesz, żeby kolejny agent mógł wykonywać git/pomiar:
- Sprawdź config DSH: `C:\Users\Mateusz\AppData\Local\Programs\DeepSeek Harness\resources\app.asar`
- Poszukaj opcji typu `allow_shell`, `sandbox_permissions`, `process_spawn`
- **To jest decyzja właściciela, nie agenta.** Agent nie modyfikuje sandboxa.

Alternatywa: użyj harnessu, który nie blokuje `pwsh` (np. uruchom opencode dla tego zadania).

## Krok 5 — Zamknięcie

Po wykonaniu kroków 1–3, oceń:
- Czy `refusal 5/12` na in-corpus PL to był artefakt, czy realny problem?
- Czy graphrag baseline jest wystarczający dla twojego use case?
- Czy wracać do hybrydy / cross-encodera, czy zaakceptować graphrag?

Zapisz decyzję w `retrieval_v2_final_outcome.md` (sekcja „Status końcowy").
