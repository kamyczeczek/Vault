# Wayfinder Execution Map: wykonanie decyzji `task` z `wayfinder-brain-map.md`

## Destination

Zamienić każdą **rozstrzygniętą, ale niewykonaną** decyzję typu `task` z
`docs/wayfinder-brain-map.md` w **zielony pomiar** — dowód, że decyzja weszła w życie,
nie tylko w `## Decisions so far`. Realizuje dług S64/S65: „decyzja bez wykonawcy to
dług"; każda zamknięta jako *out of scope* jest tu nazwana i przypisana.

Dziś w zakresie: **E1–E5** (jawny handoff z 534dfa4: B2/B4/B5/B12/B13) oraz
**E6–E7** (wygraduowane przy rozstrzyganiu — B3/B7, patrz `## Tickets`).

## Notes

- **Domena:** ta sama co mapy decyzyjnej — warstwa `brain` (`scripts/brain.py`,
  `scripts/memory/`, `scripts/memory_index.py`, `scripts/ingest_brain.py`,
  `scripts/eval_brain.py`) i bezpośrednie mechanizmy (`scripts/close.py`,
  `handoff/flags/`).
- **Tryb: `execute-in-map` — jawny override wayfindera.** `skills/wayfinder/SKILL.md`:
  „An effort can override this in its Notes, carrying execution into the map itself,
  but absent that, produce decisions, not deliverables." **Ten effort to robi** —
  tickety są **deliverable**, nie decyzje. To jest właśnie ten override; bez niego
  `task`-tickety z mapy decyzyjnej są poza destination.
- **Skille do konsultacji:** `implement`, `unlazy`, `tdd`.
- **Źródło decyzji (nie kopiuj):** `docs/wayfinder-brain-map.md` `## Decisions so far`
  + `docs/wayfinder-brain-answers/`. Ten effort **wykonuje**, nie rozstrzyga.
- **Zasada nadrzędna:** bramka musi umieć failować (`SCARS.md` S56, S62). Każdy ticket
  ma **kryterium sukcesu** i **adversarial case zapisany przed runem**.
- **Jedna sesja = jeden ticket.** Tak jak w mapie decyzyjnej: claim przed pracą.
- **Kolumna `Status` (tickets):** `open` = niewykonany; `**done**` = deliverable
  wdrożony, jego adversarial case zielony (z datą i linkiem do answer file).

## Tickets

| ID | ← | Deliverable | Kryterium sukcesu | Adversarial case (przed runem) | Status |
|---|---|---|---|---|---|
| E1 | B2 | Jedna asercja driftu schematu per agent w `memory_index.py ingest`: najnowsza sesja w store X jest w indeksie; jeśli nie — FAIL z nazwami tabel. | `ingest` exit 1 (nazywa store + tabele) gdy najnowsza sesja store'a nie jest w indeksie; PASS na realnym korpusie. | (1) wstrzyknij nowszą sesję do store'a, re-ingest bez indeksowania → FAIL z store+tabele; (2) kontrola: czysty ingest → PASS; (3) store ze zmigrowanym schematem tak, że query najnowszej sesji zwraca nic (kształt `if not events: continue`, deepseek) → FAIL, nie cichy skip. | **done** (2026-10-16) — [answer](wayfinder-brain-answers/E1-schema-drift.md) |
| E2 | B4 | Wykonać decyzję PL↔EN: usunąć case z `brain_eval.json`, re-baseline, zapisać powód. | Case nieobecny; `eval_brain.py` zre-baselinowany (liczby hit/refusal zaktualizowane); powód (cross-lingual limit lexical K1) w commicie i tu. | (1) usunięcie zostawia wiszący anchor/licznik → `eval_brain.py --check` FAIL (trzeba zaktualizować baseline); (2) kontrola: czysty `--check` PASS; (3) usunięcie nie rusza hit/MRR innych case'ów (izolacja) — jeśli rusza, ukryte sprzężenie → FAIL loud. | open |
| E3 | B5 | Wykonać decyzję refuse-risotto: zamienić query na tokenowo rozłączne z korpusem, utrzymać 4 odmowy. | Nowe query tokenowo rozłączne; liczba odmów = 4; silnik nietknięty (brak progu = brak tuningu). | (1) query z przypadkowym tokenem korpusu → trafienie, nie odmowa → FAIL; (2) kontrola: pozostałe case'y bez zmian; (3) jeśli odmowy spadną < 4 → FAIL (metryka = liczba odmów). | open |
| E4 | B12 | `model: current`/`default` w flagach (#12): naprawić 13 linii + wymusić kontrakt. | Zero flag z `model: current|default`; bramka/`close` odrzuca nickname (wymaga `provider/model-id`). | (1) flaga z `model: current` → bramka FAIL, nazywa plik; (2) realny id `opencode/deepseek-v4.1-flash-free` → PASS; (3) nickname bez `/` → FAIL/WARN. | done |
| E5 | B13 | Historia per-pytanie eval (#17): `eval_brain.py` dopisuje `brain_eval_runs.jsonl` z `failed:[...]`. | Każdy run dopisuje jedną linię JSONL z wynikiem per-pytanie, w tym `failed:[...]`; zapis append-only. | (1) wymuszony błąd → linia wymienia id failing case'u w `failed`; (2) wszystko pass → `failed: []`; (3) dwa runy → dwie linie (brak nadpisania); (4) częściowa/zepsuta lista case'ów → nie zapisuj okrojonej linii. | open |
| E6 | B3 | Wykonać decyzję B3: `close.py --verify-claims` re-derywuje twierdzenia z wykonywalnym artefaktem. | `--dry-run --verify-claims` exit 1 przy rozjeździe; `close` tylko WARN; narracja pominięta. Decyzja: `docs/wayfinder-brain-answers/B3-verify-claims.md`. | (1) fałszywy `commit <hash>` → FAIL; (2) prawdziwy hash → PASS; (3) liczba bez artefaktu → WARN; (4) twierdzenie narracyjne → no-op. | **done** (2026-10-16) — [answer](wayfinder-brain-answers/E6-verify-claims.md) |
| E7 | B7 | Wykonać decyzję B7: `expect_hash` per case w `brain_eval.json` + pre-flight w `eval_brain.py --check`. | Fail-loud `--check`, gdy wiersz spod `expect` ≠ `expect_hash`; `_row_fingerprint` jako jedno źródło „wiersza". Decyzja: `docs/wayfinder-brain-answers/B7-content-hash-anchors.md`. | (1) bezimienny scar wstawiony do `SCARS.md` → `--check` FAIL (nazywa case+ID); (2) kontrola: `--check` PASS; (3) wiersz przeredagowany in place (to samo ID, treść inna) → FAIL. | **done** (2026-10-16) — [answer](wayfinder-brain-answers/E7-expect-hash.md) |

**E1–E5** = jawny handoff zamykający 5 `task`-ticketów z 534dfa4.
**E6–E7** = wygraduowane `task`-deliverable (B3 tą sesją, B7 w 534dfa4 jako „osobny
effort" bez nazwy). Bez nich dług S64/S65 (decyzja bez wykonawcy) rośnie — stąd je tu
nazywamy.

## Out of scope

- Wszystko, co nie jest jedną z decyzji E1–E7 (brak nowego rozstrzygania).
- Pozostałe otwarte `grilling`-tickety mapy decyzyjnej: **B6**, **B8**, **B11** — to
  decyzje, nie deliverable; żyją w `docs/wayfinder-brain-map.md`.
- Cross-project i ogólna higiena (audyt #5, #6, #7, #9, #10, #13, #14) — zostają w
  `## Out of scope` mapy decyzyjnej.
- Nowa decyzja wyłoniona w trakcie wykonania → **wraca do mapy decyzyjnej**, nie jest
  rozstrzygana tutaj (ta mapa wykonuje, nie rozstrzyga).
