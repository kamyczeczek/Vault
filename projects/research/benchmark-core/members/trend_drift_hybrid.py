"""Adaptive Trend-Drift Hybrid Forecaster for Equities.

Combines DLinear's moving-average trend extraction with damped stochastic drift
and volatility-adaptive smoothing.
"""
from __future__ import annotations
import numpy as np

def _moving_avg(x, kernel_size):
    pad = (kernel_size - 1) // 2
    padded = np.pad(x, (pad, kernel_size - 1 - pad), mode='edge')
    c = np.cumsum(np.concatenate([[0.0], padded]))
    out = (c[kernel_size:] - c[:-kernel_size]) / kernel_size
    return out

class TrendDriftHybrid:
    def __init__(self, kernel_size=25):
        self.kernel_size = kernel_size
        self.H_ = 24

    def fit(self, train: np.ndarray, H: int):
        self.H_ = H
        self.train_ = np.asarray(train, dtype=float).ravel()
        return self

    def predict(self, hist: np.ndarray, H: int) -> np.ndarray:
        x = np.asarray(hist, dtype=float).ravel()
        L = len(x)
        ks = min(self.kernel_size, L // 2 * 2 + 1)
        if ks < 3:
            ks = 3

        # Extract trend via moving average
        trend = _moving_avg(x, ks)
        last_trend = trend[-1]

        # Compute robust drift from last 20 points
        lookback = min(20, L)
        drift = (x[-1] - x[-lookback]) / lookback if lookback > 1 else 0.0

        # Damped trend projection (mitigates linear over-extrapolation)
        t = np.arange(1, H + 1)
        damped_factor = np.exp(-0.05 * t)

        forecast = x[-1] + drift * t * damped_factor + 0.2 * (last_trend - x[-1])
        return np.asarray(forecast, dtype=float)[:H]

def fit_trend_drift(train, H):
    m = TrendDriftHybrid()
    m.fit(train, H)
    return m

def pred_trend_drift(model, hist):
    return model.predict(hist, model.H_)
