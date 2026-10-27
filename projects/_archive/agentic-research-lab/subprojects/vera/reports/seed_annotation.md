---
type: Concept
title: seed_annotation
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Seed Annotation Log — V1

Date: 2026-09-24 · Annotator: Goose (Sapiens AI) · Corpus fingerprint at annotation: `05bc79e4b41e`
Method: `python knowledge/graph/ask.py "<topic>"` → ID verified by existence check in `knowledge/corpus/`.
Workspace-only questions (Q3, Q4 partial, Q13/Q20 partial) cite stage contracts instead of corpus recall.

## Resolved IDs (24 distinct, all verified)

00_okf_methodology_research · 00_reflection_reorientation_cost · 01_session_compaction_for_ai_agents ·
00_workspace_rapid_understanding · 00_agent_memory_hierarchies · 00_reflection_compaction_variance ·
00_karpathy_minimalist_agentic_coding_harnesses · 02_00_software_factory_isolate_build_prove_ship ·
24_agentforce_harnessing_the_agency_of_ai_to_scale · 63_graph_engineering_for_agentic_ai_systems_ken_hua ·
00_session_compaction_for_ai_agents · 00_plan_persistence_context_window_compaction ·
12_full_walkthrough_workflow_for_ai_coding_matt_poc · 01_new_markdown_file ·
335_graph_engineering_for_agentic_ai_systems_ken_hua · 00_deep_analysis_popular_autoresearch_projects ·
00_reflection_retrieval_dominates_write · 00_automated_peer_review_and_self_correction ·
00_06_self_correction_grounding_requirement · 00_07_critic_external_tool_verification ·
50_harness_starter_kit · bm25_agentic_search_bergum · 00_graph_database_architectural_reflection ·
00_can_an_ai_out_plan_a_senior_engineer · 00_taxonomy_of_20_ai_research_failure_modes ·
07_working_effectively_with_legacy_code_michael_c_f · 15_the_pragmatic_programmer_20th_anniversary_editio ·
240_the_book_of_why_the_new_science_of_cause_and_eff · 365_the_book_of_why_the_new_science_of_cause_and_eff ·
00_icm_implementation_pitfalls_and_failure_modes · 02_agentic_git_discipline_patterns ·
50_graph_engineering_for_agentic_ai_systems_ken_hua · 50_icm_knowledge_big ·
00_agentic_auto_research_frontier_10_sources · 10_harness_r1_learning_to_edit_executable ·
452_multiagent_systems_algorithmic_game_theoretic_an

## Retries that changed outcome (two-attempt rule applied)

| Topic | Failed phrasings | Succeeded via |
|---|---|---|
| trust tiers | "trust tiers evidence levels tier 3" | "trust_tier provenance tiers raw intake attested" → 00_okf_methodology_research |
| causation | "causal falsification ablation", "book of why causation ablation intervention" | single-term "causation"/"intervention" → 240_…/365_… Book of Why chunks |
| fingerprint | "graph fingerprint deterministic provenance rebuild" | "fingerprint" → 00_icm_implementation_pitfalls… |
| second evidence | "second citation evidence rule single evidence rejected" | unresolved → Q4 marked workspace-only (contract + check_promotion.py), not abandoned |

## Findings for the lab (recorded per 2-Action Rule)

1. `reflection/memory.md` cites `365_the_book_of_why_…` — the file exists, but FTS ranks the
   Book of Why chunks under the 240- range; the 365 prefix suggests the same source was ingested
   twice under different numbers. Possible duplicate-ingestion artifact worth an eviction check.
2. `01_new_markdown_file` is a chunk carrying real eval-judge content under a boilerplate
   filename — acceptable for recall scoring, but its title will degrade human readability of
   reports citing it. Candidate rename during next maintenance pass (IDs must stay stable).
3. Q17 has no corpus-size-degradation chunk: the benchmark deliberately exposes this coverage
   gap — L5 questions are where retrieval-breadth rule says to keep the lossless source and
   retrieve iteratively. Noted, not fixed (out of scope for Phase 1).

## V1 verdict

PASS — 20/20 questions have seeds + ≥1 distractor + target_structure + level. Q3/Q4/Q13/Q20
carry explicit `workspace:` markers so recall scoring uses the right source set.

## Correction (2026-09-24, eviction pass via metrics/tools/find_duplicate_chunks.py + title inspection)
- Finding 1 (suspected duplicate ingestion of 365_/240_ and 00_/01_ pairs) is RETRACTED: the pairs are legitimate part-splits.
- Titles prove it: 00_06 = part 1/2, 01_06 = part 2/2; 00_07/01_07 and 00_00_bend2/01_00_bend2 follow the same pattern; 240_book_of_why = part 241/386 and 365_book_of_why = part 366/386 (non-overlapping segments of one 386-part source).
- No chunks evicted: no duplicate content exists in the corpus. Verdict: EVICTION NOT NEEDED. Root cause of the false alarm: single-title reads without part numbers.
