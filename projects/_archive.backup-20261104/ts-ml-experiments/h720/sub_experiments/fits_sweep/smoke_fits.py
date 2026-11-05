"""FITS smoke test (S-07): synthetic invariants before any real data.

1. Shape/determinism: predict() returns exactly 720 finite values;
   two fits on identical data give byte-identical predictions.
2. Reconstruction sanity: on a pure low-frequency synthetic series
   (daily sinusoid), a cutoff that admits the dominant frequency
   reproduces the continuation with small error (the ridge map is
   near-identity for the dominant frequencies). NOTE: the daily
   cycle (period 24) lives at rFFT bin 60 of the extended length
   1,440 (= 1440/24) — cutoffs below 60 zero it out and flatten the
   forecast (verified: cutoff 48 → MAE 0.3185 flat; cutoff 64 → MAE
   0.0400, at the noise floor).
3. LPF behaves: a 1-frequency cutoff still returns 720 finite values
   (no shape change, only content smoothing).

Run: python sub_experiments/fits_sweep/smoke_fits.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))

from methods.fits import FITSForecaster  # noqa: E402

HORIZON = 720


def synthetic_daily(n: int, seed: int = 5) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    return 10.0 + 0.5 * np.sin(2 * np.pi * t / 24.0) + rng.normal(0, 0.05, n)


def main() -> int:
    y = synthetic_daily(6000)
    failures: list[str] = []

    # 1) shape + determinism
    m1 = FITSForecaster(input_length=720, ridge_alpha=1e-3, cutoff=None)
    m1.fit(y, horizon=HORIZON)
    p1 = m1.predict()
    m2 = FITSForecaster(input_length=720, ridge_alpha=1e-3, cutoff=None)
    m2.fit(y, horizon=HORIZON)
    p2 = m2.predict()
    ok_shape = p1.shape == (HORIZON,) and np.isfinite(p1).all()
    ok_det = np.array_equal(p1, p2)
    print(f"shape/det: shape={p1.shape} finite={bool(np.isfinite(p1).all())} "
          f"byte-identical={ok_det}")
    if not (ok_shape and ok_det):
        failures.append("shape/determinism")

    # 2) reconstruction sanity on daily sinusoid (cutoff admits bin 60)
    m = FITSForecaster(input_length=720, ridge_alpha=1e-6, cutoff=64)
    m.fit(y[:5000], horizon=HORIZON)
    pred = m.predict()
    actual = y[5000 : 5000 + HORIZON]
    err = float(np.mean(np.abs(pred - actual)))
    print(f"daily-sinusoid continuation MAE: {err:.4f} (noise floor ~0.04)")
    if err > 0.15:
        failures.append(f"reconstruction (err {err:.4f})")

    # 3) tiny cutoff still returns 720 finite values
    m = FITSForecaster(input_length=720, ridge_alpha=1e-3, cutoff=1)
    m.fit(y, horizon=HORIZON)
    p = m.predict()
    ok_tiny = p.shape == (HORIZON,) and np.isfinite(p).all()
    print(f"cutoff=1: shape={p.shape} finite={bool(np.isfinite(p).all())}")
    if not ok_tiny:
        failures.append("cutoff=1 shape")

    if failures:
        print(f"\nFITS SMOKE FAILED: {failures}")
        return 1
    print("\nFITS smoke PASSED (shape, determinism, reconstruction, LPF).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
