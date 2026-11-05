"""S-10 rolling arm: MultiRateELM under the canonical rolling protocol.

Companion to ``run_sweep.py`` (t=0 single-origin). Scores the top
t=0 configs under the canonical protocol (frozen fit on train.csv,
2,161 stride-1 origins across the full test region; per-origin
history = all rows strictly before the scored window — the same
windows as every rolling-scored config in the leaderboard):

- ``multirate_R1_eq_parent`` — identity arm: MultiRateELM with the
  parent config, rates=(1,). Must reproduce the parent ELM's
  rolling 2.3092 exactly (byte-identical pathway; second rolling
  identity check after the smoke + t=0 gate).
- ``multirate_R1_4``     — best t=0 single (1.5403)
- ``multirate_R1_2_4_8_168`` — best t=0 combo (1.5622)
- ``multirate_R1_2``     — second single, cheap rate-2 refinement
- ``multirate_R1_2_4``   — early combo, 2-rate refinement of R1+4
- ``multirate_R1_4_h128`` — capacity sensitivity of the winner
- ``elm_h64_full_fastlags`` — canonical parent (rolling 2.3092)
- ``daily`` / ``persistence`` — fail-loud anchors (2.5491 / 2.5985)

Acceptance (S-10 spec): the multirate arms must beat the single-rate
ELM parent (2.3092) to count; comparison vs seasonal-naive (daily)
documents win/lose on the full test region.

Construction pattern mirrors S-08/S-09 rolling arms: frozen fit,
per-origin ``history_`` swap + ``predict()``.

Run: python sub_experiments/multirate_sweep/rolling_arm.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, VALIDATION_END, get_protocol_data  # noqa: E402
from methods.baselines import seasonal_forecast  # noqa: E402
from methods.multirate import MultiRateELM  # noqa: E402
from methods.neural_models import HeuristicLagELM  # noqa: E402

DISJOINT_STARTS = (0, 720, 1440, 2160)

ROLLING_ANCHORS = {  # canonical rolling leaderboard (4-decimal)
    "elm_h64_full_fastlags": 2.3092,
    "daily": 2.5491,
    "persistence": 2.5985,
}

T0_EXPECTED = {  # t=0 numbers from run_sweep.py (this slice)
    "multirate_R1_eq_parent": 1.5923,
    "multirate_R1_4": 1.5403,
    "multirate_R1_2_4_8_168": 1.5622,
    "multirate_R1_2": 1.6479,
    "multirate_R1_2_4": 1.5946,
    "multirate_R1_4_h128": 1.6471,
}


def mae_rmse(pred: np.ndarray, actual: np.ndarray) -> tuple[float, float]:
    err = actual - pred
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))


def rolling_score(predict_at, eval_series: np.ndarray, test: np.ndarray):
    """2,161 stride-1 origins; history = all rows before the window."""
    n_origins = len(test) - HORIZON + 1
    assert n_origins == 2161, n_origins
    per_origin = np.empty((n_origins, 2), dtype=float)
    for t in range(n_origins):
        hist = eval_series[: VALIDATION_END + t]
        pred = predict_at(hist)
        assert len(pred) == HORIZON
        per_origin[t] = mae_rmse(pred, test[t : t + HORIZON])
    rolling_mae = float(np.mean(per_origin[:, 0]))
    rolling_rmse = float(np.mean(per_origin[:, 1]))
    disjoint = {
        f"window_{i + 1}": {"mae": float(per_origin[t, 0]),
                            "rmse": float(per_origin[t, 1])}
        for i, t in enumerate(DISJOINT_STARTS)
    }
    return rolling_mae, rolling_rmse, disjoint, per_origin


def main() -> int:
    fit_history, eval_series, test = get_protocol_data().rolling_views()

    # --- frozen fits on train.csv ---------------------------------------
    mr_parent = MultiRateELM(
        rates=(1,), hidden_dim=64, history_fraction=1.0,
        lags_per_rate=(1, 2, 3, 6, 12),
    )
    mr_parent.fit(fit_history, horizon=HORIZON)
    models = {
        "multirate_R1_eq_parent": mr_parent,
        "multirate_R1_4": MultiRateELM(rates=(1, 4)),
        "multirate_R1_2": MultiRateELM(rates=(1, 2)),
        "multirate_R1_2_4": MultiRateELM(rates=(1, 2, 4)),
        "multirate_R1_2_4_8_168": MultiRateELM(rates=(1, 2, 4, 8, 168)),
        "multirate_R1_4_h128": MultiRateELM(rates=(1, 4), hidden_dim=128),
    }
    for m in models.values():
        m.fit(fit_history, horizon=HORIZON)
    parent = HeuristicLagELM(
        hidden_dim=64, history_fraction=1.0, delays=(1, 2, 3, 6, 12)
    )
    parent.fit(fit_history, horizon=HORIZON)

    def swapper(m):
        def f(hist):
            m.history_ = np.asarray(hist, dtype=float)
            return np.asarray(m.predict())
        return f

    def pers_pred(hist):  # predict() reads last_value_, not history_
        hist = np.asarray(hist, dtype=float)
        return np.full(HORIZON, float(hist[-1]))

    def daily_pred(hist):
        return seasonal_forecast(np.asarray(hist, dtype=float),
                                 HORIZON, "daily")

    arms = {
        "multirate_R1_eq_parent": swapper(models["multirate_R1_eq_parent"]),
        "multirate_R1_4": swapper(models["multirate_R1_4"]),
        "multirate_R1_2": swapper(models["multirate_R1_2"]),
        "multirate_R1_2_4": swapper(models["multirate_R1_2_4"]),
        "multirate_R1_2_4_8_168": swapper(models["multirate_R1_2_4_8_168"]),
        "multirate_R1_4_h128": swapper(models["multirate_R1_4_h128"]),
        "elm_h64_full_fastlags": swapper(parent),
        "daily": daily_pred,
        "persistence": pers_pred,
    }

    results, t0_single = [], {}
    for name, predict_at in arms.items():
        t0 = time.time()
        m, r, d, _ = rolling_score(predict_at, eval_series, test)
        results.append({
            "model": name,
            "protocol": "rolling stride-1, 2161 origins, frozen fit",
            "rolling_mae": round(m, 4),
            "rolling_rmse": round(r, 4),
            "disjoint_windows": d,
            "status": "ok",
        })
        t0_single[name] = mae_rmse(predict_at(fit_history), test[:HORIZON])
        print(f"{m:>12.4f}{r:>13.4f}  {name} [{time.time() - t0:.0f}s]")

    out = {
        "slice": "S-10-rolling",
        "protocol": "frozen fit on train.csv; 2,161 stride-1 origins; "
                    "identical windows to every rolling-scored config",
        "results": results,
        "t0_cross_check": {
            k: {"mae": round(v[0], 4), "rmse": round(v[1], 4)}
            for k, v in t0_single.items()
        },
    }
    (HERE / "results_rolling.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )

    # --- fail-loud anchors (rolling) -------------------------------------
    by_name = {r["model"]: r for r in results}
    failures = []
    for name, expected in ROLLING_ANCHORS.items():
        got = by_name[name]["rolling_mae"]
        ok = abs(got - expected) < 5e-5
        print(f"anchor {name}: {got:.4f} expected {expected:.4f} -> "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(name)

    # rolling identity: multirate_R1_eq_parent == parent ELM (rolling)
    m_r1 = by_name["multirate_R1_eq_parent"]["rolling_mae"]
    m_par = by_name["elm_h64_full_fastlags"]["rolling_mae"]
    ok = abs(m_r1 - m_par) < 5e-5
    print(f"rolling identity R=(1,) {m_r1:.4f} vs parent {m_par:.4f} -> "
          f"{'OK' if ok else 'FAIL'}")
    if not ok:
        failures.append("rolling_identity_R1")

    # t=0 cross-check vs this slice's single-origin numbers
    for name, expected in T0_EXPECTED.items():
        got = t0_single[name][0]
        ok = expected is not None and abs(got - expected) < 5e-5
        print(f"t=0 cross {name}: {got:.4f} vs single-origin "
              f"{expected} -> {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"t0:{name}")

    if failures:
        print(f"\nANCHOR CHECK FAILED: {failures} — results_rolling.json "
              "MUST NOT be trusted")
        return 1
    print(f"\nWrote {HERE / 'results_rolling.json'} — all anchors OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
