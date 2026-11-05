---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-experiment: DLinear fix (S-05)

## Purpose
Fix the DLinear raw-scale OLS artifact (legacy 16.6890 MAE, worst on the
leaderboard) and re-score the model under the canonical rolling protocol.

## Root cause (two compounding defects)
1. **Lost import (dead in HEAD)**: the 2026-08-29 methods consolidation
   dropped `from sklearn.linear_model import LinearRegression` while
   keeping both call sites — `DLinear.fit()` crashed with `NameError`
   before reaching any scoring. The legacy 16.6890 number predates the
   consolidation.
2. **Two-independent-heads artifact**: the legacy design fit seasonal
   and trend heads *independently*, each against the full raw-scale
   target, then summed predictions — both heads re-learn the same
   level, so the sum double-predicts it.

## Fix design (published-behavior class, Zeng et al. 2023 + RevIN)
- **RevIN-order standardization**: each window is standardized
  (mean/std of the window itself) *before* moving-average decomposition
  — seasonal+trend features become level-free, so the linear map never
  extrapolates along an unseen level direction. Predict de-standardizes
  with the trailing window's stats.
- **Joint solve**: one OLS problem on concatenated [seasonal; trend]
  features against the standardized target (the level is learned once).
  Optional `ridge_alpha` switches to Ridge.
- Deterministic: closed-form LAPACK solve, no RNG.
- NLinear `predict()` also gained a 1-D-history coercion fix (the
  rolling runner assigns `history_` as 1-D; legacy predict crashed with
  `IndexError`). NLinear's numbers are unchanged (no rolling score yet
  — S-06 will score it).

## Verification gates (all passed 2026-09-03)
- **Level-tracking diagnostic** (`diagnose.py`): flat train, ±20-shifted
  windows — mean error 0.007 (was 19.86 with the legacy two-heads sum).
- **Regression gate** (`regression_gate.py`): four canonical models
  reproduce their legacy t=0 anchors to 4 decimals (ELM 1.5923/1.9823,
  kNN 1.7204/2.1405, persistence 1.7952/2.2503, daily 1.6720/2.1719) —
  the S-05 changes did not touch any other model.
- **Rolling sweep** (`run_sweep.py`): protocol anchors reproduce exactly
  (ELM rolling 2.3092, daily 2.5491, persistence 2.5985); coefficient
  sanity max|coef| 0.233 (no exploding norms).

## Results (rolling, frozen fit, 2,161 stride-1 origins)

| Model | MAE | RMSE | note |
|-------|-----|------|------|
| dlinear_L96_k25_a0 | **2.1163** | 2.6045 | OLS; **new leaderboard leader** |
| dlinear_L96_k25_a1 | 2.1163 | 2.6045 | Ridge a=1.0 identical (features well-conditioned) |
| dlinear_L336_k25_a0 | 2.1220 | 2.6025 | long lookback; slightly worse MAE, better RMSE |
| dlinear_L336_k25_a1 | 2.1220 | 2.6025 | |
| elm_h64_full_fastlags (anchor) | 2.3092 | 2.8046 | previous leader |
| daily (anchor) | 2.5491 | 3.1120 | |
| persistence (anchor) | 2.5985 | 3.1282 | |

Acceptance vs slice S-05:
- Rolling MAE 2.1163 < persistence 2.5985 ✅ (also < daily 2.5491 and
  < previous leader ELM 2.3092)
- Improvement vs legacy 16.6890: **−87.3%** (>50% required) ✅
- Coefficient scale sanity: max|coef| 0.233 ✅

## Files
- `diagnose.py` — level-tracking diagnostic (artifact quantification)
- `regression_gate.py` — non-DLinear anchor reproduction gate
- `run_sweep.py` — rolling sweep + fail-loud protocol anchors
- `results.json` — sweep output
