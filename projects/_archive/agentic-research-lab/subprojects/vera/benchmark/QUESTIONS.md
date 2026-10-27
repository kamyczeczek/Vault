---
type: Concept
title: QUESTIONS
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# VERA Benchmark: 20 Research Questions

Each question block MUST contain: `id`, `question`, `level` (1–5), `scope` (in/out),
`seeds:` (corpus chunk IDs expected to be relevant), `distractors:` (plausible-but-wrong
chunk IDs), `target_structure` (expected subtopics), and `controversy` (where ≥2 sources
disagree). All chunk IDs below are verified to exist in `knowledge/corpus/` on 2026-09-24
(annotation log: `reports/seed_annotation.md`). Sources tagged `workspace:` come from lab
contracts (CONTEXT.md, stages/*/CONTEXT.md, reflection/memory.md) and are cited, not scored
for recall — they are ground-truth context, not retrieval targets.

Difficulty levels:
- 1: direct factual retrieval
- 2: multi-source synthesis
- 3: conflicting evidence
- 4: causal or methodological comparison
- 5: open-ended research proposal

---

## L1 — Direct retrieval (questions Q1–Q4)

### Q1
question: "What trust tiers does this lab use for evidence, and what does tier 3 mean?"
level: 1
scope: in: trust_tier definitions; out: graph implementation details
seeds: 00_okf_methodology_research; workspace: CONTEXT.md (chunk contract, trust_tier 0–3)
pinned_query: "trust_tier provenance tiers attested"  # B0.2 pin v1 (2026-09-24, E-suite addendum): terms verified via ask.py (top-1 = 00_okf_methodology_research); same verified term set used by the DB-1 arm log
distractors: 01_the_five_level_verification_ladder (competency ladder, adjacent but distinct)
target_structure: [tier enumeration, tier 3 definition, example]
controversy: none expected — negative control question

### Q2
question: "What does the 2-Action Rule require and which failure mode does it prevent?"
level: 1
scope: in: planning-file workflow; out: hook layer
seeds: 00_reflection_reorientation_cost, 01_session_compaction_for_ai_agents; workspace: CONTEXT.md (failure modes), templates/task_plan.md
pinned_query: "session compaction"  # B0.2 pin v2 (2026-09-24): v1 "persist notes context" recalled 0/2 seeds; v2 hits 2 seeds (scorer caveat: 01_ prefix variant not counted — see score note)
distractors: 00_workspace_rapid_understanding (workspace comprehension, not persistence)
target_structure: [rule statement, failure mode, trigger frequency]
controversy: none expected

### Q3
question: "Which search dimensions must a query on ambiguous topics be decomposed into before ingestion?"
level: 1
scope: in: 00_expand intake protocol; out: reflection stage
seeds: workspace-only — stages/00_expand/CONTEXT.md (≥2 distinct academic search dimensions rule)
distractors: bm25_agentic_search_bergum (query reformulation at retrieval time, distinct phase)
target_structure: [minimum dimension count, example pair]
controversy: none expected — RECALL NOTE: workspace-only question; recall scored against
workspace-file hits, not corpus FTS

### Q4
question: "What is the minimum source count for a promoted candidate rule's evidence?"
level: 1
scope: in: reflection/promotion contracts; out: inbox
seeds: 00_06_self_correction_grounding_requirement, 00_07_critic_external_tool_verification; workspace: stages/05_evict/CONTEXT.md, scripts/check_promotion.py
pinned_query: "grounding requirement critic" + "evidence citations minimum promotion"  # B0.2 pin (2026-09-24): two pinned single-step queries, combined pool
distractors: 50_harness_starter_kit (single-agent review fallback, adjacent)
target_structure: [number, rationale, where enforced]
controversy: none expected

---

## L2 — Multi-source synthesis (Q5–Q8)

### Q5
question: "How do the lab's accepted principles jointly constrain what a research agent may promote?"
level: 2
scope: in: reflection/memory.md rules + stage contracts; out: unverified candidates
seeds: 00_reflection_retrieval_dominates_write, 00_reflection_reorientation_cost, 00_agent_memory_hierarchies; workspace: reflection/memory.md (5 accepted rules)
pinned_query: "reflection accepted rule candidates" + "agent memory hierarchies" + "retrieval dominates write"  # B0.2 pin v3 (2026-09-24): 3-query pool after gateway per-kind reservation fix; v2 recalled 1/4
distractors: 00_reflection_compaction_variance
target_structure: [rule list, overlap map, joint obligation]
controversy: breadth-rule vs depth-rule tension (retrieval-first vs skeletal-first)

### Q6
question: "Synthesize the evidence on when lightweight file-based agent loops beat heavyweight frameworks."
level: 2
scope: in: karpathy minimalist harness + software factory chunks; out: framework marketing
seeds: 00_karpathy_minimalist_agentic_coding_harnesses, 02_00_software_factory_isolate_build_prove_ship
pinned_query: "karpathy minimalist agentic coding harnesses" + "software factory machine gate proof receipt merge gate"  # B0.2 pin v3 (2026-09-24): v2's second query ("...isolate build prove ship") recalled sibling part 00_00 (part 1/4) for seeded 02_00 (part 3/4) — DB1-F3; v3 pins part-3/4-specific terms (verified via ask.py: 02_00 ranks #1). History: v1 single query hit only 00_deep_analysis (adjacent, missed seed); v2 = two pinned queries covering both seeds
distractors: 24_agentforce_harnessing_the_agency_of_ai_to_scale (opposing scale argument), 63_graph_engineering_for_agentic_ai_systems_ken_hua
target_structure: [conditions for lightness, counterexamples, cost evidence]
controversy: YES — scaling claims (agentforce) vs minimalism (karpathy)

### Q7
question: "What do session-compaction and context-rot research say about where agents lose state, and what mitigations does this lab actually implement?"
level: 2
scope: in: compaction research + planning-with-files findings; out: unadopted features
seeds: 00_session_compaction_for_ai_agents, 01_session_compaction_for_ai_agents, 00_plan_persistence_context_window_compaction, 00_reflection_reorientation_cost
pinned_query: "session compaction context window state loss" + "plan persistence external state context window" + "reorientation cost"  # B0.2 pin v1 (2026-09-24, E-suite addendum): all 3 verified via ask.py (top-1 hits each seed family; 01_session_compaction as part-sibling per D7)
distractors: 00_workspace_rapid_understanding, 12_full_walkthrough_workflow_for_ai_coding_matt_poc
target_structure: [failure inventory, adopted mitigations, unadopted, why]
controversy: none expected

### Q8
question: "What does the eval-maturity literature (Braintrust) imply for how this lab should score its own experiments?"
level: 2
scope: in: Braintrust ingestion + reflection metrics; out: external eval platforms
seeds: 01_new_markdown_file (LLM-judge eval chunks), 335_graph_engineering_for_agentic_ai_systems_ken_hua (eval-set-as-distribution), 00_deep_analysis_popular_autoresearch_projects
pinned_query: "eval maturity llm judge human annotation" + "graph engineering eval set distribution" + "autoresearch projects deep analysis"  # B0.2 pin v1 (2026-09-24, E-suite addendum): verified via ask.py; third pin recalls 01_deep_analysis (part-sibling of seeded 00_ — D7 class)
distractors: bm25_agentic_search_bergum
target_structure: [maturity levels, which level VERA scorecard occupies, gap]
controversy: LLM-as-judge reliability vs human rubric

---

## L3 — Conflicting evidence (Q9–Q12)

### Q9
question: "Do the corpus's sources agree on whether write-time summarization is acceptable for research knowledge? Present both sides and the lab's resolution."
level: 3
scope: in: retrieval-breadth rule + summarization-heavy chunks; out: note-taking apps
seeds: 00_reflection_retrieval_dominates_write (anti-side), 01_session_compaction_for_ai_agents (avoid lossy LLM summarization — aligned), 00_reflection_compaction_variance (prefers deterministic gates, nuanced)
distractors: 00_agent_memory_hierarchies
target_structure: [side A, side B, evidence quality per side, lab's decision + why]
controversy: YES — core tension (retrieval-first vs distillation)

### Q10
question: "Compare the evidence that peer review (automated) reduces hallucination vs. the evidence that self-correction loops are sufficient. Where do sources conflict?"
level: 3
scope: in: automated peer review, self-correction, critic-verification chunks; out: human-only review
seeds: 00_automated_peer_review_and_self_correction, 00_06_self_correction_grounding_requirement, 00_07_critic_external_tool_verification
pinned_query: "evaluation agent inspects artifacts specifications" + "ungrounded self-correction degrades performance"  # B0.2 pin v1 (2026-09-24, E-suite addendum): verified via ask.py; first pin needed chunk-body terms (title-terms rank the same-source frontier chunk instead); second pin recalls 01_06 (part-sibling of seeded 00_06 — D7 class)
distractors: 24_agentforce_harnessing_the_agency_of_ai_to_scale (peer-scaling, not verification)
target_structure: [claim table with citations, conflict points, resolution]
controversy: YES

### Q11
question: "What does the corpus say about the reliability of BM25 for long documents — and does it conflict with the claim that lexical retrieval is the foundation of the lab's retrieval?"
level: 3
scope: in: BM25 agentic search research + lab retrieval contracts; out: vector-DB marketing
seeds: bm25_agentic_search_bergum, 00_reflection_retrieval_dominates_write, 00_graph_database_architectural_reflection
pinned_query: "bm25 agentic search query tuning bergum" + "retrieval dominates write reflection"  # B0.2 pin v1 (2026-09-24, E-suite addendum): verified via ask.py (top-1 hits both seeds; 00_graph_database_architectural_reflection is the third seed, reachable in deeper-mode pools)
distractors: 335_graph_engineering_for_agentic_ai_systems_ken_hua
target_structure: [BM25 findings, parameter caveats, conflict points, lab position]
controversy: partial — long-doc BM25 tuning claims vs lab's flat use

### Q12
question: "Two corpus lines argue opposite positions on agent planning autonomy (out-plan-a-senior-engineer vs failure-taxonomy). Map the disagreement."
level: 3
scope: in: capability claims vs failure-mode taxonomies; out: benchmarking methodology
seeds: 00_can_an_ai_out_plan_a_senior_engineer, 00_taxonomy_of_20_ai_research_failure_modes
pinned_query: "AI out-plan senior engineer design docs" + "taxonomy failure modes autonomous research"  # B0.2 pin v1 (2026-09-24, E-suite addendum): verified via ask.py (top-1 hits both seeds)
distractors: 07_working_effectively_with_legacy_code_michael_c_f, 15_the_pragmatic_programmer_20th_anniversary_editio
target_structure: [claims, evidence, disagreement structure, safe-use boundary]
controversy: YES

---

## L4 — Causal / methodological (Q13–Q16)

### Q13
question: "According to the causal-falsification rule, what interventional tests must an experiment pass before a hypothesis is promoted? Spec the minimum test set for a retrieval improvement."
level: 4
scope: in: causal-falsification rule + experiment design; out: general stats
seeds: 240_the_book_of_why_the_new_science_of_cause_and_eff, 365_the_book_of_why_the_new_science_of_cause_and_eff, 00_07_critic_external_tool_verification; workspace: reflection/memory.md (causal-falsification-loops rule)
distractors: 01_new_markdown_file (process, not causation)
target_structure: [required probes, negative controls, observable outputs, promotion gate]
controversy: none — application question

### Q14
question: "Causal chain: how does ungrounded self-correction propagate errors into stage contracts in this lab? Identify the intervention point where the lab breaks the chain."
level: 4
scope: in: self-correction grounding rule + 04_reflect/06_meta_evolve contracts; out: other labs
seeds: 00_06_self_correction_grounding_requirement, 00_07_critic_external_tool_verification, 00_automated_peer_review_and_self_correction; workspace: stages/06_meta_evolve/CONTEXT.md
distractors: 02_agentic_git_discipline_patterns (unrelated safety surface)
target_structure: [chain steps, observed failure instances, intervention point, evidence]
controversy: none — mechanism question

### Q15
question: "Methodologically: does the 2-Action Rule reduce context-rot incidents, and how would you design the ablation to prove it rather than assume it?"
level: 4
scope: in: planning-file research + long-session failure data; out: short tasks
seeds: 00_plan_persistence_context_window_compaction (context rot + 18-study data), 50_graph_engineering_for_agentic_ai_systems_ken_hua (context rot definition), 00_reflection_reorientation_cost
distractors: 15_the_pragmatic_programmer_20th_anniversary_editio (software rot, metaphor only)
target_structure: [hypothesis, confounds, minimal ablation, metric, negative control]
controversy: none — method design question

### Q16
question: "The lab uses deterministic graph fingerprints as provenance. Causally: which provenance defects does that rule actually prevent, and which does it not?"
level: 4
scope: in: CI/manifest CRLF history + fingerprint contracts; out: git mechanics
seeds: 00_icm_implementation_pitfalls_and_failure_modes (fingerprint staleness & re-stamping deadlocks), 02_00_software_factory_isolate_build_prove_ship, 02_agentic_git_discipline_patterns
distractors: 50_icm_knowledge_big
target_structure: [defect list, prevented vs not, evidence from CI incidents]
controversy: none — attribution question

---

## L5 — Open research proposals (Q17–Q20)

### Q17
question: "Propose a concrete experiment to determine at what corpus size lexical retrieval degrades enough to require semantic retrieval. Ground every design choice in corpus sources."
level: 5
scope: in: retrieval research + graph scaling chunks; out: vendor claims
seeds: bm25_agentic_search_bergum (long-doc parameter tuning), 335_graph_engineering_for_agentic_ai_systems_ken_hua (scale/eval-set discussion) — PARTIAL: no dedicated corpus-size-degradation chunk; design choices lean on these two + workspace retrieval contracts. RECALL is intentionally low here; judged on depth not recall.
distractors: 00_workspace_rapid_understanding (token efficiency, not retrieval scaling)
target_structure: [hypothesis, variables, baselines, stopping rule, negative control, cost]
controversy: none — proposal quality judged on grounding depth

### Q18
question: "Propose how this lab could measure its own 'research quality' over time using only in-corpus evidence, and what would falsify that measure."
level: 5
scope: in: eval-maturity + reflection meta-rules; out: external leaderboards
seeds: 335_graph_engineering_for_agentic_ai_systems_ken_hua (eval set as distribution), 01_new_markdown_file (LLM-judge caveats), 00_deep_analysis_popular_autoresearch_projects
distractors: 00_reflection_compaction_variance (slop hygiene, not quality)
target_structure: [measure, units, drift check, falsification condition]
controversy: none — proposal

### Q19
question: "Design a multi-agent debate protocol (if one is warranted) for contested L3 questions: roles, rounds, referee criteria, and the stopping condition under which debate adds nothing."
level: 5
scope: in: multi-agent debate research + Q9–Q12 controversy map; out: fixed 3-agent folklore
seeds: 00_agentic_auto_research_frontier_10_sources (AgentVerse dynamic multi-agent consensus), 10_harness_r1_learning_to_edit_executable (divergent thinking via multi-agent debate), 452_multiagent_systems_algorithmic_game_theoretic_an
distractors: 24_agentforce_harnessing_the_agency_of_ai_to_scale (scale, not debate)
target_structure: [roles, round budget, referee rubric, null-effect stopping rule]
controversy: by design — tests whether debate is worth it

### Q20
question: "Propose the promotion criteria for VERA experiment results themselves (what makes a mechanism 'wins' vs 'ceremony') and show them applied to one hypothetical result set."
level: 5
scope: in: causal-falsification rule + W-DEEP evidence standards; out: journal norms
seeds: 00_07_critic_external_tool_verification (ablation that quantifies grounding), 00_deep_analysis_popular_autoresearch_projects, 00_automated_peer_review_and_self_correction; workspace: stages/05_evict/CONTEXT.md
distractors: 02_agentic_git_discipline_patterns (gate hygiene, not promotion criteria)
target_structure: [criteria, thresholds, worked example both directions]
controversy: none — meta question

### Q21
question: "Which stage gates in this lab are load-bearing vs ceremonial, per ablation?"
level: 4
scope: in: lab gate architecture + minimalism/performance evidence; out: other labs' gate sets
seeds: 00_karpathy_minimalist_agentic_coding_harnesses, 00_why_performance_engineering_breaks_ai_coding_agent, 01_00_bend2_vibe_coding_reinventing_wheels; workspace: runs/SIM1_arms.md, runs/GATE_ABLATION_Q13Q14.md
distractors: 24_agentforce_harnessing_the_agency_of_ai_to_scale (scaling argument, opposing simplicity)
pinned_query: "minimalist harnesses performance loop"
target_structure: [gate inventory, ablation evidence per gate, ceremonial set, removal order]
controversy: minimalism vs managed-harness (karpathy/bend2 vs agentforce)

### Q22
question: "Causal chain: how does reorientation cost convert into performance loss for a fresh agent session?"
level: 4
scope: in: reorientation-cost rule + rapid-understanding research; out: compaction mechanics
seeds: 00_reflection_reorientation_cost, 00_workspace_rapid_understanding
distractors: 00_session_compaction_for_ai_agents (adjacent lever, different mechanism)
pinned_query: "reorientation cost"
target_structure: [chain steps, measurable proxies, intervention point, falsification probe]
controversy: none — mechanism question

### Q23
question: "Design the single-graph read path for all lab stages: spec the gateway API, the no-direct-file-read policy, and the exceptions list."
level: 5
scope: in: gateway primitive + context-gateway pattern; out: DB-engine internals
seeds: 00_graph_database_architectural_reflection, 02_00_software_factory_isolate_build_prove_ship; workspace: knowledge/graph/context_gateway.py
distractors: 76_graph_databases_new_opportunities_for_connected (DB theory, not this lab)
pinned_query: "graph database architectural reflection"
target_structure: [API surface, policy text, exceptions, freshness guarantee, cost budget]
controversy: by design — conditional DB-1 verdict is the input

---

## Phase-2 additions log (P2-4, 2026-09-24)

- Q21–Q23 annotated per Phase-2 direction (simplicity + understandability + DB merge);
  seeds verified via ask.py on this date; note: 00_00_bend2 / 01_00_bend2 duplicate pair
  confirmed as the third 00_/01_ duplicate-ingestion instance (seed_annotation finding 1).
- Question count is now 23; freeze rule applies from the next Phase-1 green.

## Annotation log (V1 — completed 2026-09-24)

- All 24 distinct chunk IDs above verified present in knowledge/corpus/ via
  `python knowledge/graph/ask.py` resolution + `dir knowledge\corpus`.
- Unresolvable after two attempts: "trust tiers" as corpus FTS (resolved via the OKF
  methodology chunk), "query decomposition dimensions" (workspace-only → Q3 marked),
  "minimum citation count" (workspace contract → Q4 marked), "corpus size degradation"
  (no dedicated chunk → Q17 marked PARTIAL). None abandoned: all found a valid source
  path (corpus or workspace) on retry.
- Log: reports/seed_annotation.md

## Maintenance rules

- Benchmark questions are FROZEN once Phase 1 goes green; edits create new question IDs, never in-place mutation.
- Any corpus ingestion after freezing invalidates seed annotations only if seed IDs change — re-run the checklist, log it.
- A question with zero resolvable seeds after two attempts is ABANDONed (protocol in task_plan.md), not silently dropped.
