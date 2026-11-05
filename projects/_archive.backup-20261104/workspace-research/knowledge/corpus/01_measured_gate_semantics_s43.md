---
type: Concept
id: 01_measured_gate_semantics_s43
title: "Measured Lesson — Fused Acceptance Gates Hide Decision-Theoretic Holes (h720 S-43) (part 2/2)"
source: "measured_gate_semantics_s43.md"
tags: [evaluation, gate-semantics, pre-registration, reflection]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---
taxonomy: #gate-semantics #evaluation #pre-registration
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
