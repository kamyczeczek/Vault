"""S-11 seasonal-naive-anchored residual learning (closed-form ELM).

Learns the deviation from a seasonal-naive template instead of the
raw anchor-normalised target:

- Template at origin ``i``: ``T(i)[h] = series[i - m + (h mod m)]``
  for ``h in [0, H)`` — the canonical seasonal-naive forecast of
  period ``m`` (``seasonal_forecast`` semantics; ``m=24`` daily,
  ``m=168`` weekly), built strictly from pre-origin history.
- Residual mode target: ``Y_r[i] = (series[i:i+H] - T(i)) / scale`` —
  the template REPLACES the anchor as the level carrier; predict
  re-adds ``template`` (never anchor + template together).
- Raw mode (``mode="raw"``): EXACTLY the parent ELM pathway —
  ``_lag_dataset``'s anchor-normalised Y untouched, seed-42 hidden
  draw, Ridge on Y, predict ``out*scale + anchor`` — byte-identical
  to ``HeuristicLagELM`` (asserted by the smoke identity gate), so
  the residual decomposition is the only moving part.
- Expert: the parent's lag features X (anchor-normalised, fast
  lags, q=3) and tanh hidden layer are shared verbatim.

Deterministic: seed 42 hidden draw only; template and residual are
closed-form. Anti-leakage: ``fit`` sees the training series only;
at predict time the template is built from trailing history.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np
from sklearn.linear_model import Ridge

from .base import BaseForecaster


class SeasonalResidualELM(BaseForecaster):
    """ELM on the residual against a seasonal-naive template."""

    def __init__(
        self,
        period: int = 24,
        q: int = 3,
        history_fraction: float = 1.0,
        hidden_dim: int = 64,
        ridge_alpha: float = 1.0,
        delays: tuple[int, ...] = (1, 2, 3, 6, 12),
        mode: str = "residual",
    ):
        if period < 1:
            raise ValueError("period must be >= 1")
        if mode not in ("residual", "raw"):
            raise ValueError(f"mode must be 'residual' or 'raw', got {mode!r}")
        self.period = int(period)
        self.q = q
        self.history_fraction = history_fraction
        self.hidden_dim = hidden_dim
        self.ridge_alpha = ridge_alpha
        self.delays = tuple(int(d) for d in delays)
        self.mode = mode

    # ------------------------------------------------------------------
    @staticmethod
    def _template(series: np.ndarray, idx: int, horizon: int, m: int):
        """Seasonal-naive template for horizon steps from origin idx."""
        pos = np.arange(idx - m, idx - m + horizon) % m
        return series[(idx - m) + pos]

    # ------------------------------------------------------------------
    def fit(self, y: Iterable[float], *, horizon: int) -> "SeasonalResidualELM":
        series = self._as_series(
            y, min_len=max(self.q, max(self.delays), self.period)
            + horizon + 2
        )
        self._check_horizon(horizon)
        self.horizon_ = int(horizon)
        # parent pathway — identical features and hidden draw
        X, Y, origins = self._lag_dataset(
            series, self.horizon_, self.delays, self.q,
            self.history_fraction,
        )
        if self.mode == "residual":
            # residual target in the SAME normalised space as the
            # parent's Y (scale == 1 unless a subclass normalises):
            # Y_r = (actual - template) / scale. The template
            # replaces the anchor as the level carrier.
            templates = np.stack([
                self._template(series, int(i), self.horizon_, self.period)
                for i in origins
            ])
            actual = series[origins[:, None] + np.arange(self.horizon_)]
            anchors = np.array([self._anchor(series, int(i), self.q)
                                for i in origins])[:, None]
            # parent Y = (actual - anchor); residual Y = parent Y +
            # (anchor - template) = (actual - template) in scale-1 space
            Y = Y + anchors - templates
        rng = np.random.RandomState(42)
        self.W_ = rng.normal(0, 1, size=(len(self.delays), self.hidden_dim))
        self.b_ = rng.uniform(-1, 1, size=(1, self.hidden_dim))
        H = np.tanh(X @ self.W_ + self.b_)
        self.model_ = Ridge(
            alpha=self.ridge_alpha, fit_intercept=True
        ).fit(H, Y)
        self.history_ = series
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        series = self.history_
        idx = len(series)
        anchor = self._anchor(series, idx, self.q)
        x = self._lag_features(series, idx, self.delays, anchor)
        H = np.tanh(x @ self.W_ + self.b_)
        out = np.asarray(self.model_.predict(H))[0]
        if self.mode == "residual":
            template = self._template(series, idx, self.horizon_,
                                      self.period)
            # template carries the level: out is the (scale-1)
            # residual head
            return out + template
        return out + anchor
