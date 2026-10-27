"""S-11 rolling arm: residual + RBF arms under the canonical protocol.

Companion to ``run_sweep.py`` (t=0 single-origin). Scores every arm
under the canonical protocol (frozen fit on train.csv, 2,161
stride-1 origins; per-origin history = all rows strictly before the
scored window — the same windows as every rolling-scored config in
the leaderboard). Per the S-08/S-09/S-10 lesson (t=0 ordering does
not transfer), ALL arms advance — t=0 does not select.

Arms:
- ``res_raw_eq_parent`` — identity: SeasonalResidualELM mode="raw"
  parent config; must reproduce the parent ELM rolling 2.3092.
- ``res_m24`` / ``res_m168`` — seasonal-residual tanh ELM.
- ``rbf_raw`` / ``rbf_norm168`` / ``rbf_norm720`` — RBF arms (the
  S-04 norm-asymmetry hypothesis at rolling scale).
- ``rbf_res24`` — combined local-kernel + seasonal-residual arm.
- ``elm_h64_full_fastlags`` — canonical parent (rolling 2.3092).
- ``multirate_R1_2_4`` — S-10 winner (2.2744), the family bar to
  beat.
- ``daily`` / ``persistence`` — fail-loud anchors (2.5491/2.5985).

T0_EXPECTED values are READ from this slice's results.json at run
time (prevention rule S-10 P1: cross-check constants are read, not
transcribed).

Run: python sub_experiments/residual_rbf_sweep/rolling_arm.py
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
from methods.rbf import RBFELM  # noqa: E402
from methods.residual import SeasonalResidualELM  # noqa: E402

DISJOINT_STARTS = (0, 720, 1440, 2160)

ROLLING_ANCHORS = {  # canonical rolling leaderboard (4-decimal)
    "elm_h64_full_fastlags": 2.3092,
    "multirate_R1_2_4": 2.2744,
    "daily": 2.5491,
    "persistence": 2.5985,
}

# arm -> key in this slice's t=0 results.json (read at runtime)
T0_KEYS = {
    "res_raw_eq_parent": "res_tanh_eq_parent",
    "res_m24": "res_tanh_m24",
    "res_m168": "res_tanh_m168",
    "rbf_raw": "rbf_raw",
    "rbf_norm168": "rbf_norm168",
    "rbf_norm720": "rbf_norm720",
    "rbf_res24": "rbf_res24",
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

    # T0 expected numbers READ from this slice's results.json
    sweep = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    t0_expected = {
        arm: sweep[key]["mae"] for arm, key in T0_KEYS.items()
    }

    # --- frozen fits on train.csv ---------------------------------------
    models = {
        "res_raw_eq_parent": SeasonalResidualELM(
            mode="raw", hidden_dim=64, history_fraction=1.0,
            delays=(1, 2, 3, 6, 12)),
        "res_m24": SeasonalResidualELM(period=24),
        "res_m168": SeasonalResidualELM(period=168),
        "rbf_raw": RBFELM(),
        "rbf_norm168": RBFELM(normalize_scale=True, scale_window=168),
        "rbf_norm720": RBFELM(normalize_scale=True, scale_window=720),
        "rbf_res24": RBFELM(residual_period=24),
    }
    for m in models.values():
        m.fit(fit_history, horizon=HORIZON)
    parent = HeuristicLagELM(
        hidden_dim=64, history_fraction=1.0, delays=(1, 2, 3, 6, 12)
    )
    parent.fit(fit_history, horizon=HORIZON)
    mr_winner = MultiRateELM(rates=(1, 2, 4))
    mr_winner.fit(fit_history, horizon=HORIZON)

    def swapper(m):
        def f(hist):
            m.history_ = np.asarray(hist, dtype=float)
            return np.asarray(m.predict())
        return f

    def pers_pred(hist):
        hist = np.asarray(hist, dtype=float)
        return np.full(HORIZON, float(hist[-1]))

    def daily_pred(hist):
        return seasonal_forecast(np.asarray(hist, dtype=float),
                                 HORIZON, "daily")

    arms = {
        "res_raw_eq_parent": swapper(models["res_raw_eq_parent"]),
        "res_m24": swapper(models["res_m24"]),
        "res_m168": swapper(models["res_m168"]),
        "rbf_raw": swapper(models["rbf_raw"]),
        "rbf_norm168": swapper(models["rbf_norm168"]),
        "rbf_norm720": swapper(models["rbf_norm720"]),
        "rbf_res24": swapper(models["rbf_res24"]),
        "elm_h64_full_fastlags": swapper(parent),
        "multirate_R1_2_4": swapper(mr_winner),
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
        "slice": "S-11-rolling",
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

    # rolling identity: res_raw_eq_parent == parent ELM (rolling)
    m_r = by_name["res_raw_eq_parent"]["rolling_mae"]
    m_par = by_name["elm_h64_full_fastlags"]["rolling_mae"]
    ok = abs(m_r - m_par) < 5e-5
    print(f"rolling identity res-raw {m_r:.4f} vs parent {m_par:.4f} -> "
          f"{'OK' if ok else 'FAIL'}")
    if not ok:
        failures.append("rolling_identity_res_raw")

    # t=0 cross-check vs this slice's single-origin numbers (READ)
    for name, expected in t0_expected.items():
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
