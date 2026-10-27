---
type: Concept
title: memory
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

### bm25_agentic_search_reflection — accepted
Rule: Lexical retrieval (BM25 with parameter tuning for long documents) combined with LLM agentic search trajectories achieves exceptional recall and explainability.
Evidence: `bm25_agentic_search_bergum`
Target: knowledge graph retrieval and agentic search loops
Action: Prefer BM25 lexical retrieval over dense reranking in agentic search loops; tune k1/b for long-form chunks, log agentic search trajectories, and keep reachability seeds as negative controls on the retrieval layer.

### causal-falsification-loops — accepted
Rule: Autonomous agent research and experimentation loops MUST enforce causal falsification and interventional testing (ablations and negative controls) rather than relying on associative correlation or intrinsic self-correction.
Evidence: `365_the_book_of_why_the_new_science_of_cause_and_eff`, `00_seed_ai_scientist`, `01_07_critic_external_tool_verification`
Target: autonomous research and experiment loops
Action: Run ablation and counterfactual attribution probes with observable environment output, and correct only root-cause failures, before promoting any hypothesis or code modification.

### research-quality-external-grounding — accepted
Rule: Research quality requires external grounding: verify-then-correct with tools, tests, or peer review; never promote on ungrounded self-correction.
Evidence: `00_06_self_correction_grounding_requirement`, `00_07_critic_external_tool_verification`, `00_automated_peer_review_and_self_correction`, `00_deep_analysis_popular_autoresearch_projects`
Target: reflect
Action: Block any finding, candidate promotion, or self-revision whose only evidence is model self-critique; require tool output, test-runner result, peer-review rubric score, or graph id resolution, and target corrections only at verified-wrong items (oracle discipline).

### research-breadth-retrieval-first — accepted
Rule: Research broadness is retrieval-bounded: lossless source plus iterative retrieval beats write-time summarization.
Evidence: `00_reflection_retrieval_dominates_write`, `bm25_agentic_search_bergum`, `00_graph_database_architectural_reflection`, `00_00_software_factory_isolate_build_prove_ship`
Target: graph
Action: Keep raw lossless chunks canonical; invest in retrieval (tuned lexical ranking, iterative agent reformulation, multi-query trajectories); maintain reachability seeds with negative controls; fail loud on dead tag intersections.

### research-depth-skeletal-triples — accepted
Rule: Research depth requires skeletal specification and reusable failure triples, not summaries.
Evidence: `00_don_t_vibe_code_do_skele_code_interactive_no_cod`, `01_09_mistake_correction_abstraction_level`, `00_taxonomy_of_20_ai_research_failure_modes`, `00_agent_error_taxonomy_debugging_web_research`, `00_defensive_failure_mode_hardening`
Target: inbox
Action: Require every ingested chunk to state architecture primitives, algorithmic mechanisms, and threat model and limitation boundaries with skeletal spec first, then body; record every lesson as a failure condition, reason and correction triple; isolate work, capture before and after proof, and pass independent review before ship.

### vera-expa-003 — accepted
Rule: Post-promotion audit — run every accepted lesson against held-out trajectories and decrement score when eviction predicate fires.
Evidence: `00_08_lesson_persistence_eviction_requirement`, `00_a_bandit_approach_with_evolutionary_operators_fo`
Target: reflection pipeline
Action: Run post-promotion audit on held-out trajectories for every accepted lesson; decrement the lesson score and fire the eviction predicate when the audit fails (ExpeL recurrence-prevention ledger, downvote-to-zero).

### vera-expa-002 — accepted
Rule: Every stored lesson must encode its own eviction predicate; a lesson without an escape hatch compounds confidently wrong guidance.
Evidence: `00_08_lesson_persistence_eviction_requirement`, `00_06_self_correction_grounding_requirement`, `00_agent_memory_hierarchies`
Target: reflection pipeline
Action: Require every stored lesson to encode an eviction predicate (firing condition + score decrement + re-test trigger); run the post-promotion audit on held-out trajectories and decrement the lesson score when the predicate fires.

### vera-expa-001 — accepted
Rule: Promotion gate must require independent external ground truth; self-reported success is unverifiable.
Evidence: `00_06_self_correction_grounding_requirement`, `00_00_software_factory_isolate_build_prove_ship`, `00_automated_peer_review_and_self_correction`
Target: reflection pipeline
Action: Require every candidate promotion to resolve at least one evidence node in graph.db AND cite a tool-output artifact (test result, audit log, or review-gate entry) before acceptance; block self-critique-only promotions.

### vera-expa-004 — accepted
Rule: Add AgentDebug-style root-cause attribution (detect→attribute→correct) to the reflect stage of spawn.py, producing structured error-classified candidates.
Evidence: `00_agent_error_taxonomy_debugging_web_research`, `00_agent_hooks_lifecycle_guardrails`, `00_agent_execution_hooks_guardrails`
Target: reflection pipeline
Action: On every reflect-stage spawn, run detect→attribute→correct pipeline: classify each failed candidate into an error category (retrieval miss, grounding gap, logical inconsistency, or tool misuse), emit a structured JSON diagnostic, and target correction only at the attributed root cause.

### vera-expf-rev-001 — accepted
Rule: Adding a third evidence node with non-overlapping tag dimensions raises F1 counterfactual retention from 0.0 to 0.54–0.59, converting fragile verdicts to partial.
Evidence: `00_automated_peer_review_and_self_correction`, `00_agent_execution_hooks_guardrails`, `00_agent_memory_hierarchies`
Target: reflection pipeline
Action: For automated peer-review correction loops over evidence sets, add a third agent-memory-hierarchy node with non-overlapping tag dimensions and re-run deterministic execution-hook adversarial falsification; evaluation shows F1 counterfactual retention rises from 0.0 to 0.54-0.59, converting fragile verdicts to partial

### vera-expf-rev-002 — accepted
Rule: When two original evidence nodes share ≥5 of 6 tags, adding a third node does not fix F1 fragility — the redundancy is pairwise; node replacement (not addition) is required.
Evidence: `00_08_lesson_persistence_eviction_requirement`, `00_06_self_correction_grounding_requirement`, `00_agent_memory_hierarchies`
Target: reflection pipeline
Action: Before re-running lesson-persistence adversarial falsification, swap the redundant eviction-ledger evidence node with a complementary agent-memory-hierarchy node; pairwise tag redundancy (>=5/6 shared tags) makes self-correction grounding fail when only added, not replaced

### vera-expf-final-001 — accepted
Rule: When all candidates in a reflection batch pass adversarial falsification plus post-promotion audit, promote them in the same gate cycle and record pairwise-redundancy lessons as meta-candidates about the pipeline itself.
Evidence: `00_agent_memory_hierarchies`, `00_automated_peer_review_and_self_correction`, `00_agent_error_taxonomy_debugging_web_research`
Target: reflection pipeline
Action: When a batch of agent-memory-hierarchy candidates all pass automated peer-review correction plus post-promotion audit, promote them in one gate cycle and record the error-taxonomy debugging lessons as meta-candidates about the reflection pipeline; then run apply_meta_learning.py to propagate the new rules into stage contracts

### vera-expf-001 — accepted
Rule: Adversarial falsification harness (Proponent/Critic/Judge) with counterfactual ablation, counter-evidence search, and defect injection resilience can differentiate candidate robustness and guide promotion decisions.
Evidence: `00_06_self_correction_grounding_requirement`, `00_08_lesson_persistence_eviction_requirement`
Target: reflection pipeline
Action: adopt multi-agent debate pattern for candidate evaluation

### vera-expf-audit-001 — accepted
Rule: Post-promotion audit harness (test accepted rules against held-out questions, flag vague actions, validate structural correctness) successfully differentiates well-specified rules from those needing revision.
Evidence: `00_08_lesson_persistence_eviction_requirement`, `00_a_bandit_approach_with_evolutionary_operators_fo`
Target: reflection pipeline
Action: adopt automated post-promotion audit pattern
