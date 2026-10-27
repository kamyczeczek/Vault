from __future__ import annotations
import numpy as np
import json
import time
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from members.lasso_lag_mutation import LassoLagHybrid
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.state_space_hybrid import StateSpaceDictionaryHybrid
from members.sota_baselines import fit_dlinear, pred_dlinear
from bench import TASKS, get_series

def run_lasso_benchmark():
    print("=== Running LassoLagHybrid on Scientific Benchmark Suite ===")
    selected_tasks = ["thomas_H24", "sunspot_H24", "etth1_H96", "multiscale_H96", "seasonal_H48"]

    models = {
        "LassoLagHybrid": (lambda tr, h: LassoLagHybrid(input_length=96).fit(tr, h), lambda m, h, hist: m.predict(hist, h)),
        "AMR-FBS": (lambda tr, h: fit_amr_fbs(tr, h), lambda m, h, hist: pred_amr_fbs(m, h)[:h]),
        "StateSpaceHybrid": (lambda tr, h: StateSpaceDictionaryHybrid(input_length=96).fit(tr, h), lambda m, h, hist: m.predict(hist, h)),
        "DLinear": (lambda tr, h: fit_dlinear(tr, h), lambda m, h, hist: pred_dlinear(m, hist)[:h]),
    }

    results = {}

    for task_name, H, domain in TASKS:
        if task_name not in selected_tasks:
            continue

        print(f"\n--- Task: {task_name} (H={H}) ---")
        series = get_series(task_name)
        train = series[:-H]
        test = series[-H:]

        task_res = {}
        for name, (fit_fn, pred_fn) in models.items():
            t0 = time.time()
            try:
                model = fit_fn(train, H)
                pred = pred_fn(model, H, train[-96:])
                pred = np.asarray(pred, dtype=float).ravel()[:H]
                mae = float(np.mean(np.abs(pred - test)))
                dt = time.time() - t0
                task_res[name] = {"MAE": mae, "time": dt}
                print(f"  {name:18s} : MAE {mae:.4f} ({dt:.2f}s)")
            except Exception as e:
                print(f"  {name:18s} : ERROR ({e})")
                task_res[name] = {"MAE": None, "error": str(e)}

        results[task_name] = {"H": H, "domain": domain, "models": task_res}

    with open("results_lasso_scientific.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved Lasso scientific benchmark results to results_lasso_scientific.json")

if __name__ == "__main__":
    run_lasso_benchmark()
