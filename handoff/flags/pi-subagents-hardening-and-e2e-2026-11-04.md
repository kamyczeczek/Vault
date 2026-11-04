---
flag: pi-subagents-hardening-and-e2e-2026-11-04
since: 2026-11-04
owner: mateusz
agent: opencode
model: omniroute/agy/gemini-3.8-flash-low
origin: session-close
---

`pi-subagents-hardening-and-e2e-2026-11-04` — 2026-11-04: Hardened preflight_agent.py (read-only by default, --clean-stale-locks explicit flag, active git process protection before removing index.lock, git hook configuration check HOOK_ACTIVE/HOOK_INACTIVE). Updated CLAUDE.md to resolve gate caller contradiction and updated .pi/agents definitions for preflight-runner and handoff-closer. Added support in close.py for multiple --include flags. Added unit tests in test_preflight_agent.py (9/9 pass) and created hermetic E2E test in test_handoff_closer_e2e.py verifying dirty tree stray detection and full transaction execution. Subagent handoff-closer live run verified.
not checked: —
