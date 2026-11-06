---
type: Concept
title: STATE
generated: { by: okf-enforcer/0.6, at: 2026-10-25T02:18:55Z }
---

# STATE — root workspace (generated)

> Nie edytuj ręcznie. Przebuduj: `python scripts/build_state.py`. Narracja: `HANDOFF.md`. Stan na: 2026-11-06 23:37 · HEAD `6dd8b6f` (master).

## Drzewo

brudne pliki (11):
- `M  HANDOFF.md`
- `M  STATE.md`
- `M  handoff/decisions/agents-md-agent-commit-ref.md`
- `M  handoff/decisions/bat-files-eol-crlf.md`
- `M  handoff/decisions/dead-script-deletions.md`
- `M  handoff/decisions/history-rewrite-filter-repo.md`
- `M  handoff/decisions/openai-key-rotation.md`
- `M  handoff/decisions/retrieval-v2-preflight.md`
- `A  handoff/flags/vault-simplification-complete-2026-11-06.md`
- `M  handoff/status/NEXT.md`
- `MM handoff/status/STATUS.md`

## Ostatnie commity

- `6dd8b6f fix AGENTS.md agent_commit.py reference to archived path`
- `1ffd95e feat(retrieval-v2): add missing preflight.py (stdlib-only; satisfies AGENTS.md invariant every active project ships a preflight); rebuild MAP.md`
- `87d5ff5 fix(gitattributes): add eol=crlf for raw_sessions.bat, session_brief.bat, session_digest.bat (cmd.exe requires CRLF; same fix as raw_sessions_drive.bat in previous commit)`
- `f69e772 refactor(scripts): remove dead script debug_skill_resources.mjs (debug helper, 0 active callers; caveat ~/.pi config outside repo noted in dead-script-candidates report)`
- `893fe92 refactor(scripts): remove dead script check_kb_layout.py (kb-cleanup tranche 2026-10-29; no active callers, ADR-008 stays as history)`

## Runy (`.dgc-evidence/runs/`)
LATEST (czeka na werdykt): `goose-pstack-2026-10-03`

| run | REVIEW.md | REVIEW.html | werdykt |
|---|---|---|---|
| `goose-pstack-2026-10-03` | — | tak | - |
| `pstack-research-2026-10-03` | tak | tak | PASS |

## Co dalej

- pełny stan + next steps: `HANDOFF.md` (widok z `handoff/flags/`, najwyższa flaga w `## Status`; źródło: `handoff/CONTEXT.md`)
