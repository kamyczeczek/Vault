import urllib.request
import csv
import numpy as np

def get_stock_data(ticker="SPY", n=2600):
    # Yahoo Finance historical CSV export URL
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1=946684800&period2=1787356800&interval=1d&events=history&includeAdjustedClose=true"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            lines = [line.decode('utf-8') for line in resp.readlines()]
            reader = csv.reader(lines)
            header = next(reader)
            # Find Close or Adj Close index
            close_idx = 4 # Default Adj Close index usually
            for idx, col in enumerate(header):
                if 'Adj Close' in col or 'Close' in col:
                    close_idx = idx

            prices = []
            for row in reader:
                if len(row) > close_idx:
                    try:
                        val = float(row[close_idx])
                        prices.append(val)
                    except ValueError:
                        continue
            arr = np.array(prices, dtype=float)
            if len(arr) >= n:
                return arr[-n:]
            elif len(arr) > 200:
                return arr
    except Exception as e:
        print(f"Yahoo Finance download for {ticker} failed: {e}")

    # Fallback to Geometric Brownian Motion (GBM) with stochastic volatility (GARCH-like)
    print(f"Falling back to synthetic Geometric Brownian Motion for {ticker}")
    rng = np.random.default_rng(42)
    dt = 1/252
    mu = 0.08
    sigma_base = 0.16
    n_pts = max(n, 2600)
    returns = rng.normal((mu - 0.5 * sigma_base**2) * dt, sigma_base * np.sqrt(dt), n_pts)
    # Add volatility clustering (GARCH-like effect)
    vol = sigma_base * np.ones(n_pts)
    for i in range(1, n_pts):
        vol[i] = np.sqrt(0.00001 + 0.85 * vol[i-1]**2 + 0.12 * returns[i-1]**2)
        returns[i] = rng.normal((mu - 0.5 * vol[i]**2) * dt, vol[i] * np.sqrt(dt))

    price_path = 100.0 * np.exp(np.cumsum(returns))
    return price_path[-n:]

if __name__ == "__main__":
    p = get_stock_data("SPY", 500)
    print("Stock data shape:", p.shape, "First 5:", p[:5], "Last 5:", p[-5:])
