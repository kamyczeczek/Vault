---
type: Concept
title: "Decision Graphs for AI-Agent Debugging and Task Planning — Web Research (AgentGraph, decision-graph spec, GoAT, Opswald)"
source: "https://github.com/decision-graph/decision-graph"
tags: [knowledge-graph, agents, workflow-evolution, planning, retrieval]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Decision Graphs for AI-Agent Debugging and Task Planning — Web Research

Retrieved 2026-10-03 via agent-reach: Exa semantic search
(`mcporter call 'exa.web_search_exa(query: "decision graphs AI agents debugging task planning workflow", numResults: 5)'`),
then agent-reach web reader (Jina Reader `curl -s "https://r.jina.ai/<URL>"`) on two returned URLs.
GitHub fetch fallback: anonymous Jina access to github.com returned
`AbuseAlleviationError 40305` (domain blocked until 04:51 UTC), so the GitHub spec
content was taken from the Exa highlights plus the CleverThis raw-ADR fetch; recorded, not invented.

## Source manifest (URLs from the Exa result set)

1. AgentGraph: Trace-to-Graph Platform for Interactive Analysis and Robustness Testing in Agentic AI Systems (AAAI 2026) — https://ojs.aaai.org/index.php/AAAI/article/download/42393/46354
2. decision-graph: versioned property-graph schema for decision structures (spec.json + design.md) — https://github.com/decision-graph/decision-graph
3. The Decision Graph: How AI Agents Actually Think (Opswald, 2026-03-16, Jina-fetched full text) — https://www.opswald.com/blog/decision-graph-how-agents-think/
4. CleverThis ADR-007: Decision Tree and Correction (raw markdown, Jina-fetched full text) — https://git.cleverthis.com/cleveragents/cleveragents-core/raw/commit/f66cb8d68efa283c524e958c7b46bca54a2a9def/docs/adr/ADR-007-decision-tree-and-correction.md
5. Graph of Agentic Thoughts (GoAT): graph-based reasoning bridging agentic reasoning and explainability — https://exa.ai/library/publication/m0pfst66bjh

## Skeletal specification (primitives first, then mechanism)

Decision nodes vs action nodes (Opswald). Two node types: decision node
(input: observations + context; process: reasoning over options; output:
chosen action + reasoning + alternatives considered) and action node
(input: parameters; process: tool/LLM call; output: results + observations).
Linear traces expose only action nodes; a decision graph exposes both, which
is what makes root-cause debugging possible: failures are traced backwards
through dependency chains (decision A -> action B -> observation -> decision C),
and alternative/rejected branches are visible as first-class data.

AgentGraph (AAAI 2026). Pipeline: raw execution logs -> stable line numbers
(L1, L2, ...) -> adaptive semantic window chunking (configurable overlap; each
window yields a local subgraph, temporal replay supported) -> per-window
extraction by schema-constrained LLM (OpenAI structured outputs into a
Pydantic KnowledgeGraph, with chain-of-thought steps) -> Graph Structure
Validator (enforces predefined node/relation types) -> hierarchical merge that
reconciles overlaps, deduplicates entities/relations, preserves line refs.
Fixed node types: agent, task, tool, input, output, human. Typed edges:
consumed by, performs, assigned to, uses, required by, subtask of, next,
produces, delivers to, intervenes. Failure detection across five risk
categories: agent error, planning error, execution error, retrieval error,
hallucination. Optimization recommendations across five areas: prompt
refinement, agent merging, task consolidation, tool enhancement, workflow
simplification. Quantitative layer: perturbation testing (jailbreak-suite
attempts + counterfactual fairness pairs) then causal attribution (DoWhy)
that attributes behavioural change to entities/tools/relations, surfacing
highest-impact drivers for prioritised fixes.

decision-graph spec (dg/v1, DRAFT alpha). A versioned property-graph DDL as
machine-readable JSON (`spec.json`) driving auto-generators (Arrow schema,
Cypher constraint/index/upsert templates, validators). Three layers:
Reference (Task, Actor, Tool, Resource incl. :Model, Session; natural keys,
MERGE-on-upsert, resolves across runs), Execution (WorkflowExecution,
StepExecution, :ToolCall/:Reasoning/:Message; IDs derived from OTel
trace_id/span_id when OTel-sourced so re-ingestion is idempotent, UUIDs
otherwise; per-run status/errors/provenance), Evaluation (independent
provenance, EVALUATES back into execution). Target consumers: Neo4j or any
property graph + Arrow/Parquet tabular exports for ML/RL pipelines.

GoAT (Graph of Agentic Thoughts). Unifies agent-level decisions, flow-level
rationales, memory transitions, and counterfactual paths into one queryable
graph; LLMs generate faithful and contrastive explanations over factual +
counterfactual paths; reported gains: Causal Clarity +1.14, User Trust +1.07,
Faithfulness +1. Debugging insights exposed: delegation chains, memory access
patterns, internal interpretations.

## Mechanism details

- Every graph element links to the exact trace span/line (L-number) that
  substantiates it; a Trace button opens those lines in a right pane
  (AgentGraph). This grounds LLM extraction in original text and reduces
  extraction-hallucination risk.
- Correction is subtree-scoped: in CleverThis ADR-007, correcting decision X
  invalidates exactly the downstream subtree (decisions + child plans), and
  only that portion is re-run (no partial invalidation; no re-run-from-scratch).
- Retrieval over the graph: FTS + RRF fusion of a precise AND-pass, an OR
  recall pass, and an alias pass, with per-source-family aggregation (same
  shape the lab's own knowledge/graph/ask.py uses).

## Threat model and limitation boundaries

- LLM-based extraction hallucination: bounded by schema constraints +
  per-element trace-line grounding + structure validator (AgentGraph).
- Robustness threats: jailbreak attempts against reconstructed
  relation-level prompts; fairness drift under counterfactual demographic
  variants; mitigated by perturbation scoring + causal attribution (DoWhy).
- Observability gap in status-quo tools: OpenTelemetry standardises trace
  collection but not semantic reasoning structure; monitoring is reactive
  (SentinelAgent-style) with limited failure-attribution accuracy.
- Cost/boundaries: per-decision context snapshots grow storage for large
  tool-heavy plans; dependency tracking adds engine complexity; concurrent
  child-plan correction needs coordination; LLM confidence scores feeding
  autonomy thresholds may be miscalibrated (CleverThis ADR-007 risks).

## Failure triples (condition / reason / correction)

1. Linear trace shows `Send email -> INVALID_ADDRESS` / real cause is an
   upstream stale CRM extraction that passed format validation / fix the
   data-lineage source, not the failing action; keep rejected-branch data
   visible so rejections can be re-examined.
2. DB query timeout after "load into memory" was rejected on file size /
   agent chose a query it could not sustain under load / add fallback
   strategy (chunked processing) at the decision node, record the
   alternatives considered with their rejection reasons.
3. Correction of a single decision re-runs the whole plan / no persistent
   decision record or flat append-only log / persistent typed decision tree
   with dependency edges so only the invalidated subtree re-executes.

## Tags: #knowledge-graph #workflow-evolution #planning #agents #agentic #retrieval #provenance #reflection #tool-use
