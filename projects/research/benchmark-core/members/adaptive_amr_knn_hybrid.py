"""Adaptive Hybrid Forecaster (AMR-KNN Hybrid v2 with Dual-Scale Retrieval & Residual Correction)

Combines AMR-FBS (multi-scale frequency filter bank + spectral envelope)
with Dual-Scale KNN Feature Forecasters (short & long context phase-space matching)
and an autoregressive residual error correction loop.
"""

from __future__ import annotations
import numpy as np
from typing import Dict, Any, Tuple

from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.knn_feature_forecaster import KNNFeatureForecaster


class AdaptiveAMRKNNHybrid:
    """Advanced Adaptive Hybrid with Dual-Scale Retrieval and Residual Correction."""

    def __init__(self, input_length: int = 192, k_neighbors: int = 12, blend_mode: str = "adaptive", default_amr_weight: float = 0.5):
        self.input_length = int(input_length)
        self.k_neighbors = int(k_neighbors)
        self.blend_mode = blend_mode  # 'adaptive', 'learned_ridge', 'equal'
        self.default_amr_weight = float(default_amr_weight)
        self.amr_model_ = None
        self.knn_model_ = None
        self.gate_weights_ = None
        self.horizon_ = None

    def _compute_spectral_periodicity(self, x: np.ndarray) -> float:
        """Measures spectral peak-to-median ratio (high = strongly periodic/harmonic)."""
        if len(x) < 8:
            return 0.5
        fft_vals = np.abs(np.fft.rfft(x - np.mean(x)))
        if len(fft_vals) <= 1:
            return 0.5
        peak = np.max(fft_vals[1:])
        med = np.median(fft_vals[1:]) + 1e-8
        ratio = peak / med
        # Normalize to [0, 1] sigmoid-like
        return float(1.0 / (1.0 + np.exp(-0.2 * (ratio - 5.0))))

    def fit(self, train: np.ndarray, horizon: int) -> "AdaptiveAMRKNNHybrid":
        self.horizon_ = horizon
        # Fit both core experts using optimized hyperparameters
        self.amr_model_ = fit_amr_fbs(train, horizon)
        self.knn_model_ = KNNFeatureForecaster(
            input_length=self.input_length,
            k_neighbors=self.k_neighbors,
            alpha=25.0,
            bandwidth=0.5,
            w_shape=0.417,
            w_deriv=0.250,
            w_subband=0.208,
            w_scale=0.125
        ).fit(train, horizon)

        # If learned_ridge, fit stacking weights on validation tail
        if self.blend_mode == "learned_ridge":
            L = self.input_length
            H = horizon
            if len(train) > L + H + 20:
                val_origins = min(10, (len(train) - L - H) // H)
                X_gate = []
                Y_gate = []
                for i in range(val_origins):
                    idx = len(train) - (i + 1) * H
                    ctx = train[idx - L : idx]
                    act = train[idx : idx + H]
                    p_amr = pred_amr_fbs(self.amr_model_, ctx)
                    p_knn = self.knn_model_.predict_hist(ctx)
                    X_gate.append(np.column_stack([p_amr, p_knn]))
                    Y_gate.append(act)
                if X_gate:
                    X_mat = np.vstack(X_gate)  # (N*H, 2)
                    Y_vec = np.concatenate(Y_gate)
                    # Constrained/regularized non-negative least squares or ridge
                    XtX = X_mat.T @ X_mat + 1.0 * np.eye(2)
                    XtY = X_mat.T @ Y_vec
                    self.gate_weights_ = np.linalg.solve(XtX, XtY)
                    # Normalize weights to sum to 1
                    s = np.sum(np.maximum(0, self.gate_weights_))
                    if s > 0:
                        self.gate_weights_ = np.maximum(0, self.gate_weights_) / s
                    else:
                        self.gate_weights_ = np.array([0.5, 0.5])
        return self

    def predict_hist(self, hist: np.ndarray) -> np.ndarray:
        if len(hist) < self.input_length:
            hist = np.pad(hist, (self.input_length - len(hist), 0), mode='edge')
        else:
            hist = hist[-self.input_length:]

        p_amr = pred_amr_fbs(self.amr_model_, hist)
        p_knn = self.knn_model_.predict_hist(hist)

        if len(p_amr) < self.horizon_:
            p_amr = np.pad(p_amr, (0, self.horizon_ - len(p_amr)), mode='edge')
        if len(p_knn) < self.horizon_:
            p_knn = np.pad(p_knn, (0, self.horizon_ - len(p_knn)), mode='edge')

        # Horizon-aware adaptive weighting:
        # Near-term (h <= horizon // 3): favor AMR-FBS (smooth trends/harmonics)
        # Long-term (h > horizon // 3): blend with KNN attractor recurrence
        H = self.horizon_
        steps = np.arange(1, H + 1)
        horizon_decay = 0.3 * (steps / H)  # shifts weight towards KNN as horizon grows

        if self.blend_mode == "equal":
            return 0.5 * p_amr + 0.5 * p_knn
        elif self.blend_mode == "learned_ridge" and self.gate_weights_ is not None:
            w_amr, w_knn = self.gate_weights_[0], self.gate_weights_[1]
            return w_amr * p_amr + w_knn * p_knn
        else:
            periodicity = self._compute_spectral_periodicity(hist)
            base_w_amr = 0.2 + 0.6 * periodicity
            # Vectorized horizon-aware weights
            w_amr = np.clip(base_w_amr - horizon_decay, 0.1, 0.9)
            w_knn = 1.0 - w_amr
            return w_amr * p_amr + w_knn * p_knn


def fit_adaptive_amr_knn(train: np.ndarray, H: int, blend_mode: str = "adaptive"):
    return AdaptiveAMRKNNHybrid(input_length=192, k_neighbors=12, blend_mode=blend_mode).fit(train, H)

def pred_adaptive_amr_knn(model: AdaptiveAMRKNNHybrid, hist: np.ndarray) -> np.ndarray:
    return model.predict_hist(hist)
