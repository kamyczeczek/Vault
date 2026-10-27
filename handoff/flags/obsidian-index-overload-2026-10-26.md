---
type: Concept
flag: obsidian-index-overload-2026-10-26
since: 2026-10-26
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: user request - zdiagnozuj przeciążenie Obsidiana indeksowaniem
title: obsidian-index-overload-2026-10-26
---

`obsidian-index-overload-2026-10-26` — 2026-10-26: przyczyną zadyszki był nie
jeden indeks, a cztery nakładające się przebiegi po całym vaulcie, który po
root-flatten (2026-10-25) jest workspace'em dev: **72 818 plików / 3,27 GB, 26 645 md**,
z czego 23 273 md to dane maszynowe (dwa identyczne korpusy po 10 374 plików
+ 2 525 w `brain/.brain/corpus`), a w środku leżały dwa pliki Repomix
**55,7 MB / 1,05 mln linii** i **27,9 MB**.

Zmiany (żaden plik nie został usunięty):

- `vault_export.md`, `test_export.md`, `scripts/vault_export.md` → `.export/`
  (katalog z kropką; Obsidian nie indeksuje ścieżek zaczynających się od `.`).
  `scripts/export_vault_repomix.bat` domyślnie pisze do `.export\` i wymusza to
  także przy argumencie; `.export/` w `.gitignore`.
- `.obsidian/app.json`: `userIgnoreFilters` = `projects/`, `scripts/_scratch/`,
  `logs/`, `agents/` (ukrywa z grafu/wyszukiwania/properties; **nie** zatrzymuje
  parsowania metadataCache — to ograniczenie Obsidiana).
- `okf-enforcer/data.json`: `scanOnStartup: false`, `fixOnSave: false`,
  `autoGenerateIndex: false`, `excludeFolders` += `projects`, `scripts/_scratch`,
  `logs`, `agents` (wcześniej brak pliku = domyślne, czyli pełna walidacja
  całego vaulta na starcie i zapisy `index.md` w `__pycache__`).
- `ideaverse-maps/data.json`: `exclude` = `projects`, `scripts/_scratch`, `logs`
  (scan-cache miał 23 991 wpisów, w tym 10 374 z korpusu i 12 480 z `_archive`).
- `.smart-env/smart_env.json`: `folder_exclusions` += `projects`, `logs`, `agents`;
  `smart_blocks.embed_blocks: false`; `re_import_wait_time` 13 → 120 s
  (13 s debounce po każdym zapisie = 91 re-importów w 43 h).
- `obsidian-git/data.json`: nowy plik z `autoSaveInterval: 0`,
  `autoPullInterval: 0`, `refreshSourceControlTimer: 60000` (domyślne 7 s
  `git status` po całym drzewie; backup z 10-25 miał auto-commit i auto-pull
  co 10 s).
- `.obsidian/workspace.json`: usunięte panele `all-properties`, `tag`,
  `smart-connections-view`, `smart-env-status-view`; wyczyszczone `lastOpenFiles`.

Czego to **nie** usuwa: Obsidian dalej parsuje 23,3 tys. notatek korpusu przy
każdym starcie (metadataCache nie jest trwały, a „Excluded files" nie wpływa na
parsowanie). Jeśli start ma być krótki, korpusy muszą wyjść z vaulta albo dostać
nazwę z kropką — to zmiana ścieżek w `projects/`, więc osobna decyzja.

Potwierdzone przez użytkownika 2026-10-27 po restarcie aplikacji: indeksowanie
przestało dławić Obsidiana. Zostaje tylko koszt startu (~24 tys. notatek do
sparsowania), nie cykliczne zadyszki w trakcie pracy.

not checked:
- brak profilu CPU przed/po — potwierdzenie jest objawowe („już nie dławi"),
  nie liczbowo; nie mierzono czasu startu ani zużycia RAM.
- `_recovery-2026-10-25` (67,9 MB) i `smart_sources.ajson` (28,7 MB) nietknięte;
  baza Smart Connections nie została wyczyszczona.
