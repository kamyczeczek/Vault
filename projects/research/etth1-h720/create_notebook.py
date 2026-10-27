"""Build etth1_model_visualization_notebook.ipynb for etth1-h720 project."""
import json
import pathlib

notebook_path = pathlib.Path("projects/research/etth1-h720/etth1_model_visualization_notebook.ipynb")

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# ETTh1 H720 Model Effectiveness & Zero-Leakage Visualization Notebook\n",
            "\n",
            "This notebook provides a complete visual evaluation and temporal leakage verification for long-horizon forecasting ($H=720$) on the **ETTh1** dataset.\n",
            "\n",
            "## Objectives\n",
            "1. **Zero-Leakage Verification**: Programmatic and visual proof that training and context windows do not overlap future ground truth targets.\n",
            "2. **Real Candidate Evaluation**: Visualizing actual project forecasters (**BigDictELM**, **AMR-24/168**, **H2K**, **Persistence**) rather than synthetic or generic baselines.\n",
            "3. **Train Window Visibility**: Displaying the full 360-day ($8640$-hour) training slice to show exactly *what the models trained on*.\n",
            "4. **Multi-Origin Walk-Forward Performance**: Evaluating performance across 12 locked test origins ($8640 \\dots 16560$) using stored evaluation results.\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Cell 1: Environment Setup & Project Path Imports\n",
            "import sys\n",
            "import json\n",
            "import pathlib\n",
            "import numpy as np\n",
            "import pandas as pd\n",
            "import matplotlib.pyplot as plt\n",
            "\n",
            "# Local workspace paths setup\n",
            "import _workspace_paths\n",
            "from _workspace_paths import ROOT, data_csv\n",
            "from members.h2k import H2KForecaster\n",
            "from members.big_dict_elm import BigDictELM\n",
            "from members.amr_fbs import AMRFBSForecaster\n",
            "\n",
            "print('Workspace environment loaded successfully.')\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Zero-Leakage Data Splitter & Verification Evidence\n",
            "We verify three strict temporal invariants:\n",
            "- $\\text{train\\_end} < \\text{target\\_start}$\n",
            "- $\\text{ctx\\_end} = \\text{target\\_start} - 1$\n",
            "- $\\text{overlap}(\\text{train}, \\text{target}) = \\emptyset$\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Cell 2: Rigorous Zero-Leakage Check Function\n",
            "def verify_zero_leakage(train_idx: np.ndarray, ctx_idx: np.ndarray, target_idx: np.ndarray) -> dict:\n",
            "    assert train_idx[-1] < target_idx[0], f'CRITICAL LEAK: train_idx end ({train_idx[-1]}) >= target_idx start ({target_idx[0]})'\n",
            "    assert ctx_idx[-1] == target_idx[0] - 1, f'DISCONTINUITY: ctx_idx end ({ctx_idx[-1]}) != target_idx start - 1 ({target_idx[0]-1})'\n",
            "    overlap = np.intersect1d(train_idx, target_idx)\n",
            "    assert overlap.size == 0, f'CRITICAL LEAK: Found {overlap.size} overlapping indices between train and target!'\n",
            "    \n",
            "    evidence = {\n",
            "        'train_range': f'[{train_idx[0]} : {train_idx[-1]}] (len={len(train_idx)})',\n",
            "        'ctx_range': f'[{ctx_idx[0]} : {ctx_idx[-1]}] (len={len(ctx_idx)})',\n",
            "        'target_range': f'[{target_idx[0]} : {target_idx[-1]}] (len={len(target_idx)})',\n",
            "        'overlap_count': int(overlap.size),\n",
            "        'status': 'PASSED_ZERO_LEAKAGE'\n",
            "    }\n",
            "    return evidence\n",
            "\n",
            "df = pd.read_csv(data_csv())\n",
            "origin_idx = 8640\n",
            "cap, lookback, horizon = 8640, 168, 720\n",
            "\n",
            "train_idxs = np.arange(origin_idx - cap, origin_idx)\n",
            "ctx_idxs = np.arange(origin_idx - lookback, origin_idx)\n",
            "target_idxs = np.arange(origin_idx, origin_idx + horizon)\n",
            "\n",
            "evidence = verify_zero_leakage(train_idxs, ctx_idxs, target_idxs)\n",
            "pd.DataFrame([evidence])\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Single-Origin Prediction Plot: Train Slice + Context + Target\n",
            "Plots the full 8640-hour training slice ('what the model learned on'), lookback context $L=168$, ground truth target $H=720$, predictions for real project forecasters (**BigDictELM**, **AMR-24/168**, **H2K**, **Persistence**), and step-by-step residual errors.\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Cell 3: Single-Origin Forecast & Residual Plotting\n",
            "s = df['OT'].to_numpy(float)\n",
            "train_slice = s[train_idxs]\n",
            "ctx_slice = s[ctx_idxs]\n",
            "target_actual = s[target_idxs]\n",
            "\n",
            "# Fit real project models\n",
            "bigdict = BigDictELM(input_length=96).fit(train_slice, horizon=horizon)\n",
            "pred_bigdict = bigdict.predict_hist(ctx_slice[-96:])[:horizon]\n",
            "\n",
            "amr = AMRFBSForecaster(lookback=96, seed=42).fit(train_slice, horizon)\n",
            "pred_amr = amr.predict_hist(ctx_slice[-96:])[:horizon]\n",
            "\n",
            "h2k = H2KForecaster(input_length=168, k_neighbors=48, drift_damping=0.0).fit(train_slice, horizon)\n",
            "pred_h2k = h2k.predict_hist(ctx_slice)[:horizon]\n",
            "\n",
            "persistence_pred = np.full(horizon, ctx_slice[-1])\n",
            "\n",
            "# Calculate MAEs\n",
            "maes = {\n",
            "    'Persistence': float(np.mean(np.abs(persistence_pred - target_actual))),\n",
            "    'BigDictELM': float(np.mean(np.abs(pred_bigdict - target_actual))),\n",
            "    'H2K': float(np.mean(np.abs(pred_h2k - target_actual))),\n",
            "    'AMR-24/168': float(np.mean(np.abs(pred_amr - target_actual)))\n",
            "}\n",
            "\n",
            "# Visualization\n",
            "fig = plt.figure(figsize=(16, 11))\n",
            "gs = fig.add_gridspec(3, 1, height_ratios=[1.2, 2.2, 1.2], hspace=0.35)\n",
            "\n",
            "# Panel 1: Full 8640h Training Slice\n",
            "ax0 = fig.add_subplot(gs[0])\n",
            "ax0.plot(train_idxs, train_slice, color='#7f8c8d', lw=0.8, alpha=0.7, label='Train Slice (8640h / 360 Days)')\n",
            "ax0.plot(target_idxs, target_actual, color='#1b1b1b', lw=1.2, label='Ground Truth Target (720h Future)')\n",
            "ax0.axvspan(train_idxs[0], train_idxs[-1], color='#bdc3c7', alpha=0.25, label='Fit Region (Strictly Historical)')\n",
            "ax0.axvspan(target_idxs[0], target_idxs[-1], color='#f1c40f', alpha=0.15, label='Target Region (Unseen)')\n",
            "ax0.axvline(x=origin_idx - 1, color='#e74c3c', linestyle='--', lw=1.8, label='Origin Cutoff t0')\n",
            "ax0.axhline(train_slice.mean(), color='#2980b9', linestyle=':', lw=1.5, label=f'Train Mean ({train_slice.mean():.2f}°C)')\n",
            "ax0.set_title(f'Macro View: Full 8640-hour Training Window at Origin {origin_idx}', fontsize=11, fontweight='bold')\n",
            "ax0.set_ylabel('OT (°C)')\n",
            "ax0.legend(loc='upper left', fontsize=8, ncol=3)\n",
            "ax0.grid(True, linestyle=':', alpha=0.5)\n",
            "\n",
            "# Panel 2: Zoomed Forecast View\n",
            "ax1 = fig.add_subplot(gs[1])\n",
            "zoom_hist_idxs = np.arange(origin_idx - 336, origin_idx)\n",
            "ax1.plot(zoom_hist_idxs, s[zoom_hist_idxs], color='#34495e', lw=1.5, label='Observed History (14 Days)')\n",
            "ax1.plot(ctx_idxs, ctx_slice, color='#2980b9', lw=2.5, label='Lookback Context L=168')\n",
            "ax1.plot(target_idxs, target_actual, color='#1b1b1b', lw=2.2, label='Ground Truth Target')\n",
            "ax1.plot(target_idxs, pred_bigdict, color='#2ecc71', lw=2.0, label=f'BigDictELM (MAE: {maes[\"BigDictELM\"]:.2f})')\n",
            "ax1.plot(target_idxs, pred_h2k, color='#3498db', lw=2.0, label=f'H2K (MAE: {maes[\"H2K\"]:.2f})')\n",
            "ax1.plot(target_idxs, pred_amr, color='#e74c3c', lw=2.0, label=f'AMR-24/168 (MAE: {maes[\"AMR-24/168\"]:.2f})')\n",
            "ax1.plot(target_idxs, persistence_pred, color='#95a5a6', lw=1.5, linestyle=':', label=f'Persistence (MAE: {maes[\"Persistence\"]:.2f})')\n",
            "ax1.axvline(x=origin_idx - 1, color='#e74c3c', linestyle='-.', lw=2.0, label='Cutoff Origin')\n",
            "ax1.axvspan(target_idxs[0], target_idxs[-1], color='#f1c40f', alpha=0.12, label='Forecast Horizon H=720')\n",
            "ax1.set_title(f'Zoomed Forecast Comparison at Origin {origin_idx}', fontsize=12, fontweight='bold')\n",
            "ax1.set_ylabel('Oil Temperature (OT)')\n",
            "ax1.legend(loc='upper left', fontsize=9, ncol=2)\n",
            "ax1.grid(True, linestyle=':', alpha=0.6)\n",
            "\n",
            "# Panel 3: Step-by-Step Residual Errors\n",
            "ax2 = fig.add_subplot(gs[2])\n",
            "ax2.plot(target_idxs, pred_bigdict - target_actual, color='#2ecc71', lw=1.2, label='BigDictELM Residual')\n",
            "ax2.plot(target_idxs, pred_h2k - target_actual, color='#3498db', lw=1.2, label='H2K Residual')\n",
            "ax2.plot(target_idxs, pred_amr - target_actual, color='#e74c3c', lw=1.2, label='AMR-24/168 Residual')\n",
            "ax2.plot(target_idxs, persistence_pred - target_actual, color='#95a5a6', lw=1.0, linestyle=':', label='Persistence Residual')\n",
            "ax2.axhline(0, color='black', linestyle='--', lw=1)\n",
            "ax2.set_title('Forecast Residuals Across 720 Hours (Step-by-Step Drift)', fontsize=10, fontweight='bold')\n",
            "ax2.set_xlabel('Time Series Hour Index')\n",
            "ax2.set_ylabel('Error (°C)')\n",
            "ax2.legend(loc='upper left', fontsize=8, ncol=4)\n",
            "ax2.grid(True, linestyle=':', alpha=0.5)\n",
            "plt.show()\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Multi-Origin Evaluation Visualization & Results Table\n",
            "Loads the locked evaluation artifact (`results/etth1_h720_amr24168_weekly.json`) and renders the 12-origin MAE curve and MAE table.\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Cell 4: Multi-Origin MAE Curves & Results Table\n",
            "results_json = ROOT / 'results' / 'etth1_h720_amr24168_weekly.json'\n",
            "data = json.loads(results_json.read_text(encoding='utf-8'))\n",
            "per_origin = data['per_origin']\n",
            "origins = [r['origin'] for r in per_origin]\n",
            "\n",
            "methods = ['persistence', 'nlinear_L96', 'bigdict_elm', 'amr_24_168']\n",
            "mae_matrix = {m: [r['methods'][m]['mae_raw'] for r in per_origin] for m in methods}\n",
            "\n",
            "fig, ax = plt.subplots(figsize=(14, 6))\n",
            "for m in methods:\n",
            "    ax.plot(origins, mae_matrix[m], marker='o', lw=2, label=m)\n",
            "\n",
            "ax.axhline(1.9781, color='#e74c3c', linestyle='--', lw=2, label='Incumbent Target G1 (1.9781)')\n",
            "ax.set_xticks(origins)\n",
            "ax.set_xticklabels([f'O{i+1}\\n({o})' for i, o in enumerate(origins)], fontsize=8)\n",
            "ax.set_title('Multi-Origin Raw MAE Across 12 Locked Test Origins (H720)', fontsize=12, fontweight='bold')\n",
            "ax.set_ylabel('Raw MAE (°C)')\n",
            "ax.set_xlabel('Origin Index (Cutoff)')\n",
            "ax.legend(loc='upper right')\n",
            "ax.grid(True, linestyle=':', alpha=0.6)\n",
            "plt.show()\n",
            "\n",
            "# Display Summary Table\n",
            "table_rows = []\n",
            "for m in methods:\n",
            "    vals = mae_matrix[m]\n",
            "    table_rows.append({\n",
            "        'Method': m,\n",
            "        'Mean MAE': round(float(np.mean(vals)), 4),\n",
            "        'Std MAE': round(float(np.std(vals)), 4),\n",
            "        'Min MAE': round(float(np.min(vals)), 4),\n",
            "        'Max MAE': round(float(np.max(vals)), 4),\n",
            "        'Wins < 1.9781': sum(v < 1.9781 for v in vals)\n",
            "    })\n",
            "pd.DataFrame(table_rows)\n"
        ]
    }
]

nb_content = {
    "cells": cells,
    "metadata": {
        "language_info": {"name": "python"}
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

notebook_path.write_text(json.dumps(nb_content, indent=2), encoding="utf-8")
print(f"Created real notebook file: {notebook_path}")
