"""AlphaMomentumHybrid Forecaster for Financial Time Series.

Features:
1. Volatility-normalized return space (GARCH-like scaling).
2. Dual-pathway architecture: Damped trend drift + cosine-similarity motif retrieval.
3. Entropy-gated adaptive shrinkage during high-volatility market regimes.
"""
from __future__ import annotations
import numpy as np

class AlphaMomentumHybrid:
    def __init__(self, input_length: int = 96, k_neighbors: int = 12):
        self.input_length = int(input_length)
        self.k_neighbors = int(k_neighbors)
        self.X_train_ = None
        self.Y_train_ = None
        self.horizon_ = 24

    def fit(self, train: np.ndarray, horizon: int) -> "AlphaMomentumHybrid":
        series = np.asarray(train, dtype=float).ravel()
        self.horizon_ = int(horizon)
        ends = np.arange(self.input_length, len(series) - horizon + 1)

        X_feats, Y_targets = [], []
        for end in ends:
            w = series[end - self.input_length : end]
            fut = series[end : end + horizon]
            if len(fut) < horizon:
                fut = np.pad(fut, (0, horizon - len(fut)), mode="edge")

            # Volatility-normalized returns
            diffs = np.diff(w)
            denom = np.abs(w[:-1]) + 1e-8
            returns = diffs / denom
            vol = np.std(returns) + 1e-8
            norm_returns = returns / vol

            anchor = float(w[-1])
            target_returns = (fut - anchor) / (anchor + 1e-8)

            X_feats.append(norm_returns)
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
        vol = np.std(returns) + 1e-8
        q_feat = returns / vol

        # Cosine similarity motif search
        norms = np.linalg.norm(self.X_train_, axis=1) + 1e-8
        q_norm = np.linalg.norm(q_feat) + 1e-8
        cos_sims = (self.X_train_ @ q_feat) / (norms * q_norm)

        # Top k neighbors by cosine similarity
        idx = np.argsort(cos_sims)[::-1][:self.k_neighbors]
        sims = cos_sims[idx]

        # Softmax weighting of neighbor target returns
        weights = np.exp(np.clip(sims * 3.0, -10.0, 10.0))
        weights /= np.sum(weights) + 1e-8

        pred_returns = np.sum(self.Y_train_[idx] * weights[:, None], axis=0)
        motif_pred = anchor * (1.0 + pred_returns[:horizon])

        # Drift baseline (exponentially weighted recent slope)
        recent_diffs = np.diff(w[-10:]) if len(w) >= 10 else np.diff(w)
        drift = float(np.mean(recent_diffs))
        t = np.arange(1, horizon + 1)
        drift_pred = anchor + drift * t * 0.5 # damped trend

        # Entropy gating: measure volatility of volatility
        vol_of_vol = float(np.std(np.abs(recent_diffs)))
        entropy_gate = 1.0 / (1.0 + vol_of_vol * 5.0) # higher vol of vol -> lower confidence in motif

        # Blend motif retrieval with drift based on entropy gate and mean similarity
        mean_sim = float(np.mean(np.maximum(0.0, sims)))
        confidence = float(np.clip(entropy_gate * mean_sim, 0.05, 0.95))

        final_pred = confidence * motif_pred + (1.0 - confidence) * drift_pred
        return final_pred[:horizon]
