---
type: Concept
title: vera_expf_revision_findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Experiment F Revision Round — Deterministic Ablation & 3-Node Evidence Sets

fingerprint: 4880aab33ca4
# superseded_fingerprint: 31989e46d0a5
# superseded_fingerprint: 1f0d6e7e0b21
# superseded_fingerprint: 44172cafee34
plan_version: a4d9465d311f
phase: 04_reflect (Experiment F revision)
**date:** 2026-09-25
**chapters_cited:** `00_06_self_correction_grounding_requirement`, `00_automated_peer_review_and_self_correction`, `00_08_lesson_persistence_eviction_requirement`, `00_reflection_retrieval_dominates_write`, `00_agent_error_taxonomy_debugging_web_research`, `00_agent_hooks_lifecycle_guardrails`, `00_agent_execution_hooks_guardrails`

---

## Problem with Round 1 F1

Round 1 F1 (counterfactual ablation) had two defects:

1. **Non-determinism.** `list(set)[:4]` picked arbitrary tags from a set, so baseline and modified queries could use different tag subsets across runs, making retention unstable.
2. **Fragility was tag-overlap-driven, not evidence-driven.** When two evidence nodes shared 5 of 6 tags, removing one node's tags barely changed the query (remaining_tags ≈ all_tags), so the test measured tag redundancy, not claim fragility.

Result: all 4 candidates scored identically (`requires_revision`, F1=fragile, F2=uncontested, F3=resilient). No discrimination.

---

## Revision

### R1 — Deterministic ablation query construction
`_test_ablation` now builds both baseline and modified queries from `sorted(tag_set)[:6]` — stable ordering, no set-iteration luck.

### R2 — 3-node evidence sets
Each candidate gained a third evidence node chosen for **tag complementarity** (non-overlapping tag dimensions vs. the original pair):

| Candidate | Added node | New tag dimensions |
|-----------|-----------|-------------------|
| vera-expa-001 | `00_automated_peer_review_and_self_correction` | `evaluation`, `self-evolution`, `workflow-evolution` |
| vera-expa-002 | `00_reflection_retrieval_dominates_write` | `persistence`, `retrieval` |
| vera-expa-004 | `00_agent_execution_hooks_guardrails` | `prompt-engineering` (vs. `determinism` in original) |

### R3 — Remaining query uses union of all *other* nodes
Removal of node X now queries with the union of all remaining nodes' tags, so with 3 nodes the modified query loses only the removed node's unique dimensions.

---

## Results (run 20260925_200556)

| Candidate | F1 retention | F1 status | Verdict | State |
|-----------|-------------|-----------|---------|-------|
| vera-expa-001 | 0.542 | partial | **pass_falsification** | proposed → experimental |
| vera-expa-002 | 0.333 | fragile | **requires_revision** | proposed (unchanged) |
| vera-expa-003 | 0.550 | partial | **pass_falsification** | accepted (round 1) |
| vera-expa-004 | 0.593 | partial | **pass_falsification** | proposed → experimental |

F2 and F3 unchanged: uncontested / resilient across all four.

Distribution now discriminating: 3 pass, 1 still fragile.

---

## Evidence

**E1 — vera-expa-001 now passes with evaluation/self-evolution complementarity.**
`00_automated_peer_review_and_self_correction` contributes `evaluation`, `self-evolution`, `workflow-evolution` — dimensions absent from the original pair's `agentic/agents/memory/planning/prompt-engineering/reflection` overlap. Retention rose 0.0 → 0.542.

Chunk id: `00_automated_peer_review_and_self_correction`, `00_06_self_correction_grounding_requirement`

**E2 — vera-expa-002 still fragile; tag complementarity alone is insufficient.**
`00_reflection_retrieval_dominates_write` adds `retrieval`/`persistence`, but the two remaining nodes' tags still fully contain a strong subset of the removed node's tags, so the modified query still retrieves the same dense result set minus the removed node — retention 0.333.

This is the correct discrimination, not a harness bug: the rule's original evidence pair is genuinely redundant. Fix path: replace one original node with an orthogonal-dimension source, not add a third.

Chunk id: `00_08_lesson_persistence_eviction_requirement`, `00_reflection_retrieval_dominates_write`

**E3 — vera-expa-004 passes with prompt-engineering complementarity.**
`00_agent_execution_hooks_guardrails` contributes `prompt-engineering` against the original pair's `determinism`-centered overlap. Retention 0.033 → 0.593.

Chunk id: `00_agent_execution_hooks_guardrails`, `00_agent_error_taxonomy_debugging_web_research`

---

## Decision

**D1 — 001 and 004 promoted to experimental.**
Both passed with F1 partial (retention >0.4). Next gate: post-promotion audit before formal acceptance (per vera-expa-003, now accepted in memory.md).

**D2 — 002 stays proposed; revision path is node replacement, not node addition.**
The fragility is structural (redundant pair), not a third-node gap. Revise by replacing `00_06_self_correction_grounding_requirement` with a node whose tags overlap minimally with `00_08_lesson_persistence_eviction_requirement`, then re-run.

**D3 — Deterministic ablation is now the canonical F1.**
`_test_ablation` uses sorted tag selection; future runs are reproducible on the frozen fingerprint.

---

## Next Bet

1. Replace one node in vera-expa-002's evidence pair (candidate: swap grounding-requirement for a lesson-provenance source), re-run
2. Run post-promotion audit on 001 and 004 before acceptance
