"""S-18 — Validation-gated sweep for CycleESN (SCR + NLinear linear skip + Ridge).

Protocol (S-02 / S-16c):
- Train 8,545 / Val 2,880 split.
- Sweep parameters over validation rolling (2,161 origins):
  - n_reservoir: {32, 64, 128}
  - rc (spectral radius / cycle weight): {0.7, 0.9, 0.99}
  - v (input scale): {0.01, 0.1, 0.5}
  - linear_skip: {True, False}
- Fast selection: fit on train 8,545, roll on val 2,880.
- Compare with pure NLinear on val (2.8970).
- If best beats pure NLinear on val, freeze and score on test (2,161 origins).
"""

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

TRAIN_END = 8545
DISJOINT_STARTS = (0, 720, 1440, 2160)

def mae_rmse(p: np.ndarray, a: np.ndarray) -> tuple[float, float]:
    err = np.asarray(p, float) - np.asarray(a, float)
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))

def roll_model(model, series: np.ndarray, val_start: int, n_origins: int) -> np.ndarray:
    """Fast rolling evaluation using vectorized single-predict calls."""
    preds = []
    for t in range(n_origins):
        hist = series[:val_start + t]
        model.history_ = hist[:, None] if hist.ndim == 1 else hist
        pred = model.predict()
        preds.append(pred)
    return np.asarray(preds)

def main():
    pd = get_protocol_data()
    fit_history, eval_series, test = pd.rolling_views()
    train_8545 = fit_history[:TRAIN_END]
    val = fit_history[TRAIN_END:]

    n_val_origins = len(val) - HORIZON + 1 # 2161
    A_val = np.empty((n_val_origins, HORIZON))
    for t in range(n_val_origins):
        A_val[t] = val[t:t + HORIZON]

    print(f"Data loaded: train {len(train_8545)}, val {len(val)}, test {len(test)}")

    # 1. Baseline NLinear on val
    print("\n--- Fitting NLinear L336 on train 8545 ---")
    nl = NLinear(input_length=336, ridge_alpha=1.0)
    nl.fit(train_8545, horizon=HORIZON)
    P_nl_val = roll_model(nl, fit_history, TRAIN_END, n_val_origins)
    nl_val_mae = float(np.mean(np.abs(P_nl_val - A_val)))
    print(f"NLinear L336 Val MAE: {nl_val_mae:.4f}")

    # 2. Grid of CycleESN configurations
    configs = []
    for skip in [True, False]:
        for n_res in [32, 64, 128]:
            for rc in [0.7, 0.9, 0.99]:
                for v in [0.01, 0.1, 0.5]:
                    configs.append({
                        "input_length": 336,
                        "n_reservoir": n_res,
                        "rc": rc,
                        "v": v,
                        "linear_skip": skip,
                        "ridge_alpha": 1.0,
                    })

    print(f"\n--- Running Validation Grid ({len(configs)} configs) ---")
    results = []
    t_start = time.time()

    for i, cfg in enumerate(configs):
        t0 = time.time()
        model = CycleESN(**cfg)
        model.fit(train_8545, horizon=HORIZON)
        P_val = roll_model(model, fit_history, TRAIN_END, n_val_origins)
        val_mae = float(np.mean(np.abs(P_val - A_val)))
        elapsed = time.time() - t0

        cfg_name = f"N{cfg['n_reservoir']}_rc{cfg['rc']}_v{cfg['v']}_skip{cfg['linear_skip']}"
        results.append({
            "name": cfg_name,
            "config": cfg,
            "val_mae": round(val_mae, 4),
            "delta_vs_nlinear": round(val_mae - nl_val_mae, 4),
            "fit_time": round(elapsed, 2)
        })
        print(f"[{i+1}/{len(configs)}] {cfg_name:30s} | Val MAE: {val_mae:.4f} | delta: {val_mae - nl_val_mae:+.4f} | {elapsed:.1f}s")

    # Sort by Val MAE
    results.sort(key=lambda r: r["val_mae"])
    best = results[0]
    print(f"\n=== Top 5 Configurations on Validation ===")
    for r in results[:5]:
        print(f"  {r['name']:30s} | Val MAE: {r['val_mae']:.4f} (delta: {r['delta_vs_nlinear']:+.4f})")

    print(f"\nTotal sweep time: {time.time() - t_start:.1f}s")

    # 3. Freeze best on full train 11425 and evaluate on test rolling
    print(f"\n--- Evaluating Best Config ({best['name']}) on Test Rolling ---")
    best_cfg = best["config"]
    final_model = CycleESN(**best_cfg)
    final_model.fit(fit_history, horizon=HORIZON)

    n_test_origins = len(test) - HORIZON + 1 # 2161
    P_test = roll_model(final_model, eval_series, len(fit_history), n_test_origins)

    per_origin_test = np.empty((n_test_origins, 2), float)
    for t in range(n_test_origins):
        actual = test[t:t + HORIZON]
        per_origin_test[t] = mae_rmse(P_test[t], actual)

    test_mae = float(np.mean(per_origin_test[:, 0]))
    test_rmse = float(np.mean(per_origin_test[:, 1]))

    disjoint = {
        f"window_{w+1}": {
            "mae": float(per_origin_test[idx, 0]),
            "rmse": float(per_origin_test[idx, 1]),
        }
        for w, idx in enumerate(DISJOINT_STARTS)
    }

    print(f"Best CycleESN Test Rolling MAE: {test_mae:.4f} / RMSE: {test_rmse:.4f}")
    print(f"W4 MAE: {disjoint['window_4']['mae']:.4f}")
    print(f"NLinear L336 Reference Test MAE: 2.0571 / RMSE: 2.5071")
    print(f"Delta vs NLinear L336: {test_mae - 2.0571:+.4f}")

    out_file = HERE / "results_s18.json"
    out_file.write_text(json.dumps({
        "slice": "S-18",
        "description": "CycleESN (Simple Cycle Reservoir + NLinear skip + Ridge) parameter sweep and evaluation",
        "baseline_nlinear_val_mae": round(nl_val_mae, 4),
        "best_config": best,
        "top_10_validation": results[:10],
        "test_results": {
            "rolling_mae": round(test_mae, 4),
            "rolling_rmse": round(test_rmse, 4),
            "disjoint_windows": disjoint,
            "delta_vs_nlinear": round(test_mae - 2.0571, 4),
        },
        "all_sweep_results": results
    }, indent=2), encoding="utf-8")
    print(f"Saved results to {out_file}")

if __name__ == "__main__":
    main()
