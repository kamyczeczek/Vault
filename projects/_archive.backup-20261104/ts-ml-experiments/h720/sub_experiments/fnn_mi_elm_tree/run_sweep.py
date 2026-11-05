"""Sub-experiment: MI+FNN-selected lags, ELM hidden layer, tree readout (H=720).

Two orthogonal changes vs the best ELM (normal_h64_full_fastlags, MAE 1.5923):
1. Lags are *chosen* (AMI tau -> FNN m -> multiples of tau re-ranked by MI
   with the 720-ahead target) instead of hand-picked fast lags.
2. The ELM readout is a multi-output DecisionTreeRegressor (fixed seed 42)
   instead of ridge. A ridge arm with identical lags isolates the readout
   effect.

Tree grid: max_depth x min_samples_leaf (regularization; the unpruned tree
overfits 10.7k x 720 data). RF was tried first but 100 trees took ~13 min
per fit — unusable for a sweep; a single tree fits in ~1 min.

Outputs (in this directory):
- ``results.json``     — metrics per configuration + diagnostics
- ``interactive.html`` — forecasts vs ground truth, MAE ranking, MI curve,
  FNN curve, lag-placement chart

Data: shared chronological split via ``data.py`` — fit on all of
``train.csv`` (11,425 rows), forecast H=720, score against the first
720 rows of ``test.csv``. One identical split for every subexperiment.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data  # noqa: E402
from methods import make_forecaster  # noqa: E402
from methods.neural_models import (  # noqa: E402
    _average_mutual_information,
    _fnn_fraction,
)

SWEEP_DIR = H720_ROOT / "sub_experiments" / "fnn_mi_elm_tree"


def main() -> None:
    train, actual = get_protocol_data().forecast_views()
    series = np.asarray(train, dtype=float)

    # --- 1. lag-selection diagnostics (on train only) -------------------
    mi = _average_mutual_information(series, 168, 16)
    tau_probe = make_forecaster("heuristic_lag_elm_tree")
    fnn = _fnn_fraction(series, max_dim=168 // 14, tau=14)
    probe = make_forecaster("heuristic_lag_elm_tree")
    lags = probe.select_lags(series, HORIZON)
    print(f"selected: tau={probe.tau_} m={probe.m_} lags={lags}")
    print(f"fnn%: {np.round(fnn[1:], 3)}")

    # --- 2. configurations ---------------------------------------------
    # (name, forecaster name, kwargs)
    configs: list[tuple[str, str, dict]] = []

    # tree grid: max_depth x min_samples_leaf, hidden_dim fixed at 256
    for depth in (4, 6, 8, 12, None):
        for leaf in (5, 25, 100):
            configs.append((
                f"tree_d{depth if depth else 'full'}_L{leaf}",
                "heuristic_lag_elm_tree",
                {"tree_kwargs": {"max_depth": depth, "min_samples_leaf": leaf}},
            ))

    # hidden-layer size at the best tree setting (re-joined after ranking)
    # ridge reference arms with identical lags
    configs.append(("ridge_ref_same_lags", "heuristic_lag_elm",
                    {"delays": lags, "hidden_dim": 256}))
    configs.append(("ridge_ref_fastlags", "heuristic_lag_elm",
                    {"delays": (1, 2, 3, 6, 12), "hidden_dim": 256}))

    results = []
    predictions: dict[str, np.ndarray] = {}
    for name, fc_name, kwargs in configs:
        model = make_forecaster(fc_name, **kwargs)
        t0 = time.time()
        model.fit(train, horizon=HORIZON)
        fit_s = time.time() - t0
        pred = model.predict()
        predictions[name] = pred
        mae = float(np.abs(pred - actual).mean())
        rmse = float(np.sqrt(((pred - actual) ** 2).mean()))
        results.append({
            "model": name, "mae": mae, "rmse": rmse,
            "fit_seconds": round(fit_s, 1),
            "params": {k: v for k, v in kwargs.items()},
        })
        print(f"  {name:24s} mae {mae:.4f} rmse {rmse:.4f} ({fit_s:.0f}s)")

    ranked = sorted(results, key=lambda r: r["mae"])

    # hidden_dim sweep at the winning tree config
    best_tree = min((r for r in results if r["model"].startswith("tree")),
                    key=lambda r: r["mae"])
    best_tree_kwargs = best_tree["params"]["tree_kwargs"]
    for hdim in (64, 512, 1024):
        name = f"tree_best_h{hdim}"
        model = make_forecaster("heuristic_lag_elm_tree",
                               hidden_dim=hdim,
                               tree_kwargs=best_tree_kwargs)
        t0 = time.time()
        model.fit(train, horizon=HORIZON)
        fit_s = time.time() - t0
        pred = model.predict()
        predictions[name] = pred
        mae = float(np.abs(pred - actual).mean())
        rmse = float(np.sqrt(((pred - actual) ** 2).mean()))
        results.append({
            "model": name, "mae": mae, "rmse": rmse,
            "fit_seconds": round(fit_s, 1),
            "params": {"hidden_dim": hdim, "tree_kwargs": best_tree_kwargs},
        })
        print(f"  {name:24s} mae {mae:.4f} rmse {rmse:.4f} ({fit_s:.0f}s)")
    ranked = sorted(results, key=lambda r: r["mae"])

    # --- 3. results.json -------------------------------------------------
    with open(SWEEP_DIR / "results.json", "w") as f:
        json.dump({
            "protocol": "fit train.csv (11,425 rows), forecast H=720, "
                        "score vs test.csv[:720] — via data.py shared split",
            "lags_selected": list(lags),
            "tau": probe.tau_, "m": probe.m_,
            "fnn_curve": [float(x) for x in fnn[1:]],
            "results": results,
        }, f, indent=2)

    # --- 4. interactive.html ---------------------------------------------
    hours = np.arange(HORIZON)
    best_name = ranked[0]["model"]

    # 4a. forecasts: ground truth + top-5 + ridge refs
    show = [r["model"] for r in ranked[:5]] + ["ridge_ref_same_lags"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=actual, mode="lines", name="ground truth",
        line=dict(color="black", width=3),
    ))
    palette = ["#d62728", "#1f77b4", "#2ca02c", "#9467bd", "#ff7f0e", "#8c564b"]
    for i, nm in enumerate(show):
        if nm not in predictions:
            continue
        fig.add_trace(go.Scatter(
            x=hours, y=predictions[nm], mode="lines",
            name=f"{nm} (MAE {next(r['mae'] for r in results if r['model']==nm):.4f})",
            line=dict(color=palette[i % len(palette)], width=1.5,
                     dash="solid" if nm == best_name else "dash"),
        ))
    fig.update_layout(
        title="MI+FNN lags + ELM hidden layer + tree readout (H=720)",
        xaxis_title="hours ahead", yaxis_title="OT",
        template="plotly_white", hovermode="x unified",
        legend=dict(font=dict(size=9)),
    )

    # 4b. MAE ranking bars
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=[r["model"] for r in ranked], y=[r["mae"] for r in ranked],
        text=[f"{r['mae']:.4f}" for r in ranked], textposition="outside",
        marker_color=["#d62728" if r["model"].startswith("tree")
                      else "#2ca02c" if "ridge" in r["model"]
                      else "#1f77b4" for r in ranked],
    ))
    fig_bar.update_layout(
        title="MAE ranking (red=tree readout, green=ridge readout)",
        yaxis_title="MAE", template="plotly_white", xaxis_tickangle=-40,
    )

    # 4c. diagnostics: AMI curve with tau + FNN curve with m
    fig_diag = go.Figure()
    fig_diag.add_trace(go.Scatter(
        x=np.arange(1, len(mi)), y=mi[1:], mode="lines",
        name="AMI (bits)", line=dict(color="#1f77b4"),
    ))
    fig_diag.add_vline(x=probe.tau_, line_dash="dash", line_color="red",
                       annotation_text=f"tau={probe.tau_}")
    fig_diag.update_layout(
        title=f"Average mutual information — tau={probe.tau_} at first local min",
        xaxis_title="lag (hours)", yaxis_title="MI (bits)",
        template="plotly_white",
    )

    fig_fnn = go.Figure()
    dims = np.arange(1, len(fnn))
    fig_fnn.add_trace(go.Scatter(
        x=dims, y=fnn[1:] * 100, mode="lines+markers",
        name="FNN %", line=dict(color="#d62728"),
    ))
    fig_fnn.add_hline(y=5, line_dash="dash", line_color="gray",
                      annotation_text="5% threshold")
    fig_fnn.add_vline(x=probe.m_, line_dash="dash", line_color="red",
                      annotation_text=f"m={probe.m_}")
    fig_fnn.update_layout(
        title=f"False nearest neighbours (tau={probe.tau_}) — m={probe.m_}",
        xaxis_title="embedding dimension m", yaxis_title="FNN %",
        template="plotly_white",
    )

    # 4d. lag placement on the AMI curve
    fig_lags = go.Figure()
    fig_lags.add_trace(go.Scatter(
        x=np.arange(1, len(mi)), y=mi[1:], mode="lines",
        name="AMI", line=dict(color="#1f77b4"),
    ))
    chosen_mi = [float(mi[d]) for d in lags]
    fig_lags.add_trace(go.Scatter(
        x=list(lags), y=chosen_mi, mode="markers",
        name="selected lags", marker=dict(size=12, color="red", symbol="x"),
    ))
    fig_lags.update_layout(
        title=f"Selected lags {tuple(lags)} on the AMI curve (max_lag=168)",
        xaxis_title="lag (hours)", yaxis_title="MI (bits)",
        template="plotly_white",
    )

    html = (
        "<html><head><title>fnn_mi_elm_tree</title></head>"
        "<body style='font-family: sans-serif; margin: 20px'>"
        "<h2>Forecasts — top-5 + ridge reference vs ground truth</h2>"
    )
    html += go.Figure(fig).to_html(full_html=False, include_plotlyjs="cdn")
    html += "<h2>MAE ranking</h2>"
    html += fig_bar.to_html(full_html=False, include_plotlyjs=False)
    html += "<h2>Lag selection diagnostics</h2>"
    html += fig_diag.to_html(full_html=False, include_plotlyjs=False)
    html += fig_fnn.to_html(full_html=False, include_plotlyjs=False)
    html += fig_lags.to_html(full_html=False, include_plotlyjs=False)
    html += "</body></html>"
    (SWEEP_DIR / "interactive.html").write_text(html, encoding="utf-8")

    print(f"\nwrote {SWEEP_DIR / 'results.json'}, interactive.html")


if __name__ == "__main__":
    main()
