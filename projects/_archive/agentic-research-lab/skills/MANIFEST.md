---
type: Concept
title: MANIFEST
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Skills manifest — agentic-research-lab

This project owns its skills here. The workspace root `../../skills/` is
upstream; this folder is the working copy this project actually resolves against
(D8).

**Resolution order:** this project's `skills/` first, then `../../skills/`. A
skill here shadows the root copy of the same name.

**A vendored skill is never auto-updated.** To refresh one, re-copy it from
`../../skills/<name>/` and bump its date below. Locality is the accepted cost:
an upstream fix does not propagate on its own.

**Note (D8 symmetry):** this project is the heavy skill user (20 vendored);
all other projects vendor lazily and their `skills/` are empty by design
until first use — that is the symmetric rule, not an exception.

## Vendored

All 20 vendored on 2026-09-27, each byte-identical to `../../skills/<name>/`
at copy time (sha256 over the full tree, verified per skill).

| Skill | Vendored | Upstream | Files |
|---|---|---|---|
| `ask-matt` | 2026-09-27 | `../../skills/ask-matt/` | 3 |
| `agent-reach` | 2026-09-27 | `../../skills/agent-reach/` | 7 |
| `code-review` | 2026-09-27 | `../../skills/code-review/` | 2 |
| `codebase-design` | 2026-09-27 | `../../skills/codebase-design/` | 4 |
| `diagnosing-bugs` | 2026-09-27 | `../../skills/diagnosing-bugs/` | 3 |
| `domain-modeling` | 2026-09-27 | `../../skills/domain-modeling/` | 4 |
| `grill-with-docs` | 2026-09-27 | `../../skills/grill-with-docs/` | 2 |
| `icm-architect` | 2026-09-27 | `../../skills/icm-architect/` | 12 |
| `implement` | 2026-09-27 | `../../skills/implement/` | 2 |
| `improve-codebase-architecture` | 2026-09-27 | `../../skills/improve-codebase-architecture/` | 3 |
| `planning-with-files` | 2026-09-27 | `../../skills/planning-with-files/` | 1 |
| `prototype` | 2026-09-27 | `../../skills/prototype/` | 4 |
| `research` | 2026-09-27 | `../../skills/research/` | 2 |
| `tdd` | 2026-09-27 | `../../skills/tdd/` | 4 |
| `to-spec` | 2026-09-27 | `../../skills/to-spec/` | 2 |
| `to-tickets` | 2026-09-27 | `../../skills/to-tickets/` | 2 |
| `triage` | 2026-09-27 | `../../skills/triage/` | 4 |
| `unlazy` | 2026-09-27 | `../../skills/unlazy/` | 29 |
| `wayfinder` | 2026-09-27 | `../../skills/wayfinder/` | 2 |
| `git-guardrails-claude-code` | 2026-09-27 | `../../skills/git-guardrails-claude-code/` | 3 |
| `ralph-loop` | 2026-10-02 (refreshed: small-session contract — `resume`, handoff enforcement, DONE gate block) | `../../skills/ralph-loop/` | 10 |
| `poteto-mode-lite` | 2026-10-03 | local pstack-lite research | 1 |

95 files, 503 KB.

## Known gap — RESOLVED 2026-09-27

`skill_router.py` mapped two intents to archived skills (`wizard`,
`resolving-merge-conflicts`). Both routes dropped; both entries removed from
`local_skills.md` with a retirement note. Merge/conflict and interactive-bash
intents fall through to the `icm-architect` default. Restoring either skill
is a deliberate re-vendor from `../../skills/archive/`, not a repair.

Prior record (kept for provenance): the router mapped `wizard` →
`skills/wizard/` and `merge|conflict|rebase` →
`skills/resolving-merge-conflicts/`, both archived upstream. Decision taken:
drop the routes, not restore the skills.
