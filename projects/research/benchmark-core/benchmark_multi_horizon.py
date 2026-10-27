"""Multi-Horizon Benchmark Following LTSF Protocol (Zhou et al., AAAI 2021)

Evaluates models across multiple forecast horizons: H ∈ {96, 192, 336, 720}
This is the canonical protocol from the Long-Term Series Forecasting literature.
"""

import sys
import numpy as np
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
# The dataset providers live in the sibling project that owns acquisition.
sys.path.insert(0, str(HERE.parent.parent / "_archive/datasets"))
from fetch_scientific_datasets import (
    get_electricity_transformer_data,
    get_traffic_flow_data,
    get_solar_activity_data,
)
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.knn_feature_forecaster import KNNFeatureForecaster
from members.adaptive_amr_knn_hybrid import fit_adaptive_amr_knn, pred_adaptive_amr_knn
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft


def evaluate_single(fit_fn, pred_fn, series, lookback=96, horizon=96, n_origins=5):
    """Run model with rolling origin evaluation."""
    test_start = len(series) // 2
    test_len = len(series) - test_start
    origins = [
        test_start + i * (test_len - horizon) // max(1, n_origins - 1)
        for i in range(n_origins)
    ]

    mses, maes, smapes = [], [], []
    for o in origins:
        tr = series[:o]
        hist = series[max(0, o - lookback):o]
        te = series[o:o + horizon]
        if len(tr) < lookback or len(te) < horizon:
            continue
        try:
            params = fit_fn(tr, horizon)
            preds = pred_fn(params, hist)
            preds = np.asarray(preds).reshape(-1)[:horizon]
            actual = np.asarray(te[:len(preds)])
            errors = preds - actual
            mses.append(float(np.mean(errors ** 2)))
            maes.append(float(np.mean(np.abs(errors))))
            # SMAPE
            denominator = (np.abs(actual) + np.abs(preds)) / 2.0 + 1e-8
            smapes.append(float(np.mean(2.0 * np.abs(errors) / denominator)))
        except Exception as e:
            pass
    return (float(np.mean(mses)) if mses else float('nan'),
            float(np.mean(maes)) if maes else float('nan'),
            float(np.mean(smapes)) if smapes else float('nan'))


def main():
    print("=" * 80)
    print("MULTI-HORIZON BENCHMARK (LTSF Protocol)")
    print("Horizons: H ∈ {96, 192, 336, 720}")
    print("=" * 80)

    # Load datasets
    load_data, _, _ = get_electricity_transformer_data()
    traffic_series, _ = get_traffic_flow_data()
    solar_series, _ = get_solar_activity_data()

    datasets = {
        "Electricity_Transformer_Load": load_data[:, 0],
        "Traffic_Flow": traffic_series,
        "Solar_Activity_Cycle": solar_series
    }

    # Model specs
    horizon_defaults = {
        "AMR-FBS": {"input_length": None},
        "KNNForecaster": {"input_length": 96},
        "Adaptive_AMR_KNN (Ours)": {"input_length": None},
        "DLinear": {"input_length": None},
        "SpectralFFT": {"input_length": None},
    }

    horizons = [96, 192, 336, 720]
    results = {}

    for dname, series in datasets.items():
        n = len(series)
        print(f"\n{'='*80}")
        print(f"Dataset: {dname} (N={n}, μ={series.mean():.2f}, σ={series.std():.2f})")
        print(f"{'='*80}")

        results[dname] = {}

        for H in horizons:
            print(f"\n--- Horizon H={H} ---")
            results[dname][str(H)] = {}

            # Model configurations with adaptive input lengths
            models = {
                "AMR-FBS": (lambda tr, h: fit_amr_fbs(tr, h), lambda m, h: pred_amr_fbs(m, h)),
                "KNNForecaster": (lambda tr, h: KNNFeatureForecaster(input_length=min(96, h)).fit(tr, h),
                                  lambda m, h: m.predict_hist(h)),
                "Adaptive_AMR_KNN (Ours)": (lambda tr, h: fit_adaptive_amr_knn(tr, h),
                                            lambda m, h: pred_adaptive_amr_knn(m, h)),
                "DLinear": (lambda tr, h: fit_dlinear(tr, h), lambda m, h: pred_dlinear(m, h)),
                "SpectralFFT": (lambda tr, h: fit_fft(tr, h), lambda m, h: pred_fft(m, h)),
            }

            print(f"{'Model':<25} | {'MSE':<12} | {'MAE':<12} | {'SMAPE%':<10}")
            print("-" * 63)

            for mname, (fit_f, pred_f) in models.items():
                try:
                    mse, mae, smape = evaluate_single(fit_f, pred_f, series, horizon=H)
                    results[dname][str(H)][mname] = {
                        "mse": round(mse, 4) if not np.isnan(mse) else "NaN",
                        "mae": round(mae, 4) if not np.isnan(mae) else "NaN",
                        "smape": round(smape * 100, 2) if not np.isnan(smape) else "NaN",
                    }
                    status = f"{mse:<12.3f} | {mae:<12.3f} | {smape*100:<10.2f}" if not np.isnan(mse) else "FAILED"
                    print(f"{mname:<25} | {status}")
                except Exception as e:
                    print(f"{mname:<25} | ERROR: {e}")
                    results[dname][str(H)][mname] = {"error": str(e)}

        # Compute win rates for this dataset
        print(f"\nWin Rates for {dname}:")
        win_counts = {name: 0 for name in models.keys()}
        for H in horizons:
            H_str = str(H)
            if H_str in results[dname]:
                best_m, best_mse = None, float('inf')
                for mname, metrics in results[dname][H_str].items():
                    if isinstance(metrics, dict) and "mse" in metrics and metrics["mse"] != "NaN":
                        if metrics["mse"] < best_mse:
                            best_mse = metrics["mse"]
                            best_m = mname
                if best_m:
                    win_counts[best_m] += 1

        for mname, count in win_counts.items():
            pct = count / len(horizons) * 100
            print(f"  {mname:<25}: {count}/{len(horizons)} ({pct:.0f}%)")

    # Save comprehensive results
    out_path = Path("results/results_multi_horizon.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n\nResults saved to: {out_path}")

    # Generate summary table
    print("\n" + "=" * 80)
    print("SUMMARY TABLE: WIN RATES ACROSS HORIZONS")
    print("=" * 80)

    all_models = set()
    for dname in results:
        for H in horizons:
            if str(H) in results[dname]:
                for mname in results[dname][str(H)]:
                    if isinstance(results[dname][str(H)][mname], dict):
                        all_models.add(mname)

    print(f"\n{'Model':<25}", end="")
    for H in horizons:
        print(f" | H={H:<4}", end="")
    print(" | Avg MSE")
    print("-" * 95)

    for mname in sorted(all_models):
        print(f"{mname:<25}", end="")
        mse_values = []
        for H in horizons:
            H_str = str(H)
            if H_str in results:
                for dname in results:
                    if H_str in results[dname] and mname in results[dname][H_str]:
                        if isinstance(results[dname][H_str][mname], dict):
                            mse = results[dname][H_str][mname].get("mse", float('nan'))
                            if isinstance(mse, (int, float)):
                                mse_values.append(mse)
        avg_mse = np.mean(mse_values) if mse_values else float('nan')
        print(f" | {avg_mse:<10.2f}", end="")
        print()

    return results


if __name__ == "__main__":
    main()
