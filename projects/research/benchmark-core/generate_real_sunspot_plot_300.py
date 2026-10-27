"""Generate professional real sunspot prediction plots for horizon 300 using our best novel models."""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from bench import (
    get_sunspot,
    fit_bigdict, pred_bigdict,
    fit_det_esn, pred_det_esn,
    fit_subband_bigdict, pred_subband_bigdict,
    fit_rff, pred_rff
)
from sunspot_hybrid import hybrid_sunspot_forecast
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_theta, pred_theta

def main():
    print("Loading real monthly sunspot dataset...")
    series = get_sunspot(2600)

    origin = 2300
    horizon = 300
    lookback = 120

    history = np.asarray(series[:origin], dtype=float)
    actual = np.asarray(series[origin:origin+horizon], dtype=float)

    print(f"Evaluating models on real sunspot data (Origin={origin}, Horizon={horizon})...")

    preds = {}

    # 1. Hybrid Low-Freq + Residual (Novel)
    try:
        p = hybrid_sunspot_forecast(history, history[-lookback:], horizon)
        preds["Hybrid Low-Freq + Residual (Ours)"] = np.asarray(p, dtype=float).ravel()[:horizon]
    except Exception as e:
        print(f"Hybrid failed: {e}")

    # 2. AMR-FBS (Adaptive Multi-Resolution Fractional Basis Search)
    try:
        m_amr = fit_amr_fbs(history, horizon)
        p = pred_amr_fbs(m_amr, history[-lookback:])
        preds["AMR-FBS (Ours)"] = np.asarray(p, dtype=float).ravel()[:horizon]
    except Exception as e:
        print(f"AMR-FBS failed: {e}")

    # 3. BigDict ELM (Dictionary Learning + Extreme Learning Machine)
    try:
        m_bd = fit_bigdict(history, horizon)
        p = pred_bigdict(m_bd, history[-lookback:])
        preds["BigDict-ELM (Ours)"] = np.asarray(p, dtype=float).ravel()[:horizon]
    except Exception as e:
        print(f"BigDict-ELM failed: {e}")

    # 4. Deterministic ESN (Echo State Network)
    try:
        m_esn = fit_det_esn(history, horizon)
        p = pred_det_esn(m_esn, history[-lookback:])
        preds["Deterministic ESN"] = np.asarray(p, dtype=float).ravel()[:horizon]
    except Exception as e:
        print(f"Deterministic ESN failed: {e}")

    # 5. DLinear Baseline
    try:
        m_dl = fit_dlinear(history, horizon)
        p = pred_dlinear(m_dl, history[-lookback:])
        preds["DLinear"] = np.asarray(p, dtype=float).ravel()[:horizon]
    except Exception as e:
        print(f"DLinear failed: {e}")

    # 6. Theta Baseline
    try:
        m_th = fit_theta(history, horizon)
        p = pred_theta(m_th, history[-lookback:])
        preds["Theta"] = np.asarray(p, dtype=float).ravel()[:horizon]
    except Exception as e:
        print(f"Theta failed: {e}")

    # Print MAEs
    print("\n--- Horizon 300 MAE Scores on Real Sunspots ---")
    for name, p in preds.items():
        mae = float(np.mean(np.abs(p - actual)))
        print(f"{name:35s} | MAE: {mae:.3f}")

    # Plotting
    Path("plots").mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(16, 7))

    t_hist = np.arange(-lookback, 0)
    t_fut = np.arange(0, horizon)

    ax.plot(t_hist, history[-lookback:], color="black", linewidth=1.5, label="Historical Sunspots (Context)")
    ax.plot(t_fut, actual, color="black", linewidth=2.5, label="Actual Ground Truth (Horizon 300)")

    styles = {
        "Hybrid Low-Freq + Residual (Ours)": ("tab:red", "-"),
        "AMR-FBS (Ours)": ("tab:blue", "-"),
        "BigDict-ELM (Ours)": ("tab:purple", "-."),
        "Deterministic ESN": ("tab:green", "--"),
        "DLinear": ("tab:orange", ":"),
        "Theta": ("tab:brown", "--")
    }

    for name, p in preds.items():
        if len(p) == horizon:
            mae = np.mean(np.abs(p - actual))
            color, ls = styles.get(name, ("gray", "-"))
            ax.plot(t_fut, p, color=color, linestyle=ls, linewidth=1.8, label=f"{name} [MAE: {mae:.2f}]")

    ax.axvline(0, color="gray", linestyle="--", alpha=0.7, label="Forecast Origin (t=0)")
    ax.set_title("Long-Term Real Sunspot Forecasting (Horizon H = 300 Months) — Best Novel Models vs SOTA", fontsize=14, fontweight="bold")
    ax.set_xlabel("Months Relative to Forecast Origin", fontsize=12)
    ax.set_ylabel("Monthly Sunspot Number", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", fontsize=10, ncol=2, frameon=True)

    fig.tight_layout()

    out_paths = [
        "plots/real_sunspot_forecasts_300.png",
        "plots/sunspot_longterm_forecasts_300.png"
    ]
    for out in out_paths:
        fig.savefig(out, dpi=200)
        print(f"Saved plot to {out}")
    plt.close(fig)

if __name__ == "__main__":
    main()
