"""Calendar-aware linear forecasters for S-40.

Each class extends the S-26 NLinear/DLinear/RLinear pattern with
7 calendar features concatenated to the OT window features.
Level-free via last-row anchor subtraction.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

import numpy as np
from sklearn.linear_model import Ridge

H720_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(H720_ROOT))

from methods.base import BaseForecaster  # noqa: E402
from calendar_features import load_or_compute, calendar_vector  # noqa: E402
from data import get_protocol_data  # noqa: E402


def _get_protocol_dates() -> list:
    """Extract datetime objects for all 17,420 raw rows."""
    import csv
    from datetime import datetime
    rows = list(csv.DictReader(open(H720_ROOT / "ETTh1.csv")))
    return [datetime.strptime(r["date"], "%Y-%m-%d %H:%M:%S") for r in rows]


# Precompute calendar features once at module load.
_PROTOCOL_DATES = _get_protocol_dates()
_CALENDAR_ALL = load_or_compute(_PROTOCOL_DATES)


class CalendarNLinear(BaseForecaster):
    """NLinear with calendar features concatenated to the anchor-differenced window."""

    def __init__(self, input_length: int = 336, ridge_alpha: float = 1.0):
        self.input_length = input_length
        self.ridge_alpha = ridge_alpha

    def _array(self, values: Iterable[float]) -> np.ndarray:
        result = np.asarray(values, dtype=float)
        if (
            result.ndim not in (1, 2)
            or len(result) < self.input_length + 2
            or not np.isfinite(result).all()
        ):
            raise ValueError("values are too short or non-finite")
        return result

    def fit(self, y: Iterable[float], *, horizon: int, target_index: int = 0,
            origin_idx: int | None = None) -> "CalendarNLinear":
        """Fit on history y.

        origin_idx: absolute row index in the raw ETTh1.csv (0..17419).
        Used to look up the calendar features for the training window's origins.
        For the rolling-arm harness, origin_idx is the START of the fit window.
        We use the calendar at the LAST row of the fit window (the origin).
        """
        series = self._array(y)
        self._check_horizon(horizon)
        if series.ndim == 1:
            series = series[:, None]
        if target_index < 0 or target_index >= series.shape[1]:
            raise ValueError("target_index out of range")

        # For training rows, origin calendar = calendar at the window's last index.
        # The fit_history passed in is the full fit set; we need global indices.
        # Caller must set self._fit_start to the first global index of `y`.
        fit_start = getattr(self, "_fit_start", 0)

        x_rows, y_rows = [], []
        for end in range(self.input_length, len(series) - horizon + 1):
            window = series[end - self.input_length : end]
            anchor = window[-1, target_index]
            ot_feat = (window - window[-1]).reshape(-1)
            global_idx = fit_start + end - 1  # last row of window = origin
            cal_feat = _CALENDAR_ALL[global_idx]
            x_rows.append(np.concatenate([ot_feat, cal_feat]))
            y_rows.append(series[end : end + horizon, target_index] - anchor)

        X = np.asarray(x_rows)
        Y = np.asarray(y_rows)
        self.model = Ridge(alpha=self.ridge_alpha, fit_intercept=True).fit(X, Y)
        self.history_ = series
        self.target_index = target_index
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self, origin_idx: int | None = None) -> np.ndarray:
        """Predict H steps from the current history_.

        origin_idx: global row index of the origin (last row of history_).
        """
        self._check_fitted()
        raw = self.history_[-self.input_length :]
        window = raw[:, None] if raw.ndim == 1 else raw
        anchor = window[-1, self.target_index]
        ot_feat = (window - window[-1]).reshape(-1)
        global_idx = origin_idx if origin_idx is not None else getattr(self, "_last_origin_idx", 0)
        cal_feat = _CALENDAR_ALL[global_idx]
        x = np.concatenate([ot_feat, cal_feat]).reshape(1, -1)
        return np.asarray(self.model.predict(x)[0]) + anchor


class CalendarDLinear(BaseForecaster):
    """DLinear decomposition + calendar features on the seasonal residual."""

    def __init__(self, input_length: int = 96, kernel_size: int = 25, ridge_alpha: float = 0.0):
        self.input_length = input_length
        self.kernel_size = kernel_size
        self.ridge_alpha = ridge_alpha

    def _array(self, values: Iterable[float]) -> np.ndarray:
        result = np.asarray(values, dtype=float)
        if result.ndim not in (1, 2) or len(result) < self.input_length + 2 or not np.isfinite(result).all():
            raise ValueError("values too short or non-finite")
        return result if result.ndim == 2 else result[:, None]

    @staticmethod
    def _moving_average(x: np.ndarray, kernel_size: int) -> np.ndarray:
        """Trailing moving average with kernel_size window."""
        pad = kernel_size // 2
        cumsum = np.cumsum(np.pad(x, (pad, pad), mode="edge"))
        return (cumsum[kernel_size:] - cumsum[:-kernel_size]) / kernel_size

    def fit(self, y: Iterable[float], *, horizon: int, target_index: int = 0,
            origin_idx: int | None = None) -> "CalendarDLinear":
        series = self._array(y)
        self._check_horizon(horizon)
        if target_index < 0 or target_index >= series.shape[1]:
            raise ValueError("target_index out of range")

        fit_start = getattr(self, "_fit_start", 0)
        x_rows, y_rows = [], []
        for end in range(self.input_length, len(series) - horizon + 1):
            window = series[end - self.input_length : end, target_index]
            trend = self._moving_average(window, self.kernel_size)
            seasonal = window - trend
            anchor = float(window[-1])
            ot_feat = (seasonal - seasonal[-1]).reshape(-1)
            global_idx = fit_start + end - 1
            cal_feat = _CALENDAR_ALL[global_idx]
            x_rows.append(np.concatenate([ot_feat, cal_feat]))
            # target = full series - trend_projection - anchor
            target_window = series[end : end + horizon, target_index]
            target_trend = self._moving_average(
                np.concatenate([window, target_window]), self.kernel_size
            )[-horizon:]
            y_rows.append(target_window - target_trend - anchor)

        X = np.asarray(x_rows)
        Y = np.asarray(y_rows)
        if self.ridge_alpha > 0.0:
            self.model = Ridge(alpha=self.ridge_alpha, fit_intercept=True).fit(X, Y)
        else:
            from sklearn.linear_model import LinearRegression
            self.model = LinearRegression(fit_intercept=True).fit(X, Y)
        self.history_ = series
        self.target_index = target_index
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self, origin_idx: int | None = None) -> np.ndarray:
        self._check_fitted()
        raw = self.history_[-self.input_length :]
        window = raw[:, None] if raw.ndim == 1 else raw
        w = window[:, self.target_index] if window.ndim == 2 else window
        trend = self._moving_average(w, self.kernel_size)
        seasonal = w - trend
        anchor = float(w[-1])
        ot_feat = (seasonal - seasonal[-1]).reshape(-1)
        global_idx = origin_idx if origin_idx is not None else getattr(self, "_last_origin_idx", 0)
        cal_feat = _CALENDAR_ALL[global_idx]
        x = np.concatenate([ot_feat, cal_feat]).reshape(1, -1)
        seasonal_pred = np.asarray(self.model.predict(x)[0])
        # trend forecast = last trend value projected forward
        trend_forecast = np.full(self.horizon_, float(trend[-1]))
        return trend_forecast + seasonal_pred + anchor


class CalendarRLinear(BaseForecaster):
    """RLinear with calendar features concatenated to standardized window."""

    def __init__(self, input_length: int = 336, ridge_alpha: float = 0.0):
        self.input_length = input_length
        self.ridge_alpha = ridge_alpha
        self._SCALE_EPS = 1e-8

    def _array(self, values: Iterable[float]) -> np.ndarray:
        result = np.asarray(values, dtype=float)
        if result.ndim not in (1, 2) or len(result) < self.input_length + 2 or not np.isfinite(result).all():
            raise ValueError("values too short or non-finite")
        return result if result.ndim == 2 else result[:, None]

    def fit(self, y: Iterable[float], *, horizon: int, target_index: int = 0,
            origin_idx: int | None = None) -> "CalendarRLinear":
        series = self._array(y)
        self._check_horizon(horizon)
        if target_index < 0 or target_index >= series.shape[1]:
            raise ValueError("target_index out of range")

        fit_start = getattr(self, "_fit_start", 0)
        x_rows, y_rows = [], []
        for end in range(self.input_length, len(series) - horizon + 1):
            window = series[end - self.input_length : end, target_index]
            mu = float(window.mean())
            sigma = max(float(window.std()), self._SCALE_EPS)
            ot_feat = ((window - mu) / sigma).reshape(-1)
            global_idx = fit_start + end - 1
            cal_feat = _CALENDAR_ALL[global_idx]
            x_rows.append(np.concatenate([ot_feat, cal_feat]))
            y_rows.append((series[end : end + horizon, target_index] - mu) / sigma)

        X = np.asarray(x_rows)
        Y = np.asarray(y_rows)
        if self.ridge_alpha > 0.0:
            self.model = Ridge(alpha=self.ridge_alpha, fit_intercept=True).fit(X, Y)
        else:
            from sklearn.linear_model import LinearRegression
            self.model = LinearRegression(fit_intercept=True).fit(X, Y)
        self.history_ = series
        self.target_index = target_index
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self, origin_idx: int | None = None) -> np.ndarray:
        self._check_fitted()
        raw = self.history_[-self.input_length :]
        window = raw[:, None] if raw.ndim == 1 else raw
        w = window[:, self.target_index] if window.ndim == 2 else window
        mu = float(w.mean())
        sigma = max(float(w.std()), self._SCALE_EPS)
        ot_feat = ((w - mu) / sigma).reshape(-1)
        global_idx = origin_idx if origin_idx is not None else getattr(self, "_last_origin_idx", 0)
        cal_feat = _CALENDAR_ALL[global_idx]
        x = np.concatenate([ot_feat, cal_feat]).reshape(1, -1)
        out = np.asarray(self.model.predict(x)[0])
        return out * sigma + mu
