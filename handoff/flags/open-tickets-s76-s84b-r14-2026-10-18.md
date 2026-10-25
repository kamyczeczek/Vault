---
type: Concept
flag: open-tickets-s76-s84b-r14-2026-10-18
since: 2026-10-18
owner: mateusz
agent: opencode
model: opencode/glm-5.3-flash-free
origin: session-close
title: open-tickets-s76-s84b-r14-2026-10-18
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`open-tickets-s76-s84b-r14-2026-10-18` — 2026-10-18: Zgodnie z rekomendacją ownera — łańcuch E4→close zamknięty na `8af7e77` (10 sesji od `01a14af`, każda naprawiała dług poprzedniej; stagnacja merytoryczna: diminishing returns). Nie zaczynam kolejnej sesji w tym łańcuchu. Otwarte trzy osobne tickety jako flagi (każdy mały, każdy realny; żaden nie blokuje dziś, każdy będzie blokował później):

- `ticket-s76-parse-scars-leak-2026-10-18` — `parse_scars` regex nie parsuje nagłówka `## S76 (candidate):`, bulle S76 → `id=1023/1024` jako śmieci w `brain.db`; R21 będzie czytał błędne wnioski z retrievalu. Fix: tolerancja `(candidate)` w `scripts/ingest_brain.py` + rebuild.
- `ticket-s84b-check-includes-git-rm-trap-2026-10-18` — `check_includes` wymaga `exists_on_disk or is_tracked`; `git rm` przy retire → `CLOSE_EXIT=1`. Decyzja ownera: fix `close.py` vs doc. W `not checked`: S86 (candidate) — wzorzec re-deriwowalnego claimu `_counter_artifact` (present-tense counter + jednostka + artefakt w tej samej klauzuli) dopisać do `handoff/CONTEXT.md` przy okazji najbliższej sesji close-pipeline.
- `ticket-r14-sessions-meta-shelf-freshness-2026-10-18` — `ingest_curated_shelf` sztucznie świeżuje R14 przez `sessions_meta.updated_at`; sprawdzić, czy shelf-only refresh powinien dotykać `sessions_meta` w ogóle (pomiar przed/po, nie inferencja).

Stan techniczny: wszystkie trzy flagi przeszły parse (`build_handoff.py` EXIT=0), `HANDOFF_CHECK=0`, `INTEGRITY=0`, `git diff --check` czysty. S78/S80/S81–S85 pozostają `candidate` zamierzenie — S77→S79→S85 to łańcuch korekt, nie dług; S84a naprawione w `8af7e77`.

Zgodnie z R14: dygresje jednej sesji; do decyzji właściciela przy każdym tickecie jest fix vs doc (S84b) i pomiar (R14).

not checked:
- Decyzja ownera per ticket (fix vs doc S84b; `sessions_meta` w ogóle czy nie, R14).
- Stary dług `S78 retire` decyzja właściciela — nadal domknięty.
