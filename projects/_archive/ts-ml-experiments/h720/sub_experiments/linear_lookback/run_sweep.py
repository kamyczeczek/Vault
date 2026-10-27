"""Sub-experiment S-06: long-lookback linear family (L in {336, 720}).

Scores NLinear and the new RLinear (RevIN-standardized window, no
structural transform) plus DLinear L=720 under the canonical rolling
protocol (frozen fit on train.csv 11,425 rows; 2,161 stride-1 origins;
per-origin history = all observed rows strictly before the scored
window), identical to `dlinear_fix/run_sweep.py`.

Design intent (published lookback effect): one alpha per model family
keeps the lookback chain unconfounded —
- NLinear chain L in {96, 336, 720} at ridge_alpha=1.0 (legacy default;
  the L96 row also serves as the NLinear rolling baseline)
- RLinear (new) at L in {336, 720}, both alpha 0 (OLS) and 1 (Ridge)
  to check conditioning
- DLinear L=720 completes the DLinear chain 96 -> 336 (S-05) -> 720

Anchors (fail-loud): ELM / daily / persistence must reproduce their
rolling numbers exactly.

Outputs: results.json + CONTEXT.md results section.

Run: python sub_experiments/linear_lookback/run_sweep.py
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
from methods.neural_models import DLinear, NLinear, RLinear  # noqa: E402

SWEEP_DIR = H720_ROOT / "sub_experiments" / "linear_lookback"
DISJOINT_STARTS = (0, 720, 1440, 2160)

# Canonical rolling anchors (S-01, must reproduce exactly)
ROLLING_ANCHORS = {
    "elm_h64_full_fastlags": 2.3092,
    "daily": 2.5491,
    "persistence": 2.5985,
}

# S-05 rolling numbers reused for the lookback chains (no re-run needed)
S05_DLINEAR = {"L96": 2.1163, "L336": 2.1220}

CONFIGS = [
    ("nlinear", NLinear, {"input_length": 96, "ridge_alpha": 1.0}),
    ("nlinear", NLinear, {"input_length": 336, "ridge_alpha": 1.0}),
    ("nlinear", NLinear, {"input_length": 720, "ridge_alpha": 1.0}),
    ("rlinear", RLinear, {"input_length": 336, "ridge_alpha": 0.0}),
    ("rlinear", RLinear, {"input_length": 336, "ridge_alpha": 1.0}),
    ("rlinear", RLinear, {"input_length": 720, "ridge_alpha": 0.0}),
    ("rlinear", RLinear, {"input_length": 720, "ridge_alpha": 1.0}),
    ("dlinear", DLinear, {"input_length": 720, "kernel_size": 25,
                          "ridge_alpha": 0.0}),
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
    for prefix, cls, cfg in CONFIGS:
        L = cfg["input_length"]
        a = cfg.get("ridge_alpha", 0.0)
        name = f"{prefix}_L{L}" + (f"_a{a:g}" if len(CONFIGS) > 1 else "")
        model = cls(**cfg)
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

    # Lookback chains (acceptance: monotonicity L=96->336->720 recorded)
    def mae_of(prefix: str, L: int, alpha: str | None = None) -> float | None:
        for r in results:
            want = f"{prefix}_L{L}" + (f"_a{alpha}" if alpha else "")
            if r["model"] == want:
                return r["rolling_mae"]
        return None

    chains = {
        "nlinear_alpha1": {
            "L96": mae_of("nlinear", 96, "1"),
            "L336": mae_of("nlinear", 336, "1"),
            "L720": mae_of("nlinear", 720, "1"),
        },
        "dlinear_alpha0_k25": {
            "L96": S05_DLINEAR["L96"],   # S-05 rolling, not re-run
            "L336": S05_DLINEAR["L336"],  # S-05 rolling, not re-run
            "L720": mae_of("dlinear", 720, "0"),
        },
        "rlinear_alpha0": {
            "L336": mae_of("rlinear", 336, "0"),
            "L720": mae_of("rlinear", 720, "0"),
        },
    }

    out = {
        "slice": "S-06",
        "protocol": {
            "fit": "frozen, train.csv 11,425 rows, fit once",
            "origins": 2161,
            "stride": 1,
            "horizon": HORIZON,
            "note": ("NLinear alpha=1.0 chain (legacy default); RLinear new "
                     "model, both alphas; DLinear L720 completes S-05 chain"),
        },
        "results": results,
        "lookback_chains": chains,
    }
    (SWEEP_DIR / "results.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print(f"\nLookback chains: {json.dumps(chains, indent=2)}")
    print(f"Wrote {SWEEP_DIR / 'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
