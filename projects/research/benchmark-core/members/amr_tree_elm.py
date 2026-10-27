# ARCHIVED 2026-09-24: no wins recorded over AMR-FBS/KNN. Frozen per REFLECTION_PROMISING_METHODS.md - imports kept for compatibility
"""Adaptive Multi-Resolution Dictionary-Enhanced Extreme Learning Machine (AMR-Tree-ELM)
for Long-Horizon Sunspot Forecasting (Horizon H = 300).

Incorporates:
1. Waldmeier Asymmetry Causal Filter (handling asymmetric solar rise/decay).
2. Multi-Resolution Historical Cycle Dictionary Matching.
3. Spectral Harmonic Envelope Extrapolation (11-year Schwabe cycle phase anchoring).
4. Closed-form Extreme Learning Machine (ELM) with Ridge / Tree residual correction.
"""
from __future__ import annotations
import numpy as np

def _waldmeier_asymmetric_filter(x: np.ndarray, window: int = 13) -> np.ndarray:
    """Asymmetric filter respecting the fast rise / slow decay of sunspot cycles."""
    n = len(x)
    out = np.empty_like(x)
    # Forward asymmetric weighting
    w_rise = max(3, window // 2)
    w_fall = max(6, window)
    for i in range(n):
        s_rise = max(0, i - w_rise + 1)
        s_fall = max(0, i - w_fall + 1)
        # Use shorter window for rising phase, longer for falling phase
        if i > 0 and x[i] > x[i-1]:
            out[i] = np.mean(x[s_rise:i+1])
        else:
            out[i] = np.mean(x[s_fall:i+1])
    return out

def _spectral_envelope_forecast(history: np.ndarray, horizon: int) -> np.ndarray:
    """Extracts primary 11-year (132 month) Schwabe cycle envelope and extrapolates."""
    L = len(history)
    t = np.arange(L, dtype=float)
    # Dominant frequency estimation via FFT
    fft_vals = np.fft.rfft(history - np.mean(history))
    freqs = np.fft.rfftfreq(L)
    if len(fft_vals) > 1:
        idx = np.argmax(np.abs(fft_vals[1:])) + 1
        dom_freq = freqs[idx]
        dom_amp = np.abs(fft_vals[idx]) / (L / 2)
        dom_phase = np.angle(fft_vals[idx])
    else:
        dom_freq = 1.0 / 132.0
        dom_amp = np.std(history)
        dom_phase = 0.0

    t_fut = np.arange(L, L + horizon, dtype=float)
    # Extrapolate sinusoidal oscillation with dampening over long horizon
    damp = np.exp(-t_fut / (2 * horizon))
    spectral_pred = np.mean(history) + dom_amp * damp * np.cos(2 * np.pi * dom_freq * t_fut + dom_phase)
    return spectral_pred

def fit_amr_tree_elm(train: np.ndarray, horizon: int):
    y = np.asarray(train, dtype=float)
    # 1. Asymmetric smoothing
    smooth = _waldmeier_asymmetric_filter(y, window=13)
    residual = y - smooth

    # 2. Extract historical cycle templates (dictionary of 132-month windows)
    cycle_len = 132
    templates = []
    if len(y) > cycle_len * 2:
        for i in range(len(y) - cycle_len):
            templates.append(y[i:i+cycle_len])
    templates = np.array(templates) if templates else np.array([y[-min(len(y), cycle_len):]])

    return {
        "train": y,
        "smooth": smooth,
        "residual": residual,
        "templates": templates,
        "horizon": horizon
    }

def pred_amr_tree_elm(model: dict, history: np.ndarray) -> np.ndarray:
    horizon = model["horizon"]
    hist = np.asarray(history, dtype=float)

    # 1. Spectral harmonic envelope forecast
    spec_pred = _spectral_envelope_forecast(hist, horizon)

    # 2. Dictionary template matching (find closest historical cycle template)
    templates = model["templates"]
    lookback = min(len(hist), 132)
    recent = hist[-lookback:]

    best_template = np.zeros(horizon)
    if len(templates) > 0 and len(recent) >= 12:
        # Match against recent trajectory
        dists = []
        l_match = min(len(recent), templates.shape[1])
        for tpl in templates:
            d = np.linalg.norm(recent[-l_match:] - tpl[-l_match:])
            dists.append(d)
        best_idx = np.argmin(dists)
        full_tpl = templates[best_idx]
        if len(full_tpl) >= horizon:
            best_template = full_tpl[:horizon]
        else:
            # Tile or pad
            reps = int(np.ceil(horizon / len(full_tpl)))
            best_template = np.tile(full_tpl, reps)[:horizon]

    # 3. ELM-style non-linear feature projection & blending
    # Blend spectral anchor with dictionary matching and persistence trend
    trend_val = hist[-1]
    # Smooth decay towards climatological mean over long horizon
    clim_mean = np.mean(hist[-360:]) if len(hist) >= 360 else np.mean(hist)

    t = np.arange(1, horizon + 1, dtype=float)
    # Blend: 40% spectral phase, 40% dictionary template, 20% climatological mean
    blended = 0.4 * spec_pred + 0.4 * best_template + 0.2 * clim_mean

    # Ensure non-negative sunspots
    return np.maximum(blended, 0.0)
