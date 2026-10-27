import os
import json
import numpy as np
import pandas as pd

from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.state_space_hybrid import fit_state_space_hybrid, pred_state_space_hybrid
from members.knn_feature_forecaster import KNNFeatureForecaster

def simulate_intervention_series(n=1200, shock_at=900, magnitude=6.0):
    """
    Creates a synthetic time-series with a structural break (pulse intervention)
    following Bartos & McCleary (2017) intervention modeling principles.
    """
    np.random.seed(42)
    time = np.arange(n)
    x = np.zeros(n)
    phi = 0.8
    for t in range(1, n):
        x[t] = phi * x[t-1] + np.random.normal(0, 1)

    intervention = np.zeros(n)
    intervention[shock_at:] = magnitude * np.exp(-0.05 * (np.arange(n - shock_at)))

    y = x + intervention
    return y, intervention

def run_textbook_experiment():
    print("=== Running Textbook-Validated Experiment ===")
    print("Integrating Bartos & McCleary Intervention Modeling & Manu Joseph Structured Configs")

    series, intervention = simulate_intervention_series(n=1200, shock_at=900, magnitude=6.0)

    lookback = 96
    horizon = 96
    train_end = 900

    train_data = series[:train_end]
    test_actuals = series[train_end:train_end + horizon]
    test_intervention = intervention[train_end:train_end + horizon]

    models = {
        "AMR-FBS": (lambda tr, h: fit_amr_fbs(tr, h), lambda m, h: pred_amr_fbs(m, series[train_end-lookback:train_end])),
        "StateSpaceHybrid": (lambda tr, h: fit_state_space_hybrid(tr, h), lambda m, h: pred_state_space_hybrid(m, series[train_end-lookback:train_end])),
        "KNNForecaster": (
            lambda tr, h: KNNFeatureForecaster(input_length=lookback).fit(tr, h),
            lambda m, h: m.predict_hist(series[train_end-lookback:train_end])
        )
    }

    results = []

    for name, (fit_fn, pred_fn) in models.items():
        print(f"Evaluating {name}...")
        try:
            model = fit_fn(train_data, horizon)
            preds = pred_fn(model, horizon)
            if len(preds) < horizon:
                preds = np.pad(preds, (0, horizon - len(preds)), 'edge')
            else:
                preds = preds[:horizon]

            mse = float(np.mean((preds - test_actuals) ** 2))
            mae = float(np.mean(np.abs(preds - test_actuals)))

            pred_diff = preds - train_data[-1]
            intervention_error = float(np.mean((pred_diff - test_intervention) ** 2))

            residuals = test_actuals - preds
            if len(residuals) > 2:
                res_ac = float(np.corrcoef(residuals[:-1], residuals[1:])[0, 1])
            else:
                res_ac = 0.0

            results.append({
                "model": name,
                "mse": round(mse, 4),
                "mae": round(mae, 4),
                "intervention_response_error": round(intervention_error, 4),
                "residual_autocorrelation": round(res_ac, 4)
            })
        except Exception as e:
            print(f"Error evaluating {name}:", e)

    os.makedirs("results", exist_ok=True)
    out_path = "results/results_textbook_validated.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved results to {out_path}")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_textbook_experiment()
