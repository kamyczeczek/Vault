---
type: Concept
flag: close-include-whole-tree-2026-10-24
since: 2026-10-24
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
title: close-include-whole-tree-2026-10-24
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`close-include-whole-tree-2026-10-24` — 2026-10-24: `close.py --include` rozumie katalog i całe drzewo. `find_strays` dopasowuje zawartość katalogu po prefiksie (bez rozwijania 686 ścieżek w jeden argv) oraz traktuje `.` jako „cały workspace jest zmianą" — jawnie, nie po cichu: to jedyny sposób, w jaki strukturalna migracja (przeniesienie `.git`, rename 686 plików) może przejść przez transakcję close bez ręcznego mintowania `.commit-approved` (S86). Domyślne zachowanie bez `--include` / z listą plików jest bez zmian — stray nadal blokuje commit. Test w `scripts/test_git_paths.py` buduje repo w tempie: bez `--include` → 2 strays, `--include .` → 0, `--include sub` → tylko plik poza katalogiem.

not checked:
- `--include .` w realnej migracji — sprawdzony dopiero w commicie migracyjnym; jeśli stray pojawi się mimo to, commit padnie i to jest poprawne zachowanie.
- czy `git add --intent-to-add .` jest potrzebny (S67 dotyczy untracked plików, nie katalogów) — nie testowano na katalogu z untracked treścią.
