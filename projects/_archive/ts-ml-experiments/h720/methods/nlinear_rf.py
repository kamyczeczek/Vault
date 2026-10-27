"""NLinearRF: NLinear windowing (last-value) + RandomForest readout.

Mirrors NLinear(336) — full window 336 → horizon 720 via
last-value normalisation, but replaces Ridge(alpha=1) with
RandomForestRegressor(n_estimators=trees, random_state=42).

Deterministic (random_state=42), scale-invariant (trees), no RevIN std.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from .base import BaseForecaster


class NLinearRF(BaseForecaster):
    """Last-value normalised window → RandomForest on horizon."""

    def __init__(self, input_length: int = 336, trees: int = 100):
        if input_length < 1:
            raise ValueError("input_length must be >=1")
        if trees < 1:
            raise ValueError("trees must be >=1")
        self.input_length = int(input_length)
        self.trees = int(trees)

    def _array(self, values: Iterable[float]) -> np.ndarray:
        arr = np.asarray(values, dtype=float)
        if arr.ndim not in (1,2) or len(arr) < self.input_length + 2 or not np.isfinite(arr).all():
            raise ValueError("values too short or non-finite")
        return arr

    def fit(self, y: Iterable[float], *, horizon: int, target_index: int = 0) -> "NLinearRF":
        series = self._array(y)
        self._check_horizon(horizon)
        if len(series) <= self.input_length + horizon:
            raise ValueError("invalid horizon or insufficient history")
        if series.ndim == 1:
            series = series[:, None]
        if target_index < 0 or target_index >= series.shape[1]:
            raise ValueError("target_index out of range")
        x_rows, y_rows = [], []
        for end in range(self.input_length, len(series) - horizon + 1):
            window = series[end - self.input_length:end]
            anchor = window[-1, target_index]
            x_rows.append((window - window[-1]).reshape(-1))
            y_rows.append(series[end:end+horizon, target_index] - anchor)
        self.model_ = RandomForestRegressor(
            n_estimators=self.trees, random_state=42, n_jobs=-1
        ).fit(np.asarray(x_rows), np.asarray(y_rows))
        self.history_ = series
        self.target_index = target_index
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        raw = self.history_[-self.input_length:]
        window = raw[:, None] if raw.ndim == 1 else raw
        anchor = window[-1, self.target_index]
        x = (window - window[-1]).reshape(1, -1)
        return np.asarray(self.model_.predict(x)[0]) + anchor
