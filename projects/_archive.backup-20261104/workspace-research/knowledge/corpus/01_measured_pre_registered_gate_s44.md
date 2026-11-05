---
type: Concept
id: 01_measured_pre_registered_gate_s44
title: "Measured Lesson — Pre-Registered Gates Are the Only Thing That Makes a Promotion Legitimate (h720 S-44) (part 2/2)"
source: "measured_pre_registered_gate_s44.md"
tags: [forecasting, gate-semantics, pre-registration]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---
taxonomy: #pre-registration #gate-semantics #forecasting
The general failure this prevents is not deliberate cheating. It is the honest case: an
experimenter reads a result, then decides which conditions count. Declaring the gate first
removes that decision from the moment of temptation — which is the entire value, because at
the moment of temptation the correct reasoning is unavailable to the person doing it.

## Provenance

- Design (pre-registration): `projects/ts-ml-experiments/h720/sub_experiments/blend_promotion_s44/S44_DESIGN.md`
- Harness + results: same directory (`rolling_arm.py`, `results_s44.json`, `harness.log`)
- Verified by gate: `projects/ts-ml-experiments/h720/PROCESS/run_gates.py` `check_s44_design`
  (design sections complete, binding gate all-pass, parity all-pass, verdict PROMOTED)
- Predecessor defect: `measured_gate_semantics_s43` in this corpus
