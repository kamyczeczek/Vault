"""S-11 RBF-hidden ELM (local kernels + linear ridge readout).

Replaces the tanh hidden layer with Gaussian RBF units — local
kernels (the inductive bias kNN exploits) paired with the ELM
family's closed-form ridge readout. Motivated by the S-04
asymmetry: instance normalization helps kNN strongly (2.5583 →
2.3815 at window 720) but hurts the tanh ELM (2.3092 → 2.3289) —
local-distance learners are scale-sensitive, so an RBF hidden layer
inherits the kNN normalization gain that tanh cannot use.

- Centers: ``hidden_dim`` training-feature rows drawn iid
  (RandomState(42)) from the lag-feature matrix X — each unit is an
  actual observed lag pattern (support vectors of the data), not
  a synthetic direction.
- Width: one global ``sigma = mean pairwise center distance``
  (closed-form; deterministic). Response: ``exp(-||x - c||^2 /
  (2 sigma^2))`` — no intercept term needed (RBF row never exactly
  zero on real data), but Ridge keeps ``fit_intercept=True`` to
  stay comparable with the family convention.
- Features: EXACTLY the parent pathway — ``_lag_dataset`` with the
  S-04 ``normalize_scale`` flags (raw / norm@168 / norm@720), the
  same anchor q=3, the same fast lags.
- Targets: raw horizon (parent-comparable), or residual against a
  seasonal template via ``residual_period`` (m=24 daily / m=168
  weekly — the S-11 seasonal-residual arm inside the same class).
- Readout: Ridge(alpha) per the family convention.

Deterministic: seed 42 for the center draw; sigma, templates, and
residuals are closed-form. Anti-leakage: ``fit`` sees the training
series only; centers live in feature space built from fit-time
origins; predict builds features from trailing history only.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np
from sklearn.linear_model import Ridge

from .base import BaseForecaster


class RBFELM(BaseForecaster):
    """Gaussian-RBF hidden layer ELM with ridge readout."""

    def __init__(
        self,
        q: int = 3,
        history_fraction: float = 1.0,
        hidden_dim: int = 64,
        ridge_alpha: float = 1.0,
        delays: tuple[int, ...] = (1, 2, 3, 6, 12),
        normalize_scale: bool = False,
        scale_window: int = 168,
        residual_period: int = 0,
    ):
        if residual_period < 0:
            raise ValueError("residual_period must be >= 0 (0 = raw target)")
        self.q = q
        self.history_fraction = history_fraction
        self.hidden_dim = hidden_dim
        self.ridge_alpha = ridge_alpha
        self.delays = tuple(int(d) for d in delays)
        self.normalize_scale = normalize_scale
        self.scale_window = scale_window
        self.residual_period = int(residual_period)

    # ------------------------------------------------------------------
    @staticmethod
    def _rbf_features(
        X: np.ndarray, centers: np.ndarray, sigma: float
    ) -> np.ndarray:
        """Gaussian RBF responses, shape (n, hidden_dim)."""
        d2 = (
            ((X[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
            if X.ndim == 2 else None
        )
        return np.exp(-d2 / (2.0 * sigma * sigma))

    def _template(
        self, series: np.ndarray, idx: int, horizon: int
    ) -> np.ndarray:
        """Seasonal-naive template (period m) from pre-origin history."""
        m = self.residual_period
        pos = np.arange(idx - m, idx - m + horizon) % m
        return series[(idx - m) + pos]

    # ------------------------------------------------------------------
    def fit(self, y: Iterable[float], *, horizon: int) -> "RBFELM":
        series = self._as_series(
            y, min_len=max(self.q, max(self.delays)) + horizon + 2
        )
        self._check_horizon(horizon)
        self.horizon_ = int(horizon)
        X, Y, origins = self._lag_dataset(
            series, self.horizon_, self.delays, self.q,
            self.history_fraction, normalize_scale=self.normalize_scale,
            scale_window=self.scale_window,
        )
        if self.residual_period:
            # residual target in the SAME normalised space as Y:
            # Y_r = (actual - template) / scale = Y + (anchor -
            # template)/scale (template replaces the anchor as the
            # level carrier)
            templates = np.stack([
                self._template(series, int(i), self.horizon_)
                for i in origins
            ])
            scales = np.array([
                self._window_scale(series, int(i), self.normalize_scale,
                                   self.scale_window)
                for i in origins
            ])[:, None]
            anchors = np.array([
                self._anchor(series, int(i), self.q) for i in origins
            ])[:, None]
            Y = Y + (anchors - templates) / scales
        # centers: hidden_dim iid rows of the feature matrix (seed 42)
        rng = np.random.RandomState(42)
        idx = rng.choice(len(X), size=self.hidden_dim, replace=len(X)
                          < self.hidden_dim)
        self.centers_ = X[idx].copy()
        # global width: mean pairwise center distance
        d = np.linalg.norm(
            self.centers_[:, None, :] - self.centers_[None, :, :], axis=2
        )
        self.sigma_ = float(d[d > 0].mean()) if len(d) > 1 else 1.0
        H = self._rbf_features(X, self.centers_, self.sigma_)
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
        scale = self._window_scale(
            series, idx, self.normalize_scale, self.scale_window
        )
        x = self._lag_features(
            series, idx, self.delays, anchor,
            normalize_scale=self.normalize_scale,
            scale_window=self.scale_window,
        )
        H = self._rbf_features(x, self.centers_, self.sigma_)
        out = np.asarray(self.model_.predict(H))[0] * scale
        if self.residual_period:
            # template carries the level (anchor cancels by
            # construction of the residual target)
            return out + self._template(series, idx, self.horizon_)
        return out + anchor
