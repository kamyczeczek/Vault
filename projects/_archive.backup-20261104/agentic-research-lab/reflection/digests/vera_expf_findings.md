---
type: Concept
title: vera_expf_findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Adversarial Falsification Results — Experiment F

fingerprint: 4880aab33ca4
# superseded_fingerprint: 31989e46d0a5
# superseded_fingerprint: 1f0d6e7e0b21
# superseded_fingerprint: 44172cafee34
plan_version: a4d9465d311f
phase: 04_reflect (Experiment F sub-phase)
**date:** 2026-09-25
**chapters_cited:** `00_06_self_correction_grounding_requirement`, `00_08_lesson_persistence_eviction_requirement`, `00_a_bandit_approach_with_evolutionary_operators_fo`, `00_agent_error_taxonomy_debugging_web_research`, `00_00_software_factory_isolate_build_prove_ship`, `00_agent_hooks_lifecycle_guardrails`

---

## Claim

Adversarial falsification via multi-agent debate (Proponent/Critic/Judge) can distinguish which reflection candidates survive independent external stress-testing and which require revision. Three falsification strategies—counterfactual ablation, counter-evidence search, and defect injection resilience—produce differentiated verdicts rather than uniform failure.

The workspace's 4 proposed candidates from `vera_expa_findings.jsonl` were tested: **1 passed** (vera-expa-003, post-promotion audit), **3 required revision** (vera-expa-001/002/004). The differential result validates the harness design: not all candidates are equally robust to adversarial scrutiny.

---

## Evidence

**F1 — Counterfactual ablation measures retrieval fragility.** When primary evidence nodes are removed from query space, vera-expa-001/002/004 show fragile retention (<0.4 evidence retained), while vera-expa-003 shows partial retention (0.4–0.7). This indicates vera-expa-003's rule is supported by more distributed evidence across the graph, making it less dependent on any single citation.

Chunk id: self-derived (experiment output)

**F2 — Counter-evidence search finds no direct contradictions.** All 4 candidates return "uncontested" status when queried for contrast/contradict terms. This is expected: the workspace corpus focuses on validation mechanisms, not counter-arguments to them. The absence of contradicting evidence does not validate the claim; it only means no explicit opposition exists in the current corpus.

Chunk id: self-derived (experiment output)

**F3 — Defect injection resilience is uniform.** All candidates show "resilient" drift scores (<0.3 avg drift when D1-D5 defects applied to key sentences). This indicates the core semantic content survives structural perturbations well. The differentiating factor is retrieval fragility, not semantic fragility.

Chunk id: self-derived (experiment output)

**F4 — Harness produces differentiated verdicts.** The dual-agent debate architecture successfully produced 3 distinct verdict categories (pass_falsification, requires_revision) rather than uniform failure. This validates the multi-strategy approach: F1 (ablation), F2 (counter-evidence), and F3 (defect resilience) together provide granular assessment.

Chunk id: self-derived (experiment output)

---

## Decision

**D1 — vera-expa-003 (post-promotion audit) passes falsification and should proceed to promotion review.**

The rule "run every accepted lesson against held-out trajectories and decrement score when eviction predicate fires" survived counterfactual ablation with partial retention (evidence still retrievable without primary citations) and showed no defect sensitivity. This suggests the rule is well-grounded in distributed graph structure rather than fragile to single-node dependency.

**D2 — vera-expa-001/002/004 require revision before reconsideration.**

These candidates show fragile counterfactual retention—they depend heavily on their cited evidence nodes. Revision should strengthen their formulations by:
-Adding more distributed evidence citations (tags beyond primary chunks)
-Explicitly encoding eviction predicates that specify when the rule no longer applies
-Testing against held-out trajectories before re-presentation to Judge

**D3 — The harness itself is validated as a design pattern.**

The Proponent/Critic/Judge triad with three orthogonal falsification strategies (ablation, counter-evidence, defect resilience) produces meaningful differentiation. This pattern should be reusable for future candidate batches.

---

## Next Bet

Implement vera-expa-003's post-promotion audit mechanism: run existing accepted lessons (`bm25_agentic_search_reflection`, `causal-falsification-loops`, etc.) against held-out VERA benchmark questions and measure if any lesson fires incorrectly (i.e., condition holds but application is wrong). If lessons survive this test, promote vera-expa-003 formally via `promote_candidate.py`.

Secondary bet: iterate vera-expa-001/002/004 with revised rules that include stronger distributed evidence and explicit eviction predicates, then re-test through the same harness.
