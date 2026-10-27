"""Anchored Reservoir Computing (ESN) member for the benchmark suite.
Applies NLinear de-anchoring, drives a sparse leaky-integrator recurrent reservoir (Echo State Network), and trains a closed-form multi-output Ridge regression readout for horizon H.
"""
from __future__ import annotations
import numpy as np
import pywt

def _ridge_multioutput(Phi, Y, alpha):
    d = Phi.shape[1]
    A = Phi.T @ Phi + alpha * np.eye(d)
    B = Phi.T @ Y
    try:
        L = np.linalg.cholesky(A)
        W = np.linalg.solve(L.T, np.linalg.solve(L, B))
    except np.linalg.LinAlgError:
        W = np.linalg.solve(A, B)
    return W

class ESNReservoir:
    def __init__(
        self,
        input_length=96,
        reservoir_size=192,
        spectral_radius=0.85,
        leak_rate=0.4,
        alpha=100.0,
        wavelet="db4",
        levels=1,
        seed=42,
    ):
        self.input_length = int(input_length)
        self.reservoir_size = int(reservoir_size)
        self.spectral_radius = float(spectral_radius)
        self.leak_rate = float(leak_rate)
        self.alpha = float(alpha)
        self.wavelet = wavelet
        self.levels = int(levels)
        self.seed = int(seed)
        self._fitted = False

    def _extract_inputs(self, xa: np.ndarray) -> np.ndarray:
        L = len(xa)
        # Combine raw de-anchored series with SWT subband if available
        inputs = [xa]
        try:
            coeffs = pywt.swt(xa, self.wavelet, level=self.levels)
            for lev in range(self.levels):
                cA, cD = coeffs[lev]
                if len(cA) == L: inputs.append(cA.astype(float))
                if len(cD) == L: inputs.append(cD.astype(float))
        except Exception:
            pass
        return np.stack(inputs, axis=1) # Shape (L, input_dim)

    def _run_reservoir(self, input_seq, W_in, W_res):
        T, input_dim = input_seq.shape
        h = np.zeros(self.reservoir_size)
        states = np.empty((T, self.reservoir_size))
        for t in range(T):
            x_t = input_seq[t]
            pre = W_in @ x_t + W_res @ h
            h = (1.0 - self.leak_rate) * h + self.leak_rate * np.tanh(pre)
            states[t] = h
        return states

    def fit(self, train: np.ndarray, horizon: int):
        L = self.input_length
        n = len(train)
        ends = np.arange(L, n - horizon + 1)
        if len(ends) == 0:
            ends = np.arange(L, n)
            horizon = min(horizon, n - L)

        # Determine input dim by probing
        sample_xa = np.zeros(L)
        sample_inputs = self._extract_inputs(sample_xa)
        input_dim = sample_inputs.shape[1]

        rng = np.random.default_rng(self.seed)
        W_in = rng.uniform(-0.5, 0.5, (self.reservoir_size, input_dim))
        W_res = rng.standard_normal((self.reservoir_size, self.reservoir_size))
        radius = max(np.abs(np.linalg.eigvals(W_res)))
        if radius > 0:
            W_res *= (self.spectral_radius / radius)

        X_list = []
        Y_list = []
        for e in ends:
            w = train[e-L:e]
            a = float(w[-1])
            xa = w - a
            input_seq = self._extract_inputs(xa)
            states = self._run_reservoir(input_seq, W_in, W_res)
            # Concatenate final state and mean state for rich temporal representation
            feat = np.concatenate([states[-1], np.mean(states, axis=0)])
            X_list.append(feat)
            Y_list.append(train[e:e+horizon] - a)

        X = np.stack(X_list)
        Y = np.stack(Y_list)

        self.W_out_ = _ridge_multioutput(X, Y, self.alpha)
        self.W_in_ = W_in
        self.W_res_ = W_res
        self._fitted = True
        return self

    def predict_hist(self, hist: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Model not fitted")
        w = hist[-self.input_length:]
        a = float(w[-1])
        xa = w - a
        input_seq = self._extract_inputs(xa)
        states = self._run_reservoir(input_seq, self.W_in_, self.W_res_)
        feat = np.concatenate([states[-1], np.mean(states, axis=0)])
        delta = (feat @ self.W_out_)
        return delta + a
