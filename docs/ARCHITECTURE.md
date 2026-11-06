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