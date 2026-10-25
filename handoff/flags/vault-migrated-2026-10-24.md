---
type: Concept
flag: vault-migrated-2026-10-24
since: 2026-10-24
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
title: vault-migrated-2026-10-24
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`vault-migrated-2026-10-24` — 2026-10-24: `Desktop\vault` został single-vault single-repo. `.git` przeniesiony z `root_workspace/` do `vault/`; `root_workspace` jest teraz podfolderem, nie repozytorium. `Notes/` przeniesiony do vaultha; `.smart-env/` istnieje jako pusty katalog w vaulcie (placeholder na future Smart Connections reinstall — plugin nie jest dziś zainstalowany, więc indeks się nie migruje). Nowy `vault/.gitignore` trzyma tylko wpisy vaulta, zagnieżdżony `root_workspace/.gitignore` pozostawiony (wzorce są poprawne względem workspace'u). `archival-697b9e3` i `baseline-59faa7d` w vaulcie, bundle w `Desktop\`. Następne kroki: gh repo create + push, reinstall obsidian-git, clear embeddings.

not checked:
- czy smart_env.json (1 plik, wykluczony) istnieje w `.smart-env/` — plik nie został przeniesiony, tylko usunięty; jeśli istnieje na dysku poza repo, nie został utracony.
- czy `handoff/status/STATUS.md` nie zawiera starej ścieżki `root_workspace` w linkach — wymaga checku po pushu.
