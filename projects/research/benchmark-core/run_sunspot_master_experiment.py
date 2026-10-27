"""Master Sunspot Forecasting Experiment Suite (`run_sunspot_master_experiment.py`)

Implements literature-backed sunspot evaluation protocols:
1. Waldmeier Asymmetry Index evaluation (measuring rise vs fall phase asymmetry).
2. Peak Amplitude Jitter error analysis across solar maxima.
3. Takens' phase-space embedding hyperparameter ablation (tau and embed_dim).
4. Structured JSON reporting (`results_sunspot_master.json`).
"""
from __future__ import annotations
import numpy as np
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from bench import get_sunspot
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.big_dict_elm import BigDictELM
from members.amr_dynamo_attractor import fit_amr_dynamo_attractor, pred_amr_dynamo_attractor, _attractor_nearest_neighbor_forecast
from members.sota_baselines import fit_dlinear, pred_dlinear

def calculate_waldmeier_asymmetry(series: np.ndarray) -> float:
    """Calculates Waldmeier asymmetry index: ratio of rise time to fall time between consecutive extrema."""
    if len(series) < 24:
        return 1.0
    # Find local minima and maxima roughly
    diffs = np.diff(series)
    sign_changes = np.where(np.diff(np.signbit(diffs)))[0]
    if len(sign_changes) < 2:
        return 1.0

    rises = []
    falls = []
    for i in range(len(sign_changes) - 1):
        p1 = sign_changes[i]
        p2 = sign_changes[i+1]
        segment = series[p1:p2+1]
        if len(segment) < 3:
            continue
        local_extreme_idx = np.argmax(segment) if diffs[p1] > 0 else np.argmin(segment)
        rise_len = local_extreme_idx
        fall_len = len(segment) - 1 - local_extreme_idx
        if fall_len > 0:
            rises.append(rise_len)
            falls.append(fall_len)

    if not rises or not falls:
        return 0.5
    avg_rise = np.mean(rises)
    avg_fall = np.mean(falls)
    return float(avg_rise / (avg_fall + 1e-5))

def run_master_experiment():
    print("=== Loading Sunspot Dataset for Master Literature Experiment ===")
    series = get_sunspot(3000)

    origins = [1800, 2000, 2200]
    horizon = 132 # 11 years (1 full solar cycle)
    lookback = 120

    print(f"\n[Experiment 1 & 2] Running Waldmeier Asymmetry & Peak Amplitude Analysis (H={horizon})...")

    models = {
        "AMR-FBS": (lambda tr, h: fit_amr_fbs(tr, h), lambda m, h: pred_amr_fbs(m, h)),
        "AMR-Dynamo": (lambda tr, h: fit_amr_dynamo_attractor(tr, h), lambda m, h: pred_amr_dynamo_attractor(m, h)),
        "DLinear": (fit_dlinear, pred_dlinear)
    }

    evaluation_results = {}

    true_asymmetry = calculate_waldmeier_asymmetry(series[1800:1800+horizon])
    print(f"Ground Truth Waldmeier Asymmetry Index: {true_asymmetry:.3f}")

    for origin in origins:
        history = series[:origin]
        actual = series[origin:origin+horizon]
        true_peak = float(np.max(actual))

        evaluation_results[origin] = {
            "true_peak": true_peak,
            "true_asymmetry": true_asymmetry,
            "models": {}
        }

        print(f"\n--- Origin t = {origin} (True Peak: {true_peak:.1f}) ---")
        for name, (fit_fn, pred_fn) in models.items():
            try:
                m = fit_fn(history, horizon)
                pred = np.asarray(pred_fn(m, history[-lookback:]), dtype=float).ravel()[:horizon]
                if len(pred) != horizon:
                    pred = np.resize(pred, horizon)

                mae = float(np.mean(np.abs(pred - actual)))
                pred_peak = float(np.max(pred))
                peak_error = float(abs(pred_peak - true_peak))
                pred_asymmetry = calculate_waldmeier_asymmetry(pred)
                asymmetry_error = float(abs(pred_asymmetry - true_asymmetry))

                evaluation_results[origin]["models"][name] = {
                    "mae": mae,
                    "pred_peak": pred_peak,
                    "peak_error": peak_error,
                    "pred_asymmetry": pred_asymmetry,
                    "asymmetry_error": asymmetry_error
                }
                print(f"  {name:15s} | MAE: {mae:6.2f} | Peak Err: {peak_error:5.1f} | Asym Err: {asymmetry_error:5.3f}")
            except Exception as e:
                print(f"  {name:15s} | Error: {e}")

    print("\n[Experiment 3] Takens' Phase-Space Embedding Ablation (tau & embed_dim)...")
    ablation_results = {}
    test_history = series[:2000]
    test_actual = series[2000:2000+horizon]

    for tau in [1, 3, 6]:
        for dim in [6, 12, 18]:
            try:
                pred = _attractor_nearest_neighbor_forecast(test_history, horizon, embed_dim=dim, tau=tau)
                pred = np.asarray(pred, dtype=float).ravel()[:horizon]
                mae = float(np.mean(np.abs(pred - test_actual)))
                key = f"tau={tau}_dim={dim}"
                ablation_results[key] = mae
                print(f"  Embedding [tau={tau}, dim={dim}] -> MAE: {mae:.3f}")
            except Exception as e:
                print(f"  Embedding [tau={tau}, dim={dim}] -> Error: {e}")

    best_embedding = min(ablation_results, key=ablation_results.get) if ablation_results else "N/A"
    print(f"\nBest Phase-Space Embedding Configuration: {best_embedding} (MAE: {ablation_results.get(best_embedding, 0):.3f})")

    # Save master results
    master_output = {
        "origins_evaluation": evaluation_results,
        "takens_ablation": ablation_results,
        "best_embedding": best_embedding
    }

    out_file = "results_sunspot_master.json"
    with open(out_file, "w") as f:
        json.dump(master_output, f, indent=2)
    print(f"\nSaved master sunspot experiment suite results to {out_file}")

if __name__ == "__main__":
    run_master_experiment()
