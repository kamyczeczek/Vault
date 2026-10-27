"""Plot horizon-wise Thomas comparison results."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import matplotlib.pyplot as plt


def plot_results(results, output):
    horizons = results["horizons"]
    models = results["models"]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for name, score in models.items():
        locked = score["locked"]
        axes[0].plot(horizons, [locked[str(h)] ["mae"] if str(h) in locked else locked[h]["mae"] for h in horizons], marker="o", label=name)
        axes[1].plot(horizons, [locked[str(h)] ["rmse"] if str(h) in locked else locked[h]["rmse"] for h in horizons], marker="o", label=name)
        axes[2].plot(horizons, [locked[str(h)] ["mean_correlation"] if str(h) in locked else locked[h]["mean_correlation"] for h in horizons], marker="o", label=name)
    for ax, title in zip(axes, ("MAE", "RMSE", "Correlation")):
        ax.set_title(f"Thomas locked set: {title}")
        ax.set_xlabel("Forecast horizon")
        ax.grid(alpha=.3)
    axes[0].set_ylabel("error")
    axes[2].set_ylim(-1.05, 1.05)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("plots/thomas_horizon_comparison.png"))
    args = parser.parse_args()
    plot_results(json.loads(args.input.read_text(encoding="utf-8")), args.output)

if __name__ == "__main__": main()
