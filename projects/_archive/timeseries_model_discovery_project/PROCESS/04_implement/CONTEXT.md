---
type: Concept
id: 04_implement
title: Implement and run candidates
inputs:
  working:
    - ../03_design/output/experiment-plan.md
    - ../02_survey/output/candidate-table.md
  reference:
    - _config/model-taxonomy.md
outputs:
  - output/results-<model-slug>.md
human_check: Spot-check one result file for metric calculation and seed provenance.
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# 04_implement — Execute the experiment

One job: implement each candidate and produce one result file per model.

## Process
1. Read experiment plan and candidate table.
2. For each candidate model:
   - Implement or run the model per the plan.
   - Record metrics, training time, and any failures.
   - Write `output/results-<model-slug>.md`.
3. If a model fails, record the failure mode in the result file.

## Rules
- One result file per model. Do not merge results into one file.
- Fixed seeds from experiment plan must be visible in the result file.
- Failure is informative: a failed result file is a valid output.
