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
| `projects/research/` | Research projects |
| `projects/_archive/` | Archived work |
| `scripts/check_workspace_integrity.py` | Workspace gate |
| `hooks/` | Git hooks |

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
