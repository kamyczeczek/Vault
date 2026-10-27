---
type: Concept
title: Classical time series models
tags: [classical, arima, sarima, exponential-smoothing, baseline]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Classical time series models

Classical models remain strong baselines for univariate forecasting.

## ARIMA/SARIMA
- **ARIMA**: AutoRegressive Integrated Moving Average. Requires stationary series; handles trend via differencing.
- **SARIMA**: Adds seasonal terms (P, D, Q, s). Best for strong seasonal patterns with clear period.
- **Strengths**: interpretable, fast, no hyperparameter explosion.
- **Weaknesses**: assumes linear relationships; struggles with multiple seasonalities; requires manual order selection.
- **When to use**: short horizons, strong seasonal pattern, limited data.

## Exponential Smoothing (ETS)
- **Holt-Winters**: triple exponential smoothing for trend + seasonality.
- **ETS**: state-space formulation with automatic selection (AICc).
- **Strengths**: handles level/trend/seasonality; probabilistic forecasts available.
- **Weaknesses**: single seasonality only; no exogenous variables in basic form.
- **When to use**: business forecasting with clear seasonal pattern.

## The Baseline Rule
Always compare against:
1. Naive (last observation)
2. Seasonal naive (last season's observation)
3. A classical model (ARIMA or ETS)

A candidate that cannot beat naive on your metric is not a candidate.
