"""Dedicated KNN prediction plot: full horizon + zoom on latest steps."""
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
from methods.knn_models import HeuristicLagKNN

OUT = Path(__file__).resolve().parent / "knn_prediction_plot.png"


def main() -> None:
    train, test = get_protocol_data().forecast_views()
    y_true = test[:HORIZON]

    knn = HeuristicLagKNN(
        neighbors=32,
        delays=(14, 28, 42, 56, 70),
        normalize_scale=True,
        scale_window=1440,
        ema_alpha=0.9,
        weights="distance",
    )
    knn.fit(train, horizon=HORIZON)
    pred = knn.predict()

    err = y_true - pred
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err**2)))
    print(f"KNN MAE: {mae:.4f}  RMSE: {rmse:.4f}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Full horizon
    x = np.arange(HORIZON)
    ax1.plot(x, y_true, label="Ground truth", color="black", linewidth=1.2)
    ax1.plot(x, pred, label="KNN MI/EMA0.9/k32", color="#d62728", linewidth=1.2, alpha=0.9)
    ax1.set_title(f"Full H=720 horizon (MAE {mae:.4f}, RMSE {rmse:.4f})")
    ax1.set_xlabel("Horizon step (h)")
    ax1.set_ylabel("OT (scaled)")
    ax1.legend()
    ax1.grid(True, linewidth=0.3)

    # Zoom latest steps
    zoom_start = HORIZON - 200
    ax2.plot(x[zoom_start:], y_true[zoom_start:], label="Ground truth", color="black", linewidth=1.2)
    ax2.plot(x[zoom_start:], pred[zoom_start:], label="KNN MI/EMA0.9/k32", color="#d62728", linewidth=1.2, alpha=0.9)
    ax2.set_title(f"Latest 200 steps (horizon {zoom_start}–{HORIZON-1})")
    ax2.set_xlabel("Horizon step (h)")
    ax2.set_ylabel("OT (scaled)")
    ax2.legend()
    ax2.grid(True, linewidth=0.3)

    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"saved: {OUT}")


if __name__ == "__main__":
    main()
