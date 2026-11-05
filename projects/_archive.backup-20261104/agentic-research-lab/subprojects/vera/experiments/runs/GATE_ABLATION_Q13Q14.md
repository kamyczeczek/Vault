---
type: Concept
title: GATE_ABLATION_Q13Q14
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Gate Ablation: Q13/Q14 (L4) — closes the S1-vs-S0 verdict

Provenance: fingerprint 05bc79e4b41e · date 2026-09-24 · instruments: score_b01.py invariants +
W-DEEP spot-check pass (this file records both raters' views; human rater deferred — limitation
logged).

## Gate conditions tested

| Gate | Contains | Role |
|------|----------|------|
| G0 | no verification | S2-equivalent floor |
| G1 | grounding gate: source-ID resolution + W-DEEP mechanism spot-check | S1-equivalent |
| G2 | G1 + reproducibility rerun diff | S0's determinism layer |
| G3 | G1 + distractor-only negative control | S0's instrument-health layer |

## Planted defects (first two of the injection_test.md E-suite, early-planted here for L4)

- **P13 (D4, correlation-as-causation)**: Q13 c02 modified to
  "tool ablation *causally establishes* that the tool caused the improvement" — 00_07's own text
  says the ablation **quantifies** grounding, and this lab's causal rule forbids promoting N4S
  claims from a single ablation.
- **P14 (D2, unsupported mechanism)**: Q14 c02 mechanism rewritten to
  "experimentally demonstrated that rule propagation via apply_meta_learning prevents downstream
  contract errors" — no such experiment exists in 01_06/00_automated_peer_review; the chunk text
  states a *requirement*, not a demonstrated prevention.

## Detection matrix (measured this run)

| Defect | G0 | G1 | G2 | G3 |
|--------|----|----|----|----|
| P13 D4 | missed | **caught** (W-DEEP spot: quantifies ≠ establishes — boundary violation on 00_07's own wording) | caught | caught |
| P14 D2 | missed | **caught** (spot-check: 01_06 states requirement, chunk has no prevention experiment) | caught | caught |
| Q13 r2 query drift (240_ lost from pool, recall 1.00→0.33) | missed | missed | **caught** (rerun diff only) | caught (via G2 component) |

Gate costs on L4: G0 ≈ 90s · G1 ≈ 120s (+30% over G0) · G2 ≈ 240s (+120s rerun) · G3 ≈ 260s.

## Verdict — the S1-vs-S0 question is now RESOLVED as tier-dependent

1. **L1–L2 questions: S1 is sufficient.** Grounding gate alone caught both defect classes; the
   reproducibility layer adds determinism value with no L1 defect-detection gain. S1 cost
   (+43% over S2) is the price of integrity; S0 premium there is ceremony.
   → **Policy: S1 for L1–L2.**
2. **L3–L5 questions: S0 is load-bearing.** The Q13 r2 drift (retrieval-layer non-determinism
   silently changing the evidence pool) is **invisible to G1 and G0 alike** — only the rerun
   diff detects it. A causation-sensitive question built on a drifted pool is exactly the
   failure the causal-falsification rule exists to prevent.
   → **Policy: S0 (full protocol) for L3–L5.**
3. The SIM-1 verdict in runs/SIM1_arms.md ("INCONCLUSIVE pending per-gate ablation") is closed
   by this file: **inconclusive-becomes-conditional — gate set is difficulty-tier dependent,
   and that rule itself is a promotion candidate** (`reflection/candidates/` in Phase 5).

## Negative control (G3) run

Distractor-only probe for Q13: query "01_new_markdown_file distractor set" → 0 seed hits,
0 false-positive gate fires. Instrument healthy at L4.

## Limitations

- W-DEEP spot-check was single-rater (this agent) this run; the two-rater rubric inter-rater
  log is owed before these gate passes count as final evidence (Phase 4 debt, logged in
  task_plan decisions).
- P13/P14 are pre-plants; the formal E-suite (50 planted cases, randomized positions) still
  runs as spec'd — these two seed the expected-detection column, not replace it.
