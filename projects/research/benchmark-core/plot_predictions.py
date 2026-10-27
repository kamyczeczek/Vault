"""Generate high-resolution prediction vs ground truth visual comparison plots.

Plots rolling forecast windows across all benchmark tasks for:
1. Ground Truth Actuals
2. NLinear (Baseline)
3. SWT Subband Expert (cA1)
4. BigDictELM (Multi-Family Activation + Multi-Family Wavelet Bank + Ridge)
"""
from __future__ import annotations
import sys, pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from bench import TASKS, get_series, fit_nlinear, pred_nlinear, fit_subbands, pred_subband
from members.big_dict_elm import BigDictELM

def fit_bigdict(train, H):
    m = BigDictELM(input_length=96, hidden=384, act_type="multi_family")
    m.fit(train, horizon=H)
    return m

def pred_bigdict(m, h):
    return m.predict_hist(h)

def generate_plots(output_dir="plots"):
    out_path = pathlib.Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 6 Tasks grid: 3 rows x 2 cols
    fig, axes = plt.subplots(3, 2, figsize=(18, 12), dpi=150)
    axes = axes.flatten()

    for idx, (task_name, H, task_type) in enumerate(TASKS):
        ax = axes[idx]
        series = get_series(task_name)
        train = series[:2000]

        # Fit models on train
        m_nlin = fit_nlinear(train, H, 1.0)
        m_sub = fit_subbands(train, H)
        m_elm = fit_bigdict(train, H)

        # Pick window 0 for clean evaluation visualization
        origin = 2000
        lookback = 96
        context = series[origin - lookback:origin]
        actual_future = series[origin:origin + H]

        p_nlin = np.asarray(pred_nlinear(m_nlin, context)[:H]).ravel()
        p_sub = np.asarray(pred_subband(m_sub, context, "cA1")[:H]).ravel()
        p_elm = np.asarray(pred_bigdict(m_elm, context)[:H]).ravel()

        mae_nlin = float(np.mean(np.abs(p_nlin - actual_future)))
        mae_sub = float(np.mean(np.abs(p_sub - actual_future)))
        mae_elm = float(np.mean(np.abs(p_elm - actual_future)))

        # Time axis
        t_hist = np.arange(-lookback, 0)
        t_fut = np.arange(0, H)

        # Plot context history
        ax.plot(t_hist[-48:], context[-48:], color="#6c757d", linestyle="--", linewidth=1.2, label="Context (Lookback)", alpha=0.7)
        # Plot ground truth
        ax.plot(t_fut, actual_future, color="#111111", linewidth=2.4, label="Ground Truth (Actual)", zorder=5)
        # Plot predictions
        ax.plot(t_fut, p_nlin, color="#dc3545", linewidth=1.6, linestyle="-.", label=f"NLinear (MAE: {mae_nlin:.3f})", alpha=0.85)
        ax.plot(t_fut, p_sub, color="#0d6efd", linewidth=1.6, linestyle=":", label=f"SWT Subband cA1 (MAE: {mae_sub:.3f})", alpha=0.85)
        ax.plot(t_fut, p_elm, color="#198754", linewidth=2.0, linestyle="-", label=f"BigDictELM (MAE: {mae_elm:.3f})", zorder=4)

        # Reference line at origin
        ax.axvline(x=0, color="#adb5bd", linestyle="--", alpha=0.6)

        ax.set_title(f"Task: {task_name} (H={H}, {task_type})", fontsize=12, fontweight="bold", pad=8)
        ax.set_xlabel("Horizon Step", fontsize=9)
        ax.set_ylabel("Value", fontsize=9)
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.legend(loc="best", fontsize=8, framealpha=0.9)

    plt.suptitle("Forecast Visual Comparison: BigDictELM vs Baselines across Benchmark Tasks", fontsize=15, fontweight="bold", y=0.995)
    plt.tight_layout()
    plot_file = out_path / "forecast_comparison.png"
    plt.savefig(plot_file, bbox_inches="tight")
    plt.close()
    print(f"Generated comparison plot: {plot_file}")
    return plot_file

if __name__ == "__main__":
    generate_plots()
