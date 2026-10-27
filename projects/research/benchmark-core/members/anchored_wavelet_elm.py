"""Anchored wavelet random-feature forecaster.

This module deliberately keeps the small, dependency-light ELM used by the
early experiments, but exposes the same ``fit(series, horizon)`` /
``predict_hist(history)`` contract as the other members.  The original
implementation accepted a pre-windowed matrix and had no public fitting
wrappers, which made it silently unavailable to the benchmark and sunspot
registry.  The implementation below is deterministic and direct
(multi-horizon), while retaining a compatibility path for matrix callers.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

try:  # PyWavelets is optional; moving averages remain a useful fallback.
    import pywt
except Exception:  # pragma: no cover - exercised on minimal installs
    pywt = None


def _ridge_multioutput(x: np.ndarray, y: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    """Solve a deterministic, regularised multi-output ridge system."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim != 2 or y.ndim != 2 or len(x) != len(y):
        raise ValueError("x and y must be 2-D arrays with the same number of rows")
    d = x.shape[1]
    gram = x.T @ x + float(alpha) * np.eye(d)
    cross = x.T @ y
    try:
        chol = np.linalg.cholesky(gram)
        return np.linalg.solve(chol.T, np.linalg.solve(chol, cross))
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(gram, cross, rcond=None)[0]


def _causal_ma(x: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return x.copy()
    cumulative = np.cumsum(np.concatenate(([0.0], x)))
    out = np.empty_like(x)
    for i in range(len(x)):
        start = max(0, i - window + 1)
        out[i] = (cumulative[i + 1] - cumulative[start]) / (i - start + 1)
    return out


def _resample(values: np.ndarray, length: int) -> np.ndarray:
    values = np.asarray(values, dtype=float).ravel()
    if len(values) == length:
        return values
    if len(values) == 1:
        return np.repeat(values, length)
    old = np.linspace(0.0, 1.0, len(values))
    new = np.linspace(0.0, 1.0, length)
    return np.interp(new, old, values)


class AnchoredWaveletELM:
    """Direct anchored ELM with wavelet approximation and random features.

    Parameters use both the historical ``hidden_dim`` spelling and the
    ``hidden`` spelling used by the benchmark.  ``fit`` accepts a univariate
    training series and an integer horizon.  For backwards compatibility it
    also accepts ``X`` and ``Y`` matrices; in that case the stored matrix can
    be queried with ``predict(X)``.
    """

    def __init__(
        self,
        hidden_dim: int = 64,
        alpha: float = 1.0,
        *,
        hidden: Optional[int] = None,
        input_length: int = 96,
        wavelet: str = "db4",
        levels: int = 1,
        seed: int = 42,
    ) -> None:
        if hidden is not None:
            hidden_dim = hidden
        if int(hidden_dim) < 1:
            raise ValueError("hidden_dim must be positive")
        if int(input_length) < 2:
            raise ValueError("input_length must be at least 2")
        if int(levels) < 1:
            raise ValueError("levels must be positive")
        self.hidden_dim = int(hidden_dim)
        self.hidden = self.hidden_dim
        self.alpha = float(alpha)
        self.input_length = int(input_length)
        self.wavelet = str(wavelet)
        self.levels = int(levels)
        self.seed = int(seed)

        self.mu_: Optional[np.ndarray] = None
        self.sd_: Optional[np.ndarray] = None
        self.W_: Optional[np.ndarray] = None
        self.wr_: Optional[np.ndarray] = None
        self.br_: Optional[np.ndarray] = None
        self.horizon_: Optional[int] = None
        self.history_: Optional[np.ndarray] = None
        self._matrix_mode = False
        self._input_width: Optional[int] = None

    def _features(self, window: np.ndarray) -> np.ndarray:
        """Build anchored causal wavelet/random-feature representation."""
        x = np.asarray(window, dtype=float).ravel()
        if len(x) < 2 or not np.isfinite(x).all():
            raise ValueError("window must contain at least two finite values")
        length = len(x)
        anchor = float(x[-1])
        xa = x - anchor
        # Identity, local trend, and high-pass components are stable for odd
        # and even window lengths (unlike an un-padded SWT call).
        features = [xa, _causal_ma(xa, min(3, length)), _causal_ma(xa, min(9, length))]
        if pywt is not None:
            try:
                level = min(self.levels, pywt.dwt_max_level(length, self.wavelet))
                if level >= 1:
                    coeff = pywt.wavedec(xa, self.wavelet, mode="symmetric", level=level)
                    # Keep the approximation at each level.  Detail bands are
                    # intentionally excluded: they are highly unstable on
                    # short chaotic histories.
                    for approx in coeff[:level]:
                        features.append(_resample(approx, length))
            except Exception:
                pass
        return np.concatenate(features)

    def _phi(self, features: np.ndarray) -> np.ndarray:
        if self.wr_ is None or self.br_ is None:
            raise RuntimeError("model is not fitted")
        features = np.asarray(features, dtype=float).ravel()
        if len(features) != self.wr_.shape[0]:
            raise ValueError("feature width does not match the fitted model")
        return np.concatenate([features, np.cos(features @ self.wr_ + self.br_)])

    def _fit_windows(self, series: np.ndarray, horizon: int) -> None:
        series = np.asarray(series, dtype=float).ravel()
        if not np.isfinite(series).all():
            raise ValueError("series must contain only finite values")
        L = min(self.input_length, len(series) - horizon)
        if L < 2 or len(series) - horizon - L < 1:
            raise ValueError("series is too short for the requested context/horizon")
        ends = np.arange(L, len(series) - horizon + 1)
        raw = np.stack([self._features(series[e - L : e]) for e in ends])
        targets = np.stack([series[e : e + horizon] - float(series[e - 1]) for e in ends])
        self.mu_ = raw.mean(axis=0)
        self.sd_ = raw.std(axis=0)
        self.sd_[self.sd_ < 1e-8] = 1.0
        x_std = (raw - self.mu_) / self.sd_
        rng = np.random.default_rng(self.seed)
        self.wr_ = rng.normal(0.0, 1.0 / np.sqrt(x_std.shape[1]), (x_std.shape[1], self.hidden_dim))
        self.br_ = rng.uniform(0.0, 2.0 * np.pi, self.hidden_dim)
        phi = np.concatenate([x_std, np.cos(x_std @ self.wr_ + self.br_)], axis=1)
        self.W_ = _ridge_multioutput(phi, targets, self.alpha)
        self.horizon_ = int(horizon)
        self._input_width = L

    def fit(self, series: np.ndarray, horizon: Optional[int] = None):
        """Fit on a univariate series, or on legacy ``X, Y`` matrices."""
        if horizon is not None and not np.isscalar(horizon):
            y = np.asarray(horizon, dtype=float)
            x = np.asarray(series, dtype=float)
            if x.ndim != 2 or y.ndim != 2 or len(x) != len(y):
                raise ValueError("legacy fit expects X (N,L) and Y (N,H)")
            raw = np.stack([self._features(row) for row in x])
            self.mu_ = raw.mean(axis=0)
            self.sd_ = raw.std(axis=0)
            self.sd_[self.sd_ < 1e-8] = 1.0
            x_std = (raw - self.mu_) / self.sd_
            rng = np.random.default_rng(self.seed)
            self.wr_ = rng.normal(0.0, 1.0 / np.sqrt(x_std.shape[1]), (x_std.shape[1], self.hidden_dim))
            self.br_ = rng.uniform(0.0, 2.0 * np.pi, self.hidden_dim)
            phi = np.concatenate([x_std, np.cos(x_std @ self.wr_ + self.br_)], axis=1)
            self.W_ = _ridge_multioutput(phi, y - x[:, -1:], self.alpha)
            self.horizon_ = y.shape[1]
            self._input_width = x.shape[1]
            self._matrix_mode = True
            return self
        if horizon is None:
            raise ValueError("horizon is required when fitting a series")
        self._matrix_mode = False
        self._fit_windows(np.asarray(series, dtype=float), int(horizon))
        self.history_ = np.asarray(series, dtype=float).ravel().copy()
        return self

    def predict_hist(self, history: np.ndarray) -> np.ndarray:
        """Predict exactly the fitted horizon from a causal history."""
        if self.W_ is None or self.mu_ is None or self.sd_ is None:
            raise RuntimeError("fit must be called before prediction")
        h = np.asarray(history, dtype=float).ravel()
        if len(h) < 2:
            h = np.pad(h, (0, 2 - len(h)), mode="edge")
        width = self._input_width or self.input_length
        if len(h) < width:
            h = np.pad(h, (width - len(h), 0), mode="edge")
        h = h[-width:]
        raw = self._features(h)
        x = (raw - self.mu_) / self.sd_
        phi = np.concatenate([x[None, :], np.cos(x[None, :] @ self.wr_ + self.br_)], axis=1)
        return (phi @ self.W_).ravel()

    def predict(self, history: Optional[np.ndarray] = None):
        """Predict a history, a batch of histories, or use ``history_``."""
        if history is None:
            if self.history_ is None:
                raise RuntimeError("no history was supplied and fit received no series")
            history = self.history_[-self.input_length :]
        values = np.asarray(history, dtype=float)
        if values.ndim == 1:
            return self.predict_hist(values)
        if values.ndim != 2:
            raise ValueError("history must be one- or two-dimensional")
        return np.stack([self.predict_hist(row) for row in values], axis=0)


def fit_anchored_wavelet_elm(series: np.ndarray, horizon: int) -> AnchoredWaveletELM:
    return AnchoredWaveletELM(input_length=96, hidden=96, levels=1, seed=42).fit(series, horizon)


def pred_anchored_wavelet_elm(model: AnchoredWaveletELM, history: np.ndarray) -> np.ndarray:
    return model.predict_hist(history)
