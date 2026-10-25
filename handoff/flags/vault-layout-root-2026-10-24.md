---
type: Concept
flag: vault-layout-root-2026-10-24
since: 2026-10-24
owner: mateusz
agent: opencode
model: omniroute/gemini/gemini-flash-lite-latest
origin: session-close
title: vault-layout-root-2026-10-24
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`vault-layout-root-2026-10-24` — 2026-10-24: adopt vault = root_workspace layout in ALLOWED_ROOT, CLAUDE.md, and STATUS.md; include pending .gitignore + .smart-env/smart_env.json from prior Smart Connections config session. Removes dead `vault` entry; declares `.obsidian`, `.smart-env`, `Notes` as root entries; rebuilds generated views.

not checked:
- whether `.obsidian/` or `Notes/` should be tracked (left untracked per policy; only root layout allowed in ALLOWED_ROOT).
