"""Generate Publication-Ready Visualizations for Extended Benchmark"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def plot_extended_benchmark():
    results_path = Path("results/results_extended_benchmark.json")
    with open(results_path, "r") as f:
        data = json.load(f)

    datasets = ["Electricity_Hourly", "Traffic_Flow", "Financial_Returns",
                "Weather_Temperature", "Web_Traffic", "Healthcare_Vitals"]
    horizons = [96, 192, 336, 720]
    models = ["AMR-FBS", "StateSpaceHybrid", "KNNForecaster", "BigDictELM",
              "DLinear", "SpectralFFT", "Theta"]

    # Color palette
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e']

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    for idx, dname in enumerate(datasets):
        ax = axes[idx]

        # Collect MSE values for each model across horizons
        mse_data = {m: [] for m in models}
        for H in horizons:
            h_key = f"H_{H}"
            for model in models:
                mse_val = data[dname].get(h_key, {}).get(model, {}).get("mse")
                if mse_val is not None and not np.isnan(mse_val):
                    mse_data[model].append(mse_val)
                else:
                    mse_data[model].append(np.nan)

        x = np.arange(len(horizons))
        width = 0.12

        for i, (model, color) in enumerate(zip(models, colors)):
            values = mse_data[model]
            # Skip models with all NaN (failed completely)
            if all(np.isnan(v) for v in values):
                continue
            # Use median for visualization if some NaNs
            valid_values = [v for v in values if not np.isnan(v)]
            if valid_values:
                offset = i * width
                positions = x + offset
                ax.bar(positions, valid_values, width,
                       label=model, color=color, alpha=0.8)

        ax.set_xlabel('Horizon (H)', fontsize=10)
        ax.set_ylabel('MSE', fontsize=10)
        ax.set_title(dname.replace('_', ' '), fontsize=11, fontweight='bold')
        ax.set_xticks(x + width*3)
        ax.set_xticklabels([str(H) for H in horizons], fontsize=8)
        ax.legend(fontsize=7, loc='upper right', ncol=2)
        ax.grid(True, alpha=0.3)

    plt.suptitle('Extended Benchmark: MSE by Dataset and Horizon (L=96)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    output_path = Path("plots/extended_benchmark_comparison.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()

    # Plot 2: Model win bar chart
    fig, ax = plt.subplots(figsize=(10, 6))

    analysis_path = Path("results/extended_benchmark_analysis.json")
    with open(analysis_path, "r") as f:
        analysis = json.load(f)

    wins = analysis["model_wins"]
    sorted_models = sorted(wins.items(), key=lambda x: x[1], reverse=True)
    model_names = [m[0] for m in sorted_models]
    win_counts = [m[1] for m in sorted_models]

    bars = ax.barh(model_names, win_counts, color=colors[:len(model_names)])
    ax.set_xlabel('Number of Dataset Wins', fontsize=12)
    ax.set_title('Model Performance Ranking Across 6 Datasets', fontsize=14, fontweight='bold')
    ax.set_xlim(0, max(win_counts) + 1)

    # Add value labels on bars
    for bar, count in zip(bars, win_counts):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f'{count}', va='center', fontsize=11, fontweight='bold')

    plt.tight_layout()
    output_path = Path("plots/model_performance_ranking.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()

    # Plot 3: Heatmap of best model per dataset
    best_dict = {b["dataset"]: b["best_model"] for b in analysis["best_models"]}

    fig, ax = plt.subplots(figsize=(12, 6))

    heatmap_data = np.zeros((len(datasets), len(models)))
    for i, dname in enumerate(datasets):
        for j, model in enumerate(models):
            if model == best_dict.get(dname, ""):
                heatmap_data[i, j] = 1

    im = ax.imshow(heatmap_data, cmap='Blues', aspect='auto')
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models, rotation=45, ha='right', fontsize=9)
    ax.set_yticks(range(len(datasets)))
    ax.set_yticklabels([d.replace('_', ' ') for d in datasets], fontsize=10)
    ax.set_title('Best Model per Dataset (Blue cells indicate winner)', fontsize=12, fontweight='bold')

    plt.tight_layout()
    output_path = Path("plots/best_model_heatmap.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()

    print("\nAll visualizations generated successfully!")

if __name__ == "__main__":
    plot_extended_benchmark()
