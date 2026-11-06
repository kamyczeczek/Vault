---
type: Concept
title: CLAUDE
generated: { by: omp, at: 2026-11-06 }
---

# CLAUDE.md — workspace

Root catalog. Read `AGENTS.md` first for routing and `HANDOFF.md` for current state.

## Where things live

| Path | Role |
|---|---|
| `AGENTS.md` | Root L0 router |
| `README.md` | Human entry point |
| `CONTEXT-MAP.md` | Portfolio map |
| `DECISIONS.md` | Decision record |
| `HANDOFF.md` | Active generated state |
| `STATE.md` | Generated workspace snapshot |
| `projects/` | Research projects and archive |
| `scripts/` | Workspace automation and gates |
| `skills/` | Shared agent skills |
| `tools/` | Small workspace tools |
| `agents/` | Agent registry and tooling |
| `hooks/` | Git hooks |
| `handoff/` | Flags and handoff source state |
| `docs/` | Workspace audit reports |
| `brain/` | Curated brain layer |
| `wayfinder/` | Wayfinder state and resources |
| `logs/` | Workspace logs |
| `kb/` | Knowledge layer |
| `SCARS.md` | Operational scars |
| `TASKS.md` | Workspace task list |
| `PLAN.md` | Workspace plan |
| `GATES.md` | Gate reference |
| `GLOSSARY.md` | Term definitions |
| `PHILOSOPHY.md` | Workspace principles |
| `TOOLS.md` | Tool grading bar |
| `TOKEN-EFFICIENCY.md` | Token and cache evidence |
| `.gitignore` | Ignore rules |
| `.gitattributes` | Git attributes |
| `.pi/` | Pi runtime configuration |
| `.omp/` | Oh My Pi configuration |
| `.opencode/` | OpenCode project configuration |
| `.agents/` | Goose lifecycle plugins |
| `.forge/` | Forge policy and runtime state |
| `.ralph/` | Ralph generated projection |
| `.dgc-evidence/` | Review evidence products |
| `.export/` | Generated Repomix exports |
| `WORKFLOW_GOOSE_ICM.md` | Goose ICM design |
| `.commit-approved` | Temporary commit approval token |
| `logs/` | Workspace runtime logs |

## Projects

| Project | Entry |
|---|---|
| `projects/research/benchmark-core/` | `projects/research/benchmark-core/CLAUDE.md` |
| `projects/research/knowledge-retrieval/` | `projects/research/knowledge-retrieval/CLAUDE.md` |
| `projects/research/etth1-h720/` | `projects/research/etth1-h720/CLAUDE.md` |
| `projects/research/research-engine/` | `projects/research/research-engine/CLAUDE.md` |
| `projects/research/brain/` | `projects/research/brain/CLAUDE.md` |

## Rules

- Root routes; project files own project detail.
- Generated views: run their builder, never hand-edit.
- New root entries require declaration here and in `ALLOWED_ROOT`.
