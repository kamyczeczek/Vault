import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from members.sota_baselines import fit_dlinear, pred_dlinear, fit_arima, pred_arima, fit_ets, pred_ets
from members.financial_hybrid_forecaster import FinancialHybridForecaster

try:
    from members.big_dict_elm import BigDictELM
    _HAS_BIGDICT = True
except Exception:
    _HAS_BIGDICT = False

def get_apple_data(n=2500):
    tk = yf.Ticker("AAPL")
    df = tk.history(period="10y")
    prices = df['Adj Close'].values if 'Adj Close' in df.columns else df['Close'].values
    return np.array(prices, dtype=float)[-n:]

def generate_plot():
    print("Fetching AAPL historical data for plotting...")
    prices = get_apple_data(2500)
    H = 24
    lookback = 96
    test_len = 200
    origins = [len(prices) - test_len + i * 50 for i in range(4)] # 4 clean origins

    fig, axes = plt.subplots(len(origins), 1, figsize=(14, 3.2 * len(origins)), sharex=False)
    if len(origins) == 1: axes = [axes]

    for idx, orig in enumerate(origins):
        train = prices[:orig]
        actual = prices[orig:orig+H]
        if len(actual) < H: continue
        hist = train[-lookback:]

        preds = {}
        # DLinear
        try:
            m = fit_dlinear(train, H)
            preds["DLinear"] = pred_dlinear(m, hist)
        except Exception: pass

        # ARIMA
        try:
            m = fit_arima(train, H)
            preds["ARIMA"] = pred_arima(m, hist)
        except Exception: pass

        # ETS
        try:
            m = fit_ets(train, H)
            preds["ETS"] = pred_ets(m, hist)
        except Exception: pass

        # Financial Hybrid
        try:
            m = FinancialHybridForecaster(input_length=lookback)
            m.fit(train, H)
            preds["FinancialHybrid"] = m.predict(hist, H)
        except Exception: pass

        if _HAS_BIGDICT:
            try:
                m = BigDictELM(input_length=lookback)
                m.fit(train, horizon=H)
                m.history_ = hist
                preds["BigDictELM"] = m.predict()
            except Exception: pass

        ax = axes[idx]
        context = train[-60:]
        time_ctx = np.arange(-len(context), 0)
        time_fut = np.arange(0, H)

        ax.plot(time_ctx, context, color='black', label='History (AAPL)', lw=1.5)
        ax.plot(time_fut, actual, color='dimgray', label='Ground Truth', lw=2, linestyle='--')

        styles = {
            "DLinear": ('tab:blue', '-'),
            "ARIMA": ('tab:orange', '--'),
            "ETS": ('tab:green', ':'),
            "FinancialHybrid": ('tab:red', '-.'),
            "BigDictELM": ('tab:purple', '-')
        }

        for m, p in preds.items():
            if not np.isnan(p).any():
                col, ls = styles.get(m, ('gray', '-'))
                mae = np.mean(np.abs(p - actual))
                ax.plot(time_fut, p, color=col, ls=ls, label=f"{m} (MAE: {mae:.2f})", lw=1.8)

        ax.set_title(f"AAPL Financial Model Comparison — Origin #{idx+1} (Cutoff index {orig})", fontsize=11)
        ax.legend(loc='upper left', fontsize=9, ncol=3)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    pathlib.Path("plots").mkdir(exist_ok=True, parents=True)
    out_path = "plots/apple_financial_models_comparison.png"
    plt.savefig(out_path, dpi=200)
    print(f"Saved financial model comparison plot to {out_path}")

if __name__ == "__main__":
    generate_plot()
