---
flag: smart-connections-cache-exclusions-2026-10-25
since: 2026-10-25
owner: mateusz
agent: codex
model: openai/gpt-5
origin: user-requested Smart Connections startup fix
---

`smart-connections-cache-exclusions-2026-10-25` — 2026-10-25: corrected Smart Connections folder exclusions for the active vault root by adding the root-level `scripts/`, `projects/`, and `handoff/` paths while preserving the legacy `root_workspace/` paths. Because the old cache continued to load excluded entries, the derived `smart_sources`, `smart_blocks`, `embedding_models`, and `event_logs` directories were moved to `.smart-env/_recovery-2026-10-25`; notes and `smart_env.json` were preserved. Next step: reopen Obsidian and allow Smart Connections to rebuild with the corrected scope.
