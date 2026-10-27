"""Plot Adaptive AMR-KNN Hybrid benchmark comparisons."""
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def plot_adaptive_results():
    with open("results/results_adaptive_hybrid.json", "r") as f:
        data = json.load(f)

    datasets = list(data.keys())
    models = ["AMR-FBS", "KNNForecaster", "Adaptive_AMR_KNN (Ours)", "DLinear"]
    colors = ['#e74c3c', '#2ecc71', '#3498db', '#95a5a6']

    # We will make subplots for the 6 datasets normalized to DLinear or raw MSE
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    for idx, dname in enumerate(datasets):
        ax = axes[idx]
        mses = [data[dname][m]["mse"] for m in models]
        bars = ax.bar(models, mses, color=colors, alpha=0.85)
        ax.set_title(dname.replace('_', ' '), fontsize=11, fontweight='bold')
        ax.set_ylabel('MSE', fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_xticklabels(["AMR-FBS", "KNN", "Adaptive\nHybrid", "DLinear"], fontsize=9)

        # Add values on top
        for bar in bars:
            height = bar.get_height()
            if height < 1000:
                ax.text(bar.get_x() + bar.get_width()/2., height * 1.02,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.suptitle("Adaptive AMR-KNN Hybrid: Multi-Domain General-Purpose Forecasting ($L=96, H=96$)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    out_path = Path("plots/adaptive_amr_knn_comparison.png")
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f"Saved plot: {out_path}")
    plt.close()

if __name__ == "__main__":
    plot_adaptive_results()
