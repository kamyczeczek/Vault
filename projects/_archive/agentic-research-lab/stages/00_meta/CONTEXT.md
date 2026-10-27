---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Stage 00_meta — Cross-Cutting Meta Rules & Workflow Principles

Holding pen for promoted reflection rules that do not target a single stage
(`general` / `multi-agent`). These rules are loaded by agents at the top of
every session alongside the stage contract for the active phase.

## Inputs
- `reflection/memory.md` promoted rules with target `general` or `multi-agent`
- `reflection/candidates/workflow-principles.jsonl` (promoted candidates awaiting integration)

## Process
1. Read `reflection/memory.md` and extract every accepted rule whose `Target:` is
   `general` or `multi-agent`.
2. Validate each rule carries backticked evidence ids that resolve in `graph.db`.
3. Append rules here as `## Meta Rule` blocks, newest last, with provenance header.

## Outputs
- `stages/00_meta/CONTEXT.md` (this file)

## Invoke
```bash
python scripts/apply_meta_learning.py
```

## Contract
- **Non-destructive:** never remove or rewrite an existing rule block; append only.
- **Provenance:** every rule block records its originating `memory.md` rule id and evidence ids.
- **Audit:** `scripts/check_stage_contracts.py` must pass after any append.

## Meta Rules

<!-- meta-evolved: workflow-principles backlog -->
Rules from `reflection/candidates/workflow-principles.jsonl` are promoted here by
`apply_meta_learning.py` once they pass promotion gates.


## Evolved Protocol Rule (Design-First Planning)
<!-- meta-evolved: Design-First Planning -->
- **Origin Evidence:** ``00_can_an_ai_out_plan_a_senior_engineer`, `01_can_an_ai_out_plan_a_senior_engineer`, `00_icm_implementation_pitfalls_and_failure_modes``
- **Requirement:** Rigorous upfront design and explicit specification documents ('design-first planning') dramatically improve autonomous agent implementation success, enabling one-shot execution or clean 4-5 chunk decomposition.


## Evolved Protocol Rule (Agent Escalation & Graceful Handoff)
<!-- meta-evolved: Agent Escalation & Graceful Handoff -->
- **Origin Evidence:** ``00_agentforce_harnessing_the_agency_of_ai_to_scale`, `00_self_consistency_and_tree_search_code_generation`, `00_automated_peer_review_and_self_correction`, `00_taxonomy_of_20_ai_research_failure_modes``
- **Requirement:** Agentic workflows must treat human handoff and inter-agent escalation as first-class, intentional actions rather than error fallbacks or failure exceptions. When an agent detects confidence degradation, tool-call loops, or ungrounded reasoning, it must escalate cleanly rather than retry blindly or hallucinate creative workarounds.


## Evolved Protocol Rule (Planner-Executor Split)
<!-- meta-evolved: Planner-Executor Split -->
- **Origin Evidence:** `00_agentic_rag_modular_graph`, `00_can_an_ai_out_plan_a_senior_engineer`, `00_deep_analysis_popular_autoresearch_projects`
- **Requirement:** Agent systems MUST separate planner and executor roles: the planner chooses strategy, decomposition, and retrieval; the executor grounds actions and generation. Do not delegate planning downward.


## Evolved Protocol Rule (Horizon-Aware Plan Spec)
<!-- meta-evolved: Horizon-Aware Plan Spec -->
- **Origin Evidence:** `00_icm_implementation_pitfalls_and_failure_modes`, `00_can_an_ai_out_plan_a_senior_engineer`
- **Requirement:** Plan specifications MUST be concrete for near actions and abstract for distant phases. Do not hardcode procedural details into far-horizon phases.


## Evolved Protocol Rule (Deterministic Retrieval Separation)
<!-- meta-evolved: Deterministic Retrieval Separation -->
- **Origin Evidence:** `00_agentic_rag_modular_graph`, `00_agent_memory_hierarchies`
- **Requirement:** Deterministic tag-intersection retrieval and agentic retrieval MUST remain separate tools. Do not mix them implicitly in prompts.


## Evolved Protocol Rule (Reusable Failure Triples)
<!-- meta-evolved: Reusable Failure Triples -->
- **Origin Evidence:** `00_09_mistake_correction_abstraction_level`, `00_agent_error_taxonomy_debugging_web_research`
- **Requirement:** Agent learning systems MUST store mistakes as (failure condition → reason → correction) triples, not as failed trajectories or corrected answers. Transfer scales with abstraction level.


## Evolved Protocol Rule (Root-Cause-Targeted Correction)
<!-- meta-evolved: Root-Cause-Targeted Correction -->
- **Origin Evidence:** `00_agent_error_taxonomy_debugging_web_research`, `00_agent_execution_hooks_guardrails`
- **Requirement:** When correcting agent failures, target the earliest root-cause step only, not every symptom. This yields the highest accuracy gains.


## Evolved Protocol Rule (One-Stage-One-Job Modules)
<!-- meta-evolved: One-Stage-One-Job Modules -->
- **Origin Evidence:** ``00_icm_map`, `00_deep_analysis_popular_autoresearch_projects`, `00_agent_execution_hooks_guardrails``
- **Requirement:** Every agent module or subagent must own exactly one responsibility, with explicit input/output interfaces; multi-role modules are a failure mode.

## Evolved Protocol Rule (No Cargo-Cult Completions)
<!-- meta-evolved: No Cargo-Cult Completions -->
- **Origin Evidence:** `00_agent_execution_hooks_guardrails`, `00_icm_implementation_pitfalls_and_failure_modes`, `00_taxonomy_of_20_ai_research_failure_modes`
- **Requirement:** An integration is NOT complete until a verification script exercises it end-to-end. Editing a file, updating a doc, or adding an import does not constitute wiring. Every claimed integration MUST have a corresponding test that fails if the wiring is removed. `scripts/check_wiring.py` MUST pass before any quality gate suite is considered complete.


## Evolved Protocol Rule (State Freshness Gate)
<!-- meta-evolved: State Freshness Gate -->
- **Origin Evidence:** `00_measured_liveness_not_consistency`, `00_a_complete_guide_to_managing_thousands_of_files`, `00_08_lesson_persistence_eviction_requirement`
- **Requirement:** Workspace state is only trustworthy when it is fresh. `CONTEXT.md` daily handoff must have an entry dated within 24h. If the handoff is stale, the AI must not guess — it must update the state or halt. `scripts/check_state_freshness.py` MUST pass before any quality gate suite is considered complete.


## Evolved Protocol Rule (Gate-First Discipline)
<!-- meta-evolved: Gate-First Discipline -->
- **Origin Evidence:** `skills/unlazy/SKILL.md`, `skills/unlazy/references/gates.md`
- **Requirement:** For any substantial task, write all acceptance gates BEFORE implementation. Each gate MUST have an observable outcome, a runnable `CHECK:`, an `EXPECT:` token, and an `EVIDENCE:` field. Do not silently remove an impossible gate — record `ABANDON: <id> <non-empty reason>` as a terminal handoff. A checked gate without current evidence is unmet, not met. Re-run every `CHECK:` before reporting completion.


## Evolved Protocol Rule (Persistent Planning Files)
<!-- meta-evolved: Persistent Planning Files -->
- **Origin Evidence:** `skills/planning-with-files/SKILL.md`, `skills/planning-with-files/references/method.md`
- **Requirement:** For any substantial task (3+ steps, 5+ tool calls, or spanning multiple sessions), create `task_plan.md`, `findings.md`, and `progress.md` in the task directory before execution. Each phase in `task_plan.md` MUST have Status, Owner, and Evidence. Apply the 2-Action Rule: after every 2 view/search/browser operations, immediately save findings to `findings.md`. Re-read planning files before major decisions. Mark phases complete only after evidence is recorded. A task without a plan file is unmanaged work.


## Evolved Protocol Rule (Regression-Gated Meta-Learning)
<!-- meta-evolved: Regression-Gated Meta-Learning -->
- **Origin Evidence:** `00_skillopt`, `00_verified_self_evolving_agent`
- **Requirement:** Meta-learning edits MUST NOT apply unless they pass through a regression gate. `apply_meta_learning.py` MUST run `quality_check.py --json` before and after applying any rule. If any quality gate transitions from passing to failing, the entire meta-learning pass MUST abort and restore from backup. Ungated evolution collapsed performance from 55.4% → 2.6% in SkillOpt stress testing; gated evolution stayed flat at 57.0%. Baseline capture is a one-time setup via `python scripts/apply_meta_learning.py --save-baseline`. After a successful apply, baseline advances to the new passing state. Any proposed rule that would regress a gate is rejected, not patched or special-cased.

<!-- SLOW_UPDATE_START -->
The rules above this block are considered stable cross-cutting principles.
They MUST NOT be rewritten by routine reflection passes.
Edits here require explicit human review and a separate promotion action.
<!-- SLOW_UPDATE_END -->
