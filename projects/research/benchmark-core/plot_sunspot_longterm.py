"""Plot long-horizon sunspot forecasts from the available benchmark methods."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from bench import get_sunspot
from sunspot_methods import get_sunspot_methods


def forecast_sunspot(series, origin, horizon, lookback=96):
    history = np.asarray(series[:origin], dtype=float)
    if origin < lookback or origin + horizon > len(series):
        raise ValueError("origin/horizon outside available series")
    forecasts = {"actual": np.asarray(series[origin:origin+horizon])}
    for name, method in get_sunspot_methods().items():
        try:
            prediction = np.asarray(method(history, history[-lookback:], horizon), dtype=float).ravel()
            if len(prediction) >= horizon and np.isfinite(prediction[:horizon]).all():
                forecasts[name] = prediction[:horizon]
        except (ImportError, ModuleNotFoundError, RuntimeError, ValueError) as exc:
            print(f"Skipping {name}: {exc}")
    return forecasts


def plot_sunspot_longterm(origin=2000, horizon=120, lookback=96, output="plots/sunspot_longterm_forecasts.png"):
    series = get_sunspot(max(2600, origin + horizon))
    forecasts = forecast_sunspot(series, origin, horizon, lookback)
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    t_hist = np.arange(-lookback, 0)
    t_future = np.arange(horizon)
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(t_hist, series[origin-lookback:origin], color="black", label="history")
    ax.plot(t_future, forecasts.pop("actual"), color="black", linewidth=2, label="actual")
    for name, prediction in forecasts.items():
        ax.plot(t_future, prediction, linewidth=1.2, label=name)
    ax.axvline(0, color="gray", linestyle="--")
    ax.set_title(f"Long-term sunspot forecasts (origin={origin}, horizon={horizon})")
    ax.set_xlabel("months relative to forecast origin"); ax.set_ylabel("sunspot activity")
    ax.grid(alpha=.3); ax.legend(fontsize=8, ncol=2)
    fig.tight_layout(); fig.savefig(output, dpi=180); plt.close(fig)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", type=int, default=2000)
    parser.add_argument("--horizon", type=int, default=120)
    parser.add_argument("--lookback", type=int, default=96)
    parser.add_argument("--output", default="plots/sunspot_longterm_forecasts.png")
    args = parser.parse_args()
    print(f"Saved {plot_sunspot_longterm(args.origin, args.horizon, args.lookback, args.output)}")

if __name__ == "__main__": main()
