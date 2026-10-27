"""BigDictELM ablation study.

Tests which components of the filter bank and activation dictionary drive
performance gains vs dead weight.

Ablation groups:
  1. Filter-bank components tested individually:
     identity, MA3, MA6, MA12, MA24, EMA0.3, EMA0.7, diff1, diff2,
     HP12 (xa - ma12), HP24 (xa - ma24), wavelet_db4, wavelet_sym4
  2. Activation families: cos, rbf, tanh, mish, softplus, gelu
  3. Combined effects: top filter combos + top activations
  4. Full baseline (all filters + hybrid activation)

Evaluation: etth1_H96, sunspot_H24, seasonal_H48, thomas_H24
Metrics: MAE, RMSE, wall time
"""
from __future__ import annotations
import numpy as np
import json
import time
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

try:
    import pywt
    _HAS_PYWT = True
except Exception:
    _HAS_PYWT = False


# ── Vectorised filter bank (precomputes all windows at once) ────────────────

def _vectorised_filter_bank(series_windowed, selected_filters):
    """Given an array of shape (N, L) where each row is a window, apply selected filters.
    Returns (N, D) concatenated feature matrix."""
    X = series_windowed  # (N, L)
    outs = []
    for fname in selected_filters:
        if fname == "identity":
            outs.append(X)
        elif fname.startswith("MA"):
            w = int(fname[2:])
            # cumsum approach for running average
            c = np.concatenate([[0.0], X], axis=0).cumsum(axis=0)  # (N+1, L)
            n_valid = np.minimum(np.arange(w, len(X) + 1), len(X) + 1) - \
                      np.maximum(np.arange(len(X)) - w + 1, 0)
            # Efficient: (i+1)-th cumsum minus s-th cumsum divided by count
            starts = np.maximum(np.arange(len(X)) - w + 1, 0)
            counts = np.minimum(np.arange(len(X)) + 1, w)
            sums = c[1:, :] - c[starts, :]
            ma = sums / counts[:, None]
            outs.append(ma)
        elif fname.startswith("EMA"):
            a = float(fname[3:])
            ema = np.empty_like(X)
            ema[0] = X[0]
            for i in range(1, len(X)):
                ema[i] = a * X[i] + (1 - a) * ema[i - 1]
            outs.append(ema)
        elif fname == "diff1":
            d = np.zeros_like(X)
            d[:, 1:] = np.diff(X, axis=1)
            outs.append(d)
        elif fname == "diff2":
            d1 = np.zeros_like(X)
            d1[:, 1:] = np.diff(X, axis=1)
            d2 = np.zeros_like(X)
            d2[:, 1:] = np.diff(d1, axis=1)
            outs.append(d2)
        elif fname == "HP12":
            c = np.concatenate([[0.0], X], axis=0).cumsum(axis=0)
            starts = np.maximum(np.arange(len(X)) - 12 + 1, 0)
            counts = np.minimum(np.arange(len(X)) + 1, 12)
            sums = c[1:, :] - c[starts, :]
            ma12 = sums / counts[:, None]
            outs.append(X - ma12)
        elif fname == "HP24":
            c = np.concatenate([[0.0], X], axis=0).cumsum(axis=0)
            starts = np.maximum(np.arange(len(X)) - 24 + 1, 0)
            counts = np.minimum(np.arange(len(X)) + 1, 24)
            sums = c[1:, :] - c[starts, :]
            ma24 = sums / counts[:, None]
            outs.append(X - ma24)
        elif fname.startswith("wavelet_"):
            wav = fname.split("_", 1)[1]
            wave_feats = _vectorised_wavelet(X, wav)
            outs.extend(wave_feats)
    return np.concatenate(outs, axis=1)


def _vectorised_wavelet(X, wavelet):
    """Apply wavelet SWT row-wise; returns list of (N, L) arrays."""
    feats = []
    if not _HAS_PYWT:
        return feats
    try:
        L = X.shape[1]
        for row in X:
            coeffs = pywt.swt(row, wavelet, level=2)
            for cA, cD in coeffs:
                if len(cA) == L:
                    feats.append(cA.copy())
                if len(cD) == L:
                    feats.append(cD.copy())
    except Exception:
        pass
    if not feats:
        return []
    return [np.stack(feats[i::len(feats)], axis=0) for i in range(len(feats) // (L if feats and len(feats[0]) == L else 1))] if feats else []


def _build_precomputed_filters(series, selected_filters):
    """Pre-compute all filter outputs for all windows. Returns dict of name -> (N, L)."""
    N = len(series) - 96 + 1
    L = 96
    # Build windows as (N, L)
    # Use stride_tricks for efficiency
    from numpy.lib.stride_tricks import as_strided
    strides = (series.itemsize, series.itemsize)
    windows = as_strided(series[:N + L - 1], shape=(N, L), strides=strides)
    windows = windows.astype(np.float64, copy=False)

    # Subtract last element of each window (anchoring)
    anchors = windows[:, -1].copy()
    X = windows - anchors[:, None]

    banks = {}
    for fname in selected_filters:
        if fname == "identity":
            banks[fname] = X
        elif fname.startswith("MA"):
            w = int(fname[2:])
            c = np.concatenate([[0.0], X], axis=0).cumsum(axis=0)
            starts = np.maximum(np.arange(N) - w + 1, 0)
            counts = np.minimum(np.arange(N) + 1, w)
            sums = c[1:N + 1, :] - c[starts, :]
            banks[fname] = sums / counts[:, None]
        elif fname.startswith("EMA"):
            a = float(fname[3:])
            ema = np.empty_like(X)
            ema[0] = X[0]
            for i in range(1, N):
                ema[i] = a * X[i] + (1 - a) * ema[i - 1]
            banks[fname] = ema
        elif fname == "diff1":
            d = np.zeros_like(X)
            d[:, 1:] = np.diff(X, axis=1)
            banks[fname] = d
        elif fname == "diff2":
            d1 = np.zeros_like(X)
            d1[:, 1:] = np.diff(X, axis=1)
            d2 = np.zeros_like(X)
            d2[:, 1:] = np.diff(d1, axis=1)
            banks[fname] = d2
        elif fname == "HP12":
            c = np.concatenate([[0.0], X], axis=0).cumsum(axis=0)
            starts = np.maximum(np.arange(N) - 12 + 1, 0)
            counts = np.minimum(np.arange(N) + 1, 12)
            sums = c[1:N + 1, :] - c[starts, :]
            banks["HP12"] = X - sums / counts[:, None]
        elif fname == "HP24":
            c = np.concatenate([[0.0], X], axis=0).cumsum(axis=0)
            starts = np.maximum(np.arange(N) - 24 + 1, 0)
            counts = np.minimum(np.arange(N) + 1, 24)
            sums = c[1:N + 1, :] - c[starts, :]
            banks[fname] = X - sums / counts[:, None]
        elif fname.startswith("wavelet_"):
            wav = fname.split("_", 1)[1]
            wave_feats = _precompute_wavelets(windows, wav, anchors, N, L)
            banks.update(wave_feats)
    return banks, anchors


def _precompute_wavelets(windows, wavelet, anchors, N, L):
    """Pre-compute wavelet features for all windows."""
    if not _HAS_PYWT:
        return {}
    try:
        result = {}
        all_feats = []
        for i in range(N):
            xa = windows[i] - anchors[i]
            coeffs = pywt.swt(xa, wavelet, level=2)
            for cA, cD in coeffs:
                if len(cA) == L:
                    all_feats.append(cA)
                if len(cD) == L:
                    all_feats.append(cD)
        if all_feats:
            arr = np.stack(all_feats, axis=0)  # (n_feats, N, L)
            n_feats = arr.shape[0]
            # Reshape to (N, n_feats*L) — no, we want per-feature
            # Store as separate entries keyed by wavelet_feat_index
            for j in range(n_feats):
                key = f"{wavelet}_feat{j}"
                result[key] = arr[j].T  # (N, L)
            result[f"{wavelet}_count"] = n_feats
        return result
    except Exception:
        return {}


# ── Activation builders ──────────────────────────────────────────────────

def _make_phi_from_Xs(Xs, act_type, D0, hidden, gamma_scale, idx, rng):
    """Build phi function given normalized data Xs. Returns (Phi, params)."""
    if act_type == "cos":
        Wr = rng.standard_normal((D0, hidden)) * (1.0 / np.sqrt(D0))
        b = rng.uniform(0, 2 * np.pi, size=hidden)
        P = np.cos(Xs @ Wr + b)
        return np.concatenate([Xs, P, Xs[:, idx] ** 2], axis=1), ("cos", Wr, b)
    elif act_type == "rbf":
        c_idx = rng.choice(Xs.shape[0], size=min(hidden, Xs.shape[0]), replace=False)
        centers = Xs[c_idx]
        gamma = gamma_scale / (2.0 * D0)
        x_sq = np.sum(Xs ** 2, axis=1, keepdims=True)
        c_sq = np.sum(centers ** 2, axis=1, keepdims=True).T
        d_sq = x_sq + c_sq - 2.0 * (Xs @ centers.T)
        RBF = np.exp(-gamma * np.maximum(0.0, d_sq))
        return np.concatenate([Xs, RBF, Xs[:, idx] ** 2], axis=1), ("rbf", centers, gamma)
    elif act_type == "tanh":
        Wr = rng.standard_normal((D0, hidden)) * (1.0 / np.sqrt(D0))
        b = rng.standard_normal(hidden) * 0.1
        P = np.tanh(Xs @ Wr + b)
        return np.concatenate([Xs, P, Xs[:, idx] ** 2], axis=1), ("tanh", Wr, b)
    elif act_type == "mish":
        Wr = rng.standard_normal((D0, hidden)) * (1.0 / np.sqrt(D0))
        b = rng.standard_normal(hidden) * 0.1
        z = Xs @ Wr + b
        P = z * np.tanh(np.log1p(np.exp(np.clip(z, -20, 20))))
        return np.concatenate([Xs, P, Xs[:, idx] ** 2], axis=1), ("mish", Wr, b)
    elif act_type == "softplus":
        Wr = rng.standard_normal((D0, hidden)) * (1.0 / np.sqrt(D0))
        b = rng.standard_normal(hidden) * 0.1
        P = np.log1p(np.exp(np.clip(Xs @ Wr + b, -20, 20)))
        return np.concatenate([Xs, P, Xs[:, idx] ** 2], axis=1), ("softplus", Wr, b)
    elif act_type == "gelu":
        Wr = rng.standard_normal((D0, hidden)) * (1.0 / np.sqrt(D0))
        b = rng.standard_normal(hidden) * 0.1
        z = Xs @ Wr + b
        P = z * 0.5 * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (z + 0.044715 * z ** 3)))
        return np.concatenate([Xs, P, Xs[:, idx] ** 2], axis=1), ("gelu", Wr, b)
    elif act_type == "hybrid":
        h_half = hidden // 2
        Wr_cos = rng.standard_normal((D0, h_half)) * (1.0 / np.sqrt(D0))
        b_cos = rng.uniform(0, 2 * np.pi, size=h_half)
        c_idx = rng.choice(Xs.shape[0], size=min(h_half, Xs.shape[0]), replace=False)
        centers = Xs[c_idx]
        gamma = gamma_scale / (2.0 * D0)
        P_cos = np.cos(Xs @ Wr_cos + b_cos)
        x_sq = np.sum(Xs ** 2, axis=1, keepdims=True)
        c_sq = np.sum(centers ** 2, axis=1, keepdims=True).T
        d_sq = x_sq + c_sq - 2.0 * (Xs @ centers.T)
        RBF = np.exp(-gamma * np.maximum(0.0, d_sq))
        return np.concatenate([Xs, P_cos, RBF, Xs[:, idx] ** 2], axis=1), \
               ("hybrid", Wr_cos, b_cos, centers, gamma)
    else:
        raise ValueError(f"Unknown act_type: {act_type}")


# ── Ridge helper ──────────────────────────────────────────────────────────

def _ridge_multioutput(Phi, Y, alpha):
    d = Phi.shape[1]
    A = Phi.T @ Phi + alpha * np.eye(d)
    B = Phi.T @ Y
    try:
        L_chol = np.linalg.cholesky(A)
        W = np.linalg.solve(L_chol.T, np.linalg.solve(L_chol, B))
    except np.linalg.LinAlgError:
        W = np.linalg.solve(A, B)
    return W


# ── Data generators (match bench.py) ─────────────────────────────────────

def gen_seasonal(n=2600, seed=0):
    rng = np.random.default_rng(seed)
    base = np.sin(2 * np.pi * np.arange(n) / 24) + 0.5 * np.sin(2 * np.pi * np.arange(n) / 168)
    noise = rng.standard_normal(n) * 0.15
    return (base + noise).astype(float)

def gen_trending(n=2600, seed=1):
    rng = np.random.default_rng(seed)
    return (np.cumsum(rng.standard_normal(n) * 0.3) + 0.3 * np.sin(2 * np.pi * np.arange(n) / 30)).astype(float)

def gen_multiscale(n=2600, seed=4):
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    return (np.sin(2 * np.pi * t / 12) + 0.6 * np.sin(2 * np.pi * t / 48)
            + 0.4 * np.sin(2 * np.pi * t / 168) + 0.25 * rng.standard_normal(n)).astype(float)

def get_sunspot(n=2600):
    rng = np.random.default_rng(42)
    t = np.arange(n)
    return (50.0 + 40.0 * np.sin(2 * np.pi * t / 132.0) + 10.0 * rng.standard_normal(n)).astype(float)


SERIES_MAP = {
    "etth1_H96": lambda: gen_trending(2600, seed=99),
    "sunspot_H24": get_sunspot,
    "seasonal_H48": gen_seasonal,
    "thomas_H24": lambda: gen_thomas(2600),
}


def gen_thomas(n=2600, b=0.208186, dt=0.05, seed=5, perturbation=0.0):
    """Return the x-coordinate of a reproducible Thomas chaotic trajectory."""
    rng = np.random.default_rng(seed)
    initial = np.array([0.1, 0.2, 0.3])
    if perturbation:
        initial += float(perturbation) * rng.standard_normal(3)
    state = initial.copy().astype(np.float64)
    out = np.empty((n, 3), dtype=np.float64)
    def f(x):
        return np.array([np.sin(x[1]) - b * x[0],
                         np.sin(x[2]) - b * x[1],
                         np.sin(x[0]) - b * x[2]])
    burn_in = 500
    for step in range(n + burn_in):
        k1 = f(state)
        k2 = f(state + 0.5 * dt * k1)
        k3 = f(state + 0.5 * dt * k2)
        k4 = f(state + dt * k3)
        state = state + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        if step >= burn_in:
            out[step - burn_in] = state
    return out[:, 0]


# ── Evaluator ─────────────────────────────────────────────────────────────

TRAIN_END = 2000
INPUT_LEN = 96
HIDDEN = 64          # Reduced from 384 for speed; original uses 384
ALPHA_GRID = (30, 100, 300)
SEED = 42


def evaluate_config(series, H, filter_names, act_type, label, verbose=True):
    """Fit BigDict-style model; return metric dict."""
    t0 = time.time()
    N = TRAIN_END - INPUT_LEN + 1

    # Pre-compute all windows (stride tricks)
    from numpy.lib.stride_tricks import as_strided
    s = np.asarray(series, dtype=np.float64)
    s_train = s[:TRAIN_END]
    s_full = s

    # Build train windows (same as bench.py)
    n_train = TRAIN_END - H - INPUT_LEN + 1
    strides = (s_train.itemsize, s_train.itemsize)
    train_windows = as_strided(s_train[:n_train + INPUT_LEN - 1], shape=(n_train, INPUT_LEN), strides=strides)

    # Build test windows (origins)
    origins = [TRAIN_END + i * H for i in range(5) if TRAIN_END + i * H + H <= len(s_full)]
    test_windows = []
    test_anchors = []
    for o in origins:
        w = s_full[max(0, o - INPUT_LEN):o]
        if len(w) < INPUT_LEN:
            w = np.pad(w, (INPUT_LEN - len(w), 0), mode='edge')
        test_windows.append(w)
        test_anchors.append(float(w[-1]))
    test_windows = np.array(test_windows)
    test_anchors = np.array(test_anchors)

    # Build target Y
    ends = np.arange(INPUT_LEN, TRAIN_END - H + 1)
    Y = np.stack([s_full[e:e + H] - float(s_full[e - 1]) for e in ends]).astype(np.float64)

    # Select filters
    selected = [f for f in ALL_FILTER_NAMES if any(f in fn or fn == f for fn in filter_names)]
    if not selected:
        selected = list(filter_names)

    # Pre-compute training filter banks
    t1 = time.time()
    bank_parts = {}
    X_train = train_windows - train_windows[:, -1:None]  # anchor subtraction
    for fname in selected:
        if fname == "identity":
            bank_parts[fname] = X_train
        elif fname.startswith("MA"):
            w = int(fname[2:])
            c = np.concatenate([np.zeros((1, X_train.shape[1])), X_train], axis=0).cumsum(axis=0)
            starts = np.maximum(np.arange(n_train) - w + 1, 0)
            counts = np.minimum(np.arange(n_train) + 1, w)
            bank_parts[fname] = (c[1:n_train + 1] - c[starts]) / counts[:, None]
        elif fname.startswith("EMA"):
            a = float(fname[3:])
            ema = np.empty_like(X_train)
            ema[0] = X_train[0]
            for i in range(1, n_train):
                ema[i] = a * X_train[i] + (1 - a) * ema[i - 1]
            bank_parts[fname] = ema
        elif fname == "diff1":
            d = np.zeros_like(X_train)
            d[:, 1:] = np.diff(X_train, axis=1)
            bank_parts[fname] = d
        elif fname == "diff2":
            d1 = np.zeros_like(X_train)
            d1[:, 1:] = np.diff(X_train, axis=1)
            d2 = np.zeros_like(X_train)
            d2[:, 1:] = np.diff(d1, axis=1)
            bank_parts[fname] = d2
        elif fname == "HP12":
            c = np.concatenate([np.zeros((1, X_train.shape[1])), X_train], axis=0).cumsum(axis=0)
            starts = np.maximum(np.arange(n_train) - 12 + 1, 0)
            counts = np.minimum(np.arange(n_train) + 1, 12)
            bank_parts[fname] = X_train - (c[1:n_train + 1] - c[starts]) / counts[:, None]
        elif fname == "HP24":
            c = np.concatenate([np.zeros((1, X_train.shape[1])), X_train], axis=0).cumsum(axis=0)
            starts = np.maximum(np.arange(n_train) - 24 + 1, 0)
            counts = np.minimum(np.arange(n_train) + 1, 24)
            bank_parts[fname] = X_train - (c[1:n_train + 1] - c[starts]) / counts[:, None]
        elif fname.startswith("wavelet_"):
            wav = fname.split("_", 1)[1]
            wf = _precompute_wavelets_simple(X_train, wav)
            if wf is not None:
                bank_parts[fname] = wf
    t_build = time.time() - t1

    X0 = np.concatenate([bank_parts[f] for f in selected], axis=1)
    D0 = X0.shape[1]
    stride = max(1, D0 // 64)
    idx = np.arange(0, D0, stride)[:64]
    mu = X0.mean(axis=0)
    sd = X0.std(axis=0)
    sd[sd < 1e-8] = 1.0
    Xs = (X0 - mu) / sd

    # Test features
    test_X = test_windows - test_anchors[:, None]
    test_parts = {}
    for fname in selected:
        if fname == "identity":
            test_parts[fname] = test_X
        elif fname.startswith("MA"):
            w = int(fname[2:])
            tw = test_X
            c = np.concatenate([np.zeros((1, tw.shape[1])), tw], axis=0).cumsum(axis=0)
            n_test = len(tw)
            starts = np.maximum(np.arange(n_test) - w + 1, 0)
            counts = np.minimum(np.arange(n_test) + 1, w)
            test_parts[fname] = (c[1:n_test + 1] - c[starts]) / counts[:, None]
        elif fname.startswith("EMA"):
            a = float(fname[3:])
            ema = np.empty_like(test_X)
            ema[0] = test_X[0]
            for i in range(1, len(test_X)):
                ema[i] = a * test_X[i] + (1 - a) * ema[i - 1]
            test_parts[fname] = ema
        elif fname == "diff1":
            d = np.zeros_like(test_X)
            d[:, 1:] = np.diff(test_X, axis=1)
            test_parts[fname] = d
        elif fname == "diff2":
            d1 = np.zeros_like(test_X)
            d1[:, 1:] = np.diff(test_X, axis=1)
            d2 = np.zeros_like(test_X)
            d2[:, 1:] = np.diff(d1, axis=1)
            test_parts[fname] = d2
        elif fname == "HP12":
            tw = test_X
            c = np.concatenate([np.zeros((1, tw.shape[1])), tw], axis=0).cumsum(axis=0)
            n_test = len(tw)
            starts = np.maximum(np.arange(n_test) - 12 + 1, 0)
            counts = np.minimum(np.arange(n_test) + 1, 12)
            test_parts[fname] = tw - (c[1:n_test + 1] - c[starts]) / counts[:, None]
        elif fname == "HP24":
            tw = test_X
            c = np.concatenate([np.zeros((1, tw.shape[1])), tw], axis=0).cumsum(axis=0)
            n_test = len(tw)
            starts = np.maximum(np.arange(n_test) - 24 + 1, 0)
            counts = np.minimum(np.arange(n_test) + 1, 24)
            test_parts[fname] = tw - (c[1:n_test + 1] - c[starts]) / counts[:, None]
        elif fname.startswith("wavelet_"):
            wav = fname.split("_", 1)[1]
            wf = _precompute_wavelets_simple(test_X, wav)
            if wf is not None:
                test_parts[fname] = wf

    X_test = np.concatenate([test_parts[f] for f in selected], axis=1)
    Xs_test = ((X_test - mu) / sd)

    # Build activation
    rng = np.random.default_rng(SEED)
    t_phi = time.time()
    Phi, params = _make_phi_from_Xs(Xs, act_type, D0, HIDDEN, gamma_scale=1.0, idx=idx, rng=rng)
    Phi_test = _apply_phi_same_params(Xs_test, act_type, params, mu, sd, selected, test_parts, D0, HIDDEN, gamma_scale=1.0, idx=idx)
    t_phi_end = time.time() - t_phi

    # Hyperparameter search: compute Phi once, then split for validation
    alpha_cands = list(ALPHA_GRID)
    n_val = max(1, len(Xs) // 7)

    # Generate phi on FULL standardized data first
    rng_full = np.random.default_rng(SEED)
    Phi_all, _ = _make_phi_from_Xs(Xs, act_type, D0, HIDDEN, gamma_scale=1.0, idx=idx, rng=rng_full)

    # Split for validation
    Xtr, Xva = Xs[:-n_val], Xs[-n_val:]
    Ytr, Yva = Y[:-n_val], Y[-n_val:]
    Phi_tr, Phi_va = Phi_all[:-n_val], Phi_all[-n_val:]

    best_a, best_err = alpha_cands[0], float("inf")
    for a in alpha_cands:
        Wv = _ridge_multioutput(Phi_tr, Ytr, float(a))
        err = float(np.mean((Phi_va @ Wv - Yva) ** 2))
        if err < best_err:
            best_err = err
            best_a = a
    chosen_alpha = float(best_a)

    # Refit
    W = _ridge_multioutput(Phi, Y, chosen_alpha)
    pred = Phi_test @ W  # shape (n_test, H) - delta predictions (already learned from Y = future - anchor)
    # pred already contains the delta (future - anchor); add anchor back element-wise
    test_anchors_col = test_anchors[:, None]  # (n_test, 1)
    preds_final = pred + test_anchors_col

    P = preds_final
    A = np.stack([s_full[o:o + H] for o in origins])

    mae = float(np.mean(np.abs(P - A)))
    rmse = float(np.sqrt(np.mean((P - A) ** 2)))
    wall = time.time() - t0

    if verbose:
        nwav = sum(1 for f in selected if f.startswith("wavelet_"))
        print(f"  [{label}] filters={selected} act={act_type} "
              f"MAE={mae:.4f} RMSE={rmse:.4f} time={wall:.1f}s "
              f"(build={t_build:.2f}s phi={t_phi_end:.2f}s D0={D0})")
    return {"label": label, "filter_names": list(selected), "act_type": act_type,
            "mae": mae, "rmse": rmse, "wall_time_s": round(wall, 2), "D0": D0,
            "alpha_chosen": chosen_alpha}


def _apply_phi_same_params(Xs, act_type, params, mu, sd, selected, test_parts, D0, hidden, gamma_scale, idx):
    """Apply the same phi transform using stored params."""
    kind, *rest = params
    if kind == "cos":
        Wr, b = rest
        return np.concatenate([Xs, np.cos(Xs @ Wr + b), Xs[:, idx] ** 2], axis=1)
    elif kind == "rbf":
        centers, gamma = rest
        x_sq = np.sum(Xs ** 2, axis=1, keepdims=True)
        c_sq = np.sum(centers ** 2, axis=1, keepdims=True).T
        d_sq = x_sq + c_sq - 2.0 * (Xs @ centers.T)
        RBF = np.exp(-gamma * np.maximum(0.0, d_sq))
        return np.concatenate([Xs, RBF, Xs[:, idx] ** 2], axis=1)
    elif kind == "tanh":
        Wr, b = rest
        return np.concatenate([Xs, np.tanh(Xs @ Wr + b), Xs[:, idx] ** 2], axis=1)
    elif kind == "mish":
        Wr, b = rest
        z = Xs @ Wr + b
        P = z * np.tanh(np.log1p(np.exp(np.clip(z, -20, 20))))
        return np.concatenate([Xs, P, Xs[:, idx] ** 2], axis=1)
    elif kind == "softplus":
        Wr, b = rest
        P = np.log1p(np.exp(np.clip(Xs @ Wr + b, -20, 20)))
        return np.concatenate([Xs, P, Xs[:, idx] ** 2], axis=1)
    elif kind == "gelu":
        Wr, b = rest
        z = Xs @ Wr + b
        P = z * 0.5 * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (z + 0.044715 * z ** 3)))
        return np.concatenate([Xs, P, Xs[:, idx] ** 2], axis=1)
    elif kind == "hybrid":
        Wr_cos, b_cos, centers, gamma = rest
        P_cos = np.cos(Xs @ Wr_cos + b_cos)
        x_sq = np.sum(Xs ** 2, axis=1, keepdims=True)
        c_sq = np.sum(centers ** 2, axis=1, keepdims=True).T
        d_sq = x_sq + c_sq - 2.0 * (Xs @ centers.T)
        RBF = np.exp(-gamma * np.maximum(0.0, d_sq))
        return np.concatenate([Xs, P_cos, RBF, Xs[:, idx] ** 2], axis=1)
    else:
        raise ValueError(f"Unknown phi kind: {kind}")


def _precompute_wavelets_simple(X, wavelet):
    """Pre-compute wavelet for all rows. Returns (N, L*n_feats) or None."""
    if not _HAS_PYWT:
        return None
    try:
        L = X.shape[1]
        feats_all = []
        for row in X:
            coeffs = pywt.swt(row, wavelet, level=2)
            for cA, cD in coeffs:
                if len(cA) == L:
                    feats_all.append(cA)
                if len(cD) == L:
                    feats_all.append(cD)
        if feats_all:
            arr = np.stack(feats_all, axis=0)  # (N, n_per_row, L)
            return arr.reshape(X.shape[0], -1)
        return None
    except Exception:
        return None


# ── Ablation configuration ────────────────────────────────────────────────

ALL_FILTER_NAMES = (
    "identity", "MA3", "MA6", "MA12", "MA24",
    "EMA0.3", "EMA0.7", "diff1", "diff2",
    "HP12", "HP24", "wavelet_db4", "wavelet_sym4",
)
ALL_ACTIVATIONS = ("cos", "rbf", "tanh", "mish", "softplus", "gelu")
FULL_FILTERS = ALL_FILTER_NAMES
FULL_ACT = "hybrid"

TASKS = [("etth1_H96", 96), ("sunspot_H24", 24), ("seasonal_H48", 48), ("thomas_H24", 24)]


def run_experiments():
    results = {"filter_ablation": [], "activation_ablation": [], "combo_test": [], "baseline": None}
    all_results = []

    print("=" * 70)
    print("BIGDICT ELM ABLATION STUDY")
    print("=" * 70)

    # ── Phase 1: Full baseline ─────────────────────────────────────────
    print("\n[Phase 1] Full baseline (all filters + hybrid activation)")
    for task_name, H in TASKS:
        series = SERIES_MAP[task_name]()
        r = evaluate_config(series, H, FULL_FILTERS, FULL_ACT,
                            f"{task_name}_full", verbose=True)
        results["baseline"] = r
        all_results.append(r)

    # ── Phase 2: Single-filter ablation ────────────────────────────────
    print("\n[Phase 2] Single-filter ablation (each vs identity-only baseline)")
    single_filters = [
        ("identity", ("identity",)),
        ("MA3", ("MA3",)),
        ("MA6", ("MA6",)),
        ("MA12", ("MA12",)),
        ("MA24", ("MA24",)),
        ("EMA0.3", ("EMA0.3",)),
        ("EMA0.7", ("EMA0.7",)),
        ("diff1", ("diff1",)),
        ("diff2", ("diff2",)),
        ("HP12", ("HP12",)),
        ("HP24", ("HP24",)),
        ("wavelet_db4", ("wavelet_db4",)),
        ("wavelet_sym4", ("wavelet_sym4",)),
    ]
    for label, fnames in single_filters:
        for task_name, H in TASKS:
            series = SERIES_MAP[task_name]()
            r = evaluate_config(series, H, fnames, FULL_ACT,
                                f"{task_name}_{label}", verbose=True)
            results["filter_ablation"].append(r)
            all_results.append(r)

    # ── Phase 3: Activation ablation ───────────────────────────────────
    print("\n[Phase 3] Activation family ablation (all filters, one activation)")
    for act in ALL_ACTIVATIONS:
        for task_name, H in TASKS:
            series = SERIES_MAP[task_name]()
            r = evaluate_config(series, H, FULL_FILTERS, act,
                                f"{task_name}_{act}", verbose=True)
            results["activation_ablation"].append(r)
            all_results.append(r)

    # ── Phase 4: Key combo tests ───────────────────────────────────────
    print("\n[Phase 4] Key combo tests")
    key_combos = [
        ("id_MA3_diff1", ("identity", "MA3", "diff1")),
        ("id_MA12_HP12", ("identity", "MA12", "HP12")),
        ("id_EMA03_wavdb4", ("identity", "EMA0.3", "wavelet_db4")),
        ("MA3_MA12_diff1_HP12", ("MA3", "MA12", "diff1", "HP12")),
        ("id_diff2_wavsym4", ("identity", "diff2", "wavelet_sym4")),
        ("MA6_EMA07_HP24", ("MA6", "EMA0.7", "HP24")),
    ]
    for label, fnames in key_combos:
        for task_name, H in TASKS:
            series = SERIES_MAP[task_name]()
            r = evaluate_config(series, H, fnames, FULL_ACT,
                                f"{task_name}_{label}", verbose=True)
            results["combo_test"].append(r)
            all_results.append(r)
        # Also test with cos activation on first 3 combos
        if "id" in label or label.startswith("MA3"):
            for task_name, H in TASKS:
                series = SERIES_MAP[task_name]()
                r = evaluate_config(series, H, fnames, "cos",
                                    f"{task_name}_{label}_cos", verbose=True)
                results["combo_test"].append(r)
                all_results.append(r)

    # ── Rankings ───────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("PER-TASK RANKINGS")
    print("=" * 70)
    by_task = {}
    for r in all_results:
        tn = "_".join(r["label"].split("_")[:-1])  # handle multi-part labels
        # Extract task name properly
        for tname, _ in TASKS:
            if r["label"].startswith(tname + "_"):
                tn = tname
                break
        by_task.setdefault(tn, []).append(r)

    for tn, rs in sorted(by_task.items()):
        rs_sorted = sorted(rs, key=lambda x: x["mae"])
        print(f"\n  {tn} ({len(rs)} configs):")
        for rank, r in enumerate(rs_sorted, 1):
            marker = " <-- BEST" if rank == 1 else ""
            filt_short = "+".join(f for f in r["filter_names"] if not f.startswith("wavelet"))
            nwav = sum(1 for f in r["filter_names"] if f.startswith("wavelet"))
            print(f"    #{rank:2d} {r['label']:50s} MAE={r['mae']:.4f} RMSE={r['rmse']:.4f} "
                  f"[{filt_short}{'+'+nwav*'wav' if nwav else ''}] act={r['act_type']} t={r['wall_time_s']}s{marker}")

    return results, all_results


def export_json(results, all_results, output_path="results_bigdict_ablation.json"):
    by_task = {}
    for r in all_results:
        for tname, _ in TASKS:
            if r["label"].startswith(tname + "_"):
                by_task.setdefault(tname, []).append(r)
                break

    summary = {}
    for tn, rs in sorted(by_task.items()):
        rs_sorted = sorted(rs, key=lambda x: x["mae"])
        summary[tn] = {
            "best_mae": rs_sorted[0]["mae"],
            "best_config": rs_sorted[0]["label"],
            "top5": [{"label": r["label"], "mae": r["mae"], "rmse": r["rmse"],
                      "filters": r["filter_names"], "act": r["act_type"],
                      "time_s": r["wall_time_s"]}
                     for r in rs_sorted[:5]],
            "total_configs": len(rs),
        }

    export = {
        "filter_ablation": results["filter_ablation"],
        "activation_ablation": results["activation_ablation"],
        "combo_test": results["combo_test"],
        "baseline": results["baseline"],
        "summary": summary,
    }
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2)
    print(f"\nResults written to {output_path}")
    return export


def main():
    t0 = time.time()
    results, all_results = run_experiments()
    export_json(results, all_results)
    print(f"\nTotal wall time: {time.time() - t0:.1f}s")
    print(f"Total configs tested: {len(all_results)}")


if __name__ == "__main__":
    main()
