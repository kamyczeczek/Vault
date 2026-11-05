"""Sub-experiment: HeuristicLagELM hyperparameter sweep (H=720).

Sweeps the three ELM axes on ETTh1 OT at horizon $H=720$:

- ``hidden_dim``  — number of hidden neurons (64 / 256 / 1024 / 4096)
- ``history_fraction`` — % of training origins used (1.0 / 0.5 / 0.2 / 0.1)
- ``delays``      — heuristically chosen lag sets

Protocol (locked, same as main leaderboard): fit on ``series[:11425]``,
forecast H=720, score against ``series[11425:11425+720]``.

Outputs (in ``sub_experiments/elm_sweep/``):
- ``results.json``      — metrics per configuration + references
- ``interactive.html``  — Plotly ground-truth vs best/worst/default forecasts
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

SWEEP_DIR = H720_ROOT / "sub_experiments" / "elm_sweep"

# Heuristic lag sets: default, extended (finer short + daily/weekly),
# seasonal (daily/weekly only), fast (short lags only)
DELAY_SETS: dict[str, tuple[int, ...]] = {
    "default": (1, 2, 3, 6, 12, 24),
    "extended": (1, 2, 3, 6, 12, 24, 48, 168),
    "seasonal": (24, 48, 168),
    "fast": (1, 2, 3, 6, 12),
}


def score(pred: np.ndarray, actual: np.ndarray) -> dict[str, float]:
    err = actual - pred
    return {
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err**2))),
    }


def main() -> None:
    train, actual = get_protocol_data().forecast_views()
    # (name, kwargs)
    configs: list[tuple[str, dict]] = []
    # --- axis 1+2: hidden_dim x history_fraction (default delays, q=3) ---
    for h in (64, 256, 1024, 4096):
        for frac in (1.0, 0.5, 0.2, 0.1):
            tag = f"h{h}_recent{int(frac * 100)}"
            configs.append((tag, {"hidden_dim": h, "history_fraction": frac}))
    # --- axis 3: heuristic delay sets at best-neutral h=256, full + rec50 ---
    for dname, delays in DELAY_SETS.items():
        for frac in (1.0, 0.5):
            tag = f"{dname}_lags_h256_recent{int(frac * 100)}"
            configs.append((tag, {
                "hidden_dim": 256, "delays": delays, "history_fraction": frac,
            }))
    # reference: registry default (must reproduce leaderboard 3.1723)
    configs.append(("elm_default", {}))

    results, predictions = [], {}
    for name, kwargs in configs:
        model = make_forecaster("heuristic_lag_elm", **kwargs)
        model.fit(train, horizon=HORIZON)
        pred = model.predict()
        predictions[name] = pred
        metrics = score(pred, actual)
        results.append({
            "model": name,
            "horizon": HORIZON,
            "params": {k: (list(v) if isinstance(v, tuple) else v)
                       for k, v in kwargs.items()},
            **metrics,
            "status": "ok",
        })
        print(f"{name:32s} mae {metrics['mae']:.4f} rmse {metrics['rmse']:.4f}")

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
            {"experiment": "heuristic_lag_elm_sweep", "horizon": HORIZON,
             "results": results},
            f, indent=1,
        )

    # interactive plot: ground truth + best + worst + default
    ranked = sorted(
        [r for r in results if r["params"] is not None],
        key=lambda r: r["mae"],
    )
    show = [ranked[0]["model"], "elm_default", ranked[-1]["model"]]
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
        title=f"HeuristicLagELM sweep (H={HORIZON}) — best {ranked[0]['model']} "
              f"MAE {ranked[0]['mae']:.4f}",
        xaxis_title="hours ahead", yaxis_title="OT",
        template="plotly_white",
    )
    fig.write_html(SWEEP_DIR / "interactive.html", include_plotlyjs="cdn")

    print("\nranked:")
    for r in ranked:
        print(f"  {r['model']:32s} mae {r['mae']:.4f} rmse {r['rmse']:.4f}")


if __name__ == "__main__":
    main()
