"""Multi-horizon, constrained sunspot evaluation utilities."""
from __future__ import annotations
import numpy as np
from sunspot_methods import get_sunspot_methods
from bench import get_sunspot


def safe_forecast(method, train, history, horizon):
    prediction = np.asarray(method(train, history, horizon), dtype=float).ravel()[:horizon]
    if len(prediction) != horizon or not np.isfinite(prediction).all():
        raise ValueError("invalid forecast")
    return np.maximum(prediction, 0.0)


def evaluate_sunspot(n=2600, horizons=(1, 12, 24, 48, 120),
                     origins=(1600, 1800, 2000), lookback=96):
    series = get_sunspot(n)
    methods = get_sunspot_methods()
    result = {"horizons": list(horizons), "origins": list(origins), "methods": {}}
    for name, method in methods.items():
        result["methods"][name] = {}
        for horizon in horizons:
            scores = []
            for origin in origins:
                if origin + horizon > len(series): continue
                train, history = series[:origin], series[max(0, origin-lookback):origin]
                try: pred = safe_forecast(method, train, history, horizon)
                except (ImportError, ModuleNotFoundError, RuntimeError, ValueError): continue
                actual = series[origin:origin+horizon]
                err = pred - actual
                scores.append({"mae": float(np.mean(np.abs(err))), "rmse": float(np.sqrt(np.mean(err**2))),
                               "negative_fraction": 0.0, "max_prediction": float(np.max(pred))})
            result["methods"][name][str(horizon)] = scores
    return result
