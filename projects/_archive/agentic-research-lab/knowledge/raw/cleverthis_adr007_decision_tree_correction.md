---
type: Concept
title: "CleverThis ADR-007 Deep Analysis — Persistent Decision Tree and Targeted Correction for Agent Plans"
source: "https://git.cleverthis.com/cleveragents/cleveragents-core/raw/commit/f66cb8d68efa283c524e958c7b46bca54a2a9def/docs/adr/ADR-007-decision-tree-and-correction.md"
tags: [knowledge-graph, planning, workflow-evolution, agents]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# ADR-007 (CleverThis) — Persistent Decision Tree and Targeted Correction

Full text retrieved 2026-10-03 via agent-reach Jina Reader
(`curl -s "https://r.jina.ai/https://git.cleverthis.com/cleveragents/cleveragents-core/raw/commit/f66cb8d68efa283c524e958c7b46bca54a2a9def/docs/adr/ADR-007-decision-tree-and-correction.md"`).
Status: Accepted, 2026-02-16, author/approver Jeffrey Phillips Freeman.
Skeletal specification first, then mechanism and boundaries.

## Skeleton: the data structures

- `decisions` table: one row per decision node. Fields: `decision_id` (ULID),
  `plan_id`, `parent_decision_id` (tree structure), `sequence_number`,
  `decision_type` (one of eleven), `question`, `chosen_option`,
  `alternatives_considered`, `confidence_score` (0.0-1.0, optional),
  `hot_context_hash` + `hot_context_ref` + `relevant_resources` +
  `actor_state_ref` (LangGraph checkpoint; the context snapshot must suffice
  to replay the decision in isolation), `rationale`, `actor_reasoning`
  (raw LLM reasoning, optional), `downstream_decision_ids`,
  `downstream_plan_ids`, `artifacts_produced`, `is_correction`,
  `corrects_decision_id`, `correction_reason`, `superseded_by`.
- `decision_dependencies`: parent-child edges.
- `correction_attempts`: history with attempt number, mode, guidance, outcome.
- Eleven decision types, each phase-typed: Strategize —
  `prompt_definition` (always the single root of a plan tree),
  `invariant_enforced`, `strategy_choice`, `subplan_spawn`,
  `subplan_parallel_spawn`; Execute — `implementation_choice`,
  `resource_selection`, `tool_invocation`, `error_recovery`,
  `validation_response`; Any — `user_intervention`. No untyped decisions
  are permitted.

## Mechanism: targeted correction

- Unified command `agents plan correct <decision_id> --mode=revert|append
  --guidance "<text>"` operates on decision nodes by ID. Prompt correction
  uses the same mechanism as any other correction (prompt is a node, not a
  special case).
- Correcting a decision invalidates all downstream decisions in the affected
  subtree including child plans; the system re-executes only the invalidated
  portion. Constraint: partial invalidation is not permitted — the cascade
  is exactly the dependency-subtree boundary.
- Phase discipline: Execute-phase decisions must be constrained by
  Strategize-phase decisions; violation triggers phase reversion, not silent
  override. Apply phase creates no new decisions.
- Autonomy control: `auto_decisions_strategize` / `auto_decisions_execute`
  in [0.0, 1.0]; at 1.0 every decision is manual, at 0.0 the strategy actor
  decides autonomously and records reasoning; intermediate values auto-decide
  only when confidence_score >= threshold, otherwise the user is prompted.
- Correction scenario map: vague request -> correct the `prompt_definition`
  node; bad specific choice -> correct that `strategy_choice`; bad child
  prompt -> correct the child's `prompt_definition`; wrong invariant ->
  remove `invariant_enforced`; sequential->parallel -> switch to
  `subplan_parallel_spawn`.

## Threat model and limitation boundaries

- Storage: per-decision context snapshots plus full records can grow
  unbounded for large tool-heavy plans; retention policies are required but
  the ADR defers their details.
- Cascade risk: correcting a high node in a deep hierarchy invalidates most
  completed work; correction cost is data-dependent, not bounded a priori.
- Confidence calibration: the threshold mechanism depends on LLM-reported
  confidence scores, which may be miscalibrated; a miscalibrated value
  silently moves decisions between manual and automatic lanes.
- Concurrency: corrections with downstream invalidation need coordination
  when child plans are running concurrently.
- Alternatives rejected: flat append-only decision log (no targeted
  correction; dependency search manual and infeasible at scale) and
  no-persistence re-run-from-scratch (prohibitively expensive for
  hierarchically decomposed plans).

## Failure triples

1. Original request too vague / strategy actor built an elaborate plan from
   an underspecified root / correct the root `prompt_definition` node; the
   whole subtree invalidates exactly.
2. LLM confidence 0.9 on a wrong tool selection / threshold auto-decided a
   bad execute choice / record `correction_reason` in `correction_attempts`;
   recalibrate thresholds from recorded attempts.
3. Context snapshot too small to replay / isolation replay produced
   inconsistent results / make the snapshot a hard constraint (hash +
   full ref + checkpoint), validated by context-snapshot integrity tests.

## Compliance evidence defined by the ADR

Decision-type coverage tests (all eleven types create/store/retrieve/
correct), correction-cascade tests (invalidation exactly matches the
subtree, no more, no less), context-snapshot integrity tests (isolated
replay consistency), BDD scenarios for prompt correction, strategy
revision, cross-hierarchy correction, and storage retention tests.
Related ADRs: 006 plan lifecycle, 016 invariants, 017 automation
profiles, 033 decision recording protocol, 034 tree versioning (structural
tree + influence DAG), 035 rollback and replay.

## Tags: #knowledge-graph #workflow-evolution #planning #agents #agentic #reflection #provenance #tool-use
