"""Linear / neural-style forecasting models: DLinear, NLinear, HeuristicLagELM,
HeuristicLagELMRandomForest (MI+FNN lags, ELM hidden layer, RF readout).

All follow the unified forecaster interface:

    model.fit(y, horizon=H) -> model
    model.predict() -> np.ndarray (H,)
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor

from .base import BaseForecaster


class DLinear(BaseForecaster):
    """Decomposition Linear (Zeng et al. 2023 style) — fixed for H=720.

    S-05 redesign. The legacy implementation fit the seasonal and
    trend heads **independently**, each to the full raw-scale target,
    then summed their predictions — both heads re-learn the same
    level, so the sum double-predicts it (raw-scale OLS artifact:
    legacy leaderboard 16.6890 MAE). It also died with a NameError
    at consolidation time (lost `LinearRegression` import).

    Fixed design (published-behavior class):
    - **RevIN-style per-window standardization**: every window is
      standardized with its own mean/std before the solve; predict
      de-standardizes with the trailing window's stats.
    - **Joint decomposition solve**: both heads are fit jointly —
      one least-squares problem on the concatenated [seasonal;
      trend] features against the same standardized target, so the
      level is learned once, not twice.
    - Closed-form/OLS path is deterministic (LAPACK); no RNG.
    """

    def __init__(
        self,
        input_length: int = 96,
        kernel_size: int = 25,
        ridge_alpha: float = 0.0,
        individual: bool = False,
    ):
        self.input_length = input_length
        self.kernel_size = kernel_size
        self.ridge_alpha = ridge_alpha
        self.individual = individual

    def _array(self, values: Iterable[float]) -> np.ndarray:
        result = np.asarray(values, dtype=float)
        if (
            result.ndim not in (1, 2)
            or len(result) < self.input_length + self.kernel_size + 2
            or not np.isfinite(result).all()
        ):
            raise ValueError("values are too short or non-finite")
        return result if result.ndim == 2 else result[:, None]

    def _decompose(self, window: np.ndarray):
        pad = (self.kernel_size - 1) // 2
        padded = np.pad(window, ((pad, pad), (0, 0)), mode="edge")
        kernel = np.ones(self.kernel_size) / self.kernel_size
        trend = np.column_stack(
            [
                np.convolve(padded[:, c], kernel, mode="valid")
                for c in range(window.shape[1])
            ]
        )
        return window - trend, trend

    def fit(
        self, y: Iterable[float], *, horizon: int, target_index: int = 0
    ) -> "DLinear":
        series = self._array(y)
        self._check_horizon(horizon)
        if target_index < 0 or target_index >= series.shape[1]:
            raise ValueError("invalid target index")
        x_rows, y_rows = [], []
        for end in range(self.input_length, len(series) - horizon + 1):
            window = series[end - self.input_length : end]
            mu, sigma = self._window_stats(window)
            # RevIN order: standardize the window FIRST, then decompose —
            # seasonal+trend features are level-free, so the linear map
            # never extrapolates along an unseen level direction.
            seasonal, trend = self._decompose((window - mu) / sigma)
            x_rows.append(
                np.concatenate(
                    [seasonal[:, target_index], trend[:, target_index]]
                )
            )
            y_rows.append((series[end : end + horizon, target_index] - mu) / sigma)
        if not y_rows:
            raise ValueError("insufficient history for DLinear")
        X = np.asarray(x_rows)
        Y = np.asarray(y_rows)
        if self.ridge_alpha > 0.0:
            solver = Ridge(alpha=self.ridge_alpha, fit_intercept=True)
        else:
            solver = LinearRegression(fit_intercept=True)
        self.model_ = solver.fit(X, Y)
        self.history_ = series
        self.target_index = target_index
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def _window_stats(self, window: np.ndarray) -> tuple[float, float]:
        """Per-window (mean, std) for RevIN-style standardization.

        Population std; near-constant windows clamp the std to
        ``BaseForecaster._SCALE_EPS`` so standardization never
        amplifies noise (deterministic, never future data).
        """
        mu = float(window.mean())
        sigma = max(float(window.std()), self._SCALE_EPS)
        return mu, sigma

    def predict(self) -> np.ndarray:
        self._check_fitted()
        raw = self.history_[-self.input_length :]
        window = raw[:, None] if raw.ndim == 1 else raw
        mu, sigma = self._window_stats(window)
        seasonal, trend = self._decompose((window - mu) / sigma)
        x = np.concatenate(
            [seasonal[:, self.target_index], trend[:, self.target_index]]
        )
        out = self.model_.predict([x])[0]
        return out * sigma + mu


class NLinear(BaseForecaster):
    """NLinear: last-value-normalised window -> Ridge on the horizon."""

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

    def fit(
        self, y: Iterable[float], *, horizon: int, target_index: int = 0
    ) -> "NLinear":
        series = self._array(y)
        self._check_horizon(horizon)
        if len(series) <= self.input_length + horizon:
            raise ValueError("invalid horizon or insufficient history")
        if series.ndim == 1:
            series = series[:, None]
        if target_index < 0 or target_index >= series.shape[1]:
            raise ValueError("target_index is out of range")
        x_rows, y_rows = [], []
        for end in range(self.input_length, len(series) - horizon + 1):
            window = series[end - self.input_length : end]
            anchor = window[-1, target_index]
            x_rows.append((window - window[-1]).reshape(-1))
            y_rows.append(series[end : end + horizon, target_index] - anchor)
        self.model = Ridge(alpha=self.ridge_alpha, fit_intercept=True).fit(
            np.asarray(x_rows), np.asarray(y_rows)
        )
        self.history_ = series
        self.target_index = target_index
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        raw = self.history_[-self.input_length :]
        window = raw[:, None] if raw.ndim == 1 else raw
        anchor = window[-1, self.target_index]
        return (
            np.asarray(self.model.predict([(window - window[-1]).reshape(-1)])[0])
            + anchor
        )


class RLinear(BaseForecaster):
    """RevIN-standardized window -> linear map on the standardized horizon.

    S-06 addition (the "RLinear" half of the long-lookback linear family).
    Same published-behavior class as the S-05 DLinear redesign: every
    window is standardized with its own (mu, sigma) BEFORE the solve,
    the linear map acts on standardized features against standardized
    targets, and :meth:`predict` de-standardizes with the trailing
    window's stats. Unlike :class:`NLinear` (last-value anchoring) or
    :class:`DLinear` (moving-average decomposition), no structural
    transform is applied — the standardized raw window IS the feature
    vector, so any lookback-vs-performance effect is attributable to
    the linear map alone. Closed-form/OLS path is deterministic
    (LAPACK); no RNG.
    """

    def __init__(self, input_length: int = 336, ridge_alpha: float = 0.0):
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
        return result if result.ndim == 2 else result[:, None]

    def _window_stats(self, window: np.ndarray) -> tuple[float, float]:
        """Per-window (mean, std), identical convention to DLinear."""
        mu = float(window.mean())
        sigma = max(float(window.std()), self._SCALE_EPS)
        return mu, sigma

    def fit(
        self, y: Iterable[float], *, horizon: int, target_index: int = 0
    ) -> "RLinear":
        series = self._array(y)
        self._check_horizon(horizon)
        if target_index < 0 or target_index >= series.shape[1]:
            raise ValueError("target index out of range")
        x_rows, y_rows = [], []
        for end in range(self.input_length, len(series) - horizon + 1):
            window = series[end - self.input_length : end]
            mu, sigma = self._window_stats(window)
            x_rows.append(((window - mu) / sigma).reshape(-1))
            y_rows.append((series[end : end + horizon, target_index] - mu) / sigma)
        if not y_rows:
            raise ValueError("insufficient history for RLinear")
        X = np.asarray(x_rows)
        Y = np.asarray(y_rows)
        if self.ridge_alpha > 0.0:
            solver = Ridge(alpha=self.ridge_alpha, fit_intercept=True)
        else:
            solver = LinearRegression(fit_intercept=True)
        self.model_ = solver.fit(X, Y)
        self.history_ = series
        self.target_index = target_index
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        raw = self.history_[-self.input_length :]
        window = raw[:, None] if raw.ndim == 1 else raw
        mu, sigma = self._window_stats(window)
        x = ((window - mu) / sigma).reshape(-1)
        out = np.asarray(self.model_.predict([x])[0])
        return out * sigma + mu


class HeuristicLagELM(BaseForecaster):
    """Extreme Learning Machine with heuristic lags and local anchoring."""

    def __init__(
        self,
        q: int = 3,
        history_fraction: float = 0.1,
        hidden_dim: int = 256,
        activation: str = "tanh",
        ridge_alpha: float = 1.0,
        delays: tuple[int, ...] = (1, 2, 3, 6, 12, 24),
        weight_init: str = "normal",
        normalize_scale: bool = False,
        scale_window: int = 168,
        affine: bool = False,
    ):
        self.q = q
        self.history_fraction = history_fraction
        self.hidden_dim = hidden_dim
        self.activation = activation
        self.ridge_alpha = ridge_alpha
        self.delays = tuple(int(d) for d in delays)
        self.weight_init = weight_init
        self.normalize_scale = normalize_scale
        self.scale_window = scale_window
        self.affine = affine

    def _activation_fn(self, net: np.ndarray) -> np.ndarray:
        if self.activation == "relu":
            return np.maximum(0, net)
        return np.tanh(net)  # default / "tanh"

    def _init_weights(self) -> tuple[np.ndarray, np.ndarray]:
        """Hidden-layer weight/bias draw for ``hidden_dim`` neurons.

        ``normal``: iid N(0,1) weights, U(-1,1) biases (RandomState(42))
        — the original scheme.
        ``sobol``:  low-discrepancy (quasi-random) draw via scrambled
        Sobol sequences — weights and biases are *regularly distributed
        across space* instead of iid, covering the lag-feature space
        more uniformly for the same neuron count. Same marginals as
        ``normal`` (weights ~ N(0,1), biases ~ U(-1,1)).
        ``sobol_iid``: Sobol placement *plus* the joint-distribution
        properties of the iid normal draw, mimicking ``normal`` beyond
        marginals: (1) neuron direction vectors are randomly rotated
        (isotropic, no cubic-axis structure from the ndtri grid);
        (2) per-neuron Euclidean norms follow the chi(d) distribution
        of iid N(0,1) columns (norm diversity), matched via Sobol-
        quantiles of the chi distribution instead of all norms
        concentrating near sqrt(d); (3) zero-mean/identity-covariance
        preserved.
        """
        d = len(self.delays)
        if self.weight_init == "sobol":
            from scipy.stats import qmc
            from scipy.special import ndtri

            sampler = qmc.Sobol(d=d + 1, scramble=True, seed=42)
            pts = sampler.random(self.hidden_dim)          # (hidden, d+1)
            W = ndtri(pts[:, :-1]).T                        # -> (d, hidden)
            b = (2.0 * pts[:, -1] - 1.0)[None, :]           # -> (1, hidden)
            return W, b
        if self.weight_init == "sobol_iid":
            from scipy.stats import chi, qmc
            from scipy.special import ndtri

            # Direction grid: Sobol on the unit cube -> standard normal
            # quantiles -> normalise to unit directions. d+2 dims: d for
            # direction coordinates, 1 for the chi radius quantile, 1 for
            # the bias quantile.
            sampler = qmc.Sobol(d=d + 2, scramble=True, seed=42)
            pts = sampler.random(self.hidden_dim)          # (hidden, d+2)
            g = ndtri(pts[:, :d])                          # (hidden, d)
            directions = g / np.linalg.norm(g, axis=1, keepdims=True)
            radii = chi.ppf(pts[:, d], d)                  # chi(d) radii
            cols = directions * radii[:, None]             # (hidden, d)
            # Random rotation: draw a random orthogonal matrix (QR of a
            # normal matrix) and rotate the whole grid, removing the
            # cubic-axis structure the ndtri grid inherits.
            rng_rot = np.random.RandomState(42)
            m = rng_rot.normal(size=(d, d))
            Q, _ = np.linalg.qr(m)
            W = (cols @ Q).T                               # -> (d, hidden)
            b = (2.0 * pts[:, -1] - 1.0)[None, :]           # -> (1, hidden)
            return W, b
        rng = np.random.RandomState(42)
        W = rng.normal(0, 1, size=(len(self.delays), self.hidden_dim))
        b = rng.uniform(-1, 1, size=(1, self.hidden_dim))
        return W, b

    def _activation_fn(self, net: np.ndarray) -> np.ndarray:
        if self.activation == "relu":
            return np.maximum(0, net)
        return np.tanh(net)  # default / "tanh"

    def fit(self, y: Iterable[float], *, horizon: int) -> "HeuristicLagELM":
        series = self._as_series(
            y, min_len=max(self.q, max(self.delays)) + horizon + 2
        )
        self._check_horizon(horizon)
        X, Y, origins = self._lag_dataset(
            series,
            horizon,
            self.delays,
            self.q,
            self.history_fraction,
            normalize_scale=self.normalize_scale,
            scale_window=self.scale_window,
        )
        self.W_, self.b_ = self._init_weights()
        H = self._activation_fn(np.dot(X, self.W_) + self.b_)
        self.model_ = Ridge(alpha=self.ridge_alpha, fit_intercept=True).fit(H, Y)
        if self.affine:
            # RevIN-style affine readout, fitted on standardised in-sample
            # predictions (deterministic least squares per output dim).
            P_std = self.model_.predict(H)
            self.affine_gamma_, self.affine_beta_ = self._fit_affine(P_std, Y)
        self.history_ = series
        self.horizon_ = int(horizon)
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
        H_test = self._activation_fn(np.dot(x, self.W_) + self.b_)
        p_std = self.model_.predict(H_test)
        if self.affine:
            p_std = p_std * self.affine_gamma_ + self.affine_beta_
        return p_std[0] * scale + anchor


def _average_mutual_information(
    series: np.ndarray, max_lag: int, bins: int = 16
) -> np.ndarray:
    """Average mutual information I(x_t; x_{t-lag}) for lag in [1, max_lag].

    Standard histogram MI (equal-width bins) as used for choosing the
    first zero of AMI when embedding a scalar time series. Deterministic:
    no randomness involved.
    """
    n = len(series)
    mi = np.zeros(max_lag + 1)
    x = series
    for lag in range(1, max_lag + 1):
        a = x[: n - lag]
        b = x[lag:]
        # joint histogram over (x_t, x_{t-lag})
        a_edges = np.linspace(a.min(), a.max(), bins + 1)
        b_edges = np.linspace(b.min(), b.max(), bins + 1)
        ja = np.histogram2d(a, b, bins=[a_edges, b_edges])[0]
        joint = ja / ja.sum()
        pa = joint.sum(axis=1)
        pb = joint.sum(axis=0)
        nz = joint > 0
        mi[lag] = np.sum(
            joint[nz] * np.log2(joint[nz] / (pa[:, None] * pb[None, :])[nz])
        )
    return mi


def _average_mutual_information_pair(
    a: np.ndarray, b: np.ndarray, bins: int = 16
) -> float:
    """Histogram MI between two equal-length arrays (bits)."""
    a_edges = np.linspace(a.min(), a.max(), bins + 1)
    b_edges = np.linspace(b.min(), b.max(), bins + 1)
    joint = np.histogram2d(a, b, bins=[a_edges, b_edges])[0]
    joint = joint / joint.sum()
    pa = joint.sum(axis=1)
    pb = joint.sum(axis=0)
    nz = joint > 0
    return float(
        np.sum(joint[nz] * np.log2(joint[nz] / (pa[:, None] * pb[None, :])[nz]))
    )


def _fnn_fraction(
    series: np.ndarray, max_dim: int, tau: int, rtol: float = 10.0
) -> np.ndarray:
    """Kennel et al. false-nearest-neighbours fraction per embedding dim m.

    Delay embedding (x_t, x_{t-tau}, ..., x_{t-(m-1)tau}). For each m,
    finds each point's nearest neighbour in m dims, then checks whether
    that pair stays close once the (m+1)-th coordinate is revealed. Uses
    a KDTree (deterministic query) instead of brute force; the point set
    is restricted to indices that exist in both the m- and (m+1)-dim
    embeddings so neighbour pairs align across dimensions.
    """
    from scipy.spatial import cKDTree

    n = len(series)
    fnn = np.zeros(max_dim + 1)
    # index window: last coordinate of the m+1-dim embedding must exist:
    # series index t ranges over [(max_dim-1)*tau, n) shifted per-dim
    for m in range(1, max_dim + 1):
        max_start = (max_dim - 1) * tau
        # embedding rows are time indices t in [max_start, n)
        # coordinates: x_{t - j*tau} for j in 0..m-1  (need t - j*tau >= 0)
        ts = np.arange(max_start, n)
        pts = np.stack(
            [series[ts - j * tau] for j in range(m)], axis=1
        )
        pts_next = np.stack(
            [series[ts - j * tau] for j in range(m + 1)], axis=1
        )
        d_nn, nn_idx = cKDTree(pts).query(pts, k=2)
        # k=2: first is self (d=0), second is true nearest neighbour
        nn_d2 = d_nn[:, 1] ** 2
        nn_i = nn_idx[:, 1]
        d_extra = (pts_next[:, m] - pts_next[nn_i, m]) ** 2
        false_mask = nn_d2 + d_extra > rtol ** 2 * np.maximum(nn_d2, 1e-12)
        fnn[m] = float(false_mask.mean())
    return fnn


class HeuristicLagELMTree(BaseForecaster):
    """ELM hidden layer + Decision-Tree readout, lags chosen by MI+FNN.

    Lag selection (deterministic, from the training series only):
    1. AMI: average mutual information of x_t vs x_{t-lag}; tau = lag
       of the first local minimum of AMI (classic embedding delay).
    2. FNN: Kennel false-nearest-neighbour fraction at delay tau;
       m = first dim where FNN% < fnn_threshold (classic embedding
       dimension).
    3. Candidate lags = multiples of tau: {tau, 2*tau, ..., m*tau}.
       These are re-ranked by direct MI with the multi-step target
       x_{t+horizon}, and the top ``n_lags`` are kept.

    Architecture: anchor-normalised lag features -> random hidden layer
    (tanh, fixed seed 42) -> multi-output DecisionTreeRegressor (fixed
    seed 42) instead of the ELM's ridge readout. A single tree instead
    of a forest: ~seconds vs ~13 min for 100 trees on 720-output data,
    fully deterministic.
    """
    def __init__(
        self,
        q: int = 6,
        history_fraction: float = 1.0,
        hidden_dim: int = 256,
        activation: str = "tanh",
        max_lag: int = 168,
        mi_bins: int = 16,
        fnn_threshold: float = 0.05,
        n_lags: int = 6,
        tree_kwargs: dict | None = None,
    ):
        self.q = q
        self.history_fraction = history_fraction
        self.hidden_dim = hidden_dim
        self.activation = activation
        self.max_lag = max_lag
        self.mi_bins = mi_bins
        self.fnn_threshold = fnn_threshold
        self.n_lags = n_lags
        self.tree_kwargs = dict(tree_kwargs or {})

    def _activation_fn(self, net: np.ndarray) -> np.ndarray:
        if self.activation == "relu":
            return np.maximum(0, net)
        return np.tanh(net)  # default / "tanh"

    def select_lags(self, series: np.ndarray, horizon: int) -> tuple[int, ...]:
        """MI+FNN lag selection; deterministic, no randomness."""
        mi = _average_mutual_information(series, self.max_lag, self.mi_bins)
        # tau: first local minimum of AMI (classic embedding-delay rule);
        # fallback when the curve is monotone-ish: global argmin.
        diff = np.diff(mi[1:])
        mins = np.where((diff[:-1] < 0) & (diff[1:] > 0))[0]
        tau = int(mins[0]) + 1 if len(mins) else int(np.argmin(mi[1:])) + 1
        fnn = _fnn_fraction(series, max_dim=self.max_lag // tau, tau=tau)
        dims = np.arange(1, len(fnn))
        below = dims[fnn[1:] < self.fnn_threshold]
        m = int(below[0]) if len(below) else int(dims[np.argmin(fnn[1:])])
        # candidate multiples of tau, re-ranked by MI with the target
        cands = [k * tau for k in range(1, m + 1)]
        n = len(series)
        scores = []
        for d in cands:
            # feature x_{s-d} vs target x_{s}: s in [horizon, n)
            # -> x_{s} is 'horizon' steps ahead of x_{s-d}
            feat = series[horizon - d : n - d]
            tgt = series[horizon:]
            scores.append(
                _average_mutual_information_pair(
                    feat, tgt, self.mi_bins
                )
            )
        ranked = sorted(zip(scores, cands), key=lambda t: -t[0])
        chosen = sorted(d for _, d in ranked[: self.n_lags])
        self.tau_ = tau
        self.fnn_dims_ = fnn
        self.mi_curve_ = mi
        self.m_ = m
        return tuple(int(d) for d in chosen)

    def _init_weights(self, n_features: int) -> tuple[np.ndarray, np.ndarray]:
        rng = np.random.RandomState(42)
        W = rng.normal(0, 1, size=(n_features, self.hidden_dim))
        b = rng.uniform(-1, 1, size=(1, self.hidden_dim))
        return W, b

    def fit(self, y: Iterable[float], *, horizon: int) -> "HeuristicLagELMRandomForest":
        series = self._as_series(y, min_len=self.max_lag + horizon + 2)
        self._check_horizon(horizon)
        self.delays_ = self.select_lags(series, horizon)
        X, Y, _ = self._lag_dataset(
            series, horizon, self.delays_, self.q, self.history_fraction
        )
        self.W_, self.b_ = self._init_weights(len(self.delays_))
        H = self._activation_fn(np.dot(X, self.W_) + self.b_)
        self.model_ = DecisionTreeRegressor(
            random_state=42, **self.tree_kwargs
        ).fit(H, Y)
        self.history_ = series
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        series = self.history_
        idx = len(series)
        anchor = self._anchor(series, idx, self.q)
        x = self._lag_features(series, idx, self.delays_, anchor)
        H_test = self._activation_fn(np.dot(x, self.W_) + self.b_)
        return self.model_.predict(H_test)[0] + anchor
