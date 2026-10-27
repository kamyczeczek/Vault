"""Backtest script for the Vaknin Contrarian Divergence Strategy on Apple Stock (AAPL)."""
from __future__ import annotations
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import pathlib

from members.vaknin_divergence_strategy import VakninDivergenceStrategy

def run_backtest():
    print("Fetching 10-year AAPL data for Vaknin Strategy Backtest...")
    tk = yf.Ticker("AAPL")
    df = tk.history(period="10y")
    prices = df['Adj Close'].values if 'Adj Close' in df.columns else df['Close'].values
    prices = np.array(prices, dtype=float)

    strategy = VakninDivergenceStrategy(lookback=50, z_threshold=1.8)

    positions = np.zeros(len(prices))
    daily_returns = np.diff(prices) / prices[:-1]

    for i in range(50, len(prices)):
        hist = prices[:i]
        sig = strategy.generate_signal(hist)
        positions[i] = sig

    # Strategy returns: position taken yesterday * return today
    strat_returns = positions[:-1] * daily_returns

    # Cumulative returns
    cum_bh = np.cumprod(1.0 + daily_returns) - 1.0
    cum_strat = np.cumprod(1.0 + strat_returns) - 1.0

    bh_sharpe = np.mean(daily_returns) / (np.std(daily_returns) + 1e-8) * np.sqrt(252)
    strat_sharpe = np.mean(strat_returns) / (np.std(strat_returns) + 1e-8) * np.sqrt(252)

    print(f"\n=== Vaknin Contrarian Divergence Strategy Backtest Summary ===")
    print(f"  Buy & Hold Total Return : {cum_bh[-1]*100:.2f}% | Sharpe: {bh_sharpe:.2f}")
    print(f"  Vaknin Strategy Return  : {cum_strat[-1]*100:.2f}% | Sharpe: {strat_sharpe:.2f}")

    # Plotting
    pathlib.Path("plots").mkdir(exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(cum_bh, label=f"AAPL Buy & Hold (Sharpe: {bh_sharpe:.2f})", color="black", linewidth=1.5)
    plt.plot(cum_strat, label=f"Vaknin Contrarian Strategy (Sharpe: {strat_sharpe:.2f})", color="tab:red", linewidth=2)

    plt.title("Vaknin Contrarian Divergence Strategy vs. Buy & Hold (AAPL, 10-Year)", fontsize=13, fontweight="bold")
    plt.xlabel("Trading Days", fontsize=11)
    plt.ylabel("Cumulative Return", fontsize=11)
    plt.legend(loc="upper left", frameon=True)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out_path = "plots/vaknin_strategy_backtest.png"
    plt.savefig(out_path, dpi=300)
    print(f"Saved Vaknin strategy backtest plot to {out_path}")

if __name__ == "__main__":
    run_backtest()
