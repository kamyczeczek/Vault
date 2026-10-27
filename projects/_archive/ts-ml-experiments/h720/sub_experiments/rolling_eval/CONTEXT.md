---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# rolling_eval — Rolling-Origin Evaluation of the Top-5 Models (S-01)

## Question
How do the leaderboard's top models perform when scored over **sliding
stride-1 origins across the full 2,880-row test region** (2,161
origins, published-protocol-comparable) instead of the legacy single
720-row window? Does the single-origin ranking survive rolling
averaging, or was it one favorable window draw?

## Protocol (pinned in `PROCESS/03_plan/slices.md` S-01)
- **Frozen fit**: every model fit exactly once on all of `train.csv`
  (11,425 rows) — the locked protocol's fit history. No refit, no state
  carry-over between origins.
- **Per-origin history**: at origin `t` (test-row index), `history_ =
  eval_series[:11425+t]` — all observed rows strictly before the scored
  window `test[t:t+720]`. Past test-region rows are legitimate forecast
  time history (benchmark sliding-window convention); scored rows are
  never seen.
- **Origins**: `t ∈ [0, 2160]`, stride 1 → 2,161 windows per model.
- **Disjoint spread**: secondary diagnostic at `t = 0, 720, 1440, 2160`.
- **Anchors**: origin t=0 must reproduce the legacy 4-decimal
  leaderboard numbers exactly (the legacy protocol IS this harness's
  first window). All five anchors reproduced — harness verified.
- Accessor: `data.py::ProtocolData.rolling_views()` → `(fit_history,
  eval_series, test)`.

## Results — rolling (2,161 stride-1 origins, frozen fit)

| Model | Rolling MAE | Rolling RMSE | Legacy t=0 MAE | Δ |
|---|---:|---:|---:|---:|
| **elm_h64_full_fastlags** | **2.3092** | **2.8046** | 1.5923 | +0.717 |
| elm_h256_sobol_iid_full | 2.3409 | 2.8431 | 1.6330 | +0.708 |
| daily (seasonal-naive) | 2.5491 | 3.1120 | 1.6720 | +0.877 |
| knn_q3_k32_recent10 | 2.5583 | 3.0994 | 1.7204 | +0.838 |
| persistence | 2.5985 | 3.1282 | 1.7952 | +0.803 |

## Results — disjoint 720-row windows (frozen fit)

| Model | W1 (t=0) | W2 (t=720) | W3 (t=1440) | W4 (t=2160) | max/min |
|---|---:|---:|---:|---:|---:|
| elm_h64_full_fastlags | 1.592 | 1.815 | 1.662 | 2.162 | 1.36× |
| elm_h256_sobol_iid_full | 1.633 | 1.766 | 1.722 | 2.450 | 1.50× |
| daily | 1.672 | 1.904 | 1.862 | 2.919 | 1.75× |
| knn_q3_k32_recent10 | 1.720 | **4.909** | 2.416 | 2.816 | 2.86× |
| persistence | 1.795 | 2.146 | 1.778 | 2.180 | 1.22× |

## Key Findings
1. **Ranking within learned models survives; absolute numbers don't.**
   ELM h64 stays #1 (2.3092) and the ELM > kNN ordering holds, but every
   model's MAE rises sharply off the legacy window — the single-origin
   protocol understated true error by ~0.7–0.9 MAE for all models.
   All published-comparison claims must use rolling numbers from now on.
2. **The ELM beats seasonal-naive under rolling evaluation, but by less
   than the legacy window suggested**: 2.3092 vs 2.5491 = **9.4%
   improvement** (legacy window: 1.5923 vs 1.6720 = 4.8%). Rolling
   evaluation actually *strengthened* the learned-model advantage.
3. **kNN k=32 recent-10% is regime-fragile**: window-2 MAE 4.909
   (2.86× its best window) — the hard recent-10% truncation plus
   distance weighting collapses when the regime shifts (winter
   low-amplitude). The ELM is the stability leader (1.36× max/min).
   Notably persistence is the *most* stable (1.22×) — flat forecast
   rides regime shifts best on MAE.
4. **Window-4 (t=2160, spring 2018) is the hardest window for every
   model** (all maxima there) — consistent with the research report's
   regime analysis (the test region's later windows are harder).
5. **Runtime**: full 5-model × 2,161-origin harness = 33 s — well
   under the plan's 30 min/model risk budget. Stride-1 full-region
   rolling evaluation is cheap; the stride-24 fallback (risk 2) is
   not needed.

## Legacy single-origin leaderboard (archived here; do not compare
## against rolling numbers)

| Model | MAE | RMSE | Note |
|---|---:|---:|---|
| HeuristicLagELM (fast lags, 64n, full history) | **1.5923** | **1.9823** | single window t=0 only |
| HeuristicLagELM (fast lags, 256n, sobol_iid, full) | 1.6330 | 2.0550 | single window t=0 only |
| HeuristicLagELM (fast lags, 256n, recent 50%) | 1.6344 | 2.1715 | single window t=0 only |
| daily (seasonal-naive, lag 24) | 1.6720 | 2.1719 | single window t=0 only |
| HeuristicLagELM (default lags, 256n, full) | 1.6771 | 2.0313 | single window t=0 only |
| HeuristicLagKNN (k=32, q=3, recent 10%) | 1.7204 | 2.1405 | single window t=0 only |
| HeuristicLagKNN (k=24, q=3, recent 10%) | 1.7553 | 2.1663 | single window t=0 only |
| balanced_lag_ensemble_knn (q6_k8_recent50) | 1.7639 | 2.1945 | single window t=0 only |
| TemporalLagKNN (k=32, hl=720h, recent 10%) | 1.7866 | 2.2276 | single window t=0 only |
| TemporalLagKNN (k=64, recent 10%) | 1.7931 | 2.2221 | single window t=0 only |
| persistence | 1.7952 | 2.2503 | single window t=0 only |
| balanced_lag_ensemble_knn (full hist) | 2.0333 | 2.4536 | single window t=0 only |
| nlinear | 2.3507 | 2.8173 | single window t=0 only |
| HeuristicLagKNN (k=8, q=12) | 2.4104 | 2.9878 | single window t=0 only |
| heuristic_lag_knn_recursive | 2.4308 | 3.1944 | single window t=0 only |
| balanced_lag_ensemble_knn_more_experts | 2.4411 | 2.9488 | single window t=0 only (old run) |
| HeuristicLagKNN (k=8, q=6) | 2.4379 | 2.9753 | single window t=0 only |
| heuristic_lag_rf (100 trees) | 2.7354 | 3.1826 | single window t=0 only |
| heuristic_lag_knn (k=5, default) | 2.8195 | 3.4555 | single window t=0 only |
| heuristic_lag_elm (256 hidden) | 3.1723 | 3.6719 | single window t=0 only |
| heuristic_lag_tree (single tree) | 3.3488 | 4.0927 | single window t=0 only |
| dlinear | 16.6890 | 16.8130 | single window t=0 only |

*(Archived by S-03 on 2026-09-03: the canonical leaderboard in
`h720/CONTEXT.md` now carries rolling numbers; this is the complete
legacy table (22 rows) that previously lived there. Rows above without
a rolling score have never been rolling-evaluated — they are frozen
at their legacy t=0 values.)*

## Directory Structure
- `CONTEXT.md` — this document
- `run_sweep.py` — rolling harness (re-run: `python sub_experiments/rolling_eval/run_sweep.py`)
- `results.json` — rolling + disjoint metrics, protocol spec, anchors

## Next (plan slices)
- **S-02** validation-split re-selection (fit train-only 8,545 rows,
  select on the 2,880-row validation segment, score once on test) —
  quantifies the window-tuning artifact in the current config band.
- **S-03** leaderboard conversion (rolling numbers become canonical;
  legacy table archived; brain + extension sync).
