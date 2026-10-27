---
type: Concept
id: 01_measured_aggregate_mean_hides_per_window
title: "Measured Lesson — A Regression Hidden by the Mean Was Measured Against the Wrong Baseline (h720 S-43 P2) (part 2/2)"
source: "measured_aggregate_mean_hides_per_window.md"
tags: [evaluation, forecasting, reflection, stale-baseline]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---
taxonomy: #evaluation #stale-baseline #forecasting
- If a gate says "beat the incumbent", the incumbent must be derived from the harness, not
  copied from a leaderboard constant. A constant has no provenance and no expiry date, so it
  silently survives a leadership change.
- Report the per-window/per-segment breakdown next to the aggregate whenever the aggregate
  averages over heterogeneity. A mean over a heterogeneous population is not a claim about any
  member of that population.
- Prefer deriving the baseline from the live harness over reading it from a summary document.
  The summary is a copy; the harness is the measurement.

This is the general "stale constant" failure: a hardcoded baseline value is correct until the
thing it refers to is replaced, after which it is silently wrong, and the error only appears
in the one comparison that would have caught a real regression.

## Provenance

- Fixed end-to-end in the same session: constant renamed `S20_W4_REFERENCE` (documented as the
  S-20 value, NOT the incumbent), comparison derived in-harness as `anchor_w4`, emitting
  `w4_delta_vs_s26` alongside the S-20 reference in both log and JSON.
- Artifact: `projects/ts-ml-experiments/h720/sub_experiments/patchtst_delta_bet3/results_patchtst_bet3.json`
- Reflection: `MONITORING/reflection/2026-09-13_2350_S-43-bet3-terminal-close.md` (problem P2)
- All other metrics reproduced to printed precision after the fix (deterministic, seed 0).
