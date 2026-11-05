---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-experiment: Multi-Rate / Multi-Scale Lag Features (S-10)

## Question
Does giving the ELM family N-HiTS-style multi-resolution inputs —
per-rate MaxPool-downsampled views of the series with one ELM
trajectory expert per rate — beat the single-rate parent
(`HeuristicLagELM` h64 full fastlags, rolling 2.3092) under the
canonical rolling protocol? Which rate sets transfer from t=0
single-origin selection, and which import block-boundary noise?

## Design
- **View per rate r**: non-overlapping MaxPool(stride=r, kernel=r)
  over the hourly OT series — rate r expresses "the worst-case level
  reached in each r-hour block". Rate 1 = identity (the parent).
- **Rate-1 expert**: EXACTLY the parent pathway —
  `_lag_dataset(series, 720, fastlags, q=3, hist=1.0)`, seed-42
  hidden draw (h64), Ridge(alpha=1) on the full 720-step
  anchor-normalised trajectory. With `rates=(1,)` the model is
  byte-identical to `HeuristicLagELM` (asserted in smoke, t=0, and
  rolling gates) — the identity arm pins every multirate delta to
  the coarse-rate experts alone.
- **Coarse rate-r expert**: same pathway on the view — multi-output
  Ridge on the `ceil(720/r)`-block trajectory (anchor q_r=⌊q/r⌋≥1,
  lags in view units), prediction upsampled to hourly by block
  index `t // r`. No clamping, no post-origin data.
- **Readout**: uniform mean over the per-rate hourly trajectories
  (mean, not sum: with one rate it degenerates to the parent
  instead of doubling the level).
- **Sweep** (`run_sweep.py`, t=0): identity + 5 singles (r∈{2,4,8,
  12,168}) + 10 combos + capacity sensitivity (h32/h128 on the best
  single and best combo) + inline daily/persistence. Frozen fit on
  `fit_history` (11,425 rows), score vs `forecast_views()` ground
  truth. Identity gate: R=(1,) t=0 MAE must equal the parent's 1.5923.
- **Rolling arm** (`rolling_arm.py`): 6 multirate configs + parent +
  daily + persistence under the canonical protocol (frozen fit,
  2,161 stride-1 origins, disjoint W1–W4). Fail-loud anchors:
  parent 2.3092 / daily 2.5491 / persistence 2.5985; rolling
  identity R=(1,) == parent; t=0 cross-checks vs run_sweep (6 arms).
- **Smoke** (`smoke_multirate.py`): 5 gates — construct/fit/predict
  over 4 rate configs, determinism (byte-equal re-fits), R=(1,)
  byte-identity vs parent on synthetic data, and fail-loud guards
  (empty/dupe/<1 rates, missing rate-1).

## Directory Structure
```
multirate_sweep/
├── CONTEXT.md          # this file
├── smoke_multirate.py  # 5-gate smoke (identity + guards)
├── run_sweep.py        # t=0 sweep: singles + combos + capacity + anchors
├── rolling_arm.py      # canonical rolling arm (frozen fit, 2161 origins)
├── results.json        # t=0 numbers (single-origin protocol)
└── results_rolling.json# canonical rolling numbers + anchors + t0 cross
```

## Results (rolling, frozen fit, 2,161 stride-1 origins)

| model | rolling MAE | RMSE | t=0 MAE |
|-------|------------:|-----:|--------:|
| multirate_R1_2_4 | **2.2744** | 2.7743 | 1.5946 |
| multirate_R1_2   | 2.2819 | 2.7787 | 1.6479 |
| multirate_R1_4   | 2.2835 | 2.7838 | 1.5403 |
| multirate_R1_eq_parent | 2.3092 | 2.8046 | 1.5923 |
| (parent ELM — same pathway, separate arm) | 2.3092 | 2.8046 | 1.5923 |
| multirate_R1_4_h128 | 2.3122 | 2.8140 | 1.6471 |
| multirate_R1_2_4_8_168 | 2.4634 | 2.9917 | 1.5622 |
| daily (anchor, lag-24) | 2.5491 | 3.1120 | 1.6720 |
| persistence (anchor) | 2.5985 | 3.1282 | 1.7952 |
| weekly168 template (t=0 context only) | — | — | 2.3788 |

Anchors 3/3 OK; rolling identity R=(1,) 2.3092 == parent OK;
t=0 cross-checks 6/6 OK. Disjoint windows (R1_2_4): W1 1.595,
W2 1.657, W3 1.708, W4 2.678 — the W4 regime shift dominates the
gap to the linear family (all ELM-class rows share it).

Correction (post-slice hotfix, 2026-09-03): the t=0 sweep's
inline "daily" arm originally tiled the trailing 168-hour
template (a WEEKLY template, t=0 2.3788) instead of the canonical
lag-24 daily baseline (t=0 1.6720). The rolling arm was never
affected (it calls `seasonal_forecast("daily")` and its anchor
2.5491 checked green); the mislabel lived only in the t=0 column
of `results.json` and the earlier revision of this table. Both
arms now run in the sweep (`daily` lag-24 + `weekly168`), and the
table above shows the corrected numbers.

## Findings
1. **First ELM-family rolling win over the parent since S-01**:
   R=(1,2,4) 2.2744 vs parent 2.3092 (−1.5%). Both fine rates
   contribute: R=(1,4) alone 2.2835, R=(1,2) alone 2.2819, the
   three-rate mean is best. Still well short of the linear family
   (leader NLinear L336 2.0571) and of ELMTree 2.1706.
2. **t=0 ordering does NOT transfer (third instance after S-08/S-09)**:
   t=0 best R=(1,4) 1.5403 → rolling 2.2835 (third place among
   multirate arms); the best t=0 combo R=(1,2,4,8,168) 1.5622 →
   rolling 2.4634 (worst). Single-origin selection keeps rewarding
   configs that overfit one window.
3. **Rates ≥ 8 import block-boundary noise**: every set containing
   8 or 168 rolling-degrades (R1_2_4_8_168 2.4634). MaxPool block
   maxima at weekly scale drift from the hourly path the metric
   scores; the useful secondary scales are the sub-daily ones (2h, 4h).
4. **Capacity is not the binding constraint**: h32/h128 within ±0.04
   of h64 on both the best single and best combo — the gain comes
   from the multi-scale views, not extra hidden units.
5. **Identity holds at every gate**: `rates=(1,)` ≡ parent
   byte-identically (smoke 0.00e+00, t=0 1.5923, rolling 2.3092) —
   the design change (coarse experts + mean readout) is the only
   moving part, so the −1.5% is attributable to multi-rate input
   alone.
