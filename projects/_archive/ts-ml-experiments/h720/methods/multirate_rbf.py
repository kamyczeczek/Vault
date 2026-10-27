"""S-13 MultiRate + RBF hybrid (RRoI: complementarity of the two ELM wins).

Per-rate MaxPool views (S-10) feeding per-rate Gaussian RBF experts (S-11),
mean-ensemble readout.

- Rate r view: non-overlapping MaxPool(stride=r, kernel=r) max over OT.
  Rate 1 = raw series (identity). Coarse rates express worst-case level
  per r-hour block (same view as MultiRateELM).
- Per-rate expert: EXACTLY the RBFELM pathway on that view — lag features
  (delays 1,2,3,6,12, anchor q, optional RevIN scale), iid centers
  (RandomState(42) sequential draws across rates), global sigma
  (mean pairwise center distance), Ridge(alpha) on trajectory. With
  rates=(1,) and same hidden_dim/ridge/delays/q the model is byte-identical
  to RBFELM (smoke identity). Hybrid's r=1 arm therefore inherits RBFELM's
  W4 drift robustness, while r=2/4 arms add multi-scale block corrections.
- Readout: uniform mean over per-rate hourly trajectories (block-upsample
  via t//r for r>1, like MultiRateELM). With one rate degenerates to
  parent, with multiple rates each added view contributes a correction
  without double-counting level.

Deterministic: seed 42 for the shared center-draw sequence; no other RNG.
Anti-leakage: fit sees training series only; views, features, anchors,
scales built from trailing history at predict time.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
from sklearn.linear_model import Ridge

from .base import BaseForecaster


class MultiRateRBF(BaseForecaster):
    """Per-rate MaxPool views + per-rate RBF trajectory experts."""

    def __init__(
        self,
        rates: tuple[int, ...] = (1, 2, 4),
        q: int = 3,
        history_fraction: float = 1.0,
        hidden_dim: int = 64,
        ridge_alpha: float = 1.0,
        delays: tuple[int, ...] = (1, 2, 3, 6, 12),
        normalize_scale: bool = False,
        scale_window: int = 168,
    ):
        self.rates = tuple(int(r) for r in rates)
        if not self.rates or any(r < 1 for r in self.rates):
            raise ValueError("rates must be a non-empty tuple of ints >= 1")
        if len(set(self.rates)) != len(self.rates):
            raise ValueError("rates must be distinct")
        if 1 not in self.rates:
            raise ValueError(
                "rates must include 1 (the hourly expert is the base "
                "trajectory; coarser rates only refine it)"
            )
        self.q = int(q)
        self.history_fraction = float(history_fraction)
        self.hidden_dim = int(hidden_dim)
        self.ridge_alpha = float(ridge_alpha)
        self.delays = tuple(int(d) for d in delays)
        self.normalize_scale = bool(normalize_scale)
        self.scale_window = int(scale_window)

    # ------------------------------------------------------------------
    @staticmethod
    def _maxpool_view(series: np.ndarray, rate: int) -> np.ndarray:
        if rate == 1:
            return series
        n_blocks = len(series) // rate
        return series[: n_blocks * rate].reshape(n_blocks, rate).max(axis=1)

    @staticmethod
    def _rbf_features(
        X: np.ndarray, centers: np.ndarray, sigma: float
    ) -> np.ndarray:
        # X (n, d) ; centers (k, d) -> (n, k)
        # handle 1-row case
        if X.ndim == 1:
            X = X.reshape(1, -1)
        d2 = ((X[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        return np.exp(-d2 / (2.0 * sigma * sigma))

    # ------------------------------------------------------------------
    def fit(self, y: Iterable[float], *, horizon: int) -> "MultiRateRBF":
        series = self._as_series(
            y,
            min_len=max(self.q, max(self.rates) * max(self.delays))
            + horizon
            + 2,
        )
        self._check_horizon(horizon)
        self.horizon_ = int(horizon)

        rng = np.random.RandomState(42)
        # process r=1 first for byte-identity with RBFELM when rates=(1,)
        ordered = sorted(self.rates)
        self.experts_: dict[int, dict] = {}
        for r in ordered:
            if r == 1:
                X, Y, _ = self._lag_dataset(
                    series,
                    self.horizon_,
                    self.delays,
                    self.q,
                    self.history_fraction,
                    normalize_scale=self.normalize_scale,
                    scale_window=self.scale_window,
                )
            else:
                view = self._maxpool_view(series, r)
                horizon_h = -(-self.horizon_ // r)  # ceil
                q_r = max(1, self.q // r)
                X, Y, _ = self._lag_dataset(
                    view,
                    horizon_h,
                    self.delays,
                    q_r,
                    self.history_fraction,
                    normalize_scale=self.normalize_scale,
                    scale_window=self.scale_window,
                )
            # iid centers from this view's X
            idx = rng.choice(len(X), size=self.hidden_dim, replace=len(X) < self.hidden_dim)
            centers = X[idx].copy()
            d = np.linalg.norm(
                centers[:, None, :] - centers[None, :, :], axis=2
            )
            sigma = float(d[d > 0].mean()) if len(d) > 1 else 1.0
            H = self._rbf_features(X, centers, sigma)
            model = Ridge(alpha=self.ridge_alpha, fit_intercept=True).fit(H, Y)
            # store per-rate meta for predict
            if r == 1:
                self.experts_[r] = {
                    "q": self.q,
                    "horizon_h": self.horizon_,
                    "centers": centers,
                    "sigma": sigma,
                    "model": model,
                }
            else:
                self.experts_[r] = {
                    "q": max(1, self.q // r),
                    "horizon_h": -(-self.horizon_ // r),
                    "centers": centers,
                    "sigma": sigma,
                    "model": model,
                }
        # keep original input order for readout (mean is order-invariant but keep deterministic)
        self.history_ = series
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        series = self.history_
        idx = len(series)
        preds: list[np.ndarray] = []
        # iterate in self.rates order (user's order) — mean is commutative
        for r in self.rates:
            e = self.experts_[r]
            if r == 1:
                anchor = self._anchor(series, idx, e["q"])
                scale = self._window_scale(series, idx, self.normalize_scale, self.scale_window)
                x = self._lag_features(series, idx, self.delays, anchor, self.normalize_scale, self.scale_window)
                H = self._rbf_features(x, e["centers"], e["sigma"])
                block_path = np.asarray(e["model"].predict(H))[0] * scale + anchor
                preds.append(block_path)
                continue
            view = self._maxpool_view(series, r)
            v_idx = len(view)
            anchor = self._anchor(view, v_idx, e["q"])
            scale = self._window_scale(view, v_idx, self.normalize_scale, self.scale_window)
            xv = self._lag_features(view, v_idx, self.delays, anchor, self.normalize_scale, self.scale_window)
            Hv = self._rbf_features(xv, e["centers"], e["sigma"])
            block_path = np.asarray(e["model"].predict(Hv))[0] * scale + anchor
            t = np.arange(self.horizon_)
            preds.append(block_path[t // r])
        return np.mean(preds, axis=0)
