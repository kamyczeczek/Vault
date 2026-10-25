---
type: Concept
flag: obsidian-vault-2026-10-22
since: 2026-10-22
owner: opencode
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: user request - skonfiguruj Obsidian z GitHub
title: obsidian-vault-2026-10-22
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`obsidian-vault-2026-10-22` — 2026-10-22: vault Obsidiana zbudowany jako podfolder
`vault/` z własnym repo git (nie nestowany w root repo — `/vault/` w `.gitignore`
roota). Plugin Obsidian Git 2.42.0 preinstalowany w `.obsidian/plugins/obsidian-git/`
z `data.json` (auto-save/pull 10 min, `gitPath` → hermes git).

- Sync: prywatne repo GitHub <https://github.com/kamyczeczek/obsidian-vault> (konto
  `kamyczeczek`, gh device-flow), push przez Git Credential Manager.
- Zrobione: `gh auth login` zalogowany, repo utworzone jako PRIVATE z
  `--source vault --push`, `main` śledzi `origin/main`. Plugin Obsidian Git działa
  na żywo — trzy auto-commity z szablonu `vault: {{date}} {{hostname}}`
  (19:58, 20:05) i notatki `123.md`/`124.md` już na remote.
- Zostaje: nic po stronie workspace'u. Vault otwiera się jako
  `C:\Users\Mateusz\Desktop\root_workspace\vault`.
- Mobile (2026-10-22): Obsidian + Obsidian Git, clone do pustego vaulta działa po
  **classic PAT ze scope `repo`**; fine-grained token dawał HTTP 403 (uprawnienia/
  forma uwierzytelnienia — nie diagnozowane dalej). Token trzymany w localStorage
  apki, nie w repo.

not checked:
- czy drugie urządzenie (mobile/desktop) poprawnie sklonuje vault — test sync
  jednostronny, tylko z tej maszyny.
- czy konflikt przy równoległej edycji dwóch urządzeń rozwiązuje się bez utraty
  notatek — nietestowane.
