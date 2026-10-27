---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Stage 03_graph — Derived brain

Derived brain — pure function of corpus (hash-gated).

## Inputs
- `knowledge/corpus/*.md`

## Outputs
- `knowledge/graph/graph.db`
- `knowledge/graph/GRAPH-DIGEST.md`
- `knowledge/graph/graph_index.json`
- `knowledge/graph/.graph_fingerprint`

## Invoke
```
python knowledge/graph/build_graph.py  or  python knowledge/graph/watch.py --once
```

## Contract
- Determinism: run is a no-op if the corpus fingerprint is unchanged. The live value is
  what this stage itself writes to `knowledge/graph/.graph_fingerprint`; read it from
  there or from `GRAPH-DIGEST.md` line 1 — `0626262b2982` at the time of writing, but it
  moves on every corpus edit, so never hardcode it here. A contract that quotes a stale
  fingerprint silently describes a graph that no longer exists.
- This stage's CONTEXT.md is the Inputs Table — the single disclosure level (one-level progressive disclosure).

## Handoff
Next stage consumes Outputs above via its own Inputs Table. The `.graph_fingerprint` + `GRAPH-DIGEST.md` fingerprint is the explicit handoff artifact for stage 03.
