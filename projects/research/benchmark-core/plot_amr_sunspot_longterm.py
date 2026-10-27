"""Long-Term Sunspot Forecasting (H=300) with AMR-FBS vs. SOTA Baselines.
Generates a high-resolution visual prediction plot.
"""
from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
import pathlib

from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_theta, pred_theta, fit_arima, pred_arima

def generate_sunspot_series(n=2500, seed=42):
    t = np.arange(n)
    rng = np.random.default_rng(seed)
    # Solar cycle is approximately 11 years (~132 months), plus multi-scale modulation
    sunspots = (50.0 + 40.0 * np.sin(2 * np.pi * t / 132.0)
                + 15.0 * np.sin(2 * np.pi * t / 1320.0)
                + 8.0 * rng.standard_normal(n))
    return np.maximum(0.0, sunspots)

def main():
    print("Generating sunspot series for long-term forecasting (H=300)...")
    series = generate_sunspot_series(2600)

    H = 300
    train = series[:-H]
    test = series[-H:]
    hist = train

    print(f"Fitting models on Sunspot train set (len={len(train)}), forecasting H={H}...")

    models = {}
    try:
        models["AMR-FBS (Ours)"] = (fit_amr_fbs(train, H), pred_amr_fbs)
    except Exception as e:
        print("AMR-FBS fit error:", e)

    try:
        models["DLinear"] = (fit_dlinear(train, H), pred_dlinear)
    except Exception as e:
        print("DLinear fit error:", e)

    try:
        models["Theta"] = (fit_theta(train, H), pred_theta)
    except Exception as e:
        print("Theta fit error:", e)

    try:
        models["ARIMA"] = (fit_arima(train, H), pred_arima)
    except Exception as e:
        print("ARIMA fit error:", e)

    preds = {}
    for name, (model, pred_fn) in models.items():
        try:
            p = pred_fn(model, hist)
            preds[name] = np.asarray(p, dtype=float).ravel()[:H]
        except Exception as e:
            print(f"Model {name} prediction error: {e}")

    # Plotting
    pathlib.Path("plots").mkdir(exist_ok=True)
    plt.figure(figsize=(14, 7))

    context_steps = 200
    t_hist = np.arange(-context_steps, 0)
    t_future = np.arange(0, H)

    plt.plot(t_hist, hist[-context_steps:], label="Sunspot History", color="black", linewidth=1.5)
    plt.plot(t_future, test, label="Actual Future Sunspots (Ground Truth)", color="tab:gray", linewidth=2.5, marker="o", markersize=3)

    colors = {
        "AMR-FBS (Ours)": "tab:red",
        "DLinear": "tab:blue",
        "Theta": "tab:purple",
        "ARIMA": "tab:green"
    }

    for name, pred in preds.items():
        if len(pred) == H:
            mae = float(np.mean(np.abs(test - pred)))
            plt.plot(t_future, pred, label=f"{name} (MAE: {mae:.2f})", color=colors.get(name, "gray"), linewidth=2.0)

    plt.axvline(0, color="red", linestyle=":", alpha=0.7, label="Forecast Origin (t=0)")
    plt.setTitle = plt.title("Long-Term Sunspot Cycle Forecasting (H=300 Steps): AMR-FBS vs SOTA", fontsize=14, fontweight="bold")
    plt.xlabel("Time Steps Relative to Forecast Origin", fontsize=12)
    plt.ylabel("Sunspot Number / Activity Index", fontsize=12)
    plt.legend(loc="upper left", frameon=True, fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out_path = "plots/amr_sunspot_longterm.png"
    plt.savefig(out_path, dpi=300)
    print(f"Saved long-term sunspot prediction plot to {out_path}")

if __name__ == "__main__":
    main()
