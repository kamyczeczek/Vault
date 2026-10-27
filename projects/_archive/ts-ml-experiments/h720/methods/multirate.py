"""S-10 multi-rate / multi-scale forecaster (N-HiTS-style, closed-form).

Per-rate MaxPool-downsampled views of the fit series, one ELM expert
per rate, ensemble (hierarchical mean) readout:

- Rate ``r`` view: ``v_r[j] = max(series[(j+1)*r - 1 : (j+1)*r])`` —
  non-overlapping MaxPool(stride=r, kernel=r) over the hourly OT
  series (rate r expresses the worst-case level reached in each
  r-hour block). Rate 1 = the raw series (identity view).
- Rate-1 expert: EXACTLY the leaderboard parent ELM pathway —
  ``_lag_dataset(series, H, lags, q=3, hist=1.0)``, seed-42 hidden
  draw, Ridge(alpha=1.0) on the full H-step trajectory. With
  ``rates=(1,)`` and the parent config the model is byte-identical
  to ``HeuristicLagELM`` (asserted by the smoke gate and the sweep
  identity check on real data).
- Coarse rate-r expert: same pathway on the view — multi-output Ridge
  on the ``ceil(H/r)``-block trajectory (anchor-normalised, lags in
  view units). Prediction is upsampled to hourly steps by block
  index ``t // r`` (every hourly step t < H maps to exactly one
  predicted block; no clamping, no post-origin data).
- Readout: uniform mean over the per-rate hourly trajectories. This
  is the closed-form analogue of the N-HiTS hierarchical sum: with
  one rate it degenerates to the parent (scale-preserving), and
  each additional rate contributes an r-hour-resolution correction
  of the hourly path. Mean (not sum) keeps ``rates=(1,)`` identical
  to the parent instead of double-counting the level.

Deterministic: seed 42 for the single shared hidden draw; no other
RNG; MaxPool and averaging are closed-form. Anti-leakage: ``fit``
sees the training series only; every view, lag feature, and anchor
is built from trailing history at predict time.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np
from sklearn.linear_model import Ridge

from .base import BaseForecaster


class MultiRateELM(BaseForecaster):
    """Per-rate MaxPool views + per-rate ELM trajectory experts."""

    def __init__(
        self,
        rates: tuple[int, ...] = (1, 2, 4, 8),
        q: int = 3,
        history_fraction: float = 1.0,
        hidden_dim: int = 64,
        ridge_alpha: float = 1.0,
        lags_per_rate: tuple[int, ...] = (1, 2, 3, 6, 12),
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
        self.q = q
        self.history_fraction = history_fraction
        self.hidden_dim = hidden_dim
        self.ridge_alpha = ridge_alpha
        self.lags_per_rate = tuple(int(d) for d in lags_per_rate)

    # ------------------------------------------------------------------
    @staticmethod
    def _maxpool_view(series: np.ndarray, rate: int) -> np.ndarray:
        """Non-overlapping MaxPool view of the hourly series at rate r."""
        if rate == 1:
            return series
        n_blocks = len(series) // rate
        return series[: n_blocks * rate].reshape(n_blocks, rate).max(axis=1)

    # ------------------------------------------------------------------
    def fit(self, y: Iterable[float], *, horizon: int) -> "MultiRateELM":
        series = self._as_series(
            y,
            min_len=max(self.q, max(self.rates) * max(self.lags_per_rate))
            + horizon + 2,
        )
        self._check_horizon(horizon)
        self.horizon_ = int(horizon)
        # ONE shared hidden draw (seed 42) — the rate-1 arm equals the
        # parent ELM's draw exactly (same shape, same seed).
        rng = np.random.RandomState(42)
        W = rng.normal(0, 1, size=(len(self.lags_per_rate), self.hidden_dim))
        b = rng.uniform(-1, 1, size=(1, self.hidden_dim))
        self.W_, self.b_ = W, b

        self.experts_: dict[int, dict] = {}
        for r in self.rates:
            if r == 1:
                # parent pathway — byte-identity with HeuristicLagELM
                X, Y, _ = self._lag_dataset(
                    series, self.horizon_, self.lags_per_rate,
                    self.q, self.history_fraction,
                )
                H = np.tanh(X @ W + b)
                self.experts_[1] = {
                    "q": self.q,
                    "model": Ridge(
                        alpha=self.ridge_alpha, fit_intercept=True
                    ).fit(H, Y),
                }
                continue
            view = self._maxpool_view(series, r)
            horizon_h = -(-self.horizon_ // r)  # ceil(H/r) blocks
            q_r = max(1, self.q // r)           # ~q-hour anchor span
            X, Y, _ = self._lag_dataset(
                view, horizon_h, self.lags_per_rate, q_r,
                self.history_fraction,
            )
            H = np.tanh(X @ W + b)
            self.experts_[r] = {
                "q": q_r,
                "horizon_h": horizon_h,
                "model": Ridge(
                    alpha=self.ridge_alpha, fit_intercept=True
                ).fit(H, Y),
            }
        self.history_ = series
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        series = self.history_
        idx = len(series)
        preds: list[np.ndarray] = []
        for r in self.rates:
            e = self.experts_[r]
            if r == 1:
                anchor = self._anchor(series, idx, e["q"])
                x = self._lag_features(series, idx, self.lags_per_rate, anchor)
                H = np.tanh(x @ self.W_ + self.b_)
                preds.append(
                    np.asarray(e["model"].predict(H))[0] + anchor
                )
                continue
            view = self._maxpool_view(series, r)
            v_idx = len(view)
            anchor = self._anchor(view, v_idx, e["q"])
            xv = self._lag_features(view, v_idx, self.lags_per_rate, anchor)
            Hv = np.tanh(xv @ self.W_ + self.b_)
            block_path = np.asarray(e["model"].predict(Hv))[0]
            t = np.arange(self.horizon_)
            preds.append(block_path[t // r] + anchor)
        return np.mean(preds, axis=0)
