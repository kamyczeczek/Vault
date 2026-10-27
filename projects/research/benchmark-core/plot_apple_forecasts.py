"""Generate and Save Prediction Forecast Plots for Apple Stock (AAPL).
Compares AMR-FBS, DLinear, Theta, ARIMA, and ETS on the latest rollout window.
"""
from __future__ import annotations
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import pathlib

from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_theta, pred_theta, fit_arima, pred_arima, fit_ets, pred_ets

def main():
    print("Fetching AAPL data for visualization...")
    df = yf.download("AAPL", period="2y", interval="1d", progress=False)
    if isinstance(df.columns, np.ndarray) or hasattr(df.columns, "levels"):
        # Handle multi-index columns if present in newer yfinance versions
        try:
            prices = df["Close"].iloc[:, 0].values.astype(float)
        except Exception:
            prices = df["Close"].values.astype(float)
    else:
        prices = df["Close"].values.astype(float)

    # Remove NaNs if any
    prices = prices[~np.isnan(prices)]

    H = 24
    train = prices[:-H]
    test = prices[-H:]
    hist = train

    print(f"Fitting models on AAPL train set (len={len(train)})...")
    models = {}
    models["AMR-FBS (Ours)"] = (fit_amr_fbs(train, H), pred_amr_fbs)
    models["DLinear"] = (fit_dlinear(train, H), pred_dlinear)
    models["Theta"] = (fit_theta(train, H), pred_theta)
    models["ARIMA"] = (fit_arima(train, H), pred_arima)
    models["ETS"] = (fit_ets(train, H), pred_ets)

    preds = {}
    for name, (model, pred_fn) in models.items():
        try:
            p = pred_fn(model, hist)
            preds[name] = np.asarray(p, dtype=float).ravel()[:H]
        except Exception as e:
            print(f"Model {name} failed: {e}")

    # Plotting
    pathlib.Path("plots").mkdir(exist_ok=True)
    plt.figure(figsize=(12, 6))

    # Plot recent history (last 60 days) + actual test
    context_days = 60
    t_hist = np.arange(-context_days, 0)
    t_future = np.arange(0, H)

    plt.plot(t_hist, hist[-context_days:], label="AAPL History (Actual)", color="black", linewidth=2)
    plt.plot(t_future, test, label="AAPL Future (Actual Test)", color="tab:blue", linewidth=2, marker="o")

    colors = {"AMR-FBS (Ours)": "tab:red", "DLinear": "tab:orange", "Theta": "tab:green", "ARIMA": "tab:purple", "ETS": "tab:brown"}
    styles = {"AMR-FBS (Ours)": "-", "DLinear": "--", "Theta": "-.", "ARIMA": ":", "ETS": "-"}

    for name, pred in preds.items():
        plt.plot(t_future, pred, label=f"{name} (MAE: {np.mean(np.abs(test - pred)):.2f})",
                 color=colors.get(name, "gray"), linestyle=styles.get(name, "-"), linewidth=1.5)

    plt.axvline(0, color="gray", linestyle=":", alpha=0.7)
    plt.title("Apple Stock (AAPL) 24-Day Out-of-Sample Forecast Comparison", fontsize=14, fontweight="bold")
    plt.xlabel("Trading Days Relative to Forecast Origin (t=0)", fontsize=12)
    plt.ylabel("Stock Price ($)", fontsize=12)
    plt.legend(loc="upper left", frameon=True)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out_path = "plots/apple_forecast_comparison.png"
    plt.savefig(out_path, dpi=300)
    print(f"Saved Apple stock prediction plot to {out_path}")

if __name__ == "__main__":
    main()
