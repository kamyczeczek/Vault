"""Low-frequency plus residual sunspot baseline."""
from __future__ import annotations
import numpy as np
from bench import fit_nlinear, pred_nlinear


def hybrid_sunspot_forecast(train, history, horizon, window=13):
    y = np.asarray(train, dtype=float)
    if len(y) < window + 20: raise ValueError("training series is too short")
    kernel = np.ones(window) / window
    low = np.convolve(y, kernel, mode="same")
    residual = y - low
    low_model = fit_nlinear(low, horizon, 10.0)
    res_model = fit_nlinear(residual, horizon, 10.0)
    low_pred = np.asarray(pred_nlinear(low_model, history), dtype=float).ravel()[:horizon]
    hist_low = np.convolve(np.asarray(history), kernel, mode="same")
    hist_res = np.asarray(history) - hist_low
    res_pred = np.asarray(pred_nlinear(res_model, hist_res), dtype=float).ravel()[:horizon]
    return np.maximum(low_pred + res_pred, 0.0)
