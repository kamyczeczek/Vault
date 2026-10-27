---
type: Concept
id: 01_h720_evaluation_protocol
title: "H=720 ETTh1 Forecasting & Evaluation Protocol"
source: "./CONTEXT.md"
tags: [protocol, etth1, evaluation, data, split]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# H=720 ETTh1 Evaluation Protocol

## Single Source of Truth: `data.py`
Unified evaluation protocol for all models and subexperiments:
1. **Raw Dataset**: `ETTh1.csv` containing 17,420 hourly observations (2016-07-01 00:00 to 2018-06-26 19:00). Gapless series; no resampling or interpolation permitted.
2. **Chronological Split**:
   - `train.csv`: 11,425 rows (Training set: rows 0–8,544 [8,545 rows] + Validation set: rows 8,545–11,424 [2,880 rows]).
   - `test.csv`: 2,880 rows (rows 11,425–14,224).
   - Reserve: rows 14,225+ unused.
3. **Locked Horizon H=720 (canonical scoring = rolling-origin since S-03)**:
   - Fit models exactly once on all of `train.csv` (11,425 rows) — frozen fit.
   - **Rolling-origin evaluation** (canonical): 2,161 stride-1 origins across the full test region; at origin `t` the model history is `eval_series[:11425+t]` (all observed rows strictly before the scored window `test[t:t+720]`). All published-comparison claims use rolling numbers.
   - Single-origin view (`test.csv[:720]` only) is the t=0 anchor window of the rolling harness — used for 4-decimal anchor-reproduction checks and archived legacy tables, not for claims.
   - Accessors: `rolling_views()` for rolling evaluation; `forecast_views()` for the t=0 anchor view.
4. **Mandatory Protocol Rule for Subexperiments**:
   - Every subexperiment MUST load data strictly via `data.py` accessors (`get_protocol_data()`, `rolling_views()` for rolling, `forecast_views()` for anchors).
   - Every derived sweep MUST embed anchor-reproduction checks against its source experiment (verifying 4-decimal MAE/RMSE match) and hard-fail before writing artifacts on mismatch.
   - A `results.json` containing empty results (`"results": []`) indicates a failed run and must never be trusted.
