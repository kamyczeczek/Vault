"""S-39 — ZTL-MoE: Zero-Tuning Linear Mixture-of-Experts (ETTh1 H=720).

Fixed 5-expert linear pool + deterministic EWA router + optional
per-horizon Ridge stack with fixed α=10000, no intercept. Zero-tuning:
no grid search, no validation-fitted thresholds, no learned gating weights.

Protocol: S-20-clean.
  Train fit: 8545 rows (train.csv[:8545]).
  Validation: chronological 1080/1081 split inside train.csv.
  Test refit: 11425 rows (train.csv).
  Rolling origins: 2161 stride-1 windows.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Callable, Sequence

import numpy as np
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, DLinear, RLinear
from methods.base import BaseForecaster

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
VAL_END = 11425  # train.csv length


# ---------------------------------------------------------------------------
# Expert 5 — Fourier-lag linear expert
# ---------------------------------------------------------------------------
class FourierLagExpert(BaseForecaster):
    """Deterministic Fourier-lag linear expert (fixed cosine RFF then Ridge).

    View: anchored L336 window, delays D={1,2,3,6,12,24,48,96,168,336},
    deterministic projection φ(τ)=cos(ω·τ) for ω=2πk/24, k=1..4 → 40-dim
    feature vector. Ridge α=100, no intercept.
    """

    def __init__(self, ridge_alpha: float = 100.0):
        self.ridge_alpha = ridge_alpha
        self.delays = np.array([1, 2, 3, 6, 12, 24, 48, 96, 168, 336], dtype=int)
        self.omegas = 2.0 * np.pi * np.arange(1, 5) / 24.0  # k=1..4
        self.input_length = 336

    def fit(self, y, *, horizon: int, target_index: int = 0) -> "FourierLagExpert":
        series = self._as_series(y)
        self._check_horizon(horizon)
        L = self.input_length
        H = horizon
        if len(series) < L + H:
            raise ValueError("insufficient history for FourierLagExpert")

        x_rows, y_rows = [], []
        for end in range(L, len(series) - H + 1):
            window = series[end - L : end]
            anchor = float(window[-1])
            scale = max(float(np.std(window)), self._SCALE_EPS)

            lag_vals = (series[end - self.delays] - anchor) / scale
            phi = np.cos(np.outer(lag_vals, self.omegas)).flatten()
            x_rows.append(phi)
            y_rows.append((series[end : end + H] - anchor) / scale)

        X = np.asarray(x_rows, dtype=float)
        Y = np.asarray(y_rows, dtype=float)
        self.model_ = Ridge(alpha=self.ridge_alpha, fit_intercept=False).fit(X, Y)
        self.history_ = series
        self.target_index = target_index
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        L = self.input_length
        window = self.history_[-L:]
        anchor = float(window[-1])
        scale = max(float(np.std(window)), self._SCALE_EPS)

        lag_vals = (self.history_[-self.delays] - anchor) / scale
        phi = np.cos(np.outer(lag_vals, self.omegas)).flatten()

        out = np.asarray(self.model_.predict([phi])[0], dtype=float)
        return out * scale + anchor


# ---------------------------------------------------------------------------
# Fixed 5-expert pool (zero-tuning: hyperparameters locked by DESIGN.md).
# ---------------------------------------------------------------------------
EXPERT_FACTORIES: list[tuple[str, Callable[[], object]]] = [
    ("nlinear_L336_a1",   lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10",  lambda: NLinear(input_length=336, ridge_alpha=10.0)),
    ("nlinear_L720_a1",   lambda: NLinear(input_length=720, ridge_alpha=1.0)),
    ("rlinear_L336_a0",   lambda: RLinear(input_length=336, ridge_alpha=0.0)),
    ("fourier_lag_L336_a100", lambda: FourierLagExpert(ridge_alpha=100.0)),
]


# ---------------------------------------------------------------------------
# Helpers: history-swap predict, prediction collection.
# ---------------------------------------------------------------------------
def _predict_linear_expert(model, series: np.ndarray, start: int, L: int, H: int) -> np.ndarray:
    """Predict one window via history_ swap (same pattern as S-20)."""
    window = series[start : start + L]
    orig = model.history_
    try:
        model.history_ = window
        return np.asarray(model.predict(), dtype=float)
    finally:
        model.history_ = orig


def collect_expert_preds(models: Sequence[object], series: np.ndarray,
                         origin_starts: np.ndarray) -> np.ndarray:
    """P (n, M, H): expert j's predictions for each origin."""
    n = len(origin_starts)
    P = np.empty((n, len(models), HORIZON), dtype=float)
    for j, m in enumerate(models):
        L = m.input_length
        starts = origin_starts - L
        preds = []
        for s in starts:
            preds.append(_predict_linear_expert(m, series, s, L, HORIZON))
        P[:, j, :] = np.asarray(preds)
    return P


# ---------------------------------------------------------------------------
# EWA Router — deterministic schedule (zero-tuning).
# ---------------------------------------------------------------------------
def ewa_weights(errors: np.ndarray, prev_w: np.ndarray, beta: float = 1.0,
                C: float = 1080.0, t: int = 0) -> np.ndarray:
    """Exponentially weighted average update over per-expert absolute errors.

    errors: shape (M,) — |expert_j - actual| on the most recent validation window.
    prev_w: shape (M,) — previous normalized weights.
    beta: inverse temperature (fixed 1.0).
    C: anneal denominator (fixed 1080 = val-half length).
    t: origin index (0-based within the validation update sequence).
    """
    eta = min(1.0, C / (C + float(t)))
    if not np.isfinite(errors).all():
        return prev_w
    losses = np.exp(-beta * errors)
    w = (1.0 - eta) * prev_w + eta * losses
    s = w.sum()
    if s <= 0 or not np.isfinite(s):
        return np.ones_like(w) / len(w)
    return w / s


def ewa_route(P: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Router forecast: weighted sum of expert predictions.

    P: (n, M, H), w: (M,) -> (n, H).
    """
    return np.einsum("m,nmh->nh", w, P)


# ---------------------------------------------------------------------------
# Optional stacked ridge head (fixed α, no intercept).
# --------------------------------------------------------------------------
def fit_stack_map(P: np.ndarray, A: np.ndarray, alpha: float = 10000.0,
                  fit_intercept: bool = False):
    """Per-horizon single-output ridge stacking over expert forecasts (no intercept)."""
    n, m, h = P.shape
    coef = np.empty((m, h), dtype=float)
    for k in range(h):
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
    class _Map:
        def predict(self, Pt: np.ndarray) -> np.ndarray:
            return np.einsum("mh,nmh->nh", coef, Pt)
    return _Map()


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def rolling_metrics(preds: np.ndarray, actuals: np.ndarray,
                    disjoint_starts: tuple[int, ...] | None = None):
    """Compute MAE, RMSE, and per-window disjoint metrics.

    preds, actuals: (n, H)
    disjoint_starts: offsets within the first axis to report; defaults to
        the protocol-wide DISJOINT_STARTS, clipped to valid range.
    """
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err**2, axis=1))
    mae = float(np.mean(mae_per))
    rmse = float(np.sqrt(np.mean(err**2)))
    starts = disjoint_starts if disjoint_starts is not None else DISJOINT_STARTS
    disj = {}
    for i, t in enumerate(starts):
        if t < len(mae_per):
            disj[f"window_{i+1}"] = {"mae": float(mae_per[t]), "rmse": float(rmse_per[t])}
    return mae, rmse, disj


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    t_all = time.time()
    proto = get_protocol_data()
    train_full = proto.fit_history                 # 11425 rows (train.csv)
    test_series = proto.test_scores()              # 2880 rows

    # --- Split protocol --------------------------------------------------------
    train_series = train_full[:TRAIN_END]          # 0..8544
    val_series = train_full[TRAIN_END:VAL_END]     # 8545..11424

    # --- Build expert pool (fit each on train_series once) ---------------------
    experts = []
    for name, factory in EXPERT_FACTORIES:
        m = factory()
        m.fit(train_series, horizon=HORIZON)
        experts.append((name, m))

    names, models = zip(*experts)
    M = len(models)
    print(f"Experts ready: {list(names)}")

    # --- Validation rolling origins --------------------------------------------
    # Origins are absolute indices into train_full; context up to origin t is
    # train_full[:t], so _predict_linear_expert slices train_full[t-L:t] correctly.
    val_origin_starts = np.arange(TRAIN_END, VAL_END - HORIZON + 1)  # 2161 origins
    n_val = len(val_origin_starts)
    val_A = np.array(
        [train_full[t : t + HORIZON] for t in val_origin_starts],
        dtype=float,
    )

    # Collect expert predictions over validation (full context).
    val_P = collect_expert_preds(models, train_full, val_origin_starts)

    # --- EWA router warm-up on first val half ----------------------------------
    val_fit_end = 1080  # first 1080 origins
    val_fit_P = val_P[:val_fit_end]       # (1080, M, H)
    val_fit_A = val_A[:val_fit_end]       # (1080, H)
    val_select_P = val_P[val_fit_end:]    # (1081, M, H)
    val_select_A = val_A[val_fit_end:]    # (1081, H)

    w = np.ones(M, dtype=float) / M
    for t in range(val_fit_end):
        err_t = np.mean(np.abs(val_fit_P[t] - val_fit_A[t]), axis=1)  # (M,)
        w = ewa_weights(err_t, w, beta=1.0, C=1080.0, t=t)

    print(f"EWA weights after val_fit: {dict(zip(names, w.round(4)))}")

    # Router forecast on val_select
    router_val_pred = ewa_route(val_select_P, w)
    router_val_mae, router_val_rmse, router_val_disj = rolling_metrics(router_val_pred, val_select_A)
    print(f"VAL router MAE={router_val_mae:.4f} RMSE={router_val_rmse:.4f}")

    # --- Optional fixed-α stack head (α=10000, no intercept) --------------------
    stack_map = fit_stack_map(val_fit_P, val_fit_A, alpha=10000.0, fit_intercept=False)
    stack_val_pred = stack_map.predict(val_select_P)
    stack_val_mae, stack_val_rmse, stack_val_disj = rolling_metrics(stack_val_pred, val_select_A)
    print(f"VAL stack  MAE={stack_val_mae:.4f} RMSE={stack_val_rmse:.4f}")

    use_stack = stack_val_mae < router_val_mae - 0.005
    if use_stack:
        print("[INFO] Using stack head for test (improves >0.005 on val_select)")
        test_combine = lambda Pt: stack_map.predict(Pt)
    else:
        print("[INFO] Using EWA router for test")
        test_combine = lambda Pt: ewa_route(Pt, w)

    # --- Test refit ------------------------------------------------------------
    refit_models = []
    for name, factory in EXPERT_FACTORIES:
        m = factory()
        m.fit(train_full, horizon=HORIZON)
        refit_models.append((name, m))

    refit_names, refit_models = zip(*refit_models)
    full_series = np.concatenate([train_full, test_series])
    test_origin_starts = np.arange(VAL_END, VAL_END + len(test_series) - HORIZON + 1)
    n_test = len(test_origin_starts)
    test_A = np.array(
        [full_series[t : t + HORIZON] for t in test_origin_starts],
        dtype=float,
    )

    test_P = collect_expert_preds(refit_models, full_series, test_origin_starts)
    test_pred = test_combine(test_P)

    test_mae, test_rmse, test_disj = rolling_metrics(test_pred, test_A)
    print(f"TEST full MAE={test_mae:.4f} RMSE={test_rmse:.4f}")
    print(f"TEST disjoint-4: {json.dumps(test_disj, indent=2)}")

    # --- Results ---------------------------------------------------------------
    elapsed = round(time.time() - t_all, 3)
    primary_pass = test_mae < 1.9909
    # W4 window MAE (disjoint window start 2160) vs the DEFENDED S-26 incumbent W4.
    # Prior code compared this single-window MAE against 1.9696 (the S-26 disjoint-4 MEAN cap) — a units mismatch.
    # The defended S-26 incumbent in-harness W4 = 1.9579 (derived from the S-26 2-member stack on frozen 11425).
    S26_W4_INCUMBENT = 1.9579
    w4_window_mae = test_disj.get("window_4", {}).get("mae", 999.0)
    w4_pass = w4_window_mae < S26_W4_INCUMBENT  # stability: W4 window must beat the S-26 incumbent's own W4
    transfer_delta = test_mae - router_val_mae

    results = {
        "model": "ZTL-MoE-S39",
        "experts": list(refit_names),
        "horizon": HORIZON,
        "router": "EWA",
        "stack_head_used": use_stack,
        "val_router_mae": round(router_val_mae, 6),
        "val_stack_mae": round(stack_val_mae, 6),
        "test_mae": round(test_mae, 6),
        "test_rmse": round(test_rmse, 6),
        "disjoint_4": test_disj,
        "n_val_origins": n_val,
        "n_test_origins": n_test,
        "elapsed_s": elapsed,
        "plan_impact": "S-39 ZTL-MoE prototype; 5-expert linear pool + deterministic EWA router; Expert 5 Fourier-lag implemented; zero-tuning respected",
    }
    out_path = HERE / "results_s39.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"Wrote {out_path}")

    # --- Harness log ----------------------------------------------------------
    log_path = HERE / "harness.log"
    log_lines = [
        "harness_command: python projects/ts-ml-experiments/h720/sub_experiments/ztl_moe_s39/rolling_arm.py",
        "plan_impact: S-39 ZTL-MoE prototype; 5-expert pool + EWA router; Expert 5 Fourier-lag implemented",
        f"metrics: test_mae={test_mae:.6f} test_rmse={test_rmse:.6f} w4_window_mae={w4_window_mae:.6f} (S-26 incumbent W4 ref 1.9579)",
        f"acceptance: primary={'PASS' if primary_pass else 'FAIL'} w4_stability={'PASS' if w4_pass else 'FAIL'} transfer_delta={transfer_delta:.6f}",
        f"runtime: {elapsed}s",
    ]
    log_path.write_text("\n".join(log_lines))
    print(f"Wrote {log_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
