---
type: Concept
title: START-HERE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# START-HERE.md — workspace-research

You are looking at a deterministic, graph-backed knowledge base for context engineering, ICM rules, and agent/workspace design.

## The three-layer contract

1. **Map** — `CLAUDE.md` tells you where everything is and how to route by intent.
2. **State** — `CONTEXT.md` tells you what is true right now, with an embedded date.
3. **Drawers** — stage folders (`stages/00_expand` … `stages/05_evict`) hold the workflow in work order.

## What to do first


## Live fingerprint
- Read the live corpus fingerprint from `knowledge/graph/.graph_fingerprint` or `knowledge/graph/GRAPH-DIGEST.md`.
- Do not hardcode it in contracts, prompts, or reflections.
- After any corpus change, rebuild the graph before reflecting.

1. Read `CONTEXT.md` for the operating contract.
2. Read `CLAUDE.md` for routes, rules, and ownership.
3. If you are continuing prior work, read the newest handoff entry at the top of `CONTEXT.md`.

## What NOT to do

- Do not hand-edit `knowledge/graph/graph.db`, `GRAPH-DIGEST.md`, or `graph_index.json`.
- Do not paste knowledge into system prompts by hand — route through the graph.
- Do not leave raw items in `INBOX/` after ingestion.

## How to query the brain

```bash
python knowledge/graph/ask.py "<question>" [--tag <t>] [--limit N] [--raw]
python knowledge/graph/build_graph.py
python pipeline/06_reflect/spawn.py --topic <topic-slug>
```

## Pipeline at a glance

```
INBOX/ → ingest.py → corpus → build_graph.py → ask.py → reflect → evict
```

Run `python scripts/check_*.py` to verify stage contracts before acting on new knowledge.
