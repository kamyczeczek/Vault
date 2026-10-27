"""Extended Benchmark Analysis & Visualization

Analyzes results from 6 new domain datasets across 7 forecasting models.
Generates summary tables, best-model identification, and publication plots.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def load_and_analyze():
    results_path = Path("results/results_extended_benchmark.json")
    with open(results_path, "r") as f:
        data = json.load(f)

    datasets = ["Electricity_Hourly", "Traffic_Flow", "Financial_Returns",
                "Weather_Temperature", "Web_Traffic", "Healthcare_Vitals"]
    horizons = [96, 192, 336, 720]
    models = ["AMR-FBS", "StateSpaceHybrid", "KNNForecaster", "BigDictELM",
              "DLinear", "SpectralFFT", "Theta"]

    # Build summary matrices
    mse_matrix = {d: {} for d in datasets}
    mae_matrix = {d: {} for d in datasets}

    for dname in datasets:
        for H in horizons:
            h_key = f"H_{H}"
            for model in models:
                mse_val = data[dname].get(h_key, {}).get(model, {}).get("mse", float('nan'))
                mae_val = data[dname].get(h_key, {}).get(model, {}).get("mae", float('nan'))

                if not np.isnan(mse_val):
                    if model not in mse_matrix[dname]:
                        mse_matrix[dname][model] = []
                        mae_matrix[dname][model] = []

                    mse_matrix[dname][model].append(mse_val)
                    mae_matrix[dname][model].append(mae_val)

    # Compute averages across horizons
    print("\n" + "=" * 100)
    print("AVERAGE MSE ACROSS HORIZONS (L=96)")
    print("=" * 100)
    print(f"{'Dataset':<25}", end="")
    for m in models:
        print(f"{m:>15}", end="")
    print()
    print("-" * 100)

    for dname in datasets:
        print(f"{dname:<25}", end="")
        for model in models:
            values = mse_matrix[dname].get(model, [])
            avg = np.mean(values) if values else float('nan')
            if np.isnan(avg):
                print(f"{'N/A':>15}", end="")
            else:
                print(f"{avg:>15.2f}", end="")
        print()

    # Identify best model per dataset
    print("\n" + "=" * 100)
    print("BEST MODEL PER DATASET (Lowest Average MSE)")
    print("=" * 100)

    best_results = []
    for dname in datasets:
        best_model = None
        best_mse = float('inf')
        for model in models:
            values = mse_matrix[dname].get(model, [])
            if values:
                avg = np.mean(values)
                if avg < best_mse:
                    best_mse = avg
                    best_model = model

        if best_model:
            best_results.append({"dataset": dname, "best_model": best_model, "mse": best_mse})
            print(f"{dname:<25}: {best_model} (MSE={best_mse:.2f})")

    # Model win count
    print("\n" + "=" * 100)
    print("MODEL PERFORMANCE RANKING")
    print("=" * 100)

    wins = {m: 0 for m in models}
    for result in best_results:
        wins[result["best_model"]] += 1

    sorted_wins = sorted(wins.items(), key=lambda x: x[1], reverse=True)
    for model, count in sorted_wins:
        print(f"{model:<20}: {count} wins out of {len(datasets)} datasets")

    # Save detailed analysis
    analysis = {
        "dataset_averages": {},
        "best_models": best_results,
        "model_wins": wins,
        "overall_summary": f"Evaluated {len(models)} models on {len(datasets)} datasets across {len(horizons)} horizons"
    }

    for dname in datasets:
        analysis["dataset_averages"][dname] = {}
        for model in models:
            values = mse_matrix[dname].get(model, [])
            if values:
                analysis["dataset_averages"][dname][model] = {
                    "mean_mse": float(np.mean(values)),
                    "std_mse": float(np.std(values)),
                    "min_hmse": float(min(values)),
                    "max_mse": float(max(values))
                }

    output_path = Path("results/extended_benchmark_analysis.json")
    with open(output_path, "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"\nDetailed analysis saved to: {output_path}")

    return analysis

if __name__ == "__main__":
    load_and_analyze()
