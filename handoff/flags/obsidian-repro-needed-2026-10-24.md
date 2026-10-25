---
type: Concept
flag: obsidian-repro-needed-2026-10-24
since: 2026-10-24
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
title: obsidian-repro-needed-2026-10-24
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`obsidian-repro-needed-2026-10-24` — 2026-10-24: trzy awarie po stronie Obsidiana są **nadal niepotwierdzone** i nie są „naprawione”. (1) Grey screen (sesje 6, 8): krok odtworzenia — otworzyć `Desktop\vault` w Obsidianie, otworzyć notatkę i graf, sprawdzić, czy renderuje; przegląd 2026-10-31, właściciel Mateusz. (2) Hybrid Search „server did not start” (sesja 8): odtworzyć przy zainstalowanym pluginie i wkleić pierwszy błąd z konsoli deweloperskiej; ten sam przegląd. (3) Fine-grained PAT → HTTP 403 przy Obsidian Git (sesja 24): odtworzyć **po** reinstalacji obsidian-git — dziś nie ma gdzie, bo w żadnym z dwóch vaultów nie istnieje katalog `plugins/`; klasyczny PAT działa, fine-grained nie, przyczyna nieznana.

Stan poza repo, posprzątany w tej sesji (bez commita, bo to nie pliki repo): usunięty martwy wpis MCP `smart-connections` z `~/.config/opencode/opencode.jsonc` (wskazywał na nieistniejący `vault\.obsidian\plugins\smart-connections\main.js`); `~/.pi/agent/trust.json` ma teraz tylko bieżącą ścieżkę `Desktop\vault\root_workspace` (usunięte `Desktop\root_workspace` i literówka `root_worksapce`); usunięty osierocony worktree `kilo/worktree-pool/.../catnip-mantis` (3,8 MB, 565 plików, `.git` wskazywał na nieistniejące `Desktop\root_workspace`); usunięte `handoff/state_description/` (32,4 MB, 79 plików, w pełni pochodne); obie instalacje opencode to 2.1.4 — rozjazd wersji zniknął sam, hermes wygrywa PATH.

not checked:
- cztery rzekome błędy w `session_ground_truth.py` — narzędzie odpowiada na `--help`, ścieżka w docstringu poprawiona w miejscu, ale plik jest pod `scripts/_scratch/*` (gitignored), więc poprawka nie ma commita i nie jest wersjonowana.
- `~/.config/opencode/opencode.jsonc` ma uszkodzoną strukturę w bloku `nara` (dwa klucze `"models"`, wiszący przecinek) — nie naprawiane, bo to nie dotyczy tej sesji; jeśli opencode parsuje plik luźno, część providerów może nie działać.
- czy grey screen wraca po migracji vaulta — wymaga GUI, data przeglądu wyżej.
