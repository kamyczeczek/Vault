"""Explicit Phase 1b baselines: Seasonal Naive, NLinear, DLinear.

PROTOCOL.md §14 (Faza 1b) requires the three reference baselines to exist as
unambiguous, paper-faithful implementations. `bench.fit_nlinear` is the legacy
H720-suite learner (fixed L=96, alpha tuned for that suite, MAE objective) and
`members.sota_baselines.DLinearBaseline` is a moving-average/ridge variant
written for a different benchmark; neither is a clean reference. This module
defines them from the papers and nothing else.

References
----------
- Seasonal Naive: ŷ_{T+h} = y_{T+h-m}, m = the task's own seasonality. For h > m
  the recursion uses the already-produced forecasts, which is what makes it a
  forecast rather than a peek.
- NLinear (Zeng et al., "A Time Series is Worth 64 Words: Long-term Forecasting
  with Transformers", ICLR 2023, §4.2 / Table 8): a single linear map applied to
  an *instance-normalised* input window.
      x' = x - x[-1]        (subtract the last observed value of the window)
      ŷ' = x' W + b
      ŷ  = ŷ' + x[-1]       (add it back)
- DLinear (same paper, §4.1): decompose the input window into trend and seasonal
  parts with a moving average of kernel size 25, push each part through its own
  linear map, and add the two forecasts:
      x_trend  = MovingAvg(x, 25)
      x_season = x - x_trend
      ŷ = W_trend x_trend + W_season x_season

Fitting
-------
The papers train the linear layers by gradient descent. Gradient descent needs a
seed, an epoch budget and an optimiser state, none of which are part of the
definition, and Phase 1b needs bit-reproducible numbers. Both linear layers are
therefore estimated in closed form: ridge regression (Tikhonov, alpha=1e-3) on
sliding (input window -> next H observations) pairs drawn only from the history
available before the origin. This is the same estimator family, yields the exact
least-squares optimum for alpha -> 0, and removes every random number from the
run. The estimate is a property of the data plus (lookback, alpha, kernel), all
of which are recorded in the output artifact.

Everything here is single-channel: one call fits and forecasts one series. That
matches the papers' channel-independent setting and keeps the cost of a task with
1,115 items linear in the item count.
"""
from __future__ import annotations

import numpy as np


class InsufficientHistoryError(RuntimeError):
    """Raised when the history is too short to form a single training window."""


MIN_TRAIN_WINDOWS = 1
DEFAULT_LOOKBACK = 96
DEFAULT_KERNEL = 25
DEFAULT_ALPHA = 1e-3


def clean_history(hist: np.ndarray) -> np.ndarray:
    """Return a finite float copy of `hist` with NaNs interpolated.

    fev tasks contain series with holes (uci_air_quality, jena_weather). A NaN
    in the input window would poison every model equally, so the holes are
    filled here, once, and the count is reported by the caller.
    """
    arr = np.asarray(hist, dtype=float).ravel()
    n_nan = int(np.isnan(arr).sum())
    if n_nan:
        idx = np.arange(arr.size)
        good = ~np.isnan(arr)
        if good.sum() == 0:
            raise InsufficientHistoryError("history is entirely NaN")
        arr = np.interp(idx, idx[good], arr[good])
    return arr


def _ridge(X: np.ndarray, Y: np.ndarray, alpha: float) -> np.ndarray:
    """Closed-form ridge: argmin ||XW - Y||² + α||W||². Deterministic, no seed.

    Solved through the augmented least-squares form
    ``lstsq([[X], [sqrt(α) I]], [[Y], [0]])`` rather than by inverting XᵀX.
    Design matrices here are deliberately near-collinear (all lag columns of a
    trending series), so the normal equations are badly conditioned; lstsq
    returns the minimum-norm solution of that system, which is the ridge
    optimum, without amplifying round-off.
    """
    n_features = X.shape[1]
    X_aug = np.vstack([X, np.sqrt(alpha) * np.eye(n_features)])
    Y_aug = np.vstack([Y, np.zeros((n_features, Y.shape[1]))])
    W, *_ = np.linalg.lstsq(X_aug, Y_aug, rcond=None)
    return W


def _moving_average(x: np.ndarray, kernel_size: int) -> np.ndarray:
    """DLinear's decomposition filter.

    Mirrors the official implementation: replicate-pad the ends by
    ((k-1)//2, k//2) and average k consecutive values, so the output has the
    same length as the input and no padding artefact is divided by k.
    """
    k = int(kernel_size)
    if k <= 1:
        return x.copy()
    if k % 2 == 0:
        k += 1
    front = np.repeat(x[:1], (k - 1) // 2)
    end = np.repeat(x[-1:], k // 2)
    padded = np.concatenate([front, x, end])
    kernel = np.ones(k, dtype=float) / k
    return np.convolve(padded, kernel, mode="valid")


def _training_pairs(hist: np.ndarray, H: int, lookback: int):
    """Sliding (window, next-H) pairs built strictly from `hist`."""
    n = hist.size
    L = int(lookback)
    if n - H < MIN_TRAIN_WINDOWS + 1:
        raise InsufficientHistoryError(
            f"history length {n} cannot supply a {H}-step target")
    L = max(2, min(L, n - H))
    ends = range(L, n - H + 1)
    windows = np.stack([hist[e - L:e] for e in ends])
    futures = np.stack([hist[e:e + H] for e in ends])
    return windows, futures, L


class SeasonalNaive:
    """ŷ_{T+h} = y_{T+h-m}, recursing into its own forecasts past h = m."""

    name = "SeasonalNaive"

    def __init__(self) -> None:
        self.seasonality = None

    def fit(self, hist: np.ndarray, H: int, seasonality: int) -> "SeasonalNaive":
        if hist.size == 0:
            raise InsufficientHistoryError("empty history")
        self.seasonality = max(1, int(seasonality))
        self._H = int(H)
        self._last_m = np.asarray(hist[-self.seasonality:], dtype=float)
        return self

    def predict(self) -> np.ndarray:
        m = self.seasonality
        hist_tail = list(self._last_m)
        ext = hist_tail + [hist_tail[-1]] * max(0, m - len(hist_tail))
        out = []
        for _ in range(self._H):
            out.append(ext[-m])
            ext.append(ext[-m])
        return np.asarray(out, dtype=float)

    def fit_predict(self, hist: np.ndarray, H: int, seasonality: int) -> np.ndarray:
        self.fit(hist, H, seasonality)
        return self.predict()


class NLinear:
    """Instance-normalised single linear layer (Zeng et al. 2023, §4.2)."""

    name = "NLinear"

    def __init__(self, lookback: int = DEFAULT_LOOKBACK, alpha: float = DEFAULT_ALPHA) -> None:
        self.lookback = int(lookback)
        self.alpha = float(alpha)
        self.W: np.ndarray | None = None
        self.L_used: int | None = None
        self.n_train_windows: int = 0

    def fit_predict(self, hist: np.ndarray, H: int, seasonality: int | None = None) -> np.ndarray:
        windows, futures, L = _training_pairs(hist, H, self.lookback)
        base = windows[:, -1:]                      # instance-normalisation anchor
        X = windows - base
        Y = futures - base
        self.W = _ridge(X, Y, self.alpha)
        self.L_used = L
        self.n_train_windows = int(X.shape[0])
        w = hist[-L:]
        a = float(w[-1])
        return (w - a) @ self.W + a


class DLinear:
    """Moving-average decomposition plus two linear layers (Zeng et al. 2023, §4.1).

    The two linear layers are fitted **jointly**: the paper's model is
    ``ŷ = W_trend x_trend + W_season x_season`` under a single loss, so the
    two maps are estimated against one objective and their sum is the forecast.
    Fitting them independently and adding the two least-squares solutions would
    count the shared component twice (on a pure sinusoid it doubles the forecast).
    Concretely the design matrix is ``[x_trend | x_season]`` and one ridge solve
    returns the stacked weights.
    """

    name = "DLinear"

    def __init__(
        self,
        lookback: int = DEFAULT_LOOKBACK,
        kernel_size: int = DEFAULT_KERNEL,
        alpha: float = DEFAULT_ALPHA,
    ) -> None:
        self.lookback = int(lookback)
        self.kernel_size = int(kernel_size)
        self.alpha = float(alpha)
        self.W: np.ndarray | None = None
        self.L_used: int | None = None
        self.n_train_windows: int = 0

    def _decompose_pairs(self, hist: np.ndarray, H: int):
        windows, futures, L = _training_pairs(hist, H, self.lookback)
        trend = np.stack([_moving_average(w, self.kernel_size) for w in windows])
        season = windows - trend
        return np.hstack([trend, season]), futures, L

    def fit_predict(self, hist: np.ndarray, H: int, seasonality: int | None = None) -> np.ndarray:
        X, futures, L = self._decompose_pairs(hist, H)
        self.W = _ridge(X, futures, self.alpha)
        self.L_used = L
        self.n_train_windows = int(X.shape[0])
        w = hist[-L:]
        tr = _moving_average(w, self.kernel_size)
        se = w - tr
        return np.concatenate([tr, se]) @ self.W


def build_baselines(lookback: int = DEFAULT_LOOKBACK, alpha: float = DEFAULT_ALPHA) -> dict:
    """The three Phase 1b baselines, fresh per call (they hold fitted state)."""
    return {
        "SeasonalNaive": SeasonalNaive(),
        "NLinear": NLinear(lookback=lookback, alpha=alpha),
        "DLinear": DLinear(lookback=lookback, alpha=alpha),
    }
