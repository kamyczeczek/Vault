"""Leakage-safe, horizon-wise evaluation helpers for chaotic systems."""
from __future__ import annotations
import numpy as np


def evaluate_forecaster(series, fit_predict, horizons=(1, 4, 8, 24, 48),
                        origins=(1200, 1400, 1600, 1800), min_history=96):
    """Evaluate a causal forecaster at multiple horizons and origins.

    ``fit_predict(history, horizon)`` must train only on ``history`` and return
    at least ``horizon`` predictions. Origins are indices into ``series``.
    """
    y = np.asarray(series, dtype=float)
    if y.ndim != 1 or not np.isfinite(y).all():
        raise ValueError("series must be a finite one-dimensional array")
    results = {}
    for horizon in horizons:
        errors = []
        correlations = []
        for origin in origins:
            if origin < min_history or origin + horizon > len(y):
                raise ValueError("origin is incompatible with history or horizon")
            history = y[:origin].copy()
            actual = y[origin:origin + horizon]
            prediction = np.asarray(fit_predict(history, horizon), dtype=float).ravel()[:horizon]
            if len(prediction) != horizon or not np.isfinite(prediction).all():
                raise ValueError("forecaster returned invalid predictions")
            errors.append(prediction - actual)
            if np.std(prediction) and np.std(actual):
                correlations.append(float(np.corrcoef(prediction, actual)[0, 1]))
        error = np.concatenate(errors)
        results[int(horizon)] = {
            "mae": float(np.mean(np.abs(error))),
            "rmse": float(np.sqrt(np.mean(error ** 2))),
            "mean_correlation": float(np.mean(correlations)) if correlations else 0.0,
            "origins": len(origins),
        }
    return results
