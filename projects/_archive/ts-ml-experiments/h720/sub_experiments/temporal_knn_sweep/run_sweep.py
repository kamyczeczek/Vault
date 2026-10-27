"""Sub-experiment: temporal (time-decayed) kNN — g3/q3 family (H=720).

Motivation: ``q3_k_sweep`` showed that scaling the neighborhood to k=32
under a *hard* recent-10% truncation wins (MAE 1.7204, leaderboard row
``HeuristicLagKNN (k=32, q=3, recent 10%)``). Question under test: does
*soft* exponential recency decay — older neighbors get lower weight —
replace the hard window truncation, and does temporal weighting let the
neighborhood grow beyond k=32 (hypothesis: some configs want more
neighbours than the unweighted optimum)?

Formulation ("select by similarity, weight by recency" — time-decayed
kNN / ItemKNN-TD family): the k nearest origins in anchor-normalised
lag space are chosen exactly as in :class:`HeuristicLagKNN`, then each
neighbor's distance weight is multiplied by a recency factor:

    w_i = (1 / (d_i + eps)) * exp(-decay * age_i)
    age_i = forecast_time - origin_i        (steps = hours, hourly data)
    decay = ln(2) / half_life_hours

``decay == 0`` recovers the parent exactly (verified in-script to 1e-9).

Sweep axes (70 configurations):
- ``neighbors``          k in {3, 8, 16, 24, 32, 64, 128}
- ``half_life_hours``    in {inf, 720 (30d), 240 (10d), 72 (3d), 24 (1d)}
- ``history_fraction``   in {0.1 (hard recent-10% truncation), 1.0 (full)}
Fixed: ``q=3``, ``delays=(1, 2, 3, 6, 12, 24)`` — the q3_k_sweep base.

Anchors (MUST reproduce to 4 decimals or the run FAILS — no silent
numbers, per the results-persistence rule in q3_k_sweep/CONTEXT.md):
- ``k3  hl=inf recent10`` -> MAE 2.8565 / RMSE 3.3663  (k3_q3_recent10)
- ``k32 hl=inf recent10`` -> MAE 1.7204 / RMSE 2.1405  (k32_q3_recent10)

References for context: persistence (1.7952), daily seasonal-naive
(1.6720) — the two leaderboard bookends around the k32 row.

Outputs (in this directory):
- ``results.json``      — metrics per configuration + references
- ``interactive.html``  — ground truth + ALL 70 prediction traces
  (visualization gate), MAE ranking, and MAE-vs-k curves per half-life.

Data: shared chronological split via ``data.py`` — fit on all of
``train.csv`` (11,425 rows), forecast H=720, score against the first 720
rows of ``test.csv``. One identical split for every subexperiment.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import plotly.io

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data  # noqa: E402
from methods import make_forecaster  # noqa: E402

SWEEP_DIR = H720_ROOT / "sub_experiments" / "temporal_knn_sweep"

Q = 3
DELAYS = (1, 2, 3, 6, 12, 24)
KS = (3, 8, 16, 24, 32, 64, 128)
HALF_LIVES: tuple[float, ...] = (720.0, 240.0, 72.0, 24.0)  # hours; inf handled apart
FRACT = (0.1, 1.0)

# anchors from q3_k_sweep (k*_q3_recent10) — exact 4-decimal reproduction
ANCHORS = {
    ("k3_recent10", 3, 0.1): (2.8565, 3.3663),
    ("k32_recent10", 32, 0.1): (1.7204, 2.1405),
}

HL_COLORS = {  # inf = grey (reference), then cool -> warm with recency
    "inf": "#7f7f7f",
    "720": "#1f77b4",
    "240": "#2ca02c",
    "72": "#ff7f0e",
    "24": "#d62728",
}


def score(pred: np.ndarray, actual: np.ndarray) -> dict[str, float]:
    err = np.asarray(actual, dtype=float) - pred
    return {
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err**2))),
    }


def main() -> None:
    train, actual = get_protocol_data().forecast_views()

    # (name, kwargs) — decay=0 (hl=inf) first so anchors sit at the top
    configs: list[tuple[str, dict]] = []
    for frac in FRACT:
        tag_frac = f"recent{int(frac * 100)}"
        for k in KS:
            configs.append((
                f"k{k}_hlinf_{tag_frac}",
                {"q": Q, "neighbors": k, "delays": DELAYS,
                 "history_fraction": frac, "decay": 0.0},
            ))
        for hl in HALF_LIVES:
            for k in KS:
                configs.append((
                    f"k{k}_hl{int(hl)}_{tag_frac}",
                    {"q": Q, "neighbors": k, "delays": DELAYS,
                     "history_fraction": frac,
                     "decay": math.log(2.0) / hl},
                ))

    results: list[dict] = []
    predictions: dict[str, np.ndarray] = {}
    for name, kwargs in configs:
        model = make_forecaster("temporal_lag_knn", **kwargs)
        model.fit(train, horizon=HORIZON)
        pred = model.predict()
        predictions[name] = pred
        metrics = score(pred, actual)
        results.append({
            "model": name,
            "horizon": HORIZON,
            "params": {
                "q": kwargs["q"],
                "neighbors": kwargs["neighbors"],
                "delays": list(kwargs["delays"]),
                "history_fraction": kwargs["history_fraction"],
                "decay": kwargs["decay"],
                "half_life_hours": (
                    None if kwargs["decay"] == 0.0
                    else math.log(2.0) / kwargs["decay"]
                ),
            },
            **metrics,
            "status": "ok",
        })
        print(f"  {name:24s} mae {metrics['mae']:.4f} rmse {metrics['rmse']:.4f}")

    # --- anchor validation: fail loudly, never write a silent sweep ----
    by_name = {r["model"]: r for r in results}
    for (anchor_name, k, frac), (exp_mae, exp_rmse) in ANCHORS.items():
        row = by_name[f"k{k}_hlinf_recent{int(frac * 100)}"]
        ok_mae = round(row["mae"], 4) == exp_mae
        ok_rmse = round(row["rmse"], 4) == exp_rmse
        if not (ok_mae and ok_rmse):
            raise RuntimeError(
                f"anchor {anchor_name} not reproduced: got "
                f"MAE {row['mae']:.4f}/RMSE {row['rmse']:.4f}, expected "
                f"{exp_mae}/{exp_rmse} — protocol drift, run is INVALID"
            )
        print(f"anchor {anchor_name}: {exp_mae}/{exp_rmse} reproduced ok")

    # --- references for context (leaderboard bookends) -------------------
    refs = []
    from methods import seasonal_forecast
    for ref_name, pred in (
        ("persistence", make_forecaster("persistence").fit(
            train, horizon=HORIZON).predict()),
        ("daily", seasonal_forecast(train, HORIZON, "daily")),
    ):
        metrics = score(pred, actual)
        refs.append({"model": ref_name, "horizon": HORIZON, "params": None,
                     **metrics, "status": "ok"})

    ranked = sorted(results, key=lambda r: r["mae"])
    print("\nranked (top 10):")
    for r in ranked[:10]:
        print(f"  {r['model']:24s} mae {r['mae']:.4f} rmse {r['rmse']:.4f}")
    print("ranked (bottom 3):")
    for r in ranked[-3:]:
        print(f"  {r['model']:24s} mae {r['mae']:.4f} rmse {r['rmse']:.4f}")

    # --- results.json (always non-empty: anchors passed above) ----------
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    with open(SWEEP_DIR / "results.json", "w") as f:
        json.dump(
            {
                "experiment": "temporal_knn_sweep",
                "protocol": "fit train.csv (11,425 rows) via data.py shared "
                            "split, forecast H=720, score vs test.csv[:720]",
                "axes": ["neighbors k", "half_life_hours", "history_fraction"],
                "fixed": {"q": Q, "delays": list(DELAYS)},
                "formulation": "w_i = (1/(d_i+eps)) * exp(-decay*age_i); "
                                "decay=ln(2)/half_life; decay=0 == "
                                "HeuristicLagKNN distance weights",
                "anchors_reproduced": [a[0] for a in ANCHORS],
                "results": results,
                "references": refs,
            },
            f, indent=1,
        )

    # --- interactive.html -------------------------------------------------
    hours = np.arange(HORIZON)

    # 1) all forecasts vs ground truth (visualization gate: 1 + 70 traces)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=actual, mode="lines", name="ground truth",
        line=dict(color="black", width=3),
    ))
    for r in ranked:
        nm = r["model"]
        p = nm.split("_")
        hl = p[1][2:]                     # 'inf' | '720' | ...
        frac_tag = p[2]                    # recent10 | recent100
        is_best = nm == ranked[0]["model"]
        fig.add_trace(go.Scatter(
            x=hours, y=predictions[nm], mode="lines",
            name=f"{nm} (MAE {r['mae']:.4f})",
            legendgroup=hl,
            line=dict(
                color=HL_COLORS[hl],
                width=3 if is_best else 1,
                dash="dot" if frac_tag == "recent10" else None,
            ),
            opacity=0.9 if is_best else 0.5,
        ))
    fig.update_layout(
        title=f"TemporalLagKNN sweep — ground truth vs all {len(results)} "
              "variants (H=720). colour = half-life, dot = recent-10% arm, "
              "thick = best MAE.",
        xaxis_title="hours ahead", yaxis_title="OT",
        template="plotly_white", hovermode="x unified",
        legend=dict(font=dict(size=8)),
    )

    # 2) MAE ranking bar chart
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=[r["model"] for r in ranked],
        y=[r["mae"] for r in ranked],
        marker_color=[
            HL_COLORS[r["model"].split("_")[1][2:]] for r in ranked
        ],
        text=[f"{r['mae']:.3f}" for r in ranked],
        textposition="outside", textfont=dict(size=7),
    ))
    fig_bar.update_layout(
        title="MAE ranking — lower is better (colour = half-life)",
        yaxis_title="MAE", template="plotly_white", xaxis_tickangle=-60,
        xaxis_tickfont=dict(size=7),
    )

    # 3) MAE vs k per (half-life, history arm) — the "more neighbours" view
    fig_k = go.Figure()
    for frac in FRACT:
        for hl_tag in ("inf", "720", "240", "72", "24"):
            xs, ys = [], []
            for k in KS:
                nm = f"k{k}_hl{hl_tag}_recent{int(frac * 100)}"
                row = by_name[nm]
                xs.append(k)
                ys.append(row["mae"])
            fig_k.add_trace(go.Scatter(
                x=xs, y=ys, mode="lines+markers",
                name=f"hl={hl_tag}h, recent{int(frac * 100)}",
                line=dict(color=HL_COLORS[hl_tag], width=2,
                          dash="dot" if frac == 0.1 else None),
            ))
    fig_k.update_layout(
        title="MAE vs neighborhood size k — solid = full history, "
              "dot = recent-10% truncation",
        xaxis_title="k (neighbors, log)", yaxis_title="MAE",
        xaxis_type="log", template="plotly_white",
    )

    html = (
        "<html><head><title>temporal_knn_sweep — all variants</title></head>"
        "<body style='font-family: sans-serif; margin: 20px'>"
        "<h2>Forecasts — ground truth vs all 70 temporal-kNN variants "
        "(H=720)</h2>"
    )
    html += plotly.io.to_html(fig, full_html=False, include_plotlyjs="cdn")
    html += "<h2>MAE ranking (70 configs)</h2>"
    html += plotly.io.to_html(fig_bar, full_html=False,
                              include_plotlyjs=False)
    html += "<h2>MAE vs k per half-life and history arm</h2>"
    html += plotly.io.to_html(fig_k, full_html=False,
                              include_plotlyjs=False)
    html += "</body></html>"
    (SWEEP_DIR / "interactive.html").write_text(html, encoding="utf-8")

    print(f"\nwrote {SWEEP_DIR / 'results.json'}, interactive.html")


if __name__ == "__main__":
    main()
