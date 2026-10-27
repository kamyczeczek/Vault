import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.state_space_hybrid import fit_state_space_hybrid, pred_state_space_hybrid
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_theta, pred_theta, fit_arima, pred_arima

def get_apple_data(n=2500):
    tk = yf.Ticker("AAPL")
    df = tk.history(period="10y")
    prices = df['Adj Close'].values if 'Adj Close' in df.columns else df['Close'].values
    return np.array(prices, dtype=float)[-n:]

def main():
    print("Fetching pristine AAPL historical data for multi-origin plotting...")
    prices = get_apple_data(2500)
    H = 24
    lookback = 96
    test_len = 200
    origins = [len(prices) - test_len + i * 50 for i in range(4)]

    fig, axes = plt.subplots(len(origins), 1, figsize=(14, 3.2 * len(origins)), sharex=False)
    if len(origins) == 1: axes = [axes]

    for idx, orig in enumerate(origins):
        train = prices[:orig]
        actual = prices[orig:orig+H]
        if len(actual) < H: continue
        hist = train[-lookback:]

        preds = {}
        # 1. AMR-FBS (Our Crown Jewel)
        try:
            m = fit_amr_fbs(train, H)
            preds["AMR-FBS (Ours)"] = pred_amr_fbs(m, hist)[:H]
        except Exception: pass

        # 2. StateSpaceHybrid
        try:
            m = fit_state_space_hybrid(train, H)
            preds["StateSpaceHybrid"] = pred_state_space_hybrid(m, hist)[:H]
        except Exception: pass

        # 3. DLinear
        try:
            m = fit_dlinear(train, H)
            preds["DLinear"] = pred_dlinear(m, hist)[:H]
        except Exception: pass

        # 4. ARIMA
        try:
            m = fit_arima(train, H)
            preds["ARIMA"] = pred_arima(m, hist)[:H]
        except Exception: pass

        # 5. Theta
        try:
            m = fit_theta(train, H)
            preds["Theta"] = pred_theta(m, hist)[:H]
        except Exception: pass

        ax = axes[idx]
        context = train[-60:]
        time_ctx = np.arange(-len(context), 0)
        time_fut = np.arange(0, H)

        ax.plot(time_ctx, context, color='black', label='Historical AAPL', lw=1.5)
        ax.plot(time_fut, actual, color='dimgray', label='Actual Future Path', lw=2, linestyle='--')

        styles = {
            "AMR-FBS (Ours)": ('tab:red', '-'),
            "StateSpaceHybrid": ('tab:blue', '-.'),
            "DLinear": ('tab:orange', '--'),
            "ARIMA": ('tab:green', ':'),
            "Theta": ('tab:purple', '-')
        }

        for name, p in preds.items():
            if not np.isnan(p).any():
                col, ls = styles.get(name, ('gray', '-'))
                mae = np.mean(np.abs(p - actual))
                ax.plot(time_fut, p, color=col, ls=ls, label=f"{name} (MAE: {mae:.2f})", lw=1.8)

        ax.set_title(f"Pristine Apple Stock Multi-Origin Walk-Forward Forecast — Regime #{idx+1} (Cutoff index {orig})", fontsize=11, fontweight='bold')
        ax.set_ylabel("Price ($)", fontsize=10)
        ax.legend(loc='upper left', fontsize=9, ncol=3)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    pathlib.Path("plots").mkdir(exist_ok=True, parents=True)
    out_path = "plots/pristine_apple_multiorigin.png"
    plt.savefig(out_path, dpi=200)
    print(f"Saved pristine Apple multi-origin plot to {out_path}")

if __name__ == "__main__":
    main()
