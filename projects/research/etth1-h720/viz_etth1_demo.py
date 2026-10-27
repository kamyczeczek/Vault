"""ETTh1 H720 Model Effectiveness & Zero-Leakage Visualization Script.

Demonstrates:
1. Rigorous Zero-Leakage Verification (asserts, index ranges, 0 overlap).
2. Single-origin visualization showing Train Window (8640h), Context (168h), Target (720h), and normalization anchor.
3. Actual project model comparisons: BigDictELM, AMR-24/168, H2K, Persistence.
4. Multi-origin 12-origin evaluation visualization loaded from results artifact.
"""
from __future__ import annotations

import json
import pathlib
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import _workspace_paths
from _workspace_paths import ROOT, data_csv
from members.h2k import H2KForecaster
from members.big_dict_elm import BigDictELM
from members.amr_fbs import AMRFBSForecaster

def verify_zero_leakage(train_idx: np.ndarray, ctx_idx: np.ndarray, target_idx: np.ndarray) -> dict:
    """Rigorous visual & programmatic verification of temporal boundaries."""
    # Asercja 1: strict inequality
    assert train_idx[-1] < target_idx[0], f"CRITICAL LEAK: train_idx end ({train_idx[-1]}) >= target_idx start ({target_idx[0]})"
    # Asercja 2: continuity
    assert ctx_idx[-1] == target_idx[0] - 1, f"DISCONTINUITY: ctx_idx end ({ctx_idx[-1]}) != target_idx start - 1 ({target_idx[0]-1})"
    # Asercja 3: zero overlap between train and target
    overlap = np.intersect1d(train_idx, target_idx)
    assert overlap.size == 0, f"CRITICAL LEAK: Found {overlap.size} overlapping indices between train and target!"

    evidence = {
        "train_start": int(train_idx[0]),
        "train_end": int(train_idx[-1]),
        "train_len": len(train_idx),
        "ctx_start": int(ctx_idx[0]),
        "ctx_end": int(ctx_idx[-1]),
        "ctx_len": len(ctx_idx),
        "target_start": int(target_idx[0]),
        "target_end": int(target_idx[-1]),
        "target_len": len(target_idx),
        "overlap_count": int(overlap.size),
        "status": "PASSED_ZERO_LEAKAGE"
    }
    print(f"[LEAK CHECK PASSED] Train [{evidence['train_start']}:{evidence['train_end']}] | Target [{evidence['target_start']}:{evidence['target_end']}] | Overlap: {evidence['overlap_count']}")
    return evidence

def plot_single_origin(
    df: pd.DataFrame,
    origin_idx: int = 8640,
    lookback_len: int = 168,
    horizon: int = 720,
    cap: int = 8640,
    out_path: pathlib.Path | None = None
) -> dict:
    """Plot full train slice, lookback context, ground truth, predictions for real models, and residual errors."""
    s = df["OT"].to_numpy(float)

    # 1. Slices
    train_slice = s[origin_idx - cap : origin_idx]
    ctx_slice = s[origin_idx - lookback_len : origin_idx]
    target_actual = s[origin_idx : origin_idx + horizon]

    train_idxs = np.arange(origin_idx - cap, origin_idx)
    ctx_idxs = np.arange(origin_idx - lookback_len, origin_idx)
    target_idxs = np.arange(origin_idx, origin_idx + horizon)

    # 2. Leakage check
    evidence = verify_zero_leakage(train_idxs, ctx_idxs, target_idxs)

    # Calculate normalization stats ONLY from train_slice
    train_mean = float(train_slice.mean())
    train_std = float(train_slice.std())

    # 3. Fit real project models
    print("Fitting BigDictELM...")
    bigdict = BigDictELM(input_length=96).fit(train_slice, horizon=horizon)
    pred_bigdict = bigdict.predict_hist(ctx_slice[-96:])[:horizon]

    print("Fitting AMR-24/168...")
    amr = AMRFBSForecaster(lookback=96, seed=42).fit(train_slice, horizon)
    pred_amr = amr.predict_hist(ctx_slice[-96:])[:horizon]

    print("Fitting H2K...")
    h2k = H2KForecaster(input_length=168, k_neighbors=48, drift_damping=0.0).fit(train_slice, horizon)
    pred_h2k = h2k.predict_hist(ctx_slice)[:horizon]

    persistence_pred = np.full(horizon, ctx_slice[-1])

    # Compute MAEs
    maes = {
        "persistence": float(np.mean(np.abs(persistence_pred - target_actual))),
        "bigdict_elm": float(np.mean(np.abs(pred_bigdict - target_actual))),
        "amr_24_168": float(np.mean(np.abs(pred_amr - target_actual))),
        "h2k": float(np.mean(np.abs(pred_h2k - target_actual))),
    }

    # 4. Visualization (Subplots: Overview with Train Slice, Zoomed Horizon, Residuals)
    fig = plt.figure(figsize=(16, 11))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.2, 2.2, 1.2], hspace=0.35)

    # Panel 1: Overview showing Full 8640h Training Window (Fit Region) vs Target
    ax0 = fig.add_subplot(gs[0])
    ax0.plot(train_idxs, train_slice, color="#7f8c8d", lw=0.8, alpha=0.7, label="Train Slice s[origin-8640 : origin] (360 Days)")
    ax0.plot(target_idxs, target_actual, color="#1b1b1b", lw=1.2, label="Ground Truth Target (720h Future)")
    ax0.axvspan(origin_idx - cap, origin_idx, color="#bdc3c7", alpha=0.25, label="Train Fit Region (Strictly Historical)")
    ax0.axvspan(origin_idx, origin_idx + horizon, color="#f1c40f", alpha=0.15, label="Unseen Target Region")
    ax0.axvline(x=origin_idx - 1, color="#e74c3c", linestyle="--", lw=1.8, label="Origin Cutoff t0")
    ax0.axhline(train_mean, color="#2980b9", linestyle=":", lw=1.5, label=f"Train μ ({train_mean:.2f}) - fit statistics only")
    ax0.set_title(f"Macro View: Full 8640-hour Training Slice ('On what it learned') at Origin {origin_idx}", fontsize=11, fontweight="bold")
    ax0.set_ylabel("OT (°C)", fontsize=9)
    ax0.legend(loc="upper left", fontsize=8, ncol=3)
    ax0.grid(True, linestyle=":", alpha=0.5)

    # Panel 2: Zoomed View around Cutoff (Context + Target Predictions)
    ax1 = fig.add_subplot(gs[1])
    zoom_history = 336
    zoom_hist_idxs = np.arange(origin_idx - zoom_history, origin_idx)
    zoom_hist_vals = s[origin_idx - zoom_history : origin_idx]

    ax1.plot(zoom_hist_idxs, zoom_hist_vals, color="#34495e", lw=1.5, label="Observed History (Last 14 Days)")
    ax1.plot(ctx_idxs, ctx_slice, color="#2980b9", lw=2.5, label="Lookback Context L=168 (Input to predict_hist)")
    ax1.plot(target_idxs, target_actual, color="#1b1b1b", lw=2.2, label="Ground Truth Target")

    # Real models
    ax1.plot(target_idxs, pred_bigdict, color="#2ecc71", lw=2.0, label=f"BigDictELM (MAE: {maes['bigdict_elm']:.2f})")
    ax1.plot(target_idxs, pred_h2k, color="#3498db", lw=2.0, label=f"H2K (MAE: {maes['h2k']:.2f})")
    ax1.plot(target_idxs, pred_amr, color="#e74c3c", lw=2.0, label=f"AMR-24/168 (MAE: {maes['amr_24_168']:.2f})")
    ax1.plot(target_idxs, persistence_pred, color="#95a5a6", lw=1.5, linestyle=":", label=f"Persistence (MAE: {maes['persistence']:.2f})")

    ax1.axvline(x=origin_idx - 1, color="#e74c3c", linestyle="-.", lw=2.0, label="Cutoff Origin (No Future Data Beyond)")
    ax1.axvspan(origin_idx, origin_idx + horizon, color="#f1c40f", alpha=0.12, label="Forecast Horizon H=720")

    ax1.set_title(f"ETTh1 H720 Model Performance Comparison at Origin {origin_idx}", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Oil Temperature (OT)", fontsize=10)
    ax1.legend(loc="upper left", fontsize=9, ncol=2, frameon=True)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Panel 3: Step-by-Step Residual Errors
    ax2 = fig.add_subplot(gs[2])
    ax2.plot(target_idxs, pred_bigdict - target_actual, color="#2ecc71", lw=1.2, label="BigDictELM Residual")
    ax2.plot(target_idxs, pred_h2k - target_actual, color="#3498db", lw=1.2, label="H2K Residual")
    ax2.plot(target_idxs, pred_amr - target_actual, color="#e74c3c", lw=1.2, label="AMR-24/168 Residual")
    ax2.plot(target_idxs, persistence_pred - target_actual, color="#95a5a6", lw=1.0, linestyle=":", label="Persistence Residual")
    ax2.axhline(0, color="black", linestyle="--", lw=1)
    ax2.set_title("Forecast Residuals Across 720 Hours (Step-by-Step Drift)", fontsize=10, fontweight="bold")
    ax2.set_xlabel("Hour Index in Time Series", fontsize=10)
    ax2.set_ylabel("Error (°C)", fontsize=9)
    ax2.legend(loc="upper left", fontsize=8, ncol=4)
    ax2.grid(True, linestyle=":", alpha=0.5)

    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        print(f"[PLOT SAVED] Single Origin Plot: {out_path}")
    plt.close(fig)

    return {"evidence": evidence, "maes": maes}

def plot_multi_origin_evaluation(results_json_path: pathlib.Path, out_path: pathlib.Path | None = None):
    """Plot multi-origin 12-origin MAE performance and variance heatmap from locked evaluation artifact."""
    if not results_json_path.exists():
        print(f"Warning: {results_json_path} does not exist. Skipping multi-origin plot.")
        return

    data = json.loads(results_json_path.read_text(encoding="utf-8"))
    per_origin = data["per_origin"]
    origins = [r["origin"] for r in per_origin]

    methods_to_plot = ["persistence", "nlinear_L96", "bigdict_elm", "amr_24_168"]
    labels = {"persistence": "Persistence", "nlinear_L96": "NLinear (L96)", "bigdict_elm": "BigDictELM", "amr_24_168": "AMR-24/168"}

    origin_maes = {m: [] for m in methods_to_plot}
    for r in per_origin:
        for m in methods_to_plot:
            val = r["methods"].get(m, {}).get("mae_raw", np.nan)
            origin_maes[m].append(val)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), gridspec_kw={'height_ratios': [2, 1.2]})

    # Upper Line plot: MAE per origin
    for m in methods_to_plot:
        ax1.plot(origins, origin_maes[m], marker="o", lw=2, label=labels[m])

    ax1.axhline(1.9781, color="#e74c3c", linestyle="--", lw=2, label="Incumbent Target G1 (1.9781)")
    ax1.set_xticks(origins)
    ax1.set_xticklabels([f"O{i+1}\n({o})" for i, o in enumerate(origins)], rotation=0, fontsize=8)
    ax1.set_title("Multi-Origin H720 Performance across 12 Locked Test Origins (ETTh1)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Raw MAE (°C)", fontsize=10)
    ax1.legend(loc="upper right", frameon=True)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Lower Heatmap plot: Model x Origin MAE matrix using matplotlib imshow
    heatmap_matrix = np.array([origin_maes[m] for m in methods_to_plot])
    im = ax2.imshow(heatmap_matrix, cmap="YlOrRd", aspect="auto")
    fig.colorbar(im, ax=ax2, label="MAE (°C)")

    ax2.set_xticks(np.arange(len(origins)))
    ax2.set_xticklabels([f"O{i+1}" for i in range(len(origins))])
    ax2.set_yticks(np.arange(len(methods_to_plot)))
    ax2.set_yticklabels([labels[m] for m in methods_to_plot])

    # Annotate values inside heatmap
    for i in range(len(methods_to_plot)):
        for j in range(len(origins)):
            val = heatmap_matrix[i, j]
            text_color = "white" if val > 4.5 else "black"
            ax2.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=8)

    ax2.set_title("MAE Heatmap across Origins (Shows Variance & Failure Origins)", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Evaluation Origins (O1=8640 ... O12=16560)", fontsize=10)

    plt.tight_layout()
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        print(f"[PLOT SAVED] Multi Origin Plot: {out_path}")
    plt.close(fig)

def main():
    print("Loading ETTh1 dataset...")
    df = pd.read_csv(data_csv())
    print(f"Loaded ETTh1 dataset with {len(df)} rows.")

    plots_dir = ROOT / "plots"
    plots_dir.mkdir(exist_ok=True)

    # 1. Single origin plot
    out_single = plots_dir / "etth1_h720_single_origin_demo.png"
    result_single = plot_single_origin(df, origin_idx=8640, out_path=out_single)

    # 2. Multi origin plot
    results_json = ROOT / "results" / "etth1_h720_amr24168_weekly.json"
    out_multi = plots_dir / "etth1_h720_multi_origin_demo.png"
    plot_multi_origin_evaluation(results_json, out_path=out_multi)

    print(f"Leakage Verification Summary: {result_single['evidence']['status']}")
    print(f"Single Origin 8640 MAEs: {result_single['maes']}")

    # Expected success token
    print("VIZ_DEMO_SUCCESS")

if __name__ == "__main__":
    main()
