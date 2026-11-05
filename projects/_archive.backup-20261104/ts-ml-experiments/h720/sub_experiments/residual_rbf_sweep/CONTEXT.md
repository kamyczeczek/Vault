---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-experiment: Seasonal-Residual + RBF-Hidden ELM (S-11)

## Question
Two independent inductive-bias hypotheses for the ELM family,
tested in one 2×2-style grid (user-suggested RBF folded into the
slice):
(a) **Seasonal-residual learning** — learn the deviation from a
seasonal-naive template (m=24 daily / m=168 weekly) instead of the
raw anchor-normalised target, re-adding the template in predict.
(b) **Local RBF kernels** — replace the global tanh hidden layer
with Gaussian RBF units (centers = training feature rows, seed 42;
σ = mean pairwise center distance), the inductive bias kNN
exploits; per the S-04 asymmetry (norm helps kNN 2.5583→2.3815,
hurts tanh-ELM 2.3092→2.3289) also crossed with window-std
normalization (off / @168 / @720).
Both crossed with each other (rbf_res24) and with capacity
(h32/h256). Bar to beat: parent `HeuristicLagELM` rolling 2.3092;
family leader MultiRateELM R=(1,2,4) 2.2744 (S-10).

## Design
- **SeasonalResidualELM** (`methods/residual.py`): template
  `T(i)[h] = series[i-m+(h mod m)]` from pre-origin history only;
  residual target `Y_r = Y + (anchors - templates)` (scale-1 space;
  the template replaces the anchor as the level carrier), predict
  `readout + template`. `mode="raw"` + parent config ≡
  `HeuristicLagELM` byte-identically (identity arm pins the
  residual decomposition as the only moving part).
- **RBFELM** (`methods/rbf.py`): parent `_lag_dataset` features
  (incl. S-04 `normalize_scale` flags), centers = 64 iid feature
  rows (RandomState(42)), response `exp(-||x-c||²/2σ²)` with one
  global σ = mean pairwise center distance, Ridge(α=1) readout.
  `residual_period` crosses the seasonal-residual bias in.
- **Smoke** (`smoke_residual_rbf.py`): 17 gates — construct/fit/
  predict over 11 configs, determinism (byte-equal), identity
  res-raw ≡ parent (0.00e+00), template decomposition asserts for
  both classes, fail-loud guards (period<1, bad mode,
  residual_period<0).
- **Sweep** (`run_sweep.py`, t=0): identity + parent-direct +
  res m24/m168 + RBF raw/norm168/norm720 + rbf_res24 (+norm720) +
  capacity h32/h256 + canonical anchors (daily via
  `seasonal_forecast`, weekly168 tile, persistence). Identity gate:
  res-raw t=0 == 1.5923 AND parent-direct == 1.5923.
- **Rolling arm** (`rolling_arm.py`): ALL 7 model arms advance
  (t=0 does not select — S-08/S-09/S-10 lesson) + parent + S-10
  winner + daily + persistence under the canonical protocol (frozen
  fit, 2,161 stride-1 origins, disjoint W1–W4). T0 cross-checks are
  READ from `results.json` at runtime (prevention rule: constants
  are read, not transcribed).

## Directory Structure
```
residual_rbf_sweep/
├── CONTEXT.md              # this file
├── smoke_residual_rbf.py   # 17-gate smoke (identity + decomposition + guards)
├── run_sweep.py            # t=0 sweep: 12 model arms + anchors + identity gates
├── rolling_arm.py          # canonical rolling arm (11 arms, anchors + t0 READ)
├── results.json            # t=0 numbers (single-origin protocol)
└── results_rolling.json    # canonical rolling numbers + anchors + t0 cross
```

## Results (rolling, frozen fit, 2,161 stride-1 origins)

| model | rolling MAE | RMSE | t=0 MAE |
|-------|------------:|-----:|--------:|
| multirate_R1_2_4 (S-10 winner, family bar) | **2.2744** | 2.7743 | 1.5946 |
| **rbf_raw (h64, σ-global, no norm)** | **2.2812** | 2.7684 | 1.7271 |
| rbf_norm168 | 2.3073 | 2.8078 | 1.6785 |
| res_raw_eq_parent / parent ELM (identity) | 2.3092 | 2.8046 | 1.5923 |
| rbf_norm720 | 2.3522 | 2.8572 | 1.7001 |
| rbf_res24 | 2.3953 | 2.9260 | 1.7581 |
| res_m24 | 2.4326 | 2.9709 | 1.6683 |
| res_m168 | 2.5740 | 3.1704 | 2.8643 |
| daily (anchor, lag-24) | 2.5491 | 3.1120 | 1.6720 |
| persistence (anchor) | 2.5985 | 3.1282 | 1.7952 |

Anchors 4/4 OK (parent 2.3092, multirate 2.2744, daily 2.5491,
persistence 2.5985); rolling identity res-raw 2.3092 == parent OK;
t=0 cross-checks 7/7 OK (read from results.json). Disjoint W4:
rbf_raw 2.0545 vs multirate_R1_2_4 2.6783 — RBF is markedly more
drift-robust on the hardest window while losing on average.

## Findings
1. **RBF hidden layer works (user hypothesis confirmed)**:
   rbf_raw 2.2812 beats the parent 2.3092 (−1.2%) — second
   ELM-family improvement after S-10's multirate (2.2744, −1.5%),
   but does not dethrone it. The tanh→RBF swap alone carries the
   gain (same features, same readout, same seed discipline).
2. **The S-04 normalization asymmetry does NOT transfer to RBF at
   rolling scale**: norm168 2.3073 ≈ parent, norm720 2.3522 — both
   worse than rbf_raw 2.2812. The t=0 single-origin view agreed
   with the kNN analogy (norm168 1.6785 < raw 1.7271), but rolling
   refutes it. Local kernels ≠ kNN on normalised windows: the
   kNN gain came from window-std distance alignment across
   origins, which the frozen-fit RBF centers cannot exploit.
3. **Seasonal-residual learning hurts the ELM family**: res_m24
   2.4326 (+5.3% vs parent), res_m168 2.5740 (+11.5%). The tanh
   readout on anchor-normalised features ALREADY captures the
   daily structure (its implicit trajectory basis spans it); the
   explicit template removes the anchor the features were built on
   and replaces it with a weaker, spikier level carrier.
4. **The two biases do not compose**: rbf_res24 2.3953 — worse
   than rbf_raw 2.2812 and res_m24 is itself harmful; stacking a
   harmful decomposition on a working kernel layer just inherits
   the harm.
5. **t=0 ordering does not transfer — 4th and 5th rank flips**
   (after S-08/S-09/S-10): t=0 ranked res_m24 (1.6683) and
   rbf_norm168 (1.6785) above rbf_raw (1.7271) and near daily
   (1.6720); rolling ranks rbf_raw first among the new arms. The
   S-10 hotfix lesson (inline daily labeling) is why the sweep
   imports `seasonal_forecast` for the daily arm and runs
   weekly168 separately.
6. **W4 robustness inverts at the family level**: multirate wins
   the rolling average through W1–W3 (W4 2.6783, its worst
   window), while rbf_raw is the most W4-robust learned model in
   the family (2.0545, best W4 among ELM-class arms). A
   multirate+RBF hybrid (RBF experts on multi-rate views) is the
   obvious S-12-adjacent follow-up.
