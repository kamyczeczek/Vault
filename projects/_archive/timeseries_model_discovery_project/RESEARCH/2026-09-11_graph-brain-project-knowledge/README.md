---
type: Concept
id: 2026-09-11_graph-brain-project-knowledge
date: 2026-09-11
scenario: S4
surface: graph brain project knowledge code analysis problem detection direction recommendation
status: done
supersedes: none
title: README
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Research: Graph Brain for Project-Wide Knowledge, Fast Problem Detection & Good Direction

User directive 2026-09-11: build a graph brain that knows the project in detail and enables extremely fast surfacing of code/architecture problems and of a good next-work direction. Web research via `agent-reach` (Exa, 2026-09-11) over the live code-graph RAG landscape (15 engines + 6 papers + Sourcegraph/Cody doctrine) plus local grounding in the workspace's existing brain shelf (`brains/*/rag.db`, `RESEARCH/R-0n`). Concentric finding: the graph must be a deterministic two-phase pipeline (tree-sitter → call/import/heritage resolve → community/centrality/taint + SQLite-first store with optional KuzuDB port) with hybrid retrieval (BM25 + vectors → weighted RRF dense ≥2× → 1-hop expansion → ripgrep refine → rerank) delivering three capabilities (project omniscience via 7 graph tools, fast problem detection via orphan/cycle/hotspot/tainter/blast-radius detectors, direction via staged L0 heuristic → L1 LLM-over-graph → optional L2 GNN fusion). Delivered as `findings.md` (cited architecture + phased P1→P4 rollout mirroring `brains/` invariants: `graph_index.json` + `GRAPH-BRAIN-DIGEST` + `verify_graph_sync`), `open_questions.md` (5 deferred decisions), `references.md` (all Exa sources).

## Route
Record added as R-07 in `RESEARCH/CONTEXT.md` in this session; gate `RESEARCH/check_catalog.py` green on commit.

## Status
- done — findings/open_questions/references + this frontmatter + routing row complete.
