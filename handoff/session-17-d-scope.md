---
type: Concept
title: session-17-d-scope
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Session 17 — D scope plan (retrieval improvements) — E = Tak, 2026-10-18

> **To jest plan; wykonanie = osobne sesje research. Nie uruchamiać w sesji 17.**
> Referencja: `b0e3c43` (Opcja D — świadome zamknięcie) zostaje w historii; E = Tak to nowa decyzja właściciela (sesja 17), nie reinterpretacja zamknięcia.

## Kontekst

- Decyzja E: `E = Tak` (właściciel, 2026-10-18) — reopen projektu `the-pragmatic-programmer-retrieval` dla D.
- Zapis decyzji: `handoff/session-13-owner-decision.md` (root), commit `692a121`.
- Post-closure backlog w `CONTEXT.md` projektu (sekcja `Post-closure backlog`) — stan: Odblokowane.

## Workstream 1 — Chunk-level sufficiency diagnoza (~4 h)

- **Pytanie badawcze:** Jaki odsetek top-8 chunków w trudnych pytaniach (q010, q012, i pokrewne z §"Luka any-vs-primary 2/52" w CONTEXT.md) jest niepełny semantycznie (brakuje kontekstu potrzebnego do odpowiedzi mimo obecności gold topicu)?
- **Metryka:** proxy — odsetek top-8 chunków, które po klasyfikacji (prose/related-sections/heading-only/code-listing) są `prose` i zawierają pełny passus odpowiedzi; walidacja ręczna na próbce n=10–15.
- **Próg wstępny (do zatwierdzenia przed runem — S56):** diagnoza jest użyteczna, jeśli ≥20% top-8 chunków w trudnych pytaniach jest niepełnych; poniżej → hipoteza "chunk-level sufficiency" odpada, D zamykamy ponownie.
- **Koszt:** ~4 h (klasyfikacja + walidacja ręczna + raport).
- **Zależności:** `data/chunks_classified.json` (sesja 5), `handoff/session-6/dumps/dump.json` (top-8 EN Tier 3).
- **Ryzyko:** ręczna walidacja jest subiektywna → wymaga pre-rejestracji kryterium "pełny passus" przed runem.

## Workstream 2 — Contextual retrieval augmentacja (~2 h)

- **Pytanie badawcze:** Czy dodanie kontekstu dokumentu (np. tytuł rozdziału + Topic heading) do treści chunka przed embeddingiem poprawia Recall@8 na trudnych pytaniach bez psucia reszty?
- **Metryka:** Recall@8 any + primary (na EN gold secie, 52 answerable), MRR, latencja p50/p95.
- **Próg wstępny:** zysk ≥ +0.02 Recall@8 any przy p95 ≤ 2× baseline (≤ 260 ms) — inaczej odrzucić.
- **Koszt:** ~2 h (re-embedding + re-eval).
- **Zależności:** `scripts/build_hybrid.py`, `scripts/eval_en_vs_pl.py`, `db/rag.db` (kopia — nie nadpisywać produkcyjnej).
- **Ryzyko:** augmentacja może zwiększyć szum w BM25 (dłuższe chunki); wymaga A/B na obu ścieżkach.

**Aktualizacja (sesja 23, 2026-10-18):** WS2 OUT — przy always-EN (agent tłumaczy PL→EN) baseline EN = 0.981, brak realnej przestrzeni na +0.02 MRR. Workstream zachowany jako referencja, nie do wykonania. Decyzja: `handoff/session-23-plan-decisions.md` (A1 = Tak).

## Workstream 3 — Multi-topic comparison benchmarking (~2 h)

- **Pytanie badawcze:** Czy dla pytań porównawczych (comparison) metryka primary-topic Recall jest adekwatna, czy wymaga przedefiniowania (primary = zbiór topiców)?
- **Metryka:** porównanie trzech wariantów oceny na q010/q012 i innych comparison: (a) primary-topic (obecna), (b) any-topic, (c) "primary = zbiór topiców" (nowa).
- **Próg wstępny:** wariant (c) musi być spójny z ręcznym odczytem (sesja 5) na ≥ 80% comparison; inaczej wracamy do (b) lub retired (T13/S64).
- **Koszt:** ~2 h (definicja + re-eval + raport).
- **Zależności:** `eval/gold_set_extended_en.json`, ręczny odczyt z §"Luka any-vs-primary 2/52" (CONTEXT.md).
- **Ryzyko:** decyzja o metryce należy do właściciela — plan dostarcza dane, nie rozstrzyga.

## Workstream 3b — Retrieve per topic + RRF (ranking fix) (~2 h)

- **Pytanie badawcze:** Czy retrieve per topic (dla pytań comparison, np. q010/q012) + RRF poprawia MRR/Recall@8 bez psucia reszty?
- **Metryka:** MRR, Recall@8 any + primary, latencja p50/p95.
- **Próg wstępny:** zysk ≥ +0.02 MRR (lub +0.019 Recall@8) przy p95 ≤ 2× baseline (≤ 260 ms) — inaczej odrzucić.
- **Koszt:** ~2 h (implementacja + re-eval).
- **Zależności:** `scripts/recall_hybrid.py`, `scripts/eval_en_vs_pl.py`, `db/rag.db`.
- **Ryzyko:** latencja ×2 na comparison (dwa retrieve); wymaga A/B na obu ścieżkach.

**Aktualizacja (sesja 23, 2026-10-18):** WS3b dodane decyzją M1 = (c) oba. Pomysł #2 z `Po sesji 6...txt` (multi-topic retrieval) wchodzi do planu jako WS3b. Decyzja: `handoff/session-23-plan-decisions.md`.

## Kolejność wykonania (rekomendowana)

1. Workstream 1 (diagnoza) — ustala, czy problem jest realny; jeśli próg nie przejdzie, Workstream 3 wciąż ma sens (metryka niezależna), Workstream 2 staje się opcjonalny.
2. Workstream 3 (benchmarking metryki) — niezależny od 1/2, może iść równolegle.
3. Workstream 2 (contextual) — zależy od wyniku 1 (jeśli sufficiency OK, augmentacja ma mniejszy sens).

## Status

- **Plan:** gotowy (sesja 17).
- **Wykonanie:** NIE wykonane. Osobne sesje research, po zatwierdzeniu progów przez właściciela (S56).

## DEFERRED (sesja 23, 2026-10-18) — świadomie odłożone poza zakresem D

- **M4 — MiniLM reranker:** DEFERRED. Tier 4 (`bge-reranker-base`) wykluczony pomiarem (Zadanie 5, ~10 s/query); MiniLM to inna decyzja wymagająca pomiaru latencji + Recall@8.
- **M5 — RAPTOR/graph:** DEFERRED. `data/raptor_tree` istnieje, nie referencjonowany; `graph.db` nie istnieje. Potencjał niewykorzystany — do osobnej sesji diagnostycznej (~15 min odczytu).
- **M7 — HyDE:** DEFERRED. P3, dodaje LLM w pętli (~1–3 s/query), dyskwalifikuje w produkcji realtime.
- **M8 — query expansion / multi-query:** DEFERRED. P3, latencja ×N, koszt nieproporcjonalny do zysku przy 0.981.