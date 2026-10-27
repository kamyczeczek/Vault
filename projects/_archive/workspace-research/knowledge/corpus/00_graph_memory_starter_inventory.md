---
type: Concept
id: 00_graph_memory_starter_inventory
title: "graph-memory-starter — knowledge-graph + RAG memory for AI assistants (source inventory) (part 1/2)"
source: "graph-memory-starter-inventory.md"
tags: [context-engineering, determinism, hooks, knowledge-graph, memory, prompt-engineering, retrieval]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# graph-memory-starter — knowledge-graph + RAG memory for AI assistants (source inventory)

taxonomy: #knowledge-graph #retrieval #memory #hooks #determinism

Repository `github.com/Glitch-Cat-Club/graph-memory-starter` (verified public 2026-09-16),
53 files. Full source dump preserved at
`RESEARCH/2026-09-03_knowledge-architecture-research/graph-memory-starter-full.txt` (2,428
lines) as the lossless provenance payload for this summary.

**Graph half (`src/`).** `schema.sql` = three tables: `entities(id TEXT PK uuid5, name, type,
description, source_doc)`, `relations(source_id, target_id, predicate, source_doc)`,
`aliases(entity_id, alias)`. `build_graph.py` = two-pass deterministic load of
`extraction/*.json`; `entity_id = uuid5(NAMESPACE_OID, f"{type}:{name}")` — "Ops Manager" in
doc 1 and doc 4 resolve to the same node, no ML, no lookup. `recall.py` = pure-SQL recursive
CTE `WALK`; seeds are entities whose name or alias appears in the question via `\b` regex;
k-hops default 3, top_k 8; returns triples plus entity descriptions, because "the conditions
live on the entities, not the edges"; with no seeds it returns `(no memory matches for this
prompt)` — a loud failure, never a guess. `recall_hook.py` = `UserPromptSubmit` hook emitting
`additionalContext`; timing header `memory: N facts recalled in M ms`.

**RAG half (`rag/`).** `build_index.py` chunks on markdown headings to `CHUNK_BUDGET=1600`
chars with `[file § section]` labels (label embedded in the text AND keyword-indexed); FTS5
plus `fastembed` bge-small-en-v1.5 (67 MB, 384-d, L2-normalized, packed as `struct.pack`
float blob). `search.py` = BM25 keyword leg + meaning leg merged by reciprocal rank fusion
k=60. `distil.py` = one `claude -p` call per note producing `source:/questions:/summary:/
rule:/quote:` entries; grounding check is `normalise(quote) not in normalise(body)` → the
entry is dropped and named. Runs in an empty temp dir with `MEMORY_STARTER_CHILD=1` and all
`CLAUDE*` env vars stripped, so the child has no project, settings, or parent hooks. State in
`distilled/.state.json` keyed by note path + sha256.

**Digest half.** `session_end.py` fires on SessionEnd AND PreCompact, filters the transcript in
code (keeps only user/assistant text; drops tool calls, results, file dumps, thinking,
sidechain, meta, compact summaries; strips `<system-reminder>`; cuts to last `max_turns`=30 /
`max_chars`=15000 keeping the END and re-starting at a whole turn), stages to
`digest/pending/<session_id>-<timestamp>.md`, then either spawns `headless_run.py` detached
(`subprocess.DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP` on Windows) or hands it to the next
session's `session_start.py`. All hooks wrap in try/except and `sys.exit(0)` — failure never
blocks; failures land in `digest/log/digest.log`.
