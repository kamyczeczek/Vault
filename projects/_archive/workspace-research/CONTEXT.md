---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CONTEXT.md — workspace-research

## Purpose
Maintain a deterministic, graph-backed knowledge base on context engineering, ICM rules,
and agent/workspace design. Replicates the proven `ts-research` architecture.

## Operating contract
- **Read path:** agents load context from `knowledge/graph/GRAPH-DIGEST.md` (auto-injected by
  `.omp/extensions/workspace-research.ts` at `before_agent_start`).
- **Write path:** new knowledge enters only via `INBOX/` → `scripts/ingest.py` → `knowledge/corpus/`.
  Never hand-edit `knowledge/graph/graph.db`, `GRAPH-DIGEST.md`, or `graph_index.json`.
- **Refresh:** after any corpus change run `python knowledge/graph/build_graph.py` (also wired to
  `watch.py --once` for git hooks).
- **Reflection:** `pipeline/06_reflect/spawn.py` spawns an isolated agent that reads the graph and
  writes only to `reflection/{candidates,digests}/`.

## Daily handoff
- Newest entry at the top.
- Format: `YYYY-MM-DD HH:MM — <3 bullets, session owner, next action>`.
- This block is the session handoff; read it before any other work.

### 2026-09-19 11:38 — Antigravity Agent
- Re-stamped reflection outputs with `check_reflection.py --replan` to live corpus fingerprint `e98956233d64` (12 digests, 74 candidate rows).
- Deposited web research findings from artifacts 11–14 into `INBOX/` (WorldEvolver/world models, Plan compliance/RefineAct/APB, ChatHTN/PDDL) and ingested via `scripts/ingest.py` (corpus grew to 652 chunks, graph rebuilt with 652 nodes and 207,841 edges).
- Added `Route table by intent` to `CLAUDE.md`. Full audit scorecard passes 10/10 checks (`scripts/audit_workspace.py`).
- Next action: spawn new topic reflections on ingested planning and world-model topics as needed.


## Chunk contract (`knowledge/corpus/NN_slug.md`)
```
---
id: NN_slug
title: "Human Title"
source: "original filename"
tags: [context-engineering, icm, ...]
---

# Body (indexed by FTS5 for content retrieval)
```
- `id` is unique; multiple sections of one source share the `NN_` prefix with `part` in title.
- `tags` drive `SHARES_TAG` edges in the graph and topic registration in `knowledge/topics.md`.

## Failure modes to avoid (from sibling projects)
- Stale digest: always rebuild after corpus edits; `watch.py` guards commits.
- Context drift: do not paste knowledge into system prompts by hand — route through the graph.
- INBOX rot: ingestion must empty `INBOX/` into `knowledge/raw/`; leaving raw items violates intake.
