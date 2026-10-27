---
type: Concept
id: idea-discussion-must-be-sealed-as-a-pipe
thesis: Idea discussion must be sealed as a pipeline artifact, not a raw chat transcript
stance: synth
status: unresolved
run_id: idea-2f9c4f1a70c54450
graph_generation: 0a5b47437367
created: 2026-09-28T03:33:32Z
origin: migrated from reflection/idea_sessions/idea-discussion-must-be-sealed-as-a-pipe-20260928033332.json
title: idea-discussion-must-be-sealed-as-a-pipe
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Idea discussion must be sealed as a pipeline artifact, not a raw chat transcript

## claims

## c1 — A discussion surface that produces no pipeline artifact dies or decays
- support: `00_icm_ml_research_workflow`, `01_one_stage_one_job`, `90_llm_engineers_handbook_iusztin_paul_labonne_z_li`
- counter: (none — unrefuted)

## c2 — Paired support and counter retrieval prevents one-sided confirmation
- support: `reflection_rule_of_scars`, `00_guardian_crawler_retrieval_first_knowledge_disco`, `01_layered_ai_work_engineering_control_stack`
- counter: (none — unrefuted)

## c3 — Model self-critique alone is unverifiable and must not promote
- support: `00_06_self_correction_grounding_requirement`, `00_07_critic_external_tool_verification`, `00_00_bend2_vibe_coding_reinventing_wheels`
- counter: (none — unrefuted)

## red-team

### 2026-09-28
Counter-queries over FTS5 lexical retrieval may return topically adjacent but
irrelevant chunks, faking opposition; if the corpus is shallow on a topic, empty
counter sets are the norm, so unfalsified-by-corpus flags will dominate and the
board may read as evidence when it is absence of evidence.

### 2026-09-28 — MIGRATION NOTE
The original session recorded `counter: []` on every claim while its own state
file carried `counter_empty: false` — the retrieved counter ids were discarded
before being written (`idea_session.py:147`), so all 9 evidence ids on the
staged candidate were support-only. The counters above therefore read
"(none — unrefuted)" because the ids were lost, not because the corpus was
silent. Re-retrieve with `python scripts/discuss.py claim` under each claim to
restore the counter side honestly.

## decision
- value: unresolved
- why: All claims grounded; probe accepted as a known FTS5 limitation already mitigated by the W-DEEP depth rule and citation integrity gate
- next: Re-run two-sided retrieval under this convention and measure how often counter sets come back empty versus adjacent-but-irrelevant
