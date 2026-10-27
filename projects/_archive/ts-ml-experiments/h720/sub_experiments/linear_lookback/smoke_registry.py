"""S-06 registry-wide smoke test (prevention rule S-05 P1).

Enumerates EVERY entry in ``methods.REGISTRY``, constructs its default
config, fits on ~2k synthetic rows, and predicts the slice's horizon
(720). Catches lost imports / dead constructors after consolidation
refactors (S-05 P1: ``LinearRegression`` was lost in the 2026-08-29
consolidation, leaving DLinear dead-in-HEAD with a NameError at fit).

This is NOT a quality gate — only "imports, constructs, fits,
predicts 720 finite values". Configs recorded per model.

Run: python sub_experiments/linear_lookback/smoke_registry.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))

from methods import REGISTRY  # noqa: E402

HORIZON = 720
N_ROWS = 2200  # > max default input_length (720) + horizon + margin


def synthetic_series(n: int, seed: int = 11) -> np.ndarray:
    """Deterministic AR(1) + daily seasonality + level (finite, 1-D)."""
    rng = np.random.default_rng(seed)
    y = np.zeros(n)
    eps = rng.normal(0.0, 0.1, size=n)
    t = np.arange(n)
    seasonal = 0.5 * np.sin(2.0 * np.pi * t / 24.0)
    for i in range(1, n):
        y[i] = 0.98 * y[i - 1] + eps[i]
    return y + seasonal + 10.0


def main() -> int:
    y = synthetic_series(N_ROWS)
    failures: list[str] = []
    print(f"{'model':<28}{'fit+predict s':>14}  status")
    for name in sorted(REGISTRY):
        cls = REGISTRY[name]
        # Models whose defaults exceed the synthetic budget get an
        # explicit legal config here (fail-loud beats silent skip):
        # CrossFamilyEnsemble defaults to validation_rows=2880 > 2200.
        overrides = {"cross_family_ensemble": {"validation_rows": 1000}}
        kwargs = overrides.get(name, {})
        t0 = time.time()
        try:
            model = cls(**kwargs)
            model.fit(y, horizon=HORIZON)
            pred = model.predict()
            ok = (
                isinstance(pred, np.ndarray)
                and pred.shape == (HORIZON,)
                and np.isfinite(pred).all()
            )
            status = "OK" if ok else f"BAD (shape={getattr(pred, 'shape', None)})"
        except Exception as exc:  # noqa: BLE001 — smoke test reports all failures
            status = f"FAIL ({type(exc).__name__}: {exc})"
            ok = False
        dt = time.time() - t0
        mark = "OK " if ok else "FAIL"
        print(f"{mark}{name:<25}{dt:>12.1f}s  {status}")
        if not ok:
            failures.append(name)

    print(f"\n{len(REGISTRY) - len(failures)}/{len(REGISTRY)} registry models smoke-clean")
    if failures:
        print(f"SMOKE FAILED: {failures}")
        return 1
    print("Registry-wide smoke PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
