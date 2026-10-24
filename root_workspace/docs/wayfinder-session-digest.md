# Wayfinder Map: Session digest (L0 / L1 / L2)

## Destination

**D1** — digest ≤15 KB, w którym zimny agent odpowiada na „co zmieniło się
w kierunku / co jest otwarte / gdzie sesje sobie przeczą”, a każde twierdzenie
ma klikalny dowód. Pełny audyt pozostaje w `session_ground_truth.md`.

Test sukcesu: 3 losowe pytania o kierunek; odpowiedź musi wskazać sesję
i cytat. „Nie wiem” jest poprawne tylko wtedy, gdy w korpusie nie ma dowodu
(i to też musi być zacytowane jako brak). Nie testujemy „czy plik wygląda dobrze”.

## Notes

- **Domena:** derived views of agent sessions; L2 (`03_records/sessions/` +
  `04_payloads/`) zostaje bez zmian.
- **Skille:** `wayfinder`, `grill-with-docs`, `unlazy`, `icm-architect`.
- **Zasada nadrzędna:** fakt i osąd są rozdzielone typem. `mechanical_delta`
  nie interpretuje; `judgment` powstaje dopiero po `--classify` i ma
  `evidence_check: substring_exists`, nie `verified`.
- **Build:** jeden task **T7**, bez równoległych sliców. Decyzje T1–T6 są
  zamknięte przed startem T7.

## Decisions so far

- [T1 — stabilny klucz i okno](../brain/decisions/ADR-005-session-digest-fact-judgment.md):
  `agent:session_id` jest tożsamością; `ses-NNN` to tylko wskaźnik runu;
  dzieci przez `parent_session_id`; nagłówek podaje osobno sesje główne/dzieci,
  dokładny zakres dat i semantykę N.
- [T2 — schema karty i puste pola](../brain/decisions/ADR-005-session-digest-fact-judgment.md):
  fakty = `[]`, cytaty = `{kind: none, reason: ...}`, `—` tylko w renderze MD;
  `ending` zastępuje `outcome`; słowniki `reason`, `status`, `marker` są zamknięte
  i wersjonowane.
- [T3 — jedno źródło ekstraktorów](../brain/decisions/ADR-005-session-digest-fact-judgment.md):
  czyste ekstraktory w `scripts/session_facts.py` używane przez merged i digest;
  fixture byte-identical przed/po refaktorze; cross-check sidecara ma jawny
  `fresh|stale|none|missing`, nigdy cichy fallback.
- [T4 — evidence gate i normalizer](../brain/decisions/ADR-005-session-digest-fact-judgment.md):
  `claims` — body; `proves` — body + payload pointer (`path`, `line`, `sha`);
  walidator sam liczy `line`/`sha`; odrzucone → `not_checked` z kodem;
  negative controls w CI.
- [T5 — cykl życia osądu i promocja](../brain/decisions/ADR-005-session-digest-fact-judgment.md):
  MVP emituje `judgment: []` / `judgment_status: not_run`; `--classify` czyta
  tylko karty i pisze kandydata; promocja to osobny commit z blokiem
  `promotion`, `review_ref` i wpisem w `docs/sessions/README.md`.
- [T6 — coverage hash, starzenie i diff](../brain/decisions/ADR-005-session-digest-fact-judgment.md):
  `source_cards_sha256` po kanonicznej serializacji `coverage_descriptor`;
  `validity_basis: coverage`; zmiana karty w coverage → twardy fail G10;
  nowa sesja poza coverage → `new_sessions_since`, tylko informacyjnie.

## Not yet specified

- ~~Dokładny kształt CLI `--classify` (prompt, model, retry, koszt)~~ —
  rozstrzygnięte 2026-10-22: deterministyczny backend `rules` v1, zero wywołań
  modelu (`model_calls: 0`), tylko karty, wynik do `candidates/`; backend
  modelowy może później pisać ten sam JSON bez zmiany schematu.
- Czy `docs/sessions/README.md` dostaje advisory w integrity od razu, czy
  dopiero po pierwszej promocji — T7 może to zostawić jako manual check.
- Format `review_ref` (commit vs PR vs review doc) — ustali pierwsza promocja.
- `--days` i `--count` są łączone: `--days` filtruje okno, potem `--count`
  bierze N najnowszych sesji głównych. `--until` zamraża okno dla testów.

## Out of scope

- Deduplikacja treści między sesjami (świadomie odrzucona: self-containedness).
- Streszczanie prozy asystenta bez cytatu — to failure mode, który digest ma
  wykrywać, nie powtarzać.
- Embeddingi, RAG, reranker i jakakolwiek semantyczna klasyfikacja poza
  jawnym `--classify`.
- Zmiany w L2 (`03_records/`, `04_payloads/`) i w `session_ground_truth.md`.
- Wpinanie digestu w closing ritual; `session-digest-stale` jest sygnałem,
  nie bramką każdej sesji.
- Trackowanie surowych cytatów i payloadów; tracked jest tylko promowany digest.

## Tickets

| ID | Typ | Pytanie | Status | Blokowane przez |
|---|---|---|---|---|
| T1 | decision | Jaki jest stabilny klucz sesji i jak liczymy N oraz dzieci? | closed | — |
| T2 | decision | Jaki jest schema L1, znaczenie pustych pól i budżet rozmiaru? | closed | — |
| T3 | decision | Skąd biorą się fakty bez duplikowania parserów? | closed | — |
| T4 | decision | Co dokładnie waliduje evidence i na jakim źródle? | closed | — |
| T5 | decision | Kiedy i jak powstaje osąd L0 oraz jak wygląda promocja? | closed | — |
| T6 | decision | Co hashuje `source_cards_sha256` i kiedy digest jest stale? | closed | — |
| T7 | task | Zbuduj `session_digest.py` + walidator + testy, przejdź G1–G12. | closed | — |

T7 zbudowany: `scripts/session_facts.py`, `scripts/session_digest.py`,
`scripts/verify_session_digest.py`, `scripts/test_session_facts.py`; G1–G12
mają evidence w `docs/session-digest-GATES.md`. Następny frontier: review
diff/commit, potem opcjonalny `--classify`; promocja pozostaje osobnym krokiem.
