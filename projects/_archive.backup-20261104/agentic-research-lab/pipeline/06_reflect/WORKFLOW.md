---
type: Concept
title: WORKFLOW
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Reflection Workflow — Deterministic ICM Routing

Subagent-based reflection over the Workspace-Research knowledge graph. The agent is
**auto-injected** with the graph digest (via `.omp/extensions/workspace-research.ts`,
`before_agent_start`), so it reasons over the derived index, never free recall. Routing
is **deterministic**: topic tags → exact tag-intersection query → fixed chunk-id set →
cited outputs. Identical corpus ⇒ identical digest ⇒ identical routing surface.

## Invariants (ICM)
1. **Source of truth = corpus markdown.** Graph is a pure function of corpus; fingerprint
   = `sha256` over all `knowledge/corpus/*.md` bytes (`.graph_fingerprint`).
2. **Auto-injection only.** Context reaches the agent via the digest, never pasted by hand.
3. **Routing is a query, not a guess.** Tags in `knowledge/topics.md` are the routing keys;
   `ask.py --tag` returns the exact intersection set.
4. **Write-only sink.** Reflection writes to `reflection/{digests,candidates}/` only; never
   edits source or corpus.
5. **Every claim cites a chunk id.** No citation ⇒ rejected.

## Steps

### 0. Determinism gate (refresh the brain)
```bash
python knowledge/graph/watch.py --once
```
Rebuilds the graph **only if** corpus bytes changed; otherwise no-op. The digest the
agent receives is therefore exactly the derived index of the current corpus. Record the
new fingerprint if it rebuilt.

### 1. Pick topic(s) from the controlled vocabulary
`knowledge/topics.md` lists the ICM tags (e.g. `icm`, `determinism`, `reflection`,
`context-engineering`, `anti-leakage`). A topic maps to ≥1 tag — this is the routing key.

### 2. Spawn the reflection subagent (auto-injection)
```bash
python pipeline/06_reflect/spawn.py --topic <slug>
```
`spawn.py` launches `omp launch` with `--extension workspace-research`, which injects
`GRAPH-DIGEST.md` + topics + open candidates into the agent's system prompt. The agent
is isolated, read-only on source.

### 3. Deterministic routing *inside* the agent (mandated contract)
The injected prompt forces this procedure:
1. For each topic tag set, run exact intersection:
   ```bash
   python knowledge/graph/ask.py --tag <tag1> --tag <tag2> --limit 12
   ```
   Returns the reproducible chunk-id set sharing ALL tags (ordered by id ⇒ stable).
2. Optionally expand a top chunk via graph edges (`REFERS_TO`, `SHARES_TAG` in `graph.db`).
3. Every reflection claim cites ≥1 returned chunk id. No citations ⇒ rejected.

### 4. Structured outputs
- `reflection/digests/<topic>.md` — `Claim / Evidence (chunk-id citations) / Decision / Next bet`.
- `reflection/candidates/<topic>.jsonl` — one object per candidate:
  `{"id", "state": "proposed"→"experimental"→"accepted"|"rejected", "claim", "evidence":[chunk_ids], "bet"}`.

### 5. Closure check
Agent verifies cited chunk ids exist (`ask.py "<id>"`), then a `git` checkpoint captures
digest fingerprint + reflection outputs.

## Determinism argument
- Graph = f(corpus) via hash-gated `build_graph.py`.
- Injection = same digest every run (`.graph_fingerprint` gate).
- Routing = `ask.py --tag` intersection = f(topic tags, digest) ⇒ reproducible.
- Output = fixed schema ⇒ no free-form divergence.

## Reference
- Brain query: `knowledge/graph/ask.py "<q>" [--tag T ...] [--limit N] [--raw]`
- Rebuild:    `knowledge/graph/build_graph.py`
- Watch gate: `knowledge/graph/watch.py --once`
- Spawn:      `pipeline/06_reflect/spawn.py --topic <slug>`
- Extension:  `.omp/extensions/workspace-research.ts`
