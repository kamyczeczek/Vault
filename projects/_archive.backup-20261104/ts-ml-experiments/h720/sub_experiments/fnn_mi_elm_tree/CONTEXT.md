---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# fnn_mi_elm_tree — MI+FNN lag selection, ELM hidden layer, tree readout

## Question
Do lags chosen by dynamical-systems criteria (mutual information + false
nearest neighbours) + an ELM random feature layer with a **decision-tree
readout** beat the hand-picked lag sets and ridge readout used so far?

## Design
Two orthogonal changes vs the best ELM (`normal_h64_full_fastlags`, MAE 1.5923):

1. **Lag selection** — no hand-picked lags. From the training series only:
   - AMI: τ = lag of first local minimum of average mutual information.
   - FNN: Kennel false-nearest-neighbour % at delay τ; m = first dim with
     FNN% < 5%. Selected: **τ=14, m=5** → candidate lags {14, 28, 42, 56, 70},
     re-ranked by MI with the H=720-ahead target, top n_lags kept.
   - Result on train.csv: lags **(14, 28, 42, 56, 70)** — all multiples of
     the 14-hour AMI scale, no daily (24h) or weekly (168h) lags. FNN says
     the series is low-dimensional (m=5): near-neighbor structure explains
     recurrence without the seasonal anchors.
2. **Readout** — multi-output regressor over the tanh hidden layer
   (hidden_dim x lag features, fixed seed 42), *instead of* ridge:
   - `DecisionTreeRegressor` (fixed seed 42), regularized via
     `tree_kwargs`: max_depth / min_samples_leaf / max_features grid.
   - Reference arm: same lags + same hidden layer + **ridge** readout
     (isolates the readout effect from the lag effect).

Both changes deterministic: every seed fixed at 42, selection has no
randomness. Same shared split as every subexperiment (fit all of
train.csv 11,425 rows, forecast H=720, score vs test.csv[:720]).

## Results

**Single-origin (t=0, run_sweep.py, fit train.csv → forecast vs test.csv[:720]).**
All deterministic (seed 42, no RNG in selection). Full table in
`results.json` + `interactive.html`; the ranked extremes:

| config | t=0 MAE | RMSE |
|---|---|---|
| tree_best_h512 (dfull, L25, hidden 512) | **1.7814** | 2.3739 |
| ridge_ref_fastlags (h256, lags 1..12) | 1.8946 | 2.4039 |
| ridge_ref_same_lags (h256, MI+FNN lags) | 2.0367 | 2.5004 |
| tree_d4_L5/L25/L100 (identical output) | 2.5267 | 2.9755 |
| parent ELM h64 full fastlags (S-01 ref) | 1.5923 | 1.9679 |

**Rolling (canonical protocol, `rolling_arm.py`, frozen fit, 2,161
stride-1 origins, disjoint windows W1–W4; anchors fail-loud 3/3 OK,
t=0 cross-checks 3/3 OK):**

| config | rolling MAE | RMSE | W1/W2/W3/W4 |
|---|---|---|---|
| **tree d4_L5 (h256)** | **2.1706** | 2.6423 | 2.53/1.36/1.70/2.33 |
| tree d12_L100 (h256) | 2.3049 | 2.7854 | 2.31/1.64/1.82/2.99 |
| tree dfull_L100 (h256) | 2.3106 | 2.7916 | same as d12_L100 |
| parent ELM h64 full fastlags | 2.3092 | 2.8046 | 1.59/1.81/1.66/2.16 |
| tree dfull_L25 (h256) | 2.6317 | 3.1590 | |
| tree_best_h512 (t=0 winner) | 2.6665 | 3.1966 | 1.78/2.06/1.93/2.07 |
| ridge_fastlags_h256 | 2.8890 | 3.4967 | |
| daily anchor | 2.5491 | 3.1120 | |
| persistence anchor | 2.5985 | 3.1282 | |
| ridge_same_lags (MI+FNN lags) | 3.7473 | 4.5474 | 2.04/4.92/3.04/4.77 |

**Findings (S-09):**
1. **MI+FNN lags do not transfer.** Lags (14,28,42,56,70) (τ=14,
   m=5) hurt the ridge readout catastrophically: 3.7473 vs 2.8890
   on the legacy fast lags (1,2,3,6,12) — the same readout, only
   the lag set differs. The 14-h AMI scale is a real recurrence
   scale, but for H=720 forecasting the fast daily-structure lags
   carry the signal. FNN's "low-dimensional, no seasonal anchors
   needed" reading is false for multi-step prediction.
2. **Shallow trees beat deep ones under rolling.** Depth-4 tree
   (rolling 2.1706) beats the parent ELM 2.3092 — the best
   ELM-class result of the project so far (best non-linear row on
   the leaderboard, #11 by MAE behind the ten linear-family rows); the fully-grown t=0 winner (h512,
   2.6665) degrades worst. Second rank flip after S-08 (kNN):
   single-origin selection rewards deep/expressive configs that
   overfit the specific window.
3. **Tree readout ≥ ridge readout at matched lags** (rolling):
   2.1706 (tree d4_L5) vs 3.7473 (ridge) on MI+FNN lags — the
   readout change is the only surviving win of the design.
4. W2 regime: trees d4/d12/dfull track the parent's easy W2
   (1.36–1.81) but lose W4; ridge MI+FNN explodes everywhere
   (W2 4.92).

**Execution caveat:** the worktree WIP removed `heuristic_lag_elm`
from REGISTRY (replaced by `heuristic_lag_elm_tree`), so
`run_sweep.py`'s own ridge-reference arms crash under it. The sweep
was run via a runtime shim (TEMP wrapper restoring the key at
import, zero file modifications; `rolling_arm.py` imports the class
directly and is unaffected). Restoring the key in
`methods/__init__.py` is pending the user's WIP decision.
`rolling_arm.py` + `results_rolling.json` are agent-authored
(S-09), the rest of the directory is user WIP.

## Directory Structure
- `CONTEXT.md` — this document
- `run_sweep.py` — sweep + HTML report
- `results.json` — metrics per configuration
- `interactive.html` — forecasts, ranking, MI/FNN diagnostics
