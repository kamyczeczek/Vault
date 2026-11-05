"""S-11 sweep: seasonal-residual + RBF-hidden ELM arms on ETTh1 (t=0).

Single-origin (t=0) arms — fit on the locked train history (11,425
rows), predict the first 720-row test window, score against
``forecast_views()`` ground truth. Arms advance to the canonical
rolling arm (2,161 stride-1 origins) — per the S-08/S-09/S-10
lesson, t=0 ordering is NOT trusted; every arm is rolled.

Grid (user-suggested RBF folded into the slice):
- identity arm  ``res_tanh_eq_parent`` — SeasonalResidualELM
  mode="raw" + parent config; must reproduce the parent ELM t=0
  MAE 1.5923 byte-identically (second identity check on real data;
  the smoke already pins synthetic identity).
- residual tanh arms: m=24 (daily), m=168 (weekly).
- RBF arms (Gaussian centers from feature rows, seed 42): raw
  norm-off, norm@168, norm@720 — the S-04 kNN-normalization
  asymmetry hypothesis (local kernels should inherit the gain).
- combined arm: RBF + residual m=24 (both biases at once), plus
  the norm@720 variant.
- capacity sensitivity: h32/h256 on residual m24 and RBF raw.
- anchors: daily (canonical ``seasonal_forecast`` lag-24), weekly168
  (trailing-168h tile), persistence — all computed here fail-loud
  (S-10 P4: never re-implement daily inline; import the helper).

Deterministic: seed-42 draws only. Writes results.json (sorted,
4-decimal).

Run: python sub_experiments/residual_rbf_sweep/run_sweep.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))

from data import get_protocol_data  # noqa: E402
from methods.baselines import seasonal_forecast  # noqa: E402
from methods.neural_models import HeuristicLagELM  # noqa: E402
from methods.rbf import RBFELM  # noqa: E402
from methods.residual import SeasonalResidualELM  # noqa: E402

HORIZON = 720
PARENT_T0_MAE = 1.5923  # S-01/S-09/S-10 t=0 reference, 4-decimal


def mae_rmse(pred: np.ndarray, actual: np.ndarray) -> tuple[float, float]:
    err = np.asarray(pred, dtype=float) - np.asarray(actual, dtype=float)
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err ** 2)))


def main() -> int:
    fit_history, ground_truth = get_protocol_data().forecast_views()
    if len(fit_history) != 11_425 or ground_truth.shape != (HORIZON,):
        raise RuntimeError(f"protocol sanity failed: {len(fit_history)} rows, "
                           f"gt {np.shape(ground_truth)}")

    def run(label: str, model) -> dict:
        t0 = time.time()
        model.fit(fit_history, horizon=HORIZON)
        mae, rmse = mae_rmse(model.predict(), ground_truth)
        return {"mae": round(mae, 4), "rmse": round(rmse, 4),
                "fit_s": round(time.time() - t0, 2)}

    results: dict[str, dict] = {}

    # identity arm — parent config exactly (raw mode = parent pathway)
    results["res_tanh_eq_parent"] = run(
        "res_tanh_eq_parent",
        SeasonalResidualELM(mode="raw", hidden_dim=64,
                            history_fraction=1.0,
                            delays=(1, 2, 3, 6, 12)),
    )
    # second identity via the registry class (guards the wiring too)
    results["parent_elm_direct"] = run(
        "parent_elm_direct",
        HeuristicLagELM(hidden_dim=64, history_fraction=1.0,
                        delays=(1, 2, 3, 6, 12)),
    )

    # residual tanh arms
    results["res_tanh_m24"] = run(
        "res_tanh_m24", SeasonalResidualELM(period=24))
    results["res_tanh_m168"] = run(
        "res_tanh_m168", SeasonalResidualELM(period=168))

    # RBF arms — norm hypothesis (S-04 asymmetry)
    results["rbf_raw"] = run("rbf_raw", RBFELM())
    results["rbf_norm168"] = run(
        "rbf_norm168", RBFELM(normalize_scale=True, scale_window=168))
    results["rbf_norm720"] = run(
        "rbf_norm720", RBFELM(normalize_scale=True, scale_window=720))

    # combined arms — local kernels + seasonal residual
    results["rbf_res24"] = run(
        "rbf_res24", RBFELM(residual_period=24))
    results["rbf_res24_norm720"] = run(
        "rbf_res24_norm720",
        RBFELM(residual_period=24, normalize_scale=True,
               scale_window=720))

    # capacity sensitivity
    results["res_tanh_m24_h256"] = run(
        "res_tanh_m24_h256", SeasonalResidualELM(period=24,
                                                 hidden_dim=256))
    results["rbf_raw_h256"] = run("rbf_raw_h256", RBFELM(hidden_dim=256))
    results["rbf_raw_h32"] = run("rbf_raw_h32", RBFELM(hidden_dim=32))

    # anchors (fail-loud, computed here — canonical helpers only)
    daily = seasonal_forecast(fit_history, HORIZON, "daily")  # lag 24
    weekly168 = np.tile(fit_history[-168:], 1 + HORIZON // 168)[:HORIZON]
    persistence = np.full(HORIZON, fit_history[-1])
    for label, p in [("daily", daily), ("weekly168", weekly168),
                     ("persistence", persistence)]:
        mae, rmse = mae_rmse(p, ground_truth)
        results[label] = {"mae": round(mae, 4), "rmse": round(rmse, 4)}

    # identity gates on real data
    ok_id = results["res_tanh_eq_parent"]["mae"] == PARENT_T0_MAE
    ok_direct = (results["parent_elm_direct"]["mae"]
                 == results["res_tanh_eq_parent"]["mae"])
    results["identity_gate"] = {
        "res_raw_t0_mae": results["res_tanh_eq_parent"]["mae"],
        "parent_t0_mae": PARENT_T0_MAE,
        "parent_direct_t0_mae": results["parent_elm_direct"]["mae"],
        "pass": bool(ok_id and ok_direct),
    }
    results = dict(sorted(results.items()))
    (HERE / "results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"{'config':<22}{'t=0 MAE':>10}{'RMSE':>10}{'fit s':>8}")
    order = ["res_tanh_eq_parent", "parent_elm_direct", "res_tanh_m24",
             "res_tanh_m168", "rbf_raw", "rbf_norm168", "rbf_norm720",
             "rbf_res24", "rbf_res24_norm720", "res_tanh_m24_h256",
             "rbf_raw_h256", "rbf_raw_h32", "daily", "weekly168",
             "persistence"]
    for label in order:
        row = results[label]
        print(f"{label:<22}{row['mae']:>10.4f}{row['rmse']:>10.4f}"
              f"{row.get('fit_s', 0):>8.1f}")
    print(f"\nidentity res-raw vs parent t=0: "
          f"{results['res_tanh_eq_parent']['mae']:.4f} == {PARENT_T0_MAE} "
          f"and direct {results['parent_elm_direct']['mae']:.4f} "
          f"-> {'PASS' if ok_id and ok_direct else 'FAIL'}")
    return 0 if (ok_id and ok_direct) else 1


if __name__ == "__main__":
    sys.exit(main())
