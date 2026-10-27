"""DeterministicCycleESN — Zero-randomness, structured cycle reservoir with multi-time-scale leaky integrators."""
from __future__ import annotations
import numpy as np

class DeterministicCycleESN:
    def __init__(self, input_length=96, reservoir_size=128, cycle_weight=0.85, alpha=100.0):
        self.input_length = int(input_length)
        self.reservoir_size = int(reservoir_size)
        self.cycle_weight = float(cycle_weight)
        self.alpha = float(alpha)
        self._fitted = False

    def _build_deterministic_weights(self, input_dim):
        N = self.reservoir_size
        W_res = np.zeros((N, N))
        for i in range(N):
            W_res[i, (i + 1) % N] = self.cycle_weight
        for i in range(0, N, 4):
            W_res[i, (i + 3) % N] = 0.2 * self.cycle_weight

        W_in = np.zeros((N, input_dim))
        for i in range(N):
            for d in range(input_dim):
                W_in[i, d] = np.sin(i * (d + 1) * 0.5) * 0.5

        leak_rates = np.linspace(0.05, 0.8, N)
        return W_in, W_res, leak_rates

    def _run_reservoir(self, input_seq, W_in, W_res, leak_rates):
        T, input_dim = input_seq.shape
        N = self.reservoir_size
        h = np.zeros(N)
        states = np.empty((T, N))
        for t in range(T):
            x_t = input_seq[t]
            pre = W_in @ x_t + W_res @ h
            h = (1.0 - leak_rates) * h + leak_rates * np.tanh(pre)
            states[t] = h
        return states

    def fit(self, train: np.ndarray, horizon: int):
        L = self.input_length
        n = len(train)
        ends = np.arange(L, n - horizon + 1)
        if len(ends) == 0:
            ends = np.arange(L, n)
            horizon = min(horizon, n - L)

        input_dim = 1
        W_in, W_res, leak_rates = self._build_deterministic_weights(input_dim)

        X_list = []
        Y_list = []
        for e in ends:
            w = train[e-L:e]
            a = float(w[-1])
            xa = (w - a)[:, None]
            states = self._run_reservoir(xa, W_in, W_res, leak_rates)
            feat = np.concatenate([states[-1], np.mean(states, axis=0)])
            X_list.append(feat)
            Y_list.append(train[e:e+horizon] - a)

        X = np.stack(X_list)
        Y = np.stack(Y_list)

        XtX = X.T @ X + self.alpha * np.eye(X.shape[1])
        XtY = X.T @ Y
        self.W_out_ = np.linalg.solve(XtX, XtY)
        self.W_in_ = W_in
        self.W_res_ = W_res
        self.leak_rates_ = leak_rates
        self._fitted = True
        return self

    def predict_hist(self, hist: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Model not fitted")
        w = hist[-self.input_length:]
        a = float(w[-1])
        xa = (w - a)[:, None]
        states = self._run_reservoir(xa, self.W_in_, self.W_res_, self.leak_rates_)
        feat = np.concatenate([states[-1], np.mean(states, axis=0)])
        delta = (feat @ self.W_out_)
        return delta + a
