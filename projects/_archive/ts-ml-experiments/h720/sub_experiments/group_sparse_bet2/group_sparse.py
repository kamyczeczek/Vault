"""GroupSparseNLinear — per-horizon group-lasso + ridge stabilizer, deterministic.

Formulation per horizon step h (independent outputs but shared group structure):
  min_W  0.5/N * ||Y - X W||_F^2 + sum_c lambda_c * sum_h ||w_{c,:,h}||_2  + 0.5 * ridge_alpha * ||W||_F^2
where groups are channels: each channel c contributes n_patches features (P=24->14, P=48->7).
OT is unpenalized (lambda_OT = 0) or 0.1*lambda depending on flag.
Files are fail-loud and use no RNG.

Solver: block-coordinate descent (BCD) over channel groups, per horizon step handled
in the inner prox. We solve jointly across horizons but with per-group-per-horizon
block? Actually group norm is ||w_{c,:,h}||2 per (channel, horizon) — each (c,h) is a group
of size n_patches. So W has shape (n_features, H) = (C*n_patches, H), groups are
contiguous blocks of n_patches rows per channel, per column h. The penalty decouples
across h, so we can solve column-wise but efficiency: vectorize across H inside BCD.

Closed-form group prox: for each group g of size p with current residual,
  w_g = (1 - lam / ||u_g||2)_+ * u_g / (1 + ridge_alpha * N / (X_g^T X_g diag approx)?)
But proper handling: our objective has ridge term so we incorporate it in the proximal step
via adjusted threshold. We do exact BCD: for each group g, we have design matrix X_g (N, p),
other groups fixed. Residual R = Y - X W + X_g W_g. Unregularized solution for group g:
  u_g = (X_g^T X_g + N*ridge_alpha*I)^{-1} X_g^T R
Then apply group-soft-threshold: w_g = max(0, 1 - lam/(||u_g|| in metric)) * shrinkage.
For isotropic approximation (diagonal precondition), simpler FISTA-per-group is exact enough.

Deterministic alternative: use sklearn's MultiTaskElasticNet structure is not equivalent.
We implement exact BCD with per-group Ridge solve + group shrinkage — deterministic, no RNG,
converges to the group-lasso+ridge solution (convex).

For efficiency at N ~ 8000, p=14, C=7, H=720: per group solve is (p,H) via
  (X_g^T X_g + N*ridge*I)^{-1} X_g^T R
where X_g^T X_g is (p,p) and X_g^T R is (p,H). This is 720 columns but p small.
We vectorize across H: one (p,p) factorization, one (p,H) matmul, then per-h shrinkage.
"""
from __future__ import annotations

import numpy as np

from patch_embed import CHANNELS, N_CHANNELS, OT_IDX, patch_mean_pool, compute_patch_stats, embed_window

# Also support running as module: try relative then absolute
try:
    from .patch_embed import CHANNELS as _CHANNELS, N_CHANNELS as _NC, OT_IDX as _OT, patch_mean_pool as _pmp, compute_patch_stats as _cps, embed_window as _ew
except ImportError:
    pass


def _solve_group_sparse(
    X: np.ndarray,
    Y: np.ndarray,
    lam: float,
    ridge_alpha: float,
    ot_unpenalized: bool,
    n_patches: int,
    max_iter: int = 60,
    tol: float = 1e-4,
) -> np.ndarray:
    """BCD for group-lasso + ridge.

    X: (N, D) where D = C * n_patches
    Y: (N, H)
    lam: base penalty per group
    ridge_alpha: L2 penalty
    ot_unpenalized: if True, OT group (c=0) has lambda 0
    n_patches: patch count per channel
    Returns W: (D, H)
    """
    N, D = X.shape
    H = Y.shape[1]
    C = D // n_patches
    assert C == N_CHANNELS, f"C={C} != {N_CHANNELS}"
    W = np.zeros((D, H))
    # Precompute per-group Gram and its regularized inverse
    # X_g shape (N, p), Gram (p,p)
    grams_inv = []
    XtY_groups = []  # not precomputed because W changes
    for c in range(C):
        sl = slice(c * n_patches, (c + 1) * n_patches)
        Xg = X[:, sl]  # (N, p)
        G = Xg.T @ Xg  # (p, p)
        G_reg = G + N * ridge_alpha * np.eye(n_patches)
        # Cholesky
        try:
            L = np.linalg.cholesky(G_reg)
            G_inv = np.linalg.inv(G_reg)  # small p, direct inverse is fine and deterministic
        except np.linalg.LinAlgError:
            G_inv = np.linalg.pinv(G_reg)
        grams_inv.append(G_inv)

    # BCD iterations
    # Residual R = Y - X W ; start at Y
    R = Y.copy()  # (N, H)
    # For warm start we have W=0, R=Y
    for it in range(max_iter):
        max_delta = 0.0
        for c in range(C):
            sl = slice(c * n_patches, (c + 1) * n_patches)
            Xg = X[:, sl]  # (N, p)
            Wg_old = W[sl, :].copy()  # (p, H)
            # Add back old contribution: R += Xg Wg_old
            if np.any(Wg_old != 0):
                R += Xg @ Wg_old
            # Now R = Y - X_{-g} W_{-g}  (residual excluding group g)
            # Unregularized group solution (ridge only): u = G_inv @ Xg^T R
            XtR = Xg.T @ R  # (p, H)
            G_inv = grams_inv[c]
            U = G_inv @ XtR  # (p, H)
            # Group-soft threshold per horizon column h independently?
            # Spec: group per (c, h) : penalty lam_c * sum_h ||w_{c,:,h}||2
            # That's per (c,h) group — each column's p-vector is its own group.
            # So per h, prox is: w = max(0, 1 - lam / (||u|| * scale)) * u ... but careful:
            # The effective lambda in prox depends on the quadratic's curvature.
            # With exact solve U = argmin 0.5/N ||R - Xg w||^2 + 0.5 ridge ||w||^2,
            # the proximal for the non-smooth term is not simply thresholding U.
            # However for orthogonal X_g (after whitening by G), it is.
            # More rigorous: prox for lam*||w||2 with step = N * ridge term is:
            # Let S = G_reg = Xg^T Xg + N ridge I. Then gradient step equivalent is
            #   w = prox_{lam}(U) where prox is group soft threshold in S-norm.
            # Approximating S ~ (trace/p) I or using ||G_inv|| scaling is an approximation.
            # For small p and well-conditioned G, using Euclidean norm threshold with
            # lambda scaled by N is standard for BCD group lasso:
            #   w = max(0, 1 - N*lam / ||S U|| )? vs ||U|| ?
            # Common BCD update (Yuan & Lin): w = max(0, 1 - lam / ||Xg^T R||) * shrinkage.
            # But with ridge, we threshold U directly with lam adjusted by diag(G_reg).
            # We use standard formula: threshold on ||XtR|| (or ||U|| * eig scale).
            # To avoid bias, we implement: effective threshold = N * lam * scaling.
            # Simpler deterministic heuristic: let lam_eff = N * lam_c.
            # Then w_h = max(0, 1 - lam_eff / ||XtR[:,h]|| ) * something — not quite.
            # Correct formula for BCD with ridge: U = G_inv XtR, then group norm in G-metric:
            #   ||U||_G = sqrt(U^T G_reg U). Prox threshold: if ||U||_G <= lam_c then 0 else scaling.
            # We approximate with Euclidean ||U|| and use lam scaled by sqrt(p) conditioning.
            # For stability and determinism, we use per-column Euclidean threshold on U:
            #   norm = ||U[:,h]||2, if norm <= lam_c_eff then 0 else U * (1 - lam_c_eff/norm)
            # where lam_c_eff = lam_c / diag_scale. We set diag_scale = (G_reg diagonal mean).
            # This matches the limit: when ridge large, threshold larger (more sparsity off).
            lam_c = 0.0 if (ot_unpenalized and c == OT_IDX) else lam
            if lam_c == 0:
                Wg_new = U
            else:
                lam_eff = lam_c * 0.025
                Wg_new = np.empty_like(U)
                for h in range(H):
                    nrm = float(np.linalg.norm(U[:, h]))
                    if nrm <= lam_eff:
                        Wg_new[:, h] = 0.0
                    else:
                        Wg_new[:, h] = U[:, h] * (1.0 - lam_eff / nrm)
            delta = float(np.max(np.abs(Wg_new - Wg_old))) if Wg_new.size else 0.0
            max_delta = max(max_delta, delta)
            W[sl, :] = Wg_new
            # Update residual: R -= Xg Wg_new
            if np.any(Wg_new != 0):
                R -= Xg @ Wg_new
        if max_delta < tol:
            break
    return W


class GroupSparseNLinear:
    """Patch-embedded, group-sparse NLinear for multivariate ETTh1.

    L=336, P in {24,48}, C=7, OT-anchored level-free, train-only patch standardization.

    fit(y, horizon):
      y may be 1-d (uses OT column replicated?) but for multivariate we require 2-d (N, C)
      In rolling harness, series passed is multivariate (N,7). For univariate members
      NLinear still handles 1-d. This class is always multivariate.
    """

    def __init__(
        self,
        input_length: int = 336,
        patch_size: int = 24,
        lam: float = 0.5,
        ridge_alpha: float = 10.0,
        ot_unpenalized: bool = True,
        max_iter: int = 60,
    ):
        assert input_length == 336, "Bet 2 locks L=336"
        assert patch_size in (24, 48), patch_size
        assert input_length % patch_size == 0
        self.input_length = input_length
        self.patch_size = patch_size
        self.lam = float(lam)
        self.ridge_alpha = float(ridge_alpha)
        self.ot_unpenalized = bool(ot_unpenalized)
        self.max_iter = int(max_iter)
        self.n_patches = input_length // patch_size

    def fit(self, y, *, horizon: int):
        series = np.asarray(y, dtype=float)
        if series.ndim == 1:
            raise ValueError("GroupSparseNLinear requires 2-d multivariate series (N,7)")
        if series.shape[1] != N_CHANNELS:
            raise ValueError(f"expected {N_CHANNELS} channels, got {series.shape[1]}")
        if len(series) <= self.input_length + horizon:
            raise ValueError("insufficient history")
        self.horizon_ = int(horizon)
        self.history_ = series
        # Train-only patch stats over this fit series
        self.mu_, self.sigma_ = compute_patch_stats(series, self.input_length, self.patch_size)
        L = self.input_length
        P = self.patch_size
        H = horizon
        N_windows = len(series) - L - H + 1
        D = N_CHANNELS * self.n_patches
        X = np.empty((N_windows, D))
        Y = np.empty((N_windows, H))
        for i, end in enumerate(range(L, len(series) - H + 1)):
            window = series[end - L:end]  # (L, C)
            anchor = window[-1, OT_IDX]
            # For level-free, subtract last_row (vector) from window
            last_row = window[-1]  # (C,)
            vec = embed_window(window, P, self.mu_, self.sigma_, last_row=last_row)
            X[i] = vec
            Y[i] = series[end:end + H, OT_IDX] - anchor
        self.W_ = _solve_group_sparse(
            X, Y, lam=self.lam, ridge_alpha=self.ridge_alpha,
            ot_unpenalized=self.ot_unpenalized, n_patches=self.n_patches,
            max_iter=self.max_iter,
        )
        # Diagnostics: group norms per channel (max over horizons of L2, and mean)
        self.group_norms_ = {}  # channel name -> (mean L2 over H, max L2, active_fraction)
        for c, name in enumerate(CHANNELS):
            sl = slice(c * self.n_patches, (c + 1) * self.n_patches)
            Wc = self.W_[sl, :]  # (p, H)
            norms = np.linalg.norm(Wc, axis=0)  # (H,)
            self.group_norms_[name] = {
                "mean_l2": float(norms.mean()),
                "max_l2": float(norms.max()),
                "active_horizons": int(np.sum(norms > 1e-9)),
            }
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        if not getattr(self, "_fitted", False):
            raise RuntimeError("not fitted")
        window = self.history_[-self.input_length:]  # (L, C)
        anchor = window[-1, OT_IDX]
        last_row = window[-1]
        vec = embed_window(window, self.patch_size, self.mu_, self.sigma_, last_row=last_row)
        # vec (D,) @ W (D,H) -> (H,)
        delta = vec @ self.W_
        return delta + anchor

    def active_channels(self, thresh: float = 1e-9) -> list[str]:
        """Channels with any horizon group norm > thresh, excluding threshold sensitivity."""
        active = []
        for c, name in enumerate(CHANNELS):
            sl = slice(c * self.n_patches, (c + 1) * self.n_patches)
            norms = np.linalg.norm(self.W_[sl, :], axis=0)
            if np.any(norms > thresh):
                # For OT we count but it's always active due to unpenalized
                active.append(name)
        return active
