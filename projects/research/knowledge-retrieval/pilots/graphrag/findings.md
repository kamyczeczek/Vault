---
type: Concept
title: findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Findings — pilot graphrag

Log ustaleń badawczych (2-Action Rule: po każdych 2 operacjach odczytu
zapis tutaj). Najnowsze na górze.

## 2026-10-11: Faza 8 — sygnal cross-lingual istnieje, pokrycie jest nastepnym murem

- Cosine PL-oracle 0.56 vs 0.15-0.30 na 4 parach (Q3 vs 2 oracles + 2 distraktory): multilingual MiniLM mostuje PL->EN bez slownika. Decyzja o wadze (470MB) obroniona pomiarem, nie wiara.
- RRF z flaga OFF: ranking mozna poprawiac bez ruszania baseline (MRR 0.667) ani refusal 2/2. Fallback przy braku indeksu = brak twardej zaleznosci w graphrag.py (lazy import).
- Mur #2 za rankingiem: `MIN_KEYWORD_MATCHES=2` liczy polskie keywordy w angielskim body — hybryda dowiezie oracles do top-5 (MRR), ale synteza dalej odmowi (coverage 0). Ranking-fix != answer-fix; kolejnosc: najpierw delta rankingu, potem decyzja o pokryciu semantycznym.

## 2026-10-11: Faza 8 Krok 4 — delta zmierzona, mur potwierdzony pomiarem

- Wczesniejszy oracle Q3 byl za waski (tylko part 1/2 `00_*`); wektory znalazly part 2/2 (`01_*`, cosine 0.535, top-1/2 vec-only). Korekta do 4 ids to naprawa testu, nie naciaganie wyniku — part 2/2 jawnie odpowiada na pytanie (zasady D+, body_len 1991).
- Delta: MRR@5 +0.167 (0.667 -> 0.833), Recall@5 +0.167, refusal 2/2 bez regresji. Q1/Q2 nietkniete (1.0/1.0 obie sciezki).
- Mur #2 potwierdzony end-to-end: Q3 MRR 0.5 przy odmowie TRUE — retriever dowozi, synteza odmawia. Pokrycie semantyczne (Krok 5) to zmiana zachowania odmowy = decyzja wlasciciela, nie automatyczna kontynuacja.

## 2026-10-11: Faza 7 — warstwa dowodowa bije ranking, język gubi obie strony

- Q2 (trust tiers): surowy FTS stawia distractor na top-1 (`02_the_five_level_verification_ladder` — tabela evidence-confidence, nie trust tiers labu), oracle `00_okf_methodology_research` dopiero poz. 3. graphrag top-1 exact przez body coverage.
- Q3 (kompresja sesji): oracle `00_session_compaction_for_ai_agents` istnieje (FTS5 `compaction` → rank 1), ale polskie keywordy nie trafiają w angielskie body → odmowa mimo obecności odpowiedzi. Odmowa > false positive ask.py, ale to granica keyword-matchingu, nie wiedzy grafu. Cross-lingual to osobny problem retrievala.
- n=5: brak mocy statystycznej; sekcja „Czego NIE odróżnia" w results.md jawnie lista 7 luk (skala, NDCG/MRR, synteza, cross-lingual, LLM, latencja, edges vs FTS).

## 2026-10-10: Wzorzec „artefakt → review znajduje pytanie" potwierdzony 3x z historii git

- answer-qground.md, control-protocol.md, D-005.md: każdy ma ≥2 commity
  w sekwencji wynik-najpierw-dopowiedzenie-później. To nie lenistwo sesji —
  to brak mechanicznego wymogu w kontrakcie. `not checked:` rozwiązało to
  dla flag; nic nie rozwiązywało dla dowodów.
- Lekcja: negatywna przestrzeń musi być wymogiem KONTRAKTU (FAIL bez niej),
  nie cnotą autora. Wpisane do CONTRACT.md jako kryterium mechaniczne.
- Granica reguły: wymusza pytanie, nie gwarantuje dobrego pytania. Review
  nadal potrzebne — ale review czyta sekcję, zamiast jej szukać.

## 2026-10-10: Faza 6 Q-ground — MATCH 4/4, kontrola negatywna jako dług protokołowy

- Top-1 FTS to EXACT match (przeciwieństwo Q-refusal, gdzie top-1 był
  zastępcą): ten sam retriever, dwa tryby — zastępca przy braku odpowiedzi,
  trafienie przy jej obecności. Warstwa dowodowa rozstrzyga oba.
- Lekcja protokołowa: kontrola-without-tool musi biec PIERWSZA w świeżej sesji,
  przed jakimkolwiek query. Uruchomienie jej po zobaczeniu węzła to teatr.
  Następny protokół weryfikacji: kolejność kontroli jawnie w planie.
- Zero triple semantycznych przy pełnej zgodności treści: grounding treściowy
  (body+proweniencja) ≠ grounding grafowy (ścieżki). Kontrakt mierzy treść —
  uczciwie, ale nazwane: pilot na archiwum (D-005) będzie musiał zdecydować,
  czy wymaga ścieżek.

## 2026-10-10: Faza 6 Q-refusal — odmowa stoi, dwa ustalenia poboczne

- Surowy FTS nie odróżnia adjacent od odpowiedzi: top-1 Q-refusal to dokument
  o 'Rule of Scars' jako temacie literackim (0 treści o R13), top-1 Q1 VERA to
  distractor z QUESTIONS.md. Warstwa dowodowa (resolve + body + FTS-direct +
  charakter korpusu + kontrola pozytywna) musi stać NAD rankingiem, nie za nim.
- `kg.py` (research-engine) martwy: FileNotFoundError na nieistniejącej ścieżce.
  Precedens 'istnieje kg.py' (findings:14,61) fałszywy co do używalności —
  finding zapisany, naprawa należy do sesji research-engine, nie tej.
- Korpus: top sources = podręczniki (R&N 1123, Norvig Lisp 828, Bishop 736);
  rodziny workspace/session w source_family to temat badawczy, nie fakty o tym
  workspace. Podstawa odmowy Q-refusal potwierdzona na 5 niezależnych warstwach.

## 2026-10-10: Scope shift — archiwum to graf proweniencji, nie bezużyteczny

Kluczowy fakt (korekta po pierwszej wersji):
- Spec sesji 05: relacje domenowe `STWORZYŁ`, `ZARZĄDZA` (encje: produkt, firma, osoba).
- Żywy `graph.db` (archiwum ARL): relacje proweniencji `SEQUENCE` 9247, `PART_OF` 3998,
  `SHARES_TAG` 146, `DERIVED_FROM` 42, `SCARRED_FROM` 24 (encje: dokumenty, sesje, decyzje).
- To nie "genre mismatch" w sensie "archiwum bezużyteczne". To rozbieżność celowania.
- Archiwum ma właściwości, których mini-graf nie ma: model nie zna treści,
  skala 10k wymusza retrieval, realny zaszumiony korpus, istnieje `kg.py`.

Nowe pytania Fazy 6 (proweniencja):
- „Które sesje dotyczyły NotebookLM?" — treści + `SHARES_TAG`
- „Z czego wynika decyzja D-002?" — `DERIVED_FROM`
- „Jaki był związek sesji 04 z `SCARS.md`?" — `SCARRED_FROM`
- „Co poprzedzało wpis R13?" — `SEQUENCE`

Na te pytania graf **ma** odpowiedź, a model **nie ma**. To jest dowód groundingu.

Konsekwencje Fazy 6:
- Seed = FTS5/BM25 (retriever nigdy nie pusty)
- Refusal = brak pokrycia twierdzeń dowodami (nie puste wyniki retrievera)
- Parametryzacja narzędzi po `kind` = przenośność (nie hardcode archiwum)
- Zależność KR → archiwum ARL zadeklarowana (read-only na zamrożonym)

## 2026-10-10: Phase 5 proof complete (selftest oracle-first PASS)

- `graphrag.py` 8 tools + workflow Krok 0-7 zaimplementowany, selftest
  PASS (oracle-first: odpowiedź ze speca, 2 trójki, 6 trace entries,
  refusal branch OK).
- Proof artifacts: `proof/produkt-x/plan.json`, `trace.md`, `answer.md`.
- Schema planu/odpowiedzi zamrożona, confidence rule: >=2 spójne trójki
  = wysoka, 1 = srednia, 0 = niska (odmowa). Adversarial case: losowe
  trójki odrzucone przez `weryfikuj_twierdzenia`.
- D-004 RESOLVED (Phase 5 scope); D-005 DECISION: NIE PROMUJ.

## 2026-10-10: D-002 = mini-graf (decyzja użytkownika)

- `fixtures/build_mini_graph.py` → `fixtures/mini_graph.db`:
  `mini_graph: PASS` (3/3 nodes, 2/2 edges; triple dokładnie ze speca).
- Schemat zwierciadlany vs archiwum (kolumny `nodes`/`edges` 1:1, bez
  `node_tags`/`fts` — Faza 5 nie potrzebuje; seed to stub LIKE).
- `fixtures/.gitignore`: `*.db` (derived, nigdy hand-edit).

## 2026-10-10: rekonesans worktree przed scaffoldingiem

- Żywy schemat `graph.db` (archiwum ARL): tabele `nodes` (10 373 wiersze,
  11 kolumn: id/title/path/tags/headings/body/node_type/source_family/source/
  trust_tier/semantic_edges), `edges` (13 457, kolumny src/dst/kind/conf/tag),
  `node_tags` (80 718), FTS5 `fts` (10 373). Gatunki krawędzi: SEQUENCE 9247,
  PART_OF 3998, SHARES_TAG 146, DERIVED_FROM 42, SCARRED_FROM 24.
  Źródło: `scripts/_scratch/inspect_graph_schema.py` (derived, root gitignored).
- Spec z sesji 05 używa relacji `STWORZYŁ/ZARZĄDZA` (przykład biznesowy) —
  żywego odpowiednika brak; najbliższe to DERIVES_FROM/REFERS_TO. Stąd D-001.
- Graf nie ma embeddingów ani kolumny wektorowej — tylko FTS5/BM25. Stąd D-003
  (FTS jako seed vs stub wektorowy).
- `research-engine/kg.py` to istniejący query surface (resolve/expand/
  resolve_and_expand, read-only, deterministyczny) na tej samej bazie —
  precedens do linkowania, nie kopiowania (D-002, opcja read-only).
- Loader skilli DSH nie zna `wayfinder/icm-architect/grill-me-with-docs/
  planning-with-files` (ten sam błąd co w sesji 05, potwierdzony 2026-10-09).
  Obchodzenie: czytanie SKILL.md z dysku. MANIFEST.md póki co dekoracja.
- R13: wiersz w AGENTS.md = zmiana ≥3-plikowa (wiersz + regen audit block +
  nowa wersja raportu v8→v9, v8 do `_archive/reviews/`). Dlatego D-005 trzyma
  routing poza AGENTS.md do czasu dowodu.

## 2026-10-08 (z sesji 05, transkrypt linie 524–553)

- Precedens trackera lokalnego: ARL `.wayfinder/MAP.md` (destination +
  Notes + Decisions so far + Not yet specified + Out of scope) + `tickets/
  D-001..D-006.md`. Ten pilot kopiuje formę, nie treść.
- Integrity gate w sesji 05: `OK: workspace root holds 28 declared entries,
  5 projects, all routing links resolve` — punkt odniesienia dla bramy po
  scaffoldingzie.
