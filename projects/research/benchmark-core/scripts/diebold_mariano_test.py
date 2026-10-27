"""Diebold-Mariano Statistical Significance Test
Compares forecast errors between baseline models and Adaptive_AMR_KNN (Ours)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# The dataset providers live in the sibling project that owns acquisition.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "_archive/datasets"))

import numpy as np
import json
from scipy import stats
from fetch_scientific_datasets import (
    get_electricity_transformer_data,
    get_traffic_flow_data,
    get_solar_activity_data,
)
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.knn_feature_forecaster import KNNFeatureForecaster
from members.adaptive_amr_knn_hybrid import fit_adaptive_amr_knn, pred_adaptive_amr_knn
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft


def diebold_mariano_test(e1, e2, h=1, power=2):
    """DM test for equal predictive accuracy.

    e1, e2: arrays of point forecast errors (pred - actual).
    h: forecast horizon used as Newey-West truncation lag.
    power: 2 for MSE-based DM, 1 for MAE-based DM.
    """
    e1, e2 = np.asarray(e1, dtype=float), np.asarray(e2, dtype=float)
    if power == 2:
        d = e1**2 - e2**2
    else:
        d = np.abs(e1) - np.abs(e2)

    n = len(d)
    if n < 2:
        return 0.0, 1.0

    mean_d = np.mean(d)

    # HAC variance estimator (Newey-West style)
    max_lag = min(h, n - 1)
    gamma = [np.dot(d[k:], d[:n - k]) / n for k in range(max_lag + 1)]
    variance = gamma[0] + 2 * sum(gamma[1:])

    if variance <= 0 or np.isnan(variance):
        return 0.0, 1.0

    dm_stat = mean_d / np.sqrt(variance / n)
    p_value = 2 * (1 - stats.norm.cdf(abs(dm_stat)))

    return float(dm_stat), float(p_value)


def evaluate_single(fit_fn, pred_fn, series, lookback=96, horizon=96, n_origins=5):
    """Run model and collect raw errors per rolling origin.

    fit_fn(series, lookback) -> model_params
    pred_fn(model_params, test_series) -> predictions (1D array)
    """
    test_start = len(series) // 2
    test_len = len(series) - test_start
    origins = [
        test_start + i * (test_len - horizon) // max(1, n_origins - 1)
        for i in range(n_origins)
    ]

    all_errors = []
    for o in origins:
        tr = series[:o]
        hist = series[max(0, o - lookback):o]
        te = series[o:o + horizon]
        if len(tr) < lookback or len(te) < horizon:
            continue
        try:
            params = fit_fn(tr, horizon)
            preds = pred_fn(params, hist)
            preds = np.asarray(preds).reshape(-1)[:horizon]
            actual = np.asarray(te[:len(preds)])
            errs = preds - actual
            all_errors.extend(errs)
        except Exception as e:
            print(f"    Error at origin {o}: {e}")
    return all_errors

def _pred2(fn):
    """Wrap pred_fn(model, hist) — identity since interface already matches."""
    return fn


def load_series(name):
    """Load time series, handling tuple outputs and 2D arrays.

    Returns 1D numpy array.
    """
    if name == "Electricity":
        s = get_electricity_transformer_data()
        # Tuple: (train_series, test_series, name); train_series may be 2D
        if isinstance(s, tuple):
            s = s[0]
        arr = np.asarray(s)
        # Flatten 2D (N, 2) to 1D by taking first column or flattening
        if arr.ndim == 2:
            arr = arr[:, 0]
        return arr.reshape(-1)
    elif name == "Traffic":
        s = get_traffic_flow_data()
        if isinstance(s, tuple):
            s = s[0]
        return np.asarray(s).reshape(-1)
    else:  # Solar
        s = get_solar_activity_data()
        if isinstance(s, tuple):
            s = s[0]
        return np.asarray(s).reshape(-1)


def main():
    print("=" * 80)
    print("DIEBOLD-MARIANO STATISTICAL SIGNIFICANCE TESTS")
    print("Adaptive_AMR_KNN (Ours) vs each baseline per dataset")
    print("=" * 80)

    # Baseline specs: (name, fit_fn, pred_fn)
    baseline_specs = [
        ("AMR-FBS", fit_amr_fbs, _pred2(pred_amr_fbs)),
        (
            "KNNForecaster",
            lambda s, h: KNNFeatureForecaster(input_length=96).fit(s, h),
            lambda p, t: p.predict_hist(t),
        ),
        ("DLinear", fit_dlinear, _pred2(pred_dlinear)),
        ("SpectralFFT", fit_fft, _pred2(pred_fft)),
    ]

    datasets = [
        ("Electricity_Transformer_Load", load_series("Electricity")),
        ("Traffic_Flow", load_series("Traffic")),
        ("Solar_Activity_Cycle", load_series("Solar")),
    ]

    results = {}

    for dname, series in datasets:
        if series is None or len(series) == 0:
            print(f"\n--- {dname} --- SKIP (data unavailable)")
            continue

        n = len(series)
        print(f"\n--- {dname} --- N={n}, mu={series.mean():.2f}, sigma={series.std():.2f}")

        horizon = 96
        lookback = 96

        # Collect errors for our model
        our_errors = evaluate_single(
            fit_adaptive_amr_knn,
            _pred2(pred_adaptive_amr_knn),
            series,
            lookback,
            horizon,
            n_origins=5,
        )
        ours_mse = float(np.mean(np.asarray(our_errors) ** 2))
        ours_mae = float(np.mean(np.abs(np.asarray(our_errors))))
        print(
            f"  Ours (Adaptive_AMR_KNN): {len(our_errors)} err samples, "
            f"MSE={ours_mse:.4f}, MAE={ours_mae:.4f}"
        )

        results[dname] = {
            "Adaptive_AMR_KNN (Ours)": {
                "mse": ours_mse,
                "mae": ours_mae,
                "n_samples": int(len(our_errors)),
            }
        }

        # Compare against each baseline
        for bname, bfit, bpred in baseline_specs:
            b_errors = evaluate_single(
                bfit, bpred, series, lookback, horizon, n_origins=5
            )
            if len(b_errors) < 10 or len(our_errors) < 10:
                print(f"  {bname}: insufficient samples ({len(b_errors)})")
                continue

            dm_z, p_val = diebold_mariano_test(b_errors, our_errors, h=1, power=2)
            mse_b = float(np.mean(np.asarray(b_errors) ** 2))
            better = "OUR" if ours_mse < mse_b else "BLINE"
            sig = (
                "***"
                if p_val < 0.01
                else "**"
                if p_val < 0.05
                else "*"
                if p_val < 0.10
                else ""
            )
            print(
                f"  {bname:<15} | MSE={mse_b:>10.3f} vs ours {ours_mse:.3f} "
                f"| z={dm_z:>7.3f} p={p_val:.4f} [{better} {sig}]"
            )

            results[dname][bname] = {
                "mse": mse_b,
                "mae": float(np.mean(np.abs(b_errors))),
                "n_samples": int(len(b_errors)),
                "vs_ours_dm_z": dm_z,
                "vs_ours_pval": p_val,
                "winner": better,
                "significant": bool(p_val < 0.05),
            }

    out_path = Path("results/results_dm_tests.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {out_path}")

    # Summary table
    print("\n" + "=" * 80)
    print("SIGNIFICANCE SUMMARY (*** p<0.01, ** p<0.05, * p<0.10)")
    print("=" * 80)
    for dname, dres in results.items():
        print(f"\n{dname}")
        ours_mse = dres.get("Adaptive_AMR_KNN (Ours)", {}).get("mse", "?")
        if isinstance(ours_mse, float):
            print(f"  Ours MSE = {ours_mse:.4f}")
        else:
            print(f"  Ours MSE = {ours_mse}")
        for mname, mres in dres.items():
            if mname == "Adaptive_AMR_KNN (Ours)":
                continue
            if "vs_ours_dm_z" in mres:
                sig_str = "***" if mres["significant"] else ""
                winner = mres["winner"]
                print(
                    f"  {mname:<15} z={mres['vs_ours_dm_z']:.3f} "
                    f"p={mres['vs_ours_pval']:.4f} [{winner}]{sig_str}"
                )


if __name__ == "__main__":
    main()
