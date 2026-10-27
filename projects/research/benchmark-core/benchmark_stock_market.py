from __future__ import annotations
import numpy as np
import json
import time
import yfinance as yf
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft, fit_theta, pred_theta, fit_arima, pred_arima, fit_ets, pred_ets

def fetch_stock_data(ticker="SPY", n=2600):
    print(f"Fetching financial data for {ticker} from Yahoo Finance...")
    try:
        df = yf.download(ticker, period="max", interval="1d", progress=False)
        if len(df) > 0:
            prices = df['Close'].dropna().values
            if hasattr(prices, "ndim") and prices.ndim > 1:
                prices = prices[:, 0]
            prices = np.asarray(prices, dtype=float)
            if len(prices) >= n:
                return prices[-n:]
            elif len(prices) > 200:
                # pad or interpolate if slightly shorter
                return prices
    except Exception as e:
        print(f"yfinance fetch failed: {e}")

    # Fallback to Geometric Brownian Motion (GBM) synthetic stock prices
    print("Falling back to synthetic Geometric Brownian Motion (GBM)...")
    rng = np.random.default_rng(42)
    dt = 1/252
    mu = 0.08
    sigma = 0.20
    S0 = 100.0
    returns = rng.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), n)
    prices = S0 * np.exp(np.cumsum(returns))
    return prices

def evaluate_stock_benchmark():
    tickers = ["SPY", "AAPL", "BTC-USD"]
    H = 24
    results = {}

    for ticker in tickers:
        series = fetch_stock_data(ticker, n=1500)
        if len(series) < 200:
            continue

        # Train / Test split
        train = series[:-H]
        test = series[-H:]

        print(f"\n=== Stock Benchmark: {ticker} (H={H}, Train len={len(train)}) ===")

        models = {
            "AMR-FBS": (lambda tr, h: fit_amr_fbs(tr, h), lambda m, h: pred_amr_fbs(m, h)),
            "DLinear": (lambda tr, h: fit_dlinear(tr, h), lambda m, h: pred_dlinear(m, h)),
            "Theta": (lambda tr, h: fit_theta(tr, h), lambda m, h: pred_theta(m, h)),
            "SpectralFFT": (lambda tr, h: fit_fft(tr, h), lambda m, h: pred_fft(m, h)),
            "ARIMA": (lambda tr, h: fit_arima(tr, h), lambda m, h: pred_arima(m, h)),
            "ETS": (lambda tr, h: fit_ets(tr, h), lambda m, h: pred_ets(m, h)),
        }

        task_res = {}
        for name, (fit_fn, pred_fn) in models.items():
            t0 = time.time()
            try:
                model = fit_fn(train, H)
                pred = pred_fn(model, train)
                pred = np.asarray(pred, dtype=float).ravel()[:H]
                mae = float(np.mean(np.abs(pred - test)))
                dt_elapsed = time.time() - t0
                task_res[name] = {"MAE": mae, "time": dt_elapsed}
                print(f"  {name:12s} : MAE {mae:.4f} ({dt_elapsed:.2f}s)")
            except Exception as e:
                print(f"  {name:12s} : ERROR ({e})")
                task_res[name] = {"MAE": None, "error": str(e)}

        results[ticker] = task_res

    with open("results_stock_benchmark.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved stock benchmark results to results_stock_benchmark.json")

if __name__ == "__main__":
    evaluate_stock_benchmark()
