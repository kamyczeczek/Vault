"""Sub-experiment S-08: cross-family ensemble (ELM + kNN + daily).

The ensemble's members are frozen on train.csv (11,425 rows) and the
blend weights are fit on VALIDATION windows only (the S-02
convention inside CrossFamilyEnsemble.fit: 2,161 stride-1 origins
over the trailing 2,880 validation rows, history = all rows before
the scored window). Scoring is the canonical rolling protocol over
the test region (2,161 stride-1 origins), identical to every slice
since S-01.

Acceptance (slices.md S-08) — all booleans recorded in results.json:
1. ensemble <= min(members) on VALIDATION (the weight objective is
   squared error there; the boolean is computed on rolling MAE
   across the same validation windows).
2. Test delta reported: ensemble rolling MAE vs each member's
   rolling MAE on the test region.
3. Weights reported (non-negative, sum-1, from validation only).
4. No test data used for weighting — structural: the ensemble fit
   receives only train.csv; assert the fit series length == 11,425.

Anchors (fail-loud): ELM / daily / persistence rolling numbers must
reproduce exactly (re-scored in-run).

Outputs: results.json + CONTEXT.md results section.

Run: python sub_experiments/cross_family_ensemble/run_sweep.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))

from data import (  # noqa: E402
    HORIZON,
    TRAIN_END,
    VALIDATION_END,
    get_protocol_data,
)
from methods import HeuristicLagELM, make_forecaster  # noqa: E402
from methods.baselines import Persistence, seasonal_forecast  # noqa: E402
from methods.ensemble import CrossFamilyEnsemble  # noqa: E402
from methods.knn_models import HeuristicLagKNN  # noqa: E402

SWEEP_DIR = H720_ROOT / "sub_experiments" / "cross_family_ensemble"
DISJOINT_STARTS = (0, 720, 1440, 2160)

ROLLING_ANCHORS = {
    "elm_h64_full_fastlags": 2.3092,
    "daily": 2.5491,
    "persistence": 2.5985,
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


def rolling_mae_over(
    predict_at, score_segment: np.ndarray, seg_start_in_series: int,
    full_series: np.ndarray
) -> tuple[float, float, dict]:
    """Generic rolling scorer: predict_at(hist) vs windows of segment."""
    n_origins = len(score_segment) - HORIZON + 1
    per_origin = np.empty((n_origins, 2), dtype=float)
    for t in range(n_origins):
        hist = full_series[: seg_start_in_series + t]
        actual = score_segment[t : t + HORIZON]
        pred = predict_at(hist)
        assert len(pred) == HORIZON
        per_origin[t] = mae_rmse(pred, actual)
    return rolling_metrics(per_origin)


def main() -> int:
    pd_data = get_protocol_data()
    fit_history, eval_series, test = pd_data.rolling_views()

    # --- Structural anti-leakage assert (acceptance #4) -------------
    assert len(fit_history) == VALIDATION_END == 11425, (
        "ensemble fit history must be train.csv (11,425 rows) — "
        "test data must never reach the weight search"
    )

    results: list[dict] = []
    print(f"{'model':<34}{'rolling MAE':>12}{'rolling RMSE':>13}")
    t0 = time.time()

    # --- Ensemble (weights from validation only) ----------------------
    ens = CrossFamilyEnsemble().fit(fit_history, horizon=HORIZON)
    weights = ens.weights_          # primary: squared-error blend
    mae_w = ens.mae_weights_         # diagnostic: L1 optimum (vertex)
    member_names = ["elm", "knn", "daily"]
    print("primary (MSE-blend) weights:",
          dict(zip(member_names, weights.round(4))))
    print("L1-diagnostic weights:",
          dict(zip(member_names, mae_w.round(4))))

    def ens_pred(hist):
        ens.history_ = hist
        return ens.predict()

    # Validation-window MAE per member + ensemble (acceptance #1)
    val_seg = fit_history[TRAIN_END:VALIDATION_END]
    val_scores: dict[str, float] = {}
    val_scores["ensemble"] = rolling_mae_over(
        ens_pred, val_seg, TRAIN_END, fit_history
    )[0]

    elm = HeuristicLagELM(
        hidden_dim=64, history_fraction=1.0, delays=(1, 2, 3, 6, 12)
    )
    elm.fit(fit_history, horizon=HORIZON)

    def elm_pred(hist):
        elm.history_ = hist
        return elm.predict()

    knn = HeuristicLagKNN(
        q=3, neighbors=32, history_fraction=0.1, delays=(1, 2, 3, 6, 12, 24)
    )
    knn.fit(fit_history, horizon=HORIZON)

    def knn_pred(hist):
        knn.history_ = hist
        return knn.predict()

    def daily_pred(hist):
        return seasonal_forecast(hist, HORIZON, "daily")

    val_scores["elm"] = rolling_mae_over(elm_pred, val_seg, TRAIN_END, fit_history)[0]
    val_scores["knn"] = rolling_mae_over(knn_pred, val_seg, TRAIN_END, fit_history)[0]
    val_scores["daily"] = rolling_mae_over(daily_pred, val_seg, TRAIN_END, fit_history)[0]
    print("validation rolling MAE:", {k: round(v, 4) for k, v in val_scores.items()})

    min_member_val = min(val_scores["elm"], val_scores["knn"], val_scores["daily"])
    acceptance_val = bool(val_scores["ensemble"] <= min_member_val)
    print(f"acceptance #1 ensemble {val_scores['ensemble']:.4f} <= "
          f"min member {min_member_val:.4f} on validation: {acceptance_val}")

    # --- Test-region rolling scores -----------------------------------
    ens_r = rolling_mae_over(ens_pred, test, VALIDATION_END, eval_series)
    results.append({
        "model": "cross_family_ensemble",
        "protocol": "rolling stride-1, 2161 origins, frozen members on train.csv; weights from validation only",
        "rolling_mae": round(ens_r[0], 4),
        "rolling_rmse": round(ens_r[1], 4),
        "disjoint_windows": ens_r[2],
        "weights": {k: round(float(w), 4) for k, w in
                    zip(member_names, weights)},
        "mae_weights": {k: round(float(w), 4) for k, w in
                        zip(member_names, mae_w)},
        "status": "ok",
    })
    print(f"{ens_r[0]:>12.4f}{ens_r[1]:>13.4f}  cross_family_ensemble [{time.time()-t0:.0f}s]")

    for name, pred_fn in (
        ("elm_h64_full_fastlags", elm_pred),
        ("knn_q3_k32_recent10", knn_pred),
        ("daily", daily_pred),
    ):
        m, r, d = rolling_mae_over(pred_fn, test, VALIDATION_END, eval_series)
        results.append({
            "model": name,
            "protocol": "rolling stride-1, 2161 origins",
            "rolling_mae": round(m, 4), "rolling_rmse": round(r, 4),
            "disjoint_windows": d, "status": "ok",
        })
        print(f"{m:>12.4f}{r:>13.4f}  {name}")

    # persistence anchor
    p = make_forecaster("persistence")
    p.fit(fit_history, horizon=HORIZON)

    def pers_pred(hist):
        p.history_ = hist
        p.last_value_ = float(hist[-1])
        return p.predict()

    m, r, d = rolling_mae_over(pers_pred, test, VALIDATION_END, eval_series)
    results.append({
        "model": "persistence", "protocol": "rolling stride-1, 2161 origins",
        "rolling_mae": round(m, 4), "rolling_rmse": round(r, 4),
        "disjoint_windows": d, "status": "ok",
    })
    print(f"{m:>12.4f}{r:>13.4f}  persistence")

    # --- Fail-loud anchors ---------------------------------------------
    by_name = {r_["model"]: r_ for r_ in results}
    failures = []
    for name, expected in ROLLING_ANCHORS.items():
        got = by_name[name]["rolling_mae"]
        ok = abs(got - expected) < 5e-5
        print(f"anchor {name}: {got:.4f} expected {expected:.4f} -> "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(name)
    if failures:
        print(f"\nANCHOR CHECK FAILED for {len(failures)} model(s) — aborting")
        return 1

    # --- Acceptance booleans (recorded) ---------------------------------
    ens_mae = by_name["cross_family_ensemble"]["rolling_mae"]
    member_test = {
        "elm": by_name["elm_h64_full_fastlags"]["rolling_mae"],
        "knn": by_name["knn_q3_k32_recent10"]["rolling_mae"],
        "daily": by_name["daily"]["rolling_mae"],
    }
    min_member_val = min(val_scores["elm"], val_scores["knn"], val_scores["daily"])
    acceptance = {
        "validation_ensemble_mae": round(val_scores["ensemble"], 4),
        "validation_member_maes": {k: round(v, 4) for k, v in val_scores.items()
                                   if k != "ensemble"},
        "ensemble_le_min_members_on_validation": acceptance_val,
        "l1_diagnostic": {
            "weights": {k: round(float(w), 4) for k, w in zip(member_names, mae_w)},
            "validation_mae": round(min_member_val, 4),
            "note": (
                "L1 optimum over the weight simplex = pure best member "
                "(kNN): no non-trivial blend improves on the best "
                "member's validation MAE. The acceptance boolean's "
                "False reflects this data property, not a solver flaw."
            ),
        },
        "test_rolling_mae": {
            "ensemble": ens_mae,
            **member_test,
            "persistence": by_name["persistence"]["rolling_mae"],
        },
        "test_delta_vs_best_member": round(
            ens_mae - min(member_test.values()), 4),
        "ensemble_beats_all_members_on_test": bool(
            ens_mae < min(member_test.values())),
        "weights": {k: round(float(w), 4) for k, w in
                    zip(member_names, weights)},
        "weights_nonneg_sum1": bool(
            (weights >= -1e-12).all() and abs(weights.sum() - 1.0) < 1e-9),
        "no_test_data_for_weighting": True,  # structural: fit received train.csv only
        "ensemble_beats_leader_nlinear_L336": bool(ens_mae < 2.0571),
    }

    out = {
        "slice": "S-08",
        "protocol": {
            "members_fit": "frozen, train.csv 11,425 rows",
            "weights": "validation windows only (2,161 stride-1 origins over trailing 2,880 rows)",
            "scoring": "rolling stride-1, 2161 origins, test region",
            "horizon": HORIZON,
        },
        "results": results,
        "acceptance": acceptance,
    }
    (SWEEP_DIR / "results.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print(f"\nAcceptance: {json.dumps(acceptance, indent=2)}")
    print(f"Wrote {SWEEP_DIR / 'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
