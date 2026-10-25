---
type: Concept
flag: codex-loader-2026-10-24
since: 2026-10-24
owner: mateusz
agent: codex
model: cx/gpt-5.6-luna-max
origin: scripts/agent_sessions.py and scripts/extract_did.py
title: codex-loader-2026-10-24
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`codex-loader-2026-10-24` — 2026-10-24: `scripts/agent_sessions.py` rozszerza loader o Codex Desktop (`~/.codex/sessions/`, JSONL + Zstandard fallback), `scripts/extract_did.py` zachowuje wiadomości/narzędzia/outputs z Codex, `scripts/did_sessions.bat` domyślnie zlicza 5 sesji zamiast 1. Test `test_agent_sessions.py` zielony; failure na Hermes DB jest ignorowany zamiast przerywać eksport. Również w `agent_sessions.py`: zabezpieczono `HERMES_DB.exists()` przed OSError — bez tego uprawnieniowy błąd na niektórych maszynach przerywałby cały loader. `codex` dodany do `SUPPORTED_AGENTS`.

not checked:
- czy pliki `.jsonl.zst` z Codex mają pełny schemat sesji (opencode-style) — wymaga audytu przykładowego pliku na maszynie właściciela.
- czy `extract_did.py` obsługuje zrosty z wieloma plikami w jednej sesji — nie testowano przypadku, w którym jeden dzień ma >1 rollout.
