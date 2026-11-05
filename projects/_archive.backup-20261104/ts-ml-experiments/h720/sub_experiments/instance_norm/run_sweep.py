"""Sub-experiment: instance (window-std) normalization on the HeuristicLag*
pipeline (S-04, plan slice in ``PROCESS/03_plan/slices.md``).

RevIN-style scale normalization: lag features AND multi-step targets are
divided by the trailing-window population std of the raw series at each
origin (window ``scale_window``, clamped at ``_SCALE_EPS``); predictions
are re-scaled by the forecast-time window std before the anchor is added
back. Optional per-output affine readout correction (least squares;
kNN uses leave-one-out predictions — in-sample kNN is degenerate).

Protocol (identical to S-01 rolling_eval):
- **Frozen fit**: every model fit exactly once on all of ``train.csv``
  (11,425 rows).
- **Rolling**: 2,161 stride-1 origins across the full test region; at
  origin ``t`` the model's ``history_`` is ``eval_series[:11425+t]``.
- **Anchors (fail-loud)**: the parent configs and references MUST
  reproduce the S-01 rolling numbers to 4 decimals (rolling means), and
  the t=0 legacy numbers. Aborts before writing on any mismatch.

Config grid (2 families × {parent, norm@168, norm@168+affine,
norm@720, norm@720+affine}):
- ELM parent = leaderboard leader: h64, full history, fast lags
  (1,2,3,6,12), normal init (rolling 2.3092 / 2.8046).
- kNN parent = best kNN: q=3, k=32, recent-10%, default lags
  (1,2,3,6,12,24) (rolling 2.5583 / 3.0994).

References (same protocol): daily seasonal-naive (2.5491 / 3.1120),
persistence (2.5985 / 3.1282).

Outputs (in this directory):
- ``results.json`` — per-config rolling + disjoint metrics, deltas vs
  parent in raw and train-σ units, win/lose vs daily, anchors.
- ``CONTEXT.md`` — results section (written by hand after the run).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, VALIDATION_END, get_protocol_data  # noqa: E402
from methods import HeuristicLagELM, HeuristicLagKNN  # noqa: E402
from methods.baselines import Persistence, seasonal_forecast  # noqa: E402

SWEEP_DIR = H720_ROOT / "sub_experiments" / "instance_norm"
DISJOINT_STARTS = (0, 720, 1440, 2160)

FAST_LAGS = (1, 2, 3, 6, 12)
DEFAULT_LAGS = (1, 2, 3, 6, 12, 24)

# S-01 rolling numbers (canonical leaderboard) — 4-decimal anchors.
ROLLING_ANCHORS = {
    "elm_parent": (2.3092, 2.8046),
    "knn_parent": (2.5583, 3.0994),
    "daily": (2.5491, 3.1120),
    "persistence": (2.5985, 3.1282),
}
# Legacy t=0 anchors (the rolling harness's first window).
T0_ANCHORS = {
    "elm_parent": (1.5923, 1.9823),
    "knn_parent": (1.7204, 2.1405),
    "daily": (1.6720, 2.1719),
    "persistence": (1.7952, 2.2503),
}


def mae_rmse(pred: np.ndarray, actual: np.ndarray) -> tuple[float, float]:
    err = actual - pred
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))


def rolling_metrics(per_origin: np.ndarray) -> tuple[float, float, dict]:
    rolling_mae = float(np.mean(per_origin[:, 0]))
    rolling_rmse = float(np.mean(per_origin[:, 1]))
    disjoint = {
        f"window_{i + 1}": {
            "mae": float(per_origin[t, 0]),
            "rmse": float(per_origin[t, 1]),
        }
        for i, t in enumerate(DISJOINT_STARTS)
    }
    return rolling_mae, rolling_rmse, disjoint


def evaluate_model(name: str, model, eval_series: np.ndarray, test: np.ndarray) -> dict:
    n_origins = len(test) - HORIZON + 1  # 2,161
    per_origin = np.empty((n_origins, 2), dtype=float)
    is_persistence = isinstance(model, Persistence)
    for t in range(n_origins):
        hist = eval_series[: VALIDATION_END + t]
        model.history_ = hist
        if is_persistence:
            model.last_value_ = float(hist[-1])
        pred = model.predict()
        assert len(pred) == HORIZON, f"{name}: predict returned {len(pred)}"
        per_origin[t] = mae_rmse(pred, test[t : t + HORIZON])
    rolling_mae, rolling_rmse, disjoint = rolling_metrics(per_origin)
    return {
        "model": name,
        "protocol": "rolling stride-1, 2161 origins, frozen fit on train.csv",
        "rolling_mae": round(rolling_mae, 4),
        "rolling_rmse": round(rolling_rmse, 4),
        "t0_mae": round(float(per_origin[0, 0]), 4),
        "t0_rmse": round(float(per_origin[0, 1]), 4),
        "disjoint_windows": disjoint,
        "status": "ok",
    }


def check_anchors(
    results: dict[str, dict],
) -> list[dict]:
    """Parents + references must reproduce S-01 rolling AND t=0 numbers."""
    out = []
    for name, (exp_rm, exp_rr) in ROLLING_ANCHORS.items():
        r = results[name]
        ok_r = abs(r["rolling_mae"] - exp_rm) < 5e-5 and abs(r["rolling_rmse"] - exp_rr) < 5e-5
        exp_m, exp_rm2 = T0_ANCHORS[name]
        ok_t = abs(r["t0_mae"] - exp_m) < 5e-5 and abs(r["t0_rmse"] - exp_rm2) < 5e-5
        out.append({
            "model": name,
            "rolling": (r["rolling_mae"], r["rolling_rmse"]),
            "expected_rolling": [exp_rm, exp_rr],
            "t0": (r["t0_mae"], r["t0_rmse"]),
            "expected_t0": [exp_m, exp_rm2],
            "ok": bool(ok_r and ok_t),
        })
        print(f"anchor {name}: rolling {r['rolling_mae']:.4f}/{r['rolling_rmse']:.4f} "
              f"(exp {exp_rm}/{exp_rr}), t0 {r['t0_mae']:.4f}/{r['t0_rmse']:.4f} "
              f"(exp {exp_m}/{exp_rm2}) -> {'OK' if (ok_r and ok_t) else 'FAIL'}")
    return out


def main() -> int:
    pd_data = get_protocol_data()
    fit_history, eval_series, test = pd_data.rolling_views()
    train_sigma = float(np.std(fit_history))
    print(f"train-σ (fit history population std): {train_sigma:.4f}")

    configs: list[tuple[str, object]] = [
        ("elm_parent", HeuristicLagELM(
            hidden_dim=64, history_fraction=1.0, delays=FAST_LAGS)),
        ("elm_norm168", HeuristicLagELM(
            hidden_dim=64, history_fraction=1.0, delays=FAST_LAGS,
            normalize_scale=True, scale_window=168)),
        ("elm_norm168_affine", HeuristicLagELM(
            hidden_dim=64, history_fraction=1.0, delays=FAST_LAGS,
            normalize_scale=True, scale_window=168, affine=True)),
        ("elm_norm720", HeuristicLagELM(
            hidden_dim=64, history_fraction=1.0, delays=FAST_LAGS,
            normalize_scale=True, scale_window=720)),
        ("elm_norm720_affine", HeuristicLagELM(
            hidden_dim=64, history_fraction=1.0, delays=FAST_LAGS,
            normalize_scale=True, scale_window=720, affine=True)),
        ("knn_parent", HeuristicLagKNN(
            q=3, neighbors=32, history_fraction=0.1, delays=DEFAULT_LAGS)),
        ("knn_norm168", HeuristicLagKNN(
            q=3, neighbors=32, history_fraction=0.1, delays=DEFAULT_LAGS,
            normalize_scale=True, scale_window=168)),
        ("knn_norm168_affine", HeuristicLagKNN(
            q=3, neighbors=32, history_fraction=0.1, delays=DEFAULT_LAGS,
            normalize_scale=True, scale_window=168, affine=True)),
        ("knn_norm720", HeuristicLagKNN(
            q=3, neighbors=32, history_fraction=0.1, delays=DEFAULT_LAGS,
            normalize_scale=True, scale_window=720)),
        ("knn_norm720_affine", HeuristicLagKNN(
            q=3, neighbors=32, history_fraction=0.1, delays=DEFAULT_LAGS,
            normalize_scale=True, scale_window=720, affine=True)),
        ("persistence", Persistence()),
    ]

    results: dict[str, dict] = {}
    print(f"\n{'model':<22}{'rolling MAE':>12}{'rolling RMSE':>13}   t0 MAE")
    for name, model in configs:
        model.fit(fit_history, horizon=HORIZON)
        r = evaluate_model(name, model, eval_series, test)
        results[name] = r
        print(f"{r['rolling_mae']:>12.4f}{r['rolling_rmse']:>13.4f}"
              f"   {r['t0_mae']:.4f}  {name}")

    # daily reference (function-based)
    n_origins = len(test) - HORIZON + 1
    per_origin = np.empty((n_origins, 2), dtype=float)
    for t in range(n_origins):
        hist = eval_series[: VALIDATION_END + t]
        per_origin[t] = mae_rmse(seasonal_forecast(hist, HORIZON, "daily"),
                                 test[t : t + HORIZON])
    rolling_mae, rolling_rmse, disjoint = rolling_metrics(per_origin)
    results["daily"] = {
        "model": "daily",
        "protocol": "rolling stride-1, 2161 origins, seasonal-naive lag 24",
        "rolling_mae": round(rolling_mae, 4),
        "rolling_rmse": round(rolling_rmse, 4),
        "t0_mae": round(float(per_origin[0, 0]), 4),
        "t0_rmse": round(float(per_origin[0, 1]), 4),
        "disjoint_windows": disjoint,
        "status": "ok",
    }
    print(f"{results['daily']['rolling_mae']:>12.4f}"
          f"{results['daily']['rolling_rmse']:>13.4f}   "
          f"{results['daily']['t0_mae']:.4f}  daily")

    anchors = check_anchors(results)
    failed = [a for a in anchors if not a["ok"]]
    if failed:
        print(f"\nANCHOR CHECK FAILED for {len(failed)} model(s) — aborting, "
              f"no results.json written")
        return 1

    # Acceptance deltas: normalized vs parent, raw + train-σ units;
    # win/lose vs daily (same rolling protocol).
    daily_mae = results["daily"]["rolling_mae"]
    deltas = {}
    for family, parent in (("elm", "elm_parent"), ("knn", "knn_parent")):
        pm = results[parent]["rolling_mae"]
        for name, r in results.items():
            if not name.startswith(family + "_") or name == parent:
                continue
            d_raw = r["rolling_mae"] - pm
            deltas[name] = {
                "delta_mae_raw": round(d_raw, 4),
                "delta_mae_train_sigma": round(d_raw / train_sigma, 4),
                "beats_parent": bool(r["rolling_mae"] < pm),
                "vs_daily": "win" if r["rolling_mae"] < daily_mae else "lose",
                "parent_mae": pm,
            }
        deltas[parent] = {
            "delta_mae_raw": 0.0,
            "delta_mae_train_sigma": 0.0,
            "beats_parent": None,
            "vs_daily": "win" if pm < daily_mae else "lose",
            "parent_mae": pm,
        }

    out = {
        "slice": "S-04",
        "protocol": {
            "fit": "frozen, train.csv 11,425 rows, fit once",
            "origins": 2161,
            "stride": 1,
            "horizon": HORIZON,
            "normalization": ("lag features and targets divided by trailing-"
                              "window population std (scale_window rows, "
                              "clamped at 1e-8); predictions re-scaled at "
                              "forecast time; optional per-output affine "
                              "least-squares readout (kNN: leave-one-out)"),
            "train_sigma": round(train_sigma, 4),
        },
        "results": list(results.values()),
        "deltas_vs_parent": deltas,
        "anchors": anchors,
    }
    (SWEEP_DIR / "results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {SWEEP_DIR / 'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
