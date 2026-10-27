---
type: Concept
title: measured_gate_semantics_s43
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Measured Lesson — Fused Acceptance Gates Hide Decision-Theoretic Holes (h720 S-43)

## What was measured

On the h720 ETTh1 H=720 forecasting benchmark, a candidate (Bet 3, level-free PatchTST-Delta
non-linear encoder, 3-member ridge blend) passed **every project-level promotion condition**
and was **nonetheless REJECTED**, with the model family formally closed.

Both facts are simultaneously true in one artifact, which is the finding.

## The numbers (from `results_patchtst_bet3.json`, frozen protocol, seed 0)

| Condition | Threshold | Value | Result |
|---|---|---|---|
| Blend full MAE | ≤ 1.9859 | 1.978126 | PASS |
| Blend full MAE vs incumbent | < 1.9909 (S-26) | 1.978126 | PASS |
| Blend disjoint-4 MAE | ≤ 1.9696 | 1.863419 | PASS |
| Hardest-window W4 | ≤ 1.90 | 1.889616 | PASS |
| Held-out val gain over control | > 0.005 | +0.020368 | PASS |
| **Singleton PatchTST val** | **≤ 2.90** | **3.026725** | **FAIL** |
| **Train-val gap** | **< 0.15** | **0.179497** | **FAIL** |

Verdict: `REJECT (close family)`.

## Root cause — two logically distinct gates fused into one chain

The spec fused a **singleton-capability screen** ("the member architecture cannot stand alone
against the incumbent") and a **blend-promotion gate** ("the stacked ensemble is a better
predictor") into a single `all must hold` acceptance list:

```
accepted = accept_full and accept_disj and accept_w4 and accept_heldout and accept_reg
```

These two gates can **disagree by construction**. The spec never named a precedence, and never
said what happens when they disagree. A candidate whose *blend* is promotion-grade is rejected
whenever its *member* is screen-grade — even though the two are statements about different
objects.

The singleton screen is a claim about the member architecture in isolation. The blend gate is a
claim about the stacked ensemble. Neither implies the other.

## Why the mean passing is not evidence the family is bad

The aggregate `full` MAE is a 2161-origin mean. The attention member helps most origins and
degrades the seasonally hardest window (W4, spring 2018 — the documented hardest window for
every model since S-01). A positive mean gain is therefore compatible with a real per-window
regression, and the blend result says nothing about the member in isolation.

The held-out precondition passed on the legitimate selector: S-26 delta-ridge control
2.5225 → best subset 2.5021, gain +0.0204. Selection trace iter 3 (`[nlinear_L336_a1,
nlinear_L336_a10, patchtst_P24_D32_2L]`, true 2.4936) shows the attention member carries signal
the two linear anchors do not span. **The close rests on the singleton screen, not on absence of
signal.**

## The transferable rule

**Declare the binding gate at pre-registration, before the run — including the resolution rule
for when gates disagree.** Specifically:

- Which gate BINDS the promotion decision (singleton-based or blend-based)?
- What is demoted to a non-binding diagnostic (cannot flip PASS → FAIL)?
- What happens to the family close if the promotion succeeds?

An undeclared precedence is invisible until the two gates disagree, at which point the
decision has already been made by accident — by whichever check happened to be last in the
`and` chain.

This generalizes beyond forecasting: any acceptance list mixing "the component works" with
"the assembly works" has the same hole, and the `and` chain silently picks the stricter of the
two without telling anyone it decided.

## Provenance

- Artifact: `projects/ts-ml-experiments/h720/sub_experiments/patchtst_delta_bet3/results_patchtst_bet3.json`
- Harness log: `projects/ts-ml-experiments/h720/sub_experiments/patchtst_delta_bet3/harness.log`
- Reflection: `MONITORING/reflection/2026-09-13_2350_S-43-bet3-terminal-close.md`
- Followup (gate-semantics re-registration): `sub_experiments/blend_promotion_s44/S44_DESIGN.md`
- Protocol frozen before the design document existed; S-44 re-registered gate semantics only.
