"""S-40 — Calendar-Aware Level-Free Linear Ensemble for ETTh1 H=720.

Skeleton with TODO markers for implementation. Follows S-20-clean protocol.

Run: python calendar_aware_linear_s40/rolling_arm.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from math import sin, cos, pi

import numpy as np
from sklearn.linear_model import Ridge

# ------------------------------------------------------------------
# Path setup
# ------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data  # noqa: E402
from methods.neural_models import NLinear, DLinear, RLinear  # noqa: E402

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545

# ------------------------------------------------------------------
# Calendar Feature Engineering
# ------------------------------------------------------------------

# TODO S40-1: Load/precompute Chinese holidays for ETTh1 date range.
#   Use `holidays.country_holidays('CN', years=[2016, 2017, 2018])`.
#   Cache in HERE / "calendar_features.npy" (shape (17420, 7)).
#   Precompute once; load from disk on subsequent runs.
CHINESE_HOLIDAYS = None  # placeholder


def _ensure_holidays() -> set:
    """Lazy-load and cache Chinese holiday dates."""
    global CHINESE_HOLIDAYS
    if CHINESE_HOLIDAYS is None:
        import holidays
        years = {2016, 2017, 2018}
        cn_hols = holidays.country_holidays("CN", years=years)
        CHINESE_HOLIDAYS = set(cn_hols.keys())
    return CHINESE_HOLIDAYS


def calendar_features(timestamp) -> np.ndarray:
    """7-dim calendar feature vector for origin timestamp.

    Order: [hour_sin, hour_cos, dow_sin, dow_cos, month_sin, month_cos, holiday].
    All values are deterministic, no RNG.
    """
    holiday_set = _ensure_holidays()
    hod = (timestamp.hour + timestamp.minute / 60.0) / 24.0
    dow = timestamp.weekday() / 7.0
    month = (timestamp.month - 1) / 12.0
    holiday = 1.0 if timestamp.date() in holiday_set else 0.0
    return np.array(
        [sin(2 * pi * hod), cos(2 * pi * hod),
         sin(2 * pi * dow), cos(2 * pi * dow),
         sin(2 * pi * month), cos(2 * pi * month),
         holiday],
        dtype=float,
    )


# ------------------------------------------------------------------
# Calendar-Aware Member Pool
# ------------------------------------------------------------------
# TODO S40-2: Implement calendar-aware forecaster classes in
#   `calendar_members.py` and import them here.
#   Each class must inherit from BaseForecaster and implement:
#     fit(y, *, horizon, origin_idx=None) -> self
#     predict(origin_idx=None) -> np.ndarray(H,)
#   Level-free via last-row anchor subtraction (identical to S-26 NLinear).
#   Calendar features broadcast across horizon; no horizon-shifted calendar.
#
#   Required classes:
#     CalendarNLinear(input_length, ridge_alpha)
#     CalendarDLinear(input_length, kernel_size, ridge_alpha)
#     CalendarRLinear(input_length, ridge_alpha)
#
#   Each class must:
#     1. Concatenate calendar features to the OT window features at fit/predict.
#     2. Maintain level-free prediction (predict returns pred + anchor).
#     3. Be byte-deterministic (no random state; Ridge uses default solver).
#     4. Accept origin_idx kwarg in fit/predict for calendar feature lookup.

# Placeholder imports — replace with actual implementations.
try:
    from calendar_members import (  # type: ignore
        CalendarNLinear,
        CalendarDLinear,
        CalendarRLinear,
    )
    _CALENDAR_MEMBERS_AVAILABLE = True
except ImportError:
    _CALENDAR_MEMBERS_AVAILABLE = False
    CalendarNLinear = None  # type: ignore
    CalendarDLinear = None  # type: ignore
    CalendarRLinear = None  # type: ignore

# ------------------------------------------------------------------
# Member Definitions
# ------------------------------------------------------------------
# TODO S40-3: Replace the placeholder lambdas with actual member factories.
#   Each factory returns a fresh, unfitted forecaster instance.
#   S-26 control members (no calendar) use existing NLinear/DLinear/RLinear.
#   Calendar-aware members use CalendarNLinear/CalendarDLinear/CalendarRLinear.
#
#   Member 0-1: S-26 control pair (no calendar).
#   Member 2-3: calendar-aware NLinear L336 a=1/a=10.
#   Member 4:     calendar-aware NLinear L96  a=1.
#   Member 5:     calendar-aware NLinear L720 a=1.
#   Member 6:     calendar-aware DLinear L96 k25 a=0.
#   Member 7:     calendar-aware RLinear L336 a=0.

MEMBERS = [
    # S-26 controls (no calendar)
    ("nlinear_L336_a1",      lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10",     lambda: NLinear(input_length=336, ridge_alpha=10.0)),
    # Calendar-aware members (TODO: replace with CalendarNLinear once implemented)
    ("nlinear_L336_a1_cal",  lambda: NLinear(input_length=336, ridge_alpha=1.0)),   # TODO S40-3a
    ("nlinear_L336_a10_cal", lambda: NLinear(input_length=336, ridge_alpha=10.0)),  # TODO S40-3b
    ("nlinear_L96_a1_cal",   lambda: NLinear(input_length=96,  ridge_alpha=1.0)),   # TODO S40-3c
    ("nlinear_L720_a1_cal",  lambda: NLinear(input_length=720, ridge_alpha=1.0)),   # TODO S40-3d
    ("dlinear_L96_a0_cal",   lambda: DLinear(input_length=96,  kernel_size=25, ridge_alpha=0.0)),  # TODO S40-3e
    ("rlinear_L336_a0_cal",  lambda: RLinear(input_length=336, ridge_alpha=0.0)),  # TODO S40-3f
]

# ------------------------------------------------------------------
# Prediction Helpers
# ------------------------------------------------------------------


def member_preds_linear(model, series: np.ndarray, starts: np.ndarray,
                        L: int, H: int) -> np.ndarray:
    """Per-window predict via history_ swap.

    For calendar-aware models, set `model._last_origin_idx` before calling
    predict so the model can look up the correct calendar features.
    """
    win_idx = starts[:, None] + np.arange(L)
    windows = series[win_idx]
    origin_indices = starts + L - 1  # global origin index for each window
    preds = []
    for w, oidx in zip(windows, origin_indices):
        orig = model.history_
        try:
            if getattr(orig, "ndim", 1) == 2 and w.ndim == 1:
                model.history_ = w[:, None]
            else:
                model.history_ = w
            if hasattr(model, "_last_origin_idx"):
                model._last_origin_idx = int(oidx)
            preds.append(np.asarray(model.predict(), dtype=float))
        finally:
            model.history_ = orig
    return np.asarray(preds)


def collect_preds(models, series: np.ndarray, origin_starts: np.ndarray) -> np.ndarray:
    """P (n, M, H): member j's predictions for windows starting at starts-L."""
    n = len(origin_starts)
    P = np.empty((n, len(models), HORIZON))
    for j, m in enumerate(models):
        L = m.input_length
        starts = origin_starts - L
        P[:, j, :] = member_preds_linear(m, series, starts, L, HORIZON)
    return P


# ------------------------------------------------------------------
# Stack Map (identical to S-20 — per-horizon ridge, no intercept)
# ------------------------------------------------------------------


def fit_stack_map(P: np.ndarray, A: np.ndarray, alpha: float, fit_intercept: bool = False):
    """Per-horizon single-output ridge stacking over member predictions.

    Intercept is NOT fitted (S-20/S-28 scar).
    """
    n, m, h = P.shape
    coef = np.empty((m, h))
    intercept = np.zeros(h)
    for k in range(h):
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
        if fit_intercept:
            intercept[k] = r.intercept_
    class _Map:
        def predict(self, Pt: np.ndarray) -> np.ndarray:
            return np.einsum("mh,nmh->nh", coef, Pt) + intercept[None, :]
    return _Map()


# ------------------------------------------------------------------
# Rolling Metrics (identical to S-20)
# ------------------------------------------------------------------


def rolling_metrics(preds: np.ndarray, actuals: np.ndarray):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err**2, axis=1))
    mae = float(np.mean(mae_per))
    rmse = float(np.sqrt(np.mean(err**2)))
    disj = {
        f"window_{i+1}": {"mae": float(mae_per[t]), "rmse": float(rmse_per[t])}
        for i, t in enumerate(DISJOINT_STARTS)
    }
    return mae, rmse, disj


# ------------------------------------------------------------------
# Main Protocol
# ------------------------------------------------------------------


def main():
    t_all = time.time()

    # TODO S40-4: Verify calendar-aware members are importable.
    if not _CALENDAR_MEMBERS_AVAILABLE:
        print("ERROR: calendar_members.py not implemented. See TODO S40-2/S40-3.")
        return 1

    pd = get_protocol_data()
    fit_history, eval_series, test = pd.rolling_views()
    train_8545 = fit_history[:TRAIN_END]
    val = fit_history[TRAIN_END:]
    n_val = len(val) - HORIZON + 1
    assert len(train_8545) == 8545 and len(val) == 2880 and len(test) == 2880

    # 1) members frozen on train 8545
    print("fitting 8 members on train 8545 ...")
    models = []
    for name, factory in MEMBERS:
        m = factory()
        m.fit(train_8545, horizon=HORIZON)
        models.append(m)
        print(f"  {name:24s} fitted")

    # 2) val predictions
    val_origin_starts = np.arange(n_val) + TRAIN_END
    print("collecting val predictions ...")
    P_val = collect_preds(models, fit_history, val_origin_starts)
    A_val = np.stack([val[t : t + HORIZON] for t in range(n_val)])

    # per-member val MAE
    for j, (name, _) in enumerate(MEMBERS):
        m = float(np.mean(np.mean(np.abs(P_val[:, j, :] - A_val), axis=1)))
        print(f"  {name:24s} val MAE {m:.4f}")

    # 3) chronological alpha selection inside val
    n_fit = n_val // 2
    P_fit, A_fit = P_val[:n_fit], A_val[:n_fit]
    P_sel, A_sel = P_val[n_fit:], A_val[n_fit:]
    print(f"\nalpha selection: fit on {n_fit} origins, select on {n_val - n_fit} origins ...")
    alphas = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]
    alpha_scores = {}
    for a in alphas:
        r = fit_stack_map(P_fit, A_fit, a)
        sel_mae = float(np.mean(np.mean(np.abs(r.predict(P_sel) - A_sel), axis=1)))
        alpha_scores[a] = sel_mae
        print(f"  alpha {a:8g}: second-half val MAE {sel_mae:.4f}")
    best_alpha = min(alpha_scores, key=alpha_scores.get)
    print(f"selected alpha = {best_alpha}")

    # 4) refit stack map on ALL val origins with selected alpha
    stack = fit_stack_map(P_val, A_val, best_alpha)
    val_mae_full = float(np.mean(np.mean(np.abs(stack.predict(P_val) - A_val), axis=1)))
    print(f"stack-map (alpha={best_alpha}) refit on all val: MAE {val_mae_full:.4f}")

    # 5) frozen test: members re-fit on 11,425
    print("\nre-fitting members on full 11425 ...")
    frozen = []
    for _, factory in MEMBERS:
        m = factory()
        m.fit(fit_history, horizon=HORIZON)
        frozen.append(m)
    n_test = len(test) - HORIZON + 1
    test_origin_starts = np.arange(n_test) + 11425
    print("collecting test predictions ...")
    P_test = collect_preds(frozen, eval_series, test_origin_starts)
    A_test = np.stack([test[t : t + HORIZON] for t in range(n_test)])

    preds_stack = stack.predict(P_test)
    test_mae, test_rmse, disj = rolling_metrics(preds_stack, A_test)

    # baselines
    preds_mean = P_test.mean(axis=1)
    mean_mae, mean_rmse, _ = rolling_metrics(preds_mean, A_test)
    j_best = 0
    best_mae, best_rmse, _ = rolling_metrics(P_test[:, j_best, :], A_test)

    print(f"\n===============================================")
    print(f"CALENDAR-AWARE LINEAR (8 members, per-horizon stack, alpha={best_alpha})")
    print(f"  test rolling: {test_mae:.4f} / {test_rmse:.4f}")
    disj_mean = float(np.mean([disj[f"window_{i+1}"]["mae"] for i in range(4)]))
    print(f"  disjoint: " + ", ".join(f"W{i+1} {disj[f'window_{i+1}']['mae']:.4f}" for i in range(4)))
    print(f"  vs S-26 incumbent 1.9909: {test_mae - 1.9909:+.4f}")
    print(f"  W4 window: {disj['window_4']['mae']:.4f}  (S-26 incumbent in-harness W4 = 1.9579; the value 1.84/1.8427 is the S-20 6-member leaderboard W4)")
    print(f"  disjoint-4 mean: {disj_mean:.4f} (cap 1.9696, S-26 disjoint-4 mean)")
    print(f"baselines (same harness): best member {best_mae:.4f}, equal-mean {mean_mae:.4f}")
    print(f"===============================================")

    # Acceptance checks
    accept = True
    reasons = []
    if test_mae >= 1.9909:
        accept = False
        reasons.append(f"full MAE {test_mae:.4f} >= 1.9909")
    if disj_mean >= 1.9696:
        accept = False
        reasons.append(f"disjoint-4 mean {disj_mean:.4f} >= 1.9696")
    transfer = val_mae_full - test_mae
    if abs(transfer) > 0.02:
        accept = False
        reasons.append(f"transfer delta {transfer:+.4f} > 0.02")

    print(f"\nACCEPT: {accept}")
    if reasons:
        print("REJECT reasons:")
        for r in reasons:
            print(f"  - {r}")

    out = {
        "slice": "S-40",
        "protocol": {
            "members": [n for n, _ in MEMBERS],
            "map": "per-horizon multi-output ridge stacking over member predictions",
            "alpha_selection": "chronological: fit val origins [0,1080), select on [1080,2161)",
            "alpha_candidates": alphas,
            "calendar_features": "hour_sin/cos, dow_sin/cos, month_sin/cos, holiday flag (7-dim, broadcast)",
        },
        "validation": {
            "member_val_mae": {n: round(float(np.mean(np.mean(np.abs(P_val[:, j, :] - A_val), axis=1))), 4)
                               for j, (n, _) in enumerate(MEMBERS)},
            "alpha_scores_second_half": {str(a): round(s, 4) for a, s in alpha_scores.items()},
            "selected_alpha": best_alpha,
            "refit_all_val_mae": round(val_mae_full, 4),
        },
        "test": {
            "rolling_mae": round(test_mae, 4),
            "rolling_rmse": round(test_rmse, 4),
            "disjoint_windows": disj,
            "delta_vs_s26": round(test_mae - 1.9909, 4),
            "transfer_delta": round(transfer, 4),
            "baseline_best_member": round(best_mae, 4),
            "baseline_equal_mean": round(mean_mae, 4),
        },
        "acceptance": {
            "accept": accept,
            "reject_reasons": reasons,
        },
    }
    out_path = HERE / "results_s40.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {out_path} (total {time.time() - t_all:.1f}s)")
    return 0 if accept else 2


if __name__ == "__main__":
    raise SystemExit(main())
