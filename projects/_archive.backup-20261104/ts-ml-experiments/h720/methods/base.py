"""Abstract base class for all forecasting models.

Every model in :mod:`methods` inherits from :class:`BaseForecaster` and
implements the same two-method interface so experiment runners can treat
them uniformly:

    model = SomeForecaster(**hyperparams)
    model.fit(y, horizon=H)          # y: 1-D history; returns self
    forecast = model.predict()       # -> np.ndarray shape (H,)

Notes
-----
* ``horizon`` is a keyword argument of :meth:`fit`, keeping constructors
  pure hyperparameter bags. Each subclass encodes its own lookback
  behaviour via hyperparameters (``delays``, ``input_length``).
* Models store the fitted history internally, so :meth:`predict` takes
  no arguments and returns a 1-D ``numpy.ndarray`` of length ``horizon``.
* ``fit`` always returns ``self``; calling ``predict`` before ``fit``
  raises ``RuntimeError``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

import numpy as np


class BaseForecaster(ABC):
    """Common interface shared by every forecasting method."""

    #: Filled by :meth:`fit`; allows :meth:`predict` to validate the horizon.
    horizon_: int
    _fitted: bool = False

    @abstractmethod
    def fit(self, y: Iterable[float], *, horizon: int) -> "BaseForecaster":
        """Train on history ``y`` for the given ``horizon``."""

    @abstractmethod
    def predict(self) -> np.ndarray:
        """Return the forecast as a 1-D array of length ``horizon_``."""

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------
    def _check_horizon(self, horizon: int) -> None:
        if not isinstance(horizon, int) or isinstance(horizon, bool) or horizon < 1:
            raise ValueError(f"horizon must be a positive integer, got {horizon!r}")

    def _check_fitted(self) -> None:
        if not getattr(self, "_fitted", False):
            raise RuntimeError("fit must be called before predict")

    def _as_series(self, y: Iterable[float], min_len: int = 1) -> np.ndarray:
        """Coerce history to a 1-D float array with at least ``min_len`` values."""
        series = np.asarray(list(y), dtype=float)
        if series.ndim != 1 or len(series) < min_len or not np.isfinite(series).all():
            raise ValueError(
                f"history must be a finite 1-D series of length >= {min_len}"
            )
        return series

    @staticmethod
    def _anchor(series: np.ndarray, idx: int, q: int) -> float:
        """Local anchor: mean of the ``q`` values ending at (excluding) ``idx``."""
        return float(series[idx - q : idx].mean())

    #: Minimum scale to avoid division by (near-)constant windows.
    _SCALE_EPS: float = 1e-8

    @classmethod
    def _window_scale(
        cls,
        series: np.ndarray,
        idx: int,
        normalize_scale: bool,
        scale_window: int,
    ) -> float:
        """RevIN-style trailing-window scale ending at (excluding) ``idx``.

        Returns the population std of ``series[max(0, idx - scale_window):idx]``
        when ``normalize_scale`` is set, else ``1.0`` (identity — keeps the
        unnormalised code path byte-identical). Near-constant windows are
        clamped to ``_SCALE_EPS``. Early origins (``idx < scale_window``)
        use the truncated window — deterministic, never future data.
        """
        if not normalize_scale:
            return 1.0
        window = series[max(0, idx - scale_window) : idx]
        return max(float(np.std(window)), cls._SCALE_EPS)

    @classmethod
    def _lag_features(
        cls,
        series: np.ndarray,
        idx: int,
        delays: tuple[int, ...],
        anchor: float,
        normalize_scale: bool = False,
        scale_window: int = 168,
    ) -> np.ndarray:
        """Anchor-normalised lag features, shape ``(1, len(delays))``.

        Feature ``j`` is ``(series[idx - delays[j]] - anchor) / scale`` where
        ``scale`` is the trailing-window std when ``normalize_scale`` is set
        (else 1). ``idx`` may equal ``len(series)`` (forecast time) or be an
        interior origin.
        """
        scale = cls._window_scale(series, idx, normalize_scale, scale_window)
        return np.array(
            [[float(series[idx - d] - anchor) / scale for d in delays]]
        )

    @staticmethod
    def _fit_affine(
        preds: np.ndarray, targets: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Per-output least-squares affine map ``targets ~ gamma * preds + beta``.

        Column-wise closed form (deterministic, no RNG): for each output
        dimension ``j``, ``gamma_j = cov(p_j, y_j) / var(p_j)`` (``1.0`` when
        ``var(p_j)`` is degenerate) and ``beta_j = mean(y_j) - gamma_j *
        mean(p_j)``. Used for the optional RevIN-affine readout correction.
        """
        preds = np.asarray(preds, dtype=float)
        targets = np.asarray(targets, dtype=float)
        pm = preds.mean(axis=0)
        ym = targets.mean(axis=0)
        pc = preds - pm
        yc = targets - ym
        var = (pc * pc).sum(axis=0)
        cov = (pc * yc).sum(axis=0)
        safe_var = np.where(var > 1e-12, var, 1.0)
        gamma = np.where(var > 1e-12, cov / safe_var, 1.0)
        beta = ym - gamma * pm
        return gamma, beta

    @staticmethod
    def _loo_knn_predictions(
        X: np.ndarray, Y: np.ndarray, k: int
    ) -> np.ndarray:
        """Leave-one-out distance-weighted kNN predictions on the training set.

        In-sample kNN is degenerate for affine fitting (each point is its
        own zero-distance neighbour, so predictions equal the targets
        exactly); the LOO variant excludes the self-index and averages the
        ``k`` remaining neighbours with ``1/max(d, 1e-12)`` weights — the
        same convention as the parent's ``weights="distance"`` readout.
        Deterministic: pure geometry, no RNG.
        """
        from sklearn.neighbors import NearestNeighbors

        n = len(X)
        kk = min(k + 1, n)
        nn = NearestNeighbors(n_neighbors=kk).fit(X)
        dist, ind = nn.kneighbors(X)
        P = np.empty((n, Y.shape[1]), dtype=float)
        for i in range(n):
            keep = ind[i] != i
            d = dist[i][keep][:k]
            j = ind[i][keep][:k]
            if len(d) == 0:
                P[i] = Y[i]
                continue
            w = 1.0 / np.maximum(d, 1e-12)
            P[i] = (w @ Y[j]) / w.sum()
        return P

    @classmethod
    def _origins(
        cls,
        series: np.ndarray,
        horizon: int,
        min_lookback: int,
        history_fraction: float,
    ) -> np.ndarray:
        """Training origins, most recent ``history_fraction`` of the series.

        Falls back to the full series when the recent window yields fewer
        than 3 origins. Raises when even the full series cannot supply 3.
        """
        n = len(series)
        start = max(min_lookback, int(n * (1.0 - history_fraction)))
        origins = np.arange(start, n - horizon + 1)
        if len(origins) < 3:
            origins = np.arange(min_lookback, n - horizon + 1)
        if len(origins) < 3:
            raise ValueError(
                f"not enough valid origins (need >= 3, series length {n}, "
                f"horizon {horizon})"
            )
        return origins

    @classmethod
    def _lag_dataset(
        cls,
        series: np.ndarray,
        horizon: int,
        delays: tuple[int, ...],
        q: int,
        history_fraction: float = 1.0,
        normalize_scale: bool = False,
        scale_window: int = 168,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Build the anchor-normalised lag training set.

        Returns ``(X, Y, origins)`` where row ``k`` corresponds to origin
        ``i = origins[k]``:
        - ``X[k] = [(series[i - d] - anchor(i)) / scale(i)] for d in delays``
        - ``Y[k] = (series[i : i + horizon] - anchor(i)) / scale(i)``
        with ``anchor(i) = mean(series[i - q : i])`` and ``scale(i)`` the
        trailing-window std when ``normalize_scale`` is set (else 1 —
        identical to the historical unnormalised dataset).

        With ``normalize_scale=False`` (default) the output is
        byte-identical to the pre-S-04 dataset: the scale factor is 1.0
        everywhere and division is a no-op.
        """
        origins = cls._origins(series, horizon, max(q, max(delays)), history_fraction)
        anchors = np.array([cls._anchor(series, int(i), q) for i in origins])
        scales = np.array(
            [
                cls._window_scale(series, int(i), normalize_scale, scale_window)
                for i in origins
            ]
        )
        X = np.column_stack(
            [(series[origins - d] - anchors) / scales for d in delays]
        ).astype(float)
        Y = np.stack(
            [
                (series[i : i + horizon] - a) / s
                for i, a, s in zip(origins, anchors, scales)
            ]
        )
        return X, Y, origins
