---
type: Concept
title: local_skills
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# Local Skill Routing Rules (`skill_router.py`)

## Core Principle (Workspace Localization)
To ensure the workspace is fully self-contained and reproducible without relying on external or global agent paths, **all skills MUST reside locally within the workspace `skills/` directory**.

## Local Skill Catalog
The skill router (`skill_router.py`) maps task intents strictly to local folders under `skills/`:
1. **`ask-matt`** (`skills/ask-matt/`) — Ask which skill or flow fits your situation. A router over the skills in this repo.
2. **`agent-reach`** (`skills/agent-reach/`) — Internet read layer: 15 platforms via upstream CLIs/APIs.
3. **`code-review`** (`skills/code-review/`) — Review changes since a fixed point along standards and spec axes.
4. **`codebase-design`** (`skills/codebase-design/`) — Deep-module vocabulary; finding deepening opportunities.
5. **`diagnosing-bugs`** (`skills/diagnosing-bugs/`) — Diagnosis loop for hard bugs and performance regressions.
6. **`domain-modeling`** (`skills/domain-modeling/`) — Build/sharpen a project's domain model, write CONTEXT.md, record ADRs.
7. **`grill-with-docs`** (`skills/grill-with-docs/`) — Relentless interview to sharpen a plan while creating ADRs and glossary.
8. **`icm-architect`** (`skills/icm-architect/`) — Design any process/idea/problem into an ICM workspace (Build mode), restructure an existing folder/repo/vault into ICM conventions (Restructure mode), or audit code into a walkable edit map (System map form).
9. **`implement`** (`skills/implement/`) — Implement a piece of work based on a spec or set of tickets.
10. **`improve-codebase-architecture`** (`skills/improve-codebase-architecture/`) — Scan a codebase for deepening opportunities, present as HTML report.
11. **`planning-with-files`** (`skills/planning-with-files/`) — Manus-style persistent file-based planning: task_plan.md, findings.md, progress.md on disk so work survives context loss.
12. **`prototype`** (`skills/prototype/`) — Throwaway prototype to answer a design question.
13. **`research`** (`skills/research/`) — Investigate against primary sources, capture findings as Markdown.
14. **`tdd`** (`skills/tdd/`) — Test-driven development loop and practices.
15. **`to-spec`** (`skills/to-spec/`) — Turn requirements into a specification.
16. **`to-tickets`** (`skills/to-tickets/`) — Break a spec into tracer-bullet tickets with blocking edges.
17. **`triage`** (`skills/triage/`) — Triage incoming issues and bugs through a state machine.
18. **`unlazy`** (`skills/unlazy/`) — Completion discipline for substantial autonomous work: acceptance gates before execution, Depth Tree decomposition, evidence re-verification before reporting.
19. **`wayfinder`** (`skills/wayfinder/`) — Plan work too big for one session as a map of decision tickets.
20. **`git-guardrails-claude-code`** (`skills/git-guardrails-claude-code/`) — Block dangerous git operations with guardrails.
21. **`ralph-loop`** (`skills/ralph-loop/`) — **Default work mode of this project** (see `CLAUDE.md`): human-confirmed, evidence-gated iterations on a decision graph; small resume-safe sessions (one `resume` cold start ≤ 8K tokens, one frontier node, mandatory stamped handoff, controller blocks DONE while gates are unmet; learnings promote into project docs).

Retired 2026-09-27: `resolving-merge-conflicts` and `wizard` were dropped
from routing (both archived upstream in `../../skills/archive/`; restoring
them is a re-vendor, not a fix). Merge/conflict and interactive-bash intents
now fall through to the `icm-architect` default.

## Zero External Reliance
- `skill_router.py` references only local workspace paths and local `.omp` skills.
- No global environment or external CLI tool paths are assumed.

## Maintenance
- This project owns its skills in `skills/` (D8). The root `skills/` is upstream:
  vendor from there on first use, and record the upstream and date in
  `skills/MANIFEST.md`. A vendored copy is never auto-updated — re-vendor
  deliberately and bump the stamp.
- After adding or archiving a skill here, run `python ../../skills/verify_catalog.py`
  to check the root catalog too.
- Archived skills live in `../../skills/archive/` and are excluded from routing.
