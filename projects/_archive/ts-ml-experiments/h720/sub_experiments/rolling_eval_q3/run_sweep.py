"""Sub-experiment: rolling-origin evaluation of the q3 kNN k-grid (H=720).

Implements the user-named priority of plan scope `h720-s01` (leaf-1,
`.unlazy/h720-s01/PLAN.md` C1). The legacy `q3_k_sweep` experiment scored
a single 720-row window (``test.csv[:720]``) — one high-variance draw that
crowned ``k=32`` the family optimum. This harness re-scores the full
13-config k-grid over sliding stride-1 origins across the 2,880-row test
region, under the S-01 rolling protocol (pattern:
``sub_experiments/rolling_eval/run_sweep.py``):

- **Family**: ``HeuristicLagKNN(q=3, neighbors=k, history_fraction=0.1,
  delays=(1,2,3,6,12,24))`` for k in {1,2,3,4,5,6,8,10,12,16,20,24,32}.
- **Frozen fit**: every model is fit exactly once on all of
  ``train.csv`` (11,425 rows) — the locked protocol's fit history.
  Note: ``history_fraction=0.1`` is applied *inside* the model to the
  full fit history (most recent 10% of train.csv origins) — never to a
  pre-sliced window.
- **Per-origin history**: at origin ``t`` (test-row index), the model's
  ``history_`` is set to ``eval_series[:11425+t]`` — every observed row
  strictly before the scored window. Past test-region rows are part of
  the history at forecast time (benchmark sliding-window convention);
  the scored rows themselves are never seen.
- **2,161 origins** (``t in [0, 2160]``, stride 1) per model: MAE/RMSE
  averaged over origins.
- **Disjoint-window spread**: secondary diagnostic — the frozen-fit
  forecasts at t = 0, 720, 1440, 2160 (four disjoint 720-row windows),
  plus the max/min window-MAE ratio (stability).

Anti-leakage: the scored window ``test[t:t+720]`` is never part of the
history slice ``eval_series[:11425+t]`` (the slice ends one row before
the window starts) — structurally guaranteed by the slicing, checked by
assertion in the runner.

Anchors (MUST reproduce the legacy q3_k_sweep 4-decimal numbers at
origin t=0 — the legacy single-origin protocol is exactly this harness's
first window; failure aborts the run, no silent numbers):
- ``knn_q3_k32_recent10`` -> MAE 1.7204 / RMSE 2.1405
- ``knn_q3_k3_recent10``  -> MAE 2.8565 / RMSE 3.3663

Outputs (in this directory):
- ``results.json`` — per-k rolling + disjoint metrics, stability ratios,
  legacy-t0 comparison, anchors
- ``CONTEXT.md``   — results section (updated by hand after the run)

Data: shared chronological split via ``data.py`` (frozen fit on
train.csv, sliding evaluation over the full test region — see
``data.py::ProtocolData.rolling_views``). No RNG anywhere: KNN with
distance weights is fully deterministic.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, VALIDATION_END, get_protocol_data  # noqa: E402
from methods import HeuristicLagKNN  # noqa: E402

SWEEP_DIR = H720_ROOT / "sub_experiments" / "rolling_eval_q3"

DEFAULT_LAGS = (1, 2, 3, 6, 12, 24)
Q3_K_GRID = (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32)
DISJOINT_STARTS = (0, 720, 1440, 2160)


def model_name(k: int) -> str:
    return f"knn_q3_k{k}_recent10"


# Legacy q3_k_sweep single-origin (t=0) anchors, 4 decimals
# (sub_experiments/q3_k_sweep/CONTEXT.md, re-verified 2026-09-02).
ANCHORS = {
    "knn_q3_k32_recent10": (1.7204, 2.1405),
    "knn_q3_k3_recent10": (2.8565, 3.3663),
}

# Legacy q3_k_sweep t=0 MAE for the whole k-grid (same source table);
# carried into results.json for the rolling-vs-legacy comparison.
LEGACY_T0_MAE = {
    1: 3.3836, 2: 2.8347, 3: 2.8565, 4: 2.9516, 5: 2.9054, 6: 2.7639,
    8: 2.1921, 10: 2.2421, 12: 2.0515, 16: 2.0081, 20: 1.7747,
    24: 1.7553, 32: 1.7204,
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
    fresh (no refit, no state carry-over). The KNN index (``model_``)
    stays frozen — fitted once on train.csv.
    """
    n_origins = len(test) - HORIZON + 1  # 2,161
    per_origin = np.empty((n_origins, 2), dtype=float)

    for t in range(n_origins):
        hist_end = VALIDATION_END + t
        # Anti-leakage: history ends one row before the scored window.
        assert hist_end <= len(eval_series), "history slice overruns eval series"
        hist = eval_series[:hist_end]
        actual = test[t : t + HORIZON]

        model.history_ = hist
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


def check_anchors(
    models: list[tuple[str, object, int]],
    fit_history: np.ndarray,
    test: np.ndarray,
) -> list[dict]:
    """Origin t=0 must reproduce the legacy 4-decimal numbers exactly.

    Emitted in ``ANCHORS`` order (k32 first) so the ledger's G2 CHECK
    prints ``anchors pass: k32`` first.
    """
    by_name = {name: model for name, model, _k in models}
    anchor_results = []
    for name, (exp_mae, exp_rmse) in ANCHORS.items():
        model = by_name[name]
        model.history_ = fit_history
        pred = model.predict()
        mae, rmse = mae_rmse(pred, test[:HORIZON])
        ok = bool(abs(mae - exp_mae) < 5e-5 and abs(rmse - exp_rmse) < 5e-5)
        anchor_results.append({
            "model": name, "t0_mae": round(mae, 4), "t0_rmse": round(rmse, 4),
            "expected": [exp_mae, exp_rmse], "ok": ok,
        })
        print(f"anchor {name}: {mae:.4f}/{rmse:.4f} "
              f"expected {exp_mae}/{exp_rmse} -> {'OK' if ok else 'FAIL'}")
    return anchor_results


def main() -> int:
    pd_data = get_protocol_data()
    fit_history, eval_series, test = pd_data.rolling_views()

    # Frozen fits on all of train.csv exactly (the locked protocol's fit
    # history); history_fraction=0.1 truncates origins INSIDE the model.
    models: list[tuple[str, object, int]] = []
    for k in Q3_K_GRID:
        model = HeuristicLagKNN(
            q=3, neighbors=k, history_fraction=0.1, delays=DEFAULT_LAGS
        )
        model.fit(fit_history, horizon=HORIZON)
        models.append((model_name(k), model, k))

    results = []
    print(f"{'model':<24}{'roll MAE':>9}{'roll RMSE':>10}"
          f"{'W1':>8}{'W2':>8}{'W3':>8}{'W4':>8}{'max/min':>8}")
    for name, model, k in models:
        r = evaluate_model(name, model, eval_series, test)
        w = r["disjoint_windows"]
        w_maes = [w[f"window_{i}"]["mae"] for i in range(1, 5)]
        r["k"] = k
        r["max_min_ratio"] = round(max(w_maes) / min(w_maes), 3)
        r["legacy_t0_mae"] = LEGACY_T0_MAE[k]
        r["t0_matches_legacy"] = bool(
            abs(w_maes[0] - LEGACY_T0_MAE[k]) < 5e-5
        )
        results.append(r)
        print(f"{name:<24}{r['rolling_mae']:>9.4f}{r['rolling_rmse']:>10.4f}"
              f"{w_maes[0]:>8.4f}{w_maes[1]:>8.4f}{w_maes[2]:>8.4f}"
              f"{w_maes[3]:>8.4f}{r['max_min_ratio']:>8.2f}")

    n_match = sum(1 for r in results if r["t0_matches_legacy"])
    print(f"t=0 window matches legacy q3_k_sweep table: "
          f"{n_match}/{len(results)} (4-decimal)")

    anchor_results = check_anchors(models, fit_history, test)
    failed = [a for a in anchor_results if not a["ok"]]
    if failed:
        print(f"\nANCHOR CHECK FAILED for {len(failed)} model(s) — aborting, "
              f"no results.json written")
        for a in failed:
            print(f"  {a['model']}: got {a['t0_mae']}/{a['t0_rmse']}, "
                  f"expected {a['expected']}")
        return 1

    out = {
        "slice": "S-01-q3",
        "protocol": {
            "fit": "frozen, train.csv 11,425 rows, fit once",
            "origins": 2161,
            "stride": 1,
            "horizon": HORIZON,
            "family": ("HeuristicLagKNN(q=3, history_fraction=0.1, "
                       "delays=(1,2,3,6,12,24))"),
            "k_grid": list(Q3_K_GRID),
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
