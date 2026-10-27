"""Backtest script for Subband Momentum Strategy on Apple stock."""
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from members.subband_momentum_strategy import SubbandMomentumStrategy

def backtest():
    print("Fetching 10-year AAPL data for Subband Momentum Backtest...")
    df = yf.Ticker("AAPL").history(period="10y")
    prices = df['Adj Close'].values if 'Adj Close' in df.columns else df['Close'].values
    prices = np.array(prices, dtype=float)

    lookback = 96
    strategy = SubbandMomentumStrategy(lookback=lookback)

    signals = []
    returns = []

    for i in range(lookback, len(prices)):
        hist = prices[i-lookback:i]
        sig = strategy.generate_signal(hist)
        signals.append(sig)

        ret = (prices[i] - prices[i-1]) / prices[i-1]
        returns.append(sig * ret)

    signals = np.array(signals)
    returns = np.array(returns)

    bh_cum = np.cumprod(1.0 + np.diff(prices)/prices[:-1]) - 1.0
    strat_cum = np.cumprod(1.0 + returns[1:]) - 1.0

    print("\n=== Subband Wavelet Momentum Strategy Backtest ===")
    print(f"  Buy & Hold Total Return : {bh_cum[-1]*100:.2f}%")
    print(f"  Subband Strategy Return : {strat_cum[-1]*100:.2f}%")

    # Plot
    plt.figure(figsize=(12, 6), dpi=150)
    plt.plot(bh_cum * 100, label="Buy & Hold", color="black", linewidth=2)
    plt.plot(strat_cum * 100, label="Subband Momentum Strategy (AMR-FBS Filter)", color="blue", linewidth=2)
    plt.title("Institutional Momentum Strategy via Wavelet Subband Filtering (AAPL 10Y)", fontsize=14, fontweight="bold")
    plt.xlabel("Trading Days", fontsize=12)
    plt.ylabel("Cumulative Return (%)", fontsize=12)
    plt.legend(loc="upper left", frameon=True)
    plt.grid(True, alpha=0.3)

    pathlib.Path("plots").mkdir(exist_ok=True, parents=True)
    out_path = "plots/subband_momentum_backtest.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"Saved subband momentum backtest plot to {out_path}")

if __name__ == "__main__":
    backtest()
