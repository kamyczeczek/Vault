# HISTORY.md — Vault

> Kuratorowana historia rozwoju Vault: punkty zwrotne, intencje, decyzje,
> konsekwencje, to co przetrwało i co porzucono. Nie katalog commitów.
> Każdy punkt zwrotny ma ślad dowodowy: sesja → decyzja → commit → stan.
>
> Ostatnia weryfikacja: 2026-11-06. Źródła: sesje agentów (indeks FTS5,
> 2171 sesji, 2026-07-09 → 2026-11-06), handoffy/flagi (269 flag w
> handoff/flags/; 269 sesji typu curated w indeksie), ADR-y (9 w 4
> lokalizacjach), DECISIONS.md (D1..Dn), git (100 commitów), kod i testy.

## Geneza — projekty i eksperymenty poprzedzające unifikację (2026-07-09 → 2026-10-23)

**Uwaga o zakresie.** To nie jest historia istniejącego repozytorium Vault
(to zaczyna się 2026-10-24). To geneza intelektualna: wcześniejsze projekty
i eksperymenty, z których wyrósł obecny system. Nazwy projektów i daty
wczesne mają niższą pewność — wiele materiałów nie ma dat.

- **2026-07-09 — Pierwsze sesje w store'ach.** [fakt] Indeks sesji obejmuje
  2171 sesji od 2026-07-09. [interpretacja] Początek eksperymentów
  badawczych bez wspólnej infrastruktury. [niepewność] Przynależność
  wczesnych sesji do „Vault” jako przedsięwzięcia jest niepewna — ścieżka
  robocza była `PROJECTS/root_worksapce`. [źródło] memory_index (date range);
  `scripts/_scratch/sessions/90_archive/`.
- **2026-09-16 / 2026-09-20 — RAG jako warstwa wiedzy.** [fakt] Sesje
  omp `01a0aa9f-e15` (2026-09-16) i `01a0ba21-88c` (2026-09-20)
  dyskutują ewolucję Naïve → Advanced → Modular → Graph → Agentic RAG.
  [interpretacja] Zmiana z „mamy projekty” na „potrzebujemy retrieval”.
  [niepewność] Czy to był świadomy pivot, czy naturalna ewolucja — sesje
  nie rozstrzygają. [ślad] sesja `01a0ba21-88c` → decyzja o RAG jako
  warstwie wiedzy → stan: `projects/research/brain/` (FTS5 sidecar),
  `projects/research/knowledge-retrieval/`, `projects/research/retrieval-v2/`.
  [źródło] memory_index; jcode `session_hedgehog` (2026-09-23, MUST-RAG).
- **2026-09-27 — research-engine z anti-leakage.** [fakt] Sesja opencode
  `ses_f1c759ef` (2026-09-27): ModelDiscoveryEngine, AntiLeakageHarness w
  `PROJECTS/root_worksapce/projects/research-engine`. [interpretacja] Pierwsza
  próba systematycznego odkrywania modeli z ochroną przed leakage. [ślad]
  sesja `ses_f1c759ef2ffeY3VIn2aSP6T1Bw` → decyzja o anty-leakage →
  aktualna lokalizacja `projects/research/research-engine/` różni się od
  lokalizacji wskazanej w sesji. Migracja w ramach unifikacji jest
  prawdopodobna, ale nie została potwierdzona diffem ani historią zmian.
  [potwierdzenie] brak `projects/research-engine` w drzewie;
  `projects/research/research-engine/` istnieje z `CLAUDE.md`, `CONTEXT.md`,
  `preflight.py`, `history.bundle`. [źródło] memory_index;
  `projects/research/research-engine/`.
- **2026-10-01 — Test knowledge graph.** [fakt] Sesja pi `01a0f427-cea`
  (2026-10-01). [niepewność] Zakres i wynik eksperymentu nieznany bez
  drillu. [źródło] memory_index.
- **2026-10-03 — ICM wczesne.** [fakt] Sesja opencode `ses_efd6471c`
  (2026-10-03). [interpretacja] Początek struktury kontraktowej (ICM).
  [źródło] memory_index.
- **2026-10-04 — Goose MCP graph test.** [fakt] Archiwum
  `90_archive/ARCHIVE/Goose-MCP-graf-test-hipotezy-2b-2026-10-04.md`.
  [źródło] plik archiwalny.
- **2026-10-11 — DSH / konfiguracja agentów.** [fakt] Sesja opencode
  `ses_ed7b85d9` (2026-10-11). [źródło] memory_index.
- **2026-10-16 / 2026-10-17 — Wayfinder brain (5 decyzji).** [fakt]
  Sesje opencode `ses_ebd6cc86`, `ses_ebd8a1f4`, `ses_ebd22e8e` (2026-10-16)
  i pi `01a14a7f-582` (2026-10-17). [interpretacja] Pivot od implementacji
  do decyzji: mapa jako artefakt. [ślad] sesja
  `ses_ebd6cc866ffeqRq3KQ0FNqKpqC` → 5 decyzji w `docs/wayfinder-brain-map.md`
  → grill B3 (commit hash niezweryfikowany w tym repo — sesja powiązana, nie
  potwierdzona przez commit) → stan: `docs/wayfinder-brain-map.md` +
  `docs/wayfinder-brain-answers/` (B1, B3, B7, B9, E1, E4, E6, E7).
  [źródło] memory_index + docs/.

## Unifikacja (2026-10-24 → 2026-10-28)

- **2026-10-24 — Vault layout & git bootstrap.** [fakt] Sesje opencode
  `ses_e914b9a8`, `ses_e914b9a7` (2026-10-24 18:18) i codex `01a170a0-0a4`
  (2026-10-25). [ślad] sesja `ses_e914b9a80ffe9FzcJRHY4i2X9H` → decyzja
  o bootstrapie → commit `59faa7d` (vault-layout-and-git-bootstrap) i
  `edba1b8` (vault-migrated) → stan: root workspace re-bootstrapped, single
  vault. [fakt] flagi `vault-migrated`, `vault-single-repo`,
  `vault-root-flatten`. [interpretacja] **Granica pre-Vault ↔ Vault**:
  powstanie repozytorium = unifikacja. Nie początek przedsięwzięcia.
  [źródło] memory_index + git log.
- **2026-10-25 — Single repo + research engine.** [fakt] Sesja opencode
  `ses_e8c3a094` (2026-10-25) i codex `01a173c7-632` (2026-10-25). [ślad]
  sesja `ses_e8c3a094cffeOIcA8kluNFwWSU` → migracja → commit `cfac8a4`
  (vault-root-flatten-2026-10-25: przeniesienie zawartości `root_workspace/`
  do root, 0 zmian treści — same renames) i `d1231b5`
  (vault-single-repo-2026-10-24: rozstrzygnięcie sporu o root vaulta; zmiana
  HANDOFF, STATE, brain/decisions/index, flaga, STATUS) → stan: jedno repo.
  [fakt] W sesji opencode `ses_e7d5a5da` (2026-10-28) użytkownik stwierdził,
  że plany monorepo były „stale/regenerated” — praca już zrobiona.
  [interpretacja] Odrzucenie planów monorepo jako redundantnych. [źródło]
  memory_index.
- **2026-10-28 — Migracja zakończona.** [fakt] Sesja opencode `ses_e7fa63a1`
  (2026-10-28): „Migracja Vaulta do single-repo”, definicja done: czysty
  git status. [ślad] sesja `ses_e7fa63a10ffeiHtYxMb0nvOtRI` → commit
  `4d3609f` (single-repo-codegraph-2026-10-28: monorepo zweryfikowany,
  CodeGraph indeksuje projekt; zmiana .gitignore, HANDOFF, STATE, flaga,
  scripts/close.py) → stan: jedno repo z CodeGraph. [fakt] Sesja opencode
  `ses_e80be222` (2026-10-28): knowledge retrieval RAG. [źródło]
  memory_index.

## Ewolucja wiedzy i retrievalu (2026-09-20 → 2026-10-29)

*Tematycznie nachodzi na Unifikację (wayfinder brain 2026-10-16 poprzedza
bootstrap 2026-10-24). Szczegóły RAG i wayfinder brain opisane w Genezie;
tutaj tylko punkty zwrotne i ślad dowodowy.*

- **2026-09-20 / 2026-09-23 — RAG jako warstwa.** [fakt] S2 + jcode
  MUST-RAG. [ślad] sesja `01a0ba21-88c` → decyzja o RAG jako warstwie wiedzy
  → stan: `projects/research/brain/` (FTS5 sidecar), `knowledge-retrieval/`,
  `retrieval-v2/`.
- **2026-10-16 / 2026-10-17 — Wayfinder brain (decyzje).** [fakt] S3.
  [ślad] sesja `ses_ebd6cc866ffeqRq3KQ0FNqKpqC` → 5 decyzji w
  `docs/wayfinder-brain-map.md` → grill B3 (commit hash niezweryfikowany w
  tym repo — sesja powiązana, nie potwierdzona przez commit) → stan:
  `docs/wayfinder-brain-map.md` + `docs/wayfinder-brain-answers/`.
- **2026-10-28 — Knowledge retrieval RAG.** [fakt] `ses_e80be222`. [ślad]
  sesja → RAG zintegrowany z Vault → stan: `knowledge-retrieval` (active).
- **2026-10-29 — Audyt spójności ETTh1.** [fakt] Sesja opencode
  `ses_e7ac5f25` (2026-10-29). [ślad] sesja → ADR-0001 → stan: S49
  zamknięty (patrz raport ETTh1).

## Zamknięcia i odrzucone kierunki

Rozróżnienie: **porzucenie** (zrezygnowano z pomysłu), **archiwizacja**
(przeniesiono do `_archive/`, grade demoted), **zastąpienie** (zastąpiono
innym rozwiązaniem).

- **ETTh1 H720 (S49) — porzucony.** [fakt] README: „closed — S49 H720
  rejected”. [fakt] ADR-0001 (accepted, 2026-10-29). [ślad] sesja
  `ses_e7ac5f259ffeJ63nN4OGdAvZYM` → ADR-0001 → stan: badanie zamknięte,
  projekt pozostaje zasobem (raport ETTh1).
- **Plany monorepo — porzucone jako stale.** [fakt] Sesja `ses_e7d5a5da`
  (2026-10-28): użytkownik: „plan jest stale/regenerated”. [ślad]
  sesja → odrzucenie planów → stan: jedno repo (commit `cfac8a4`).
- **upload_drive API — porzucone i zastąpione.** [fakt] Flaga
  `drive-upload-did-sessions-2026-10-28`: Drive API zbudowane, potem
  porzucone (wymaga projektu Google Cloud, którego właściciel nie chce).
  Zastąpione przez `sync_did_sessions.py` (kopia do folderu Drive dla
  komputerów, zero API). [ślad] flaga → decyzja właściciela → stan:
  `scripts/sync_did_sessions.py`, `scripts/did_sessions_drive.bat`.
- **Grill B3 (content-hash anchors) — porzucony jako osobny ticket.**
  [źródło] S3 (`ses_ebd6cc86`).
- **ARL (agentic-research-lab) — archiwizowany (demoted).** [fakt]
  `CONTEXT-MAP.md`: grade `demoted` (tools-first split 2026-10-08). Przeniesiony
  do `projects/_archive/agentic-research-lab/`. [źródło] CONTEXT-MAP.
- **datasets — archiwizowany (demoted).** [fakt] `CONTEXT-MAP.md`: grade
  `demoted` (2026-09-27). Przeniesiony do `projects/_archive/datasets/`.

## Uproszczenie (2026-11-05 → 2026-11-06)

- **2026-11-05 — Grill simplification.** [fakt] Sesja omp `01a1adb0-66f`
  (2026-11-05): audyt uproszczenia, C1–C3. [ślad] sesja
  `01a1adb0-66f` → decyzja o uproszczeniu → stan: audyt
  `docs/audit-vault-simplification-2026-11-05.md`. [interpretacja] Zmiana
  kierunku: od rozbudowy do odchudzania. [źródło] memory_index + docs.
- **2026-11-06 — Audyt + recon + root slimming.** [fakt] Sesje omp
  `01a1adf0-acc`, `01a1adfe-c0a`, `01a1ae5b-a92`, `01a1ae7f-b08`
  (2026-11-06). [ślad] sesje → decyzje C1/C3 → commity `e5eaa4c`
  (C1: backup usunięty, 3152 plików, 291 MB) i `4d6267b` (C3: entry files)
  → stan: root odchudzony. [fakt] C2 (sekrety) otwarte — `scan_secrets.py`
  zwrócił `SECRETS_CLEAN`, brak commitu. [fakt]
  `docs/dependency-map-2026-11-06.md` (20 ENTRY/GATE, 85 INTERNAL, 9 DOC-ONLY,
  27 ZERO). [źródło] flagi + docs + git.

## Co przetrwało z wcześniejszych koncepcji (synteza)

| Koncepcja (era) | Przetrwało jako | Co potwierdza dowód |
|---|---|---|
| RAG / retrieval | `projects/research/brain/` (`.brain/` FTS5 sidecar), `knowledge-retrieval/`, `retrieval-v2/` | projekt active w CONTEXT-MAP (status projektu) |
| Model discovery | `projects/research/research-engine/` | projekt active w CONTEXT-MAP |
| Wayfinder decyzje | `docs/wayfinder-brain-map.md`, `wayfinder-brain-answers/` | artefakt zachowany (pliki istnieją) |
| ICM / kontrakt | `AGENTS.md`, `CLAUDE.md`, `skills/` | użycie potwierdzone (L0 gate, AGENTS.md) |
| Memory index | `scripts/memory/`, `scripts/memory_index.py` | użycie potwierdzone (2171 sesji w indeksie) |
| Session digest | `docs/wayfinder-session-digest.md` | artefakt zachowany (MVP) |
| Brain FTS5 sidecar | `projects/research/brain/.brain/` | komponent istnieje (katalog) |
| ETTh1 H720 | `projects/research/etth1-h720/` (badanie zamknięte) | projekt active (zasób), badanie zamknięte (ADR-0001) |
| ARL | `projects/_archive/agentic-research-lab/` | archiwizacja (demoted) |
| datasets | `projects/_archive/datasets/` | archiwizacja (demoted) |

## Niepewności (jawnie)

1. Daty startu/zakończenia 9 projektów w `_archive/` — większość bez dat.
2. Wayfinder tickets #1–#10 — skolapsowane w C1–C3, nie śledzone jako done.
3. Status `SECRETS_CLEAN` (C2) — audyt otwarty, brak commitu.
4. Ery E0–E3 — roboczy szkielet, nie zatwierdzona historia.
```

---

## FINALNA PROPOZYCJA — `docs/ARCHITECTURE.md`

```markdown
# ARCHITECTURE.md — Vault (mapa warstw)

> Jak Vault działa jako system. Mapa warstw + przepływy + pętla sprzężenia
> zwrotnego. Nie katalog plików, nie kopia CONTEXT-MAP.
>
> Zasada: własność danych ≠ odpowiedzialność za generowanie artefaktów.
> Człowiek jest podmiotem podejmującym i zatwierdzającym decyzje (nie
> warstwą techniczną).

## Cztery warstwy

### 1. Research
**Odpowiedzialność:** eksperymenty, benchmarki, walidacja wyników, odkrywanie
modeli.
**Własność danych:** wyniki, modele, benchmarki, ADR-y projektowe.
**Gdzie mieszka:** `projects/research/*` (benchmark-core, etth1-h720,
research-engine, knowledge-retrieval, brain, retrieval-v2,
the-pragmatic-programmer-retrieval).

### 2. Knowledge
**Odpowiedzialność:** pamięć, retrieval, indeksowanie, utrwalone decyzje,
narracja.
**Własność danych:** indeks sesji (FTS5, 2171 sesji), brain sidecar (`.brain/`),
wayfinder maps, ADR-y, DECISIONS, SCARS, GLOSSARY, flagi handoff, narracja
(HISTORY).
**Gdzie mieszka (dane):** `scripts/_scratch/sessions/05_store/memory.db`,
`projects/research/brain/.brain/`, `handoff/`, `docs/`, root `*.md`.
**Uwaga:** `handoff/flags/` to WEJŚCIE (pisane przez agentów/człowieka);
`HANDOFF.md`/`STATE.md` to WYNIK (generowane). Nie są tym samym.

### 3. Agent Infrastructure
**Odpowiedzialność:** routing, skills, konfiguracje, preflight, kontrakt L0.
**Własność danych:** zasady pracy, skills, routing projektów.
**Gdzie mieszka:** `AGENTS.md`, `CLAUDE.md`, `skills/`, konfigi OpenCode/OMP/Pi.

### 4. Automation & Governance
**Odpowiedzialność:** walidacja, budowanie stanu, gate'y, skrypty, generowanie
artefaktów.
**Własność procesu:** `build_handoff.py`, `build_state.py`, `memory_index.py`
(skrypt budujący indeks), `check_workspace_integrity.py`, `preflight.py`,
git hooks.
**Produkuje:** `HANDOFF.md`, `STATE.md`, `memory.db` (pochodna),
walidację, stan repozytorium.

## Źródła prawdy (zależnie od rodzaju danych)

| Rodzaj danych | Źródło prawdy | Generowany widok |
|---|---|---|
| Surowe sesje | store'y agentów (`~/.local/share/opencode/opencode.db`, itd.) — źródło pierwotne | `did_sessions.md` (eksport) |
| Indeks sesji | `memory.db` — odtwarzalny indeks pochodny; źródło prawdy tylko dla aktualnego stanu indeksu | `memory_index.py ingest` |
| Wiedza (brain) | `brain sidecar` (`.brain/`) — indeks/struktura pochodna; nie automatycznie źródło prawdy dla wiedzy, którą indeksuje | `brain.py` (skrypt) |
| Decyzje | `DECISIONS.md`, ADR-y | — |
| Stan bieżący | `handoff/flags/` (wejście) | `HANDOFF.md`, `STATE.md` |
| Kod / implementacja | repozytorium (git) | — |

`HANDOFF.md` i `STATE.md` są **generowanymi widokami stanu**, nie
niezależnymi źródłami prawdy.

## Rozdział własności (Knowledge) vs generowania (Automation)

| Artefakt | Własność danych (Knowledge) | Generowanie (Automation) |
|---|---|---|
| `memory.db` (indeks sesji) | Knowledge (dane sesji) | `memory_index.py ingest` |
| `HANDOFF.md` | Knowledge (flagi jako wejście) | `build_handoff.py` |
| `STATE.md` | Knowledge (stan bieżący) | `build_state.py` |
| `brain` sidecar (`.brain/`) | Knowledge (indeks wiedzy) | `brain.py` (skrypt) |

## Człowiek jako podmiot decyzji

```
┌─────────────────────────────────────────────┐
│  CZŁOWIEK (decyzje i zatwierdzenia)         │
│  zatwierdza ery, korekty, zakres narracji   │
│  — nie jest warstwą techniczną              │
└──────────────┬──────────────────────────────┘
               │ zatwierdzenie / odrzucenie
               ▼
┌─────────────────────────────────────────────┐
│  AGENT (propozycja, wykonanie, weryfikacja) │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  AUTOMATION (generowanie, walidacja)        │
└─────────────────────────────────────────────┘
```

Żadna propozycja agenta nie jest traktowana jako decyzja użytkownika bez
jawnego zatwierdzenia.

## Przepływy (dwukierunkowe)

```
Research ◄──wyniki/feedback──► Knowledge ◄──kontekst/decyzje──► Agent Infra
   ▲                                                              │
   │                                                              ▼
   └──── Automation & Governance ◄──walidacja/handoff── egzekucja ─┘
```

- **Research → Knowledge:** wyniki i ADR-y trafiają do handoffów, docs,
  DECISIONS.
- **Knowledge → Research:** retrieval i pamięć dostarczają kontekst dla nowych
  eksperymentów.
- **Knowledge → Agent Infra:** AGENTS.md i skills korzystają z CONTEXT-MAP i
  DECISIONS jako źródeł.
- **Agent Infra → Automation:** agenci uruchamiają skrypty, gate'y, preflight.
- **Automation → (wszystkie):** build_handoff/build_state aktualizują stan;
  check_workspace_integrity waliduje; wyniki wracają jako nowe flagi.

## Pętla sprzężenia zwrotnego

```
praca → flaga handoff (wejście) → build_handoff → HANDOFF.md (wynik)
      → memory/retrieval → decyzja (człowiek/agent) → walidacja (gate) → praca
```

Jedna flaga = jeden plik = jeden writer. Stan jest generowany, nie pisany
ręcznie. Integrity gate (`--check`) wykrywa nieaktualność.

## Czego ten dokument NIE robi

- Nie opisuje decyzji (→ `DECISIONS.md`).
- Nie opisuje scars (→ `SCARS.md`).
- Nie opisuje filozofii (→ `PHILOSOPHY.md`).
- Nie opisuje portfela projektów (→ `CONTEXT-MAP.md`).
- Nie opisuje stanu bieżącego (→ `HANDOFF.md`/`STATE.md`).

ARCHITECTURE linkuje do tych źródeł, nie streszcza.
```

---

## RAPORT ETTh1 — rozstrzygający (bez zmian w repo)

**Semantyka statusu `active` w CONTEXT-MAP:** grade odnosi się do **projektu
jako zasobu badawczego**, nie do konkretnego badania wewnątrz niego.

**ADR-0001 (accepted, 2026-10-29):** zamyka **linię badawczą S49**
(hipoteza H720), nie projekt. „Ewentualne przyszłe badania nad H720 wymagają
sformułowania nowej hipotezy.”

**Rozdzielenie (3 warstwy):**

| Warstwa | Status | Dowód |
|---|---|---|
| Badanie/hipoteza S49 (H720) | Zamknięte | ADR-0001, README: „closed — S49 H720 rejected” |
| Projekt jako zasób badawczy | Active | CONTEXT-MAP grade `active`, kod/ADR-y/dane istnieją |
| Ścieżka nawigacyjna w AGENTS.md | Aktywna (nawigacja) | AGENTS.md linia 12 — nie grade |

**Opcjonalna propozycja (do osobnej decyzji, nie wykonana):** w `README.md`
linia 15 („ETTh1 H720 study is closed”) dodać link do ADR-0001:
`projects/research/etth1-h720/docs/adr/0001-s49-closeout-and-protocol-discrepancies.md`.
Nie wymaga edycji CONTEXT-MAP ani AGENTS.md. Nie wykonuję bez zatwierdzenia.

---

Oba dokumenty są gotowe do zapisu w `docs/`. Zatwierdzasz? (bez commitów, bez zmian w istniejących plikach).