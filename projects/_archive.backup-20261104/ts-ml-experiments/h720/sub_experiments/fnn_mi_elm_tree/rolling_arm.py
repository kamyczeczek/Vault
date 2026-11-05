"""S-09 rolling arm: MI+FNN configs under the canonical rolling protocol.

Companion to ``run_sweep.py`` (user-designed, t=0 single-origin
protocol, results.json). The S-09 contract additionally requires
ROLLING numbers for this experiment's families, so this runner
scores them under the canonical protocol (frozen fit on train.csv,
2,161 stride-1 origins across the full test region; per-origin
history = all rows strictly before the scored window — the same
windows as every rolling-scored config in the leaderboard):

- ``tree_best``            — winning tree config from results.json
  (re-fit here; select_lags is deterministic, must reproduce the
  user's (14,28,42,56,70) — asserted fail-loud),
- ``ridge_same_lags``      — ridge readout, identical MI+FNN lags
  (readout-isolation arm vs tree_best),
- ``ridge_fastlags_h256``  — ridge readout on the legacy fast lags
  (lag-set isolation arm vs ridge_same_lags),
- ``elm_h64_full_fastlags``— canonical ELM parent (S-01/S-08 arm,
  rolling 2.3092 — like-for-like competitor, hidden_dim/hist differ),
- ``daily`` / ``persistence`` — fail-loud anchors (2.5491 / 2.5985).

Fail-loud anchors (rolling MAE, 4-decimal, from the leaderboard):
elm_h64_full_fastlags 2.3092 / daily 2.5491 / persistence 2.5985.
Cross-protocol check: the t=0 window of tree_best / both ridges must
reproduce the user's single-origin results.json numbers exactly.

Construction pattern mirrors cross_family_ensemble/run_sweep.py (S-08):
frozen fit, then per-origin ``history_`` swap + ``predict()``.

Run: python sub_experiments/fnn_mi_elm_tree/rolling_arm.py
(written as part of slice S-09; run_sweep.py is the user's design.)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, VALIDATION_END, get_protocol_data  # noqa: E402
from methods.baselines import seasonal_forecast  # noqa: E402
from methods.neural_models import HeuristicLagELM, HeuristicLagELMTree  # noqa: E402

SWEEP_DIR = H720_ROOT / "sub_experiments" / "fnn_mi_elm_tree"
DISJOINT_STARTS = (0, 720, 1440, 2160)

ROLLING_ANCHORS = {  # canonical rolling leaderboard (4-decimal)
    "elm_h64_full_fastlags": 2.3092,
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

    # --- pull the winning tree config from the user's t=0 run -----------
    res_path = SWEEP_DIR / "results.json"
    if not res_path.exists():
        print("run_sweep.py results.json missing — run it first")
        return 1
    t0_run = json.loads(res_path.read_text(encoding="utf-8"))
    lags = tuple(int(d) for d in t0_run["lags_selected"])
    tree_grid = [r for r in t0_run["results"]
                 if r["model"].startswith("tree")
                 and not r["model"].startswith("tree_best")]
    best_grid = min(tree_grid, key=lambda r: r["mae"])
    tree_kwargs = best_grid["params"]["tree_kwargs"]
    all_tree = [r for r in t0_run["results"] if r["model"].startswith("tree")]
    overall = min(all_tree, key=lambda r: r["mae"])
    if overall["model"].startswith("tree_best_h"):
        best_hdim = int(overall["model"].rsplit("h", 1)[1])
    else:
        best_hdim = 256  # grid rows ran at the default hidden_dim=256
    print(f"selected lags: {lags}")
    print(f"tree_best -> {overall['model']} (t=0 MAE {overall['mae']:.4f}), "
          f"tree_kwargs {tree_kwargs}, hidden_dim {best_hdim}")

    # --- frozen fits on train.csv ---------------------------------------
    tree_m = HeuristicLagELMTree(hidden_dim=best_hdim, tree_kwargs=tree_kwargs)
    tree_m.fit(fit_history, horizon=HORIZON)
    if tuple(tree_m.delays_) != lags:  # determinism cross-check
        print(f"FAIL: tree select_lags {tuple(tree_m.delays_)} != "
              f"run_sweep {lags}")
        return 1
    ridge_mi = HeuristicLagELM(delays=lags, hidden_dim=256)
    ridge_mi.fit(fit_history, horizon=HORIZON)
    ridge_fast = HeuristicLagELM(delays=(1, 2, 3, 6, 12), hidden_dim=256)
    ridge_fast.fit(fit_history, horizon=HORIZON)
    parent = HeuristicLagELM(
        hidden_dim=64, history_fraction=1.0, delays=(1, 2, 3, 6, 12)
    )
    parent.fit(fit_history, horizon=HORIZON)
    from methods import make_forecaster  # noqa: E402
    persist = make_forecaster("persistence")
    persist.fit(fit_history, horizon=HORIZON)

    def swapper(m):
        def f(hist):
            m.history_ = np.asarray(hist, dtype=float)
            return np.asarray(m.predict())
        return f

    def pers_pred(hist):  # predict() reads last_value_, not history_
        persist.history_ = np.asarray(hist, dtype=float)
        persist.last_value_ = float(hist[-1])
        return np.asarray(persist.predict())

    def daily_pred(hist):
        return seasonal_forecast(np.asarray(hist, dtype=float),
                                 HORIZON, "daily")

    arms = {
        "tree_best": swapper(tree_m),
        "ridge_same_lags": swapper(ridge_mi),
        "ridge_fastlags_h256": swapper(ridge_fast),
        "elm_h64_full_fastlags": swapper(parent),
        "daily": daily_pred,
        "persistence": pers_pred,
    }

    # --- rolling + t=0 windows ------------------------------------------
    results, t0_single = [], {}
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

    # --- grid rolling: top-6 distinct t=0 tree configs -------------------
    # (kills the "you only rolled the winner" objection; distinct by
    # (tree_kwargs, hidden_dim), skips the already-scored winner)
    seen = {(tuple(sorted(tree_kwargs.items())), best_hdim)}
    grid_rows = sorted(
        (r for r in all_tree), key=lambda r: r["mae"]
    )
    for row in grid_rows:
        kw = row["params"].get("tree_kwargs")
        if kw is None:  # hdim sweep rows carry hidden_dim + tree_kwargs
            continue
        hd = row["params"].get("hidden_dim", 256)
        key = (tuple(sorted(kw.items())), hd)
        if key in seen:
            continue
        seen.add(key)
        if len(seen) > 6:
            break
        m = HeuristicLagELMTree(hidden_dim=hd, tree_kwargs=kw)
        m.fit(fit_history, horizon=HORIZON)
        assert tuple(m.delays_) == lags
        f = swapper(m)
        t0 = time.time()
        mae, rmse, dw, _ = rolling_score(f, eval_series, test)
        results.append({
            "model": f"grid_{row['model']}",
            "protocol": "rolling stride-1, 2161 origins, frozen fit",
            "rolling_mae": round(mae, 4),
            "rolling_rmse": round(rmse, 4),
            "disjoint_windows": dw,
            "status": "ok",
        })
        print(f"{mae:>12.4f}{rmse:>13.4f}  grid_{row['model']} "
              f"[{time.time() - t0:.0f}s]")

    out = {
        "slice": "S-09-rolling",
        "protocol": "frozen fit on train.csv; 2,161 stride-1 origins; "
                    "identical windows to every rolling-scored config",
        "lags_selected": list(lags),
        "tree_config": {"t0_model": overall["model"],
                        "grid_row": best_grid["model"],
                        "tree_kwargs": tree_kwargs,
                        "hidden_dim": best_hdim},
        "results": results,
        "t0_cross_check": {
            k: {"mae": round(v[0], 4), "rmse": round(v[1], 4)}
            for k, v in t0_single.items()
        },
    }
    (SWEEP_DIR / "results_rolling.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )

    # --- fail-loud anchors (rolling) -------------------------------------
    by_name = {r["model"]: r for r in results}
    failures = []
    for name, expected in ROLLING_ANCHORS.items():
        got = by_name[name]["rolling_mae"]
        ok = abs(got - expected) < 5e-5
        print(f"anchor {name}: {got:.4f} expected {expected:.4f} -> "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(name)

    # t=0 cross-check vs the user's single-origin numbers
    t0_user = {r["model"]: r["mae"] for r in t0_run["results"]}
    cross = {
        "tree_best": min(t0_user[k] for k in t0_user if k.startswith("tree")),
        "ridge_same_lags": t0_user.get("ridge_ref_same_lags"),
        "ridge_fastlags_h256": t0_user.get("ridge_ref_fastlags"),
    }
    for name, expected in cross.items():
        got = t0_single[name][0]
        ok = expected is not None and abs(got - expected) < 5e-5
        print(f"t=0 cross {name}: {got:.4f} vs single-origin "
              f"{expected if expected is not None else 'MISSING'} -> "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"t0:{name}")

    if failures:
        print(f"\nANCHOR CHECK FAILED: {failures} — results_rolling.json "
              "MUST NOT be trusted")
        return 1
    print(f"\nWrote {SWEEP_DIR / 'results_rolling.json'} — all anchors OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
