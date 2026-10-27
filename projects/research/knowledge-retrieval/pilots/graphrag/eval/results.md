---
type: Concept
title: results
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Wyniki ewaluacji graphrag MVP — 5 pytań (Faza 7, Krok 4.3)

Data: 2026-10-11. MVP: `pilots/graphrag/graphrag.py`. Baseline: `ask.py` (czysty FTS5, bez mechanizmu odmowy).
Pytania i oracles: `questions.md`. Proofy: `proof/graphrag/<slug>/` (answer.md + plan.json + trace.md).

## Tabela porównawcza

| # | Pytanie | Typ | graphrag: pokrycie | graphrag: halucynacje | graphrag: refusal | ask.py: top-1 trafność | ask.py: halucynacje |
|---|---------|-----|-------------------|----------------------|-------------------|----------------------|---------------------|
| Q1 | Czym jest SEVerA... | in-corpus | 100% (10/10) | 0 | NIE (odp.) | TAK — `00_severa_...` | 0 |
| Q2 | What trust tiers... | in-corpus | 100% (10/10) | 0 | NIE (odp.) | NIE — `02_the_five...` (oracle `00_okf...` na poz. 3) | 0 |
| Q3 | Kompresja sesji... | in-corpus | 0% (0/4) | 0 | TAK (odmowa) | NIE — `00_agentic_eng...` | irrelevant |
| Q4 | CRLF/SCARS | out-of-corpus | 0% (0/7) | 0 | TAK (poprawna) | NIE — `reflection_scars` | false positive |
| Q5 | Jan Kowalski | out-of-corpus | 0% (0/10) | 0 | TAK (poprawna) | NIE — `794_paradigms...` | false positive |

## Szczegóły

### Q1 — SEVerA (in-corpus)
- **graphrag**: 10 węzłów, wszystkie 10 pokryte body, confidence **wysoka**. Top: `00_severa_verified_synthesis_of_self_evolving_agent` (tier 1).
- **ask.py**: top-1 ten sam node — trafny.
- **Werdykt**: remis.

### Q2 — Trust tiers (in-corpus)
- **graphrag**: 10 węzłów, wszystkie pokryte, confidence **wysoka**. Top: `00_okf_methodology_research` — dokładnie oracle.
- **ask.py**: top-1 = `02_the_five_level_verification_ladder` — distractor (tabela evidence-confidence tiers, nie trust tiers labu); oracle `00_okf_methodology_research` dopiero na pozycji 3.
- **Werdykt**: graphrag wygrywa (top-1 exact vs distractor na top-1).

### Q3 — Kompresja sesji (in-corpus)
- **graphrag**: 4 węzły, 0 pokrytych → odmowa. Oracle `00_session_compaction_for_ai_agents` istnieje w grafie (FTS5 `compaction` → rank 1), ale polskie keywordy nie trafiają w angielskie body.
- **ask.py**: top-1 = `00_agentic_engineering_od_chaosu_do_wiadomego_proje` — nietrafny.
- **Przyczyna**: language mismatch — korpus EN, query PL.
- **Werdykt**: graphrag wygrywa (odmowa > false positive), ale oba zawodzą.

### Q4 — CRLF/SCARS (out-of-corpus)
- **graphrag**: 7 węzłów, 0 pokrytych (MIN_KEYWORD_MATCHES=2 filtruje `scars`-only trafienia) → poprawna odmowa.
- **ask.py**: top-1 = `reflection_rule_of_scars` — false positive (ogólna reguła scars, nie wpis CRLF).
- **Werdykt**: graphrag wygrywa.

### Q5 — Jan Kowalski (out-of-corpus)
- **graphrag**: 10 węzłów, 0 pokrytych → poprawna odmowa.
- **ask.py**: top-1 = `794_paradigms_of_artificial_intelligence_programming` — false positive (Robert Kowalski w bibliografii, nie Jan Kowalski z workspace).
- **Werdykt**: graphrag wygrywa.

## Werdykt ogólny

| Kryterium | graphrag.py | ask.py |
|-----------|-------------|--------|
| In-corpus trafne (Q1-Q2) | 2/2 | 1/2 (Q2 top-1 to distractor) |
| In-corpus Q3 | odmowa (language mismatch) | false positive |
| Out-of-corpus refusal (Q4-Q5) | 2/2 poprawne | 0/2 (oba false positive) |
| Halucynacje (claims bez pokrycia) | 0 | 0 (ale 2 false positives w refusal) |

**graphrag.py wygrywa na 4/5 pytaniach** (Q2, Q3, Q4, Q5), remis na 1 (Q1).

### Mocne strony graphrag
- Mechanizm odmowy (`MIN_KEYWORD_MATCHES=2` + body coverage) skutecznie blokuje false positives na out-of-corpus.
- Zero halucynacji — każde twierdzenie musi mieć cytat z nodes.body.
- Confidence jest liczbowe (liczba pokrytych węzłów), nie "pewność modelu".

### Słabe strony graphrag
- **Language mismatch**: polskie query terms nie trafiają w angielski korpus (Q3).
- 5 pytań to za mało do wniosków statystycznych.

## Baseline rankingowy Fazy 7 (Faza 8, Krok 1.5)

Data: 2026-10-11. Metryki: `mrr_at_k` / `recall_at_k` / `ndcg_at_k`
(`graphrag.py`, sekcja metryki rankingowe). Oracle IDs: `questions.md`
(sekcja Oracle IDs). Ranking = kolejnosc `retrieve()` (FTS5, top-10).
Metoda: `eval/_tmp_baseline8.py` (read-only, bez zapisu proofow).

| # | Pytanie | Oracle w top-5 | MRR@5 | Recall@5 | NDCG@5 | Odmowa |
|---|---------|----------------|-------|----------|--------|--------|
| Q1 | SEVerA | top-1 exact | 1.000 | 1.000 | 1.000 | NIE (odp.) |
| Q2 | Trust tiers | top-1 exact | 1.000 | 1.000 | 1.000 | NIE (odp.) |
| Q3 | Kompresja sesji | brak (0/4) | 0.000 | 0.000 | 0.000 | TAK (odmowa) |
| Q4 | CRLF/SCARS | n/d (out-of-corpus) | n/d | n/d | n/d | TAK (poprawna) |
| Q5 | Jan Kowalski | n/d (out-of-corpus) | n/d | n/d | n/d | TAK (poprawna) |

- **Baseline in-corpus (Q1-Q3): MRR@5 = 0.667, Recall@5 = 0.667.**
- **Baseline refusal (Q4-Q5): 2/2.**
- **Co to mowi:** Q1 i Q2 to perfekcyjne top-1 (MRR 1.0), caly dlug
  to Q3 = 0 (language mismatch PL query → EN korpus). Nie ma problemu
  rankingu w obrebie jezyka (Q2 top-1 exact mimo distractora w `ask.py`);
  jest problem pokrycia miedzy jezykami (Q3 oracle istnieje, retriever
  go nie widzi). Poprawa Fazy 8 musi ruszyc Q3 bez regresji Q4/Q5.
- **Korekta oracle Q3 (Faza 8):** raport o kompresji to 2 czesci —
  `00_*` (part 1/2) + `01_*` (part 2/2, + `_research` duplikaty).
  Baseline FTS nie znajduje zadnej z 4 (0/4); liczby MRR/Recall bez zmian.

## Hybryda Fazy 8: FTS5 + multilingual MiniLM, fuzja RRF (Krok 4)

Data: 2026-10-11. Model: `paraphrase-multilingual-MiniLM-L12-v2`
(dim 384, wagi w lokalnym HF cache). Indeks: `fixtures/graph_vec.db`
(kopia graph.db + `nodes.embedding`, 10373/10373, L2-norm).
Metoda: `eval/hybrid_eval.py` (baseline flaga OFF vs hybryda flaga ON,
`rrf_fuse(k=60)`, top-10 → top-5). Oracle Q3 = 4 ids (part 1/2 + 2/2).

| # | Pytanie | Baseline MRR@5 / Recall@5 | Hybryda MRR@5 / Recall@5 / NDCG@5 | Odmowa (hybryda) |
|---|---------|---------------------------|-----------------------------------|------------------|
| Q1 | SEVerA | 1.000 / 1.000 | 1.000 / 1.000 / 1.000 | NIE (odp.) |
| Q2 | Trust tiers | 1.000 / 1.000 | 1.000 / 1.000 / 1.000 | NIE (odp.) |
| Q3 | Kompresja sesji | 0.000 / 0.000 | 0.500 / 0.500 / 0.414 (pierwsze trafienie poz. 2) | TAK (odmowa — patrz nizej) |
| Q4 | CRLF/SCARS | n/d | n/d | TAK (poprawna, bez regresji) |
| Q5 | Jan Kowalski | n/d | n/d | TAK (poprawna, bez regresji) |

- **Delta in-corpus (Q1-Q3): MRR@5 = +0.167 (0.667 → 0.833), Recall@5 = +0.167.**
- **Refusal (Q4-Q5): 2/2 — bez regresji.**
- **Co to mowi:** wektory znajduja wlasciwy raport (part 2/2 na
  poz. 1-2 rankingu wektorowego, cosine 0.535), RRF dowozi go na
  poz. 2-4 fuzji. Diagnostyka `_tmp_vecdebug` (usuniety po uzyciu):
  vec-top2 = `01_session_compaction_*`, FTS-top4 = 0 oracles,
  fused-top10 = oracles na 2 i 4.
- **Znany mur (ranking-fix != answer-fix):** Q3 end-to-end dalej
  ODMOWA mimo MRR 0.5 — `oblicz_pokrycie` liczy polskie keywordy
  w angielskim body (`MIN_KEYWORD_MATCHES=2`), wiec synteza nie widzi
  pokrycia. Decyzja o pokryciu semantycznym = Krok 5 (poza tym wpisem).

## Czego ta ewaluacja NIE odróżnia

1. **Skala statystyczna**: n=5 nie daje mocy statystycznej. Potrzeba ≥50 pytań z rozkładem domeny.
2. **Jakość syntezy**: mierzymy tylko binary coverage, nie spójność/pełnię/strukturę odpowiedzi.
3. **Ranking FTS5**: Faza 7 nie mierzyla NDCG/MRR — Faza 8 mierzy
   (baseline MRR@5=0.667 + hybryda RRF +0.167 na Q3, refusal bez regresji).
   Wlasciwy wezel na pozycji 7 nadal mozliwy przy innych pytaniach.
4. **Cross-lingual retrieval**: to nie jest celowy test, choć jest to rzeczywisty failure mode (PL query → EN corpus).
5. **LLM w planie/syntezie**: MVP jest deterministyczne. Wariant z LLM (Faza 7b) może się zachowywać inaczej.
6. **Latencja**: nie mierzono czasu odpowiedzi.
7. **Edge proveniencia vs. czysty FTS**: Q1 używa `edge_proveniencia`, ale nie testujemy ich osobno.

## Notatki techniczne

- **Bug naprawiony w trakcie ewaluacji**: `f-string` concatenation bug w `syntezuj_odpowiedz` (ex linia 276-277) — `{pytanie}` pojawiało się dosłownie w answer.md odmowy. Naprawiono przez scalenie w jeden f-string; proofy Q3-Q5 wygenerowano ponownie.
- **Temp files usunięte**: `_debug_fts.py`, `_debug_fts2.py`, `_patch_cover.py`, `_tmp_query.py`.
- **Artefakty selftestu vs dowody 5Q**: `proof/graphrag/jaki-wpis-...-crlf` (bez sufiksu) to artefakt Q-refusal `selftestu`, odtwarzany przy każdym `selftest`; krótki slug `czym-jest-severa` (spoza zestawu 5Q) usunięty. Dowody ewaluacji to slugi z pełnymi pytaniami z `questions.md`.

## Krok 5 Fazy 8 — Diagnoza krytyczna i pomiar rozkładu cosine

Data: 2026-10-11. Rzetelny pomiar rozkładu cosine oraz test 4-way w `hybrid_eval.py` wykazały następujące fakty:
1. **Delta semantic ON vs OFF = +0.000** we wszystkich 4 konfiguracjach (Baseline/Hybryda x OFF/ON).
2. **Rzeczywiste cosines oracles Q3**: 0.48–0.54, oracles Q2: 0.54–0.56 — oba poniżej sztywnego progu `0.60`.
3. **Bramka semantyczna z progiem 0.60 jest funkcjonalnie martwa** (nie mogła uratować Q3). Q3 działa wyłącznie dzięki `PL_TO_EN_MAP` (exact-match).
4. **Decyzja dla Właściciela** (trzy warianty):
   - **Wariant 1**: Obniżyć próg cosine (np. do 0.45), pod warunkiem zachowania refusal 2/2 na OOC.
   - **Wariant 2**: Zrezygnować z bramki semantycznej (usunąć kod z `graphrag.py` i `hybrid_eval.py`), zostawiając `PL_TO_EN_MAP`.
   - **Wariant 3**: Zostawić kod jako feature flag domyślnie OFF (koszt zerowy, brak ryzyka).

## Trust Set Evaluation (2026-10-11 — 58 questions)

Data: 2026-10-11. Pełny test set: 33 in-corpus + 15 out-of-corpus + 10 boundary.
Wdrożony Wariant 1 (obniżenie progu cosine `prog_cosine = 0.45`).

- **IN-CORPUS (n=33)**: MRR@5 = 0.207, Recall@5 = 0.242, False Refusal = 0.0%
- **OUT-OF-CORPUS (n=15)**: Refusal = 100.0% (15/15)
- **BOUNDARY (n=10)**: Refusal = 50.0%
- **Decyzja OWNER**: Wariant 1 (obniżenie progu cosine do 0.45). Pilot zamrożony.
