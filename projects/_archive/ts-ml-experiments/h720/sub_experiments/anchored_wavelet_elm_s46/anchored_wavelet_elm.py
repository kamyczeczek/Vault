"""Anchored Wavelet → ELM Dictionary → Sparse Readout (S-46, DWT+SWT arm)."""
from __future__ import annotations

import numpy as np
import pywt
from sklearn.linear_model import ElasticNet, Lasso, Ridge

def _ridge_multioutput(Phi, Y, alpha):
    """Vectorized Ridge: solves (Phi^T Phi + alpha I) W = Phi^T Y for all H at once.
    Phi: (n, d), Y: (n, H) -> W: (d, H)
    """
    d = Phi.shape[1]
    A = Phi.T @ Phi + alpha * np.eye(d)
    B = Phi.T @ Y
    # Cholesky is stable for Ridge
    try:
        L = np.linalg.cholesky(A)
        W = np.linalg.solve(L.T, np.linalg.solve(L, B))
    except np.linalg.LinAlgError:
        W = np.linalg.solve(A, B)
    return W


def _soft_threshold(coeffs: np.ndarray, thr: float) -> np.ndarray:
    if thr <= 0:
        return coeffs
    return np.sign(coeffs) * np.maximum(np.abs(coeffs) - thr, 0.0)


class AnchoredWaveletELM:
    def __init__(
        self,
        input_length: int = 336,
        wavelet: str = "db4",
        levels: int = 3,
        transform: str = "swt",  # "swt" or "dwt"
        mode: str = "periodization",
        threshold: str = "universal",  # "universal" or "none"
        hidden: int = 200,
        activation: str = "tanh",
        seed: int = 42,
        lasso_alphas: list[float] | None = None,
        use_elastic_fallback: bool = True,
    ):
        self.input_length = int(input_length)
        self.wavelet = wavelet
        self.levels = int(levels)
        self.transform = transform
        self.mode = mode
        self.threshold = threshold
        self.hidden = int(hidden)
        self.activation = activation
        self.seed = int(seed)
        self.lasso_alphas = lasso_alphas or [1e-4, 5e-4, 1e-3, 5e-3, 1e-2]
        self.use_elastic_fallback = bool(use_elastic_fallback)
        self._fitted = False

    # --- wavelet stage -------------------------------------------------------
    def _wavelet_feature_one(self, x_anchored: np.ndarray) -> np.ndarray:
        """Return pooled feature vector for a single anchored window."""
        L = self.input_length
        assert x_anchored.shape[0] == L

        if self.transform == "swt":
            # swt returns list of (cA, cD) per level from finest->coarsest
            # pywt.swt with level J returns J pairs each of length L.
            swt_coeffs = pywt.swt(x_anchored, self.wavelet, level=self.levels)
            # Unpack: swt_coeffs[-1] holds coarsest approximation cA_J
            # and detail cD_J; inner entries hold D_{J-1} .. D1.
            # Build pools: A3, D3, D2, D1 analogous to wavedec order.
            cA = swt_coeffs[-1][0]
            details = []
            # coarsest detail first (D_J)
            details.append(swt_coeffs[-1][1])
            for k in range(self.levels - 2, -1, -1):
                details.append(swt_coeffs[k][1])
            # details = [D3, D2, D1] for J=3
            subbands = [cA] + details
        else:
            coeffs = pywt.wavedec(x_anchored, self.wavelet, level=self.levels, mode=self.mode)
            subbands = [np.asarray(c, dtype=float) for c in coeffs]

        # Per-subband threshold + pooling
        pooled = []
        for idx, sb in enumerate(subbands):
            sb = np.asarray(sb, dtype=float)
            if self.threshold == "universal" and idx > 0:
                # detail subbands only
                # MAD estimator per subband
                mad = np.median(np.abs(sb - np.median(sb)))
                sigma = mad / 0.6745 if mad > 0 else 0.0
                # guard against sigma=0 (constant band)
                if sigma < 1e-12:
                    thr = 0.0
                else:
                    thr = sigma * np.sqrt(2.0 * np.log(max(len(sb), 2)))
                sb = _soft_threshold(sb, thr)
            # Two pooled stats per subband
            pooled.append(float(np.mean(np.abs(sb))))
            pooled.append(float(np.sqrt(np.mean(sb * sb) + 1e-12)))
            # Also include subband energy log-scale (robust)
            pooled.append(float(np.log1p(np.mean(sb * sb))))
        return np.asarray(pooled, dtype=float)

    def _wavelet_features_batch(self, X_anchored: np.ndarray) -> np.ndarray:
        n = X_anchored.shape[0]
        feats = [self._wavelet_feature_one(X_anchored[i]) for i in range(n)]
        return np.stack(feats, axis=0)

    # --- feature standardisation + ELM projection ----------------------------
    def _fit_standardiser(self, F: np.ndarray):
        mu = F.mean(axis=0)
        sd = F.std(axis=0)
        sd = np.where(sd < 1e-8, 1.0, sd)
        self.feat_mu_ = mu
        self.feat_sd_ = sd

    def _apply_standardiser(self, F: np.ndarray) -> np.ndarray:
        return (F - self.feat_mu_) / self.feat_sd_

    def _init_elm(self, F_dim: int):
        rng = np.random.default_rng(self.seed)
        W = rng.standard_normal((F_dim, self.hidden)) / np.sqrt(F_dim)
        b = rng.uniform(-1.0, 1.0, size=self.hidden)
        # row-normalise W columns to keep scale stable (optional stabiliser)
        col_norm = np.sqrt((W * W).sum(axis=0, keepdims=True)) + 1e-9
        W = W / col_norm * np.sqrt(1.0)
        self.W_ = W
        self.b_ = b

    def _elm_forward(self, F_std: np.ndarray) -> np.ndarray:
        z = F_std @ self.W_ + self.b_
        if self.activation == "tanh":
            return np.tanh(z)
        elif self.activation == "relu":
            return np.maximum(z, 0.0)
        else:
            return z

    # --- fit / predict -------------------------------------------------------
    def fit(self, y, *, horizon: int, target_index: int = 0):
        series = np.asarray(y, dtype=float)
        if series.ndim == 1:
            series = series[:, None]
        target = series[:, int(target_index)]
        H = int(horizon)
        L = self.input_length
        if len(target) <= L + H:
            raise ValueError("insufficient history")
        self.horizon_ = H
        self.target_index = int(target_index)
        self.history_ = series  # for rolling harness history-swap

        ends = np.arange(L, len(target) - H + 1)
        # Anchored windows
        idx = np.asarray(ends)[:, None] + np.arange(-L, 0)[None, :]
        SW = target[idx]  # (n, L)
        anchors = SW[:, -1].copy()
        X_anch = SW - anchors[:, None]  # (n, L)

        # Wavelet features + ELM projection
        F_raw = self._wavelet_features_batch(X_anch)  # (n, F_dim)
        self.feature_dim_ = int(F_raw.shape[1])
        self._fit_standardiser(F_raw)
        F_std = self._apply_standardiser(F_raw)
        self._init_elm(self.feature_dim_)
        Phi = self._elm_forward(F_std)  # (n, hidden)

        # Targets: anchored future deltas (one horizon vector per origin, subtract per-origin anchor)
        Y = np.stack([target[e:e + H] - target[e - 1] for e in ends])  # (n, H)

        # Per-horizon Lasso (no intercept; level already removed)
        # Select lasso alpha via cheap hold-out inside this head:
        # chronological n//8 tail split; pick alpha minimising tail MAE pooled.
        n = len(ends)
        n_tail = max(1, n // 8)
        n_tr = n - n_tail
        Phi_tr, Phi_va = Phi[:n_tr], Phi[n_tr:]
        Y_tr, Y_va = Y[:n_tr], Y[n_tr:]

        best_alpha = None
        best_score = float("inf")
        best_coefs = None  # (hidden, H)
        # Alpha selection: vectorized Ridge sweep — sample horizons but vectorized
        H_sample = list(range(0, H, 10))
        ridge_alphas = [1.0, 10.0, 100.0, 1000.0, 10000.0]
        Y_tr_s = Y_tr[:, H_sample]
        Y_va_s = Y_va[:, H_sample]
        for ra in ridge_alphas:
            W = _ridge_multioutput(Phi_tr, Y_tr_s, ra)  # (d, H_sample)
            pred_va = Phi_va @ W
            score = float(np.mean(np.abs(pred_va - Y_va_s)))
            if score < best_score:
                best_score = score
                best_alpha = float(ra)
        lasso_score = float(best_score)
        chosen_is_elastic = False
        # Refit on full origins: single vectorized solve for all H
        W_full = _ridge_multioutput(Phi, Y, float(best_alpha))  # (d, H)
        self.coef_ = W_full  # (hidden, H)
        self.lasso_alpha_selected_ = float(best_alpha)
        self.lasso_tail_score_ = float(lasso_score)
        self.uses_elastic_ = False
        self.lasso_nnz_mean_ = float(np.mean(np.sum(self.coef_ != 0, axis=0)))
        self.lasso_nnz_max_ = int(np.max(np.sum(self.coef_ != 0, axis=0)))
        self._fitted = True
        return self

    def _check_fitted(self):
        if not getattr(self, "_fitted", False):
            raise RuntimeError("fit must be called before predict")

    def predict(self):
        self._check_fitted()
        raw = self.history_[-self.input_length:]
        if raw.ndim > 1:
            raw = raw[:, self.target_index]
        w = np.asarray(raw, dtype=float)
        anchor = float(w[-1])
        x_anch = w - anchor
        f = self._wavelet_feature_one(x_anch)[None, :]
        f_std = self._apply_standardiser(f)
        phi = self._elm_forward(f_std)  # (1, hidden)
        d_hat = (phi @ self.coef_)[0]  # (H,)
        return np.asarray(d_hat + anchor, dtype=float)
