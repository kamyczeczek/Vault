"""SubbandBigDict — Hybrid Subband Filter-Bank ELM for the benchmark suite.
Decomposes series into SWT subbands (cA, d1, d2), applies multi-scale filter bank to each subband independently, concatenates feature dictionaries, and trains per-horizon Ridge with anchoring.
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

def _causal_ma(x, win):
    if win <= 1:
        return x.copy()
    c = np.cumsum(np.concatenate([[0.0], x]))
    out = np.empty_like(x)
    for i in range(len(x)):
        s = max(0, i - win + 1)
        out[i] = (c[i+1] - c[s]) / (i - s + 1)
    return out

def _ema(x, alpha):
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i-1]
    return out

class SubbandBigDict:
    def __init__(self, input_length=96, wavelet="db4", levels=2, alpha=100.0, seed=42):
        self.input_length = int(input_length)
        self.wavelet = wavelet
        self.levels = int(levels)
        self.alpha = float(alpha)
        self.seed = int(seed)
        self._fitted = False

    def _extract_features(self, xa: np.ndarray) -> np.ndarray:
        L = len(xa)
        feats = [xa]
        # Filter bank on xa
        for w in (3, 6, 12, 24):
            feats.append(_causal_ma(xa, w))
        for a in (0.3, 0.7):
            feats.append(_ema(xa, a))
        d1 = np.concatenate([[0.0], np.diff(xa)])
        feats.append(d1)
        d2 = np.concatenate([[0.0], np.diff(d1)])
        feats.append(d2)

        # Subbands via SWT
        try:
            coeffs = pywt.swt(xa, self.wavelet, level=self.levels)
            for lev_idx in range(self.levels):
                cA, cD = coeffs[lev_idx]
                if len(cA) == L:
                    feats.append(cA.astype(float))
                    # Apply MA to subbands as well
                    for w in (3, 12):
                        feats.append(_causal_ma(cA.astype(float), w))
                if len(cD) == L:
                    feats.append(cD.astype(float))
                    for w in (3, 12):
                        feats.append(_causal_ma(cD.astype(float), w))
        except Exception:
            pass

        return np.concatenate(feats)

    def fit(self, train: np.ndarray, horizon: int):
        L = self.input_length
        n = len(train)
        ends = np.arange(L, n - horizon + 1)
        if len(ends) == 0:
            ends = np.arange(L, n)
            horizon = min(horizon, n - L)

        X_list = []
        Y_list = []
        for e in ends:
            w = train[e-L:e]
            a = float(w[-1])
            xa = w - a
            feat = self._extract_features(xa)
            X_list.append(feat)
            Y_list.append(train[e:e+horizon] - a)

        X = np.stack(X_list)
        Y = np.stack(Y_list)

        # RFF non-linear projection
        rng = np.random.default_rng(self.seed)
        D0 = X.shape[1]
        h_dict = 256
        Wr = rng.standard_normal((D0, h_dict)) / np.sqrt(D0)
        b = rng.uniform(0, 2 * np.pi, h_dict)
        phi_rand = np.cos(X @ Wr + b)

        Phi = np.hstack([X, phi_rand])
        self.W_ = _ridge_multioutput(Phi, Y, self.alpha)
        self.Wr_ = Wr
        self.b_ = b
        self._fitted = True
        return self

    def predict_hist(self, hist: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Model not fitted")
        w = hist[-self.input_length:]
        a = float(w[-1])
        xa = w - a
        X = self._extract_features(xa)[None, :]
        phi_rand = np.cos(X @ self.Wr_ + self.b_)
        Phi = np.hstack([X, phi_rand])
        delta = (Phi @ self.W_)[0]
        return delta + a
