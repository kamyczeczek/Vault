"""Multi-Origin Diverse Backtesting for Sunspot Forecasting (Horizon H = 300).
Evaluates top models across multiple different historical starting points (origins) to test robustness against varying solar cycle phases (rising, peak, falling, solar minimum).
"""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from bench import get_sunspot
from sunspot_methods import get_sunspot_methods
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.amr_dynamo_attractor import fit_amr_dynamo_attractor, pred_amr_dynamo_attractor

def main():
    print("Loading full monthly sunspot dataset...")
    series = get_sunspot(3200)

    origins = [1800, 2000, 2200, 2300]
    horizon = 300
    lookback = 120

    key_model_names = [
        "amr_fbs",
        "bigdict_tree",
        "amr_tree_elm",
        "amr_dynamo_attractor",
        "bigdict_elm",
        "nlinear_a1",
        "persistence"
    ]

    all_methods = get_sunspot_methods()
    results = {name: [] for name in key_model_names}
    origin_actuals = {}

    print(f"\nRunning multi-origin evaluation (Horizon H={horizon}) across origins: {origins}")

    for origin in origins:
        if origin + horizon > len(series):
            continue

        history = np.asarray(series[:origin], dtype=float)
        actual = np.asarray(series[origin:origin+horizon], dtype=float)
        origin_actuals[origin] = actual

        print(f"\n--- Origin t = {origin} ---")
        for name in key_model_names:
            try:
                if name == "amr_fbs":
                    m = fit_amr_fbs(history, horizon)
                    pred = np.asarray(pred_amr_fbs(m, history[-lookback:]), dtype=float).ravel()[:horizon]
                elif name == "amr_dynamo_attractor":
                    m = fit_amr_dynamo_attractor(history, horizon)
                    pred = np.asarray(pred_amr_dynamo_attractor(m, history[-lookback:]), dtype=float).ravel()[:horizon]
                else:
                    method = all_methods[name]
                    pred = np.asarray(method(history, history[-lookback:], horizon), dtype=float).ravel()[:horizon]

                if len(pred) == horizon and np.isfinite(pred).all():
                    mae = float(np.mean(np.abs(pred - actual)))
                    results[name].append(mae)
                    print(f"  {name:25s} | MAE: {mae:.3f}")
                else:
                    results[name].append(np.nan)
                    print(f"  {name:25s} | MAE: INVALID")
            except Exception as e:
                results[name].append(np.nan)
                print(f"  {name:25s} | Error: {e}")

    # Summary table across origins
    print("\n" + "="*65)
    print(f"SUMMARY: Average Horizon {horizon} MAE Across Diverse Origins")
    print("="*65)
    for name in key_model_names:
        maes = [m for m in results[name] if not np.isnan(m)]
        avg_mae = np.mean(maes) if maes else float('inf')
        print(f"  {name:25s} | Mean MAE: {avg_mae:.3f} (over {len(maes)} origins)")

    # Plotting multi-origin forecasts
    Path("plots").mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(len(origins), 1, figsize=(14, 3.5 * len(origins)), sharex=False)
    if len(origins) == 1:
        axes = [axes]

    for idx, origin in enumerate(origins):
        ax = axes[idx]
        hist_win = series[max(0, origin-lookback):origin]
        act_win = origin_actuals[origin]

        t_hist = np.arange(-len(hist_win), 0)
        t_fut = np.arange(horizon)

        ax.plot(t_hist, hist_win, color="black", label="History (Context)")
        ax.plot(t_fut, act_win, color="black", linewidth=2.5, label="Actual Ground Truth")

        # Plot AMR-Dynamo-Attractor
        try:
            history = np.asarray(series[:origin], dtype=float)
            m = fit_amr_dynamo_attractor(history, horizon)
            pred_dyn = np.asarray(pred_amr_dynamo_attractor(m, history[-lookback:]), dtype=float).ravel()[:horizon]
            ax.plot(t_fut, pred_dyn, color="crimson", linewidth=2.0, label="AMR-Dynamo-Attractor (Ours)")
        except Exception:
            pass

        # Plot AMR-FBS
        try:
            m = fit_amr_fbs(history, horizon)
            pred_amr = np.asarray(pred_amr_fbs(m, history[-lookback:]), dtype=float).ravel()[:horizon]
            ax.plot(t_fut, pred_amr, color="dodgerblue", linewidth=1.5, linestyle="--", label="AMR-FBS")
        except Exception:
            pass

        ax.axvline(0, color="gray", linestyle=":", label="Origin (t=0)")
        ax.set_title(f"Sunspot Long-Horizon Forecast (Origin t={origin}, Horizon H={horizon})", fontsize=11, fontweight="bold")
        ax.set_ylabel("Sunspots")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left", fontsize=8, ncol=3)

    axes[-1].set_xlabel("Months Relative to Forecast Origin")
    fig.tight_layout()
    output_path = "plots/sunspot_multi_origin_evaluation_300.png"
    fig.savefig(output_path, dpi=200)
    print(f"\nSaved multi-origin evaluation plot to {output_path}")
    plt.close(fig)

if __name__ == "__main__":
    main()
