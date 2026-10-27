import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_theta, pred_theta, fit_arima, pred_arima, fit_ets, pred_ets

try:
    from members.big_dict_elm import BigDictELM
    _HAS_BIGDICT = True
except Exception:
    _HAS_BIGDICT = False

try:
    from members.subband_bigdict import SubbandBigDict
    _HAS_SUBBAND_BIGDICT = True
except Exception:
    _HAS_SUBBAND_BIGDICT = False

def get_apple_data(n=2500):
    tk = yf.Ticker("AAPL")
    df = tk.history(period="10y")
    if 'Adj Close' in df.columns:
        prices = df['Adj Close'].values
    else:
        prices = df['Close'].values
    return np.array(prices, dtype=float)[-n:]

def run_multi_origin_backtest():
    print("Fetching 10-year AAPL historical data...")
    prices = get_apple_data(2500)
    H = 24
    lookback = 96

    # Define rolling origins
    # Test across 5 different rolling cutoff points in the test set
    test_len = 200
    origins = [len(prices) - test_len + i * 40 for i in range(5)] # 5 origins

    models_to_test = ["AMR-FBS", "DLinear", "Theta", "ARIMA", "ETS"]
    if _HAS_BIGDICT: models_to_test.append("BigDictELM")
    if _HAS_SUBBAND_BIGDICT: models_to_test.append("SubbandBigDict")

    errors = {m: [] for m in models_to_test}

    print(f"Running multi-origin evaluation across {len(origins)} origins (H={H})...")

    fig, axes = plt.subplots(len(origins), 1, figsize=(14, 3 * len(origins)), sharex=False)
    if len(origins) == 1: axes = [axes]

    for idx, orig in enumerate(origins):
        train = prices[:orig]
        actual = prices[orig:orig+H]
        if len(actual) < H:
            continue

        hist = train[-lookback:]

        preds = {}
        # Fit & Predict AMR-FBS
        try:
            m_amr = fit_amr_fbs(train, H)
            preds["AMR-FBS"] = pred_amr_fbs(m_amr, hist)
        except Exception as e:
            preds["AMR-FBS"] = np.full(H, np.nan)

        # Fit & Predict DLinear
        try:
            m_dl = fit_dlinear(train, H)
            preds["DLinear"] = pred_dlinear(m_dl, hist)
        except Exception as e:
            preds["DLinear"] = np.full(H, np.nan)

        # Fit & Predict Theta
        try:
            m_th = fit_theta(train, H)
            preds["Theta"] = pred_theta(m_th, hist)
        except Exception as e:
            preds["Theta"] = np.full(H, np.nan)

        # Fit & Predict ARIMA
        try:
            m_ar = fit_arima(train, H)
            preds["ARIMA"] = pred_arima(m_ar, hist)
        except Exception as e:
            preds["ARIMA"] = np.full(H, np.nan)

        # Fit & Predict ETS
        try:
            m_et = fit_ets(train, H)
            preds["ETS"] = pred_ets(m_et, hist)
        except Exception as e:
            preds["ETS"] = np.full(H, np.nan)

        if _HAS_BIGDICT:
            try:
                m_bd = BigDictELM(input_length=lookback)
                m_bd.fit(train, horizon=H)
                m_bd.history_ = hist
                preds["BigDictELM"] = m_bd.predict()
            except Exception:
                pass

        if _HAS_SUBBAND_BIGDICT:
            try:
                m_sb = SubbandBigDict(input_length=lookback)
                m_sb.fit(train, horizon=H)
                m_sb.history_ = hist
                preds["SubbandBigDict"] = m_sb.predict()
            except Exception:
                pass

        # Compute MAE per model for this origin
        for m, p in preds.items():
            if not np.isnan(p).any() and len(p) == H:
                mae = np.mean(np.abs(p - actual))
                errors[m].append(mae)

        # Plotting this origin
        ax = axes[idx]
        context_window = train[-60:]
        time_ctx = np.arange(-len(context_window), 0)
        time_fut = np.arange(0, H)

        ax.plot(time_ctx, context_window, color='black', label='History (AAPL)', lw=1.5)
        ax.plot(time_fut, actual, color='gray', label='Ground Truth', lw=2, linestyle='--')

        styles = {
            "AMR-FBS": ('tab:blue', '-'),
            "DLinear": ('tab:orange', '-.'),
            "Theta": ('tab:green', ':'),
            "ARIMA": ('tab:purple', '--'),
            "ETS": ('tab:brown', ':'),
            "BigDictELM": ('tab:red', '-'),
            "SubbandBigDict": ('tab:pink', '--')
        }

        for m, p in preds.items():
            if not np.isnan(p).any():
                col, ls = styles.get(m, ('gray', '-'))
                ax.plot(time_fut, p, color=col, ls=ls, label=f"{m} (MAE: {np.mean(np.abs(p - actual)):.2f})", lw=1.8)

        ax.set_title(f"AAPL Origin #{idx+1} (Cutoff index {orig})", fontsize=11)
        ax.legend(loc='upper left', fontsize=8, ncol=3)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    pathlib.Path("plots").mkdir(exist_ok=True, parents=True)
    out_path = "plots/apple_multi_origin_forecasts.png"
    plt.savefig(out_path, dpi=200)
    print(f"\nSaved multi-origin Apple forecast plot to {out_path}")

    print("\n=== Multi-Origin Average MAE Summary across AAPL cutoffs ===")
    for m, err_list in errors.items():
        if len(err_list) > 0:
            print(f"  {m:15s} : Mean MAE {np.mean(err_list):.4f} (over {len(err_list)} origins)")

if __name__ == "__main__":
    run_multi_origin_backtest()
