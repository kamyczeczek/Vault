"""KNN Feature-Space Forecaster v2 for the benchmark suite.

Combines NLinear de-anchoring, multi-channel shape/derivative/subband representation,
composite manifold distance matching (shape, velocity, phase, scale), confidence-gated
motif trajectory retrieval, and locally weighted Ridge forecast blending.
"""
from __future__ import annotations

from typing import Any
import numpy as np

try:
    import pywt
except Exception:  # pragma: no cover
    pywt = None


class KNNFeatureForecaster:
    """Regime-aware direct multi-horizon hybrid motif KNN forecaster."""

    FILTER_LENGTHS = (3, 6, 12, 24)

    def __init__(
        self,
        input_length: int = 96,
        k_neighbors: int = 24,
        alpha: float = 10.0,
        bandwidth: float = 0.75,
        w_shape: float = 0.40,
        w_deriv: float = 0.25,
        w_subband: float = 0.20,
        w_scale: float = 0.15,
        confidence_threshold: float = 1.8,
    ) -> None:
        if input_length < 2:
            raise ValueError("input_length must be at least 2")
        if k_neighbors < 1:
            raise ValueError("k_neighbors must be positive")
        if alpha <= 0:
            raise ValueError("alpha must be positive")
        if bandwidth <= 0:
            raise ValueError("bandwidth must be positive")

        self.input_length = int(input_length)
        self.k_neighbors = int(k_neighbors)
        self.alpha = float(alpha)
        self.bandwidth = float(bandwidth)

        # Distance composition weights
        self.w_shape = float(w_shape)
        self.w_deriv = float(w_deriv)
        self.w_subband = float(w_subband)
        self.w_scale = float(w_scale)
        self.confidence_threshold = float(confidence_threshold)

        self.X_shape_train_: np.ndarray | None = None
        self.X_deriv_train_: np.ndarray | None = None
        self.X_subband_train_: np.ndarray | None = None
        self.X_scale_train_: np.ndarray | None = None
        self.Y_train_: np.ndarray | None = None
        self.horizon_: int | None = None

    def _z_normalize(self, arr: np.ndarray) -> np.ndarray:
        std = np.std(arr, axis=-1, keepdims=True) + 1e-8
        mean = np.mean(arr, axis=-1, keepdims=True)
        return (arr - mean) / std

    def _extract_channels(self, window: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Extract multi-faceted channel representations from a raw window."""
        x = np.asarray(window, dtype=np.float64).ravel()
        anchor = float(x[-1])
        deanchored = x - anchor

        # 1. Shape channel (Z-normalized deanchored history)
        shape_feat = (deanchored - np.mean(deanchored)) / (np.std(deanchored) + 1e-8)

        # 2. Derivative channel (first & second differences)
        d1 = np.diff(deanchored, prepend=0.0)
        d2 = np.diff(d1, prepend=0.0)
        deriv_feat = np.concatenate([d1, d2])

        # 3. Subband / filter-bank channel
        subbands = [deanchored]
        for w in self.FILTER_LENGTHS:
            if len(deanchored) >= w:
                k = np.ones(w, dtype=np.float64) / w
                subbands.append(np.convolve(deanchored, k, mode="same"))
            else:
                subbands.append(deanchored)

        if pywt is not None:
            try:
                cA, d1_wt = pywt.swt(deanchored, "db4", level=1)[0]
                subbands.extend([np.asarray(cA, dtype=np.float64), np.asarray(d1_wt, dtype=np.float64)])
            except Exception:
                pass
        subband_feat = np.concatenate(subbands)

        # 4. Scale / regime channel (level, trend slope, volatility, min-max range)
        slope = float(deanchored[-1] - deanchored[0]) / max(len(deanchored), 1)
        vol = float(np.std(d1))
        range_span = float(np.max(deanchored) - np.min(deanchored))
        scale_feat = np.array([anchor, float(np.mean(x)), slope, vol, range_span], dtype=np.float64)

        return shape_feat, deriv_feat, subband_feat, scale_feat

    def fit(self, train: np.ndarray, horizon: int) -> "KNNFeatureForecaster":
        """Fit by materializing structured channel representations."""
        series = np.asarray(train, dtype=np.float64).ravel()
        if series.ndim != 1 or len(series) < self.input_length:
            raise ValueError("train must be a one-dimensional series")
        if horizon < 1:
            raise ValueError("horizon must be positive")

        ends = np.arange(self.input_length, len(series) - horizon + 1)
        if len(ends) == 0:
            raise ValueError("series is too short for requested horizon")

        shapes, derivs, subbands, scales, targets = [], [], [], [], []
        for end in ends:
            w = series[end - self.input_length : end]
            anchor = float(w[-1])
            fut = series[end : end + horizon]
            if len(fut) < horizon:
                fut = np.pad(fut, (0, horizon - len(fut)), mode="edge")

            s, d, sb, sc = self._extract_channels(w)
            shapes.append(s)
            derivs.append(d)
            subbands.append(sb)
            scales.append(sc)
            targets.append(fut - anchor)

        self.X_shape_train_ = np.stack(shapes, axis=0)
        self.X_deriv_train_ = np.stack(derivs, axis=0)
        self.X_subband_train_ = np.stack(subbands, axis=0)
        self.X_scale_train_ = np.stack(scales, axis=0)
        self.Y_train_ = np.stack(targets, axis=0)
        self.horizon_ = int(horizon)

        # Standardize non-shape channels across training set
        self.deriv_mean_ = np.mean(self.X_deriv_train_, axis=0)
        self.deriv_scale_ = np.std(self.X_deriv_train_, axis=0) + 1e-8
        self.X_deriv_train_std_ = (self.X_deriv_train_ - self.deriv_mean_) / self.deriv_scale_

        self.sb_mean_ = np.mean(self.X_subband_train_, axis=0)
        self.sb_scale_ = np.std(self.X_subband_train_, axis=0) + 1e-8
        self.X_subband_train_std_ = (self.X_subband_train_ - self.sb_mean_) / self.sb_scale_

        self.scale_mean_ = np.mean(self.X_scale_train_, axis=0)
        self.scale_scale_ = np.std(self.X_scale_train_, axis=0) + 1e-8
        self.X_scale_train_std_ = (self.X_scale_train_ - self.scale_mean_) / self.scale_scale_

        return self

    def predict_hist(self, hist: np.ndarray) -> np.ndarray:
        """Predict trajectory via composite manifold distance matching."""
        if self.X_shape_train_ is None or self.Y_train_ is None:
            raise RuntimeError("fit must be called before predict_hist")

        history = np.asarray(hist, dtype=np.float64).ravel()
        if len(history) >= self.input_length:
            w = history[-self.input_length :]
        else:
            w = np.pad(history, (self.input_length - len(history), 0), mode="edge")

        anchor = float(w[-1])
        q_shape, q_deriv, q_subband, q_scale = self._extract_channels(w)

        # Standardize query non-shape channels
        q_deriv_std = (q_deriv - self.deriv_mean_) / self.deriv_scale_
        q_sb_std = (q_subband - self.sb_mean_) / self.sb_scale_
        q_scale_std = (q_scale - self.scale_mean_) / self.scale_scale_

        # Channel distances
        d_shape = np.linalg.norm(self.X_shape_train_ - q_shape[None, :], axis=1) / np.sqrt(len(q_shape))
        d_deriv = np.linalg.norm(self.X_deriv_train_std_ - q_deriv_std[None, :], axis=1) / np.sqrt(len(q_deriv))
        d_sb = np.linalg.norm(self.X_subband_train_std_ - q_sb_std[None, :], axis=1) / np.sqrt(len(q_subband))
        d_scale = np.linalg.norm(self.X_scale_train_std_ - q_scale_std[None, :], axis=1) / np.sqrt(len(q_scale))

        # Composite hybrid distance metric
        d_composite = (
            self.w_shape * d_shape
            + self.w_deriv * d_deriv
            + self.w_subband * d_sb
            + self.w_scale * d_scale
        )

        K = min(self.k_neighbors, len(d_composite))
        indices = np.argsort(d_composite, kind="stable")[:K]

        nn_dists = d_composite[indices]
        y_nn = self.Y_train_[indices]

        # Gaussian kernel distance weights
        sigma = max(float(np.median(nn_dists)), 1e-5)
        weights = np.exp(-0.5 * (nn_dists / (self.bandwidth * sigma)) ** 2)
        weights /= np.sum(weights) + 1e-12

        # 1. Distance-weighted trajectory continuation (pure motif retrieval)
        motif_traj = np.sum(y_nn * weights[:, None], axis=0)

        # 2. Local Ridge Regression over subband features
        x_sb_nn = self.X_subband_train_std_[indices]
        w_sqrt = np.sqrt(weights)[:, None]
        X_w = x_sb_nn * w_sqrt
        Y_w = y_nn * w_sqrt

        gram = X_w.T @ X_w
        diag_idx = np.arange(gram.shape[0])
        gram[diag_idx, diag_idx] += self.alpha
        cross = X_w.T @ Y_w

        try:
            ridge_W = np.linalg.solve(gram, cross)
            ridge_traj = q_sb_std @ ridge_W
        except Exception:
            ridge_traj = motif_traj

        # 3. Confidence gating / blend:
        # If nearest match is high-confidence (small distance), favor motif retrieval.
        # Otherwise, lean towards local linear/Ridge extrapolation.
        top_dist = float(nn_dists[0])
        confidence = np.exp(-top_dist / self.confidence_threshold)

        delta_hat = confidence * motif_traj + (1.0 - confidence) * ridge_traj
        return delta_hat + anchor

    def get_params(self) -> dict[str, Any]:
        return {
            "input_length": self.input_length,
            "k_neighbors": self.k_neighbors,
            "alpha": self.alpha,
            "bandwidth": self.bandwidth,
            "weights": {
                "shape": self.w_shape,
                "deriv": self.w_deriv,
                "subband": self.w_subband,
                "scale": self.w_scale,
            },
        }
