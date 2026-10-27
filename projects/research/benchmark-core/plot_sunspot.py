"""Generate and save prediction plot for sunspot test data comparing NLinear, BigDict ELM, Deterministic ESN, and Hybrid Pool H."""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pathlib

import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from bench import get_sunspot, fit_nlinear, pred_nlinear, fit_bigdict, pred_bigdict, fit_det_esn, pred_det_esn

def main():
    print("Loading sunspot dataset...")
    series = get_sunspot(2600)
    H = 24
    train = series[:2000]
    test_origin = 2000
    history = series[test_origin-96:test_origin]
    actual_future = series[test_origin:test_origin+H]

    print("Fitting models on sunspot training data...")
    # 1. NLinear
    m_nlin = fit_nlinear(train, H, 1.0)
    pred_nlin = np.asarray(pred_nlinear(m_nlin, history)).ravel()[:H]

    # 2. BigDict ELM
    m_big = fit_bigdict(train, H)
    pred_big = np.asarray(pred_bigdict(m_big, history)).ravel()[:H]

    # 3. Deterministic ESN
    m_esn = fit_det_esn(train, H)
    pred_esn = np.asarray(pred_det_esn(m_esn, history)).ravel()[:H]

    print("Generating plot...")
    plt.figure(figsize=(10, 5))
    time_past = np.arange(-96, 0)
    time_future = np.arange(0, H)

    plt.plot(time_past, history, label="Historical Context (Past 96)", color="black", linewidth=1.5)
    plt.plot(time_future, actual_future, label="Ground Truth Future ($H=24$)", color="blue", linewidth=2, marker="o")
    plt.plot(time_future, pred_nlin, label="NLinear Baseline", color="gray", linestyle="--", marker="x")
    plt.plot(time_future, pred_big, label="BigDict ELM", color="green", linestyle="-.", marker="s")
    plt.plot(time_future, pred_esn, label="Deterministic ESN", color="red", linestyle=":", marker="^")

    plt.axvline(0, color="gray", linestyle=":", alpha=0.7)
    plt.title("Sunspot Dataset ($H=24$) Forecast Comparison", fontsize=14, fontweight="bold")
    plt.xlabel("Time Steps Relative to Forecast Origin ($t=0$)", fontsize=12)
    plt.ylabel("Sunspot Activity Number", fontsize=12)
    plt.legend(frameon=True, facecolor="white", edgecolor="none")
    plt.grid(True, alpha=0.3)

    out_dir = pathlib.Path("results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "sunspot_forecast_plot.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved sunspot forecast plot to {out_path}")

if __name__ == "__main__":
    main()
