"""Vaknin Contrarian Divergence Strategy (`VakninDivergenceStrategy`).

Quantifies the gap between mass psychological price acceleration (narrative)
and structural subband baseline (objective fundamental trend).
Triggers contrarian mean-reversion signals when narrative overextends.
"""
from __future__ import annotations
import numpy as np

class VakninDivergenceStrategy:
    def __init__(self, lookback: int = 50, z_threshold: float = 2.0):
        self.lookback = int(lookback)
        self.z_threshold = float(z_threshold)

    def generate_signal(self, prices: np.ndarray) -> float:
        """Returns position signal in [-1.0, 1.0]:
        +1.0 = Strong Contrarian Long (Oversold narrative panic)
        -1.0 = Strong Contrarian Short (Overbought narrative euphoria)
         0.0 = Neutral / No Discrepancy
        """
        p = np.asarray(prices, dtype=float).ravel()
        if len(p) < self.lookback:
            return 0.0

        window = p[-self.lookback:]
        # Structural baseline (SMA or median)
        baseline = np.median(window)
        # Volatility / dispersion
        std = np.std(window) + 1.0e-8

        # Current price psychological deviation from structural baseline
        current_price = p[-1]
        z_score = (current_price - baseline) / std

        # Contrarian logic: If price is overextended upward (> +z_threshold), signal short (-1).
        # If price is overextended downward (< -z_threshold), signal long (+1).
        signal = 0.0
        if z_score > self.z_threshold:
            signal = -1.0 # Short overhyped euphoria
        elif z_score < -self.z_threshold:
            signal = 1.0  # Long oversold panic

        return signal
