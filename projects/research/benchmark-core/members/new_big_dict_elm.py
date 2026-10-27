"""NewBigDictELM v2 — Standalone diverse-activation ELM with configurable output anchoring.

Key independence from NLinear:
- Input features use RAW window values, not NLinear-style last-value subtraction
- Anchor is applied only at OUTPUT stage (predicted delta + anchor)
- No dependence on NLinear preprocessing pipeline
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

def _ema(x, alpha):
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i-1]
    return out

def _filter_bank_one(xa: np.ndarray, *, wavelet_bank=("db4","sym4"), levels=2, use_packet=False, packet_depth=2):
    L = len(xa)
    feats = []
    feats.append(xa)
    for w in (3, 6, 12, 24):
        feats.append(_causal_ma(xa, w))
    for a in (0.3, 0.7):
        feats.append(_ema(xa, a))
    d1 = np.concatenate([[0.0], np.diff(xa)])
    feats.append(d1)
    d2 = np.concatenate([[0.0], np.diff(d1)])
    feats.append(d2)
    ma12 = _causal_ma(xa, 12)
    ma24 = _causal_ma(xa, 24)
    feats.append(xa - ma12)
    feats.append(xa - ma24)
    if _HAS_PYWT:
        for wav in wavelet_bank:
            try:
                coeffs = pywt.swt(xa, wav, level=levels)
                for lev_idx in range(levels):
                    cA, cD = coeffs[lev_idx]
                    if len(cA) == L:
                        feats.append(cA.astype(float))
                    if len(cD) == L:
                        feats.append(cD.astype(float))
            except Exception:
                continue
    return feats

class NewBigDictELM:
    """Standalone BigDictELM with configurable output anchoring, independent from NLinear."""
    def __init__(
        self,
        input_length=96,
        hidden=384,
        act_type="hybrid",  # 'cos', 'rbf', 'hybrid', 'multi_family'
        rbf_gamma_scale=1.0,
        alpha=100.0,
        alpha_grid=(30, 100, 300),
        wavelet_bank=("db4", "sym4"),
        levels=2,
        anchor="last",      # 'last', 'first', 'mean', 'none'
        use_packet=False,
        packet_depth=2,
        seed=42,
    ):
        self.input_length = int(input_length)
        self.hidden = int(hidden)
        self.act_type = act_type
        self.rbf_gamma_scale = float(rbf_gamma_scale)
        self.alpha = float(alpha)
        self.alpha_grid = alpha_grid
        self.wavelet_bank = wavelet_bank
        self.levels = int(levels)
        self.anchor = anchor
        self.use_packet = bool(use_packet)
        self.packet_depth = int(packet_depth)
        self.seed = int(seed)
        self._fitted = False

    def _bank(self, xa):
        return _filter_bank_one(
            xa,
            wavelet_bank=self.wavelet_bank,
            levels=self.levels,
            use_packet=self.use_packet,
            packet_depth=self.packet_depth,
        )

    def _get_anchor(self, window):
        """Compute anchor value from window based on strategy."""
        window = np.asarray(window, dtype=float).ravel()
        if self.anchor == "last":
            return float(window[-1])
        elif self.anchor == "first":
            return float(window[0])
        elif self.anchor == "mean":
            return float(np.mean(window))
        elif self.anchor == "none":
            return 0.0
        else:
            raise ValueError(f"Unknown anchor: {self.anchor}")

    def _create_phi_transform(self, Xs, centers_data=None, rng=None):
        D0 = Xs.shape[1]
        stride = max(1, D0 // 64)
        idx = np.arange(0, D0, stride)[:64]
        scale = 1.0 / np.sqrt(D0)

        if self.act_type == "cos":
            if centers_data is None:
                Wr = rng.standard_normal((D0, self.hidden)) * scale
                b = rng.uniform(0, 2 * np.pi, size=self.hidden)
                model_params = ("cos", Wr, b, idx)
            else:
                _, Wr, b, _ = centers_data
                model_params = centers_data

            def phi_fn(X):
                p_cos = np.cos(X @ Wr + b)
                return np.concatenate([X, p_cos, X[:, idx]**2], axis=1)

        elif self.act_type == "rbf":
            if centers_data is None:
                c_idx = rng.choice(len(Xs), size=min(self.hidden, len(Xs)), replace=False)
                centers = Xs[c_idx]
                gamma = self.rbf_gamma_scale / (2.0 * D0)
                model_params = ("rbf", centers, gamma, idx)
            else:
                _, centers, gamma, _ = centers_data
                model_params = centers_data

            def phi_fn(X):
                x_sq = np.sum(X**2, axis=1, keepdims=True)
                c_sq = np.sum(centers**2, axis=1, keepdims=True).T
                d_sq = x_sq + c_sq - 2.0 * (X @ centers.T)
                rbf = np.exp(-gamma * np.maximum(0.0, d_sq))
                return np.concatenate([X, rbf, X[:, idx]**2], axis=1)

        elif self.act_type == "hybrid":
            h_half = self.hidden // 2
            if centers_data is None:
                Wr = rng.standard_normal((D0, h_half)) * scale
                b = rng.uniform(0, 2 * np.pi, size=h_half)
                c_idx = rng.choice(len(Xs), size=min(h_half, len(Xs)), replace=False)
                centers = Xs[c_idx]
                gamma = self.rbf_gamma_scale / (2.0 * D0)
                model_params = ("hybrid", Wr, b, centers, gamma, idx)
            else:
                _, Wr, b, centers, gamma, _ = centers_data
                model_params = centers_data

            def phi_fn(X):
                p_cos = np.cos(X @ Wr + b)
                x_sq = np.sum(X**2, axis=1, keepdims=True)
                c_sq = np.sum(centers**2, axis=1, keepdims=True).T
                d_sq = x_sq + c_sq - 2.0 * (X @ centers.T)
                rbf = np.exp(-gamma * np.maximum(0.0, d_sq))
                return np.concatenate([X, p_cos, rbf, X[:, idx]**2], axis=1)

        elif self.act_type == "multi_family":
            h_quart = max(1, self.hidden // 4)
            if centers_data is None:
                Wr_cos = rng.standard_normal((D0, h_quart)) * scale
                b_cos = rng.uniform(0, 2 * np.pi, size=h_quart)
                c_idx = rng.choice(len(Xs), size=min(h_quart, len(Xs)), replace=False)
                centers = Xs[c_idx]
                gamma = self.rbf_gamma_scale / (2.0 * D0)
                Wr_tanh = rng.standard_normal((D0, h_quart)) * scale
                b_tanh = rng.standard_normal(h_quart) * 0.1
                Wr_mish = rng.standard_normal((D0, h_quart)) * scale
                b_mish = rng.standard_normal(h_quart) * 0.1
                model_params = ("multi_family", Wr_cos, b_cos, centers, gamma, Wr_tanh, b_tanh, Wr_mish, b_mish, idx)
            else:
                _, Wr_cos, b_cos, centers, gamma, Wr_tanh, b_tanh, Wr_mish, b_mish, _ = centers_data
                model_params = centers_data

            def phi_fn(X):
                p_cos = np.cos(X @ Wr_cos + b_cos)
                x_sq = np.sum(X**2, axis=1, keepdims=True)
                c_sq = np.sum(centers**2, axis=1, keepdims=True).T
                d_sq = x_sq + c_sq - 2.0 * (X @ centers.T)
                rbf = np.exp(-gamma * np.maximum(0.0, d_sq))
                p_tanh = np.tanh(X @ Wr_tanh + b_tanh)
                z_mish = X @ Wr_mish + b_mish
                p_mish = z_mish * np.tanh(np.log1p(np.exp(np.clip(z_mish, -20, 20))))
                return np.concatenate([X, p_cos, rbf, p_tanh, p_mish, X[:, idx]**2], axis=1)

        else:
            raise ValueError(f"Unknown act_type: {self.act_type}")

        return phi_fn, model_params

    def fit(self, y, *, horizon: int):
        series = np.asarray(y, dtype=float).ravel()
        L = self.input_length
        H = int(horizon)
        n = len(series)
        if n < L + H:
            raise ValueError(f"series too short {n} < {L+H}")

        # Build windows and targets
        ends = np.arange(L, n - H + 1)
        # Use RAW window values for features (no NLinear-style subtraction)
        flats = [
            np.concatenate(self._bank(series[e - L:e])).astype(float)
            for e in ends
        ]
        X0 = np.stack(flats)

        # Targets: predict delta from anchor, then add anchor back
        Y = np.stack([series[e:e + H] - self._get_anchor(series[e - L:e]) for e in ends])

        # Hyperparameter search via 15% val split
        alpha_cands = list(self.alpha_grid) if self.alpha_grid is not None else [self.alpha]
        if len(alpha_cands) > 1 and len(X0) > 50:
            n_val = max(1, len(X0) // 7)
            Xtr, Ytr = X0[:-n_val], Y[:-n_val]
            Xva, Yva = X0[-n_val:], Y[-n_val:]

            mu = Xtr.mean(axis=0)
            sd = Xtr.std(axis=0)
            sd[sd < 1e-8] = 1.0
            Xtrs = (Xtr - mu) / sd
            Xvas = (Xva - mu) / sd

            rng = np.random.default_rng(self.seed)
            phi_fn_val, _ = self._create_phi_transform(Xtrs, rng=rng)
            Phi_tr = phi_fn_val(Xtrs)
            Phi_va = phi_fn_val(Xvas)

            best_a = self.alpha
            best_err = float("inf")
            for a in alpha_cands:
                W = _ridge_multioutput(Phi_tr, Ytr, float(a))
                pred = Phi_va @ W
                err = float(np.mean((pred - Yva)**2))
                if err < best_err:
                    best_err = err
                    best_a = a
            chosen_alpha = float(best_a)
        else:
            chosen_alpha = float(self.alpha)

        # Refit on full dataset
        mu = X0.mean(axis=0)
        sd = X0.std(axis=0)
        sd[sd < 1e-8] = 1.0
        Xs = (X0 - mu) / sd

        rng = np.random.default_rng(self.seed)
        phi_fn_full, model_params = self._create_phi_transform(Xs, rng=rng)
        Phi = phi_fn_full(Xs)

        self.mu_ = mu
        self.sd_ = sd
        self.phi_params_ = model_params
        self.D0_ = Xs.shape[1]
        self.Phi_dim_ = Phi.shape[1]
        self.W_ = _ridge_multioutput(Phi, Y, chosen_alpha)
        self.alpha_chosen_ = chosen_alpha
        self.H_ = H
        self.history_ = series
        self._fitted = True
        return self

    def predict_hist(self, hist):
        if not self._fitted:
            raise RuntimeError("fit first")
        hist = np.asarray(hist, dtype=float).ravel()
        L = self.input_length
        if len(hist) < L:
            hist = np.pad(hist, (L - len(hist), 0), mode="edge")
        else:
            hist = hist[-L:]

        anchor_val = self._get_anchor(hist)
        flat = np.concatenate(self._bank(hist)).astype(float)
        xs = ((flat - self.mu_) / self.sd_)[None, :]
        phi_fn, _ = self._create_phi_transform(xs, centers_data=self.phi_params_)
        phi = phi_fn(xs)

        pred = phi @ self.W_
        return pred[0] + anchor_val

    def predict(self):
        return self.predict_hist(self.history_[-self.input_length:])
