---
flag: session-digest-design-2026-10-22
since: 2026-10-22
owner: opencode
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: design discussion (grill-with-docs + icm-architect + wayfinder + unlazy)
---

`session-digest-design-2026-10-22` — 2026-10-22: digest sesji zaprojektowany
i zbudowany jako druga warstwa nad L2. **Status 2026-10-23: L0 unproven/closed —
nie jest warstwą analityczną; L1 zostaje selektorem. Wynik A/B:
`handoff/flags/session-digest-ab-2026-10-23.md`.** Rozdzielone fakt i osąd typem
(`mechanical_delta | judgment`), evidence tylko `substring_exists`, stabilny
klucz `agent:session_id`, coverage hash po `coverage_descriptor`.

- Mapa i decyzje: `docs/wayfinder-session-digest.md` (D1, T1–T6 closed, T7 built).
- ADR: `brain/decisions/ADR-005-session-digest-fact-judgment.md` (schema L1/L0,
  normalizer, markery, promocja, worked example 9-vs-10).
- Bramki: `docs/session-digest-GATES.md` G1–G12 — wszystkie `[x]` z evidence.
- Kod: `scripts/session_facts.py`, `scripts/session_digest.py`,
  `scripts/verify_session_digest.py`, `scripts/test_session_facts.py`,
  `scripts/test_session_classify.py`, `scripts/session_digest.bat`.

Pomiar 2026-10-22: 100 sesji głównych + 105 dzieci; L0 788 B; L1 99 277 B;
`SCHEMA_OK`, `QUOTES_OK`, `STABILITY_OK`, `DETERMINISM_OK`, `BUDGET_OK`,
negative controls quote/payload/coverage OK, `REFACTOR_SAFETY_OK`,
`HEADER_OK`, 12 testów ekstraktorów OK. `check_workspace_integrity.py` OK;
`git diff --check` czysty. Commit: design/docs, potem build kodu (dwie części).

`--classify` wbudowany 2026-10-22 jako rules-v1: cards-only, 0 model calls,
`judgment_status: candidate`, `promotion: null`; bramka G13. Wrapper:
`scripts\session_digest.bat N [--classify]`. Pomiar: 40 sesji → 6 kandydatów
(open_threads=4, contradictions=2), `JUDGMENT_OK`.

Review 2026-10-22 (`judgment-check/candidates/digest.judgment.md`): 0/6
kandydatów prawdziwych → **bez promocji**. 4 `open_threads` to obowiązkowa
linia `not checked:` z rytuału `close.py`, nie otwarty wątek (j-0004 ma nawet
commity 0b97dfb, bf0a2f9). 2 `contradictions` porównują sesję, która ma własne
commity (j-0001: 0d0a585, 1a5a19d, 4e3b2ed, bac575a), z sąsiednimi sesjami tej
samej flagi — brak rozjazdu. Przyczyna: `session_facts._marker_scan` bierze
ostatni marker z całego body (także `not checked:` cytowane w treści flagi),
a rules-v1 ma `not_checked` w `OPEN_MARKERS`. Następny krok: rules-v2 (marker
tylko z końcowego bloku, `not_checked` nie jest open) + re-run `--classify`;
promocja dopiero po kandydatach z niezależnym evidence i `review_ref`.

not checked: backend modelowy dla `--classify` (świadomie rules-v1);
`losses.dup` (jawnie w L0 `not_checked`);
stary `tool_calls.jsonl` bez `key` daje `tool_facts.status=missing` do następnego
runu merged. Memory index: ingest 2026-10-23 ponownie dodał wycofane wcześniej
meta-sesje i `retrieval_eval` spadł 15/15 → 13/15; A (workaround) zastosowane
ponownie na minimalnym zbiorze 4 sesji (`ses_ea98f264`, `ses_eb2c4e7e`,
`01a14d3f`, `01a14d44`) → 15/15. To osobny temat retrieval, nie digestu; trwały
fix B (lista `EXCLUDED_SESSION_IDS` w `memory_index.py`) jest w
`handoff/flags/memory-meta-session-exclusion-durable-2026-10-23.md`. Świeżość
trzyma curated shelf.
