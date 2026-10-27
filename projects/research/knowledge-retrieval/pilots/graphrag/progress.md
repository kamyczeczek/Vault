---
type: Concept
title: progress
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Progress — pilot graphrag

Dziennik wykonania (update po każdej akcji). Najnowsze na górze.

## 2026-10-11: Faza 8 Krok 2-3 — wagi multilingual, sygnal cross-lingual, RRF z flaga

1. Wagi `paraphrase-multilingual-MiniLM-L12-v2` sciagniete do lokalnego HF cache (snapshot e8f8c21, 494MB, tylko model.safetensors+config; decyzja uzytkownika: opcja A).
2. Sygnal cross-lingual zweryfikowany przed indeksem: cosine(Q3-PL, oracle-compaction)=0.56 vs distraktory 0.15-0.30 (mean-pooling, L2-norm, transformers+torch, bez sentence-transformers).
3. Indeks w tle: `fixtures/build_vector_index.py` (kopia graph.db -> fixtures/graph_vec.db, kolumna nodes.embedding BLOB float32 dim 384 + vec_meta; batch 64, maxlen 256). Oryginal w _archive nietkniety; `fixtures/.gitignore` kryje *.db.
4. RRF w `graphrag.py`: `rrf_fuse(k=60)` + `wyszukaj_hybrydowo()` + `Plan.uzyj_wektorow=False` (default OFF = baseline Fazy 7 nietkniety); fallback do czystego FTS przy braku indeksu. Sasiedzi wyekstrahowani do `_rozszerz_o_sasiadow()` (bez zmiany logiki).
5. Test `_tmp_rrftest` PASS: RRF syntetyk (fuzja 2 sciezek, single, empty) + regresja Q1 MRR@5=1.0 przy fladze OFF. `vec_index.py`: lazy loader + `wyszukaj_wektorowo()` + `indeks_gotowy()`. `eval/hybrid_eval.py` gotowy na INDEX_DONE.
6. Znane ograniczenie (next): `oblicz_pokrycie` liczy keywordy PL w body EN — sama hybryda ruszy MRR Q3, ale odpowiedz end-to-end dalej odmowi bez poprawki pokrycia. Decyzja po zmierzeniu delty rankingu.
7. NEXT: po INDEX_DONE -> `hybrid_eval.py` (baseline vs hybryda) -> delta MRR/Recall + refusal Q4/Q5 -> wpis w results.md -> commit w KR.

## 2026-10-11: Faza 8 Krok 4 — hybryda dowozi Q3 (MRR +0.167, refusal 2/2)

1. INDEX_DONE: `fixtures/graph_vec.db` — 10373/10373 embeddingow, dim 384, bloby 1536B, oracle Q3 norm 1.0000 (kontrola `_tmp_indexcheck`, PASS, tmp usuniety).
2. Diagnostyka `_tmp_vecdebug`: vec-top1/2 = `01_session_compaction_*` (0.5351) — wlasciwy raport, ale part 2/2 spoza wczesniejszego oracle (tylko `00_*`). FTS-top4 = 0 oracles. Fused: oracles na poz. 2 i 4.
3. Korekta oracle Q3: 2 -> 4 ids (part 1/2 + part 2/2 + `_research` duplikaty) w `questions.md` + `ranking_eval.py` + `hybrid_eval.py`. Baseline bez zmian (FTS 0/4, MRR@5=0.667).
4. `hybrid_eval.py` (flaga OFF vs ON): Q1 1.0/1.0, Q2 1.0/1.0, Q3 0.0 -> MRR@5=0.500/Recall@5=0.500/NDCG@5=0.414 (pierwsze trafienie poz. 2). Delta in-corpus +0.167/+0.167; refusal Q4/Q5 2/2 bez regresji.
5. Mur potwierdzony: Q3 end-to-end dalej ODMOWA (coverage liczy PL-keywordy w EN-body) — ranking-fix != answer-fix. Wpis w results.md (sekcja Hybryda Fazy 8). NEXT: decyzja o Kroku 5 (pokrycie semantyczne) + commit w KR.

## 2026-10-11: Faza 7 — MVP graphrag.py + ewaluacja na 5 pytaniach (Krok 4.3)

1. `graphrag.py` MVP (deterministyczny: FTS5 seed → body coverage → synteza z cytatami / odmowa): selftest PASS (Q-ground + Q-refusal).
2. Bug-fix w trakcie: f-string concat w `syntezuj_odpowiedz` wypisywał literal `{pytanie}` w answer.md odmowy; scalono w jeden f-string, proofy Q3-Q5 regenerowane.
3. Ewaluacja 5Q vs baseline `ask.py` (czysty FTS5): graphrag wygrywa 4/5 (Q2, Q3, Q4, Q5), remis Q1; 0 halucynacji; refusal 2/2 na out-of-corpus (ask.py 0/2 — oba false positive).
4. Q2 potwierdza tezę z Fazy 6 (warstwa dowodowa NAD rankingiem): ask.py top-1 to distractor, oracle dopiero poz. 3; graphrag top-1 exact. Q3 to language mismatch (PL query → EN korpus) — oba zawodzą, graphrag odmawia zamiast false positive.
5. Dowody: `eval/questions.md` (pytania+oracles+metryki) + `eval/results.md` (tabela, werdykt, czego NIE odróżnia) + `proof/graphrag/<slug>/` (5 dowodów 5Q + artefakt Q-refusal selftestu).

## 2026-10-10: Review #4 rozliczone mechanicznie (agent pi)

1. Teza strukturalna zweryfikowana z historii git (nie z opisu): answer-qground
   2 commity (wynik, potem dopisek), control-protocol 2 commity (zapis, potem
   łatki), D-005 3 commity (wariant B, przepisanie, naprawa rozjazdu) — 3x
   artefakt → review znajduje pytanie → dopisek. Wzorzec potwierdzony.
2. Poprawka mechaniczna (jak `not checked:`): CONTRACT.md „Kryterium
   mechaniczne" + „Porażka (v2)" wymagają odtąd sekcji „Czego ten dowód NIE
   odróżnia" (≥1 wpis) w każdym answer.md — pytanie PRZED wynikiem, nie po.
3. Proliferacja flag (7 z jednego wątku) + `--amend` w close.py: NIE
   implementuję — decyzja właściciela (close-ritual-coupled, owner mateusz);
   odnotowane jako propozycja we fladze zamknięcia, nie jako kod.

## 2026-10-10: Faza 6 Q-ground EXECUTED (agent pi, ludzkie oracle z review)

1. Człowiek wkleił w sesji review abstrakt arXiv:2603.25111v2 (spoza grafu);
   wpisany do CONTRACT.md (kondensacja 4-blokowa) + plan.json PRZED query.
2. Żywy eksperyment (read-only): ask.py top-1 EXACT
   (00_severa_verified_synthesis_of_self_evolving_agent, source URL = arXiv ID
   z oracle); body 2 158, tier 1, autorzy = oracle.
3. Zgodność claim-by-claim: 4/4 MATCH z cytatami body (ryzyko / FGGM /
   three-stage / zero-violations+tasks). 1 jawna różnica: oracle ma 'constrained
   symbolic regression', kondensat korpusu tylko 'symbolic math synthesis' —
   kondensat, nie sprzeczność. Pokrycie krawędziowe 0 (tylko SEQUENCE+PART_OF).
4. Kontrola bez narzędzia NIEWYKONALNA w tej sesji (skażona z definicji —
   sesja widziała węzeł wcześniej); musi biec pierwsza w świeżej sesji.
   Pełne 'grounding udowodniony' czeka na nią.
5. Dowód: proof/falsifier-v2/{trace-qground.md,answer-qground.md}.

## 2026-10-10: Faza 6 Q-refusal EXECUTED (agent pi, protokół close-ritual-probed)

1. Oracle-first: oczekiwania w `proof/falsifier-v2/plan.json` PRZED pierwszym query
   (Q-refusal → odmowa; kontrola pozytywna VERA Q1 → seed 00_okf_methodology_research
   w top; Q-ground + kontrola bez narzędzia = DEFERRED na ludzkie oczekiwanie).
2. Żywy eksperyment na archiwum (read-only): `ask.py` Q-refusal top-1 =
   `reflection_rule_of_scars`, ale body (10 347 znaków) ma 0 trafień
   R13/CRLF/SCARS.md/Where to go/AGENTS.md/sesja 04 → top-1 FTS to literatura
   (Liu 2026), nie odpowiedź. Warstwa węzłów: resolve(R13/CRLF) = 0, FTS
   'SCARS.md' = 0 dokumentów. Odpowiedź: ODMOWA z 5 dowodami braku pokrycia.
3. Oba tryby porażki: kontrola pozytywna (seed Q1 w top-3) dowodzi, że pustka
   to brak odpowiedzi, nie martwy retriever — bez niej 'odmowa' nieodróżnialna
   od 'narzędzie nie znajduje'. Surowy FTS stawia adjacent-but-wrong na top-1
   w obu pytaniach (Q1: distractor z QUESTIONS.md; Q-refusal: literatura o scars).
4. Finding: `research-engine/kg.py` martwy (FileNotFoundError — ścieżka
   `projects/research/agentic-research-lab/...` nie istnieje; żywe archiwum
   w `projects/_archive/`). Nie naprawiam: obcy projekt, jedna sesja = jeden projekt.
5. Dowód: `proof/falsifier-v2/{plan.json,trace.md,answer.md}` + sonda
   `probe_graph.py` (wszystko w proof/ = gitignored, nic w historii).
   Q-ground: węzeł SEVerA ISTNIEJE (arXiv:2603.25111v2) — synteza czeka na
   ludzkie oczekiwanie; pytanie do człowieka niedostępne (ask_user_question
   zwrócił błąd), więc jawnie zablokowane, nie przemilczane.

## 2026-10-10: scaffolding pilota (trasa A)

1. Odzyskano spec z sesji 05: export `goose 20261008_3` →
   root `scripts/_scratch/graphrag_session.md` (812 linii; + helper
   `find_graphrag_session.py`, oba derived/gitignored).
2. Rekonesans worktree: schemat graph.db (10 373/13 457), gatunki krawędzi,
   `kg.py` jako precedens, blizna R13, zepsuty loader skilli — wszystko
   w `findings.md`.
3. Decyzja użytkownika: trasa A (pilot w KR). Poprzedni szkic trasy B
   odrzucony przed budową.
4. Utworzono `pilots/graphrag/CONTRACT.md` (kontrakt pilota, trasa A,
   D-001..D-005 otwarte, kod po D-002/D-003).
5. Utworzono `task_plan.md` (fazy 1–4 complete z transcriptu, 5–6 pending),
   `findings.md`, `progress.md` (ten plik).
6. Utworzono `.wayfinder/MAP.md` + bilety D-000 (resolved, trasa A) ..
   D-005 (open). Forma z precedensu ARL `.wayfinder/MAP.md`.
7. Wpis w KR `CONTEXT.md ## Open work`: pilot Fazy 2, kandydat pivotu.
8. NEXT: bramy (MAP --check, diff --check, integrity), potem flaga
   `graphrag-pilot-scaffolded` + rebuild HANDOFF/STATE.

## 2026-10-10: D-002 = mini-graf (decyzja użytkownika "mini-graf")

1. `fixtures/build_mini_graph.py` + `fixtures/.gitignore` (*.db) →
   `mini_graph: PASS` (3 nodes, 2 edges, triple ze speca sesji 05).
2. D-002 RESOLVED (mini-graf na Fazę 5, archiwum opcją na Fazę 6);
   D-001/D-003 zawężone (relacje ze speca + stub LIKE wystarczą);
   MAP Decisions so far + task_plan (Faza 5 in_progress) + findings.
3. NEXT: 8 narzędzi na mini-grafie, potem dowód Fazy 5.

## 2026-10-10: Phase 5 proof complete (oracle-first)

1. `graphrag.py` selftest PASS — oracle-first: odpowiedź "Jan Kowalski",
   2 evidence triples, 6 trace entries (8 tools touched), refusal OK.
2. Proof artifacts: `proof/produkt-x/plan.json`, `trace.md`, `answer.md`.
3. D-004 RESOLVED (Phase 5 schema/confidence), D-005 DECISION: NIE PROMUJ.
4. Faza 5 DONE. **Korekta: archiwum nie "genre mismatch" — to scope shift.
   Faza 6 na archiwum = pytania o proweniencję (sesje/decyzje/SCARRED_FROM/
   DERIVED_FROM/SEQUENCE), seed FTS5, refusal = brak pokrycia twierdzeń.
   To realny dowód groundingu na prywatnej historii, której model nie zna.**

## 2026-10-10: D-002 = mini-graf (decyzja użytkownika "mini-graf")

1. `fixtures/build_mini_graph.py` + `fixtures/.gitignore` (*.db) →
   `mini_graph: PASS` (3 nodes, 2 edges, triple ze speca sesji 05).
2. D-002 RESOLVED (mini-graf na Fazę 5); archiwum = graf proweniencji.
3. D-001/D-003 RESOLVED jako scope shift (proweniencja, nie domena).
4. MAP Decisions so far + task_plan + findings + progress zaktualizowane.

## 2026-10-08 (sesja 05, stan końcowy)

- Szkic planu w transcriptcie (fazy 1–6, 5/6 pending), `task_plan.md`
  nigdy nie powstał na dysku (`Test-Path task_plan.md` → False).
- 2 błędy "model high demand" przerwały sesję; użytkownik zamknął ją ".".
- Brak projektu, brak mapy, brak kodu — cały plan dormant do 2026-10-10.
