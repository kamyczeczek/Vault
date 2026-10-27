"""Market Agent-Based Model (ABM) and Scenario Generator (`market_simulation_demo.py`).

Simulates a heterogeneous agent market (Fundamentalists, Chartists, Noise traders)
and generates alternative future scenarios (bullish growth vs. crash/crisis) from a history fragment.
"""
from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
import pathlib

class FinancialABMSimulator:
    def __init__(self, n_fundamentalists=200, n_chartists=300, intrinsic_value=100.0, seed=42):
        self.n_f = n_fundamentalists
        self.n_c = n_chartists
        self.V0 = intrinsic_value
        np.random.seed(seed)

    def simulate(self, initial_price=100.0, steps=250, sentiment_shock=0.0):
        """Simulate market price trajectory using heterogeneous agent interaction."""
        prices = np.zeros(steps)
        prices[0] = initial_price

        # Agent parameters
        # Fundamentalists reaction speed & noise
        f_weight = 0.05
        # Chartists trend weight and herding tendency
        c_weight = 0.12

        current_price = initial_price
        for t in range(1, steps):
            # Intrinsic anchor with slow drift
            V = self.V0 + np.sin(t / 30.0) * 5.0

            # Fundamental demand (pulls towards value)
            demand_f = f_weight * (V - current_price) / V

            # Chartist demand (momentum + herding)
            if t > 1:
                return_recent = (current_price - prices[t-2]) / prices[t-2]
            else:
                return_recent = 0.0

            # Herding effect: amplify chartist reaction during high volatility or shock
            herding = 1.0 + max(0.0, sentiment_shock + np.random.randn() * 0.1)
            demand_c = c_weight * return_recent * herding

            # Noise traders / liquidity shocks
            noise = np.random.normal(0.0, 0.015)

            # Total excess demand
            excess_demand = demand_f + demand_c + noise

            # Price clearing (exponential price impact)
            current_price = current_price * np.exp(excess_demand)
            current_price = max(current_price, 1.0) # prevent negative prices
            prices[t] = current_price

        return prices

    def generate_scenarios(self, history: np.ndarray, horizon: int = 50, n_scenarios: int = 5):
        """Given a history fragment, simulate different future scenarios (bull vs crash)."""
        last_price = float(history[-1])
        scenarios = {}

        # Scenario 1: Bullish momentum (optimistic sentiment shock)
        scenarios["Bullish Growth"] = self.simulate(initial_price=last_price, steps=horizon, sentiment_shock=-0.5)

        # Scenario 2: Baseline / Normal market
        scenarios["Baseline Market"] = self.simulate(initial_price=last_price, steps=horizon, sentiment_shock=0.0)

        # Scenario 3: Bearish / Panic crash (pessimistic sentiment shock & herding)
        scenarios["Panic Crash"] = self.simulate(initial_price=last_price, steps=horizon, sentiment_shock=1.5)

        return scenarios

if __name__ == "__main__":
    print("Running Financial ABM Market Simulation & Scenario Generator...")
    abm = FinancialABMSimulator()

    # Generate historical context
    history = abm.simulate(initial_price=100.0, steps=150, sentiment_shock=0.0)

    # Generate future scenarios
    future_scenarios = abm.generate_scenarios(history, horizon=60, n_scenarios=3)

    # Plot results
    plt.figure(figsize=(10, 6))
    t_hist = np.arange(len(history))
    t_fut = np.arange(len(history) - 1, len(history) - 1 + len(next(iter(future_scenarios.values()))))

    plt.plot(t_hist, history, label="Historical Context", color="black", lw=2)

    colors = {"Bullish Growth": "green", "Baseline Market": "blue", "Panic Crash": "red"}
    for name, path in future_scenarios.items():
        full_path = np.concatenate([[history[-1]], path[1:]])
        plt.plot(t_fut, full_path, label=name, color=colors.get(name, "gray"), lw=1.5, ls="--")

    plt.axvline(x=len(history)-1, color="orange", linestyle=":", label="Forecast Origin")
    plt.title("Agent-Based Market Simulation: Alternative Future Scenarios")
    plt.xlabel("Time Step")
    plt.ylabel("Asset Price")
    plt.legend()
    plt.grid(True, alpha=0.3)

    pathlib.Path("plots").mkdir(exist_ok=True)
    out_path = "plots/market_abm_scenarios.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved market ABM scenario plot to {out_path}")
