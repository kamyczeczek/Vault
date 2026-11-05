---
type: Concept
id: 03_model_registry_and_contracts
title: "Unified Time Series Model Registry & Forecaster Contract"
source: "./methods/"
tags: [models, registry, contract, architecture]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Unified Forecaster Contract & Registry

## Contract Specification
Every model in `./methods/` implements the standardized interface:
- Inherits from `BaseForecaster` in `methods/base.py`.
- `fit(y: np.ndarray, *, horizon: int = 720) -> self`
- `predict() -> np.ndarray` (shape: `(horizon,)`)

## Model Package Layout
- `methods/base.py`: Abstract Base Class `BaseForecaster` + anchor-lag feature extraction utilities (`_lag_dataset`, `_origins`, `_lag_features`, `_anchor`).
- `methods/baselines.py`: `Persistence` (repeats last value), `seasonal_forecast` / `seasonal_score` (daily 24h lag, weekly 168h lag).
- `methods/knn_models.py`:
  - `HeuristicLagKNN`: kNN over anchor-normalized lag features.
  - `heuristic_lag_knn_recursive`: Recursive step-by-step autoregressive kNN.
  - `heuristic_lag_rf`: Random Forest regressor on anchor-lag features.
  - `heuristic_lag_tree`: Single Decision Tree regressor.
  - `BalancedLagEnsembleKNN`: Multi-expert ensemble spanning 16 lag configurations.
  - `TemporalLagKNN`: Time-decayed neighbor-weighted kNN ($w_i = \frac{1}{d_i+\epsilon} e^{-\lambda \cdot \text{age}_i}$).
- `methods/neural_models.py`:
  - `DLinear`: Decomposition Linear (S-05 redesign): RevIN-order standardization — each window standardized (own mean/std) *before* moving-average trend/seasonal decomposition (level-free features); *joint* closed-form OLS on concatenated [seasonal; trend] against the standardized horizon; de-standardize at predict. Replaced the legacy two-independent-heads design (each head fit to the full raw target, summed → double-predicted level; legacy 16.6890 archived) and restored the lost `LinearRegression` import (dead-in-HEAD since 2026-08-29 consolidation).
  - `NLinear`: Normalization Linear model subtracting the last observation (last-value anchoring, Ridge readout; rolling leader since S-06: L=336 a=1 → 2.0571 MAE).
  - `RLinear`: NEW in S-06 — RevIN-standardized window (per-window mu/sigma, `_SCALE_EPS` clamp) fed raw (no anchoring, no decomposition) to a closed-form OLS/Ridge map on the standardized horizon. Empirically ≡ DLinear row-for-row at every shared lookback (decomposition is an invertible re-parametrization of the window's column span — Toner-Darlow equivalence confirmed in-project); DLinear's S-05 win is attributable to RevIN+joint solve, not the decomposition.
  - `HeuristicLagELM`: Extreme Learning Machine (single-hidden-layer feedforward network with fixed random/Sobol weights and pseudo-inverse ridge regression output).
  - `HeuristicLagELMTree` (S-09): ELM tanh hidden layer (fixed seed 42) with a multi-output `DecisionTreeRegressor` readout; lags selected from the training series by dynamical-systems criteria — AMI (τ = first local min of average mutual information = 14) + Kennel FNN (m = first dim with FNN% < 5% = 5) → lags 14/28/42/56/70, deterministic. Rolling (canonical): shallow depth-4 tree (min_samples_leaf=5, h256) **2.1706** — best ELM-class result, best non-linear leaderboard row (#11 by MAE behind the ten linear-family rows); deep/full trees degrade under rolling (t=0 winner dfull h512 1.7814 → rolling 2.6665; second single-origin→rolling rank flip after S-08); MI+FNN lags themselves are a dead end at H=720 (ridge readout on them scores 3.7473 vs 2.8890 on fast lags). Worktree `REGISTRY` state (`heuristic_lag_elm_tree` key replacing `heuristic_lag_elm`) is user WIP, uncommitted.
- `methods/multirate.py` (S-10):
  - `MultiRateELM` (`multirate_elm` REGISTRY key): N-HiTS-style multi-resolution forecaster — per-rate non-overlapping MaxPool(stride=r, kernel=r) views of the hourly series, one ELM trajectory expert per rate (shared seed-42 hidden draw, Ridge on the ceil(H/r)-block anchor-normalised trajectory, upsample `t//r`), uniform mean-ensemble readout. `rates=(1,)` + the parent config ≡ `HeuristicLagELM` byte-identically (pinned at smoke/t=0/rolling gates). Rolling (canonical): R=(1,2,4) **2.2744** vs parent 2.3092 — first ELM-family rolling win over the parent since S-01; rates ≥ 8 import block-boundary noise (R1_2_4_8_168 2.4634); t=0 ordering does not transfer (third rank flip after S-08/S-09); capacity h32/h128 flat. Fail-loud guards: rates must be non-empty distinct ints ≥ 1 and include 1 (the hourly expert is the base trajectory).
- `methods/fits.py` (S-07):
  - `FITSForecaster`: frequency-domain forecaster — rFFT of the RevIN-standardized window → closed-form complex ridge to the extended spectrum (L+720) → optional LPF cutoff (rFFT bin of extended length) → iRFFT → horizon tail. Deterministic, no RNG. Full-spectrum FITS ≡ RLinear/DLinear row-for-row at shared L (rFFT is a unitary basis change of the same least-squares problem — third member of the Toner-Darlow equivalence class); every LPF cutoff hurts on ETTh1 H=720 rolling (published aggressive-low-pass claim does not transfer).
- `methods/ensemble.py` (S-08):
  - `CrossFamilyEnsemble`: blends elm_h64_full_fastlags + knn_q3_k32_recent10 + daily seasonal-naive. Members frozen on the full fit series; weight search on VALIDATION windows only (2,161 stride-1 origins over the trailing 2,880 rows; fail-loud length guards `val_start >= 0`, `n_origins >= 1`). TWO deterministic solvers, both on a cell-order residual matrix (`transpose(0,2,1)` before reshape — a direct C-order reshape scrambles member identity with horizon step): primary `weights_` = squared-error blend (closed-form equality-constrained solve + Duchi simplex projection; [0.3048, 0.6056, 0.0896] → test rolling 2.3103 = ELM 2.3092 + 0.0011) and diagnostic `mae_weights_` = exact L1 optimum (pairwise coordinate descent + ternary line search) which degenerates to the pure-kNN vertex — no non-trivial blend beats the best member's validation MAE on this data (negative result, fully recorded).
- `methods/__init__.py`: Factory `make_forecaster(name, **kwargs)` and dictionary `REGISTRY`.
- `methods/residual.py` (S-11):
  - `SeasonalResidualELM` (`seasonal_residual_elm` REGISTRY key): tanh-ELM parent pathway on the deviation from a seasonal-naive template — template `T(i)[h] = series[i-m+(h mod m)]` (m=24 daily / m=168 weekly, pre-origin history only), residual target `Y_r = Y + (anchors - templates)` (the template replaces the anchor as the level carrier), predict re-adds the template. `mode="raw"` + parent config ≡ `HeuristicLagELM` byte-identically (smoke 0.00e+00, t=0 1.5923, rolling 2.3092). Rolling verdict (canonical): seasonal-residual learning HURTS the tanh ELM — m24 2.4326 (+5.3% vs parent), m168 2.5740 (+11.5%); the anchor-normalised trajectory basis already spans the daily structure, the explicit template swaps in a spikier level carrier. Fail-loud guards: period ≥ 1, mode ∈ {residual, raw}.
- `methods/rbf.py` (S-11):
  - `RBFELM` (`rbf_elm` REGISTRY key): Gaussian RBF hidden layer + ridge readout — centers = `hidden_dim` iid training feature rows (RandomState(42)), one global width σ = mean pairwise center distance, response `exp(-||x-c||²/2σ²)`; parent `_lag_dataset` features with S-04 `normalize_scale` flags + optional `residual_period` cross. Rolling (canonical): rbf_raw (h64, no norm) **2.2812** vs parent 2.3092 (−1.2%) — second ELM-family rolling win (user-suggested hypothesis), behind S-10 multirate 2.2744; most W4-drift-robust learned model in the family (W4 2.0545 vs multirate 2.6783). S-04 norm-gain does NOT transfer at rolling scale (norm168 2.3073, norm720 2.3522 — the t=0 norm-gain was a single-window artifact); biases do not compose (rbf_res24 2.3953). Fail-loud guard: residual_period ≥ 0.
