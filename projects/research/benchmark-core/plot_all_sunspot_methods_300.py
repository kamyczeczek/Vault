"""Plot ALL sunspot forecasting methods (including all novel models and baselines) for horizon 300 on real sunspot data."""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from bench import get_sunspot
from sunspot_methods import get_sunspot_methods
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs

def main():
    print("Loading real monthly sunspot data...")
    series = get_sunspot(2600)
    origin = 2300
    horizon = 300
    lookback = 120

    history = np.asarray(series[:origin], dtype=float)
    actual = np.asarray(series[origin:origin+horizon], dtype=float)

    print(f"Running all sunspot methods (Origin={origin}, Horizon={horizon})...")

    forecasts = {}

    # 1. Get registry methods from sunspot_methods.py
    for name, method in get_sunspot_methods().items():
        try:
            pred = np.asarray(method(history, history[-lookback:], horizon), dtype=float).ravel()
            if len(pred) >= horizon and np.isfinite(pred[:horizon]).all():
                forecasts[name] = pred[:horizon]
        except Exception as e:
            print(f"Skipping {name}: {e}")

    # 2. Add AMR-FBS explicitly
    try:
        m_amr = fit_amr_fbs(history, horizon)
        pred_amr = np.asarray(pred_amr_fbs(m_amr, history[-lookback:]), dtype=float).ravel()
        if len(pred_amr) >= horizon:
            forecasts["amr_fbs"] = pred_amr[:horizon]
    except Exception as e:
        print(f"Skipping amr_fbs: {e}")

    print(f"\nSuccessfully generated forecasts for {len(forecasts)} methods:")
    mae_scores = {}
    for name, pred in forecasts.items():
        mae = float(np.mean(np.abs(pred - actual)))
        mae_scores[name] = mae
        print(f"  - {name:30s} | MAE: {mae:.3f}")

    # Plotting all methods
    Path("plots").mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(18, 9))

    t_hist = np.arange(-lookback, 0)
    t_fut = np.arange(horizon)

    ax.plot(t_hist, history[-lookback:], color="black", linewidth=1.5, label="Historical Sunspots (Context)")
    ax.plot(t_fut, actual, color="black", linewidth=3.0, label="Actual Ground Truth (Horizon 300)")

    # Sort methods by MAE
    sorted_methods = sorted(mae_scores.items(), key=lambda x: x[1])

    for name, mae in sorted_methods:
        pred = forecasts[name]
        label = f"{name} (MAE: {mae:.2f})"
        ax.plot(t_fut, pred, linewidth=1.4, alpha=0.85, label=label)

    ax.axvline(0, color="red", linestyle="--", alpha=0.7, label="Forecast Origin (t=0)")
    ax.set_title(f"Comprehensive Sunspot Forecasts — All {len(forecasts)} Models (Horizon H = {horizon} Months)", fontsize=15, fontweight="bold")
    ax.set_xlabel("Months Relative to Forecast Origin", fontsize=12)
    ax.set_ylabel("Monthly Sunspot Number", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", fontsize=9, ncol=3, frameon=True)

    fig.tight_layout()
    output_path = "plots/sunspot_longterm_all_models_300.png"
    fig.savefig(output_path, dpi=200)
    print(f"\nSaved comprehensive plot to {output_path}")
    plt.close(fig)

if __name__ == "__main__":
    main()
