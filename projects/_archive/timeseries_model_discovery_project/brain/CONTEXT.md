---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# brain/CONTEXT.md — Unified Brain Folder

## Purpose
Single root for project knowledge, graph index, and worker auto-injection assets.

## Structure

| Path | Role |
|---|---|
| `brain/internal/` | Brain implementation files: corpus, DBs, indices, scripts |
| `brain/worker/` | Isolated worker cwd with auto-injecting extension |
| `brain/CONTEXT.md` | This file — unified brain contract |

## Subfolder contracts

### brain/internal
- Source of truth for all brain data
- Contains: `corpus/`, `graph.db`, `rag.db`, `reflection_index.json`, `skills_index.json`, `digest.md`
- Scripts: `ask.py`, `verify_sync.py`, `build_reflection_index.py`, `gen_digest.py`
- All queries run from this folder or resolve module-relative

### brain/worker
- Worker cwd for `--cwd brain/worker` sessions
- Auto-injects scar digest + deterministic query commands via `.omp/extensions/ts-brain.ts`
- Main orchestrator does NOT receive automatic injection
- Worker resolves brain assets module-relative: `../internal/...`

## Routing

From `AGENTS.md`:
- Graph knowledge base → `brain/`
- Isolated ts-brain worker → `brain/worker/`

## Invariants

1. `brain/internal/` is the single source of truth for all brain data
2. Worker extension at `brain/worker/.omp/extensions/ts-brain.ts` is opt-in only
3. Main orchestrator agent MUST NOT receive automatic brain injection
4. After any change to brain structure, update routing in `AGENTS.md` and `PROCESS/WORKFLOW.md`
