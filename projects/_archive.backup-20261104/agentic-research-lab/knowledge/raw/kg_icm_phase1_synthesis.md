---
type: Concept
title: kg_icm_phase1_synthesis
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# KG–ICM integration: what the literature says (Phase 1 synthesis, 2026-10-04)

Source: 3 literature sweeps (GraphRAG-family, agent memory systems, code graphs)
+ 8 arxiv seed notes in INBOX. Answers the 4 handoff research questions.

## Q1 — ICM vs standard GraphRAG: what ICM adds

GraphRAG (Microsoft): LLM extracts entities/relations at INDEX time, Leiden
communities + LLM summaries; query is local (entity ego-graph) or global
(map-reduce over community reports). Cost: global ranks #1 on abstract QA at
57x time / 210x tokens vs vanilla RAG; any corpus change forces teardown+regen.
Single-hop accuracy REGRESSES (-13.4pp on NQ) — the graph adds noise where a
chunk would do.

ICM inverts the cost profile: NO LLM at index time (chunks + tags + FTS5,
deterministic content-hash build), LLM at READ time (reflection with
provenance: fingerprint, plan_version, citations as `Chunk id: NN_slug`).
This is the LightRAG lesson (union-style incremental updates, <100 tokens +
1 call vs GraphRAG's 610K) pushed further: nothing to re-extract, ever.
What ICM keeps from GraphRAG: the local/global split — local = tag
intersection + FTS (`ask.py`), global = reflection digests, which ARE the
community reports, written by the agent instead of the indexer.

## Q2 — query patterns with measured effect (transfer to ask.py / route.py)

- HippoRAG2: single-step PPR over KG matches iterative IRCoT recall
  (+5-14pp R@5 multi-hop) at 10-30x lower cost. Lesson: ONE good retrieval
  beats an agentic loop for bridge questions. `ask.py --tag` intersection is
  the poor-man's PPR; the gap is seed selection (query-to-triple beats
  NER-to-node by 12.5pp) — route.py should expand the query before matching.
- CRAG / reflective RAG: a CHEAP evaluator (Correct/Ambiguous/Incorrect,
  84% vs ChatGPT 58-65%) gates expensive expansion; +4-37pp over RAG.
  Transfer: score FTS5 hits (useful/redundant/confusing) BEFORE 1-hop
  expansion — prevents drift and the k=15 noise collapse ReAct measured.
- ReAct discipline: cap ~7 steps, top-k≈10, duplicate-action early stop;
  trajectory is the working set, SQLite the durable set. Hallucination
  false-positives 6% vs CoT 14%.
- MemGPT DMR +58pp and Zep LongMemEval +18.5% prove runtime graph R/W moves
  task success, not just retrieval metrics.

## Q3 — ICM as daily practice (not batch reflection)

Graphiti (Zep): every turn is an EPISODE; facts are edges with
t_valid/t_invalid; contradiction INVALIDATES (never deletes) the old edge.
Reads return fact+quote side by side so a critic verifies grounding.
Daily-practice mapping: (a) close_session writes episodes, not summaries;
(b) memory.md entries carry valid_from/invalid_at + superseded_by;
(c) a nightly merge (not inline) resolves contradictions — MemGPT's rule
that runtime writes stay O(1) append-only with a dedup key.
ReAct trajectory + CRAG critic is the per-task half; Graphiti bi-temporal
edges are the cross-session half. ICM's "reflection -> meta-learning" is
exactly this split: reflection produces episodes, meta-learning is the
nightly merge that evolves the workflow.

## Q4 — failure modes and runtime mitigations (maps to our 5 known issues)

1. Fingerprint staleness -> Graphiti invalidate-don't-delete + LightRAG
   union updates: restamp in place when cited IDs resolve, mark
   superseded_by when they don't; never silently drop (our restamp rule).
2. Citation concentration (100% top-3) -> HippoRAG spreads via PPR;
   critic gate demotes redundant hits; diversity is a retrieval property,
   not a writer property.
3. Dead routes (zero-chunk tags) -> LightRAG mode-fallback: when the graph
   is untrusted for a query, fall back to naive chunks and LOG the dead
   route (route health monitor = Phase 4 candidate).
4. Write-only memory (no eviction) -> Graphiti bi-temporal model is the
   ONLY surveyed system with principled decay; adopt valid/invalid pairs
   for memory.md + candidates. Nothing else surveyed evicts either.
5. Weak-model tool misuse -> ReAct finding: small models cannot learn
   Thought+Act jointly from few-shot (needs ~3K finetune traces); route
   complex research to stronger models, weak models get single-step
   retrieval (HippoRAG pattern: no agentic loop required).

## Cheapest code-graph schema (Phase 2/4 candidate)

Nodes file/class/function(+span); edges defines/calls/imports/inherits only.
Tree-sitter per file (~ms) into SQLite; file-watcher re-parses changed files
only. Three tools: relevant_files(task), callers/callees(sym),
impact_radius(sym), ego-graph <=2 hops. Measured: +2.3-4.7pp SWE-bench Lite
resolve (+27-100% relative), -70% regressions as test-impact skill. No
CFG/PDG/dataflow until this proves out — structure first, embeddings later
as a cached column (content-hash keyed, re-embed on save).
