---
type: Concept
title: memory
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# reflection/memory.md — promoted accepted rules

Written by `scripts/promote_candidate.py` (promote with `--memory reflection/memory.md`);
backfilled once on 2026-09-16 from candidates already in state `accepted`.
Contracted 04_reflect input: a spawned reflection reads it, so a promoted rule
constrains future runs instead of accumulating silently.
Gated by `scripts/check_promotion.py` — an accepted rule with no landed entry
fails the gate.

### C1 — accepted
- claim: Load-bearing agent state (plan, invariants, task spec, intermediate results) must live in explicit external stores (files, skills, structured memory), not in transient model-internal memory.
- evidence: `00_plans_don_t_persist_why_context_management_is_lo`, `33_improving_planning_with_large_language`, `20_self_evolving_world_models_for_llm_agent_plannin`, `00_interpretable_context_methodology_folder_structu`

### C2 — accepted
- claim: Each stage/agent should load only the context it needs for its current job; over-broad context degrades output and accountability.
- evidence: `00_icm_map`, `00_one_stage_one_job`, `00_is_progressive_disclosure_all_you_need_for_long`, `00_interpretable_context_methodology_folder_structu`

### C3 — accepted
- claim: Emitted artifacts must be reproducible and independently verifiable; claims require cited evidence, not model assertion.
- evidence: `02_why_passing_benchmarks_doesn_t_mean_your_ai_wrot`, `02_real_design_patterns_for_agentic_software_factor`, `00_plain_text_as_interface`

### C7 — accepted
- claim: Every stage output is an edit surface; human intervention is a feature, designed in, not a failure mode.
- evidence: `00_icm_map`, `02_real_design_patterns_for_agentic_software_factor`

### C8 — accepted
- claim: Reserve frontier models for design/judgment; use cheaper models for execution/well-defined one-offs.
- evidence: `02_jak_naprawd_wycisn_2_3x_z_ai_w_kodowaniu_na_pods`, `02_real_design_patterns_for_agentic_software_factor`

### W1 — accepted
- claim: Enforce watch.py --once at spawn entry and refuse spawn when .graph_fingerprint != GRAPH-DIGEST fingerprint
- evidence: `00_interpretable_context_methodology_folder_structu`

### W2 — accepted
- claim: Keep one-level disclosure as only expansion (tag intersection + single-hop edge); forbid ad-hoc corpus browsing beyond returned ids with CI check for un-cited claims
- evidence: `00_is_progressive_disclosure_all_you_need_for_long`

### W3 — accepted
- claim: Wire check_reflection.py into spawn_recursive.py post-merge; gate git checkpoint on citation+schema pass
- evidence: `00_memory_for_autonomous_llm_agents_mechanisms_eval`

### W4 — accepted
- claim: Add adaptive one-hop edge expansion (REFERS_TO/SHARES_TAG) only when intersection result below threshold; otherwise no expansion
- evidence: `00_adapt_as_needed_decomposition_and_planning_with`

### W5 — accepted
- claim: Generate knowledge/raw/manifest.jsonl mapping raw sources to derived corpus chunk ids via ingest.py; verify corpus hash covers raw
- evidence: `00_awesome_context_engineering`

### W6 — accepted
- claim: Implement deterministic INBOX cleanup invariant: log intake->corpus provenance and purge INBOX atomically after successful ingestion
- evidence: `00_from_plan_to_action_how_well_do_agents_follow_th`

### W7 — accepted
- claim: Add stage CONTEXT.md with Inputs Table for reflection stage explicitly listing allowed graph queries and leaf chunk sets
- evidence: `00_icm_map`

### W8 — accepted
- claim: Run NB1 replay-pairing regression (task with vs without each ICM layer) to promote or reject C10; decide if folder depth is decorative vs load-bearing
- evidence: `00_icm_knowledge_big`

### planning-research-workflow-topic-coverage-gap — accepted
- claim: knowledge/topics.md lists planning but planning-research-workflow was uncovered (no digest/candidates) until this reflection; one-stage-one-job + plain-text-as-interface require every topic workflow to have an inspectable file surface
- evidence: `00_one_stage_one_job`, `00_plain_text_as_interface`, `00_interpretable_context_methodology_folder_structu`

### P1 — accepted
- claim: Add pipeline/WORKFLOW.md as canonical global plan (ordered phases 01_inbox→02_corpus→03_graph→04_reflect with entry/gate/handoff per phase); require phase-compliance citation in agent outputs
- evidence: `00_from_plan_to_action_how_well_do_agents_follow_th`

### P2 — accepted
- claim: Add ADAPT-style as-needed decomposition: if ask.py intersection < threshold or executor signals failure, split topic into alias sub-tags deterministically (ORDER BY id, one level) and re-query; log depth in digest
- evidence: `00_adapt_as_needed_decomposition_and_planning_with`

### P3 — accepted
- claim: Re-inject current phase CONTEXT.md Inputs Table + global plan header every N tool calls or on context truncation as a plan reminder
- evidence: `00_from_plan_to_action_how_well_do_agents_follow_th`

### P5 — accepted
- claim: Annotate each stages/*/CONTEXT.md with explicit budgets and enforce via watch.py/build_graph.py guards
- evidence: `00_awesome_context_engineering`

### P6 — accepted
- claim: Adopt this digest + planning-tasks.jsonl as the planning topic sink; add planning to reflection coverage check in spawn_recursive.py
- evidence: `00_interpretable_context_methodology_folder_structu`

### P7 — accepted
- claim: Keep one-level disclosure only; handle synonymy via alias tags registered in knowledge/topics.md, forbid recursive routing expansion
- evidence: `00_is_progressive_disclosure_all_you_need_for_long`

### P8 — accepted
- claim: Stamp every reflection/digests/*.md and reflection/candidates/*.jsonl with fingerprint + plan version + routing queries; reject digests missing that provenance in check_reflection.py
- evidence: `00_icm_knowledge_big`

### workspace-health-routing-shadow-dirs — accepted
- claim: stages/ is canonical but sibling shadow dirs stages01_inbox/..stages04_reflect/ coexist at root, creating a routing drift hazard for fresh agents cold-walking via CONTEXT.md
- evidence: `00_interpretable_context_methodology_folder_structu`, `00_icm_map`, `00_one_stage_one_job`, `00_icm_43_copies_four_moves`

### workspace-health-determinism-gate-advisory — accepted
- claim: graph.db fingerprint exists in GRAPH-DIGEST.md (35b86bc954fa) but spawn.py/extension only warn on STALE_DIGEST; a stale digest can be consumed silently
- evidence: `00_interpretable_context_methodology_folder_structu`, `00_agent_memory_hierarchies`, `00_is_progressive_disclosure_all_you_need_for_long`, `00_pocock_context_shared_language`

### workspace-health-stage-contract-underspecified — accepted
- claim: pipeline/06_reflect/ stage exists (WORKFLOW.md + route.py + spawn_recursive.py) but its Inputs Table does not enumerate allowed ask.py --tag intersections and leaf chunk sets
- evidence: `00_icm_map`, `00_one_stage_one_job`, `00_plain_text_as_interface`

### workspace-health-anti-leakage-currently-clean — accepted
- claim: No scale leakage observed (empty INBOX, paired digests/candidates, check_reflection.py validates state machine); long-term anti-leakage needs periodic re-anchoring surface
- evidence: `00_icm_43_copies_four_moves`, `00_from_plan_to_action_how_well_do_agents_follow_th`, `00_plans_don_t_persist_why_context_management_is_lo`

### workspace-health-verification-loop-load-bearing — accepted
- claim: Reflection credibility depends on check_reflection.py validating every digest citation resolves in graph.db and every candidates/*.jsonl record satisfies the state machine; without it outputs are unverifiable
- evidence: `00_memory_for_autonomous_llm_agents_mechanisms_eval`, `00_pocock_grilling`, `00_icm_43_copies_four_moves`

### W-AUDIT-1 — accepted
- claim: stages/04_reflect/CONTEXT.md hardcodes fingerprint 17a3297a22fc in its Determinism clause, but the live corpus fingerprint is 0626262b2982 — the contract describing the hash gate cites a hash dead since the 2026-09-15 corpus tag repair.
- evidence: `00_interpretable_context_methodology_folder_structu`

### W-AUDIT-4 — accepted
- claim: pipeline/06_reflect/_audit_workspace.prompt mandates ask.py --tag icm --tag agent-workspaces as its first routing query, but agent-workspaces is absent from knowledge/topics.md — a mandated route that resolves to zero chunks.
- evidence: `00_icm_43_copies_four_moves`, `00_adapt_as_needed_decomposition_and_planning_with`

### W-AUDIT-5 — accepted
- claim: 18 MONITORING/reflection/ files (2026-09-12..14) and 6 RESEARCH/ files plus 2 brain artifacts are written but untracked — Rule 6 holds on disk but not in git history.
- evidence: `00_from_plan_to_action_how_well_do_agents_follow_th`

### W-AUDIT-6 — accepted
- claim: ROOT/problems/ is an empty directory while the live problem log lives in MONITORING/KNOWLEDGE/problems/ (cited by PROGRESS.md) — two problem homes, one unused.
- evidence: `00_interpretable_context_methodology_folder_structu`

### research-process-vocabulary-reachability-gate — accepted
- claim: The research loop is closed at the artifact level but its intake is vocabulary-shaped: zero-hit questions are correct AND-semantics, not a bug, and the corpus's own boundary condition ('the vocabulary must be maintained, or questions silently go unanswered') is currently unmonitored — dead_route_tags() checks prompt tags, not question reachability.
- evidence: `00_reflection_closed_vocabulary_before_content`, `00_reflection_retrieval_dominates_write`, `00_is_progressive_disclosure_all_you_need_for_long`, `00_icm_43_copies_four_moves`
