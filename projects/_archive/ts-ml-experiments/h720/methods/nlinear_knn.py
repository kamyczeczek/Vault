"""NLinear + KNN residual hybrid (S-16).

Frozen NLinear (L=336, ridge 1) as global baseline, KNN on its residuals
as local correction — the residual version from the user proposal:

  Ŷ = Ŷ_NLinear + α· R̂_KNN   where R = Y - Ŷ_NLinear

KNN searches on anchor-normalised lag features X' = X - x_L (same pipeline
as HeuristicLagKNN) and is trained on (X', R) pairs, not (X', Y).

Alpha fixed at 1.0 for the first bet; adaptive α(d) left for S-16b.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
from sklearn.neighbors import KNeighborsRegressor

from .base import BaseForecaster
from .neural_models import NLinear
from .knn_models import HeuristicLagKNN


class NLinearKNNHybrid(BaseForecaster):
    """NLinear (global) + KNN on residuals (local)."""

    def __init__(
        self,
        nlinear_length: int = 336,
        nlinear_alpha: float = 1.0,
        knn_delays: tuple[int, ...] = (14, 28, 42, 56, 70),
        knn_q: int = 3,
        knn_neighbors: int = 32,
        knn_history_fraction: float = 0.1,
        knn_normalize_scale: bool = True,
        knn_scale_window: int = 1440,
        knn_weights: str = "distance",
        knn_ema_alpha: float | None = 0.9,
        alpha: float = 1.0,
    ):
        if knn_weights not in ("uniform", "distance", "softmax"):
            raise ValueError("knn_weights must be uniform/distance/softmax")
        if knn_ema_alpha is not None and not (0 < knn_ema_alpha <= 1):
            raise ValueError("knn_ema_alpha must be in (0,1] or None")
        self.nlinear_length = int(nlinear_length)
        self.nlinear_alpha = float(nlinear_alpha)
        self.knn_delays = tuple(int(d) for d in knn_delays)
        self.knn_q = int(knn_q)
        self.knn_neighbors = int(knn_neighbors)
        self.knn_history_fraction = float(knn_history_fraction)
        self.knn_normalize_scale = bool(knn_normalize_scale)
        self.knn_scale_window = int(knn_scale_window)
        self.knn_weights = knn_weights
        self.knn_ema_alpha = knn_ema_alpha
        self.alpha = float(alpha)

    def _ema_anchor(self, series: np.ndarray, idx: int, alpha: float) -> float:
        ema = float(series[0])
        for t in range(1, idx):
            ema = alpha * float(series[t]) + (1 - alpha) * ema
        return ema

    def fit(self, y: Iterable[float], *, horizon: int) -> "NLinearKNNHybrid":
        series = self._as_series(y, min_len=max(self.nlinear_length, max(self.knn_delays), self.knn_q) + horizon + 2)
        self._check_horizon(horizon)
        self.horizon_ = int(horizon)

        # 1) Fit NLinear on full window → last-value normalised 336→720 Ridge
        self.nlinear_ = NLinear(input_length=self.nlinear_length, ridge_alpha=self.nlinear_alpha)
        self.nlinear_.fit(series, horizon=horizon)

        # 2) Build residual training set for KNN: for each origin i,
        #    compute NLinear's forecast for window ending at i, then R = Y - Ŷ_N
        #    X' is the KNN lag features at i (anchor-normalised)
        #    Use the same origins logic as HeuristicLagKNN / NLinear
        #    For simplicity, reuse HeuristicLagKNN's origin handling via a dummy KNN to get origins,
        #    but we need to generate X',Y pairs with EMA/SMA anchor as configured.

        # Build origins as KNN would (using its q/delays/history_fraction)
        # We need X_knn, Y_raw, origins
        # To avoid duplicating _lag_dataset, instantiate a temporary HeuristicLagKNN
        # to generate the origins and then compute residuals with NLinear forecasts.

        # We need to generate for each origin i:
        #   anchor_knn = EMA or SMA
        #   x = lag_features(series, i, delays, anchor_knn)
        #   y_nlinear_pred = NLinear forecast for window ending at i (using its own window)
        #   y_true = series[i:i+H]
        #   r = (y_true - y_nlinear_pred) / scale_knn   ???  But KNN's Y is anchor-normalised already
        # Instead, we train KNN on residual in the same normalised space as KNN's Y:
        #   KNN's Y is (series[i:i+H] - anchor_knn)/scale
        #   NLinear's Y is (series[i:i+H] - anchor_nlinear) ??? No, NLinear's anchor is window[-1]
        #   So residual in KNN's normalised space is:
        #   R_std = (Y_true - anchor_knn)/scale - (Ŷ_N - anchor_knn)/scale
        #   But Ŷ_N is already anchor_nlinear + ... — mixing anchors is messy.

        # Simpler: train KNN on raw residual in original space, then add:
        #   R_raw = Y_true - Ŷ_N (both in original space, length H)
        #   KNN predicts R_raw from X' (anchor-normalised lags)
        # This is the cleanest residual definition (user proposal: R = Y - Ŷ_N in original space).

        # So we need to for each origin i:
        #   X' as KNN would (anchor_knn normalised)
        #   Ŷ_N(i) = NLinear forecast for window ending at i
        #   R(i) = Y_true(i) - Ŷ_N(i)

        # Build origins for KNN
        dummy = HeuristicLagKNN(
            q=self.knn_q, neighbors=self.knn_neighbors, delays=self.knn_delays,
            history_fraction=self.knn_history_fraction, normalize_scale=self.knn_normalize_scale,
            scale_window=self.knn_scale_window, weights=self.knn_weights, ema_alpha=self.knn_ema_alpha
        )
        # Use dummy's _origins to get origins indices
        origins = dummy._origins(series, horizon, max(self.knn_q, max(self.knn_delays)), self.knn_history_fraction)

        # Precompute NLinear predictions for each origin
        # NLinear is frozen after fit on full series, but its forecast for origin i
        # should be based on window ending at i, not full history.
        # However NLinear.fit built its Ridge on all windows ending at various ends;
        # its predict() uses history_[-336:] — so to get Ŷ_N(i), we can temporarily
        # set nlinear_.history_ to series[:i] and call predict, then restore.
        # This is the correct per-origin NLinear forecast.

        X_list = []
        R_list = []
        orig_nlinear_history = self.nlinear_.history_
        # For EMA anchor, we need ema series for KNN anchors
        if self.knn_ema_alpha is not None:
            alpha = float(self.knn_ema_alpha)
            ema = np.empty_like(series, dtype=float)
            ema[0] = float(series[0])
            for t in range(1, len(series)):
                ema[t] = alpha * float(series[t]) + (1 - alpha) * ema[t-1]
        for i in origins:
            # X' for KNN at i
            if self.knn_ema_alpha is not None:
                anchor_knn = ema[i-1] if i>0 else float(series[0])
            else:
                anchor_knn = dummy._anchor(series, int(i), self.knn_q)
            scale_knn = dummy._window_scale(series, int(i), self.knn_normalize_scale, self.knn_scale_window)
            x = dummy._lag_features(series, int(i), self.knn_delays, anchor_knn, self.knn_normalize_scale, self.knn_scale_window)
            # NLinear forecast at i
            # need window of length nlinear_length ending at i
            if i < self.nlinear_length:
                continue  # not enough history for NLinear window
            # set history to series[:i] for NLinear predict
            self.nlinear_.history_ = series[:i] if series.ndim==1 else series[:i]
            # NLinear predict expects history_ to be set and will use last 336
            try:
                y_pred_nlinear = self.nlinear_.predict()
            except Exception:
                continue
            y_true = series[i:i+horizon]
            if len(y_true) < horizon:
                continue
            # raw residual
            r = y_true - y_pred_nlinear
            # KNN will be trained to predict r from x (x is (1, D), r is (H,))
            # KNN expects Y in shape (n, H) — we store r as is (already anchor-free? No, r is raw residual, not anchor-normalised)
            # But x is anchor-normalised, so KNN will learn mapping from normalised lags to raw residual
            # That's intentional: KNN corrects NLinear's raw error based on shape
            X_list.append(x[0])
            R_list.append(r)
        # restore
        self.nlinear_.history_ = orig_nlinear_history

        X_knn = np.asarray(X_list, dtype=float)
        R_knn = np.asarray(R_list, dtype=float)
        if len(X_knn) < 3:
            raise ValueError("not enough origins for KNN residual fit")

        # Fit KNN on residuals
        if self.knn_weights == "softmax":
            self.knn_X_ = X_knn
            self.knn_R_ = R_knn
            self.knn_model_ = KNeighborsRegressor(
                n_neighbors=min(self.knn_neighbors, len(X_knn)), weights="uniform"
            ).fit(X_knn, R_knn)
            dist, _ = self.knn_model_.kneighbors(X_knn, n_neighbors=min(5, len(X_knn)))
            nz = dist[dist > 1e-12]
            self.knn_sigma_ = float(nz.mean()) if len(nz) else 1.0
        else:
            self.knn_X_ = X_knn
            self.knn_R_ = R_knn
            self.knn_model_ = KNeighborsRegressor(
                n_neighbors=min(self.knn_neighbors, len(R_knn)), weights=self.knn_weights
            ).fit(X_knn, R_knn)
            dist, _ = self.knn_model_.kneighbors(X_knn, n_neighbors=min(5, len(X_knn)))
            nz = dist[dist > 1e-12]
            self.knn_sigma_ = float(nz.mean()) if len(nz) else 1.0
        self.history_ = series
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        series = self.history_
        idx = len(series)
        # NLinear base forecast
        y_base = self.nlinear_.predict()
        # KNN residual correction
        # Build x for current idx
        if self.knn_ema_alpha is not None:
            alpha = float(self.knn_ema_alpha)
            ema = float(series[0])
            for t in range(1, idx):
                ema = alpha * float(series[t]) + (1 - alpha) * ema
            anchor_knn = ema
        else:
            # use HeuristicLagKNN's anchor helper via dummy
            dummy = HeuristicLagKNN(q=self.knn_q, delays=self.knn_delays)
            anchor_knn = dummy._anchor(series, idx, self.knn_q)
        # scale for KNN lag features (same as fit)
        dummy2 = HeuristicLagKNN(q=self.knn_q, delays=self.knn_delays, normalize_scale=self.knn_normalize_scale, scale_window=self.knn_scale_window)
        scale_knn = dummy2._window_scale(series, idx, self.knn_normalize_scale, self.knn_scale_window)
        x = dummy2._lag_features(series, idx, self.knn_delays, anchor_knn, self.knn_normalize_scale, self.knn_scale_window)
        if self.knn_weights == "softmax":
            dist, ind = self.knn_model_.kneighbors(x, n_neighbors=min(self.knn_neighbors, len(self.knn_X_)))
            d = dist[0]
            w = np.exp(-d / max(float(self.knn_sigma_), 1e-12))
            w = w / w.sum()
            r_pred = (w @ self.knn_R_[ind[0]])
        else:
            r_pred = self.knn_model_.predict(x)[0]
        return y_base + self.alpha * r_pred
