---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Stage 03_graph — Knowledge Graph Construction & Integrity

## Inputs
- `knowledge/corpus/*.md`

## Process
1. Run `python knowledge/graph/build_graph.py` to index nodes, calculate tags, and create cross-links.
2. Verify sync status via `python knowledge/graph/watch.py --once`.

## Outputs
- `knowledge/graph/graph.db` (FTS5 indexed graph database)
- `knowledge/graph/.graph_fingerprint`
- `knowledge/graph/GRAPH-DIGEST.md`

## Exit Gate
- `.graph_fingerprint` matches digest fingerprint.
- Graph nodes count equals corpus chunk count.
- `python knowledge/graph/watch.py --once` exits 0.


## Evolved Protocol Rule (Defensive Architecture Against Autonomous Research Failure Modes)
<!-- meta-evolved: Defensive Architecture Against Autonomous Research Failure Modes -->
- **Origin Evidence:** ``00_taxonomy_of_20_ai_research_failure_modes`, `00_defensive_failure_mode_hardening``
- **Requirement:** Workspace pipelines must enforce rigorous negative controls, provenance validation, and citation grounding checks to prevent metric gaming, circular citations, and ungrounded memory promotion.


## Evolved Protocol Rule (Minimalist Script-Based Harness Architecture)
<!-- meta-evolved: Minimalist Script-Based Harness Architecture -->
- **Origin Evidence:** ``00_karpathy_minimalist_agentic_coding_harnesses`, `00_deep_analysis_popular_autoresearch_projects``
- **Requirement:** Avoid heavyweight, opaque agent frameworks in favor of transparent, file-based Python scripts and direct command-line execution loops for core verification and research operations.


## Evolved Protocol Rule (ICM Implementation Pitfall Hardening)
<!-- meta-evolved: ICM Implementation Pitfall Hardening -->
- **Origin Evidence:** ``00_icm_implementation_pitfalls_and_failure_modes`, `00_taxonomy_of_20_ai_research_failure_modes``
- **Requirement:** Prevent write-only memory loops, fingerprint desyncs, and dead routing by enforcing closed-loop promotion checks, automated re-stamping, and strict controlled vocabulary lookups.


## Evolved Protocol Rule (Agent Sandboxing & Isolation)
<!-- meta-evolved: Agent Sandboxing & Isolation -->
- **Origin Evidence:** ``00_taxonomy_of_20_ai_research_failure_modes`, `00_defensive_failure_mode_hardening`, `00_agentforce_harnessing_the_agency_of_ai_to_scale`, `00_can_an_ai_out_plan_a_senior_engineer``
- **Requirement:** Autonomous agent pipelines must execute untrusted or exploratory actions in isolated verification environments (sandboxes, disposable worktrees, temporary namespaces) before any modification touches production artifacts or canonical state. Sandboxing is not optional hygiene—it is the primary defense against runaway agents corrupting the workspace, polluting the knowledge graph, or committing invalid state transitions.


## Evolved Protocol Rule (Lexical retrieval (BM25 with parameter tuning for long documents) combined with LLM agentic search trajectories achieves exceptional recall and explainability.)
<!-- meta-evolved: Lexical retrieval (BM25 with parameter tuning for long documents) combined with LLM agentic search trajectories achieves exceptional recall and explainability. -->
- **Origin Evidence:** ``bm25_agentic_search_bergum``
- **Requirement:** Optimize BM25 parameters and leverage code-mode virtual file system primitives for agentic retrieval.


## Evolved Protocol Rule (Research broadness is retrieval-bounded: lossless source plus iterative retrieval beats write-time summarization.)
<!-- meta-evolved: Research broadness is retrieval-bounded: lossless source plus iterative retrieval beats write-time summarization. -->
- **Origin Evidence:** ``00_reflection_retrieval_dominates_write`, `bm25_agentic_search_bergum`, `00_graph_database_architectural_reflection`, `00_00_software_factory_isolate_build_prove_ship``
- **Requirement:** Keep raw lossless chunks canonical; invest in retrieval (tuned lexical ranking, iterative agent reformulation, multi-query trajectories); maintain reachability seeds with negative controls; fail loud on dead tag intersections.
