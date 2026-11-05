"""New Dataset Expansion for the Benchmark Suite

Comprehensive dataset catalog across domains referenced in textbooks:
1. Energy/Electricity (Manu Joseph 2024, Ch. 5) - hourly consumption patterns
2. Traffic Flow (Auffarth 2021) - transportation networks, spatial-temporal correlations
3. Financial Markets (Bartos & McCleary 2017) - volatility clustering, regime shifts
4. Weather/Climate (Multiple references) - temperature, precipitation, multi-variate
5. Web Traffic (M4/M5 competition context) - irregular seasonality, promotion effects
6. Healthcare/Biomedical (Applications chapter) - patient monitoring, vital signs
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional

def get_electricity_hourly(n_points: int = 8000, seed: int = 42) -> np.ndarray:
    """
    Synthetic electricity consumption data with daily and weekly patterns.
    Based on Manu Joseph (2024) Ch. 5 discussion of energy forecasting.

    Pattern: 24-hour cycles with weekly seasonality + trend + noise
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_points)

    # Base load with daily pattern (hourly data: 24 points per day)
    daily_cycle = 20 * np.sin(2 * np.pi * t / 24) + \
                  10 * np.sin(4 * np.pi * t / 24)  # Double peak
    weekly_cycle = 5 * np.sin(2 * np.pi * t / (24 * 7))
    trend = 0.001 * t

    # Structural break at 60% to simulate demand shift
    break_mask = t > n_points * 0.6
    break_effect = np.zeros(n_points)
    break_indices = np.where(break_mask)[0]
    if len(break_indices) > 0:
        break_effect[break_indices] = 15 * np.exp(-(t[break_indices] - n_points * 0.6) / 1000)

    noise = rng.normal(0, 2, n_points)

    return (50 + trend + daily_cycle + weekly_cycle + break_effect + noise).astype(float)

def get_traffic_flow(n_points: int = 8000, seed: int = 42) -> np.ndarray:
    """
    Traffic flow data with rush hour patterns and weekend drops.
    Reference: Auffarth (2021) transportation applications.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_points)

    # Rush hours (morning ~9am, evening ~6pm with 24hr cycle)
    morning_rush = 15 * np.exp(-0.5 * ((t % 24 - 8) / 1.5) ** 2)
    evening_rush = 15 * np.exp(-0.5 * ((t % 24 - 17) / 1.5) ** 2)

    # Weekend effect
    is_weekend = (t % 168) >= (5 * 24)
    weekend_factor = np.where(is_weekend, 0.4, 1.0)

    base = 30
    noise = rng.normal(0, 3, n_points)

    return (base * weekend_factor + morning_rush + evening_rush + noise).astype(float)

def get_financial_returns(n_points: int = 8000, seed: int = 42) -> np.ndarray:
    """
    Synthetic financial returns with volatility clustering (GARCH-like).
    Reference: Bartos & McCleary (2017) intervention modeling.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_points)

    # Volatility clustering
    vol = np.zeros(n_points)
    omega = 0.01
    alpha = 0.1
    beta = 0.85

    shocks = rng.normal(0, 1, n_points)
    for i in range(1, n_points):
        vol[i] = omega + alpha * shocks[i-1]**2 + beta * vol[i-1]

    returns = shocks * np.sqrt(vol)

    # Add occasional market crash events
    crash_indices = [n_points // 4, n_points // 2, 3 * n_points // 4]
    for ci in crash_indices:
        if ci < n_points:
            returns[ci:ci+20] -= rng.uniform(5, 15, 20)

    return (100 + np.cumsum(returns) * 10).astype(float)

def get_weather_temperature(n_points: int = 8000, seed: int = 42) -> np.ndarray:
    """
    Daily temperature with strong annual seasonality and weather noise.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_points)

    # Annual cycle (daily data)
    yearly = 15 * np.sin(2 * np.pi * t / 365 - np.pi/2)  # Cold in winter
    trend = 0.002 * t  # Slight warming

    # Random weather fluctuations
    weather_noise = rng.normal(0, 3, n_points)

    return (20 + yearly + trend + weather_noise).astype(float)

def get_web_traffic(n_points: int = 8000, seed: int = 42) -> np.ndarray:
    """
    Web traffic with irregular patterns, promotions, and viral events.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_points)

    # Base pattern
    base = 100

    # Weekly pattern
    weekly = 30 * np.sin(2 * np.pi * t / (24 * 7))

    # Random viral spikes
    spikes = np.zeros(n_points)
    n_spikes = rng.integers(10, 30)
    for _ in range(n_spikes):
        spike_pos = rng.integers(100, n_points - 100)
        spike_mag = rng.uniform(20, 80)
        spike_width = rng.integers(2, 10)
        spikes[spike_pos:spike_pos+spike_width] += spike_mag * np.exp(-0.5 * ((np.arange(spike_width)) / spike_width) ** 2)

    noise = rng.normal(0, 5, n_points)

    return (base + weekly + spikes + noise).astype(float)

def get_healthcare_vitals(n_points: int = 8000, seed: int = 42) -> np.ndarray:
    """
    Patient heart rate with circadian rhythm and medical events.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_points)

    # Circadian rhythm (24h cycle)
    circadian = 10 * np.sin(2 * np.pi * t / 24)

    # Activity levels (higher during day)
    activity = 5 * np.maximum(0, np.sin(2 * np.pi * t / 24))

    # Medical events causing temporary changes
    events = np.zeros(n_points)
    n_events = rng.integers(5, 15)
    for _ in range(n_events):
        event_pos = rng.integers(200, n_points - 200)
        event_dur = rng.integers(50, 200)
        event_mag = rng.uniform(5, 20)
        events[event_pos:event_pos+event_dur] += event_mag

    noise = rng.normal(0, 1.5, n_points)

    return (70 + circadian + activity + events + noise).astype(float)

def generate_all_datasets() -> dict:
    """Generate all synthetic datasets."""
    datasets = {
        "Electricity_Hourly": get_electricity_hourly(),
        "Traffic_Flow": get_traffic_flow(),
        "Financial_Returns": get_financial_returns(),
        "Weather_Temperature": get_weather_temperature(),
        "Web_Traffic": get_web_traffic(),
        "Healthcare_Vitals": get_healthcare_vitals(),
    }
    return datasets

if __name__ == "__main__":
    import json
    datasets = generate_all_datasets()
    for name, data in datasets.items():
        print(f"{name}: length={len(data)}, mean={np.mean(data):.2f}, std={np.std(data):.2f}")

    # Save dataset metadata
    meta = {name: {"length": len(data), "mean": float(np.mean(data)),
                   "std": float(np.std(data)), "min": float(np.min(data)),
                   "max": float(np.max(data))} for name, data in datasets.items()}

    with open("results/dataset_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
    print("\nSaved dataset metadata to results/dataset_metadata.json")
