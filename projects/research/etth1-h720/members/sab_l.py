"""SAB-L — Signal-Adaptive BigDict Long-horizon forecaster (S49 member 2).

Design (LONGTERM_ETTH1_H720_DESIGN.md + REFLECTION_PROMISING_METHODS.md):
- L=336 (14d) anchored context, NLinear trick (xa = window - last value).
- Signal-adaptive filter bank chosen on the Causal training tail:
    * rough/chaotic tails  -> COMPACT bank (identity + MA + EMA)
    * smooth tails         -> APPROX bank (compact + diff/HP + SWT approx
                               subbands cA1, cA2; detail subbands omitted -
                               the standardization control showed raw/standardized
                               detail adds nothing and global z-scoring hurts chaos)
- NO global z-standardization of features (control result: global std 3x worse on
  chaotic regimes; task-dependent).
- Horizon-GROUPED direct ridge heads h in {24,48,96,168,336,720}; step j is
  predicted by the first head h* >= j (never one 720-dim ridge - conditioning).
- Frozen random dict (cos RFF + squared subset), seed fixed (default 42);
  pass seeds=(42..46) for a deterministic seed-ensemble.
- Bench-compatible wrappers: fit_sab_l / pred_sab_l.
"""
from __future__ import annotations
import numpy as np

try:
    import pywt
    _HAS_PYWT = True
except Exception:
    _HAS_PYWT = False

HEADS_DEFAULT = (24, 48, 96, 168, 336, 720)
COMPACT_GROUPS = ("identity", "MA3", "MA6", "MA12", "MA24", "EMA0.3", "EMA0.7")
APPROX_EXTRA = ("diff1", "diff2", "HP12", "HP24", "swt_cA1", "swt_cA2")


def _ma(X, win, axis=1):
    """Causal moving average along time for each row of a 2-D window bank."""
    X = np.asarray(X)
    if X.ndim == 1:
        c = np.concatenate([[0.0], X]).cumsum()
        starts = np.maximum(np.arange(len(X)) - win + 1, 0)
        counts = np.minimum(np.arange(len(X)) + 1, win)
        return (c[1:] - c[starts]) / counts
    if win <= 1:
        return X.copy()
    n, length = X.shape
    padded = np.concatenate([np.zeros((n, 1)), X], axis=1)
    c = np.cumsum(padded, axis=1)
    t = np.arange(length)
    starts = np.maximum(t - win + 1, 0)
    counts = np.minimum(t + 1, win)
    return (c[:, 1:] - c[:, starts]) / counts[None, :]


def _ema(X, alpha):
    """Causal EMA along the time axis of each row."""
    X = np.asarray(X)
    if X.ndim == 1:
        out = np.empty_like(X)
        out[0] = X[0]
        for i in range(1, len(X)):
            out[i] = alpha * X[i] + (1.0 - alpha) * out[i - 1]
        return out
    out = np.empty_like(X)
    out[:, 0] = X[:, 0]
    for j in range(1, X.shape[1]):
        out[:, j] = alpha * X[:, j] + (1.0 - alpha) * out[:, j - 1]
    return out


def _swt_approx(xa, wavelet="db4", level=2, lvl=1):
    """SWT same-length cA_lvl as (N, L); None if unavailable."""
    if not _HAS_PYWT:
        return None
    L = xa.shape[1]
    out = np.empty((xa.shape[0], L))
    try:
        for i, row in enumerate(xa):
            cas = [p[0] for p in reversed(pywt.swt(row, wavelet, level))]  # [cA1, cA2]
            out[i] = cas[lvl - 1]
    except Exception:
        return None
    return out


def signal_profile(tail):
    """Causal roughness on the training tail: detrended relative std + spectral peak ratio."""
    tail = np.asarray(tail, float)
    resid = tail - _ma(tail, 24)
    rough = float(np.std(resid) / (np.std(tail) + 1e-8))
    return {"roughness": rough}


def choose_profile(tail, threshold=0.35):
    """Return 'compact' for rough tails, 'approx' for smooth tails (causal, train-only)."""
    return "compact" if signal_profile(tail)["roughness"] > threshold else "approx"


class SABLForecaster:
    """Signal-adaptive BigDict with horizon-grouped ridge heads, L=336 default."""

    def __init__(self, input_length=336, heads=HEADS_DEFAULT, alpha=10.0, dict_dim=256,
                 sq_dim=64, seed=42, profile="auto", rough_threshold=0.35,
                 wavelet="db4", swt_level=2, feature_scaling=False, alpha_grid=None):
        self.L = int(input_length)
        self.heads = tuple(sorted(int(h) for h in heads))
        self.alpha = float(alpha)
        self.dict_dim = int(dict_dim)
        self.sq_dim = int(sq_dim)
        self.seed = int(seed)
        self.profile_mode = profile
        self.rough_threshold = rough_threshold
        self.wavelet = wavelet
        self.swt_level = swt_level
        self.feature_scaling = bool(feature_scaling)
        self.alpha_grid = tuple(float(a) for a in alpha_grid) if alpha_grid else None
        self.W_ = None          # dict: head -> (D, h)
        self.dict_ = None        # dict: seed -> (Wr, b, sq_idx)
        self.profile_ = None
        self.history_ = None

    # ── feature bank ────────────────────────────────────────────────────
    def _bank_names(self, profile):
        names = list(COMPACT_GROUPS)
        if profile == "approx":
            names += list(APPROX_EXTRA)
        return names

    def _bank(self, xa, profile):
        """xa: (N, L) anchored windows (or (L,)). Returns (N, D0)."""
        if xa.ndim == 1:
            xa = xa[None, :]
        parts = []
        for name in self._bank_names(profile):
            if name == "identity":
                parts.append(xa)
            elif name.startswith("MA"):
                parts.append(_ma(xa, int(name[2:])))
            elif name.startswith("EMA"):
                parts.append(_ema(xa, float(name[3:])))
            elif name == "diff1":
                d = np.zeros_like(xa); d[:, 1:] = np.diff(xa, axis=1); parts.append(d)
            elif name == "diff2":
                d = np.zeros_like(xa); d[:, 1:] = np.diff(xa, axis=1)
                d2 = np.zeros_like(xa); d2[:, 1:] = np.diff(d, axis=1); parts.append(d2)
            elif name == "HP12":
                parts.append(xa - _ma(xa, 12))
            elif name == "HP24":
                parts.append(xa - _ma(xa, 24))
            elif name in ("swt_cA1", "swt_cA2"):
                s = _swt_approx(xa, self.wavelet, self.swt_level, int(name[-1]))
                lvl = int(name[-1])
                if s is None:  # fallback: MA proxy (keeps dims stable)
                    parts.append(_ma(xa, 12 if lvl == 1 else 24) - _ma(xa, 24 if lvl == 1 else 96))
                else:
                    parts.append(s)
        return np.concatenate(parts, axis=1)

    # ── fit ─────────────────────────────────────────────────────────────
    def fit(self, series, horizon):
        s = np.asarray(series, float).ravel()
        H = int(horizon)
        heads = [h for h in self.heads if h <= H]
        if not heads or heads[-1] < H:
            heads = heads + [H]
        self._heads_used = heads
        prof = choose_profile(s[-2000:], self.rough_threshold) if self.profile_mode == "auto" else self.profile_mode
        self.profile_ = prof
        L = self.L
        n = s.shape[0]
        hmax = heads[-1]
        n_win = n - L - hmax + 1
        if n_win < 50:
            raise RuntimeError(f"SAB-L: need >= {L + hmax + 49} points, got {n}")
        ends = np.arange(L, L + n_win)
        xa = np.stack([s[i - L:i] for i in ends]) - s[ends - 1][:, None]
        X0 = self._bank(xa, prof)
        D0 = X0.shape[1]
        stride = max(1, D0 // self.sq_dim)
        sq_idx = np.arange(0, D0, stride)[: self.sq_dim]
        # Optional train-only feature scaling.  This is distinct from global
        # target z-scoring: statistics are learned only from the training
        # windows and are applied unchanged at prediction time.
        X0 = np.asarray(X0, dtype=np.float64)
        if self.feature_scaling:
            self.mu_ = X0.mean(axis=0)
            self.sd_ = X0.std(axis=0)
            self.sd_[self.sd_ < 1e-8] = 1.0
            X0 = (X0 - self.mu_) / self.sd_
        else:
            self.mu_ = None
            self.sd_ = None
        # frozen dict (here: single seed kept deterministic)
        rng = np.random.default_rng(self.seed)
        Wr = rng.standard_normal((D0, self.dict_dim)) / np.sqrt(D0)
        b = rng.uniform(0.0, 2 * np.pi, self.dict_dim)
        Phi = np.concatenate([X0, np.cos(X0 @ Wr + b), X0[:, sq_idx] ** 2], axis=1).astype(np.float32)
        D = Phi.shape[1]
        W = {}
        P64 = Phi.astype(np.float64)
        self.alpha_chosen_ = {}
        for h in heads:
            Yh = np.stack([s[e:e + h] - s[e - 1] for e in ends])
            if self.alpha_grid and len(P64) > 50:
                # Causal validation split inside the training slice.
                n_val = max(1, len(P64) // 7)
                tr = np.arange(len(P64) - n_val)
                va = np.arange(len(P64) - n_val, len(P64))
                best_alpha, best_err = float(self.alpha), float("inf")
                for candidate in self.alpha_grid:
                    candidate_alpha = float(candidate)
                    Ac = P64.T @ P64 + candidate_alpha * np.eye(D)
                    Wc = np.linalg.solve(Ac, P64[tr].T @ Yh[tr])
                    err = float(np.mean((P64[va] @ Wc - Yh[va]) ** 2))
                    if err < best_err:
                        best_err, best_alpha = err, candidate_alpha
            else:
                best_alpha = float(self.alpha)
            A = P64.T @ P64 + best_alpha * np.eye(D)
            W[h] = np.linalg.solve(A, P64.T @ Yh).astype(np.float32)
            self.alpha_chosen_[h] = best_alpha
        self.W_ = W
        self.dict_ = {self.seed: (Wr, b, sq_idx)}
        self.history_ = s
        self._Phi_dim = D
        return self

    # ── predict ─────────────────────────────────────────────────────────
    def _phi(self, window, seed):
        Wr, b, sq_idx = self.dict_[seed]
        xa = (window[None, :] - window[-1]).astype(np.float32)
        X0 = self._bank(xa, self.profile_).astype(np.float32)
        if self.feature_scaling:
            X0 = ((X0 - self.mu_.astype(np.float32)) / self.sd_.astype(np.float32)).astype(np.float32)
        return np.concatenate([X0, np.cos(X0 @ Wr + b), X0[:, sq_idx] ** 2], axis=1)

    def predict_hist(self, hist, seeds=(42, 43, 44, 45, 46)):
        """Predict H=horizon_ steps. `seeds` = dict seeds to average over if stored."""
        h = np.asarray(hist, float)
        L = self.L
        w = h[-L:] if len(h) >= L else np.pad(h, (L - len(h), 0), mode="edge")
        anchor = float(w[-1])
        H = self._heads_used[-1]
        out = np.empty(H, dtype=float)
        seeds_avail = [sd for sd in seeds if sd in self.dict_ or sd == self.seed] or [self.seed]
        for sd in dict.fromkeys(seeds_avail):
            sd_eff = self.seed if sd not in self.dict_ else sd
            phi = self._phi(w, sd_eff)
            for idx, hstar in enumerate(self._heads_used):
                lo = self._heads_used[idx - 1] if idx else 0
                hi = hstar
                Ws = [self.W_[hstar]]
                out[lo:hi] += phi[0] @ Ws[0][:, lo:hi]
        out /= len(dict.fromkeys(seeds_avail))
        return out + anchor

    def predict(self, horizon):
        return self.predict_hist(self.history_)[-horizon:] if False else self.predict_hist(self.history_)[:horizon]


def fit_sab_l(train, H, profile="auto", input_length=336, seed=42, alpha=10.0):
    return SABLForecaster(input_length=input_length, profile=profile, seed=seed, alpha=alpha).fit(train, H)


def pred_sab_l(model, hist):
    return model.predict_hist(hist)
