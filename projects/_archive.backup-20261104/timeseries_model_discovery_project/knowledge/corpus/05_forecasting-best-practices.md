---
type: Concept
title: Forecasting best practices
tags: [best-practices, data-splitting, leakage, backtesting, reproducibility]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Forecasting best practices

Reproducibility is a feature, not an afterthought.

## Data splitting
- **Train/validation/test**: chronological split only. Never random shuffle for time series.
- **Validation**: use for hyperparameter tuning and early stopping.
- **Test**: held out until final evaluation. No peeking.
- **Fixed seeds**: all randomness must have a fixed seed. Document the seed in the result file.

## Avoiding leakage
- **No future information**: features at time t must only use data up to time t.
- **No test-set leakage**: hyperparameter tuning on test set invalidates results.
- **Scaling**: fit scaler on train only; transform val/test with train statistics.

## Backtesting strategies
- **Expanding window**: train on all data up to t, predict t+1. Most realistic.
- **Rolling window**: train on fixed-size window ending at t. Good for non-stationary data.
- **Multiple horizons**: if predicting h steps ahead, evaluate each horizon separately.

## Experiment documentation
Every experiment must produce:
1. Dataset version / hash
2. Random seeds used
3. Hyperparameters and search space
4. Train/val/test split boundaries
5. Metric definitions
6. Result files with timestamps

## The reproducibility rule
An experiment is reproducible if another agent can:
1. Read the experiment plan.
2. Run it without asking questions.
3. Get the same result (within numerical tolerance).
