import yfinance as yf
import numpy as np
import sys
import pathlib

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from members.financial_hybrid_forecaster import FinancialHybridForecaster
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_arima, pred_arima, fit_ets, pred_ets

def get_apple_data(n=2500):
    tk = yf.Ticker("AAPL")
    df = tk.history(period="10y")
    prices = df['Adj Close'].values if 'Adj Close' in df.columns else df['Close'].values
    return np.array(prices, dtype=float)[-n:]

def evaluate():
    prices = get_apple_data(2500)
    H = 24
    lookback = 96
    test_len = 200
    origins = [len(prices) - test_len + i * 40 for i in range(5)]

    errors = {"FinancialHybrid": [], "DLinear": [], "ARIMA": [], "ETS": []}

    for orig in origins:
        train = prices[:orig]
        actual = prices[orig:orig+H]
        hist = train[-lookback:]

        # Hybrid
        try:
            m = FinancialHybridForecaster(input_length=lookback)
            m.fit(train, H)
            p_hyb = m.predict(hist, H)
            errors["FinancialHybrid"].append(np.mean(np.abs(p_hyb - actual)))
        except Exception as e:
            print("Hybrid error:", e)

        # DLinear
        try:
            m_dl = fit_dlinear(train, H)
            p_dl = pred_dlinear(m_dl, hist)
            errors["DLinear"].append(np.mean(np.abs(p_dl - actual)))
        except Exception:
            pass

        # ARIMA
        try:
            m_ar = fit_arima(train, H)
            p_ar = pred_arima(m_ar, hist)
            errors["ARIMA"].append(np.mean(np.abs(p_ar - actual)))
        except Exception:
            pass

        # ETS
        try:
            m_et = fit_ets(train, H)
            p_et = pred_ets(m_et, hist)
            errors["ETS"].append(np.mean(np.abs(p_et - actual)))
        except Exception:
            pass

    print("=== Financial Hybrid Evaluation on AAPL (5 Origins) ===")
    for m, errs in errors.items():
        if len(errs) > 0:
            print(f"  {m:18s} : Mean MAE {np.mean(errs):.4f}")

if __name__ == "__main__":
    evaluate()
