# Wayfinder Map: Ulepszenia warstwy `brain`

## Destination

Lista **rozstrzygniętych decyzji** o tym, które z 18 kandydatów z audytu warstwy `brain`
wchodzą, **w jakiej kolejności** i **z jakim kryterium sukcesu** — albo jawnie
**odrzuconych z powodem i decydentem**. Cel: droga do wykonania jest jasna, zanim
ktokolwiek pójdzie budować. To mapa **decyzji**, nie deliverable.

## Notes

- **Domena:** warstwa `brain` (`scripts/brain.py`, `scripts/memory/retrieval_v1.py`,
  `scripts/ingest_brain.py`, `scripts/memory/brain_eval.json`) oraz jej bezpośrednie
  mechanizmy: `scripts/memory_index.py` i kontrakt flag/handoff (`scripts/close.py`,
  `handoff/flags/`).
- **Zakres (decyzja właściciela, sesja planistyczna 2026-10-16):** **tylko warstwa brain
  i jej bezpośrednie mechanizmy.** Cross-project i ogólna higiena procesu → *Out of scope*.
- **Skille do konsultacji:** `wayfinder`, `grilling`, `domain-modeling`, `research`.
- **Gdzie żyją answers:** `docs/wayfinder-brain-answers/B<N>-<slug>.md` (konwencja: jej
  `README.md`). Mapa tylko linkuje; `## Decisions so far` trzyma jedną linię (nazwa + link +
  gist). B1/B9 zmigrowane 2026-10-16.
- **Tryb i claim:** rozstrzyganie grupami tematycznymi (nie 1 ticket/sesja; właściciel,
  2026-10-16). Claim przed pracą — równoległa sesja pomija zajęty ticket.
- **Task ≠ decision:** destination = decyzje, nie deliverable; ticket typu `task` bez trybu
  execute-in-map w tym Notes → out of scope (handoff wykonawczy).
- **Zasada nadrzędna:** bramka musi umieć failować (`SCARS.md` S56, S62). Każde kryterium
  sukcesu ma adversarial case zapisany **przed** runem.
- **Fakty zweryfikowane w worktree (nie z briefu):**
  - `handoff/flags/` — liczba plików jest zmienna (dryfuje); nie snapshotować jej w
    kontrakcie. Sprawdź na żywo: `(Get-ChildItem handoff/flags).Count`.
  - `agent_sessions.py::SUPPORTED_AGENTS` = 11 → poza opencode jest **10** store'ów
    (brief mówił 8; brakowało `omp`, `deepseek`).
  - `ingest_brain.py::check()` porównuje **fingerprint wiersza** (`id|title|root_cause|fix|gate|scar`),
    raportuje `missing`/`extra`/`drifted` — **nie** tylko liczbę wierszy. Premisa kandydata #16
    była nieścisła (patrz B8).
  - `brain_eval.json` anchoruje na `table:id` gdzie `problems:10XX = 1000 + kolejność linii` —
    wstawienie scara w środku `SCARS.md` przesuwa anchory, a `--check` tego nie widzi (patrz B7).
  - `supersedes`/`superseded_by` istnieją w schemacie (`scripts/_scratch/migrate_brain.py`),
    ale `ingest_brain.py` ich nie wypełnia — decyzja właściciela: odłożone.

## Decisions so far

<!-- Właściciel = decydent. Runda chartująca 2026-10-16 + sesja wykonawcza B7 2026-10-16. -->

- [Destination-named]: destination = lista rozstrzygniętych decyzji; scope = tylko warstwa
  brain i jej bezpośrednie mechanizmy. Właściciel, 2026-10-16.
- [PL↔EN-resolved]: **metric fix** — lexical K1 ma limit cross-lingual; usunąć case z
  `brain_eval.json`, nie dodawać mapy PL→EN (brak zmierzonej potrzeby; `brain/CONTEXT.md`
  „No vectors and no reranker"). Właściciel. → egzekucja w B4.
- [refuse-risotto-resolved]: **badly designed case** — zamienić query na tokenowo rozłączne
  z korpusem; nie zmieniać silnika (brak progu = brak tuningu). Właściciel. → egzekucja w B5.
- [supersedes-deferred]: `supersedes`/`superseded_by` — **odłożone**; kolumny zostają
  nieużywane, dopóki nie pojawi się konsument ukrywający `status='superseded'`. Właściciel.
- [B1 — drift surface of non-opencode stores](wayfinder-brain-answers/B1-drift-surface.md):
  10 store'ów poza opencode; tylko opencode sonduje `sqlite_master`. Najwyższe ryzyko cichej
  utraty: **deepseek** (już raz migrował format, `if not events: continue`). → motywuje B2.
- [B9 — izolowany worker refleksji](wayfinder-brain-answers/B9-reflection-worker.md):
  „worker refleksji" = **zarchiwizowany** `pipeline/06_reflect` ARL, wołany ręcznie (brak
  crona/hooka); brak śladu sesji 569 i brak literału `bun.exe` (to `omp.exe` przez Bun).
  Poza warstwą brain → #8 w *Out of scope*, B10 zamknięty.
- [Grupowanie + rekoncyliacja driftu]: rozstrzyganie **grupami tematycznymi** (nie
  1 ticket/sesja). ID w prompcie sesji rozjechały się z mapą (prompt „metryka = B3/B4/B12" =
  mapa **B4/B5/B7**); mapa jest autorytatywna, frontier = 10 (nie 11+2). Właściciel, 2026-10-16.
- [Task ticks → out of scope]: B2/B4/B5/B12/B13 (typ `task`) poza destination (mapa decyzji,
  nie deliverable; brak execute-in-map w Notes). Właściciel, 2026-10-16.
- [B7 — content-hash w anchorach `brain_eval.json`](wayfinder-brain-answers/B7-content-hash-anchors.md):
  adopt `expect_hash` per case, fail-loud w `eval_brain.py --check` (R21); kryterium = 3 mutacje
  (shift / reword / kontrola). Właściciel, 2026-10-16.
- [execution handoff](wayfinder-brain-execution-map.md): 5 tasków (B2/B4/B5/B12/B13) →
  `wayfinder-brain-execution-map.md` (tryb `execute-in-map`); E6/E7 (B3/B7) wygraduowane tam.
  Mapa decyzyjna zostaje jako referencja. Właściciel, 2026-10-16.
- [B3 — `close.py --verify-claims`](wayfinder-brain-answers/B3-verify-claims.md):
  zakres = twierdzenia z wykonywalnym artefaktem (hash/licznik/gate), narracja pominięta;
  fail-loud w `--dry-run`, WARN w `close`; kryterium = 3 mutacje. Właściciel, 2026-10-16.

## Not yet specified

- Polityka wersjonowania scarów/decyzji (`supersedes`): wraca jako świeży effort, gdy
  pojawi się **pierwszy konsument** ukrywający `status='superseded'` (dziś: nikt go nie potrzebuje).
- Kształt filtra pustych sesji zależy od tego, czy „pusta" = brak treści asystenta czy brak
  jakiejkolwiek wymiany — do zaostrzenia w B6.
- Detektory korupcji wewnątrz wiersza zależą od tego, co `--check` (fingerprint treści) już
  łapie, a co nie — do zaostrzenia w B8.

## Out of scope

- **#5** wymuszenie `python -c` (hook/preflight) — ogólna higiena procesu, nie warstwa brain.
- **#6** zakaz tautologii w scarach (`N = M + K` bez komendy weryfikującej) — ogólna higiena
  treści, nie warstwa brain.
- **#7** cross-project transfer scarów / federacja — cross-project.
- **#9** `ORDER BY id` bias w `workspace-research` — projekt zarchiwizowany.
- **#10** semantic search / `family_rank@5` — `brain/CONTEXT.md` jawnie: brak zmierzonej
  niedostateczności; decyzja właściciela (2026-10-16) = out.
- **#13** `_scratch/` churn — higiena.
- **#14** zamiana point-fixów na generalizacje — meta-zasada, nie warstwa brain.
- **#8** izolowany worker refleksji — to zarchiwizowany `pipeline/06_reflect` ARL (cross-project),
  nie mechanizm warstwy brain; zweryfikowane w B9 (brak śladu sesji 569, brak `bun.exe`,
  brak żywego wywołania). Residuum: wpis `reflection/logs` w `DECLARED_OUTPUT_DIRS`
  (`check_workspace_integrity.py:206`) — do sprzątnięcia razem z ARL, nie tutaj.
- **Tickety `task`** (spec poza destination; mapa decyzji, nie deliverable — właściciel,
  2026-10-16): **B2** (asercja driftu schematu), **B4** (usunięcie case PL↔EN), **B5**
  (zamiana query refuse-risotto), **B12** (naprawa `model: current` w flagach), **B13**
  (historia per-pytanie eval). Decyzje, które je motywują, żyją w `## Decisions so far`;
  wykonanie = handoff do osobnego effortu.

---

## Tickets (Child Issues)

| ID | Typ | Tytuł / pytanie | Blocked by | Status |
|---|---|---|---|---|
| B1 | research | Które z 10 store'ów poza opencode czytają tabelę/klucz wrażliwy na migrację schematu (cicha utrata wierszy jak S68)? | — | **resolved** |
| B2 | task | Jedna asercja driftu schematu per agent w `memory_index.py ingest` (najnowsza sesja w store X jest w indeksie; jeśli nie — FAIL z nazwami tabel). | — (B1 done) | **closed — out of scope** (`task`) |
| B3 | grilling | `close.py --verify-claims`: które twierdzenia flagi re-derywować, i jaki failure mode? | — | **resolved** |
| B4 | task | Wykonać decyzję PL↔EN: usunąć case z `brain_eval.json`, re-baseline, zapisać powód. | — | **closed — out of scope** (`task`) |
| B5 | task | Wykonać decyzję refuse-risotto: zamienić query na tokenowo rozłączne, utrzymać 4 odmowy. | — | **closed — out of scope** (`task`) |
| B6 | grilling | Filtr pustych sesji w `memory_index.py` (#4): próg i miejsce. | — | open |
| B7 | grilling | Content-hash w anchorach `brain_eval.json` (#15): przyjąć `expect_hash` per case? | — | **resolved** |
| B8 | grilling | Detekcja korupcji wewnątrz wiersza (#16): które detektory, skoro `--check` już porównuje fingerprint treści? | — | open |
| B9 | research | Izolowany worker refleksji (#8): dlaczego `bun.exe` timeout od sesji 569? | — | **resolved** |
| B10 | grilling | Worker refleksji: przywrócić czy wycofać (#8)? | B9 | **closed — out of scope** (B9: ARL/archived, nie brain) |
| B11 | grilling | Wiersz routingu `brain` w `AGENTS.md` (#11): plan R13 (≥3 pliki). | — | open |
| B12 | task | `model: current`/`default` w flagach (#12): naprawić 13 linii + wymusić kontrakt. | — | **closed — out of scope** (`task`) |
| B13 | task | Historia per-pytanie eval (#17): `eval_brain.py` dopisuje `brain_eval_runs.jsonl` z `failed:[...]`. | — | **closed — out of scope** (`task`) |

**Frontier (open, unblocked, unclaimed):** B6, B8, B11.
**Resolved:** B1, B9 (research, sesja planistyczna); B7, B3 (grilling, 2026-10-16).
**Closed out of scope:** B10; oraz `task`-tickety B2, B4, B5, B12, B13 (destination = decyzje).
Handoff wykonawczy: [docs/wayfinder-brain-execution-map.md](wayfinder-brain-execution-map.md).

Answers (pełna treść) żyją w `docs/wayfinder-brain-answers/` — mapa tylko linkuje.
