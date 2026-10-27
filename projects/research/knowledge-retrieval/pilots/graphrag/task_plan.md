---
type: Concept
title: task_plan
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Task Plan: GraphRAG Agent (pilot w knowledge-retrieval)

Goal: deterministyczna warstwa planowania zapytań do grafu (spec: sesja
`goose 20261008_3`) jako pilot Fazy 2 transferu ARL, z dowodem na 1 pytaniu.

Route: trasa A — pilot wewnątrz `knowledge-retrieval` (decyzja użytkownika
2026-10-10; domyka GraphRAG + `arl-transfer-pivot` jednym ruchem).

## Phases

- [x] Phase 1: Define System Identity and Mission
  - Status: complete (spec z sesji 05, linie 12–16: planner/orchestrator, nie executor)
  - Owner: sesja 05 (goose 20261008_3)
  - Evidence: `scripts/_scratch/graphrag_session.md` linie 11–16

- [x] Phase 2: Map Core Principles and Constraints
  - Status: complete (6 zasad: zero halucynacji, tylko dowody, zakaz Cypher/Gremlin, pełny ślad, język użytkownika, brak dowodów = brak odpowiedzi)
  - Owner: sesja 05
  - Evidence: transkrypt linie 17–28

- [x] Phase 3: Design Tool Interfaces (8 tools)
  - Status: complete (nazwy PL z sesji: wektorowe_wyszukiwanie_zapytania, pobierz_encje, przechodzenie_grafu, rozszerz_ontologie, polacz_z_baza_wiedzy, weryfikuj_twierdzenia, generuj_odpowiedz, sledz_wykonanie)
  - Owner: sesja 05
  - Evidence: transkrypt linie 30–41
  - Caveat: nazwy PL to placeholders ("Zastąp poniższe nazwy rzeczywistymi narzędziami"). Mapowanie na żywy schemat → D-001.

- [x] Phase 4: Structure the 7-Step Workflow
  - Status: complete (Krok 0 analiza → Krok 7 ślad i cytowania, z obsługą błędów i przykładem Produkt X → Firma Y → Jan Kowalski)
  - Owner: sesja 05
  - Evidence: transkrypt linie 42–146

- [x] Phase 5: Define JSON Plan/Answer Schemas
  - Status: complete — schema zamrożona w `proof/produkt-x/` (plan.json,
    trace.md, answer.md); selftest PASS (oracle-first: odpowiedź ze speca,
    2 trójki, 6 trace entries, refusal branch OK); confidence rule: >=2
    spójne trójki = wysoka
  - Owner: sesja 2026-10-10
  - Evidence: `proof/produkt-x/plan.json`, `trace.md`, `answer.md`

- [ ] Phase 6: Design Error Handling and Confidence Logic
  - Status: pending — reguła confidence (progi liczby/jakości dowodów) + 5 gałęzi błędów ze speca
  - Owner: unassigned
  - Evidence: `proof/<slug>/answer.md` z sekcją confidence + gałąź "brak dowodów"

## Decisions Made

- 2026-10-10: trasa A (pilot w KR, nie osobny projekt) — użytkownik; domyka GraphRAG + pivot ARL
- 2026-10-10: D-002 = mini-graf na Fazę 5 (użytkownik); archiwum = graf proweniencji (SEQUENCE/PART_OF/DERIVED_FROM/SCARRED_FROM/SHARES_TAG)
- 2026-10-10: D-001 RESOLVED: scope shift — archiwum nie ma relacji domenowych, ale ma proweniencję; pytania Fazy 6 o sesje/decyzje/proweniencję
- 2026-10-10: D-003 RESOLVED: FTS5 seed na archiwum + definicja refusal = brak pokrycia twierdzeń dowodami (retriever nigdy nie pusty)
- 2026-10-10: kod implementacyjny dopiero po D-002 i D-003 — CONTRACT.md; rusztowanie nie decyduje po cichu
- 2026-10-10: D-004 RESOLVED (Phase 5 scope) — schema/confidence zamrożone w `proof/produkt-x/`, selftest oracle-first PASS
- 2026-10-10: D-005 DECISION: NIE PROMUJ — dowód = format (Faza 5) + grounding na proweniencji (Faza 6); routing w KR CONTRACT; parametryzacja rodzajów krawędzi = przenośność

## Next Step

Pilot Faza 5 DONE: dowód kontraktu na mini-grafie (oracle-first PASS).
## Phase 6 Status (2026-10-10, v2 po naprawie skażenia v1)

- [x] Falsyfikator v1 SUPERSEDED (oracle-second: oczekiwanie skopiowane z query; węzeł z korpusu ARL, nie z sesji)
- [x] Falsyfikator v2 w CONTRACT.md: Q-ground treściowe o SEVerA (oczekiwanie DO UZUPEŁNIENIA przez człowieka PRZED query) + Q-refusal o R13/SCARS.md (oracle-first, oczekiwana odmowa) + konkret kontroli bez narzędzia
- [x] Stan terminalny v2 w CONTRACT.md
- [x] Lista krawędzi potwierdzona: DERIVED_FROM(42), PART_OF(3998), SCARRED_FROM(24), SEQUENCE(9247), SHARES_TAG(146)
- [x] Faza 6 Q-refusal EXECUTED (2026-10-10, agent pi): odmowa z 5 dowodami braku pokrycia (resolve 0 / FTS 0 / body 0 / korpus-literatura / kontrola pozytywna VERA Q1); dowód w proof/falsifier-v2/
- [x] Faza 6 Q-ground EXECUTED (2026-10-10, agent pi, ludzkie oracle arXiv:2603.25111v2): synteza z nodes.body MATCH 4/4 z cytatami (FGGM/three-stage/zero-violations/tasks); 1 jawna różnica (brak 'symbolic regression' w kondensacie); pokrycie krawędziowe 0; dowód w proof/falsifier-v2/trace-qground.md + answer-qground.md
- [x] Kontrola bez narzędzia (goły model gemini-3.5-flash-lite o SEVerA): 4× NIE (brak FGGM/three-stage/tau2-bench/cytatów), brak parafrazy oracle, odpowiedź ogólnikowa → grounding Q-ground UDOWODNIONY; dowód w proof/falsifier-v2/control-answer.md + control-result.md
- [x] **Audyt proceduralny (2026-10-10)**: niezależna ślepa re-ocena potwierdza 4× NIE + brak parafrazy; kontrola proceduralnie ważna po audycie logów sesji (model różny od autora Fazy 6, pusty system prompt, brak narzędzi, brak plików w kontekście).

## Next Step

Faza 6 DOMKNIĘTA: Q-ground MATCH 4/4, Q-refusal ODMOWA, kontrola bez narzędzia
4× NIE + brak parafrazy; niezależna ślepa re-ocena i audyt procesu potwierdzają
grounding Q-ground. Dowód w proof/falsifier-v2/control-answer.md +
control-result.md. Faza 5 i Faza 6 gotowe do promocji (Gate D) — decyzja
należy do właściciela.

## Phase 7 Status (2026-10-11)

- [x] MVP `graphrag.py` (deterministyczny retriever: FTS5 → body coverage → synteza/odmowa) + selftest PASS.
- [x] Ewaluacja na 5 pytaniach vs `ask.py`: `eval/questions.md` + `eval/results.md` + `proof/graphrag/` (Krok 4.3).
- [x] Werdykt: graphrag wygrywa 4/5, remis 1/5, 0 halucynacji. Decyzja o promocji (Gate D) należy do właściciela.

## Phase 8 Status (2026-10-11, w toku — opcja A: multilingual + RRF)

- [x] Krok 0-1: recon + metryki (`mrr/recall/ndcg_at_k`) + baseline rankingowy (MRR@5=0.667, Recall@5=0.667, refusal 2/2; caly dlug = Q3).
- [x] Krok 2 (w toku): wagi multilingual w HF cache; sygnal 0.56 vs 0.15-0.30; indeks `fixtures/graph_vec.db` buduje sie w tle (~10-20 min CPU).
- [x] Krok 3: `rrf_fuse` + `wyszukaj_hybrydowo` + flaga `uzyj_wektorow` (OFF); test syntetyk + regresja Q1 PASS.
- [x] Krok 4: `eval/hybrid_eval.py` — INDEX_DONE (10373/10373) -> korekta oracle Q3 do 4 ids (part 1/2+2/2) -> delta MRR@5 +0.167 (0.667 -> 0.833), Recall +0.167, refusal 2/2 bez regresji -> results.md (sekcja Hybryda Fazy 8).
- [ ] Krok 5 — DO POPRAWY: próg 0.60 nieseparowalny od rozkładu (oracles 0.48-0.55 < 0.60); oczekuje na decyzję właściciela (wariant 1/2/3)
