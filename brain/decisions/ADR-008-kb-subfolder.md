---
type: Concept
title: ADR-008-kb-subfolder
---

# ADR-008: `kb/` jest podfolderem repo — wiedza schodzi pod workspace, nie nad niego

## Status

Accepted (2026-10-29). **Supersedes ADR-006** in full — the one-vault/one-repo
decision stands, but the boundary moves from above the workspace to `kb/` below it.

> Numeracja: polecenie brzmiało „ADR-007", ale `ADR-007-git-baseline-and-remote`
> już istnieje i opisuje inną decyzję. Przepisanie historii byłoby gorsze niż
> przesunięcie numeru, więc nowy ADR to 008.

## Kontekst

ADR-006 zrobił `Desktop\vault` jednocześnie vaultem i rootem repo, a workspace
wepchnął do podfolderu `root_workspace`. Flaga `vault-root-flatten-2026-10-25`
spłaszczyła ten podfolder, więc od 2026-10-25 root repo jest workspace'em — i
przez to `.obsidian/`, `.smart-env/`, `Notes/` i `library/` leżą w tym samym
katalogu co `scripts/`, `hooks/`, `skills/`, `.agents/`, `.opencode/` i `projects/`.

Skutek jest mierzalny: graf i embeddingi Obsidiana obejmują maszynerię agenta.
Dwie warstwy o przeciwnych cyklach życia (wiedza czytana przez człowieka vs kod
uruchamiany przez agenta) dzielą jeden katalog, więc każda zmiana w `projects/`
jest kandydatem do indeksu, a każdy pełny przebieg indeksujący jest kosztem
ponoszonym za pliki, których nikt nie czyta.

ADR-006 rozwiązywał inny problem (jeden vault, jedno repo) i robił to poprawnie.
Błędem było tylko **położenie** granicy: wiedza wyszła nad workspace zamiast zejść
pod niego.

## Decyzja

1. **Root repo zostaje `Desktop\vault`.** Bez zmiany nazwy, bez przenoszenia
   `.git`. Workspace jest rootem repo — to się nie zmienia.
2. **Wiedza schodzi do `kb/`.** Cztery katalogi, które czyta Obsidian i człowiek,
   mieszkają odtąd w `kb/`: `.obsidian`, `.smart-env`, `Notes`, `library`.
   Vault Obsidiana otwiera się na `kb/`, nie na root.
3. **Nazwa to `kb/`, nie `vault/`.** `Desktop\vault\vault` myliłoby się z rootem,
   a zmienna `VAULT` w `check_workspace_integrity.py` wskazywałaby katalog o tej
   samej nazwie co repo.
4. **`brain/` zostaje poza `kb/`.** To pamięć maszynowa (`brain.db` + warstwa
   kuratorska) zapisywana przez `ingest_brain.py`, `retrieval_v1.py` i `brain.py`,
   a nie notatki do czytania. Ewentualne przeniesienie do `.runtime/` to osobna
   decyzja, nie ten commit.
5. **Cztery pliki wiedzy zostają w roocie.** `DECISIONS.md`, `SCARS.md`,
   `PHILOSOPHY.md`, `GLOSSARY.md` mają odwołania w kodzie startowym sesji
   (`build_context_txt.py`, `brain.py`, `ingest_brain.py`, `memory_index.py`,
   R20/R21 bramki), więc przeniesienie ich byłoby zmianą routera, nie porządkami.
6. **R1b zmienia polaryzację.** `VAULT_OWNED = {.obsidian, .smart-env, Notes,
   library}` musi istnieć **w `kb/` i nigdzie indziej**; `.git` przechodzi do
   `ROOT_OWNED` (musi być w root i nigdy w `kb/`).
7. **Wzorce `.gitignore` z ukośnikiem dostają prefiks `kb/`.** Wzorzec zawierający
   `/` jest rozstrzygany względem katalogu pliku `.gitignore`, więc
   `.obsidian/workspace.json` przestałby cokolwiek ignorować po przeniesieniu.
8. **Zakres tego kroku jest wąski.** To nie jest „osobne repo dla harnessu",
   nie jest to `.runtime/` i nie jest to zmiana nazwy roota na `workspace/`.
   Każdy z tych kroków jest osobną decyzją i osobnym commitem.

## Konsekwencje

- **Odciążenie Obsidiana jest strukturalne, nie objawowe.** Graf, wyszukiwanie,
  properties, Smart Connections i pluginy skanują `kb/`, a nie `projects/`.
- **Ścieżka vaulta się zmienia.** Obsidian trzeba otworzyć ponownie na `kb/`;
  `.obsidian/workspace.json` jest per-maszyna i gitignored, więc świeży klon ma
  stan domyślny do chwili pierwszego otwarcia.
- **`.smart-env` nie jest migrowane.** Indeks embeddingów jest odtwarzalny, a jego
  klucze (`Notes/...`) są zapisane względem starego roota; po przeniesieniu i tak
  wymaga reindeksu. Zostaje tylko `smart_env.json`.
- **Wszystkie ścieżki w kodzie są jawnie `kb/`-owe.** Nie ma aliasu ani fallbacku
  na starą lokalizację: cichy fallback sprawiłby, że bramka `check_kb_layout.py`
  przestałaby cokolwiek znaczyć.
- **Historia zostaje historią.** `handoff/`, `docs/reviews/` i wcześniejsze ADR-y
  dalej mówią o `Notes/` i `.obsidian/` w roocie — to zapis stanu z dnia, w którym
  powstały. Bramka skanuje wyłącznie powierzchnie żywe.
- **Granica dostępu się nie zmienia.** Agent w roocie nadal widzi `kb/`; separację
  daje cwd sesji (`projects/<x>`) i `close.py --include`, nie zagnieżdżenie katalogu.

## Weryfikacja

- `python.exe scripts/check_workspace_integrity.py` → exit 0.
- `python.exe scripts/check_kb_layout.py --layout --stale` → `KB-LAYOUT OK · KB-STALE OK`,
  z negatywną kontrolą `--selftest`.
- `python.exe scripts/test_gate_allowlist_parity.py` → SUCCESS (wiersze `kb/`).
- `git log --diff-filter=R -1 --name-status` → cztery katalogi jako rename'y do `kb/`.

## Not checked

- Ręczne otwarcie `kb/` w Obsidianie i reindeks Smart Connections — poza sesją.
- Zachowanie wtyczek, które zapisywały ścieżki względem starego roota vaulta.
