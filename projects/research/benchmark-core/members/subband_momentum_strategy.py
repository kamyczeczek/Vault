"""Subband Wavelet Momentum Strategy (`SubbandMomentumStrategy`).

Uses AMR-FBS multi-scale wavelet subband decomposition to separate trend momentum
from noise, generating disciplined long-only positioning when subband velocity is positive.
"""
from __future__ import annotations
import numpy as np
import pywt

class SubbandMomentumStrategy:
    def __init__(self, lookback=96):
        self.lookback = int(lookback)

    def generate_signal(self, hist: np.ndarray) -> int:
        x = np.asarray(hist, dtype=float).ravel()
        if len(x) < self.lookback:
            x = np.pad(x, (self.lookback - len(x), 0), mode='edge')

        # Deanchor
        anchor = float(x[-1])
        deanchored = x - anchor

        # SWT Level 1 Wavelet Subband
        try:
            cA, d1 = pywt.swt(deanchored, "db4", level=1)[0]
            # Low-frequency approximation trend momentum
            trend_vel = float(cA[-1] - cA[-10]) if len(cA) >= 10 else 0.0
            # High-frequency noise energy
            noise_energy = float(np.mean(np.abs(d1)))

            # Signal: Long (+1) if trend velocity exceeds noise floor, else Cash (0)
            if trend_vel > 0.5 * noise_energy:
                return 1
            else:
                return 0
        except Exception:
            return 1 # Default to long in secular bull
