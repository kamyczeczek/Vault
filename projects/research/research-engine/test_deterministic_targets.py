"""Evaluation of Highly Deterministic, Stationary Financial Targets.

Tests:
1. Rolling Z-Score (Mean-Reversion bounded target).
2. Fractional Differencing (Stationary memory-preserving target).
"""
from __future__ import annotations
import yfinance as yf
import numpy as np
import sys
import pathlib

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from members.state_space_hybrid import fit_state_space_hybrid, pred_state_space_hybrid
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_arima, pred_arima

def fractional_difference(series, d=0.4, lag_window=20):
    """Compute fractional differencing to achieve stationarity while retaining memory."""
    x = np.asarray(series, dtype=float)
    weights = [1.0]
    for k in range(1, lag_window):
        weights.append(-weights[-1] * (d - k + 1) / k)
    weights = np.array(weights[::-1])

    out = np.zeros_like(x)
    for i in range(lag_window, len(x)):
        out[i] = np.sum(weights * x[i-lag_window:i])
    return out

def evaluate_deterministic_targets():
    print("Fetching AAPL data for deterministic target evaluation...")
    df = yf.Ticker("AAPL").history(period="5y")
    prices = df['Adj Close'].values if 'Adj Close' in df.columns else df['Close'].values
    prices = np.array(prices, dtype=float)

    window = 20
    rolling_mean = np.convolve(prices, np.ones(window)/window, mode='valid')
    rolling_std = np.array([np.std(prices[i:i+window]) for i in range(len(prices)-window+1)])

    # Target 1: Rolling Z-Score (Mean-Reverting Bounded Target)
    z_scores = (prices[window-1:] - rolling_mean) / (rolling_std + 1e-8)

    H = 10
    lookback = 64
    test_len = 200
    origins = [len(z_scores) - test_len + i * 40 for i in range(5)]

    errors = {"StateSpaceHybrid": [], "DLinear": []}

    for orig in origins:
        train = z_scores[:orig]
        actual = z_scores[orig:orig+H]
        hist = train[-lookback:]

        try:
            m_ss = fit_state_space_hybrid(train, H)
            p_ss = pred_state_space_hybrid(m_ss, hist)
            errors["StateSpaceHybrid"].append(np.mean(np.abs(p_ss[:H] - actual)))
        except Exception:
            pass

        try:
            m_dl = fit_dlinear(train, H)
            p_dl = pred_dl = pred_dlinear(m_dl, hist)
            errors["DLinear"].append(np.mean(np.abs(p_dl[:H] - actual)))
        except Exception:
            pass

    print("\n=== Evaluating Bounded Stationary Z-Score Target (Mean-Reversion) ===")
    for m, errs in errors.items():
        if len(errs) > 0:
            print(f"  {m:18s} : Z-Score MAE {np.mean(errs):.4f}")

    # Target 2: Fractional Differencing
    frac_series = fractional_difference(prices, d=0.4)
    frac_errors = {"StateSpaceHybrid": [], "DLinear": []}

    for orig in origins:
        train = frac_series[:orig]
        actual = frac_series[orig:orig+H]
        hist = train[-lookback:]

        try:
            m_ss = fit_state_space_hybrid(train, H)
            p_ss = pred_state_space_hybrid(m_ss, hist)
            frac_errors["StateSpaceHybrid"].append(np.mean(np.abs(p_ss[:H] - actual)))
        except Exception:
            pass

        try:
            m_dl = fit_dlinear(train, H)
            p_dl = pred_dlinear(m_dl, hist)
            frac_errors["DLinear"].append(np.mean(np.abs(p_dl[:H] - actual)))
        except Exception:
            pass

    print("\n=== Evaluating Stationary Fractional Differencing Target (d=0.4) ===")
    for m, errs in frac_errors.items():
        if len(errs) > 0:
            print(f"  {m:18s} : FracDiff MAE {np.mean(errs):.4f}")

if __name__ == "__main__":
    evaluate_deterministic_targets()
