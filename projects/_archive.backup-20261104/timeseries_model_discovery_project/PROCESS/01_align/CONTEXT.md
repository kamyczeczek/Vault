---
type: Concept
id: 01_align
title: Align on problem definition
inputs:
  working: []
  reference:
    - _config/forecast-metrics.md
    - knowledge/corpus/*.md
outputs:
  - output/problem-brief.md
human_check: Read problem-brief.md aloud. Verify forecast horizon, metrics, and constraints are unambiguous.
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# 01_align — Define the forecasting problem

One job: write a problem brief that an experiment can be designed against.

## Process
1. Read the dataset description and sample data.
2. State the forecast horizon, seasonality, and missing-data policy.
3. Choose primary and secondary metrics.
4. List hard constraints (latency, interpretability, retrain frequency).
5. Write `output/problem-brief.md`.

## Rules
- No model names here. This stage defines the problem, not the solution.
- If the dataset has no clear seasonality, say so explicitly.
- Metrics come from `_config/forecast-metrics.md`; do not invent new ones.
