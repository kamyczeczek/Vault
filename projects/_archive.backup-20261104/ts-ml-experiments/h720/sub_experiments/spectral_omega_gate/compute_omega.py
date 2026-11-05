"""Compute spectral predictability Omega (omega) for time series windows.
Implements omega with DC removal, optional Hann taper, optional anchoring,
one-sided rfft power spectral density, normalized spectral entropy, and Omega = 1 - H/Hmax.
Per RESEARCH/2026-09-12_spectral-predictability-omega.md §5 and §A.4.
"""
from __future__ import annotations
import numpy as np
import argparse

def compute_omega(window: np.ndarray, condition: str = "hann") -> float:
    """Compute spectral predictability Omega for a 1D window.

    Conditioning options:
        - "hann": mean subtraction + Hann window taper (paper-exact default)
        - "none": mean subtraction (DC removal)
        - "anchor": last-value anchoring (x - x[-1])
    """
    x = np.asarray(window, dtype=float).ravel()
    if x.size < 4:
        return float("nan")
    if np.allclose(x.std(), 0.0):
        return 1.0  # Constant series -> zero entropy -> Omega = 1.0

    if condition == "anchor":
        x = x - x[-1]
    elif condition == "hann":
        x = x - x.mean()
        x = x * np.hanning(len(x))
    else:  # "none"
        x = x - x.mean()

    # One-sided rfft power spectral density (DC bin excluded: k=1..K)
    spec = np.fft.rfft(x)
    power = np.abs(spec) ** 2
    if power.size <= 1:
        return 0.0
    # Exclude DC bin 0 (k=0) per paper §A.4
    power_ac = power[1:]
    total_power = power_ac.sum()
    if total_power <= 0 or np.isnan(total_power):
        return 0.0

    p = power_ac / total_power
    p = p[p > 0]
    if p.size == 0:
        return 0.0

    H = -np.sum(p * np.log(p))
    K = len(power_ac)
    H_max = np.log(K) if K > 1 else 1.0
    if H_max <= 0:
        return 0.0

    H_norm = H / H_max
    omega = 1.0 - H_norm
    return float(np.clip(omega, 0.0, 1.0))

def main():
    parser = argparse.ArgumentParser(description="Compute spectral predictability Omega")
    parser.add_argument("--condition", choices=["anchor", "hann", "none"], default="hann")
    args = parser.parse_args()

    rng = np.random.default_rng(42)
    print(f"Condition: {args.condition}")
    for L in [96, 336, 720, 1008]:
        # T > 1000 precondition check per paper §5.3
        precondition_ok = L > 1000
        signal = np.sin(2 * np.pi * np.arange(L) / 24) + 0.1 * rng.standard_normal(L)
        omega = compute_omega(signal, args.condition)
        print(f"Sine wave Omega (L={L}, T>1000: {precondition_ok}): {omega:.4f}")

if __name__ == "__main__":
    main()
