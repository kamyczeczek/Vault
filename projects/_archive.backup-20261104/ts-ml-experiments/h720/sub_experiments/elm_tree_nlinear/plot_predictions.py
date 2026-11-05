"""Visualize predictions vs ground truth for the H=720 rolling forecast.

Plots:
- S-20 per-horizon ridge mixture (6 linear members): incumbent, MAE 1.9980
- HeuristicLagELMTree (S-09): best nonlinear, MAE 2.1706
- HeuristicLagELMTreeN (S-22): last-value anchor variant, MAE 2.1749
- HeuristicLagKNN MI/EMA0.9/k32 (S-15): best KNN, MAE 2.2503
- NLinear L336 (S-06): best single linear, MAE 2.0571
- Daily seasonal-naive + Persistence: fail-loud anchors

Uses the t=0 origin window (test[:720]) for a stable side-by-side comparison.
All models are frozen-fitted on train.csv exactly once.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods import make_forecaster
from methods.baselines import seasonal_forecast
from methods.neural_models import HeuristicLagELMTree, HeuristicLagELMTreeN
from methods.knn_models import HeuristicLagKNN

OUT = Path(__file__).resolve().parent / "prediction_plots_s22.png"


def main() -> None:
    train, test = get_protocol_data().forecast_views()
    y_true = test[:HORIZON]

    models = {}

    # S-06 NLinear L336 a=1
    m = make_forecaster("nlinear", input_length=336)
    m.fit(train, horizon=HORIZON)
    models["NLinear L336 (2.0571)"] = m.predict()

    # S-09 ELMTree (mean anchor)
    elm = HeuristicLagELMTree(hidden_dim=256, tree_kwargs={"max_depth": 4, "min_samples_leaf": 5})
    elm.fit(train, horizon=HORIZON)
    models["ELMTree (2.1706)"] = elm.predict()

    # S-22 ELMTreeN (last-value anchor)
    elm_n = HeuristicLagELMTreeN(hidden_dim=256, tree_kwargs={"max_depth": 4, "min_samples_leaf": 5})
    elm_n.fit(train, horizon=HORIZON)
    models["ELMTreeN (2.1749)"] = elm_n.predict()

    # S-15 best KNN (MI lags 14,28,42,56,70, EMA 0.9, norm1440, k=32)
    knn = HeuristicLagKNN(
        neighbors=32,
        delays=(14, 28, 42, 56, 70),
        normalize_scale=True,
        scale_window=1440,
        ema_alpha=0.9,
        weights="distance",
    )
    knn.fit(train, horizon=HORIZON)
    models["KNN MI/EMA0.9/k32 (2.2503)"] = knn.predict()

    # Baselines
    models["Daily (2.5491)"] = seasonal_forecast(train, HORIZON, "daily")
    persist = make_forecaster("persistence")
    persist.fit(train, horizon=HORIZON)
    models["Persistence (2.5985)"] = persist.predict()

    # Plot
    x = np.arange(HORIZON)
    colors = {
        "NLinear L336 (2.0571)": "#1f77b4",
        "ELMTree (2.1706)": "#ff7f0e",
        "ELMTreeN (2.1749)": "#2ca02c",
        "KNN MI/EMA0.9/k32 (2.2503)": "#d62728",
        "Daily (2.5491)": "#9467bd",
        "Persistence (2.5985)": "#8c564b",
    }

    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    axes = axes.flatten()
    targets = list(models.keys())
    for ax, name in zip(axes, targets):
        pred = models[name]
        ax.plot(x, y_true, label="Ground truth", color="black", linewidth=1.2)
        ax.plot(x, pred, label=name, color=colors[name], linewidth=1.2, alpha=0.9)
        ax.set_title(name)
        ax.set_xlabel("Horizon step (h)")
        ax.set_ylabel("OT (scaled)")
        ax.legend(fontsize=8)
        ax.grid(True, linewidth=0.3)

    # Remove empty subplot
    axes[-1].remove()

    fig.suptitle("H=720 ETTh1 predictions vs ground truth (t=0 origin, test[:720])", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT, dpi=150)
    print(f"saved: {OUT}")


if __name__ == "__main__":
    main()
