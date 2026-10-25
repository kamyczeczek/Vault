---
type: Concept
flag: vault-single-repo-2026-10-24
since: 2026-10-24
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
title: vault-single-repo-2026-10-24
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`vault-single-repo-2026-10-24` — 2026-10-24: rozstrzygnięty spór o root vaulta. `Desktop\vault` jest jedynym vaultem i jedynym repo; `root_workspace` staje się podfolderem bez własnego `.git`. Cztery wpisy (`.git`, `.obsidian`, `.smart-env`, `Notes`) są vault-owned i bramka egzekwuje dla nich XOR między `ROOT` i `VAULT`. `Notes/` będzie trackowane w prywatnym repo (`kamyczeczek/vault`), `.smart-env/` odtwarzane od nowa, zagnieżdżony `.gitignore` zostaje. Historia: `59faa7d` przyjęty jako baseline, `697b9e3` tagowany jako `archival-697b9e3` **przed** bundle'em. Decyzje: `brain/decisions/ADR-006-single-vault-single-repo.md`, `ADR-007-git-baseline-and-remote.md`. Kolejne kroki: gate XOR (osobny commit), `_repo_rel()` w `scripts/` przed migracją, migracja jako ostatni commit, `gh repo create --push`.

not checked:
- czy `Desktop\ARCHIVE\ROOT` zawiera cokolwiek, czego nie ma w `59faa7d` — nie porównywano; przyjęto, że to starszy, inny workspace.
- czy `Notes/` nie zawiera materiału, którego właściciel nie chce w prywatnym repo — decyzja właściciela: trackowane.
- czy plugin Smart Connections da się zainstalować w tym vaulcie — w żadnym z dwóch vaultów nie ma katalogu `plugins/`, więc `.smart-env/` jest dziś sierotą.
