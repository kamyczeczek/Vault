"""Extended Benchmark Suite: New Domain Datasets

Evaluates benchmark-core models across 6 new synthetic domains:
- Energy/Electricity (hourly consumption)
- Traffic Flow (rush hour patterns)
- Financial Markets (volatility clustering)
- Weather/Climate (annual cycles)
- Web Traffic (irregular spikes)
- Healthcare/Biomedical (vital signs)

Protocol: L=96, H ∈ {96, 192, 336, 720}, MSE/MAE, 5 rolling origins
"""

import numpy as np
import json
import pathlib
import sys
import time
from typing import Dict, List

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "_archive/datasets"))

# Import dataset generators
from new_datasets_catalog import generate_all_datasets

# Import forecasting models
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.state_space_hybrid import fit_state_space_hybrid, pred_state_space_hybrid
from members.knn_feature_forecaster import KNNFeatureForecaster
from members.big_dict_elm import BigDictELM
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft, fit_theta, pred_theta

def evaluate_model_on_dataset(
    model_name: str,
    fit_fn,
    pred_fn,
    series: np.ndarray,
    lookback: int = 96,
    horizon: int = 96,
    n_origins: int = 5
) -> Dict[str, float]:
    """Evaluate single model on dataset with rolling origins."""
    results = {
        "mse_list": [],
        "mae_list": []
    }

    test_start = len(series) // 2  # Start evaluation at midpoint
    test_len = len(series) - test_start

    origins = [test_start + i * (test_len - horizon) // (n_origins - 1)
               for i in range(n_origins)]

    for origin_idx, origin in enumerate(origins):
        try:
            train_data = series[:origin]
            test_actuals = series[origin:origin + horizon]

            if len(train_data) < lookback + 10:
                continue

            model = fit_fn(train_data, horizon)
            preds = pred_fn(model, series[origin-lookback:origin])

            if len(preds) < horizon:
                preds = np.pad(preds, (0, horizon - len(preds)), 'edge')
            else:
                preds = preds[:horizon]

            mse = float(np.mean((preds - test_actuals) ** 2))
            mae = float(np.mean(np.abs(preds - test_actuals)))

            results["mse_list"].append(mse)
            results["mae_list"].append(mae)

        except Exception as e:
            if origin_idx == 0:
                print(f"    Error at origin 0 for {model_name}: {e}")
            continue

    # Average across origins
    result = {
        "mse": float(np.mean(results["mse_list"])) if results["mse_list"] else float('nan'),
        "mae": float(np.mean(results["mae_list"])) if results["mae_list"] else float('nan'),
        "n_origins_evaluated": len(results["mse_list"])
    }

    return result

def run_extended_benchmark():
    print("=" * 90)
    print("   EXTENDED BENCHMARK SUITE: NEW DOMAIN DATASETS")
    print("   Protocol: Lookback L=96 | Horizons H ∈ {96, 192, 336, 720}")
    print("   Metrics: MSE & MAE averaged over 5 rolling origins")
    print("=" * 90)

    datasets = generate_all_datasets()
    horizons = [96, 192, 336, 720]
    lookback = 96

    all_results = {}

    # Model configurations (all use same L=96 lookback)
    model_configs = [
        ("AMR-FBS", lambda tr, h: fit_amr_fbs(tr, h),
         lambda m, hist: pred_amr_fbs(m, hist)),
        ("StateSpaceHybrid", lambda tr, h: fit_state_space_hybrid(tr, h),
         lambda m, hist: pred_state_space_hybrid(m, hist)),
        ("KNNForecaster", lambda tr, h: KNNFeatureForecaster(input_length=lookback).fit(tr, h),
         lambda m, hist: m.predict_hist(hist)),
        ("BigDictELM", lambda tr, h: BigDictELM(input_length=lookback).fit(tr, horizon=h),
         lambda m, hist: m.predict_hist(hist)),
        ("DLinear", lambda tr, h: fit_dlinear(tr, h),
         lambda m, hist: pred_dlinear(m, hist)),
        ("SpectralFFT", lambda tr, h: fit_fft(tr, h),
         lambda m, hist: pred_fft(m, hist)),
        ("Theta", lambda tr, h: fit_theta(tr, h),
         lambda m, hist: pred_theta(m, hist)),
    ]

    for dname, series in datasets.items():
        print(f"\n{'='*60}")
        print(f"Dataset: {dname} (N={len(series)}, mean={np.mean(series):.2f}, std={np.std(series):.2f})")
        print(f"{'='*60}")

        all_results[dname] = {}

        for H in horizons:
            all_results[dname][f"H_{H}"] = {}
            print(f"\n  Horizon H = {H}:")

            for model_name, fit_fn, pred_fn in model_configs:
                try:
                    result = evaluate_model_on_dataset(
                        model_name, fit_fn, pred_fn, series,
                        lookback=lookback, horizon=H, n_origins=5
                    )

                    all_results[dname][f"H_{H}"][model_name] = {
                        "mse": round(result["mse"], 4),
                        "mae": round(result["mae"], 4)
                    }

                    status = f"MSE={result['mse']:.3f} MAE={result['mae']:.3f}" if not np.isnan(result['mse']) else "FAILED"
                    print(f"    {model_name:20s}: {status}")

                except Exception as e:
                    all_results[dname][f"H_{H}"][model_name] = {"mse": float('nan'), "mae": float('nan')}
                    print(f"    {model_name:20s}: ERROR - {e}")

    # Save results
    output_path = HERE / "results" / "results_extended_benchmark.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\n\nResults saved to: {output_path}")

    # Print summary table
    print("\n" + "=" * 90)
    print("SUMMARY TABLE: All Models × All Datasets (MSE values)")
    print("=" * 90)

    headers = ["Model \\ Dataset"] + list(datasets.keys())
    print("  ".join(f"{h:>12s}" for h in headers))
    print("-" * 120)

    for model_name, _, _ in model_configs:
        row = [model_name]
        for dname in datasets.keys():
            mse_val = all_results[dname]["H_96"].get(model_name, {}).get("mse", float('nan'))
            if np.isnan(mse_val):
                row.append("      N/A")
            else:
                row.append(f"{mse_val:>10.2f}")
        print("  ".join(row))

    return all_results

if __name__ == "__main__":
    run_extended_benchmark()
