"""Benchmark Adaptive AMR-KNN Hybrid against standalone AMR-FBS, KNNForecaster, and Baselines."""

import numpy as np
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "_archive/datasets"))
from new_datasets_catalog import generate_all_datasets
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.knn_feature_forecaster import KNNFeatureForecaster
from members.adaptive_amr_knn_hybrid import fit_adaptive_amr_knn, pred_adaptive_amr_knn
from members.sota_baselines import fit_dlinear, pred_dlinear

def evaluate_model(fit_fn, pred_fn, series, lookback=96, horizon=96, n_origins=5):
    test_start = len(series) // 2
    test_len = len(series) - test_start
    origins = [test_start + i * (test_len - horizon) // (n_origins - 1) for i in range(n_origins)]

    mses = []
    maes = []
    for o in origins:
        tr = series[:o]
        te = series[o : o + horizon]
        m = fit_fn(tr, horizon)
        p = pred_fn(m, series[o - lookback : o])
        if len(p) < horizon:
            p = np.pad(p, (0, horizon - len(p)), 'edge')
        else:
            p = p[:horizon]
        mses.append(float(np.mean((p - te) ** 2)))
        maes.append(float(np.mean(np.abs(p - te))))
    return float(np.mean(mses)), float(np.mean(maes))

def run_adaptive_eval():
    datasets = generate_all_datasets()
    H = 96
    lookback = 96

    models = {
        "AMR-FBS": (lambda tr, h: fit_amr_fbs(tr, h), lambda m, hist: pred_amr_fbs(m, hist)),
        "KNNForecaster": (lambda tr, h: KNNFeatureForecaster(input_length=lookback).fit(tr, h), lambda m, hist: m.predict_hist(hist)),
        "Adaptive_AMR_KNN (Ours)": (lambda tr, h: fit_adaptive_amr_knn(tr, h, blend_mode="adaptive"), lambda m, hist: pred_adaptive_amr_knn(m, hist)),
        "DLinear": (lambda tr, h: fit_dlinear(tr, h), lambda m, hist: pred_dlinear(m, hist))
    }

    results = {}
    print(f"{'Dataset':<22} | {'AMR-FBS MSE':<12} | {'KNN MSE':<12} | {'Adaptive Hybrid':<15} | {'DLinear':<12}")
    print("-" * 80)
    for dname, series in datasets.items():
        results[dname] = {}
        row_str = f"{dname:<22} | "
        for mname, (fit_f, pred_f) in models.items():
            mse, mae = evaluate_model(fit_f, pred_f, series, lookback=lookback, horizon=H)
            results[dname][mname] = {"mse": round(mse, 3), "mae": round(mae, 3)}
            row_str += f"{mse:<12.2f} | "
        print(row_str)

    with open("results/results_adaptive_hybrid.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved evaluation to results/results_adaptive_hybrid.json")

if __name__ == "__main__":
    run_adaptive_eval()
