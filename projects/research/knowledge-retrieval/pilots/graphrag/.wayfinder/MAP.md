# Wayfinder map — pilot graphrag (Faza 2 transferu ARL)

## Destination

Deterministyczna warstwa planowania zapytań do grafu (spec: sesja
`goose 20261008_3`), udowodniona na 1 pytaniu: plan JSON → trace → odpowiedź
z dowodami + confidence, 0 nieuzasadnionych twierdzeń. Mapa done = droga
wolna, nie produkt gotowy (wayfinder: plan, don't do).

## Notes

- Domain: `knowledge-retrieval` (jakość ścieżki odczytu); pilot Fazy 2 z
  flagi `arl-transfer-pivot`; trasa A (decyzja użytkownika 2026-10-10)
- Skills per ticket (z dysku — loader DSH zepsuty, defekt znany z sesji 05):
  `grilling` + `domain-modeling` przy wątpliwości; `icm-architect`
  przy kontraktach; `planning-with-files` zawsze (task_plan/findings/progress)
- Standing constraints: kod implementacyjny dopiero po D-002 i D-003;
  AGENTS.md bez nowego wiersza do czasu dowodu (R13); linkuj `kg.py`,
  nie kopiuj; archiwum ARL tylko read-only, nigdy edycja
- Ground truth dowodu: przykład z sesji 05 (Produkt X → Firma Y →
  Jan Kowalski) jako test oracle-first

## Decisions so far

- [Trasa A — pilot w knowledge-retrieval](tickets/D-000.md): osobny projekt
  odrzucony; KR jest kandydatem pivotu ARL, GraphRAG jego pierwszym pilotem
- [Backend: mini-graf na Fazę 5](tickets/D-002.md): `fixtures/mini_graph.db`
  (3 nodes, 2 edges, PASS); archiwum = graf proweniencji dokumentów/sesji
- [Relacje: scope shift — proweniencja, nie domena](tickets/D-001.md): archiwum
  ma SEQUENCE/PART_OF/DERIVED_FROM/SCARRED_FROM/SHARES_TAG; pytania Fazy 6
  o sesje/decyzje/proweniencję, nie o firmy
- [Seed: FTS5 na archiwum, refusal = brak pokrycia twierdzeń](tickets/D-003.md):
  retriever nigdy nie wraca pusty; definicja „brak dowodów" = odrzucone
  twierdzenia, nie puste wyniki
- [Schema + confidence: Phase 5 done](tickets/D-004.md): `plan.json`/
  `answer.md`/`trace.md` w `proof/produkt-x/`, selftest PASS, oracle-first
- [Routing / promocja: NIE PROMUJ](tickets/D-005.md): dowód = format (Faza 5)
  + grounding na proweniencji (Faza 6); routing w KR CONTRACT; parametryzacja
  rodzajów krawędzi = przenośność

## Not yet specified

- Metryka confidence: progi liczby/jakości dowodów (część D-004, czeka na D-001/D-002)
- Drugie pytanie dowodowe po pierwszym zielonym (eskalacja, nie zakres)

## Out of scope

- Budowa nowego silnika grafu / migracja poza FTS5
- Embeddings w Fazie 2 (flaga pivotu je zabiła; D-003 rozstrzyga seed bez nich)
- Naprawa loadera skilli DSH (defekt platformy, nie pilota)
- Wiersz w AGENTS.md przed dowodem (R13)
