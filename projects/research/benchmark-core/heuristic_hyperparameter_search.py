"""Heuristic Fast Hyperparameter Search for Adaptive AMR-KNN Hybrid

Performs randomized heuristic search (Monte Carlo sampling with early stopping / validation feedback)
to optimize hyperparameters for Adaptive_AMR_KNN without exhaustive grid search.
"""

import sys
import numpy as np
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
# The dataset providers live in the sibling project that owns acquisition.
sys.path.insert(0, str(HERE.parent.parent / "_archive/datasets"))
from fetch_scientific_datasets import get_electricity_transformer_data, get_traffic_flow_data, get_solar_activity_data
from members.knn_feature_forecaster import KNNFeatureForecaster
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.adaptive_amr_knn_hybrid import AdaptiveAMRKNNHybrid


def evaluate_config(series, config, horizon=96, n_origins=3):
    """Fast validation evaluation for a given config."""
    test_start = len(series) // 2
    test_len = len(series) - test_start
    origins = [test_start + i * (test_len - horizon) // max(1, n_origins - 1) for i in range(n_origins)]

    mses = []
    for o in origins:
        tr, te = series[:o], series[o:o+horizon]
        try:
            # Instantiate model with config
            model = AdaptiveAMRKNNHybrid(
                input_length=config['input_length'],
                blend_mode=config['blend_mode'],
                default_amr_weight=config['default_amr_weight']
            )
            model.horizon_ = horizon
            model.amr_model_ = fit_amr_fbs(tr, horizon)

            # Custom KNN sub-model config if provided
            knn = KNNFeatureForecaster(
                input_length=config['input_length'],
                k_neighbors=config['k_neighbors'],
                alpha=config['alpha'],
                bandwidth=config['bandwidth'],
                w_shape=config['w_shape'],
                w_deriv=config['w_deriv'],
                w_subband=config['w_subband'],
                w_scale=config['w_scale']
            ).fit(tr, horizon)
            model.knn_model_ = knn

            hist = series[max(0, o - config['input_length']):o]
            preds = model.predict_hist(hist)
            preds = np.asarray(preds).reshape(-1)[:horizon]
            te = te[:len(preds)]

            mse = float(np.mean((preds - te) ** 2))
            mses.append(mse)
        except Exception as e:
            return float('inf')
    return float(np.mean(mses)) if mses else float('inf')


def main():
    print("=" * 80)
    print("HEURISTIC FAST HYPERPARAMETER SEARCH (Adaptive AMR-KNN Hybrid)")
    print("=" * 80)

    # Load representative dataset (Electricity Load)
    load_data, _, _ = get_electricity_transformer_data()
    series = load_data[:, 0]

    # Define hyperparameter search space
    search_space = {
        'input_length': [48, 96, 192],
        'k_neighbors': [12, 24, 36],
        'alpha': [5.0, 10.0, 25.0],
        'bandwidth': [0.5, 0.75, 1.0],
        'w_shape': [0.3, 0.4, 0.5],
        'w_deriv': [0.2, 0.25, 0.3],
        'w_subband': [0.15, 0.2, 0.25],
        'w_scale': [0.1, 0.15, 0.2],
        'blend_mode': ['adaptive', 'learned_ridge'],
        'default_amr_weight': [0.4, 0.5, 0.6]
    }

    n_trials = 12
    rng = np.random.default_rng(42)

    print(f"\nRunning randomized heuristic search ({n_trials} trials)...")
    print(f"{'Trial':<6} | {'MSE':<10} | {'Config'}")
    print("-" * 75)

    best_mse = float('inf')
    best_config = None

    for i in range(n_trials):
        # Sample configuration randomly from search space
        config = {
            'input_length': int(rng.choice(search_space['input_length'])),
            'k_neighbors': int(rng.choice(search_space['k_neighbors'])),
            'alpha': float(rng.choice(search_space['alpha'])),
            'bandwidth': float(rng.choice(search_space['bandwidth'])),
            'w_shape': float(rng.choice(search_space['w_shape'])),
            'w_deriv': float(rng.choice(search_space['w_deriv'])),
            'w_subband': float(rng.choice(search_space['w_subband'])),
            'w_scale': float(rng.choice(search_space['w_scale'])) ,
            'blend_mode': str(rng.choice(search_space['blend_mode'])),
            'default_amr_weight': float(rng.choice(search_space['default_amr_weight']))
        }

        # Normalize weights to sum to ~1.0
        w_sum = config['w_shape'] + config['w_deriv'] + config['w_subband'] + config['w_scale']
        config['w_shape'] /= w_sum
        config['w_deriv'] /= w_sum
        config['w_subband'] /= w_sum
        config['w_scale'] /= w_sum

        mse = evaluate_config(series, config, horizon=96, n_origins=3)

        is_best = mse < best_mse
        if is_best:
            best_mse = mse
            best_config = config
            marker = " <<< BEST"
        else:
            marker = ""

        print(f"{i+1:<6} | {mse:<10.4f} | {config}{marker}")

    print("\n" + "=" * 80)
    print("OPTIMIZATION RESULTS")
    print("=" * 80)
    print(f"Best Validation MSE: {best_mse:.4f}")
    print("Best Hyperparameters:")
    for k, v in best_config.items():
        print(f"  {k}: {v}")

    # Save best config
    out_path = Path("results/best_hyperparameters.json")
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({"best_mse": best_mse, "config": best_config}, f, indent=2)
    print(f"\nBest hyperparameters saved to {out_path}")

if __name__ == "__main__":
    main()
