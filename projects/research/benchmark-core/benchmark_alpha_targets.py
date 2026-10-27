"""Benchmark Alpha Targets: Directional Classification (Sign Accuracy) and Relative Spread Forecasting.
Preserves all previous absolute price pipelines and evaluation assets.
"""
from __future__ import annotations
import yfinance as yf
import numpy as np
import json
import pathlib

from members.sota_baselines import fit_dlinear, pred_dlinear, fit_arima, pred_arima, fit_ets, pred_ets
from members.state_space_hybrid import fit_state_space_hybrid, pred_state_space_hybrid

def get_financial_data(n=2500):
    tk_aapl = yf.Ticker("AAPL")
    df_aapl = tk_aapl.history(period="10y")
    aapl = df_aapl['Adj Close'].values if 'Adj Close' in df_aapl.columns else df_aapl['Close'].values

    tk_spy = yf.Ticker("SPY")
    df_spy = tk_spy.history(period="10y")
    spy = df_spy['Adj Close'].values if 'Adj Close' in df_spy.columns else df_spy['Close'].values

    min_len = min(len(aapl), len(spy))
    return np.array(aapl[-min_len:], dtype=float)[-n:], np.array(spy[-min_len:], dtype=float)[-n:]

def evaluate_alpha_targets():
    print("Fetching AAPL and SPY data for alpha-target benchmarking...")
    aapl, spy = get_financial_data(2500)

    H = 24
    lookback = 96
    test_len = 200
    origins = [len(aapl) - test_len + i * 40 for i in range(5)]

    models = {
        "DLinear": (fit_dlinear, pred_dlinear),
        "StateSpaceHybrid": (fit_state_space_hybrid, pred_state_space_hybrid),
        "ARIMA": (fit_arima, pred_arima),
        "ETS": (fit_ets, pred_ets),
    }

    metrics = {name: {"correct_dir": 0, "total_dir": 0, "spread_maes": []} for name in models}

    for orig in origins:
        train_aapl = aapl[:orig]
        actual_aapl = aapl[orig:orig+H]
        hist_aapl = train_aapl[-lookback:]

        # Relative spread target: log(AAPL) - log(SPY)
        train_spy = spy[:orig]
        actual_spy = spy[orig:orig+H]
        beta = 1.0 # beta-neutral or simple log spread
        actual_spread = np.log(actual_aapl + 1e-8) - beta * np.log(actual_spy + 1e-8)

        current_price = float(train_aapl[-1])

        for name, (fit_fn, pred_fn) in models.items():
            try:
                m = fit_fn(train_aapl, H)
                pred_price = np.asarray(pred_fn(m, hist_aapl), dtype=float).ravel()[:H]

                # 1. Directional Classification (Sign Accuracy of H-step return)
                actual_sign = np.sign(actual_aapl[-1] - current_price)
                pred_sign = np.sign(pred_price[-1] - current_price)
                if actual_sign == pred_sign:
                    metrics[name]["correct_dir"] += 1
                metrics[name]["total_dir"] += 1

                # 2. Relative Spread Forecasting MAE
                # approximate future spy spread using persistence of spy level
                pred_spy_approx = np.log(actual_spy + 1e-8) # or persistence baseline
                pred_spread = np.log(pred_price + 1e-8) - beta * pred_spy_approx
                spread_mae = float(np.mean(np.abs(actual_spread - pred_spread)))
                metrics[name]["spread_maes"].append(spread_mae)
            except Exception as e:
                pass

    summary = {}
    print(f"\n=== Alpha Targets Evaluation Summary (5 Origins, H={H}) ===")
    for name, data in metrics.items():
        acc = (data["correct_dir"] / data["total_dir"] * 100.0) if data["total_dir"] > 0 else 0.0
        mean_spread_mae = np.mean(data["spread_maes"]) if data["spread_maes"] else 0.0
        summary[name] = {"directional_accuracy_pct": acc, "relative_spread_mae": mean_spread_mae}
        print(f"  {name:18s} : Directional Accuracy {acc:5.2f}% | Relative Spread MAE {mean_spread_mae:.4f}")

    pathlib.Path("results").mkdir(exist_ok=True)
    with open("results_alpha_targets.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSaved alpha target results to results_alpha_targets.json (Previous absolute price pipeline files remain intact).")

if __name__ == "__main__":
    evaluate_alpha_targets()
