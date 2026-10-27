"""Visualize actual and predicted Thomas trajectories at locked origins."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from bench import gen_thomas, fit_nlinear, pred_nlinear
from thomas_methods import get_thomas_methods


def forecast_at(series, origin, horizon):
    history = series[:origin]
    forecasts = {"actual": series[origin:origin+horizon]}
    for name, method in get_thomas_methods().items():
        try:
            forecasts[name] = np.asarray(method(history, horizon)).ravel()[:horizon]
        except (ImportError, ModuleNotFoundError, RuntimeError, ValueError) as exc:
            # Optional or incompatible methods should not prevent plotting others.
            print(f"Skipping {name}: {exc}")
    return forecasts


def plot_forecasts(series, origins=(1800, 1900), horizon=48, output="plots/thomas_forecasts.png"):
    fig, axes = plt.subplots(len(origins), 1, figsize=(12, 4 * len(origins)), squeeze=False)
    for row, origin in enumerate(origins):
        ax = axes[row, 0]
        context = 96
        x_hist = np.arange(origin-context, origin)
        x_future = np.arange(origin, origin+horizon)
        ax.plot(x_hist, series[origin-context:origin], color="black", label="history")
        ax.plot(x_future, series[origin:origin+horizon], color="black", linestyle="--", label="actual")
        forecasts = forecast_at(series, origin, horizon)
        for name, values in forecasts.items():
            if name != "actual": ax.plot(x_future, values, label=name)
        ax.axvline(origin, color="gray", alpha=.5)
        ax.set_title(f"Thomas forecasts at origin {origin}, horizon {horizon}")
        ax.set_xlabel("time step"); ax.set_ylabel("x")
        ax.grid(alpha=.3); ax.legend(fontsize=8, ncol=2)
    fig.tight_layout(); output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=150); plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="plots/thomas_forecasts.png")
    parser.add_argument("--horizon", type=int, default=48)
    args = parser.parse_args()
    plot_forecasts(gen_thomas(), horizon=args.horizon, output=args.output)

if __name__ == "__main__": main()
