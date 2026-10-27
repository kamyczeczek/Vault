"""FITS-style frequency-domain forecaster (S-07, h720).

Published-behavior class (Xu et al. 2024, "FITS: Modeling Time Series
with 10k Parameters"): the standardized lookback window is mapped to
the frequency domain (rFFT), a complex ridge readout learns the
linear map from the lookback spectrum to the EXTENDED spectrum
(lookback + horizon, so the forecast is a continuation of the same
frequency representation), a low-pass filter zeroes frequencies above
the cutoff, and the inverse rFFT materializes the extended signal —
the forecast is its horizon tail.

In-project design notes:
- RevIN-style per-window standardization BEFORE the rFFT (same
  convention as DLinear/RLinear: window (mu, sigma), ``_SCALE_EPS``
  clamp; de-standardize the horizon tail at predict). Frequency
  extrapolation on a raw-scale spectrum would carry the level into
  every coefficient — the S-05 lesson, applied to the spectral
  domain.
- Closed-form ridge on complex features (no iterative solver, no
  RNG): ``W = (X^H X + aI)^{-1} X^H Y`` with an explicit intercept
  column folded into the complex design (real 1s) so the DC term is
  not forced through the origin.
- The LPF cutoff is a plain integer: keep frequencies ``< cutoff``
  (of the rFFT of the extended length) — ``None`` keeps everything.
- Deterministic end to end: rFFT (numpy pocketfft) + closed-form
  solve; no seeds, no RNG anywhere.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np

from .base import BaseForecaster


class FITSForecaster(BaseForecaster):
    """Frequency-domain linear forecaster (rFFT + complex ridge + LPF)."""

    def __init__(
        self,
        input_length: int = 720,
        ridge_alpha: float = 1e-3,
        cutoff: int | None = None,
    ):
        self.input_length = input_length
        self.ridge_alpha = ridge_alpha
        self.cutoff = cutoff

    # -- helpers ---------------------------------------------------------
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
        """Per-window (mean, std), identical convention to DLinear/RLinear."""
        mu = float(window.mean())
        sigma = max(float(window.std()), self._SCALE_EPS)
        return mu, sigma

    def _spectrum(self, window: np.ndarray, horizon: int) -> np.ndarray:
        """Standardized window -> extended-length rFFT (features, row)."""
        mu, sigma = self._window_stats(window)
        std = (window - mu) / sigma
        n_ext = self.input_length + horizon
        return np.fft.rfft(std[:, 0], n=n_ext)

    def _filter(self, spectrum: np.ndarray) -> np.ndarray:
        """Low-pass: zero frequencies at/after the cutoff index."""
        if self.cutoff is None:
            return spectrum
        out = np.zeros_like(spectrum)
        keep = min(self.cutoff, len(spectrum))
        out[:keep] = spectrum[:keep]
        return out

    # -- fit / predict ---------------------------------------------------
    def fit(
        self, y: Iterable[float], *, horizon: int, target_index: int = 0
    ) -> "FITSForecaster":
        series = self._array(y)
        self._check_horizon(horizon)
        if target_index < 0 or target_index >= series.shape[1]:
            raise ValueError("target index out of range")
        n_ext = self.input_length + horizon
        x_rows, y_rows = [], []
        for end in range(self.input_length, len(series) - horizon + 1):
            window = series[end - self.input_length : end]
            mu, sigma = self._window_stats(window)
            std = (window[:, target_index] - mu) / sigma
            f = np.fft.rfft(std, n=n_ext)
            target = series[end : end + horizon, target_index]
            t_std = (target - mu) / sigma
            g = np.fft.rfft(
                np.concatenate([std, t_std]), n=n_ext
            )  # same length; extended-spectrum supervision
            x_rows.append(f)
            y_rows.append(g)
        X = np.asarray(x_rows)  # complex (n, F)
        Y = np.asarray(y_rows)  # complex (n, F)
        # Fold a real intercept into the complex design: column of ones
        # solves the per-frequency DC offset in closed form.
        n = X.shape[0]
        ones = np.ones((n, 1), dtype=complex)
        Xd = np.concatenate([X, ones], axis=1)
        gram = Xd.conj().T @ Xd
        reg = np.eye(Xd.shape[1], dtype=complex) * self.ridge_alpha
        W = np.linalg.solve(gram + reg, Xd.conj().T @ Y)  # (F+1, F)
        self.W_ = W
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
        std = (window[:, self.target_index] - mu) / sigma
        n_ext = self.input_length + self.horizon_
        f = np.fft.rfft(std, n=n_ext)
        x = np.concatenate([f, np.array([1.0 + 0.0j])])
        g_hat = self._filter(np.asarray(x @ self.W_))
        ext = np.fft.irfft(g_hat, n=n_ext)
        tail = ext[self.input_length :] * sigma + mu
        return np.asarray(tail[: self.horizon_])
