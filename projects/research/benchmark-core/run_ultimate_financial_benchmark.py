"""Ultimate Financial Benchmark Suite.
Compares our invented models (StateSpaceHybrid, BigDictELM, AMR-FBS, KNNForecaster)
and reference models (DLinear, ARIMA, ETS, Theta) on Cointegrated Spread & Directional Sign prediction across 10-year AAPL vs SPY history.
"""
from __future__ import annotations
import yfinance as yf
import numpy as np
import json
import pathlib
import matplotlib.pyplot as plt

from members.state_space_hybrid import fit_state_space_hybrid, pred_state_space_hybrid
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.knn_feature_forecaster import KNNFeatureForecaster
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_arima, pred_arima, fit_ets, pred_ets, fit_theta, pred_theta

try:
    from members.big_dict_elm import BigDictELM
    _HAS_BIGDICT = True
except Exception:
    BigDictELM = None
    _HAS_BIGDICT = False

def get_financial_data(n=2500):
    tk_aapl = yf.Ticker("AAPL")
    df_aapl = tk_aapl.history(period="10y")
    aapl = df_aapl['Adj Close'].values if 'Adj Close' in df_aapl.columns else df_aapl['Close'].values

    tk_spy = yf.Ticker("SPY")
    df_spy = tk_spy.history(period="10y")
    spy = df_spy['Adj Close'].values if 'Adj Close' in df_spy.columns else df_spy['Close'].values

    min_len = min(len(aapl), len(spy))
    return np.array(aapl[-min_len:], dtype=float)[-n:], np.array(spy[-min_len:], dtype=float)[-n:]

def run_benchmark():
    print("Fetching 10-year AAPL and SPY data for ultimate financial benchmark...")
    aapl, spy = get_financial_data(2500)

    H = 24
    lookback = 96
    test_len = 200
    origins = [len(aapl) - test_len + i * 40 for i in range(5)]

    models_def = {
        "StateSpaceHybrid": (fit_state_space_hybrid, lambda m, hist, h: pred_state_space_hybrid(m, hist)),
        "AMR-FBS": (lambda tr, h: fit_amr_fbs(tr, h), lambda m, hist, h: pred_amr_fbs(m, hist)),
        "KNNForecaster": (lambda tr, h: KNNFeatureForecaster(input_length=lookback).fit(tr, h), lambda m, hist, h: m.predict_hist(hist)),
        "DLinear": (fit_dlinear, lambda m, hist, h: pred_dlinear(m, hist)),
        "ARIMA": (fit_arima, lambda m, hist, h: pred_arima(m, hist)),
        "ETS": (fit_ets, lambda m, hist, h: pred_ets(m, hist)),
        "Theta": (fit_theta, lambda m, hist, h: pred_theta(m, hist)),
    }

    if _HAS_BIGDICT:
        models_def["BigDictELM"] = (lambda tr, h: BigDictELM(input_length=lookback).fit(tr, horizon=h), lambda m, hist, h: m.predict(hist))

    metrics = {name: {"spread_maes": [], "dir_correct": 0, "dir_total": 0} for name in models_def}

    last_run_data = {}

    for idx, orig in enumerate(origins):
        print(f"\n--- Origin {idx+1}/5 (Index {orig}) ---")
        train_aapl = aapl[:orig]
        actual_aapl = aapl[orig:orig+H]
        hist_aapl = train_aapl[-lookback:]

        train_spy = spy[:orig]
        actual_spy = spy[orig:orig+H]
        hist_spy = train_spy[-lookback:]

        # Cointegrated spread target: log(AAPL) - log(SPY)
        actual_spread = np.log(actual_aapl + 1e-8) - np.log(actual_spy + 1e-8)
        train_spread = np.log(train_aapl + 1e-8) - np.log(train_spy + 1e-8)
        hist_spread = train_spread[-lookback:]

        current_spread = float(train_spread[-1])

        origin_preds = {}

        for name, (fit_fn, pred_fn) in models_def.items():
            try:
                import time
                t0 = time.time()
                m = fit_fn(train_spread, H)
                pred = np.asarray(pred_fn(m, hist_spread, H), dtype=float).ravel()[:H]
                dt = time.time() - t0

                if len(pred) == H:
                    origin_preds[name] = pred
                    mae = float(np.mean(np.abs(actual_spread - pred)))
                    metrics[name]["spread_maes"].append(mae)

                    act_dir = np.sign(actual_spread[-1] - current_spread)
                    pred_dir = np.sign(pred[-1] - current_spread)
                    if act_dir == pred_dir:
                        metrics[name]["dir_correct"] += 1
                    metrics[name]["dir_total"] += 1

                    print(f"  {name:16s} | Spread MAE: {mae:.4f} | Dir Acc: {metrics[name]['dir_correct']/metrics[name]['dir_total']*100:5.1f}% | Time: {dt:.2f}s")
            except Exception as e:
                print(f"  {name:16s} | ERROR: {e}")

        last_run_data = {
            "actual_spread": actual_spread,
            "hist_spread": hist_spread,
            "preds": origin_preds
        }

    # Summary report
    summary = {}
    print("\n==================================================")
    print("=== ULTIMATE FINANCIAL BENCHMARK SUMMARY (AAPL vs SPY Spread) ===")
    print("==================================================")
    for name, data in metrics.items():
        if data["spread_maes"]:
            mean_mae = np.mean(data["spread_maes"])
            dir_acc = (data["dir_correct"] / data["dir_total"] * 100.0) if data["dir_total"] > 0 else 0.0
            summary[name] = {"mean_spread_mae": mean_mae, "directional_accuracy_pct": dir_acc}
            print(f"  {name:18s} : Spread MAE {mean_mae:.4f} | Directional Accuracy {dir_acc:5.2f}%")

    pathlib.Path("results").mkdir(exist_ok=True)
    with open("results_ultimate_financial.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSaved ultimate financial benchmark results to results_ultimate_financial.json")

    # Generate final comparison plot for the last origin
    pathlib.Path("plots").mkdir(exist_ok=True)
    plt.figure(figsize=(12, 6))
    t_hist = np.arange(-len(last_run_data["hist_spread"]), 0)
    t_future = np.arange(0, H)

    plt.plot(t_hist, last_run_data["hist_spread"], label="Spread History", color="black", linewidth=1.5)
    plt.plot(t_future, last_run_data["actual_spread"], label="Actual Future Spread", color="tab:gray", linewidth=2, marker="o", markersize=4)

    colors = {
        "StateSpaceHybrid": "tab:red",
        "AMR-FBS": "tab:orange",
        "BigDictELM": "tab:blue",
        "KNNForecaster": "tab:cyan",
        "DLinear": "tab:green",
        "ARIMA": "tab:purple",
        "ETS": "tab:brown",
        "Theta": "tab:pink"
    }

    for name, pred in last_run_data.get("preds", {}).items():
        mae = float(np.mean(np.abs(last_run_data["actual_spread"] - pred)))
        plt.plot(t_future, pred, label=f"{name} (MAE: {mae:.4f})", color=colors.get(name, "gray"), linewidth=1.5)

    plt.axvline(0, color="red", linestyle=":", alpha=0.7)
    plt.title("Ultimate Financial Benchmark: Cointegrated Spread Forecasting (AAPL vs SPY, H=24)", fontsize=13, fontweight="bold")
    plt.xlabel("Trading Days Relative to Origin", fontsize=11)
    plt.ylabel("Log-Spread (log(AAPL) - log(SPY))", fontsize=11)
    plt.legend(loc="upper left", fontsize=9, frameon=True)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out_plot = "plots/ultimate_financial_forecasts.png"
    plt.savefig(out_plot, dpi=300)
    print(f"Saved ultimate financial forecast plot to {out_plot}")

if __name__ == "__main__":
    run_benchmark()
