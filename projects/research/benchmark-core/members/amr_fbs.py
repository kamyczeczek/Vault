"""Adaptive Multi-Resolution Filter-Bank Synthesis (AMR-FBS) with Spectral-Temporal Hybrid Ensembling.

Combines NLinear anchoring, dynamic multi-resolution causal filter banks, Fourier/wavelet spectral envelope modeling, and vectorized Ridge regression for robust time-series forecasting across diverse and chaotic regimes.
"""
from __future__ import annotations
import numpy as np

try:
    import pywt
    _HAS_PYWT = True
except Exception:
    _HAS_PYWT = False

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

def _causal_ma(x, win):
    if win <= 1:
        return x.copy()
    c = np.cumsum(np.concatenate([[0.0], x]))
    out = np.empty_like(x)
    for i in range(len(x)):
        s = max(0, i - win + 1)
        out[i] = (c[i+1] - c[s]) / (i - s + 1)
    return out

def _fft_envelope(xa, n_harmonics=3):
    L = len(xa)
    t = np.arange(L, dtype=float)
    fft_vals = np.fft.rfft(xa)
    freqs = np.fft.rfftfreq(L)
    if len(fft_vals) > 1:
        idx = np.argsort(np.abs(fft_vals[1:]))[::-1] + 1
        top_idx = idx[:min(n_harmonics, len(idx))]
    else:
        top_idx = [0]

    envelope = np.zeros(L, dtype=float)
    for i in top_idx:
        freq = freqs[i]
        amp = np.abs(fft_vals[i]) / L
        phase = np.angle(fft_vals[i])
        envelope += 2.0 * amp * np.cos(2.0 * np.pi * freq * t + phase)
    return envelope

class AMRFBSForecaster:
    def __init__(self, lookback=96, alpha=10.0, n_harmonics=3, hdict=256, seed=42):
        self.lookback = lookback
        self.alpha = alpha
        self.n_harmonics = n_harmonics
        self.hdict = hdict
        self.seed = seed
        self.W_ = None
        self.mu_ = None
        self.sd_ = None

    def _extract_features(self, x: np.ndarray) -> np.ndarray:
        L = len(x)
        feats = [x]
        for w in (2, 4, 8, 16, 32, 64):
            if w < L:
                feats.append(_causal_ma(x, w))

        env = _fft_envelope(x, self.n_harmonics)
        feats.append(env)
        feats.append(x - env)

        if _HAS_PYWT and L >= 16:
            try:
                coeffs = pywt.wavedec(x, 'db4', level=min(3, pywt.dwt_max_level(L, 'db4')))
                cA = coeffs[0]
                cA_resampled = np.interp(np.linspace(0, len(cA)-1, L), np.arange(len(cA)), cA)
                feats.append(cA_resampled)
            except Exception:
                pass

        F = np.column_stack(feats)
        return F

    def fit(self, train: np.ndarray, horizon: int):
        train = np.asarray(train, dtype=float)
        n = len(train)
        L = min(self.lookback, n - horizon)
        if L < 16:
            L = max(16, n // 2)

        X_list, Y_list = [], []
        for i in range(L, n - horizon + 1):
            window = train[i-L:i]
            anchor = window[-1]
            xa = window - anchor
            F = self._extract_features(xa)
            f_flat = F.reshape(-1)
            X_list.append(f_flat)
            y_future = train[i:i+horizon] - anchor
            Y_list.append(y_future)

        X = np.array(X_list)
        Y = np.array(Y_list)

        self.mu_ = X.mean(axis=0)
        self.sd_ = X.std(axis=0) + 1e-8
        X_std = (X - self.mu_) / self.sd_

        rng = np.random.RandomState(self.seed)
        D0 = X_std.shape[1]
        Wr = rng.normal(0, 1.0 / np.sqrt(D0), size=(D0, self.hdict))
        b = rng.uniform(0, 2 * np.pi, size=self.hdict)
        phi_rand = np.cos(X_std @ Wr + b)

        Phi = np.hstack([X_std, phi_rand])
        self.W_ = _ridge_multioutput(Phi, Y, self.alpha)
        return self

    def predict_hist(self, hist: np.ndarray) -> np.ndarray:
        hist = np.asarray(hist, dtype=float)
        L = min(self.lookback, len(hist))
        window = hist[-L:]
        anchor = window[-1]
        xa = window - anchor
        F = self._extract_features(xa)
        f_flat = F.reshape(-1)

        if len(f_flat) != len(self.mu_):
            if len(f_flat) < len(self.mu_):
                f_flat = np.pad(f_flat, (0, len(self.mu_) - len(f_flat)))
            else:
                f_flat = f_flat[:len(self.mu_)]

        f_std = (f_flat - self.mu_) / self.sd_
        rng = np.random.RandomState(self.seed)
        D0 = len(f_std)
        Wr = rng.normal(0, 1.0 / np.sqrt(D0), size=(D0, self.hdict))
        b = rng.uniform(0, 2 * np.pi, size=self.hdict)
        phi_rand = np.cos(f_std @ Wr + b)

        phi = np.hstack([f_std, phi_rand])
        delta_hat = phi @ self.W_
        return delta_hat + anchor

def fit_amr_fbs(train, H):
    model = AMRFBSForecaster()
    model.fit(train, H)
    return model

def pred_amr_fbs(model, hist):
    return model.predict_hist(hist)
