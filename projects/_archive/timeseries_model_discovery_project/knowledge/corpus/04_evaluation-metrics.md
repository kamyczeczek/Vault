---
type: Concept
title: Evaluation metrics for forecasting
tags: [metrics, mae, mse, mape, smape, coverage, calibration]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Evaluation metrics for forecasting

Metric choice determines which models win. Pick metrics before looking at results.

## Scale-dependent metrics
- **MAE**: Mean Absolute Error. Interpretable in original units. Robust to outliers.
- **MSE**: Mean Squared Error. Penalizes large errors more. Use when large errors are costly.
- **RMSE**: Root MSE. Same units as data. Preferred when variance matters.

## Scale-free metrics
- **MAPE**: Mean Absolute Percentage Error. Interpretable but biased; undefined when actual=0.
- **sMAPE**: Symmetric MAPE. Bounded [0,200]. Still biased but less than MAPE.
- **MASE**: Mean Absolute Scaled Error. Compares to naive forecast. <1 = better than naive. Most robust.

## Probabilistic metrics
- **Coverage**: proportion of true values within prediction interval. Target: nominal level (e.g., 90%).
- **Calibration**: reliability of predicted quantiles.
- **CRPS**: Continuous Ranked Probability Score. Proper scoring rule for full distribution.

## The metric selection rule
1. Define primary metric before experiment.
2. Use at least one scale-dependent and one scale-free metric.
3. For probabilistic forecasts, add coverage + CRPS.
4. Report all metrics; do not cherry-pick.

## The baseline rule
Always compare against:
- Naive (last observation)
- Seasonal naive
- Classical model (ARIMA/ETS)

A candidate that cannot beat naive on primary metric is not a candidate.
