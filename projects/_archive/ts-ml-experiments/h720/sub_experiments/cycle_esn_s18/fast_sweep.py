"""S-18 — Fast Vectorized Sweep & Test Evaluation for CycleESN."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods.cycle_esn import CycleESN
from methods.neural_models import NLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
VAL_END = 11425


def evaluate_rolling_batch(model: CycleESN, eval_series: np.ndarray, test_series: np.ndarray):
    L = model.input_length
    H = HORIZON
    n_origins = len(test_series) - H + 1
    base_offset = len(eval_series) - len(test_series)
    window_indices = np.arange(n_origins)[:, None] + base_offset - L + np.arange(L)
    windows = eval_series[window_indices]
    anchors = windows[:, -1:]
    windows_norm = windows - anchors

    N = model.n_reservoir
    V = model.V_[None, :]
    rc = model.rc
    states = np.zeros((n_origins, N), dtype=float)

    for k in range(L):
        u_k = windows_norm[:, k : k + 1]
        states = np.tanh(u_k * V + rc * np.roll(states, shift=1, axis=1))

    if model.linear_skip:
        features = np.hstack([windows_norm, states])
    else:
        features = states

    preds_norm = model.model_.predict(features)
    preds = preds_norm + anchors

    target_indices = np.arange(n_origins)[:, None] + np.arange(H)
    actuals = test_series[target_indices]

    errors = preds - actuals
    mae_per_origin = np.mean(np.abs(errors), axis=1)
    rmse_per_origin = np.sqrt(np.mean(errors**2, axis=1))

    overall_mae = float(np.mean(mae_per_origin))
    overall_rmse = float(np.sqrt(np.mean(errors**2)))

    disjoint = {
        f"window_{i+1}": {
            "mae": float(mae_per_origin[t]),
            "rmse": float(rmse_per_origin[t]),
        }
        for i, t in enumerate(DISJOINT_STARTS)
    }
    return overall_mae, overall_rmse, disjoint


def evaluate_val_batch(model: CycleESN, fit_history: np.ndarray) -> float:
    L = model.input_length
    H = HORIZON
    val_series = fit_history[TRAIN_END:]
    n_origins = len(val_series) - H + 1

    window_indices = np.arange(n_origins)[:, None] + TRAIN_END - L + np.arange(L)
    windows = fit_history[window_indices]
    anchors = windows[:, -1:]
    windows_norm = windows - anchors

    N = model.n_reservoir
    V = model.V_[None, :]
    rc = model.rc
    states = np.zeros((n_origins, N), dtype=float)

    for k in range(L):
        u_k = windows_norm[:, k : k + 1]
        states = np.tanh(u_k * V + rc * np.roll(states, shift=1, axis=1))

    if model.linear_skip:
        features = np.hstack([windows_norm, states])
    else:
        features = states

    preds_norm = model.model_.predict(features)
    preds = preds_norm + anchors

    target_indices = np.arange(n_origins)[:, None] + np.arange(H)
    actuals = val_series[target_indices]
    return float(np.mean(np.abs(preds - actuals)))


def run_fast_sweep():
    print("Running S-18 fast sweep synchronously...")
    pd = get_protocol_data()
    fit_history, eval_series, test = pd.rolling_views()
    train_8545 = fit_history[:TRAIN_END]

    # Baseline NLinear val MAE
    nl_val = NLinear(input_length=336, ridge_alpha=1.0).fit(train_8545, horizon=HORIZON)
    val_series = fit_history[TRAIN_END:]
    n_origins = len(val_series) - HORIZON + 1
    w_idx = np.arange(n_origins)[:, None] + TRAIN_END - 336 + np.arange(336)
    w_nl = fit_history[w_idx]
    anc_nl = w_nl[:, -1:]
    p_nl = nl_val.model.predict(w_nl - anc_nl) + anc_nl
    t_idx = np.arange(n_origins)[:, None] + np.arange(HORIZON)
    act_val = val_series[t_idx]
    nl_val_mae = float(np.mean(np.abs(p_nl - act_val)))
    print(f"NLinear L336 baseline Val MAE: {nl_val_mae:.4f}")

    # Focused grid: L=336, N in [32, 64], rc in [0.9, 0.95, 0.99], v in [0.01, 0.05, 0.1], skip=[True], alpha=[1.0, 10.0]
    grid = []
    for N in [32, 64]:
        for rc in [0.9, 0.95, 0.99]:
            for v in [0.01, 0.05, 0.1]:
                for alpha in [1.0, 10.0]:
                    grid.append({"L": 336, "N": N, "rc": rc, "v": v, "skip": True, "alpha": alpha})

    print(f"Running focused grid ({len(grid)} configs)...")
    results = []
    t0 = time.time()
    for i, cfg in enumerate(grid):
        m = CycleESN(
            input_length=cfg["L"],
            n_reservoir=cfg["N"],
            rc=cfg["rc"],
            v=cfg["v"],
            linear_skip=cfg["skip"],
            ridge_alpha=cfg["alpha"]
        )
        m.fit(train_8545, horizon=HORIZON)
        val_mae = evaluate_val_batch(m, fit_history)
        delta = val_mae - nl_val_mae
        results.append({**cfg, "val_mae": round(val_mae, 4), "delta_vs_nl": round(delta, 4)})
        if (i+1) % 10 == 0 or delta < -0.01:
            print(f"[{i+1}/{len(grid)}] N{cfg['N']} rc{cfg['rc']} v{cfg['v']} a{cfg['alpha']} | Val: {val_mae:.4f} (delta: {delta:+.4f})")

    results.sort(key=lambda x: x["val_mae"])
    best = results[0]
    print(f"\nWinner: {best} in {time.time()-t0:.2f}s")

    # Freeze best on full fit_history (11425) and score on test
    print("Freezing best on full 11,425 history and scoring on test...")
    frozen = CycleESN(
        input_length=best["L"],
        n_reservoir=best["N"],
        rc=best["rc"],
        v=best["v"],
        linear_skip=best["skip"],
        ridge_alpha=best["alpha"]
    )
    frozen.fit(fit_history, horizon=HORIZON)
    test_mae, test_rmse, disjoint = evaluate_rolling_batch(frozen, eval_series, test)
    print(f"Test Rolling MAE: {test_mae:.4f}, RMSE: {test_rmse:.4f}")

    out = HERE / "results_s18.json"
    out.write_text(json.dumps({
        "slice": "S-18",
        "best_config": best,
        "test_results": {
            "rolling_mae": round(test_mae, 4),
            "rolling_rmse": round(test_rmse, 4),
            "disjoint_windows": disjoint,
            "delta_vs_nlinear": round(test_mae - 2.0571, 4),
            "delta_vs_ensemble": round(test_mae - 2.0519, 4)
        },
        "top_validation": results[:5]
    }, indent=2), encoding="utf-8")
    print(f"Saved to {out}")


if __name__ == "__main__":
    run_fast_sweep()
