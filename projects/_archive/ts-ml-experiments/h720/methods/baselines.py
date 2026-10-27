"""Trivial reference baselines for time-series forecasting.

All baselines follow the unified forecaster interface:

    Persistence().fit(y, horizon=H).predict() -> np.ndarray (H,)
"""

from __future__ import annotations

from typing import Iterable

import numpy as np

from .base import BaseForecaster


class Persistence(BaseForecaster):
    """Repeat the last training value for the whole horizon."""

    def fit(self, y: Iterable[float], *, horizon: int) -> "Persistence":
        series = self._as_series(y, min_len=1)
        self._check_horizon(horizon)
        self.horizon_ = int(horizon)
        self.last_value_ = float(series[-1])
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        return np.full(self.horizon_, self.last_value_, dtype=float)


def seasonal_forecast(history: Iterable[float], horizon: int, kind: str) -> np.ndarray:
    """Seasonal-naive forecast.

    ``kind`` selects the lag: ``persistence`` -> 1, ``daily`` -> 24, ``weekly`` -> 168.
    """
    if horizon < 1:
        raise ValueError("horizon must be positive")
    h = np.asarray(list(history), dtype=float)
    if h.ndim != 1 or len(h) < 1 or not np.isfinite(h).all():
        raise ValueError("history must be a finite non-empty series")
    lag = {"persistence": 1, "daily": 24, "weekly": 168}.get(kind)
    if lag is None or len(h) < lag:
        raise ValueError(f"insufficient history for {kind} baseline")
    if kind == "persistence":
        return np.repeat(h[-1], horizon)
    return np.resize(h[-lag:], horizon)


def seasonal_score(
    history: Iterable[float], actual: Iterable[float], kind: str
) -> dict[str, float]:
    """MAE/RMSE of a seasonal-naive forecast against ``actual``."""
    h = np.asarray(list(history), dtype=float)
    a = np.asarray(list(actual), dtype=float)
    pred = seasonal_forecast(h, len(a), kind)
    error = a - pred
    return {
        "model": kind,
        "horizon": int(len(a)),
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "status": "ok",
    }
