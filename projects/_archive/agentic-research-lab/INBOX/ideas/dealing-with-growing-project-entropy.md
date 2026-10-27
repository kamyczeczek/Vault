---
type: Concept
id: dealing-with-growing-project-entropy
thesis: Dealing with growing project entropy — drift is silent, gates catch known drift, scar memory prevents recurrence
stance: synth
status: unresolved
run_id: idea-01557e5e3aa1465e
graph_generation: 0a5b47437367
created: 2026-09-28T03:58:59Z
origin: migrated from reflection/idea_sessions/dealing-with-growing-project-entropy-dri-20260928035859.json
title: dealing-with-growing-project-entropy
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Dealing with growing project entropy

## claims

## c1 — Project entropy accumulates silently: drift happens a day at a time
- support: `18_the_pragmatic_programmer_20th_anniversary_editio`, `73_harness_starter_kit`, `166_icm_knowledge_big`
- counter: (none — unrefuted)

## c2 — Deterministic gates are the only mechanism that catches drift without human vigilance
- support: `01_taxonomy_of_20_ai_research_failure_modes`, `00_agentic_git_discipline_patterns`, `01_00_software_factory_isolate_build_prove_ship`
- counter: (none — unrefuted)

## c3 — Failing surfaces that leave no artifact decay or die, so remedies must produce staged artifacts
- support: `09_the_five_level_verification_ladder`, `00_icm_ml_research_workflow`, `00_measured_liveness_not_consistency`
- counter: (none — unrefuted)

## c4 — Every extra surface is itself an entropy source: each is a copy that drifts
- support: `122_cerebras_knowledge_base_second_brain`, `895_artificial_intelligence_a_modern_approach_4th_ed`, `244_icm_knowledge_big`
- counter: (none — unrefuted)

## red-team

### 2026-09-28
Gates only catch the drift classes they were written for; novel entropy (stale
MAP.md, gate self-drift, unused gates) passes unseen. A gate that is not run
every session is indistinguishable from a gate that does not exist. Execution
frequency is the bottleneck, not detection power. The corpus's own evidence
(frog in the pan, broken windows) argues that the first failure mode is
noticing, and a static list of gates cannot notice new drift classes.

### 2026-09-28 — MIGRATION NOTE
As with the sibling session, the original recorded `counter: []` on every claim
while its state file carried `counter_empty: false`: the retrieved counter ids
were discarded at `idea_session.py:147`, so all 12 evidence ids on the staged
candidate were support-only. The "(none — unrefuted)" markers above record a
lost id list, not a silent corpus.

## decision
- value: unresolved
- why: problem and gates are grounded; execution-frequency failure mode is not yet covered by any existing gate
- next: Measure gate coverage — list every drift class found in the last 30 days of archive and ledger sessions, tag each with the gate that would have caught it, and report classes with zero coverage as candidates for a new check
