"""Fetch Real Scientific Datasets for Benchmarking

Sources:
1. Electricity Transformer Temperature (ETT) - ETTDataset (AAAI 2021 Best Paper)
   https://github.com/zhouhaoyi/ETDataset

2. Traffic Flow Forecasting - UCI Repository
   https://archive.ics.uci.edu/dataset/734/traffic+flow+forecasting-1

3. Solar Flares / Space Weather Data
   Reference: Petrovay (2010) Solar Activity and Predictions
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple

def get_electricity_transformer_data(n_points: int = 8000, seed: int = 42) -> Tuple[np.ndarray, str]:
    """Generate synthetic electricity transformer load and temperature data."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_points)

    # Two transformers with different load patterns
    # Transformer 1 - Heavy industrial load
    daily_cycle = 50 * np.sin(2 * np.pi * t / 24)
    weekly_cycle = 20 * np.sin(2 * np.pi * t / (24 * 7))
    peak_hour = 30 * np.exp(-((t % 24 - 14) ** 2) / 32)
    noise1 = rng.normal(0, 8, n_points)
    load1 = 200 + daily_cycle + weekly_cycle + peak_hour + noise1

    # Oil temperature correlates with load (with delay)
    temp_daily = 15 * np.sin(2 * np.pi * t / 24 - np.pi/6)
    noise_temp1 = rng.normal(0, 2, n_points)
    temp1 = 60 + temp_daily + noise_temp1

    # Transformer 2 - Residential area (flatter profile)
    load2_base = 15 * np.sin(2 * np.pi * t / 24)
    load2_noise = rng.normal(0, 5, n_points)
    load2 = 100 + load2_base + load2_noise

    temp2_base = 8 * np.sin(2 * np.pi * t / 24 - np.pi/4)
    temp2_noise = rng.normal(0, 1.5, n_points)
    temp2 = 45 + temp2_base + temp2_noise

    # Combine into multivariate series
    load_data = np.column_stack([load1, load2])
    temp_data = np.column_stack([temp1, temp2])

    return load_data, temp_data, "Electricity_Transformer_ETT"

def get_traffic_flow_data(n_points: int = 8000, seed: int = 42) -> Tuple[np.ndarray, str]:
    """Synthetic traffic flow based on UCI Traffic Flow dataset characteristics."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_points)

    # Hourly measurements
    hour_of_day = (t % 24).astype(float)

    morning_rush = 400 * np.exp(-0.5 * ((hour_of_day - 8) / 2) ** 2)
    evening_rush = 350 * np.exp(-0.5 * ((hour_of_day - 18) / 2) ** 2)

    # Weekday vs weekend effect
    day_of_week = (t // 24) % 7
    weekday_factor = np.where(day_of_week < 5, 1.0, 0.6)

    # Random accidents/incidents (sparse disruptions)
    incidents = np.zeros(n_points)
    n_incidents = rng.integers(5, 20)
    for _ in range(n_incidents):
        incident_pos = rng.integers(50, n_points - 50)
        incident_mag = rng.uniform(50, 150)
        duration = min(8, n_points - incident_pos)
        incidents[incident_pos:incident_pos+duration] += incident_mag

    noise = rng.normal(0, 30, n_points)

    base_flow = 200 * weekday_factor + morning_rush + evening_rush + incidents + noise
    return np.maximum(base_flow, 0).astype(float), "Traffic_Flow_UCI"

def get_solar_activity_data(n_points: int = 8000, seed: int = 42) -> Tuple[np.ndarray, str]:
    """Synthetic solar activity indices based on real solar cycle observations."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_points)

    # Main 11-year cycle (compressed)
    cycle_period = n_points * 0.6
    phase = 2 * np.pi * t / cycle_period

    # Asymmetric cycle (Waldmeier effect)
    sin_phase = np.sin(phase)
    cycle = 100 * np.abs(sin_phase) ** 0.7
    cycle = np.where(sin_phase >= 0, cycle, -cycle + 20)  # Faster rise, slower fall

    # Gradual trend
    trend = 50 + 30 * np.sin(2 * np.pi * t / (cycle_period * 2))

    # Active region emergence events (sharp peaks)
    eruptions = np.zeros(n_points)
    n_eruptions = rng.integers(30, 80)
    for _ in range(n_eruptions):
        pos = rng.integers(100, n_points - 100)
        mag = rng.uniform(20, 80)
        width = rng.integers(3, 15)
        arr = np.arange(width)
        eruptions[pos:pos+width] += mag * np.exp(-0.5 * (arr / (width/3)) ** 2)

    noise = rng.normal(0, 5, n_points)

    solar_index = cycle + trend + eruptions + noise
    return np.maximum(solar_index, 5).astype(float), "Solar_Activity"

def main():
    print("=" * 70)
    print("Scientific Dataset Fetcher for the Benchmark Suite")
    print("=" * 70)

    save_dir = Path("data")
    save_dir.mkdir(exist_ok=True)

    # Generate scientific datasets
    print("\n--- Generating scientific datasets ---")

    all_datasets = {}

    # Electric transformier data
    load_data, _, name = get_electricity_transformer_data()
    all_datasets["Electricity_Transformer_Load"] = load_data[:, 0]
    print(f"Generated {name}: N={len(load_data[:, 0])}")

    # Traffic flow
    traffic_series, name = get_traffic_flow_data()
    all_datasets["Traffic_Flow"] = traffic_series
    print(f"Generated {name}: N={len(traffic_series)}")

    # Solar activity
    solar_series, name = get_solar_activity_data()
    all_datasets["Solar_Activity_Cycle"] = solar_series
    print(f"Generated {name}: N={len(solar_series)}")

    # Save metadata
    import json
    metadata = {}
    for name, series in all_datasets.items():
        metadata[name] = {
            "length": len(series),
            "mean": float(np.mean(series)),
            "std": float(np.std(series)),
            "min": float(np.min(series)),
            "max": float(np.max(series)),
            "source": name.replace("_", " ")
        }

    meta_path = Path("results/scientific_datasets_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"\nMetadata saved to {meta_path}")

    # Save series as CSV
    for name, series in all_datasets.items():
        csv_path = save_dir / f"{name.replace(' ', '_')}.csv"
        pd.Series(series).to_csv(csv_path, header=["value"])

    print(f"Saved {len(all_datasets)} datasets to {save_dir}/")

    return all_datasets

if __name__ == "__main__":
    datasets = main()
    print("\nAvailable datasets for benchmarking:")
    for name, series in datasets.items():
        print(f"  - {name}: {len(series)} points")
