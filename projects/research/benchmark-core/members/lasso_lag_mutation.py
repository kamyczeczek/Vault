# ARCHIVED 2026-09-24: no wins recorded. Archived per REFLECTION_PROMISING_METHODS.md - imports kept for compatibility
"""Lasso Lag-Selection Mutation Model (`LassoLagHybrid`).

Combines:
1. Sparse auto-regressive lag selection via L1 regularized Lasso regression ($\alpha$ penalty).
2. Subband / State-space multi-scale feature expansion combined with sparse lag coefficients.
"""
from __future__ import annotations
import numpy as np
from sklearn.linear_model import Lasso

class LassoLagHybrid:
    def __init__(self, input_length: int = 96, max_lags: int = 36, alpha: float = 0.01):
        self.input_length = int(input_length)
        self.max_lags = int(max_lags)
        self.alpha = float(alpha)
        self.models_ = []
        self.horizon_ = 24

    def fit(self, train: np.ndarray, horizon: int) -> "LassoLagHybrid":
        series = np.asarray(train, dtype=float).ravel()
        self.horizon_ = int(horizon)
        n = len(series)
        L = self.input_length

        ends = np.arange(L + self.max_lags, n - horizon + 1)
        if len(ends) == 0:
            ends = np.arange(self.max_lags + 2, n - horizon + 1)
            L = max(10, len(ends))

        X_list, Y_list = [], []
        for end in ends:
            w = series[end - L : end]
            # Build lag feature matrix from history window
            lags = []
            for lag in range(1, self.max_lags + 1):
                if len(w) > lag:
                    lags.append(w[-lag])
                else:
                    lags.append(0.0)

            anchor = float(w[-1])
            fut = series[end : end + horizon] - anchor
            if len(fut) < horizon:
                fut = np.pad(fut, (0, horizon - len(fut)), mode="edge")

            X_list.append(lags)
            Y_list.append(fut)

        X_mat = np.array(X_list, dtype=float)
        Y_mat = np.array(Y_list, dtype=float)

        # Fit multi-output Lasso or independent Lasso per horizon step
        self.models_ = []
        for h_idx in range(horizon):
            lasso = Lasso(alpha=self.alpha, max_iter=2000, tol=1e-3, random_state=42)
            try:
                lasso.fit(X_mat, Y_mat[:, h_idx])
            except Exception:
                # Fallback if convergence fails
                from sklearn.linear_model import Ridge
                lasso = Ridge(alpha=1.0)
                lasso.fit(X_mat, Y_mat[:, h_idx])
            self.models_.append(lasso)

        return self

    def predict(self, hist: np.ndarray, horizon: int) -> np.ndarray:
        history = np.asarray(hist, dtype=float).ravel()
        if len(history) >= self.input_length:
            w = history[-self.input_length:]
        else:
            w = np.pad(history, (self.input_length - len(history), 0), mode="edge")

        lags = []
        for lag in range(1, self.max_lags + 1):
            if len(w) > lag:
                lags.append(w[-lag])
            else:
                lags.append(0.0)
        q_feat = np.array(lags, dtype=float)[None, :]

        anchor = float(w[-1])
        preds = []
        for lasso in self.models_[:horizon]:
            p = float(lasso.predict(q_feat)[0])
            preds.append(anchor + p)

        return np.asarray(preds, dtype=float)[:horizon]

def fit_lasso_lag(train, H):
    m = LassoLagHybrid(input_length=96, max_lags=36, alpha=0.005)
    m.fit(train, H)
    return m

def pred_lasso_lag(model, hist):
    return model.predict(hist, model.horizon_)
