import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import pathlib
import sys
import json

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.knn_feature_forecaster import KNNFeatureForecaster
from members.state_space_hybrid import fit_state_space_hybrid, pred_state_space_hybrid
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_arima, pred_arima, fit_ets, pred_ets, fit_theta, pred_theta

def get_data():
    tk = yf.Ticker("AAPL")
    df = tk.history(period="10y")
    prices = df['Adj Close'].values if 'Adj Close' in df.columns else df['Close'].values
    return np.array(prices, dtype=float)

def run_stress_tests():
    print("Fetching AAPL historical data for advanced stress testing...")
    prices = get_data()
    lookback = 96

    # Test across different horizons: H=5 (weekly), H=24 (monthly), H=60 (quarterly)
    horizons = [5, 24, 60]
    models_def = {
        "AMR-FBS": (fit_amr_fbs, pred_amr_fbs),
        "KNNForecaster": (lambda tr, h: KNNFeatureForecaster(input_length=lookback).fit(tr, h), lambda m, h, hist: m.predict_hist(hist)[:h]),
        "StateSpaceHybrid": (fit_state_space_hybrid, pred_state_space_hybrid),
        "DLinear": (fit_dlinear, pred_dlinear),
        "ARIMA": (fit_arima, pred_arima),
        "ETS": (fit_ets, pred_ets),
        "Theta": (fit_theta, pred_theta)
    }

    results = {}
    test_len = 300
    origins = [len(prices) - test_len + i * 75 for i in range(4)]

    for H in horizons:
        print(f"\n--- Testing Horizon H={H} ---")
        results[f"H_{H}"] = {m: [] for m in models_def}

        for orig in origins:
            train = prices[:orig]
            actual = prices[orig:orig+H]
            if len(actual) < H: continue
            hist = train[-lookback:]

            for name, (fit_fn, pred_fn) in models_def.items():
                try:
                    m = fit_fn(train, H)
                    pred = pred_fn(m, hist)[:H]
                    if len(pred) == H:
                        mae = float(np.mean(np.abs(pred - actual)))
                        # Directional accuracy
                        actual_dir = np.sign(actual - train[-1])
                        pred_dir = np.sign(pred - train[-1])
                        dir_acc = float(np.mean(pred_dir == actual_dir))
                        results[f"H_{H}"][name].append({"mae": mae, "dir_acc": dir_acc})
                except Exception as e:
                    pass

    summary = {}
    for h_key, models in results.items():
        summary[h_key] = {}
        for m, metrics in models.items():
            if len(metrics) > 0:
                mean_mae = float(np.mean([x["mae"] for x in metrics]))
                mean_dir = float(np.mean([x["dir_acc"] for x in metrics]))
                summary[h_key][m] = {"mean_mae": mean_mae, "mean_dir_acc": mean_dir}
                print(f"  [{h_key}] {m:18s} | MAE: {mean_mae:6.2f} | Dir Acc: {mean_dir*100:5.1f}%")

    out_json = "results_apple_stress_tests.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved stress test results to {out_json}")

if __name__ == "__main__":
    run_stress_tests()
