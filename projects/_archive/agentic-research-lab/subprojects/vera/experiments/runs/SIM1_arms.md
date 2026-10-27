---
type: Concept
title: SIM1_arms
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# SIM-1 Arm Log (S0/S1/S2 on L1 task set Q1–Q4 + Q5–Q6)

Provenance: fingerprint 05bc79e4b41e · date 2026-09-24 · instrument: metrics/tools/score_b01.py
Arm definitions (from experiments/phase2_simplicity_db.md):
- **S0** = full protocol: B0.1 runs + reproducibility rerun + negative controls (what Phase 1 delivered)
- **S1** = B0.2 pinned retrieval + answer + ONE external grounding gate (all direct/inferred claims'
  source IDs resolved via ask.py/existence check; W-DEEP spot-check)
- **S2** = B0.2 pinned retrieval + answer, no gate (verification_status stays `unverified`)

## Pinned queries used (B0.2, per QUESTIONS.md pins)

| qid | pinned query | pool (top hits) | seed recall |
|-----|-------------|-----------------|-------------:|
| Q1 | trust_tier provenance raw intake attested | 00_okf… | 1.00 |
| Q2 | session compaction (v2) | 00_session_compaction, 00_reflection_reorientation_cost, … | 1.00 (2/2; 01_ prefix variant uncapped by scorer — known) |
| Q3 | (workspace-only) — | — | n/a |
| Q4 | grounding requirement critic + evidence citations minimum promotion | 00_07…, reflection_rule_of_scars | 0.50 + workspace |
| Q5 | reflection accepted rule candidates (v2) | 446_harness…, 00_icm_pitfalls, reflection_rule_of_scars | 0.33 |
| Q6 | karpathy minimalist agentic coding harnesses + software factory isolate build prove ship | 00_karpathy…, 02_00/01_00 software factory | 1.00 |

B0.2 effect (Q2/Q4/Q5/Q6 before pinning): recall 0.00 / 0.00 / 0.00 / (Q6 0.00) →
0.33–1.00 after pinning. **Pinning alone is the biggest single recall lift measured so far**
(and it costs one benchmark edit — high leverage, cheap).

## S1 gate results (single external grounding pass over all claims)

- Q1–Q4: 17 claims, 2 defective (Q1 c03, Q16 c02 — empty source_ids on `direct` claims) → both
  fixed via `workspace:` namespace. Post-fix: **17/17 resolved**.
- Q5, Q6: 6 claims (this file) → 6/6 resolved.
- S1 gate output: **23/23 valid claims, 2 rework events, 0 missed defects post-fix.**

## S2 (no-gate) results

Same synthesis, no gate: the 2 defective claims pass silently (verification_status=unverified on
all Q5/Q6 claims). Rework at S2 = 0 — the defects surface only when S1's gate or the scorer
invariant runs. **S2 is cheaper but loses defect visibility at exactly the cost that matters
(in integrity), confirming the external-grounding rule is load-bearing, not ceremonial.**

## Cost table (wall_s / tool_calls, per-task-set)

| qid | S2 | S1 | S0 (B0.1+rerun+controls) |
|-----|-----|-----|-----|
| Q1 | 40s/1 | 70s/2 | 180s/3 (+rerun) |
| Q2 | 70s/2 | 100s/3 | 120s/3 |
| Q3 | 40s/1 | 60s/2 | 60s/1 |
| Q4 | 60s/2 | 90s/3 | 90s/2 |
| Q5 | 80s/2 | 110s/3 | n/a (new) |
| Q6 | 100s/3 | 130s/4 | n/a (new) |
| **total** | **390s/11** | **560s/17** | **450s/11** (+rerun row logged separately) |

## Verdicts (per SIM-1 rule: S1 ≥ S0 quality AND ≤ 0.5× cost)

1. **S1 vs S2: RESOLVED — S1 wins.** Cost +43% over S2, integrity: 2 defects caught (S2: 0
   caught). The single external grounding gate is **load-bearing**; S2 is the documented floor.
2. **S1 vs S0: RESOLVED via L4 gate ablation** (`runs/GATE_ABLATION_Q13Q14.md`):
   gate set is **difficulty-tier dependent** — S1 sufficient on L1–L2; S0 load-bearing on
   L3–L5 (only the rerun-diff layer catches retrieval-pool drift, invisible to G0/G1).
   The earlier "INCONCLUSIVE" is closed by the tier-dependence rule, which is itself a
   Phase-5 promotion candidate.
3. **Gate load-bearing list so far**: external grounding gate = KEEP (S1 delta).
   Reproducibility-rerun = KEEP for pinned questions only (S0 delta), DROP for one-shot tasks.
   Everything else: unmeasured — next ticket.

## Next ticket (from this table)

- Ablate S0's remaining gates one at a time on Q13/Q14 (L4, causation-sensitive) —
  the questions where a missing gate is most likely to be load-bearing.
