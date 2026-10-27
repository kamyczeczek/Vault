---
type: Concept
title: CLAUDE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CLAUDE.md — _archive

Retired work, kept for the record. Nothing here is live: no project routes to this
folder, and nothing in it is imported.

## Why this exists

When a workspace restructures, files that were live stop being live. Deleting them
destroys the reasoning that led to the current structure — and in this case, that
reasoning is the record. `agentic-research-lab/CONTEXT.md` is a running log of
defects found and fixed; a repo whose history is only the fixed version cannot
explain why a gate exists.

## What is here

| Path | Was | Why retired |
|---|---|---|
| `ts-diverse-pre-split/` | the monolithic ts-diverse repo | Split into `benchmark-core`, `etth1-h720`, `research-engine`, `datasets`, `brain`. Git history preserved intact |
| `*.py` at this level | one-off repair scripts | Single-purpose fixes to `bench.py` and the KG tools, applied and superseded. They record what was broken, not what to run |

## Rules

- **Nothing routes here.** If a live project needs one of these files, the need is
  a bug in the split, not a reason to import from the archive.
- **Never edit an archived file.** It is a record of what was true at a point in
  time. Correct the live copy and leave the archive alone.
- `ts-diverse-pre-split/` keeps its own `.git` — the history before the split is
  the only record of how the monolithic workspace was structured.
