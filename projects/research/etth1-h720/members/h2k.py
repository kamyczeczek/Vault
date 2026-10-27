"""Corrected H2K: level-relative, damped block continuation with causal scaling."""
from __future__ import annotations

from typing import Optional
import numpy as np


class H2KForecaster:
    """Three-block, drift-corrected motif KNN for long horizons.

    For each training endpoint, the query is a level-normalized recent
    window.  A neighbor's future is expressed relative to *its own* local
    level and then added to the query's local level.  The neighbor-level
    correction is learned from training data; it is not taken from the future
    query.  Forecast blocks are re-anchored to the preceding block, with a
    damped local slope to prevent a noisy final point from exploding a
    30-day extrapolation.
    """

    def __init__(
        self,
        input_length: int = 96,
        k_neighbors: int = 12,
        block_length: int = 240,
        anchor_length: int = 24,
        slope_length: int = 24,
        drift_damping: float = 0.25,
        max_drift: float = 0.0,
        residual_scale_floor: float = 1e-8,
    ) -> None:
        if input_length < 2:
            raise ValueError("input_length must be at least 2")
        if k_neighbors < 1:
            raise ValueError("k_neighbors must be positive")
        if block_length < 1:
            raise ValueError("block_length must be positive")
        if anchor_length < 1 or slope_length < 1:
            raise ValueError("anchor and slope lengths must be positive")
        if drift_damping < 0:
            raise ValueError("drift_damping must be non-negative")
        self.input_length = int(input_length)
        self.k_neighbors = int(k_neighbors)
        self.block_length = int(block_length)
        self.anchor_length = int(anchor_length)
        self.slope_length = int(slope_length)
        self.drift_damping = float(drift_damping)
        self.max_drift = float(max_drift)
        self.residual_scale_floor = float(residual_scale_floor)
        self.level_scale = 1.0
        self.confidence_floor = 0.0
        self.X_: Optional[np.ndarray] = None
        self.Y_: Optional[np.ndarray] = None
        self.level_scale_: Optional[np.ndarray] = None
        self.ends_: Optional[np.ndarray] = None
        self.horizon_: Optional[int] = None
        self.predict_level_scale_: float = 1.0
        self.predict_damping_: float = 0.0

    @staticmethod
    def _causal_mean(x: np.ndarray, window: int) -> np.ndarray:
        if window <= 1:
            return x.copy()
        c = np.cumsum(np.concatenate(([0.0], x)))
        out = np.empty_like(x, dtype=float)
        for i in range(len(x)):
            start = max(0, i - window + 1)
            out[i] = (c[i + 1] - c[start]) / (i - start + 1)
        return out

    def _represent(self, window: np.ndarray) -> tuple[np.ndarray, float, float, float]:
        x = np.asarray(window, dtype=float).ravel()
        level = float(np.mean(x[-self.anchor_length:]))
        detrended = x - level
        slope = float((x[-1] - x[max(0, len(x) - self.slope_length)]) /
                      max(1, len(x) - self.slope_length))
        if not np.isfinite(slope):
            slope = 0.0
        if self.max_drift > 0:
            slope = float(np.clip(slope, -self.max_drift, self.max_drift))
        scale = max(float(np.std(detrended)), self.residual_scale_floor)
        return (detrended / scale).astype(float), level, slope, scale

    def fit(self, train: np.ndarray, horizon: int) -> "H2KForecaster":
        series = np.asarray(train, dtype=float).ravel()
        if series.ndim != 1 or len(series) < self.input_length:
            raise ValueError("train must be a one-dimensional series")
        if horizon < 1:
            raise ValueError("horizon must be positive")
        ends = np.arange(self.input_length, len(series) - horizon + 1)
        if len(ends) == 0:
            raise ValueError("series is too short for requested horizon")
        xs, ys, scales = [], [], []
        for end in ends:
            shape, level, _, scale = self._represent(series[end - self.input_length:end])
            future = series[end:end + horizon]
            xs.append(shape)
            # Store the *deviation* from the endpoint's local level.  The
            # neighbor's own local level is applied only during retrieval.
            ys.append(future - level)
            scales.append(scale)
        self.X_ = np.stack(xs)
        self.Y_ = np.stack(ys)
        self.level_scale_ = np.asarray(scales, dtype=float)
        self.ends_ = ends.astype(int)
        self.horizon_ = int(horizon)
        # These are deliberately conservative defaults.  A development sweep
        # may freeze alternatives before touching the locked late origins.
        self.predict_level_scale_ = 1.0
        self.predict_damping_ = self.drift_damping
        return self

    def _retrieve(self, query: np.ndarray) -> np.ndarray:
        mu = np.mean(self.X_, axis=0)
        scale = np.std(self.X_, axis=0) + 1e-8
        X = (self.X_ - mu) / scale
        q = (query - mu) / scale
        d = np.sqrt(np.mean((X - q[None, :]) ** 2, axis=1))
        k = min(self.k_neighbors, len(d))
        idx = np.argpartition(d, k - 1)[:k]
        idx = idx[np.argsort(d[idx], kind="stable")]
        sigma = max(float(np.median(d[idx])), 1e-6)
        weights = np.exp(-0.5 * (d[idx] / sigma) ** 2)
        weights /= np.sum(weights) + 1e-12
        return np.sum(weights[:, None] * self.Y_[idx], axis=0)

    def _slope(self, current: np.ndarray) -> float:
        x = np.asarray(current, dtype=float).ravel()
        q = min(self.slope_length, len(x))
        if q < 2:
            return 0.0
        slope = float((x[-1] - x[-q]) / max(1, q - 1))
        if not np.isfinite(slope):
            return 0.0
        if self.max_drift > 0:
            slope = float(np.clip(slope, -self.max_drift, self.max_drift))
        return slope

    def _reliability(self, distances: np.ndarray) -> np.ndarray:
        """Smooth retrieval-quality weights in [0, 1]."""
        if len(distances) == 0:
            return np.zeros(0, dtype=float)
        med = max(float(np.median(distances)), 1e-6)
        return np.clip(np.exp(-0.5 * (distances / med) ** 2), 0.0, 1.0)

    def predict_hist(self, hist: np.ndarray) -> np.ndarray:
        if self.X_ is None or self.Y_ is None or self.horizon_ is None:
            raise RuntimeError("fit must be called before predict_hist")
        history = np.asarray(hist, dtype=float).ravel()
        if len(history) < self.input_length:
            history = np.pad(history, (self.input_length - len(history), 0), mode="edge")
        current = history.copy()
        result = []
        n_blocks = int(np.ceil(self.horizon_ / self.block_length))
        for _ in range(n_blocks):
            block_len = min(self.block_length, self.horizon_ - len(result))
            query, level, _, _ = self._represent(current[-self.input_length:])
            deviation = self._retrieve(query)
            slope = self._slope(current)
            t = np.arange(1, block_len + 1, dtype=float)
            # The retrieved deviation is a zero-level continuation.  Restore
            # the current local level, but shrink the motif toward the
            # persistence baseline when the query has no close match.
            query_mean = float(np.mean(current[-self.input_length:]))
            confidence = float(np.exp(-0.5 * (np.mean((self.X_ - query[None, :]) ** 2) /
                                              (np.mean(np.var(self.X_, axis=0)) + 1e-8))))
            block = query_mean + confidence * (deviation[:block_len] - np.mean(deviation[:block_len])) + \
                (1.0 - confidence) * np.zeros(block_len)
            block = level + (block - level) + self.drift_damping * slope * t
            result.extend(block.tolist())
            current = np.concatenate([current, block])
        return np.asarray(result[:self.horizon_], dtype=float)


def fit_h2k(train: np.ndarray, horizon: int, **kwargs) -> H2KForecaster:
    return H2KForecaster(**kwargs).fit(train, horizon)


def pred_h2k(model: H2KForecaster, hist: np.ndarray) -> np.ndarray:
    return model.predict_hist(hist)
