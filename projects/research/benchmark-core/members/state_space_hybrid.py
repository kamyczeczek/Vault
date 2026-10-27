"""State Space + Dictionary Hybrid Forecaster (`StateSpaceDictionaryHybrid`).

Combines:
1. A structured linear state-space (SSM) recurrent backbone for global long-range memory and drift tracking.
2. A local BigDict / Subband residual correction pathway for non-linear transient refinement.
"""
from __future__ import annotations
import numpy as np
import pywt

class StateSpaceDictionaryHybrid:
    def __init__(self, input_length: int = 96, state_dim: int = 16, alpha: float = 100.0):
        self.input_length = int(input_length)
        self.state_dim = int(state_dim)
        self.alpha = float(alpha)

        self.A_ = None  # SSM transition matrix (diagonal/structured)
        self.B_ = None  # SSM input matrix
        self.C_ = None  # SSM output matrix
        self.W_res_ = None # Residual ridge weights
        self.horizon_ = 24

    def fit(self, train: np.ndarray, horizon: int) -> "StateSpaceDictionaryHybrid":
        series = np.asarray(train, dtype=float).ravel()
        self.horizon_ = int(horizon)
        n = len(series)
        L = self.input_length

        ends = np.arange(L, n - horizon + 1)
        if len(ends) == 0:
            ends = np.arange(2, n - horizon + 1)
            L = max(2, len(ends))

        # 1. Initialize stable diagonal SSM transition parameters (HiPPO-inspired decay)
        dt = 0.1
        diag_vals = np.linspace(-0.1, -1.0, self.state_dim)
        self.A_ = np.exp(diag_vals * dt)
        self.B_ = np.ones((self.state_dim, 1)) / np.sqrt(self.state_dim)
        self.C_ = np.ones((1, self.state_dim)) / np.sqrt(self.state_dim)

        # Collect state representations and residual targets
        X_states, Y_targets = [], []
        for end in ends:
            w = series[end - L : end]
            fut = series[end : end + horizon]
            if len(fut) < horizon:
                fut = np.pad(fut, (0, horizon - len(fut)), mode="edge")

            # Simulate SSM recurrent state over window w
            h = np.zeros(self.state_dim)
            for val in w:
                h = self.A_ * h + (self.B_[:, 0] * float(val))

            anchor = float(w[-1])
            c_h = self.C_ @ h
            c_scalar = float(c_h[0]) if hasattr(c_h, "__len__") else float(c_h)
            base_pred = c_scalar * np.ones(horizon) + anchor
            residual = fut - base_pred

            X_states.append(h)
            Y_targets.append(residual)

        X_mat = np.stack(X_states, axis=0)
        Y_mat = np.stack(Y_targets, axis=0)

        # Ridge regression for residual correction mapping: h -> residual
        XtX = X_mat.T @ X_mat
        diag_idx = np.arange(XtX.shape[0])
        XtX[diag_idx, diag_idx] += self.alpha
        XtY = X_mat.T @ Y_mat
        self.W_res_ = np.linalg.solve(XtX, XtY)

        return self

    def predict(self, hist: np.ndarray, horizon: int) -> np.ndarray:
        history = np.asarray(hist, dtype=float).ravel()
        if len(history) >= self.input_length:
            w = history[-self.input_length:]
        else:
            w = np.pad(history, (self.input_length - len(history), 0), mode="edge")

        # Simulate SSM state on history
        h = np.zeros(self.state_dim)
        for val in w:
            h = self.A_ * h + (self.B_[:, 0] * float(val))

        anchor = float(w[-1])
        c_h = self.C_ @ h
        c_scalar = float(c_h[0]) if hasattr(c_h, "__len__") else float(c_h)
        base_pred = c_scalar * np.ones(horizon) + anchor

        # Residual correction from SSM latent state
        res_pred = h @ self.W_res_

        final_pred = base_pred + res_pred
        return np.asarray(final_pred, dtype=float).ravel()[:horizon]

def fit_state_space_hybrid(train, H):
    m = StateSpaceDictionaryHybrid(input_length=96, state_dim=16)
    m.fit(train, H)
    return m

def pred_state_space_hybrid(model, hist):
    return model.predict(hist, model.horizon_)
