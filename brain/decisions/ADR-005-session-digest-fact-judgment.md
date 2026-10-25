---
type: Concept
title: ADR-005-session-digest-fact-judgment
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# ADR-005: Session digest — fakt/osąd, stabilny klucz, coverage hash

## Status

Accepted (design); **L0 unproven — A/B 2026-10-23**. T7 is built; gates in
`docs/session-digest-GATES.md`. L1 is in use as a selection index. L0 is not an
analysis layer until a test shows otherwise (`handoff/flags/session-digest-ab-2026-10-23.md`).

## Kontekst

`last_sessions_merged.md` miał być indeksem, a bywał transkryptem. Diagnoza
z 2026-10-22 mówiła o pliku 3,1 MB; pomiar z tego samego dnia pokazał inny
stan: `02_products/last_sessions_merged.md` ma **6 458 B** i jest indeksem
10 sesji, a 3,9 MB ma `last_sessions_exact.md`. L2 to dziś
`03_records/sessions/ses-NNN.md` + `04_payloads/`, nie monolit z kotwicą
`#session-N`.

To zmienia problem. Nie brakuje transkryptu ani indeksu — brakuje **drugiej
warstwy**: zwartego, diffowalnego digestu, który mówi, co się zmieniło
w kierunku, co jest otwarte i gdzie sesje sobie przeczą. Mechaniczne fakty
już częściowo istnieją: `tool_calls.jsonl`, `claims.jsonl`, `index.tsv`,
`session_ground_truth.md` (442 169 B / 100 sesji) oraz nagłówek merged
(zakres dat, miks agentów/modeli, mikro-sesje, straty).

Trzy pułapki, które ten ADR zamyka:

1. **`ses-NNN` nie jest stabilnym id.** `03_records/CONTEXT.md` mówi wprost:
   „session N of the last run, not a stable id”. Przy N=100 → 110 wszystkie
   karty zmieniłyby numer i diff przestałby być diffem.
2. **Substring dowodzi istnienia cytatu, nie tego, że cytat uzasadnia
   twierdzenie.** Etykieta `verified` byłaby kłamstwem w pliku integralności.
3. **Dowody „B dowodzi ¬X” często są w tool-outputach**, a ciała sesji są
   signature-compacted. Gate sprawdzający tylko body przepuściłby prozę
   i odrzucił najlepsze dowody.

## Decyzja

### 1. Trzy warstwy, jedno źródło prawdy

- **L0 — `session_digest.md`** (≤15 KB): cross-session stan, nie dziennik.
- **L1 — `session_cards.json`** (kanoniczny) + `session_cards.md` (render):
  jedna karta na **sesję główną**; dzieci są listą `child_session_ids`
  w karcie rodzica, nie osobnymi kartami w MVP.
- **L2 — `03_records/sessions/` + `04_payloads/`**: bez zmian; ground truth
  i miejsce, do którego prowadzą dowody.

Run mechaniczny pisze L1 i szkielet L0. Warstwa osądu jest opcjonalna
i oddzielona.

### 2. Każde twierdzenie L0 ma typ i evidence

```text
claim := {
  type: "mechanical_delta" | "judgment",
  evidence_check: "substring_exists",
  supports: null | "unverified_inference",
  evidence: {
    session_key: "<agent>:<session_id>",
    source: "body" | "payload",
    path?: "<repo-relative path>",
    line?: <int>,
    sha?: "<sha256 of the normalized cited region>"
  }
}
```

- `mechanical_delta` = różnica między kartami (nowe flags/commits/tests),
  bez interpretacji; `supports: null`.
- `judgment` = dopiero po `--classify`; `supports: "unverified_inference"`.
- `evidence_check` ma dokładnie jedną wartość: `substring_exists`. Nie ma
  `verified`, bo walidator nie ocenia inferencji.
- Brak evidence → wpis nie wchodzi do L0; trafia do `not_checked` z kodem
  powodu.

### 3. Stabilny klucz i okno

- Tożsamość: **`agent:session_id`** (`SessionItem.id`, nie `ses-NNN`).
- `ses-NNN` jest wyłącznie wskaźnikiem runu i może się zmieniać.
- N liczy **sesje główne**; dzieci są przypięte przez `parent_session_id`
  i wypisane w `child_session_ids`. Karta dziecka nie jest liczona jako
  niezależna sesja i nie jest materializowana w L1 w MVP (jej treść zostaje
  w L2; karta rodzica zmienia się, gdy zmieni się lista dzieci).
- Nagłówek L0 podaje osobno: liczbę sesji głównych, liczbę dzieci, dokładny
  zakres dat, semantykę N (`count` vs `days`) oraz `--days`, jeśli użyte.
- Mikro-sesja = `message_count <= 4`; jest oznaczana, nie wykluczana.

### 4. Schema karty i puste pola

```text
card := {
  stable_key, agent, session_id, ses_n,
  parent_session_id, child_session_ids,
  date, duration, model, micro,
  goal:    {kind: "prompt" | "none", text?, reason?},
  ending:  {kind: "marker" | "quote" | "none",
            text?, marker?, raw_line?, source_line?, markers_version?, reason?},
  flags: [], flags_missing: [], commits: [], files: [], tests: [],
  tool_facts: {status, calls, sha256?, mtime?},
  losses: {...},
  card_sha256
}

card_sha256 = sha256(canonical_json(card bez card_sha256 i bez ses_n))
```

Zamknięte, wersjonowane słowniki:

- `goal.reason` / `ending.reason`:
  `empty_model_output | boilerplate | not_extracted | agent_unsupported_mvp | no_evidence`
- `tool_facts.status`: `none | fresh | stale | missing`
- `ending.marker` / `markers_version`:
  `empty_model_output | stop_gate | blokada | not_checked | awaiting_owner`

Zasady pustych pól:

- fakty mechaniczne = `[]` (zero mechaniczne), nie `—`, nie `none`;
- cytaty = `{kind: "none", reason: "..."}` (brak dowodu);
- `—` tylko w renderze Markdown dla `kind: none`;
- `tool_facts.status: none` znaczy „sesja nie ma tool-calli”, a nie „brak
  danych”; `missing` znaczy „nie udało się odczytać albo sidecar nie ma
  mapowalnego `key`”; `calls` wtedy pochodzi z body, nie z ordinala `ses_n`.

`ending` zastępuje `outcome`, bo ostatnia linia prozy nie jest konkluzją.
`ending.marker` uznajemy tylko w pozycji maszynowej: pole nagłówka sesji albo
samodzielna linia (poza fence, bez prefiksu/sufiksu poza whitespace).
`STOP GATE` w prozie nie jest markerem. Ekstraktor zapisuje `source_line`
i `raw_line`; walidator sprawdza samodzielność i zgodność po normalizacji.

`flags` to flagi **dotknięte** przez tool input (`write`/`edit`/`git rm`/`mv`),
nie każda wzmianka w prozie. `commits` to hashe z linii `[main <sha>]`
w tool output, nie dowolny hash w tekście. `files` to ścieżki z inputów
`write`/`edit`, top 5 po częstości, skrócone względem `ROOT`. `tests` to
ostatnie 5 linii wyników. `losses` mierzy `trunc`/`artifact`/`ext768`/
`superseded`; `losses.dup` nie jest mierzony w MVP i jest jawnie w L0
`not_checked`, nie cichym zerem.

Budżet: **L0 ≤15 KB twardo**; **L1 70–150 KB** dla 100 sesji głównych,
mierzone. Ponad 150 KB → tnij `files`/`commits` przed cytatami.
Pomiar 2026-10-22: L0 788 B, L1 99 277 B dla 100 sesji głównych
(105 dzieci w `child_session_ids`).

### 5. Jedno źródło ekstraktorów

Czyste funkcje (`_flag_id`, `_last_line`, `_losses_str`, regexy commitów,
markerów i strat) przenosimy do `scripts/session_facts.py`. Używają ich
`scripts/last_session_merged.py` i `scripts/session_digest.py`. Ciało sesji
jest źródłem cytatów; `tool_calls.jsonl` jest cross-checkiem, nie twardą
zależnością. Sidecar zapisuje `key` = `agent:session_id`; mapowanie po
`ses_n` jest zabronione, bo to ordinal runu. Gdy sidecar nie ma `key`,
`tool_facts.status` = `missing` (a `calls` pochodzi z body), nigdy fałszywe
`fresh`. Cross-check zapisuje `tool_calls_sha256`/`mtime` i status
`fresh|stale|none|missing`; nie ma cichego fallbacku. Refaktor ma gate:
output merged na fixture byte-identical przed/po.

### 6. Coverage hash i starzenie

`source_cards_sha256` liczymy po **kanonicznej serializacji**
`coverage_descriptor`, nie po całych kartach i nie po całym pliku:

```text
coverage_descriptor := {
  schema_version,
  normalizer_version,
  cards: [{stable_key, card_sha256}, ...]   // posortowane po stable_key
}

source_cards_sha256 = sha256(canonical_json(coverage_descriptor))
canonical_json = json.dumps(obj, sort_keys=True, separators=(",", ":"),
                            ensure_ascii=False).encode("utf-8")
```

`normalizer_version` jest częścią hasha, bo zmiana normalizera zmienia to,
co digest twierdzi o evidence. Digest deklaruje `validity_basis: coverage`
(nie „current as of”).

Dwa sygnały:

- **`covered_cards_mismatch`** — karta w coverage się zmieniła → twardy fail
  G10, `session-digest-stale`;
- **`new_sessions_since`** — lista `stable_key` z bieżącego runu poza
  coverage → tylko informacja w nagłówku i README, nie blokuje.

Dzięki temu promowany digest nie starzeje się sam przez nowe sesje.

### 7. Evidence gate i normalizer

- `claims` (mechaniczne) — źródło `body`.
- `proves` (osąd) — źródło `body` albo `payload`; pointer musi mieć `path`,
  `line`, `sha`; walidator sprawdza plik payloadu, nie tylko body.
- Walidator sam liczy `line` i `sha`; nie ufa danym od LLM.
- Normalizer jest wersjonowaną funkcją: CRLF→LF, collapse poziomych
  whitespace; **bez** ruszania backticków, fence’ów i markdownu.
  `normalizer_version` trafia do karty i coverage.
- Odrzucone wpisy → `not_checked` z kodem:
  `quote_not_found | payload_not_found | payload_sha_mismatch | marker_not_standalone | unsupported_agent`.
- Negative controls w CI: fałszywy cytat i fałszywy payload-pointer muszą
  zostać odrzucone.

### 8. Cykl życia osądu i promocja

- MVP: `judgment: []`, `judgment_status: not_run` — brak jest jawny.
- L0 ma sidecar `session_digest.json` (te same fakty co MD) dla walidatora;
  MD pozostaje czytelny dla człowieka.
- `--classify` (później): czyta **tylko** karty, nie L2; pisze
  `candidates/digest.judgment.md`.
- Promocja to osobny commit/run po review:
  `docs/sessions/digest-YYYY-MM-DD.md` (data promocji, nie runu), blok
  `promotion: {promoted_at, promoted_by, review_ref}`.
- `docs/sessions/README.md` jest ręczny i zmienia się **tylko** w commicie
  promocji: ścieżka najnowszego digestu, `digest_sha256`,
  `source_cards_sha256`, data.
- Run mechaniczny nigdy nie dotyka promowanego digestu ani README.
- `review_ref` jest wymagany, inaczej human gate jest nieaudytowalny.

### 9. Zakres i tracked

- MVP: `opencode`. Inne agenty nie są pomijane — dostają kartę z
  `goal/ending: {kind: none, reason: agent_unsupported_mvp}`.
- Mechaniczne karty i runy zostają w gitignored `02_products/`.
- Tracked jest tylko promowany digest i README; bez payloadów i surowych
  cytatów. Cytaty w promowanym pliku mają limit długości.

## Worked example: 9 vs 10

Pomiar 2026-10-22:

```text
last_sessions_merged.md   6 458 B
session_ground_truth.md   442 169 B
tool_calls.jsonl          1 599 wierszy / 9 distinct session ids
eksport merged            10 sesji
```

`ses-006` to opencode, 8 wiadomości, **0 tool-calli** (`Straty: brak`,
`Ostatnia linia: [empty model output]`). Dlatego sidecar ma 9 sesji, a eksport
10: sidecar liczy sesje, które mają wywołania, nie sesje w ogóle. To nie
ubytek danych.

Karta `ses-006` dostaje:

```text
tool_facts: {status: "none", calls: 0}
ending:     {kind: "marker", marker: "empty_model_output",
             text: "[empty model output]", source_line: <n>}
```

Bez rozróżnienia `none` / `missing` za tydzień ktoś napisze „9 sesji”
i będzie to wyglądało na ubytek. To jest dokładnie różnica między „zero
mechaniczne” a „brak danych”, którą ten ADR utrwala.

## Wynik A/B (2026-10-23)

Pytanie: *co się stało z `--classify` — ile kandydatów, czy promowano, dlaczego,
następny krok?* Te same 3 sesje (review/promocja, classify, commit); trzy korpusy:

| Korpus | Zawartość | Rozmiar | Odczyt | Wynik |
|---|---|---|---|---|
| P | L1: 3 karty + 3 pełne body | 270 040 B | 1 828 / 5 670 linii | 4/4 fakty |
| Q | `did` dla tych samych 3 sesji | 180 308 B | 3 726 / 3 726 | 4/4 + 3 extra |
| R | tylko 3 karty L1 | 3 913 B | 147 / 147 | 0/4 — „brak w materiale” |

Punktowane: 6 kandydatów (4 `open_threads` + 2 `contradictions`); 0/6
prawdziwych → brak promocji; przyczyna `_marker_scan` + `not_checked` w
`OPEN_MARKERS`; następny krok rules-v2 + `review_ref`. L0 nie wniósł nic
(781 B, `_brak_`).

Wniosek: **L1-only nie jest warstwą analityczną** (0/4), a `did` odpowiedział
pełniej i taniej niż L1+body (180 KB vs 270 KB). L0 zostaje zamknięte jako
unproven; L1 zostaje selektorem (`session_cards.json` → filtr `files`/`flags`
→ eksport 2–5 sesji). Bez `--profile llm`.

Ograniczenia: n=1 pytanie, 3 sesje, jeden model; P i Q mają różny filtr treści;
ocena nie w pełni blind; sesja projektowa (574 KB w `did`) poza testem.
Evidence: `handoff/flags/session-digest-ab-2026-10-23.md`.

## Konsekwencje

- L0 jest małe i diffowalne; nowa sesja nie unieważnia promowanego digestu.
- Każde twierdzenie L0 ma sprawdzalny pointer; czytelnik wie, co jest faktem,
  a co inferencją.
- Refaktor ekstraktorów jest mały i gate’owany, więc merged i digest nie
  rozjadą się w parserach.
- Koszt: dwa uruchomienia (mechaniczny + opcjonalny classify), ręczna
  promocja i utrzymanie `normalizer_version` / `markers_version`.
- Koszt: karty dla sesji bez tool-calli i dla nieobsługiwanych agentów są
  celowo ubogie; to jest poprawne, nie „do naprawy”.

## Odrzucone alternatywy

- **Ulepszanie transkryptu zamiast dodania warstwy.** To samo 3 MB w innym
  formacie; problemem był brak syntezy, nie format.
- **`ses-NNN` jako klucz.** Numeracja runu zmienia się przy każdym N; diff
  przestałby być diffem.
- **Hash całego `session_cards.json`.** Każda nowa sesja unieważniałaby
  digest; `new_sessions_since` ma być informacją, nie statusem.
- **`verified` zamiast `substring_exists`.** Walidator nie wie, czy cytat
  uzasadnia twierdzenie; nazwa musi to mówić.
- **Klasyfikacja `outcome` heurystyką na wolnym tekście.** `STOP GATE`
  występuje 118× w korpusie jako temat rozmowy; marker tylko z zamkniętego
  słownika i tylko w pozycji maszynowej.
- **Automatyczna promocja po `--classify`.** Human gate bez review_ref jest
  nieaudytowalny.
- **Trackowanie surowych cytatów/payloadów.** Ryzyko wrażliwych danych;
  tracked jest tylko digest po review.
- **`--profile llm` przed testem A/B.** Test 2026-10-23 nie wykazał przewagi
  L1/L0 nad `did` (L1-only 0/4; `did` 4/4 przy 180 KB vs 270 KB dla L1+body).
  Nowy profil to koszt bez dowodu.

## Referencje

- `docs/wayfinder-session-digest.md` — mapa, D1, T1–T7.
- `docs/session-digest-GATES.md` — G1–G12.
- `scripts/_scratch/sessions/CLAUDE.md` — routing labu.
- `scripts/_scratch/sessions/03_records/CONTEXT.md` — ostrzeżenie o `ses-NNN`.
- `scripts/agent_sessions.py` — `SessionItem`, `parent`.
- `scripts/last_session_merged.py` — ekstraktory do wydzielenia.
