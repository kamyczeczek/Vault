"""Recency-weighted error analysis for H=720 forecasts.

Canonical metric (uniform MAE/RMSE) stays fixed. This script adds
recency-weighted variants to see whether model rankings change when
recent horizon steps count more.

Weight schemes:
- uniform:            w_t = 1.0
- exp_{lambda}:       w_t = exp(-lambda * (H-t)/H), lambda in {0.5, 1.0, 2.0}
- linear:             w_t = t / H
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods import make_forecaster
from methods.baselines import seasonal_forecast
from methods.knn_models import HeuristicLagKNN
from methods.neural_models import HeuristicLagELMTree, HeuristicLagELMTreeN


def build_models(train: np.ndarray) -> dict[str, np.ndarray]:
    out = {}
    out["NLinear L336"] = (
        make_forecaster("nlinear", input_length=336)
        .fit(train, horizon=HORIZON)
        .predict()
    )
    out["ELMTree"] = (
        HeuristicLagELMTree(hidden_dim=256, tree_kwargs={"max_depth": 4, "min_samples_leaf": 5})
        .fit(train, horizon=HORIZON)
        .predict()
    )
    out["ELMTreeN"] = (
        HeuristicLagELMTreeN(hidden_dim=256, tree_kwargs={"max_depth": 4, "min_samples_leaf": 5})
        .fit(train, horizon=HORIZON)
        .predict()
    )
    out["KNN MI/EMA0.9/k32"] = (
        HeuristicLagKNN(
            neighbors=32,
            delays=(14, 28, 42, 56, 70),
            normalize_scale=True,
            scale_window=1440,
            ema_alpha=0.9,
            weights="distance",
        )
        .fit(train, horizon=HORIZON)
        .predict()
    )
    out["Daily"] = seasonal_forecast(train, HORIZON, "daily")
    out["Persistence"] = (
        make_forecaster("persistence")
        .fit(train, horizon=HORIZON)
        .predict()
    )
    return out


def weight_schemes(H: int):
    schemes = {
        "uniform": np.ones(H, dtype=float),
    }
    for lam in (0.5, 1.0, 2.0):
        t = np.arange(H)
        schemes[f"exp λ={lam}"] = np.exp(-lam * (H - 1 - t) / H)
    schemes["linear"] = np.arange(H, dtype=float) / H
    # normalise each scheme to mean 1 so MAE is comparable across schemes
    for k, w in schemes.items():
        schemes[k] = w / w.mean()
    return schemes


def score(pred: np.ndarray, true: np.ndarray, w: np.ndarray) -> float:
    return float(np.mean(np.abs(true - pred) * w))


def main() -> int:
    train, test = get_protocol_data().forecast_views()
    y_true = test[:HORIZON]
    preds = build_models(train)
    schemes = weight_schemes(HORIZON)

    rows = []
    for name, pred in preds.items():
        row = {"model": name}
        for scheme, w in schemes.items():
            row[scheme] = score(pred, y_true, w)
        rows.append(row)

    # Print ranking under each scheme
    schemes_print = list(schemes.keys())
    header = ["model"] + [s.replace("exp ", "exp_").replace("λ", "lambda") for s in schemes_print]
    print(" | ".join(f"{h:>28}" for h in header))
    for scheme in schemes_print:
        ranked = sorted(rows, key=lambda r: r[scheme])
        print(f"\n--- {scheme} (lower is better) ---")
        for i, r in enumerate(ranked, 1):
            print(f"{i:>2}. {r['model']:>24} {r[scheme]:.4f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
