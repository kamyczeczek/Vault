---
type: Concept
flag: vault-root-flatten-2026-10-25
since: 2026-10-25
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
title: vault-root-flatten-2026-10-25
generated: { by: okf-enforcer/0.6, at: 2026-10-25T20:37:28Z }
---

`vault-root-flatten-2026-10-25` — 2026-10-25: zawartość `root_workspace/` była
już przeniesiona do korzenia repo **na dysku**, ale nie w indeksie: HEAD trzymał
cały vault pod prefiksem `root_workspace/`, a korzeń miał te same pliki jako
nieśledzone. Ten commit zapisuje przeniesienie: 866 wpisów, z czego 577 to
czyste rename'y (`R100`, `root_workspace/X → X`), 148 dodatków i 135 usunięć;
dla każdego z 30 wpisów najwyższego poziomu `missing=0` (porównanie
`git ls-files root_workspace` z dyskiem). Dopóki tego nie było, `git status`
pokazywał ~1000 wpisów, a `close.py` odmawiał **każdego** commita na `[stage]`
z listą 711 usunięć.

Konsekwencja, której nie da się rozdzielić: **`handoff/` wchodzi do repo
w całości** — 325 plików, z czego śledzone były 3. Usunięcie
`root_workspace/handoff/*` bez dodania `handoff/*` wykasowałoby te pliki z HEAD
bez odpowiednika, więc „handoff jako osobna sesja" jest nierozłączny od
spłaszczenia. To domyka lukę z raportu: bez tego żadna deklaracja „domknięte" nie
jest weryfikowalna ze świeżego klonu.

**Blokada, która wymusiła zmianę `.gitignore`.** `close.py` nie umie wyrazić
katalogu, którego *wszystkie* śledzone pliki są usunięte: `git add --
root_workspace` kończy się `fatal: pathspec 'root_workspace' did not match any
files` (git nie dopasowuje pathspecca do katalogu nieistniejącego na dysku; to
samo `-A`/`-u`). `find_strays` dodatkowo nie rozumie linii `R  a -> b`, więc 577
rename'ów byłoby strayami niezależnie od `--include`. Jedyna sankcjonowana droga
dla migracji strukturalnej to `--include .` (flaga
`close-include-whole-tree-2026-10-24`), ale ona robi `git add -- .`, a w drzewie
było `projects/` = 67 720 plików / 2,4 GB i `library/` = 225 MB. Dlatego ten
commit dodaje 11 reguł ignore dla tego, co **nigdy** nie jest treścią vaulta:
`projects/` (niezmiennik, który close.py deklarował tylko w komunikacie błędu),
`library/`, `agents/backup/`, `brain/*.db*`, `tools/out/`, `logs/`, `.pi/`, kopie
`.obsidian/{repair-backup,plugins.disabled}-*` / `*.bak-*`, `scan-cache.json`.
`library/` (225 MB PDF-ów) zostaje **wyłącznie na dysku** — to świadoma decyzja,
nie przeoczenie: wersjonowanie tych plików wymaga LFS albo backupu poza gitem.

Weszły też 4 pliki lokalnego stanu aplikacji, bo blokowały commit jako strays:
`.obsidian/community-plugins.json`, `.obsidian/plugins/obsidian-git/data.json`,
`.obsidian/plugins/smart-connections/data.json`, `.smart-env/smart_env.json`
(oraz plugin `ideaverse-maps`, 10 MB — inne pluginy są śledzone, więc dla
spójności ten też). Next: close z re-runem benchmarku pod pinem `85038826`,
potem commit 2 (migracja 5 notatek do `sources: [{file, lines}]`).

not checked: `--include .` **wyłącza sprawdzanie strayów w całości** — to
udokumentowane zachowanie tej flagi, ale znaczy, że ten commit nie dowodzi
„nic obcego się nie wciągnęło" poza tym, co sam sprawdziłem (866 wpisów
obejrzanych przez `git diff --cached --shortstat` i listę `??` przed commitem).
Nie naprawiono `close.py` — błąd z `git add -- <usunięty katalog>` i z liniami
`R  a -> b` w `find_strays` nadal tam jest i wróci przy następnej migracji; to
kandydat na osobny commit i scar. Nie sprawdzono, ile z 711 par jest bajtowo
identycznych (próbka: `AGENTS.md` identyczny, `handoff/flags/T101.md` różny).
Nie pushowano — `master` wyprzedza `origin/master` o 8 commitów. Nie ruszono
trybu `scoped`, gate'u cytowań, migracji 5 notatek, Q02/Q20, 10 passage'ów
`related`, ani otwartej decyzji o `CONTEXT.md` w `raw_only`.
