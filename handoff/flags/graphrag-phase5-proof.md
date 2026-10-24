---
flag: graphrag-phase5-proof
since: 2026-10-10
owner: Mateusz
agent: opencode
model: muse-spark-1.3-contributor-free
origin: user "kontynuuj" 2026-10-10; spec: goose 20261008_3 (sesja 05)
---

`graphrag-phase5-proof` — 2026-10-10: Faza 5 pilota GraphRAG zakończona
z dowodem oracle-first. `graphrag.py` (8 narzędzi + workflow Krok 0-7,
ze speca sesji 05) na mini-grafie `fixtures/mini_graph.db` (D-002
RESOLVED: mini-graf na Fazę 5) przechodzi selftest:

- Pytanie: "Kto zarządza firmą, która stworzyła produkt X?"
- Odpowiedź: "Produkt X stworzył Firma Y, Firma Y zarządza Jan Kowalski."
- Dowody: 2 trójki (STWORZYŁ, ZARZĄDZA) — spójna ścieżka
- Ślad: 6 wpisów (seed stub, traversal, entity, resolve, verify, generate)
- Confidence: **wysoka** (>=2 spójne trójki)
- Refusal branch: nieznane pytanie -> odmowa z komunikatem specyfikacji

Proof artifacts w `proof/produkt-x/`: `plan.json`, `trace.md`, `answer.md`.

**Korekta: nie "genre mismatch" — to scope shift.** Archiwum ARL
(`graph.db`, 10 373 / 13 457) to **graf proweniencji dokumentów i sesji**
(relacje SEQUENCE, PART_OF, DERIVED_FROM, SCARRED_FROM, SHARES_TAG).
Ma właściwości, których mini-graf nie ma: model nie zna treści, skala
wymusza retrieval, realny zaszumiony korpus, `kg.py` query surface.

Faza 6 = pytania o proweniencję (sesje/decyzje), nie o firmy:
- „Z czego wynika D-002?" — `DERIVED_FROM`
- „Sesja 04 ↔ SCARS.md?" — `SCARRED_FROM`
- Seed = FTS5/BM25 (retriever nigdy nie pusty)
- Refusal = brak pokrycia twierdzeń dowodami (nie puste wyniki)
- Parametryzacja `kind` = przenośność; zależność KR → archiwum ARL read-only

D-001/D-003 RESOLVED jako scope shift. D-005 DECISION: **NIE PROMUJ**.
Dowód = format (Faza 5) + grounding na proweniencji (Faza 6).

Bramy: MAP zregenowana (5 modułów), `diff --check` czysty, KR preflight READY.
Root integrity FAIL na stanie zastanym (śmieci root + lag R14 + cudze zmiany KR).

Next: Faza 6 (warunek: zapytanie do graph.db — rozstrzygnij listę krawędzi,
zadeklaruj zależność KR→ARL, parametryzuj kind). Gate ARL: przenośny kontrakt
+ dowód groundingu na prywatnej historii.