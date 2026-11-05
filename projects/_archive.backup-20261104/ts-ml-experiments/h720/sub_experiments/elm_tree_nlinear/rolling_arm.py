"""S-22 rolling arm: HeuristicLagELMTreeN under the canonical rolling protocol.

New model: same MI+FNN lags + ELM hidden layer + Decision-Tree readout as
``HeuristicLagELMTree`` (S-09, rolling 2.1706), but with **last-value
anchoring** (NLinear trick): forecast = last(history) + tree(ELM(lags -
last)). Lag features are still centred by last value; only the additive
level term changes from ``mean(last q)`` to ``last``.

Fail-loud anchors (rolling MAE, 4-decimal):
- ELMTree (mean-anchor)      2.1706
- daily                      2.5491
- persistence                2.5985

Run: python sub_experiments/elm_tree_nlinear/rolling_arm.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, VALIDATION_END, get_protocol_data  # noqa: E402
from methods.baselines import seasonal_forecast  # noqa: E402
from methods.neural_models import HeuristicLagELMTree, HeuristicLagELMTreeN  # noqa: E402

SWEEP_DIR = H720_ROOT / "sub_experiments" / "elm_tree_nlinear"
DISJOINT_STARTS = (0, 720, 1440, 2160)

ROLLING_ANCHORS = {
    "heuristic_lag_elm_tree": 2.1706,
    "daily": 2.5491,
    "persistence": 2.5985,
}


def mae_rmse(pred: np.ndarray, actual: np.ndarray) -> tuple[float, float]:
    err = actual - pred
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))


def rolling_score(predict_at, eval_series: np.ndarray, test: np.ndarray):
    """2,161 stride-1 origins; history = all rows before the window."""
    n_origins = len(test) - HORIZON + 1
    assert n_origins == 2161, n_origins
    per_origin = np.empty((n_origins, 2), dtype=float)
    for t in range(n_origins):
        hist = eval_series[: VALIDATION_END + t]
        pred = predict_at(hist)
        assert len(pred) == HORIZON
        per_origin[t] = mae_rmse(pred, test[t : t + HORIZON])
    rolling_mae = float(np.mean(per_origin[:, 0]))
    rolling_rmse = float(np.mean(per_origin[:, 1]))
    disjoint = {
        f"window_{i + 1}": {"mae": float(per_origin[t, 0]),
                            "rmse": float(per_origin[t, 1])}
        for i, t in enumerate(DISJOINT_STARTS)
    }
    return rolling_mae, rolling_rmse, disjoint, per_origin


def main() -> int:
    fit_history, eval_series, test = get_protocol_data().rolling_views()

    # --- frozen fits -----------------------------------------------------------
    tree_kwargs = {"max_depth": 4, "min_samples_leaf": 5}
    base = HeuristicLagELMTree(hidden_dim=256, tree_kwargs=tree_kwargs)
    base.fit(fit_history, horizon=HORIZON)

    new = HeuristicLagELMTreeN(hidden_dim=256, tree_kwargs=tree_kwargs)
    new.fit(fit_history, horizon=HORIZON)

    if tuple(new.delays_) != tuple(base.delays_):
        print(f"FAIL: lag mismatch N={tuple(new.delays_)} vs base={tuple(base.delays_)}")
        return 1

    from methods import make_forecaster  # noqa: E402
    persist = make_forecaster("persistence")
    persist.fit(fit_history, horizon=HORIZON)

    def swapper(m):
        def f(hist):
            m.history_ = np.asarray(hist, dtype=float)
            return np.asarray(m.predict())
        return f

    def pers_pred(hist):
        persist.history_ = np.asarray(hist, dtype=float)
        persist.last_value_ = float(hist[-1])
        return np.asarray(persist.predict())

    def daily_pred(hist):
        return seasonal_forecast(np.asarray(hist, dtype=float), HORIZON, "daily")

    arms = {
        "heuristic_lag_elm_tree_n": swapper(new),
        "heuristic_lag_elm_tree": swapper(base),
        "daily": daily_pred,
        "persistence": pers_pred,
    }

    results = []
    t0_single = {}
    for name, predict_at in arms.items():
        t0 = time.time()
        m, r, d, _ = rolling_score(predict_at, eval_series, test)
        results.append({
            "model": name,
            "protocol": "rolling stride-1, 2161 origins, frozen fit",
            "rolling_mae": round(m, 4),
            "rolling_rmse": round(r, 4),
            "disjoint_windows": d,
            "status": "ok",
        })
        t0_single[name] = mae_rmse(predict_at(fit_history), test[:HORIZON])
        print(f"{m:>12.4f}{r:>13.4f}  {name} [{time.time() - t0:.0f}s]")

    out = {
        "slice": "S-22-elm-tree-nlinear",
        "protocol": "frozen fit on train.csv; 2,161 stride-1 origins; identical windows to every rolling-scored config",
        "lags_selected": list(new.delays_),
        "tree_config": {"max_depth": 4, "min_samples_leaf": 5, "hidden_dim": 256},
        "results": results,
        "t0_cross_check": {
            k: {"mae": round(v[0], 4), "rmse": round(v[1], 4)}
            for k, v in t0_single.items()
        },
    }
    (SWEEP_DIR / "results.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )

    # --- fail-loud anchors ----------------------------------------------------
    by_name = {r["model"]: r for r in results}
    ok = True
    for name, expected in ROLLING_ANCHORS.items():
        got = by_name[name]["rolling_mae"]
        if abs(got - expected) > 8e-4:
            print(f"FAIL anchor {name}: got {got:.4f}, expected {expected:.4f}")
            ok = False
    if not ok:
        return 1

    best = min(results, key=lambda r: r["rolling_mae"])
    print(f"best model: {best['model']} {best['rolling_mae']:.4f}/{best['rolling_rmse']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
