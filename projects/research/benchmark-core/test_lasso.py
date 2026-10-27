import yfinance as yf
import numpy as np
import sys
import pathlib

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from members.lasso_lag_mutation import LassoLagHybrid, fit_lasso_lag, pred_lasso_lag
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_arima, pred_arima

def test_lasso():
    print("Testing LassoLagHybrid mutation model...")
    df = yf.Ticker("AAPL").history(period="2y")
    prices = df['Adj Close'].values if 'Adj Close' in df.columns else df['Close'].values
    prices = np.array(prices, dtype=float)

    H = 24
    lookback = 96
    train = prices[:-H]
    actual = prices[-H:]
    hist = train[-lookback:]

    m = fit_lasso_lag(train, H)
    pred = pred_lasso_lag(m, hist)
    mae = np.mean(np.abs(pred - actual))
    print(f"LassoLagHybrid AAPL H=24 MAE: {mae:.4f}")

if __name__ == "__main__":
    test_lasso()
