"""Diagnostic: quantify the DLinear raw-scale artifact on synthetic data.

Two constant-shift windows (train on flat, predict on windows with
different levels). A linear decomposition model that tracks level should
predict ~0 deviation from the level. The legacy two-independent-heads
implementation double-predicts the level (each head fits the full
target, then predictions are summed -> ~2x level).

Run: python sub_experiments/dlinear_fix/diagnose.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))

from methods.neural_models import DLinear, NLinear  # noqa: E402


def level_check(name: str, model, train: np.ndarray, test_hist: np.ndarray,
                horizon: int = 720, true_level: float = 0.0) -> None:
    model.fit(train, horizon=horizon)
    model.history_ = test_hist  # frozen fit, new trailing window
    pred = model.predict()
    err = pred - true_level
    print(f"{name:<10} mean_err={np.mean(err):>+9.3f}  "
          f"mae={np.mean(np.abs(err)):.3f}  "
          f"last-96-mean={pred[-96:].mean():>9.3f}")


def main() -> int:
    rng = np.random.default_rng(42)
    n = 12_000
    horizon = 720

    # Flat training series at level 0 (pure noise, no trend)
    train = rng.normal(0.0, 1.0, size=n)
    # Prediction-window histories: distribution-shifted levels (std 1, mean ±20).
    # NOTE: an exactly-constant window would clamp sigma to _SCALE_EPS and
    # explode the standardised features — a known degenerate limit outside
    # ETTh1's data range (window stds there are ~5-15); not a realistic test.
    hist_low = rng.normal(-20.0, 1.0, size=600)
    hist_high = rng.normal(20.0, 1.0, size=600)

    print("=== Level-tracking test (flat train level 0; window level ±20) ===")
    level_check("DLinear", DLinear(input_length=96, kernel_size=25),
                train, hist_low, horizon, true_level=-20.0)
    print()
    print("=== Level-tracking test, high window ===")
    level_check("DLinear", DLinear(input_length=96, kernel_size=25),
                train, hist_high, horizon, true_level=20.0)
    level_check("NLinear", NLinear(input_length=96, ridge_alpha=1.0),
                train, hist_high, horizon, true_level=20.0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
