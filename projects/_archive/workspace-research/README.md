---
type: Concept
title: README
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# Workspace-Research

Knowledge base for **context engineering, ICM (Interpretable Context Methodology) rules, and agent/workspace design** — built on the same proven pattern as `ts-research` (corpus markdown as source of truth → derived graph brain → auto-injected into agents → spawned reflection).

## What it is
A self-contained knowledge project. Raw research (PDFs, notes, the `ICM_knowledge_big.md` dump) lands in `INBOX/`, gets ingested into front-matter markdown chunks in `knowledge/corpus/`, and is indexed into an FTS5 SQLite graph (`knowledge/graph/`). Every worker agent is auto-injected with the graph digest at start; a spawned reflection agent reasons over the graph and writes to `reflection/`.

## Layout
- `INBOX/` — raw seed material (PDFs, markdown, notes). Consumed by `scripts/ingest.py`.
- `knowledge/raw/` — archived originals after ingestion (deterministic cleanup).
- `knowledge/corpus/` — **canonical knowledge chunks** (front-matter: id/title/source/tags). Source of truth.
- `knowledge/graph/` — derived graph DB + digest + `ask.py` + `watch.py` + `build_graph.py`. Never hand-edited.
- `knowledge/topics.md` — topic vocabulary for retrieval/registration.
- `reflection/` — `candidates/` + `digests/` (reflection agent writes here only).
- `pipeline/06_reflect/spawn.py` — spawn graph-injected reflection agent.
- `.omp/extensions/workspace-research.ts` — worker extension: auto-injects graph + corpus.
- `scripts/ingest.py` — INBOX → corpus chunking.

## Quick start
```bash
# ingest raw INBOX material into corpus chunks
python scripts/ingest.py

# index corpus into the graph + write GRAPH-DIGEST.md
python knowledge/graph/build_graph.py

# query the brain
python knowledge/graph/ask.py "ICM determinism rules"

# keep graph fresh on commit (hash-gated, no-op if unchanged)
python knowledge/graph/watch.py --once

# spawn reflection agent (auto-injects graph digest)
python pipeline/06_reflect/spawn.py
```

## ICM rules (non-negotiable)
1. **Knowledge as files** — findings are markdown chunks; the graph brain is a derived index.
2. **Single source of truth** — corpus markdown; `build_graph.py` regenerates all derived state.
3. **Determinism** — corpus content drives the graph; identical corpus ⇒ identical graph.
4. **Graph backbone** — all agent context derived from the knowledge graph.
5. **Reflection is spawned** — isolated agent, graph-injected, writes to `reflection/` only.
6. **Clean intake** — `INBOX/` is emptied into `knowledge/raw/` on ingestion; no stale raw items.
