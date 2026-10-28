---
flag: codegraph-routing-claude-rules-2026-10-28
since: 2026-10-28
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`codegraph-routing-claude-rules-2026-10-28` — 2026-10-28: Wpisano regułę nawigacji CodeGraph CLI do `CLAUDE.md` §Rules; zdefiniowano G3 jako DEFERRED orakuł różnicowy.

Stan: Po weryfikacji pomiarowej odrzucono Wariant B (policy file w `instructions` to ~249 tokenów stałego narzutu, brak dowodu behawioralnego w logach na skuteczność `jcodemunch-policy.md`). Zamiast tego zrealizowano Opcję A: regułę wpisano do `CLAUDE.md` §Rules. `scripts/audit_agents_md.py` dotyczy wyłącznie `AGENTS.md`, więc `CLAUDE.md` nie jest objęty blokadą R13. Bramka `check_workspace_integrity.py` pozostaje zielona (`OK: 36 declared entries, 7 projects`). Utworzono ledger `docs/codegraph-routing-GATES.md`: G1 i G2 zweryfikowane (`exit=0`), a G3 (empiryczny dowód spadku blind read i wywołania CLI w sesji etth1-h720) odroczona z jawnym orakłem.

Next: Pierwsza sesja na `etth1-h720` bez podawania słowa `codegraph` w prompcie — weryfikacja G3. Jeśli model nie użyje CLI, wpięcie MCP.

not checked: G3 — deferred to next session owner (sesja badawcza etth1-h720); zachowanie innych harnessów niż opencode.
