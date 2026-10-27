"""S-10 sweep: MultiRateELM rate combinations on ETTh1 (t=0 protocol).

Single-origin (t=0) arms — fit on the locked train history (11,425
rows), predict the first 720-row test window, score against
``forecast_views()`` ground truth. Winning combos advance to the
canonical rolling arm (2,161 stride-1 origins).

Arms:
- identity arm  R=(1,) parent config — must reproduce the parent's
  t=0 MAE 1.5923 byte-identically (second identity check on real
  data; the smoke already pins synthetic identity).
- singles:  R=(1,2) (1,4) (1,8) (1,12) (1,168)
- combos (>=10): (1,2,4) (1,2,8) (1,2,12) (1,2,168) (1,4,8)
  (1,4,12) (1,2,4,8) (1,2,4,12) (1,4,8,12) (1,2,4,8,168)
- capacity-matched sensitivity: hidden 32 (//2) and 128 (*2) on the
  best combo — documents whether the shared-hidden budget binds.
- anchors: daily (seasonal naive m=168) and persistence, fitted on
  train history exactly like every other arm.

Deterministic: no RNG besides the seed-42 draw inside fit.
Writes results.json (sorted, 4-decimal).
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
from methods.multirate import MultiRateELM  # noqa: E402

HORIZON = 720
PARENT_T0_MAE = 1.5923  # S-01/S-09 t=0 reference, 4-decimal


def mae_rmse(pred: np.ndarray, actual: np.ndarray) -> tuple[float, float]:
    err = np.asarray(pred, dtype=float) - np.asarray(actual, dtype=float)
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err ** 2)))


def main() -> int:
    fit_history, ground_truth = get_protocol_data().forecast_views()
    if len(fit_history) != 11_425 or ground_truth.shape != (HORIZON,):
        raise RuntimeError(f"protocol sanity failed: {len(fit_history)} rows, "
                           f"gt {np.shape(ground_truth)}")

    def run(label: str, model: MultiRateELM) -> dict:
        t0 = time.time()
        model.fit(fit_history, horizon=HORIZON)
        mae, rmse = mae_rmse(model.predict(), ground_truth)
        return {"mae": round(mae, 4), "rmse": round(rmse, 4),
                "fit_s": round(time.time() - t0, 2)}

    results: dict[str, dict] = {}

    # identity arm — parent config exactly
    results["R1_eq_parent"] = run("R1_eq_parent", MultiRateELM(
        rates=(1,), hidden_dim=64, history_fraction=1.0,
        lags_per_rate=(1, 2, 3, 6, 12),
    ))
    # singles
    for r in [2, 4, 8, 12, 168]:
        label = f"R1+{r}"
        results[label] = run(label, MultiRateELM(rates=(1, r)))
    # combos
    combos = [
        (1, 2, 4), (1, 2, 8), (1, 2, 12), (1, 2, 168), (1, 4, 8),
        (1, 4, 12), (1, 2, 4, 8), (1, 2, 4, 12), (1, 4, 8, 12),
        (1, 2, 4, 8, 168),
    ]
    for rates in combos:
        label = "R" + "_".join(str(x) for x in rates)
        results[label] = run(label, MultiRateELM(rates=rates))

    # capacity-matched sensitivity on the current best combo
    best_combo = min(
        combos, key=lambda rc: results["R" + "_".join(map(str, rc))]["mae"]
    )
    best_label = "R" + "_".join(str(x) for x in best_combo)
    results[f"{best_label}_h32"] = run(f"{best_label}_h32", MultiRateELM(
        rates=best_combo, hidden_dim=32,
    ))
    results[f"{best_label}_h128"] = run(f"{best_label}_h128", MultiRateELM(
        rates=best_combo, hidden_dim=128,
    ))
    # capacity sensitivity of the best single (rolling front-runner)
    best_single = min(
        [2, 4, 8, 12, 168],
        key=lambda r: results[f"R1+{r}"]["mae"],
    )
    results[f"R1+{best_single}_h32"] = run(
        f"R1+{best_single}_h32",
        MultiRateELM(rates=(1, best_single), hidden_dim=32),
    )
    results[f"R1+{best_single}_h128"] = run(
        f"R1+{best_single}_h128",
        MultiRateELM(rates=(1, best_single), hidden_dim=128),
    )

    # anchors (fail-loud, computed here — not copied from the leaderboard)
    daily = seasonal_forecast(fit_history, HORIZON, "daily")  # lag 24
    weekly168 = np.tile(fit_history[-168:], 1 + HORIZON // 168)[:HORIZON]
    persistence = np.full(HORIZON, fit_history[-1])
    for label, p in [("daily", daily), ("weekly168", weekly168),
                     ("persistence", persistence)]:
        mae, rmse = mae_rmse(p, ground_truth)
        results[label] = {"mae": round(mae, 4), "rmse": round(rmse, 4)}

    # identity gate on real data
    ok = results["R1_eq_parent"]["mae"] == PARENT_T0_MAE
    results["identity_gate"] = {
        "r1_t0_mae": results["R1_eq_parent"]["mae"],
        "parent_t0_mae": PARENT_T0_MAE,
        "pass": ok,
    }
    results = dict(sorted(results.items()))
    (HERE / "results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"{'config':<22}{'t=0 MAE':>10}{'RMSE':>10}{'fit s':>8}")
    for label in ["R1_eq_parent"] + [f"R1+{r}" for r in [2, 4, 8, 12, 168]] \
            + ["R" + "_".join(map(str, rc)) for rc in combos] \
            + [f"R1+{best_single}_h32", f"R1+{best_single}_h128",
               f"{best_label}_h32", f"{best_label}_h128"] \
            + ["daily", "weekly168", "persistence"]:
        row = results[label]
        print(f"{label:<22}{row['mae']:>10.4f}{row['rmse']:>10.4f}"
              f"{row.get('fit_s', 0):>8.1f}")
    print(f"\nidentity R=(1,) vs parent t=0: "
          f"{results['R1_eq_parent']['mae']:.4f} == {PARENT_T0_MAE} "
          f"-> {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
