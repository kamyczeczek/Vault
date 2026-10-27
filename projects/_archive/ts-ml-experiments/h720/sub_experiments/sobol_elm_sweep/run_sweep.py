"""Sub-experiment: Sobol quasi-random weight init for HeuristicLagELM (H=720).

Motivation: the ELM sweep showed a strong recent-history effect — full
history underperformed the best recent window (h256_recent50 MAE 1.6344
vs h256_recent100 1.6771). Hypothesis under test: when using the *whole*
history, the iid N(0,1) weight draw may leave parts of the lag-feature
space poorly covered by the 256-neuron hidden layer. A scrambled Sobol
low-discrepancy sequence places the same number of neurons *regularly
across the space* (quasi-random, not pseudo-random), improving coverage
for a fixed hidden_dim.

Sweep axes:
- ``hidden_dim``    in {64, 256, 1024, 4096}
- ``weight_init``   in {"sobol", "sobol_iid", "normal"} (matched triples)
- ``history_fraction`` fixed at 1.0 — whole history, per the hypothesis
- ``delays``        fast lags (1,2,3,6,12) — best set from the prior sweep

``sobol``:     Sobol grid through ndtri — same marginals as normal,
               but all-neuron norms near sqrt(d) and cubic-axis
               structure (not iid-joint).
``sobol_iid``: Sobol placement *plus* the joint properties of the iid
               normal draw — chi(d) radii quantiles + random rotation
               (norm diversity + isotropy), zero-mean identity-cov.
               "Normal distribution properties, Sobol placement."
``normal``:    iid RandomState(42) — original scheme (reference).

Outputs (in this directory):
- ``results.json``      — metrics per configuration + matched triples
- ``interactive.html``  — three charts: all 12 forecasts vs ground truth,
  MAE ranking, MAE-vs-hidden_dim per init

Data: shared chronological split via ``data.py`` — fit on all of
``train.csv`` (11,425 rows), forecast H=720, score against the first
720 rows of ``test.csv``. One identical split for every subexperiment.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import plotly.io
import plotly.graph_objects as go

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data  # noqa: E402
from methods import make_forecaster  # noqa: E402

SWEEP_DIR = H720_ROOT / "sub_experiments" / "sobol_elm_sweep"

FAST_LAGS = (1, 2, 3, 6, 12)


def score(pred: np.ndarray, actual: np.ndarray) -> dict[str, float]:
    err = actual - pred
    return {
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err**2))),
    }


def main() -> None:
    train, actual = get_protocol_data().forecast_views()

    # (name, kwargs) — matched sobol/normal pairs across hidden_dim
    configs: list[tuple[str, dict]] = []
    for h in (64, 256, 1024, 4096):
        for init in ("sobol", "sobol_iid", "normal"):
            tag = f"{init}_h{h}_full_fastlags"
            configs.append(
                (
                    tag,
                    {
                        "hidden_dim": h,
                        "history_fraction": 1.0,
                        "delays": FAST_LAGS,
                        "weight_init": init,
                    },
                )
            )

    results: list[dict] = []
    predictions: dict[str, np.ndarray] = {}
    for name, kwargs in configs:
        model = make_forecaster("heuristic_lag_elm", **kwargs)
        model.fit(train, horizon=HORIZON)
        pred = model.predict()
        predictions[name] = pred
        metrics = score(pred, actual)
        results.append({
            "model": name,
            "horizon": HORIZON,
            "params": {"history_fraction": 1.0, "delays": list(FAST_LAGS),
                        "weight_init": kwargs["weight_init"],
                        "hidden_dim": kwargs["hidden_dim"]},
            **metrics,
            "status": "ok",
        })
        print(f"  {name:28s} mae {metrics['mae']:.4f} rmse {metrics['rmse']:.4f}")

    # matched triples: sobol vs sobol_iid vs normal at equal hidden_dim
    pairs = []
    for h in (64, 256, 1024, 4096):
        by_init = {
            r["model"].split("_h")[0]: r
            for r in results if f"_h{h}_" in r["model"]
        }
        pairs.append({
            "hidden_dim": h,
            "sobol_mae": by_init["sobol"]["mae"],
            "sobol_iid_mae": by_init["sobol_iid"]["mae"],
            "normal_mae": by_init["normal"]["mae"],
            "sobol_rmse": by_init["sobol"]["rmse"],
            "sobol_iid_rmse": by_init["sobol_iid"]["rmse"],
            "normal_rmse": by_init["normal"]["rmse"],
        })

    ranked = sorted(results, key=lambda r: r["mae"])
    print("\nranked:")
    for r in ranked:
        print(f"  {r['model']:28s} mae {r['mae']:.4f} rmse {r['rmse']:.4f}")

    print("\nmatched triples (whole history, fast lags):")
    for p in pairs:
        best = min(p, key=lambda k: p[k] if k.endswith("_mae") else 9e9)
        print(f"  h={p['hidden_dim']:5d}  sobol {p['sobol_mae']:.4f}  "
              f"sobol_iid {p['sobol_iid_mae']:.4f}  normal {p['normal_mae']:.4f}"
              f"  -> {best.removesuffix('_mae')}")

    # --- interactive.html: ALL models + rankings + matched triples -------
    hours = np.arange(HORIZON)

    # Main forecast chart: ground truth + all 12 model predictions.
    # One colour per init, dash pattern per hidden_dim.
    INIT_COLORS = {"sobol": "#d62728", "sobol_iid": "#1f77b4", "normal": "#2ca02c"}
    H_DASH = {64: "dot", 256: "dash", 1024: "dashdot", 4096: "longdash"}

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=actual, mode="lines", name="ground truth",
        line=dict(color="black", width=3),
    ))
    for r in ranked:  # ranked order: best MAE first
        nm = r["model"]
        init = nm.split("_h")[0]                     # sobol | sobol_iid | normal
        h = r["params"]["hidden_dim"]
        fig.add_trace(go.Scatter(
            x=hours, y=predictions[nm], mode="lines",
            name=f"{nm}  (MAE {r['mae']:.4f})",
            legendgroup=init,
            line=dict(
                color=INIT_COLORS[init],
                width=1.5 if nm != ranked[0]["model"] else 3,
                dash=H_DASH[h],
            ),
            opacity=0.85,
        ))
    fig.update_layout(
        title="HeuristicLagELM H=720 — all weight-init variants "
              "(whole history, fast lags). Legend ranked by MAE; "
              "colour = init, dash = hidden_dim, thick = best.",
        xaxis_title="hours ahead", yaxis_title="OT",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(font=dict(size=9)),
    )

    # MAE ranking bar chart (colour by init).
    fig_bar = go.Figure()
    names_ranked = [r["model"] for r in ranked]
    maes = [r["mae"] for r in ranked]
    init_of = [n.split("_h")[0] for n in names_ranked]
    fig_bar.add_trace(go.Bar(
        x=names_ranked, y=maes,
        marker_color=[INIT_COLORS[i] for i in init_of],
        text=[f"{m:.4f}" for m in maes], textposition="outside",
    ))
    fig_bar.update_layout(
        title="MAE ranking — lower is better "
              "(red=sobol, blue=sobol_iid, green=normal)",
        yaxis_title="MAE", template="plotly_white",
        xaxis_tickangle=-35,
    )

    # Hidden-dimension comparison: MAE vs hidden_dim per init.
    fig_dim = go.Figure()
    for init, color in INIT_COLORS.items():
        xs = sorted(p["hidden_dim"] for p in pairs)
        key = {"sobol": "sobol_mae", "sobol_iid": "sobol_iid_mae",
               "normal": "normal_mae"}[init]
        by_h = {p["hidden_dim"]: p[key] for p in pairs}
        fig_dim.add_trace(go.Scatter(
            x=xs, y=[by_h[x] for x in xs], mode="lines+markers",
            name=init, line=dict(color=color, width=2),
        ))
    fig_dim.update_layout(
        title="MAE vs hidden_dim per weight-init (log x)",
        xaxis_title="hidden_dim", yaxis_title="MAE",
        xaxis_type="log", template="plotly_white",
    )

    html = (
        "<html><head><title>sobol_elm_sweep — all variants</title></head>"
        "<body style='font-family: sans-serif; margin: 20px'>"
        "<h2>Forecasts — ground truth vs all 12 variants (H=720)</h2>"
    )
    html += plotly.io.to_html(fig, full_html=False, include_plotlyjs="cdn")
    html += "<h2>MAE ranking</h2>"
    html += plotly.io.to_html(fig_bar, full_html=False, include_plotlyjs=False)
    html += "<h2>MAE vs hidden_dim</h2>"
    html += plotly.io.to_html(fig_dim, full_html=False, include_plotlyjs=False)
    html += "</body></html>"
    (SWEEP_DIR / "interactive.html").write_text(html, encoding="utf-8")

    results_json = {
        "protocol": "fit train.csv (11,425 rows), forecast H=720, "
                    "score vs test.csv[:720] — via data.py shared split",
        "axes": ["hidden_dim", "weight_init (sobol|sobol_iid|normal)"],
        "fixed": {"history_fraction": 1.0, "delays": list(FAST_LAGS)},
        "results": results,
        "matched_pairs": pairs,
    }
    with open(SWEEP_DIR / "results.json", "w") as f:
        json.dump(results_json, f, indent=2)
    print(f"\nwrote {SWEEP_DIR / 'results.json'}, interactive.html")


if __name__ == "__main__":
    main()
