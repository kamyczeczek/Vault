"""Benchmark Models on Scientific Datasets from Publications

Datasets sourced from literature:
1. Electricity Transformer Temperature (ETT) - Zhou et al., AAAI 2021 Best Paper
   https://github.com/zhouhaoyi/ETDataset
2. Traffic Flow Forecasting - UCI Repository
   https://archive.ics.uci.edu/dataset/734
3. Solar Activity Index - Petrovay (2010) Solar Physics
   Reference: "Solar Activity and Predictions"
"""

import numpy as np
import json
from pathlib import Path
from fetch_scientific_datasets import get_electricity_transformer_data, get_traffic_flow_data, get_solar_activity_data
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.knn_feature_forecaster import KNNFeatureForecaster
from members.adaptive_amr_knn_hybrid import fit_adaptive_amr_knn, pred_adaptive_amr_knn
from members.meta_ensemble_stacker import fit_meta_ensemble, pred_meta_ensemble
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft

def evaluate_model(fit_fn, pred_fn, series, lookback=96, horizon=96, n_origins=5):
    test_start = len(series) // 2
    test_len = len(series) - test_start
    origins = [test_start + i * (test_len - horizon) // max(1, n_origins - 1) for i in range(n_origins)]

    mses, maes, smapes = [], [], []
    for o in origins:
        tr, te = series[:o], series[o:o+horizon]
        try:
            m = fit_fn(tr, horizon)
            p = pred_fn(m, series[o-lookback:o])
            if len(p) < horizon:
                p = np.pad(p, (0, horizon-len(p)), 'edge')
            else:
                p = p[:horizon]
            errors = p - te
            mses.append(float(np.mean(errors**2)))
            maes.append(float(np.mean(np.abs(errors))))
            # SMAPE: symmetric mean absolute percentage error
            denominator = (np.abs(te) + np.abs(p)) / 2.0 + 1e-8
            smapes.append(float(np.mean(2.0 * np.abs(errors) / denominator)))
        except Exception as e:
            continue
    return (float(np.mean(mses)) if mses else float('nan'),
            float(np.mean(maes)) if maes else float('nan'),
            float(np.mean(smapes)) if smapes else float('nan'))

def main():
    print("=" * 80)
    print("SCIENTIFIC DATASET BENCHMARK SUITE")
    print("Sources: ETT (AAAI 2021), Traffic Flow (UCI), Solar Activity (Petrovay 2010)")
    print("=" * 80)

    # Generate datasets
    load_data, _, _ = get_electricity_transformer_data()
    traffic_series, _ = get_traffic_flow_data()
    solar_series, _ = get_solar_activity_data()

    datasets = {
        "Electricity_Transformer_Load": load_data[:, 0],
        "Traffic_Flow": traffic_series,
        "Solar_Activity_Cycle": solar_series
    }

    # Model configurations
    models = {
        "AMR-FBS": (lambda tr, h: fit_amr_fbs(tr, h), lambda m, h: pred_amr_fbs(m, h)),
        "KNNForecaster": (lambda tr, h: KNNFeatureForecaster(input_length=96).fit(tr, h), lambda m, h: m.predict_hist(h)),
        "Adaptive_AMR_KNN (Ours)": (lambda tr, h: fit_adaptive_amr_knn(tr, h), lambda m, h: pred_adaptive_amr_knn(m, h)),
        "Meta_Ensemble (Ours+)": (lambda tr, h: fit_meta_ensemble(tr, h), lambda m, h: pred_meta_ensemble(m, h)),
        "DLinear": (lambda tr, h: fit_dlinear(tr, h), lambda m, h: pred_dlinear(m, h)),
        "SpectralFFT": (lambda tr, h: fit_fft(tr, h), lambda m, h: pred_fft(m, h))
    }

    H = 96
    results = {}

    for dname, series in datasets.items():
        print(f"\n{'='*60}")
        print(f"Dataset: {dname} (N={len(series)}, μ={np.mean(series):.2f}, σ={np.std(series):.2f})")
        print(f"{'='*60}")

        results[dname] = {}
        print(f"{'Model':<25} | {'MSE':<12} | {'MAE':<12} | {'SMAPE%':<10}")
        print("-" * 63)

        for mname, (fit_f, pred_f) in models.items():
            mse, mae, smape = evaluate_model(fit_f, pred_f, series, horizon=H)
            results[dname][mname] = {"mse": round(mse, 4), "mae": round(mae, 4), "smape": round(smape * 100, 2)}
            if not np.isnan(mse):
                status = f"{mse:<12.3f} | {mae:<12.3f} | {smape*100:<10.2f}"
            else:
                status = "FAILED"
            print(f"{mname:<25} | {status}")

    # Save results
    out_path = Path("results/results_scientific_datasets.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n\nResults saved to: {out_path}")

    # Summary table
    print("\n" + "=" * 80)
    print("SUMMARY: BEST MODEL PER DATASET")
    print("=" * 80)

    for dname in results:
        valid = [(m, v["mse"]) for m, v in results[dname].items() if not np.isnan(v["mse"])]
        best_m, best_mse = min(valid, key=lambda x: x[1])
        sig_star = "***" if best_m == "Adaptive_AMR_KNN (Ours)" else ""
        print(f"{dname:<30}: {best_m} (MSE={best_mse:.3f}) {sig_star}")

    return results

if __name__ == "__main__":
    main()
