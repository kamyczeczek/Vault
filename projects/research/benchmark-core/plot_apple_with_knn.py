"""Multi-Origin AAPL Forecasting with KNNFeatureForecaster and SOTA Baselines.
Generates multi-panel comparison plots including KNN-based motif matching.
"""
from __future__ import annotations
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import pathlib

from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_theta, pred_theta, fit_arima, pred_arima, fit_ets, pred_ets
from members.knn_feature_forecaster import KNNFeatureForecaster

try:
    from members.big_dict_elm import BigDictELM
    _HAS_BIGDICT = True
except Exception:
    BigDictELM = None
    _HAS_BIGDICT = False

def main():
    print("Fetching 10-year AAPL historical data...")
    df = yf.download("AAPL", period="max", interval="1d", progress=False)
    if isinstance(df.columns, np.ndarray) or hasattr(df.columns, "levels"):
        try:
            prices = df["Close"].iloc[:, 0].values.astype(float)
        except Exception:
            prices = df["Close"].values.astype(float)
    else:
        prices = df["Close"].values.astype(float)

    prices = prices[~np.isnan(prices)]
    # Use last ~2000 trading days
    if len(prices) > 2000:
        prices = prices[-2000:]

    H = 24
    num_origins = 5
    # Select 5 origin cutoffs near the end of the series
    origins = [len(prices) - 150 * i - H for i in range(num_origins - 1, -1, -1)]

    print(f"Running multi-origin evaluation across {num_origins} origins (H={H}) with KNN integration...")

    results_summary = {name: [] for name in ["KNNFeatureForecaster", "BigDictELM", "AMR-FBS", "DLinear", "Theta", "ARIMA", "ETS"]}

    fig, axes = plt.subplots(num_origins, 1, figsize=(14, 3.5 * num_origins), sharex=False)
    if num_origins == 1:
        axes = [axes]

    colors = {
        "KNNFeatureForecaster": "tab:red",
        "BigDictELM": "tab:blue",
        "AMR-FBS": "tab:orange",
        "DLinear": "tab:green",
        "Theta": "tab:purple",
        "ARIMA": "tab:brown",
        "ETS": "tab:pink"
    }

    for idx, origin_idx in enumerate(origins):
        ax = axes[idx]
        train = prices[:origin_idx]
        test = prices[origin_idx:origin_idx+H]
        hist = train

        if len(test) < H:
            continue

        # Fit models
        models = {}
        try:
            knn = KNNFeatureForecaster(input_length=96, k_neighbors=24)
            knn.fit(train, H)
            models["KNNFeatureForecaster"] = (knn, lambda m, h: m.predict_hist(h))
        except Exception as e:
            print(f"KNN fit failed at origin {idx}: {e}")

        if _HAS_BIGDICT:
            try:
                bd = BigDictELM(input_length=96)
                bd.fit(train, horizon=H)
                models["BigDictELM"] = (bd, lambda m, h: m.predict(h))
            except Exception:
                pass

        try:
            models["AMR-FBS"] = (fit_amr_fbs(train, H), pred_amr_fbs)
        except Exception:
            pass

        try:
            models["DLinear"] = (fit_dlinear(train, H), pred_dlinear)
        except Exception:
            pass

        try:
            models["Theta"] = (fit_theta(train, H), pred_theta)
        except Exception:
            pass

        try:
            models["ARIMA"] = (fit_arima(train, H), pred_arima)
        except Exception:
            pass

        try:
            models["ETS"] = (fit_ets(train, H), pred_ets)
        except Exception:
            pass

        # Predict & evaluate
        context_days = 60
        t_hist = np.arange(-context_days, 0)
        t_future = np.arange(0, H)

        ax.plot(t_hist, hist[-context_days:], label="History", color="black", linewidth=1.5)
        ax.plot(t_future, test, label="Actual Future", color="tab:gray", linewidth=2, marker="o", markersize=4)

        for name, (model, pred_fn) in models.items():
            try:
                pred = np.asarray(pred_fn(model, hist), dtype=float).ravel()[:H]
                if len(pred) == H:
                    mae = float(np.mean(np.abs(test - pred)))
                    results_summary[name].append(mae)
                    ax.plot(t_future, pred, label=f"{name} (MAE:{mae:.2f})", color=colors.get(name, "gray"), linewidth=1.5)
            except Exception as e:
                pass

        ax.axvline(0, color="red", linestyle=":", alpha=0.7)
        ax.set_title(f"Apple Stock (AAPL) Forecast Origin #{idx+1} (Date Index ~{origin_idx})", fontsize=11, fontweight="bold")
        ax.set_ylabel("Price ($)", fontsize=10)
        ax.legend(loc="upper left", fontsize=8, frameon=True)
        ax.grid(True, alpha=0.3)

    plt.xlabel("Trading Days Relative to Origin", fontsize=11)
    plt.tight_layout()
    pathlib.Path("plots").mkdir(exist_ok=True)
    out_plot = "plots/apple_knn_multi_origin_forecasts.png"
    plt.savefig(out_plot, dpi=300)
    print(f"\nSaved multi-origin KNN Apple forecast plot to {out_plot}")

    print("\n=== Multi-Origin Average MAE Summary across AAPL cutoffs (with KNN) ===")
    for name, maes in results_summary.items():
        if maes:
            print(f"  {name:20s}: Mean MAE {np.mean(maes):.4f} (over {len(maes)} origins)")

if __name__ == "__main__":
    main()
