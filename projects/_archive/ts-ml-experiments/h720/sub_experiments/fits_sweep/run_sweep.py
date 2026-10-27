"""Sub-experiment S-07: rolling-origin evaluation of the FITS model.

Scores the frequency-domain forecaster (rFFT of the standardized
lookback -> complex ridge readout to the extended spectrum -> LPF
cutoff -> iRFFT, horizon tail) under the canonical rolling protocol
(frozen fit on train.csv 11,425 rows; 2,161 stride-1 origins),
identical to `linear_lookback/run_sweep.py`.

Cutoff semantics: rFFT bin index of the extended length
(L + 720). Reference bins for L=720 (n_ext = 1440): weekly cycle
(period 168) ~ bin 8.6; daily cycle (24) = bin 60. Cutoffs below 60
remove the daily cycle; `None` keeps the full spectrum.

Acceptance mapping (slices.md S-07):
- >= 3 LPF cutoffs reported -> grid {8, 16, 32, 64, 128, None}
  at L=720 and L=336 (12 configs)
- best config compared vs best ELM (2.3092 rolling) and daily
  seasonal-naive (2.5491) under the same protocol -> fail-loud
  anchors re-scored in-run
- deterministic + predict() == 720 -> smoke_fits.py gate + assert

Outputs: results.json + CONTEXT.md results section.

Run: python sub_experiments/fits_sweep/run_sweep.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, VALIDATION_END, get_protocol_data  # noqa: E402
from methods import HeuristicLagELM, make_forecaster  # noqa: E402
from methods.baselines import Persistence, seasonal_forecast  # noqa: E402
from methods.fits import FITSForecaster  # noqa: E402

SWEEP_DIR = H720_ROOT / "sub_experiments" / "fits_sweep"
DISJOINT_STARTS = (0, 720, 1440, 2160)

# Canonical rolling anchors (S-01, must reproduce exactly)
ROLLING_ANCHORS = {
    "elm_h64_full_fastlags": 2.3092,
    "daily": 2.5491,
    "persistence": 2.5985,
}

CUTOFFS: list[int | None] = [8, 16, 32, 64, 128, None]

CONFIGS = [
    ({"input_length": 720, "ridge_alpha": 1e-3, "cutoff": c}) for c in CUTOFFS
] + [
    ({"input_length": 336, "ridge_alpha": 1e-3, "cutoff": c}) for c in CUTOFFS
]


def mae_rmse(pred: np.ndarray, actual: np.ndarray) -> tuple[float, float]:
    err = actual - pred
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))


def rolling_metrics(per_origin: np.ndarray) -> tuple[float, float, dict]:
    rolling_mae = float(np.mean(per_origin[:, 0]))
    rolling_rmse = float(np.mean(per_origin[:, 1]))
    disjoint = {
        f"window_{i + 1}": {
            "mae": float(per_origin[t, 0]),
            "rmse": float(per_origin[t, 1]),
        }
        for i, t in enumerate(DISJOINT_STARTS)
    }
    return rolling_mae, rolling_rmse, disjoint


def evaluate_model(
    name: str, model, eval_series: np.ndarray, test: np.ndarray
) -> dict:
    n_origins = len(test) - HORIZON + 1  # 2,161
    per_origin = np.empty((n_origins, 2), dtype=float)
    is_persistence = isinstance(model, Persistence)
    for t in range(n_origins):
        hist_end = VALIDATION_END + t
        assert hist_end <= len(eval_series), "history slice overruns eval series"
        hist = eval_series[:hist_end]
        actual = test[t : t + HORIZON]
        model.history_ = hist
        if is_persistence:
            model.last_value_ = float(hist[-1])
        pred = model.predict()
        assert len(pred) == HORIZON, f"{name}: predict returned {len(pred)}"
        per_origin[t] = mae_rmse(pred, actual)
    rolling_mae, rolling_rmse, disjoint = rolling_metrics(per_origin)
    return {
        "model": name,
        "protocol": "rolling stride-1, 2161 origins, frozen fit on train.csv",
        "rolling_mae": round(rolling_mae, 4),
        "rolling_rmse": round(rolling_rmse, 4),
        "disjoint_windows": disjoint,
        "status": "ok",
    }


def evaluate_daily(eval_series: np.ndarray, test: np.ndarray) -> dict:
    n_origins = len(test) - HORIZON + 1
    per_origin = np.empty((n_origins, 2), dtype=float)
    for t in range(n_origins):
        hist = eval_series[: VALIDATION_END + t]
        pred = seasonal_forecast(hist, HORIZON, "daily")
        per_origin[t] = mae_rmse(pred, test[t : t + HORIZON])
    rolling_mae, rolling_rmse, disjoint = rolling_metrics(per_origin)
    return {
        "model": "daily",
        "protocol": "rolling stride-1, 2161 origins, seasonal-naive lag 24",
        "rolling_mae": round(rolling_mae, 4),
        "rolling_rmse": round(rolling_rmse, 4),
        "disjoint_windows": disjoint,
        "status": "ok",
    }


def main() -> int:
    pd_data = get_protocol_data()
    fit_history, eval_series, test = pd_data.rolling_views()

    results: list[dict] = []
    print(f"{'model':<34}{'rolling MAE':>12}{'rolling RMSE':>13}")
    t0 = time.time()
    for cfg in CONFIGS:
        L = cfg["input_length"]
        c = cfg["cutoff"]
        name = f"fits_L{L}_c{'all' if c is None else c}_a1e-3"
        model = FITSForecaster(**cfg)
        model.fit(fit_history, horizon=HORIZON)
        r = evaluate_model(name, model, eval_series, test)
        results.append(r)
        print(f"{r['rolling_mae']:>12.4f}{r['rolling_rmse']:>13.4f}  {name} "
              f"[{time.time() - t0:.0f}s]")

    # Anchor baselines re-scored under the identical protocol (fail-loud)
    elm = HeuristicLagELM(
        hidden_dim=64, history_fraction=1.0, delays=(1, 2, 3, 6, 12)
    )
    elm.fit(fit_history, horizon=HORIZON)
    r = evaluate_model("elm_h64_full_fastlags", elm, eval_series, test)
    results.append(r)
    print(f"{r['rolling_mae']:>12.4f}{r['rolling_rmse']:>13.4f}  "
          f"elm_h64_full_fastlags (anchor)")

    p = make_forecaster("persistence")
    p.fit(fit_history, horizon=HORIZON)
    r = evaluate_model("persistence", p, eval_series, test)
    results.append(r)
    print(f"{r['rolling_mae']:>12.4f}{r['rolling_rmse']:>13.4f}  persistence (anchor)")

    d = evaluate_daily(eval_series, test)
    results.append(d)
    print(f"{d['rolling_mae']:>12.4f}{d['rolling_rmse']:>13.4f}  daily (anchor)")

    # Fail-loud anchor check
    by_name = {r["model"]: r for r in results}
    failures = []
    for name, expected in ROLLING_ANCHORS.items():
        got = by_name[name]["rolling_mae"]
        ok = abs(got - expected) < 5e-5
        print(f"anchor {name}: {got:.4f} expected {expected:.4f} -> "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(name)
    if failures:
        print(f"\nANCHOR CHECK FAILED for {len(failures)} model(s) — aborting")
        return 1

    # Acceptance comparison: best FITS vs ELM and daily (same protocol)
    fits_rows = [r for r in results if r["model"].startswith("fits_")]
    best = min(fits_rows, key=lambda r: r["rolling_mae"])
    comparison = {
        "best_fits": {"model": best["model"],
                      "rolling_mae": best["rolling_mae"],
                      "rolling_rmse": best["rolling_rmse"]},
        "best_elm_rolling": {"model": "elm_h64_full_fastlags",
                             "rolling_mae": by_name["elm_h64_full_fastlags"]["rolling_mae"]},
        "daily_rolling": {"model": "daily",
                          "rolling_mae": by_name["daily"]["rolling_mae"]},
        "fits_beats_elm": best["rolling_mae"] < by_name["elm_h64_full_fastlags"]["rolling_mae"],
        "fits_beats_daily": best["rolling_mae"] < by_name["daily"]["rolling_mae"],
        "fits_beats_current_leader_nlinear_L336": best["rolling_mae"] < 2.0571,
    }

    out = {
        "slice": "S-07",
        "protocol": {
            "fit": "frozen, train.csv 11,425 rows, fit once",
            "origins": 2161,
            "stride": 1,
            "horizon": HORIZON,
            "note": ("FITS: rFFT of standardized window -> complex ridge to "
                     "extended spectrum -> LPF cutoff -> iRFFT; cutoff = "
                     "rFFT bin of extended length (L+720); daily cycle at "
                     "bin 60 for L=720"),
        },
        "results": results,
        "acceptance_comparison": comparison,
    }
    (SWEEP_DIR / "results.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print(f"\nAcceptance comparison: {json.dumps(comparison, indent=2)}")
    print(f"Wrote {SWEEP_DIR / 'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
