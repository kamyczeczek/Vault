"""Financial Hybrid Forecaster for the benchmark suite.

Combines stochastic drift anchoring (ETS/Theta style), volatility-normalized
return-space KNN motif retrieval, and adaptive shrinkage toward zero drift
during high-entropy market regimes.
"""
from __future__ import annotations

import numpy as np

class FinancialHybridForecaster:
    def __init__(self, input_length: int = 96, k_neighbors: int = 16):
        self.input_length = int(input_length)
        self.k_neighbors = int(k_neighbors)
        self.X_train_ = None
        self.Y_train_ = None
        self.horizon_ = 24

    def fit(self, train: np.ndarray, horizon: int) -> "FinancialHybridForecaster":
        series = np.asarray(train, dtype=float).ravel()
        self.horizon_ = int(horizon)
        ends = np.arange(self.input_length, len(series) - horizon + 1)

        X_feats, Y_targets = [], []
        for end in ends:
            w = series[end - self.input_length : end]
            fut = series[end : end + horizon]
            if len(fut) < horizon:
                fut = np.pad(fut, (0, horizon - len(fut)), mode="edge")

            # Feature: return-space Z-normalized shape (length input_length - 1)
            diffs = np.diff(w)
            denom = np.abs(w[:-1]) + 1e-8
            returns = diffs / denom
            feat = (returns - np.mean(returns)) / (np.std(returns) + 1e-8)

            anchor = float(w[-1])
            target_returns = (fut - anchor) / (anchor + 1e-8)

            X_feats.append(feat)
            Y_targets.append(target_returns)

        self.X_train_ = np.stack(X_feats, axis=0)
        self.Y_train_ = np.stack(Y_targets, axis=0)
        return self

    def predict(self, hist: np.ndarray, horizon: int) -> np.ndarray:
        history = np.asarray(hist, dtype=float).ravel()
        if len(history) >= self.input_length:
            w = history[-self.input_length:]
        else:
            w = np.pad(history, (self.input_length - len(history), 0), mode="edge")

        anchor = float(w[-1])
        diffs = np.diff(w)
        denom = np.abs(w[:-1]) + 1e-8
        returns = diffs / denom
        q_feat = (returns - np.mean(returns)) / (np.std(returns) + 1e-8)

        # KNN motif search
        dists = np.linalg.norm(self.X_train_ - q_feat[None, :], axis=1)
        idx = np.argsort(dists)[:self.k_neighbors]

        # Locally weighted average of target returns
        d_k = dists[idx]
        weights = np.exp(-d_k / (np.mean(d_k) + 1e-8))
        weights /= np.sum(weights) + 1e-8

        pred_returns = np.sum(self.Y_train_[idx] * weights[:, None], axis=0)

        # Stochastic drift baseline (linear trend from last 10 points)
        drift = (w[-1] - w[-10]) / 10.0 if len(w) >= 10 else 0.0
        t = np.arange(1, horizon + 1)
        drift_pred = w[-1] + drift * t * 0.3 # damped drift

        motif_pred = anchor * (1.0 + pred_returns[:horizon])

        # Blend motif retrieval with damped drift based on distance confidence
        confidence = float(1.0 / (1.0 + np.mean(d_k)))
        final_pred = confidence * motif_pred + (1.0 - confidence) * drift_pred
        return final_pred[:horizon]
