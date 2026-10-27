"""Generate Publication-Quality Figures for Multi-Horizon Benchmark Results."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
import json

# Set publication style
matplotlib.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

def load_results():
    """Load multi-horizon benchmark results."""
    with open("results/results_multi_horizon.json", "r") as f:
        return json.load(f)

def plot_performance_vs_horizon(results, output_dir):
    """Plot MSE performance vs forecast horizon for each dataset."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    datasets = list(results.keys())
    horizons = [96, 192, 336, 720]
    models = ["Adaptive_AMR_KNN (Ours)", "AMR-FBS", "KNNForecaster", "DLinear", "SpectralFFT"]
    colors = {"Adaptive_AMR_KNN (Ours)": "#2E86AB", "AMR-FBS": "#A23B72",
              "KNNForecaster": "#F18F01", "DLinear": "#C73E1D", "SpectralFFT": "#3B1F2B"}
    markers = {"Adaptive_AMR_KNN (Ours)": "o", "AMR-FBS": "s",
               "KNNForecaster": "^", "DLinear": "D", "SpectralFFT": "v"}

    for idx, dname in enumerate(datasets):
        ax = axes[idx]
        dataset_data = results[dname]

        for model in models:
            mse_values = []
            for H in horizons:
                if str(H) in dataset_data and model in dataset_data[str(H)]:
                    metrics = dataset_data[str(H)][model]
                    if isinstance(metrics, dict) and "mse" in metrics and metrics["mse"] != "NaN":
                        mse_values.append(metrics["mse"])
                    else:
                        mse_values.append(np.nan)
                else:
                    mse_values.append(np.nan)

            valid_mask = ~np.isnan(mse_values)
            if np.any(valid_mask):
                ax.plot(horizons, mse_values, marker=markers.get(model, 'o'),
                       color=colors.get(model, 'blue'), linewidth=2,
                       markersize=6, label=model, alpha=0.8)

        ax.set_xlabel('Forecast Horizon (h)', fontsize=10)
        ax.set_title(dname.replace('_', '\n'), fontsize=11)
        ax.set_xticks(horizons)
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)

        if idx == 0:
            ax.legend(loc='upper left', fontsize=8, framealpha=0.9)

    plt.suptitle('Model Performance vs Forecast Horizon (MSE)', fontsize=13, y=1.02)
    plt.tight_layout()
    out_path = output_dir / "performance_vs_horizon.png"
    plt.savefig(out_path, bbox_inches='tight')
    print(f"Saved: {out_path}")
    plt.close()

def plot_win_rates(results, output_dir):
    """Plot win rate bar chart across datasets."""
    fig, ax = plt.subplots(figsize=(10, 6))

    datasets = list(results.keys())
    models = ["Adaptive_AMR_KNN (Ours)", "AMR-FBS", "KNNForecaster", "DLinear", "SpectralFFT"]
    colors = {"Adaptive_AMR_KNN (Ours)": "#2E86AB", "AMR-FBS": "#A23B72",
              "KNNForecaster": "#F18F01", "DLinear": "#C73E1D", "SpectralFFT": "#3B1F2B"}

    # Calculate win rates
    win_counts = {model: [0] * len(datasets) for model in models}

    for idx, dname in enumerate(datasets):
        dataset_data = results[dname]
        horizons = [96, 192, 336, 720]

        for H in horizons:
            H_str = str(H)
            if H_str in dataset_data:
                best_mse = float('inf')
                best_model = None
                for model in models:
                    if model in dataset_data[H_str]:
                        metrics = dataset_data[H_str][model]
                        if isinstance(metrics, dict) and "mse" in metrics and metrics["mse"] != "NaN":
                            if metrics["mse"] < best_mse:
                                best_mse = metrics["mse"]
                                best_model = model
                if best_model:
                    win_counts[best_model][idx] += 1

    # Convert to percentages
    win_pcts = {model: [count / len([96, 192, 336, 720]) * 100 for count in counts]
                for model, counts in win_counts.items()}

    x = np.arange(len(datasets))
    width = 0.15

    for i, model in enumerate(models):
        bars = ax.bar(x + i * width, win_pcts[model], width, label=model, color=colors[model], alpha=0.85)
        # Add value labels
        for bar, pct in zip(bars, win_pcts[model]):
            if pct > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                       f'{pct:.0f}%', ha='center', va='bottom', fontsize=8)

    ax.set_xlabel('Dataset', fontsize=11)
    ax.set_ylabel('Win Rate (%)', fontsize=11)
    ax.set_title('Model Win Rates Across Datasets (across 4 horizons each)', fontsize=13)
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels([d.replace('_', '\n') for d in datasets], fontsize=9)
    ax.legend(loc='upper right', fontsize=9)
    ax.set_ylim(0, 105)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    out_path = output_dir / "win_rates.png"
    plt.savefig(out_path, bbox_inches='tight')
    print(f"Saved: {out_path}")
    plt.close()

def plot_heatmap(results, output_dir):
    """Plot heatmap of MSE values across models and datasets."""
    fig, ax = plt.subplots(figsize=(10, 6))

    datasets = list(results.keys())
    models = ["Adaptive_AMR_KNN (Ours)", "AMR-FBS", "KNNForecaster", "DLinear", "SpectralFFT"]
    horizons = [96, 192, 336, 720]

    # Compute average MSE across horizons for each dataset-model pair
    heat_data = np.zeros((len(datasets), len(models)))

    for i, dname in enumerate(datasets):
        for j, model in enumerate(models):
            mse_values = []
            dataset_data = results[dname]
            for H in horizons:
                H_str = str(H)
                if H_str in dataset_data and model in dataset_data[H_str]:
                    metrics = dataset_data[H_str][model]
                    if isinstance(metrics, dict) and "mse" in metrics and metrics["mse"] != "NaN":
                        mse_values.append(metrics["mse"])
            heat_data[i, j] = np.mean(mse_values) if mse_values else np.nan

    # Normalize within each dataset for better visualization
    for i in range(len(datasets)):
        row = heat_data[i, :]
        valid = row[~np.isnan(row)]
        if len(valid) > 0:
            heat_data[i, :] = (row - np.min(valid)) / (np.max(valid) - np.min(valid) + 1e-8) * 100

    im = ax.imshow(heat_data, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=100)

    ax.set_xticks(np.arange(len(models)))
    ax.set_yticks(np.arange(len(datasets)))
    ax.set_xticklabels(models, fontsize=9)
    ax.set_yticklabels([d.replace('_', '\n') for d in datasets], fontsize=9)
    ax.set_xlabel('Model', fontsize=11)
    ax.set_title('Normalized MSE Heatmap (Green=Best, Red=Worst)', fontsize=13)

    # Add text annotations
    for i in range(len(datasets)):
        for j in range(len(models)):
            if not np.isnan(heat_data[i, j]):
                text = ax.text(j, i, f'{heat_data[i, j]:.0f}',
                             ha="center", va="center", color="black" if heat_data[i, j] < 50 else "white",
                             fontsize=9)

    plt.colorbar(im, ax=ax, label='Normalized MSE (0=Best, 100=Worst)')
    plt.tight_layout()
    out_path = output_dir / "mse_heatmap.png"
    plt.savefig(out_path, bbox_inches='tight')
    print(f"Saved: {out_path}")
    plt.close()

def plot_comparison_table(results, output_dir):
    """Create a publication-ready comparison table."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')

    datasets = list(results.keys())
    models = ["Adaptive_AMR_KNN (Ours)", "AMR-FBS", "KNNForecaster", "DLinear", "SpectralFFT"]
    horizons = [96, 192, 336, 720]

    # Create table data with columns: Model, Dataset1, Dataset2, Dataset3, Overall Avg
    table_data = [['Model'] + [d.replace('_', ' ') for d in datasets] + ['Overall Avg']]

    for model in models:
        row = [model]
        mse_sum = 0
        mse_count = 0
        for dname in datasets:
            mse_values = []
            dataset_data = results[dname]
            for H in horizons:
                H_str = str(H)
                if H_str in dataset_data and model in dataset_data[H_str]:
                    metrics = dataset_data[H_str][model]
                    if isinstance(metrics, dict) and "mse" in metrics and metrics["mse"] != "NaN":
                        mse_values.append(metrics["mse"])
            if mse_values:
                avg_mse = np.mean(mse_values)
                row.append(f'{avg_mse:.1f}')
                mse_sum += avg_mse
                mse_count += 1
            else:
                row.append('-')
        overall_avg = mse_sum / mse_count if mse_count > 0 else 0
        row.append(f'{overall_avg:.1f}')
        table_data.append(row)

    table = ax.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)

    # Style header row
    for j in range(len(table_data[0])):
        cell = table[(0, j)]
        cell.set_facecolor('#40466e')
        cell.set_text_props(color='white', weight='bold')

    # Highlight best model per dataset
    for i, dname in enumerate(datasets):
        dataset_data = results[dname]
        min_mse = float('inf')
        best_model = None
        for model in models:
            for H in horizons:
                H_str = str(H)
                if H_str in dataset_data and model in dataset_data[H_str]:
                    metrics = dataset_data[H_str][model]
                    if isinstance(metrics, dict) and "mse" in metrics and metrics["mse"] != "NaN":
                        if metrics["mse"] < min_mse:
                            min_mse = metrics["mse"]
                            best_model = model

        if best_model:
            model_idx = models.index(best_model)
            for col in range(1, len(table_data[0])):
                cell = table[(i + 1, col)]
                cell.set_facecolor('#d8f3dc' if col <= 3 else '#b7e4c7')

    ax.set_title('Multi-Horizon Benchmark Results: Average MSE per Model per Dataset',
                fontsize=14, pad=20)
    plt.tight_layout()
    out_path = output_dir / "comparison_table.png"
    plt.savefig(out_path, bbox_inches='tight')
    print(f"Saved: {out_path}")
    plt.close()

def main():
    output_dir = Path("plots")
    output_dir.mkdir(exist_ok=True)

    print("Loading results...")
    results = load_results()

    print("\nGenerating figures...")
    plot_performance_vs_horizon(results, output_dir)
    plot_win_rates(results, output_dir)
    plot_heatmap(results, output_dir)
    plot_comparison_table(results, output_dir)

    print("\nAll publication-quality figures generated!")
    print(f"Output directory: {output_dir.absolute()}")

if __name__ == "__main__":
    main()
