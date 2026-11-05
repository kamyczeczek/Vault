"""Sub-experiment: rolling-origin evaluation of the top-5 models (H=720).

Implements plan slice S-01 (`PROCESS/03_plan/slices.md`). The legacy
protocol scored a single 720-row window (``test.csv[:720]``) — one
high-variance draw. This harness scores every model over sliding
stride-1 origins across the full 2,880-row test region:

- **Frozen fit**: every model is fit exactly once on all of
  ``train.csv`` (11,425 rows) — the locked protocol's fit history.
- **Per-origin history**: at origin ``t`` (test-row index), the model's
  ``history_`` is set to ``eval_series[:11425+t]`` — every observed row
  strictly before the scored window. Past test-region rows are part of
  the history at forecast time (benchmark sliding-window convention);
  the scored rows themselves are never seen.
- **2,161 origins** (``t in [0, 2160]``, stride 1) per model: MAE/RMSE
  averaged over origins; per-window metrics also stored for spread
  analysis.
- **Disjoint-window spread**: secondary diagnostic — the frozen-fit
  forecasts at t = 0, 720, 1440, 2160 (four disjoint 720-row windows).

Anti-leakage: the scored window ``test[t:t+720]`` is never part of the
history slice ``eval_series[:11425+t]`` (the slice ends one row before
the window starts) — structurally guaranteed by the slicing, checked by
assertion in the runner.

Anchors (MUST reproduce to 4 decimals at origin t=0 — the legacy
single-origin protocol is exactly this harness's first window; failure
aborts the run, no silent numbers):
- ``elm_h64_full_fastlags``   -> MAE 1.5923 / RMSE 1.9823
- ``elm_h256_sobol_iid_full`` -> MAE 1.6330 / RMSE 2.0550
- ``knn_q3_k32_recent10``     -> MAE 1.7204 / RMSE 2.1405
- ``daily``                   -> MAE 1.6720 / RMSE 2.1719
- ``persistence``             -> MAE 1.7952 / RMSE 2.2503

Outputs (in this directory):
- ``results.json`` — per-model rolling + disjoint metrics + anchors
- ``CONTEXT.md``   — results section (updated by hand after the run)

Data: shared chronological split via ``data.py`` (frozen fit on
train.csv, sliding evaluation over the full test region — see
``data.py::ProtocolData.rolling_views``).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, VALIDATION_END, get_protocol_data  # noqa: E402
from methods import HeuristicLagELM, HeuristicLagKNN, make_forecaster  # noqa: E402
from methods.baselines import Persistence, seasonal_forecast  # noqa: E402

SWEEP_DIR = H720_ROOT / "sub_experiments" / "rolling_eval"

FAST_LAGS = (1, 2, 3, 6, 12)
DEFAULT_LAGS = (1, 2, 3, 6, 12, 24)
DISJOINT_STARTS = (0, 720, 1440, 2160)

# Legacy leaderboard rows (4-decimal anchors, origin t=0)
ANCHORS = {
    "elm_h64_full_fastlags": (1.5923, 1.9823),
    "elm_h256_sobol_iid_full": (1.6330, 2.0550),
    "knn_q3_k32_recent10": (1.7204, 2.1405),
    "daily": (1.6720, 2.1719),
    "persistence": (1.7952, 2.2503),
}


def mae_rmse(pred: np.ndarray, actual: np.ndarray) -> tuple[float, float]:
    err = actual - pred
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))


def rolling_metrics(per_origin: np.ndarray) -> tuple[float, float, dict]:
    """Aggregate per-origin (mae, rmse) rows into rolling + disjoint views."""
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


def evaluate_model(
    name: str, model, eval_series: np.ndarray, test: np.ndarray
) -> dict:
    """Frozen-fit rolling evaluation of one fitted model.

    At each origin t the model's ``history_`` is re-assigned to the
    trailing slice ending at the origin and ``predict()`` is called
    fresh (no refit, no state carry-over). ``Persistence`` additionally
    re-sets ``last_value_`` (it caches the last history value at fit).
    """
    n_origins = len(test) - HORIZON + 1  # 2,161
    per_origin = np.empty((n_origins, 2), dtype=float)

    is_persistence = isinstance(model, Persistence)
    for t in range(n_origins):
        hist_end = VALIDATION_END + t
        # Anti-leakage: history ends one row before the scored window.
        assert hist_end <= len(eval_series), "history slice overruns eval series"
        hist = eval_series[:hist_end]
        actual = test[t : t + HORIZON]

        model.history_ = hist
        if is_persistence:
            model.last_value_ = float(hist[-1])
        pred = model.predict()

        assert len(pred) == HORIZON, f"{name}: predict returned {len(pred)}"
        per_origin[t] = mae_rmse(pred, actual)

    rolling_mae, rolling_rmse, disjoint = rolling_metrics(per_origin)
    return {
        "model": name,
        "protocol": "rolling stride-1, 2161 origins, frozen fit on train.csv",
        "rolling_mae": round(rolling_mae, 4),
        "rolling_rmse": round(rolling_rmse, 4),
        "disjoint_windows": disjoint,
        "status": "ok",
    }


def evaluate_daily(
    eval_series: np.ndarray, test: np.ndarray
) -> tuple[dict, np.ndarray]:
    """Rolling seasonal-naive (lag 24) — function-based, no fitted state."""
    n_origins = len(test) - HORIZON + 1
    per_origin = np.empty((n_origins, 2), dtype=float)
    for t in range(n_origins):
        hist = eval_series[: VALIDATION_END + t]
        pred = seasonal_forecast(hist, HORIZON, "daily")
        per_origin[t] = mae_rmse(pred, test[t : t + HORIZON])
    rolling_mae, rolling_rmse, disjoint = rolling_metrics(per_origin)
    result = {
        "model": "daily",
        "protocol": "rolling stride-1, 2161 origins, seasonal-naive lag 24",
        "rolling_mae": round(rolling_mae, 4),
        "rolling_rmse": round(rolling_rmse, 4),
        "disjoint_windows": disjoint,
        "status": "ok",
    }
    return result, per_origin


def check_anchors(
    models: list[tuple[str, object]],
    per_origin_daily: np.ndarray,
    fit_history: np.ndarray,
    test: np.ndarray,
) -> list[dict]:
    """Origin t=0 must reproduce the legacy 4-decimal numbers exactly."""
    anchor_results = []
    for name, model in models:
        model.history_ = fit_history
        if isinstance(model, Persistence):
            model.last_value_ = float(fit_history[-1])
        pred = model.predict()
        mae, rmse = mae_rmse(pred, test[:HORIZON])
        exp_mae, exp_rmse = ANCHORS[name]
        ok = bool(abs(mae - exp_mae) < 5e-5 and abs(rmse - exp_rmse) < 5e-5)
        anchor_results.append({
            "model": name, "t0_mae": round(mae, 4), "t0_rmse": round(rmse, 4),
            "expected": [exp_mae, exp_rmse], "ok": ok,
        })
        print(f"anchor {name}: {mae:.4f}/{rmse:.4f} "
              f"expected {exp_mae}/{exp_rmse} -> {'OK' if ok else 'FAIL'}")
    # daily t=0 row (first per-origin row already computed)
    mae, rmse = per_origin_daily[0]
    ok = bool(abs(mae - 1.6720) < 5e-5 and abs(rmse - 2.1719) < 5e-5)
    anchor_results.append({
        "model": "daily", "t0_mae": round(mae, 4), "t0_rmse": round(rmse, 4),
        "expected": [1.6720, 2.1719], "ok": ok,
    })
    print(f"anchor daily: {mae:.4f}/{rmse:.4f} expected 1.6720/2.1719 "
          f"-> {'OK' if ok else 'FAIL'}")
    return anchor_results


def main() -> int:
    pd_data = get_protocol_data()
    fit_history, eval_series, test = pd_data.rolling_views()

    # Frozen fits on train.csv exactly (the locked protocol's fit history)
    models: list[tuple[str, object]] = [
        ("elm_h64_full_fastlags", HeuristicLagELM(
            hidden_dim=64, history_fraction=1.0, delays=FAST_LAGS)),
        ("elm_h256_sobol_iid_full", HeuristicLagELM(
            hidden_dim=256, history_fraction=1.0, delays=FAST_LAGS,
            weight_init="sobol_iid")),
        ("knn_q3_k32_recent10", HeuristicLagKNN(
            q=3, neighbors=32, history_fraction=0.1, delays=DEFAULT_LAGS)),
        ("persistence", make_forecaster("persistence")),
    ]

    results = []
    print(f"{'model':<28}{'rolling MAE':>12}{'rolling RMSE':>13}")
    for name, model in models:
        model.fit(fit_history, horizon=HORIZON)
        r = evaluate_model(name, model, eval_series, test)
        results.append(r)
        print(f"{r['rolling_mae']:>12.4f}{r['rolling_rmse']:>13.4f}  {name}")

    daily_result, per_origin_daily = evaluate_daily(eval_series, test)
    results.append(daily_result)
    print(f"{daily_result['rolling_mae']:>12.4f}"
          f"{daily_result['rolling_rmse']:>13.4f}  daily")

    anchor_results = check_anchors(models, per_origin_daily, fit_history, test)
    failed = [a for a in anchor_results if not a["ok"]]
    if failed:
        print(f"\nANCHOR CHECK FAILED for {len(failed)} model(s) — aborting, "
              f"no results.json written")
        for a in failed:
            print(f"  {a['model']}: got {a['t0_mae']}/{a['t0_rmse']}, "
                  f"expected {a['expected']}")
        return 1

    out = {
        "slice": "S-01",
        "protocol": {
            "fit": "frozen, train.csv 11,425 rows, fit once",
            "origins": 2161,
            "stride": 1,
            "horizon": HORIZON,
            "note": ("per-origin history = all observed rows strictly "
                     "before the scored window"),
        },
        "results": results,
        "anchors_t0": anchor_results,
    }
    (SWEEP_DIR / "results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {SWEEP_DIR / 'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
