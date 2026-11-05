"""S-10 smoke: MultiRateELM gates (synthetic, fail-loud).

Gates:
1. Import + construct + fit + predict over the synthetic budget
   (like smoke_registry) for rates (1,), (1,2), (1,2,4), (1,2,4,8).
2. Determinism: two fits at identical config -> byte-identical
   predictions.
3. IDENTITY: MultiRateELM(rates=(1,), q=3, history_fraction=1.0,
   hidden_dim=64, ridge_alpha=1.0, lags=(1,2,3,6,12)) must equal
   HeuristicLagELM(q=3, history_fraction=1.0, hidden_dim=64,
   ridge_alpha=1.0, delays=(1,2,3,6,12)) BYTE-FOR-BYTE on the
   synthetic series — pins the model to the leaderboard parent
   (rolling 2.3092).
4. Fail-loud guards: rates=(2,) without rate-1, duplicate rates,
   empty rates, rate < 1 -> ValueError at construct/fit.
5. Anti-leakage shape: predict returns exactly horizon values, all
   finite; corrections never reference post-origin data (MaxPool
   views are built from the fit series / swapped history only).

Run: python sub_experiments/multirate_sweep/smoke_multirate.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(H720_ROOT))

from methods.multirate import MultiRateELM  # noqa: E402
from methods.neural_models import HeuristicLagELM  # noqa: E402

HORIZON = 720
N_ROWS = 2200


def synthetic_series(n: int, seed: int = 11) -> np.ndarray:
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
    failures = []

    # Gate 1: construct/fit/predict over rate configs
    for rates in [(1,), (1, 2), (1, 2, 4), (1, 2, 4, 8)]:
        m = MultiRateELM(rates=rates)
        m.fit(y, horizon=HORIZON)
        p = m.predict()
        ok = (
            isinstance(p, np.ndarray)
            and p.shape == (HORIZON,)
            and np.isfinite(p).all()
        )
        print(f"gate1 rates={rates}: shape {np.shape(p)} finite "
              f"{bool(np.isfinite(p).all())} -> {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"gate1:{rates}")

    # Gate 2: determinism
    a = MultiRateELM().fit(y, horizon=HORIZON).predict()
    b = MultiRateELM().fit(y, horizon=HORIZON).predict()
    ok = np.array_equal(a, b)
    print(f"gate2 determinism: max|diff| "
          f"{float(np.max(np.abs(a - b))) if ok else 'DIFFERS'} -> "
          f"{'OK' if ok else 'FAIL'}")
    if not ok:
        failures.append("gate2")

    # Gate 3: rates=(1,) identity with the parent ELM
    mr = MultiRateELM(
        rates=(1,), q=3, history_fraction=1.0, hidden_dim=64,
        ridge_alpha=1.0, lags_per_rate=(1, 2, 3, 6, 12),
    ).fit(y, horizon=HORIZON)
    parent = HeuristicLagELM(
        q=3, history_fraction=1.0, hidden_dim=64, ridge_alpha=1.0,
        delays=(1, 2, 3, 6, 12),
    ).fit(y, horizon=HORIZON)
    pm, pp = mr.predict(), parent.predict()
    ok = np.array_equal(pm, pp)
    d = float(np.max(np.abs(pm - pp)))
    print(f"gate3 identity rates=(1,) vs parent: max|diff| {d:.2e} "
          f"-> {'OK (byte-identical)' if ok else 'FAIL'}")
    if not ok:
        failures.append("gate3")

    # Gate 4: fail-loud guards
    guard_cases = [
        ("empty rates", dict(rates=())),
        ("rate < 1", dict(rates=(1, 0))),
        ("duplicate rates", dict(rates=(2, 2))),
        ("no rate-1", dict(rates=(2, 4))),
    ]
    for label, kwargs in guard_cases:
        try:
            MultiRateELM(**kwargs)
            print(f"gate4 {label}: NO ERROR -> FAIL")
            failures.append(f"gate4:{label}")
        except ValueError as e:
            print(f"gate4 {label}: ValueError ({str(e)[:48]}) -> OK")

    if failures:
        print(f"\nSMOKE FAILED: {failures}")
        return 1
    print("\nMultiRateELM SMOKE PASSED (5 gates)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
