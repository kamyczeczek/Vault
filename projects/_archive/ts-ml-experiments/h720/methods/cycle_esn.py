"""Deterministic Simple Cycle Reservoir (SCR) with NLinear Inductive Biases (S-18).

Combines:
1. Rodan & Tiño (2011) Simple Cycle Reservoir (SCR):
   - Circular reservoir topology: W[i+1, i] = r_c, W[0, N-1] = r_c (directed ring).
   - Spectral radius is exactly r_c < 1.0 (Echo State Property).
   - Deterministic input weights: fixed magnitude v > 0, signs from decimal expansion of pi thresholded at 4.5.
   - Zero randomness (no RNG calls).
2. NLinear (Zeng et al., AAAI 2023) inductive biases:
   - Last-value anchoring: x_norm = window - window[-1]
   - Linear skip connection: concatenates raw x_norm directly to reservoir states [x_norm, h_T]
   - Ridge readout to multi-step horizon H=720
   - De-anchoring: y_pred = y_norm + window[-1]
"""

from __future__ import annotations

import math
from typing import Iterable
import numpy as np
from sklearn.linear_model import Ridge

from .base import BaseForecaster


def get_pi_signs(n: int) -> np.ndarray:
    """Generate n deterministic signs in {-1.0, 1.0} from digits of pi."""
    import decimal
    with decimal.localcontext() as ctx:
        ctx.prec = n + 10
        C = 426880 * decimal.Decimal(10005).sqrt()
        K = 6
        M = 1
        X = 1
        L = 13591409
        S = L
        for i in range(1, math.ceil(n / 14) + 2):
            M = (M * (K**3 - 16 * K)) // (i**3)
            L += 545140134
            X *= -262537412640768000
            S += decimal.Decimal(M * L) / X
            K += 12
        pi = C / S
        pi_str = str(pi).replace(".", "")[1:n+1]

    digits = np.array([int(c) for c in pi_str[:n]], dtype=int)
    signs = np.where(digits >= 5, 1.0, -1.0)
    return signs


class CycleESN(BaseForecaster):
    """Deterministic Cycle Reservoir with NLinear last-value normalization."""

    def __init__(
        self,
        input_length: int = 336,
        n_reservoir: int = 64,
        rc: float = 0.9,
        v: float = 0.1,
        linear_skip: bool = True,
        ridge_alpha: float = 1.0,
    ):
        self.input_length = input_length
        self.n_reservoir = n_reservoir
        self.rc = rc
        self.v = v
        self.linear_skip = linear_skip
        self.ridge_alpha = ridge_alpha

        signs = get_pi_signs(self.n_reservoir)
        self.V_ = signs * float(self.v)  # shape (N,)

    def _compute_features_batch(
        self, series: np.ndarray, horizon: int
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Vectorized feature extraction across all sliding windows."""
        s = np.asarray(series, dtype=float).squeeze()
        T = len(s)
        L = self.input_length
        N = self.n_reservoir
        num_windows = T - L - horizon + 1
        if num_windows <= 0:
            raise ValueError("Insufficient series length for sliding windows.")

        # Vectorized striding for all input windows: shape (num_windows, L)
        idx = np.arange(num_windows)[:, None] + np.arange(L)
        windows = s[idx]
        anchors = windows[:, -1:]
        windows_norm = windows - anchors  # shape (num_windows, L)

        # Targets: shape (num_windows, horizon)
        target_idx = np.arange(num_windows)[:, None] + L + np.arange(horizon)
        targets = s[target_idx] - anchors

        # Vectorized reservoir update across all windows simultaneously:
        # At step k (from 0 to L-1):
        # input is windows_norm[:, k:k+1], shape (num_windows, 1)
        # state is (num_windows, N)
        V = self.V_[None, :]  # shape (1, N)
        rc = self.rc
        states = np.zeros((num_windows, N), dtype=float)

        for k in range(L):
            u_k = windows_norm[:, k : k + 1]  # (num_windows, 1)
            # In circular SCR: state j gets input V[j]*u_k + rc * state_{j-1}
            # np.roll on axis=1 shifts column j-1 to column j
            rolled = np.roll(states, shift=1, axis=1)
            states = np.tanh(u_k * V + rc * rolled)

        if self.linear_skip:
            features = np.hstack([windows_norm, states])
        else:
            features = states

        return features, targets, anchors.squeeze(-1)

    def _extract_single_features(self, window_1d: np.ndarray) -> np.ndarray:
        """Extract features for a single input window of length L."""
        w = np.asarray(window_1d, dtype=float).squeeze()
        L = self.input_length
        N = self.n_reservoir
        anchor = float(w[-1])
        w_norm = w - anchor

        # Single window reservoir forward pass
        V = self.V_
        rc = self.rc
        h = np.zeros(N, dtype=float)
        for k in range(L):
            u_k = w_norm[k]
            h = np.tanh(u_k * V + rc * np.roll(h, 1))

        if self.linear_skip:
            return np.concatenate([w_norm, h])
        return h

    def fit(self, y: Iterable[float], *, horizon: int = 720) -> "CycleESN":
        series = np.asarray(y, dtype=float).squeeze()
        self._check_horizon(horizon)
        self.horizon_ = int(horizon)

        X_mat, Y_mat, _ = self._compute_features_batch(series, self.horizon_)
        self.model_ = Ridge(alpha=self.ridge_alpha, fit_intercept=True).fit(X_mat, Y_mat)
        self.history_ = series
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        raw = self.history_[-self.input_length :]
        if raw.ndim > 1:
            raw = raw.squeeze()
        anchor = float(raw[-1])
        feats = self._extract_single_features(raw)
        pred_norm = self.model_.predict([feats])[0]
        return np.asarray(pred_norm) + anchor
