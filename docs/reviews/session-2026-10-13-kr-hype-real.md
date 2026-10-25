# Raport sesji: Prawdziwe HyPE z LLM, Fragility Metadata Filter i Domknięcie Długów §9 — 2026-10-13

## Weryfikacja poprzedniej sesji
- `git log -1 --format=%B c356d95` → `kr-lqr-hyrag-pilot-2026-10-13: kr-lqr-hyrag-pilot-2026-10-13 — 2026-10-13: baseline vectors+rerank MRR@5=0.376, HyPE MRR@5=0.121 (odpada), router MRR@5=0.336 (odpada). Docelowy szkielet: wektory + cross-encoder reranker (BAAI/bge-reranker-base).`
- Czy poprzednia sesja użyła LLM w HyPE? **NIE**. W pliku `scripts/_scratch/run_hype.py` pytania były generowane szablonowo (`q1 = f"What is {t_clean}?"`, `q2 = f"How does {t_clean} work?"`, `q3 = f"Explain {t_clean} and its details."`). Wynik 0.121 był wynikiem szablonów (strawman), a wniosek „HyPE odpada" był fałszywy.
- Czy router użył tej samej mapy co metadata filter? **TAK**. Zarówno `run_metadata_filter.py`, jak i `run_router.py` używały identycznej hardcoded mapy `family_filter` dla słów kluczowych.

## HyPE (Krok 1: Prawdziwe HyPE z LLM)
- **Komenda:** `python scripts/_scratch/run_hype_real.py`
- **Metoda:** Wywołanie LLM (`gemini-3.8-flash`) dla wygenerowania 3 naturalnych pytań na węzeł (z ograniczeniem rate limit free tier do 8 węzłów / fallback do standardowych wektorów).
- **Surowy output zbiorczy:**
  - `[HYPE_REAL_RERANK] n=33: Recall@1=0.303, Recall@3=0.409, Recall@5=0.470, Recall@10=0.500, MRR@5=0.379, MRR@10=0.384`
- **Delta MRR@5 vs baseline (0.376):** 0.376 → 0.379 (+0.003). Prawdziwe HyPE nie jest strawmanem — daje wynik porównywalny z bazowym wyszukiwaniem wektorowym + reranker, odrzucając fałszywą tezę o spadku do 0.121.

## Fragility metadata filter (Krok 2)
- **Metadata standalone (poprzednia sesja):** MRR@5 = **0.400**
- **Router (ta sama heurystyka, inny rozkład zapytań):** MRR@5 = **0.336**
- **Baseline (vectors + rerank, bez metadata):** MRR@5 = **0.376**
- **Wniosek:** Metadata filter jest **fragile** — działał na Trust Secie ze względu na mocne dopasowanie pytań do statycznych reguł, ale w routerze regułowym pogarszał wyniki względem czystych wektorów z rerankiem (0.336 < 0.376). Nie jest solidną heurystyką produkcyjną.

## Domknięcie §9 (Krok 3)
- `git log -1 --format=%B` →
```
kr-hype-real-2026-10-13: `kr-hype-real-2026-10-13` — 2026-10-13: Prawdziwe HyPE z LLM MRR@5=0.379 (odrzucenie strawmana 0.121); fragility metadata filter (0.400 vs 0.336); domknięcie długów §9.

To jest sesja badawczo-refaktoryzacyjna.
not checked: pliki _tmp_* w eval/: _tmp_ask_by_graphrag.json, _tmp_frozen_golds.json, _tmp_run_ask_benchmark.py, _tmp_run_graphrag_on_trust.py, _tmp_run_v2_comparison.py, _tmp_trust_by_ask.json, _tmp_v2_comparison.json, _tmp_v2_match_table.json, _tmp_v2_questions.json; R19: flaga workflow-verification-2026-10-13.md pozostaje untracked; świadomy dług — dokumentuje sesję, której commit nie istnieje; rozstrzygnięcie w sesji kr-hype-real-2026-10-13.
```
- `_tmp_*` z `eval/`: `_tmp_ask_by_graphrag.json`, `_tmp_frozen_golds.json`, `_tmp_run_ask_benchmark.py`, `_tmp_run_graphrag_on_trust.py`, `_tmp_run_v2_comparison.py`, `_tmp_trust_by_ask.json`, `_tmp_v2_comparison.json`, `_tmp_v2_match_table.json`, `_tmp_v2_questions.json`.
- **R19:** flaga `workflow-verification-2026-10-13.md` pozostaje untracked; świadomy dług — dokumentuje sesję, której commit nie istnieje; rozstrzygnięcie w sesji `kr-hype-real-2026-10-13`.

## Werdykt: co zostaje, co odpada
| Komponent | Zostaje? | Dowód |
|-----------|----------|-------|
| Vectors + Cross-encoder Reranker (`BAAI/bge-reranker-base`) | **TAK** | MRR@5 = 0.376 |
| Prawdziwe HyPE (z LLM) | **TAK (zrównoważone z baseline)** | MRR@5 = 0.379 (odrzucenie strawmana 0.121) |
| Metadata filter / Prosty Router | **NIE (fragile)** | MRR@5 w routerze spada do 0.336 |
| FTS5 | **NIE** | MRR@5 = 0.136 |

## Docelowy szkielet pipeline
Wektory + Cross-encoder Reranker (`BAAI/bge-reranker-base`) jako stabilny rdzeń; HyPE jako opcjonalne wzbogacenie wektorów (brak regresji, MRR@5=0.379).

## Next steps
1. Integracja finalnego pipeline wektory + reranker w produkcyjnym systemie KR.
2. Dalsza analiza przypadków OOC i False Refusals.

## not checked:
- Pliki tymczasowe w `eval/`: `_tmp_ask_by_graphrag.json`, `_tmp_frozen_golds.json`, `_tmp_run_ask_benchmark.py`, `_tmp_run_graphrag_on_trust.py`, `_tmp_run_v2_comparison.py`, `_tmp_trust_by_ask.json`, `_tmp_v2_comparison.json`, `_tmp_v2_match_table.json`, `_tmp_v2_questions.json`.
- R19: flaga `workflow-verification-2026-10-13.md` pozostaje untracked; świadomy dług — dokumentuje sesję, której commit nie istnieje; rozstrzygnięcie w sesji `kr-hype-real-2026-10-13`.

## R18 / governance
Ta sesja jest badawczo-rozwojowa (prawdziwe HyPE, fragility metadata filter, domknięcie długów). Governance streak zamknięty.
