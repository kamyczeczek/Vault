# Memory index verify — T4 (2026-10-14, sesja `11/10`)

<!-- audit:begin -->
## Kontekst
Sesja `11/10`: FAZA 1 wykazała brak technicznej ścieżki dla L1-contracts
bez decyzji właściciela (wykluczenie HANDOFF.md: 507428 → ~342000 B,
nadal > 250 KB; szersze cięcia redefiniują kontrakt = warunek (b) flagi
`chain-non-convergence-2026-10-14`). Zgodnie z planem sesji wykonano
ticket T4 z innej domeny (historia sesji).

## Wynik: memory_index.py działa, hit@5=1.000
- `python scripts/memory_index.py stats`: index
  `scripts/_scratch/sessions/memory.db` — 1374 sesje, 228852 chunki,
  zakres 2026-07-09 → 2026-10-13 (03:12:20).
- By agent: omp 503, opencode 203, hermes 189, goose 112, curated 110,
  pi 107, jcode 65, antigravity 32, droid 24, cursor 17, cline 12.
- By chunk type: content 135208, tool 46401, error 35673,
  decision 11208, curated 362.
- `python scripts/eval_memory_retrieval.py`: `15/15` PASS,
  hit@5=1.000, MRR=0.644.

## Zbiór ewaluacyjny
`scripts/eval_memory_retrieval.py` — 15 zapytań (m.in. provider error,
whitespace scar, FTS decision, freshness failure, workspace gate,
prompt caching, session affinity, unicode tokenizer, memory contract,
agent memory). Każde PASS z top-5 sesji.

## Uwaga: lag indeksu (R14, nie blokuje)
`check_workspace_integrity.py`: index covers through 2026-10-13
03:12:20, newest on disk 2026-10-14 02:22:05 (lag 23:09:45) — status OK,
nie fail. Świeże sesje (w tym sesja `1/10` z dziś) nie są jeszcze zaindeksowane.

## FAZA 1 (L1-contracts) — podsumowanie dowodu
Skrypt `scripts/_scratch/count_l1_components.py` (usunięty po użyciu):
63 pliki, suma on-disk 575086 B vs output repomix 507428 B (ratio 0.88).
Grupy: HANDOFF.md 187359, skills 168510, root/docs/handoff misc 122861,
projects 94617, STATE.md 1739. TOP: HANDOFF.md 187359, DECISIONS.md
31553, SCARS.md 21399, benchmark-core/MAP.md 18788.
- Wykluczenie samego HANDOFF.md: ~507428 − 165000 ≈ 342000 B > 250 KB.
- Zejście pod próg wymaga też wycięcia skills (redefinicja kontraktu)
  albo opcji w `build_handoff.py` (warunek (b) flagi) — obie ścieżki
  wymagają decyzji właściciela. Werdykt: NIE.
- Brak bramki na 250 KB w `check_workspace_integrity.py` (grep: brak
  "250"/"L1") — próg jest z mapy, nie z gate'a; cięcie konfigiem w celu
  "zejścia pod próg" byłoby gamingiem metryki (duch S62, zasada 4).

## Tool calls
| Wartość | Komenda | Surowy output (fragment) |
|---|---|---|
| `1374`, `228852`, `503`, `203`, `189`, `135208`, `46401`, `35673`, `11208`, `362` | `python scripts/memory_index.py stats` | sessions/chunks by agent and type |
| `15`, `1.000`, `0.644` | `python scripts/eval_memory_retrieval.py` | hit@5 and MRR |
| `507428`, `575086`, `63`, `187359`, `168510`, `122861`, `94617`, `31553`, `21399`, `18788`, `342000`, `250` | `python scripts/_scratch/count_l1_components.py` | FAZA 1 component sizes |
| `110`, `107`, `0.88`, `1739`, `165000` | `python scripts/memory_index.py stats` + FAZA 1 math | curated/pi agent counts, disk-to-repomix ratio, STATE.md, HANDOFF repomix share |
| `506999`, `507311` | `docs/reviews/session-2026-10-14-state-export-final.md` | historical L1 sizes (sesja 5 → 6) |

## not checked:
- L1-contracts: decyzja właściciela (zaakceptować dług czy wskazać kierunek).
- KR pilot terminated: decyzja właściciela o nowym kierunku.
- Re-indeksacja pamięci po dzisiejszych sesjach (R14 lag 23:09:45).
<!-- audit:end -->
