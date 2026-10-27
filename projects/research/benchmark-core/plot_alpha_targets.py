"""Visualization script for Relative Spread Forecasting (AAPL vs SPY).
Plots model predictions vs raw ground truth spread.
"""
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import sys
import pathlib

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from members.state_space_hybrid import fit_state_space_hybrid, pred_state_space_hybrid
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_arima, pred_arima, fit_ets, pred_ets

def plot_spread_forecasts():
    print("Fetching AAPL and SPY data for spread visualization...")
    tk_a = yf.Ticker("AAPL")
    tk_b = yf.Ticker("SPY")
    df_a = tk_a.history(period="5y")
    df_b = tk_b.history(period="5y")

    pa = df_a['Adj Close'].values if 'Adj Close' in df_a.columns else df_a['Close'].values
    pb = df_b['Adj Close'].values if 'Adj Close' in df_b.columns else df_b['Close'].values

    min_len = min(len(pa), len(pb))
    pa = pa[-min_len:]
    pb = pb[-min_len:]

    # Compute log spread: log(AAPL) - log(SPY)
    spread = np.log(pa) - np.log(pb)

    H = 24
    lookback = 96
    orig = len(spread) - 50 # recent cutoff

    train = spread[:orig]
    actual = spread[orig:orig+H]
    hist = train[-lookback:]

    # Models
    models = {}
    try:
        m_ss = fit_state_space_hybrid(train, H)
        models["StateSpaceHybrid"] = pred_state_space_hybrid(m_ss, hist)
    except Exception as e:
        print("SSM error:", e)

    try:
        m_dl = fit_dlinear(train, H)
        models["DLinear"] = pred_dlinear(m_dl, hist)
    except Exception:
        pass

    try:
        m_ar = fit_arima(train, H)
        models["ARIMA"] = pred_ar = pred_arima(m_ar, hist)
    except Exception:
        pass

    plt.figure(figsize=(12, 6), dpi=150)

    # Plot history tail
    hist_t = np.arange(-len(hist), 0)
    fut_t = np.arange(0, H)

    plt.plot(hist_t, hist, label="Historical Spread (Log AAPL - Log SPY)", color="black", linewidth=2)
    plt.plot(fut_t, actual, label="Ground Truth Future Spread", color="green", linewidth=2.5, linestyle="--")

    colors = {"StateSpaceHybrid": "purple", "DLinear": "blue", "ARIMA": "orange"}
    for name, pred in models.items():
        plt.plot(fut_t, pred[:H], label=f"{name} Prediction", color=colors.get(name, "red"), linewidth=2, alpha=0.85)

    plt.axvline(0, color="gray", linestyle=":", alpha=0.7, label="Forecast Origin")
    plt.title("Relative Value Forecast: AAPL vs. SPY Log Spread (H=24)", fontsize=14, fontweight="bold")
    plt.xlabel("Trading Days Relative to Origin", fontsize=12)
    plt.ylabel("Log Spread Value", fontsize=12)
    plt.legend(loc="upper left", frameon=True)
    plt.grid(True, alpha=0.3)

    pathlib.Path("plots").mkdir(exist_ok=True, parents=True)
    out_path = "plots/apple_relative_spread_forecasts.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"Saved relative spread prediction plot to {out_path}")

if __name__ == "__main__":
    plot_spread_forecasts()
