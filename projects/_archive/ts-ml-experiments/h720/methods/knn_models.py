"""Tree / forest / AR-residual forecasting models built on lag features.

All models follow the unified forecaster interface:

    model.fit(y, horizon=H) -> model
    model.predict() -> np.ndarray (H,)

Feature construction (anchor-normalised lags) is factored into
:class:`~methods.base.BaseForecaster` so every model shares one code path.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor

from .base import BaseForecaster

# --------------------------------------------------------------------------
# Balanced-lag ensemble: 16 expert lag sets spanning fast/daily/weekly scales
# --------------------------------------------------------------------------
LAGS: tuple[tuple[int, ...], ...] = (
    (1, 24, 168),
    (2, 48, 168),
    (3, 72, 168),
    (6, 24, 168),
    (12, 48, 168),
    (1, 2, 24),
    (2, 3, 48),
    (3, 6, 72),
    (6, 12, 24),
    (1, 12, 48),
    (1, 3, 168),
    (2, 6, 168),
    (3, 12, 168),
    (1, 6, 72),
    (2, 12, 72),
    (6, 48, 168),
)


# --------------------------------------------------------------------------
# Heuristic embedded-lag KNN (direct multi-output)
# --------------------------------------------------------------------------
class HeuristicLagKNN(BaseForecaster):
    """Direct multi-output KNN over anchor-normalised lag features."""

    def __init__(
        self,
        q: int = 6,
        neighbors: int = 5,
        delays: tuple[int, ...] = (1, 2, 3, 6, 12, 24),
        history_fraction: float = 1.0,
        normalize_scale: bool = False,
        scale_window: int = 168,
        affine: bool = False,
        weights: str = "distance",
        ema_alpha: float | None = None,
    ):
        if weights not in ("uniform", "distance", "softmax"):
            raise ValueError("weights must be 'uniform', 'distance', or 'softmax'")
        if ema_alpha is not None and not (0 < ema_alpha <= 1):
            raise ValueError("ema_alpha must be in (0,1] or None")
        self.q = q
        self.neighbors = neighbors
        self.delays = tuple(int(d) for d in delays)
        self.history_fraction = history_fraction
        self.normalize_scale = normalize_scale
        self.scale_window = scale_window
        self.affine = affine
        self.weights = weights
        self.ema_alpha = ema_alpha
    def fit(self, y: Iterable[float], *, horizon: int) -> "HeuristicLagKNN":
        series = self._as_series(y, min_len=max(self.q, max(self.delays)) + horizon + 2)
        self._check_horizon(horizon)
        # EMA anchor vs SMA anchor branching
        if self.ema_alpha is not None:
            alpha = float(self.ema_alpha)
            ema = np.empty_like(series, dtype=float)
            ema[0] = float(series[0])
            for t in range(1, len(series)):
                ema[t] = alpha * float(series[t]) + (1 - alpha) * ema[t-1]
            origins = self._origins(series, horizon, max(self.q, max(self.delays)), self.history_fraction)
            anchors = ema[origins - 1]
            scales = np.array([self._window_scale(series, int(i), self.normalize_scale, self.scale_window) for i in origins])
            X = np.column_stack([(series[origins - d] - anchors) / scales for d in self.delays]).astype(float)
            Y = np.stack([(series[i:i+horizon] - a) / s for i, a, s in zip(origins, anchors, scales)])
            self.ema_ = ema
        else:
            X, Y, origins = self._lag_dataset(
                series,
                horizon,
                self.delays,
                self.q,
                self.history_fraction,
                normalize_scale=self.normalize_scale,
                scale_window=self.scale_window,
            )
            self.ema_ = None
        if self.weights == "softmax":
            self.X_ = X
            self.Y_ = Y
            self.model_ = KNeighborsRegressor(
                n_neighbors=min(self.neighbors, len(origins)), weights="uniform"
            ).fit(X, Y)
            dist, _ = self.model_.kneighbors(X, n_neighbors=min(5, len(X)))
            nz = dist[dist > 1e-12]
            self.sigma_ = float(nz.mean()) if len(nz) else 1.0
            if self.affine:
                P_std = self._loo_knn_predictions(X, Y, self.neighbors)
                self.affine_gamma_, self.affine_beta_ = self._fit_affine(P_std, Y)
        else:
            self.X_ = None
            self.sigma_ = None
            self.model_ = KNeighborsRegressor(
                n_neighbors=min(self.neighbors, len(origins)), weights=self.weights
            ).fit(X, Y)
            if self.affine:
                P_std = self._loo_knn_predictions(X, Y, self.neighbors)
                self.affine_gamma_, self.affine_beta_ = self._fit_affine(P_std, Y)
        self.history_ = series
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        series = self.history_
        idx = len(series)
        if self.ema_alpha is not None:
            alpha = float(self.ema_alpha)
            ema = float(series[0])
            for t in range(1, idx):
                ema = alpha * float(series[t]) + (1 - alpha) * ema
            anchor = ema
        else:
            anchor = self._anchor(series, idx, self.q)
        scale = self._window_scale(
            series, idx, self.normalize_scale, self.scale_window
        )
        x = self._lag_features(
            series, idx, self.delays, anchor,
            normalize_scale=self.normalize_scale,
            scale_window=self.scale_window,
        )
        if self.weights == "softmax":
            # softmax over the k nearest neighbours: w ∝ exp(-d / sigma)
            # sigma is the global mean kNN distance fitted at train time
            dist, ind = self.model_.kneighbors(x, n_neighbors=min(self.neighbors, len(self.X_)))
            d = dist[0]
            w = np.exp(-d / max(float(self.sigma_), 1e-12))
            w = w / w.sum()
            p_std = (w @ self.Y_[ind[0]])[None, :]
        else:
            p_std = self.model_.predict(x)
        if self.affine:
            p_std = p_std * self.affine_gamma_ + self.affine_beta_
        return p_std[0] * scale + anchor


class HeuristicLagKNNRecursive(HeuristicLagKNN):
    """Recursive (1-step-ahead x H) variant of :class:`HeuristicLagKNN`.

    Fits a 1-step model; at prediction time repeatedly appends the last
    forecast to the history and re-feeds the lag features.
    """

    def fit(self, y: Iterable[float], *, horizon: int) -> "HeuristicLagKNNRecursive":
        series = self._as_series(y, min_len=max(self.q, max(self.delays)) + 2)
        self._check_horizon(horizon)
        X, Y, _ = self._lag_dataset(
            series, 1, self.delays, self.q, self.history_fraction
        )
        self.model_ = KNeighborsRegressor(
            n_neighbors=min(self.neighbors, len(X)), weights="distance"
        ).fit(X, Y)
        self.history_ = series
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        series = self.history_.copy()
        preds = np.empty(self.horizon_, dtype=float)
        for step in range(self.horizon_):
            idx = len(series)
            anchor = self._anchor(series, idx, self.q)
            x = self._lag_features(series, idx, self.delays, anchor)
            preds[step] = float(np.ravel(self.model_.predict(x))[0]) + anchor
            series = np.append(series, preds[step])
        return preds

class TemporalLagKNN(HeuristicLagKNN):
    """HeuristicLagKNN with exponential temporal decay on neighbor weights.

    Formulation "select by similarity, weight by recency": the k nearest
    origins in anchor-normalised lag space are chosen exactly as in the
    parent, but each neighbor's distance weight is multiplied by a
    recency factor before averaging:

        w_i = (1 / (d_i + eps)) * exp(-decay * age_i)
        age_i = forecast_time - origin_i   (steps, hours for hourly data)

    ``decay == 0`` recovers the parent's distance-weighted kNN.
    Weights are normalised in log space (shift by max), so large decay
    values cannot under/overflow; the weighted mean is invariant to the
    shift.
    """

    def __init__(
        self,
        q: int = 6,
        neighbors: int = 5,
        delays: tuple[int, ...] = (1, 2, 3, 6, 12, 24),
        history_fraction: float = 1.0,
        decay: float = 0.0,
    ):
        super().__init__(
            q=q,
            neighbors=neighbors,
            delays=delays,
            history_fraction=history_fraction,
        )
        self.decay = float(decay)

    def fit(self, y: Iterable[float], *, horizon: int) -> "TemporalLagKNN":
        series = self._as_series(y, min_len=max(self.q, max(self.delays)) + horizon + 2)
        self._check_horizon(horizon)
        X, Y, origins = self._lag_dataset(
            series, horizon, self.delays, self.q, self.history_fraction
        )
        self.X_ = X
        self.Y_ = Y
        self.origins_ = origins
        self.history_ = series
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        series = self.history_
        idx = len(series)
        anchor = self._anchor(series, idx, self.q)
        x = self._lag_features(series, idx, self.delays, anchor)
        dist = np.linalg.norm(self.X_ - x, axis=1)
        k = min(self.neighbors, len(dist))
        nn = np.argpartition(dist, k - 1)[:k]
        log_w = -np.log(dist[nn] + 1e-12) - self.decay * (idx - self.origins_[nn])
        w = np.exp(log_w - log_w.max())

        return (w @ self.Y_[nn]) / w.sum() + anchor


class HeuristicLagRandomForest(BaseForecaster):
    """Direct multi-output Random Forest over anchor-normalised lag features."""

    def __init__(
        self,
        q: int = 6,
        delays: tuple[int, ...] = (1, 2, 3, 6, 12, 24),
        trees: int = 100,
        history_fraction: float = 1.0,
        ema_alpha: float | None = None,
    ):
        if ema_alpha is not None and not (0 < ema_alpha <= 1):
            raise ValueError("ema_alpha must be in (0,1] or None")
        self.q = q
        self.delays = tuple(int(d) for d in delays)
        self.trees = trees
        self.history_fraction = history_fraction
        self.ema_alpha = ema_alpha

    def fit(self, y: Iterable[float], *, horizon: int) -> "HeuristicLagRandomForest":
        series = self._as_series(y, min_len=max(self.q, max(self.delays)) + horizon + 2)
        self._check_horizon(horizon)
        if self.ema_alpha is not None:
            alpha = float(self.ema_alpha)
            ema = np.empty_like(series, dtype=float)
            ema[0] = float(series[0])
            for t in range(1, len(series)):
                ema[t] = alpha * float(series[t]) + (1 - alpha) * ema[t-1]
            origins = self._origins(series, horizon, max(self.q, max(self.delays)), self.history_fraction)
            anchors = ema[origins - 1]
            X = np.column_stack([(series[origins - d] - anchors) for d in self.delays]).astype(float)
            Y = np.stack([(series[i:i+horizon] - a) for i, a in zip(origins, anchors)])
            self.ema_ = ema
        else:
            X, Y, _ = self._lag_dataset(
                series, horizon, self.delays, self.q, self.history_fraction
            )
            self.ema_ = None
        self.model_ = RandomForestRegressor(
            n_estimators=self.trees, random_state=42, n_jobs=-1
        ).fit(X, Y)
        self.history_ = series
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        series = self.history_
        idx = len(series)
        if self.ema_alpha is not None:
            alpha = float(self.ema_alpha)
            ema = float(series[0])
            for t in range(1, idx):
                ema = alpha * float(series[t]) + (1 - alpha) * ema
            anchor = ema
        else:
            anchor = self._anchor(series, idx, self.q)
        x = self._lag_features(series, idx, self.delays, anchor)
        return self.model_.predict(x)[0] + anchor


class HeuristicLagDecisionTree(HeuristicLagRandomForest):
    """Direct multi-output decision tree over the same lag features."""

    def __init__(self, q: int = 6, delays: tuple[int, ...] = (1, 2, 3, 6, 12, 24),
                 max_depth: int | None = None, history_fraction: float = 1.0, ema_alpha: float | None = None):
        if ema_alpha is not None and not (0 < ema_alpha <= 1):
            raise ValueError("ema_alpha must be in (0,1] or None")
        super().__init__(q=q, delays=delays, history_fraction=history_fraction, ema_alpha=ema_alpha)
        self.max_depth = max_depth

    def fit(self, y: Iterable[float], *, horizon: int) -> "HeuristicLagDecisionTree":
        series = self._as_series(y, min_len=max(self.q, max(self.delays)) + horizon + 2)
        self._check_horizon(horizon)
        if self.ema_alpha is not None:
            alpha = float(self.ema_alpha)
            ema = np.empty_like(series, dtype=float)
            ema[0] = float(series[0])
            for t in range(1, len(series)):
                ema[t] = alpha * float(series[t]) + (1 - alpha) * ema[t-1]
            origins = self._origins(series, horizon, max(self.q, max(self.delays)), self.history_fraction)
            anchors = ema[origins - 1]
            X = np.column_stack([(series[origins - d] - anchors) for d in self.delays]).astype(float)
            Y = np.stack([(series[i:i+horizon] - a) for i, a in zip(origins, anchors)])
            self.ema_ = ema
        else:
            X, Y, _ = self._lag_dataset(
                series, horizon, self.delays, self.q, self.history_fraction
            )
            self.ema_ = None
        self.model_ = DecisionTreeRegressor(
            max_depth=self.max_depth, random_state=42
        ).fit(X, Y)
        self.history_ = series
        self.horizon_ = int(horizon)
        self._fitted = True
        return self


# --------------------------------------------------------------------------
# Balanced-lag ensemble KNN (direct multi-output, averaged experts)
# --------------------------------------------------------------------------
class BalancedLagEnsembleKNN(BaseForecaster):
    """Ensemble of per-lag-set KNN experts; predictions are averaged.

    Each expert in ``lag_sets`` gets its own KNN trained on that set's
    anchor-normalised lag features; the forecast is the expert mean.

    Default uses full history; the sub-experiments sweep
    (sub_experiments/ensemble_sweep) found recent-50% and fast-lags
    variants score better on this split (MAE 1.76/1.81 vs 2.03, H=720).
    """

    def __init__(
        self,
        lag_sets: tuple[tuple[int, ...], ...] = LAGS,
        q: int = 6,
        neighbors: int = 8,
        history_fraction: float = 1.0,
    ):
        self.lag_sets = tuple(tuple(int(d) for d in s) for s in lag_sets)
        self.q = q
        self.neighbors = neighbors
        self.history_fraction = history_fraction

    def fit(self, y: Iterable[float], *, horizon: int) -> "BalancedLagEnsembleKNN":
        max_lag = max(d for s in self.lag_sets for d in s)
        series = self._as_series(y, min_len=max(self.q, max_lag) + horizon + 2)
        self._check_horizon(horizon)
        self.models_ = [
            (
                lags,
                KNeighborsRegressor(
                    n_neighbors=min(
                        self.neighbors,
                        len(
                            self._origins(
                                series, horizon,
                                min_lookback=max(self.q, max(lags)),
                                history_fraction=self.history_fraction,
                            )
                        ),
                    ),
                    weights="distance",
                ).fit(
                    *self._lag_dataset(
                        series, horizon, lags, self.q, self.history_fraction
                    )[:2]
                ),
            )
            for lags in self.lag_sets
        ]
        self.history_ = series
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        series = self.history_
        idx = len(series)
        anchor = self._anchor(series, idx, self.q)
        expert_preds = [
            model.predict(self._lag_features(series, idx, lags, anchor))[0] + anchor
            for lags, model in self.models_
        ]
        return np.mean(expert_preds, axis=0)
