---
type: Concept
title: Machine learning models for time series
tags: [ml, xgboost, lightgbm, feature-engineering, tabular]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Machine learning models for time series

Tree-based models dominate tabular forecasting competitions.

## XGBoost / LightGBM / CatBoost
- **Approach**: frame forecasting as supervised learning with lag features.
- **Feature engineering**: lags, rolling statistics, date features, target encoding.
- **Strengths**: handles mixed data types, robust to outliers, fast inference, SHAP values available.
- **Weaknesses**: requires feature engineering; does not extrapolate beyond training range; struggles with long-range dependencies.
- **When to use**: tabular data with mixed features, short-to-medium horizons, need for interpretability.

## Feature engineering patterns
- **Lags**: t-1, t-7, t-30 depending on seasonality.
- **Rolling stats**: mean/std over window, expanding window.
- **Date features**: hour, day of week, month, holiday flags.
- **Target encoding**: mean target by categorical feature (with leak prevention).

## The hybrid pattern
Residuals from classical models often become features for ML models. This combines structural modeling (classical) with flexible fitting (ML).

## When ML beats deep learning
- Limited data (< 10k observations)
- Need for fast retraining
- Need for feature importance / interpretability
