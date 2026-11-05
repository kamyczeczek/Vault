"""S-11 smoke: SeasonalResidualELM + RBFELM gates (synthetic, fail-loud).

Gates (both classes):
1. construct/fit/predict: finite 720-vector across the config grid.
2. determinism: two identical fits -> byte-equal predictions.
3. identity: SeasonalResidualELM(mode="raw") + parent config ==
   HeuristicLagELM byte-identically (the residual decomposition is
   the only moving part).
4. residual decomposition: template + residual reconstructs the
   forecast path (asserted on one synthetic window, fail-loud) for
   SeasonalResidualELM(period=24) AND RBFELM(residual_period=24).
5. fail-loud guards: bad period (<1), bad mode, residual_period<0
   -> ValueError at construct.

Run: python sub_experiments/residual_rbf_sweep/smoke_residual_rbf.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(H720_ROOT))

from methods.neural_models import HeuristicLagELM  # noqa: E402
from methods.rbf import RBFELM  # noqa: E402
from methods.residual import SeasonalResidualELM  # noqa: E402

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


def template(series: np.ndarray, horizon: int, m: int) -> np.ndarray:
    pos = np.arange(len(series) - m, len(series) - m + horizon) % m
    return series[(len(series) - m) + pos]


def main() -> int:
    y = synthetic_series(N_ROWS)
    failures = []

    # ---- SeasonalResidualELM -------------------------------------------
    cfgs = [dict(period=24), dict(period=168), dict(mode="raw"),
            dict(period=24, hidden_dim=256)]
    for cfg in cfgs:
        m = SeasonalResidualELM(**cfg).fit(y, horizon=HORIZON)
        p = m.predict()
        ok = p.shape == (HORIZON,) and np.isfinite(p).all()
        print(f"gate1 residual {cfg}: {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"residual:{cfg}")

    a = SeasonalResidualELM(period=24).fit(y, horizon=HORIZON).predict()
    b = SeasonalResidualELM(period=24).fit(y, horizon=HORIZON).predict()
    ok = np.array_equal(a, b)
    print(f"gate2 residual determinism: {'OK' if ok else 'FAIL'}")
    if not ok:
        failures.append("residual-det")

    sr = SeasonalResidualELM(
        mode="raw", hidden_dim=64, history_fraction=1.0,
        delays=(1, 2, 3, 6, 12),
    ).fit(y, horizon=HORIZON)
    parent = HeuristicLagELM(
        hidden_dim=64, history_fraction=1.0, delays=(1, 2, 3, 6, 12),
    ).fit(y, horizon=HORIZON)
    d = float(np.max(np.abs(sr.predict() - parent.predict())))
    ok = d == 0.0
    print(f"gate3 residual raw==parent: max|diff| {d:.2e} "
          f"-> {'OK' if ok else 'FAIL'}")
    if not ok:
        failures.append("residual-identity")

    m = SeasonalResidualELM(period=24).fit(y, horizon=HORIZON)
    tmpl = template(y, HORIZON, 24)
    # decomposition: forecast = template + modelled deviation;
    # the modelled deviation must reproduce via the internal state
    res_pred = m.predict() - tmpl  # implied residual path
    x = m._lag_features(y, len(y), m.delays, m._anchor(y, len(y), m.q))
    H = np.tanh(x @ m.W_ + m.b_)
    res_direct = np.asarray(m.model_.predict(H))[0]
    d = float(np.max(np.abs(res_pred - res_direct)))
    ok = d < 1e-9  # float round-off from associativity only
    print(f"gate4 residual decomposition: max|diff| {d:.2e} "
          f"-> {'OK' if ok else 'FAIL'}")
    if not ok:
        failures.append("residual-decomp")

    # ---- RBFELM ----------------------------------------------------------
    cfgs = [dict(), dict(normalize_scale=True, scale_window=168),
            dict(normalize_scale=True, scale_window=720),
            dict(residual_period=24), dict(residual_period=168),
            dict(hidden_dim=256), dict(ridge_alpha=0.1)]
    for cfg in cfgs:
        m = RBFELM(**cfg).fit(y, horizon=HORIZON)
        p = m.predict()
        ok = p.shape == (HORIZON,) and np.isfinite(p).all()
        print(f"gate1 rbf {cfg}: sigma {m.sigma_:.3f} "
              f"-> {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"rbf:{cfg}")

    a = RBFELM().fit(y, horizon=HORIZON).predict()
    b = RBFELM().fit(y, horizon=HORIZON).predict()
    ok = np.array_equal(a, b)
    print(f"gate2 rbf determinism: {'OK' if ok else 'FAIL'}")
    if not ok:
        failures.append("rbf-det")

    m = RBFELM(residual_period=24).fit(y, horizon=HORIZON)
    tmpl = template(y, HORIZON, 24)
    # decomposition: predict = readout*scale - anchor + template
    # (the template replaces the anchor as the level carrier)
    pred = m.predict()
    scale = m._window_scale(y, len(y), False, 168)
    anchor = m._anchor(y, len(y), m.q)
    x = m._lag_features(y, len(y), m.delays, anchor)
    H = m._rbf_features(x, m.centers_, m.sigma_)
    manual = (np.asarray(m.model_.predict(H))[0] * scale + tmpl)
    d = float(np.max(np.abs(pred - manual)))
    ok = d < 1e-9
    print(f"gate4 rbf decomposition: max|diff| {d:.2e} "
          f"-> {'OK' if ok else 'FAIL'}")
    if not ok:
        failures.append("rbf-decomp")

    # ---- guards -----------------------------------------------------------
    for label, cls, kw in [
        ("period<1", SeasonalResidualELM, dict(period=0)),
        ("bad mode", SeasonalResidualELM, dict(mode="weird")),
        ("residual_period<0", RBFELM, dict(residual_period=-1)),
    ]:
        try:
            cls(**kw)
            print(f"gate5 {label}: NO ERROR -> FAIL")
            failures.append(f"guard:{label}")
        except ValueError:
            print(f"gate5 {label}: ValueError -> OK")

    if failures:
        print(f"\nSMOKE FAILED: {failures}")
        return 1
    print("\nS-11 SMOKE PASSED (residual + rbf, all gates)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
