"""Simple horizon-aware selector using development-origin validation."""
from __future__ import annotations
import numpy as np
from sunspot_eval import safe_forecast


def choose_methods(methods, series, development_origins, horizon, lookback=96):
    scores = {}
    for name, method in methods.items():
        errors=[]
        for origin in development_origins:
            train=series[:origin]; hist=series[origin-lookback:origin]
            try: errors.append(np.mean(np.abs(safe_forecast(method, train, hist, horizon)-series[origin:origin+horizon])))
            except (ImportError, ModuleNotFoundError, RuntimeError, ValueError): pass
        if errors: scores[name]=float(np.mean(errors))
    return min(scores, key=scores.get) if scores else None
