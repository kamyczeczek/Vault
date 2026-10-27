"""Patch embedding for Group-Sparse Bet 2 — per-channel non-overlapping P.

Spec: L=336 window, P=24 (336->14 tokens, mean-pooled) and P=48 (336->7 tokens),
train-only mu/sigma standardization. Deterministic, no RNG.
"""
from __future__ import annotations

import numpy as np


CHANNELS = ["OT", "HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL"]
N_CHANNELS = 7
OT_IDX = 0  # OT is first in our channel order


def patch_mean_pool(window: np.ndarray, patch_size: int) -> np.ndarray:
    """Per-channel non-overlapping mean pooling.

    window: (L, C) with L % P == 0
    Returns (n_patches, C) where n_patches = L // P.
    Each patch is mean over P rows.
    """
    L, C = window.shape
    assert L % patch_size == 0, f"L={L} not divisible by P={patch_size}"
    n_patches = L // patch_size
    # (n_patches, P, C) -> mean over P
    return window.reshape(n_patches, patch_size, C).mean(axis=1)


def compute_patch_stats(series: np.ndarray, L: int, P: int) -> tuple[np.ndarray, np.ndarray]:
    """Train-only mu/sigma over patch features.

    Uses sliding windows over series (training series only, typically 8545 or 11425 rows).
    For each window ending at position end (L <= end <= len(series)-1),
    computes patch features and aggregates global mean/std per (channel, patch_position)
    flattened to (C * n_patches,) features.

    We compute stats over the flattened patch feature matrix built from all training windows.
    Returns (mu, sigma) each shape (C * n_patches,) with floor sigma >= 1e-6.
    """
    n_patches = L // P
    n_features = N_CHANNELS * n_patches
    # Collect all patch vectors
    X_all = []
    # For calibration, sweep windows just like GroupSparseNLinear will see them:
    # windows are series[end-L:end] for end in [L, len(series)-horizon] — but for stats
    # we use all windows up to len(series)-1 to get enough samples; the exact range
    # doesn't materially change mu/sigma as long as TRAIN-ONLY.
    # Use stride 1, all windows ending at L..len(series)
    for end in range(L, len(series)):
        window = series[end - L:end]  # (L, C)
        patches = patch_mean_pool(window, P)  # (n_patches, C) — note patch_mean_pool returns (14,7) but we want per-channel then transpose
        # patch_mean_pool currently returns (n_patches, C) already
        # Flatten as channel-major: for each channel c, patches 0..n_patches-1 contiguous
        # But our window shape is (L, C) where C=7 columns in CHANNELS order.
        # patch_mean_pool does reshape(L,C) -> (n_patches,P,C).mean(axis=1) -> (n_patches,C)
        # So patches[p, c] = mean of rows.
        # We want feature vector of length C*n_patches: channel groups contiguous.
        # Map: for c in 0..C-1, for p in 0..n_patches-1: idx = c*n_patches + p = patches[p, c]
        vec = np.empty(n_features)
        for c in range(N_CHANNELS):
            for p in range(n_patches):
                vec[c * n_patches + p] = patches[p, c]
        X_all.append(vec)
    X_all = np.stack(X_all, axis=0)  # (N_windows, n_features)
    mu = X_all.mean(axis=0)
    sigma = X_all.std(axis=0)
    sigma = np.maximum(sigma, 1e-6)
    # Guard against zero-variance channels (e.g. constant patches)
    return mu, sigma


def embed_window(window: np.ndarray, P: int, mu: np.ndarray, sigma: np.ndarray, last_row: np.ndarray | None = None) -> np.ndarray:
    """Embed one window to patch features, standardized.

    window: (L, C)
    If last_row is not None, the window is first level-free shifted: window - last_row (broadcast).
    Then patch-mean-pooled, flattened channel-major, standardized with mu/sigma.
    Returns shape (C * n_patches,)
    """
    if last_row is not None:
        window = window - last_row  # broadcast (L,C) - (1,C) or (C,)
    patches = patch_mean_pool(window, P)  # (n_patches, C)
    n_patches = patches.shape[0]
    vec = np.empty(N_CHANNELS * n_patches)
    for c in range(N_CHANNELS):
        for p in range(n_patches):
            vec[c * n_patches + p] = patches[p, c]
    # Standardize
    vec = (vec - mu) / sigma
    return vec
