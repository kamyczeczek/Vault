"""Sub-experiment: BalancedLagEnsembleKNN hyperparameter sweep (H=720).

Sweeps ``q`` (anchor window), ``neighbors`` (expert KNN k), and
``history_fraction`` (recent-window truncation) for the 16-expert
balanced-lag ensemble, plus a reduced-lag-grid variant. Evaluation uses
the locked protocol: fit on ETTh1 OT ``series[:11425]``, forecast H=720,
score against ``series[11425:11425+720]``.

Outputs (in ``sub_experiments/ensemble_sweep/``):
- ``results.json``  — metrics per configuration + reference baselines
- ``interactive.html`` — Plotly ground-truth vs top-configuration forecasts
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data  # noqa: E402
from methods import make_forecaster  # noqa: E402


SWEEP_DIR = H720_ROOT / "sub_experiments" / "ensemble_sweep"






def score(pred: np.ndarray, actual: np.ndarray) -> dict[str, float]:
    err = actual - pred
    return {
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err**2))),
    }


def main() -> None:
    train, actual = get_protocol_data().forecast_views()
    # (name, kwargs) — baseline config is q6_k8_full (the registry default)
    configs: list[tuple[str, dict]] = [
        ("q3_k4_full", {"q": 3, "neighbors": 4}),
        ("q3_k8_full", {"q": 3, "neighbors": 8}),
        ("q3_k16_full", {"q": 3, "neighbors": 16}),
        ("q6_k4_full", {"q": 6, "neighbors": 4}),
        ("q6_k8_full", {"q": 6, "neighbors": 8}),  # registry default
        ("q6_k16_full", {"q": 6, "neighbors": 16}),
        ("q12_k8_full", {"q": 12, "neighbors": 8}),
        ("q24_k8_full", {"q": 24, "neighbors": 8}),
        ("q6_k8_recent50", {"q": 6, "neighbors": 8, "history_fraction": 0.5}),
        ("q6_k8_recent20", {"q": 6, "neighbors": 8, "history_fraction": 0.2}),
        ("q6_k8_recent10", {"q": 6, "neighbors": 8, "history_fraction": 0.1}),
        # reduced grid: 6 experts, fast lags only (<= 48h)
        ("q6_k8_full_fastlags", {
            "q": 6, "neighbors": 8,
            "lag_sets": ((1, 2, 24), (2, 3, 48), (6, 12, 24),
                         (1, 12, 48), (2, 6, 48), (6, 24, 48)),
        }),
    ]

    results, predictions = [], {}
    for name, kwargs in configs:
        model = make_forecaster("balanced_lag_ensemble_knn", **kwargs)
        model.fit(train, horizon=HORIZON)
        pred = model.predict()
        predictions[name] = pred
        metrics = score(pred, actual)
        results.append({
            "model": name,
            "horizon": HORIZON,
            "params": {k: v for k, v in kwargs.items()},
            **metrics,
            "status": "ok",
        })
        print(f"{name:24s} mae {metrics['mae']:.4f} rmse {metrics['rmse']:.4f}")

    # references for context
    for ref_name in ("persistence", "daily", "nlinear"):
        if ref_name == "daily":
            from methods import seasonal_forecast
            pred = seasonal_forecast(train, HORIZON, "daily")
        else:
            m = make_forecaster(ref_name).fit(train, horizon=HORIZON)
            pred = m.predict()
        metrics = score(pred, actual)
        results.append({
            "model": ref_name, "horizon": HORIZON, "params": None,
            **metrics, "status": "ok",
        })

    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    with open(SWEEP_DIR / "results.json", "w") as f:
        json.dump(
            {"experiment": "balanced_lag_ensemble_knn_sweep", "horizon": HORIZON,
             "results": results},
            f, indent=1,
        )

    # interactive plot: ground truth + the two best configs + default
    ranked = sorted(
        [r for r in results if r["params"] is not None],
        key=lambda r: r["mae"],
    )
    show = [ranked[0]["model"], ranked[-1]["model"], "q6_k8_full"]
    hours = np.arange(1, HORIZON + 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=actual, mode="lines", name="ground truth",
        line=dict(color="black", width=2),
    ))
    colors = ["#d62728", "#1f77b4", "#2ca02c", "#9467bd"]
    for i, name in enumerate(dict.fromkeys(show)):
        fig.add_trace(go.Scatter(
            x=hours, y=predictions[name], mode="lines", name=name,
            line=dict(color=colors[i % len(colors)], width=1.5, dash="dash"),
        ))
    fig.update_layout(
        title=f"BalancedLagEnsembleKNN sweep (H={HORIZON}) — best {ranked[0]['model']} "
              f"MAE {ranked[0]['mae']:.4f}",
        xaxis_title="hours ahead", yaxis_title="OT",
        template="plotly_white",
    )
    fig.write_html(SWEEP_DIR / "interactive.html", include_plotlyjs="cdn")

    print("\nranked:")
    for r in ranked:
        print(f"  {r['model']:24s} mae {r['mae']:.4f} rmse {r['rmse']:.4f}")


if __name__ == "__main__":
    main()
