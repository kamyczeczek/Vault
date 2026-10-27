"""Small causal forecasting baselines for dynamical-system experiments."""
from __future__ import annotations
import numpy as np
from sklearn.linear_model import Ridge


def fit_delay_ridge(history, lag=24, alpha=1.0):
    x = np.asarray(history, dtype=float)
    if len(x) <= lag: raise ValueError("history must be longer than lag")
    X = np.stack([x[i-lag:i] for i in range(lag, len(x))])
    y = x[lag:]
    return Ridge(alpha=alpha).fit(X, y), lag


def predict_delay_recursive(model, history, horizon, lag=24):
    values = list(np.asarray(history, dtype=float)[-lag:])
    if len(values) != lag: raise ValueError("history must contain lag values")
    for _ in range(horizon):
        values.append(float(model.predict(np.asarray(values[-lag:]).reshape(1, -1))[0]))
    return np.asarray(values[-horizon:])


def recursive_delay_forecast(history, horizon, lag=24, alpha=1.0):
    model, lag = fit_delay_ridge(history, lag=lag, alpha=alpha)
    return predict_delay_recursive(model, history, horizon, lag=lag)
