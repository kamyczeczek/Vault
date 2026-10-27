---
type: Concept
grade: active
title: CLAUDE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CLAUDE.md — brain

Project Brain sidecars: the derived corpus and FTS5 graph that let a project query
its own sources. Nothing here is source of truth — every file is rebuildable from
the project it indexes.

## Where things live

| Path | Role | Description |
|---|---|---|
| `CLAUDE.md` | Catalog (L0) | This file |
| `CONTEXT.md` | Contract (L1) | How a brain is built, and what makes it trustworthy |
| `scripts/ingest.py` | Factory (L3) | Turn raw INBOX material into corpus chunks |
| `scripts/ask.py` | Factory (L3) | Query a brain's graph |
| `.brain/corpus/` | Product (L4) | Atomic markdown chunks, one per source unit. Gitignored |
| `.brain/graph/` | Product (L4) | `graph.db` — SQLite FTS5 index. Gitignored |

## Route by intent

| Intent | Go to |
|---|---|
| Query this project's index | `python scripts/ask.py "<question>"` |
| Ingest new material | put raw files in the project's `INBOX/`, then `python scripts/ingest.py` |
| Build a brain for another project | `python ../../_archive/agentic-research-lab/scripts/bootstrap_project_brain.py <path>` |
| Check a brain is current | rebuild it; the graph carries no timestamp of its own |

## Dependencies

- **On `../../_archive/agentic-research-lab`** — the reference implementation of bootstrap,
  ingest, and graph build. This project is the pattern, not the code.

## Standalone

Run `python preflight.py` first; exit 1 lists exactly what is missing.
Siblings live under `$WORKSPACE_ROOT` (default: this project's parent,
i.e. `projects/research/`). Missing optional siblings degrade the project;
missing hard files block it. What each sibling is used for: see
`Dependencies` above.

## Rules

- **A brain is derived, always.** `corpus/`, `graph.db`, and the fingerprint are
  gitignored in every project. If you cannot rebuild one from its project, the
  project is missing its sources, not the brain missing its data.
- **One home per fact.** If two projects index the same document, each keeps its
  own chunk; neither copies the other's index.
- **Cite a chunk, not a summary.** `ask.py` returns chunk ids. Pass those ids
  onward, never the prose around them.
