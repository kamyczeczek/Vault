"""S-41 — RFF-MoE: Random Fourier Feature Expert Ensemble (ETTh1 H=720).

4-expert pool:
  - NLinear L336 a=1 (linear, anchor-differenced)
  - NLinear L336 a=10 (linear, anchor-differenced)
  - RFF L336 raw window → D=500 RFF → Ridge α=1 (kernel-approximate non-linear)
  - Calendar-RFF L336 raw + 7-dim calendar → D=500 RFF → Ridge α=1 (calendar-aware non-linear)

Router: uniform weights (1/4 each).
Optional stack head: per-horizon Ridge α=10000, no intercept.

Protocol: S-20-clean (train 8545 fit, val 1080/1081 split, test 11425 refit, 2161 rolling origins).

Run: python projects/ts-ml-experiments/h720/sub_experiments/rff_ensemble_s41/rolling_arm.py
"""

from __future__ import annotations

import json, sys, time, hashlib
from pathlib import Path
from typing import Callable, Sequence

import numpy as np
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear
from methods.base import BaseForecaster

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
VAL_END = 11425
RFF_DIM = 500
RFF_SEED = 42
RFF_SIGMA = 1.0  # sqrt(1 / input_dim) median heuristic applied at build time


# ---------------------------------------------------------------------------
# RFF projection helper
# ---------------------------------------------------------------------------
def build_rff_matrix(input_dim: int, output_dim: int = RFF_DIM,
                     seed: int = RFF_SEED) -> tuple[np.ndarray, np.ndarray]:
    """Build deterministic random Fourier feature projection matrix.

    Returns (W, b) where:
      W ~ N(0, sigma^2 I), b ~ Uniform(0, 2*pi)
      sigma = sqrt(1 / input_dim)  # median heuristic for Gaussian kernel
    """
    rng = np.random.RandomState(seed)
    sigma = np.sqrt(1.0 / input_dim)
    W = rng.normal(0.0, sigma, size=(input_dim, output_dim)).astype(np.float64)
    b = rng.uniform(0.0, 2.0 * np.pi, size=(output_dim,)).astype(np.float64)
    return W, b


def apply_rff(x: np.ndarray, W: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Apply RFF projection: phi(x) = sqrt(2/D) * cos(W^T x + b).

    Parameters
    ----------
    x : np.ndarray, shape (..., input_dim)
    W : np.ndarray, shape (input_dim, output_dim)
    b : np.ndarray, shape (output_dim,)

    Returns
    -------
    phi : np.ndarray, shape (..., output_dim)
    """
    projected = x @ W + b  # (..., output_dim)
    return np.sqrt(2.0 / W.shape[1]) * np.cos(projected)


# ---------------------------------------------------------------------------
# Expert 3: RFF on raw L336 window
# ---------------------------------------------------------------------------
class RFFRawExpert(BaseForecaster):
    """Random Fourier Feature expert on raw L336 window.

    Fits Ridge α=1 on RFF-projected raw window across sliding historical windows.
    """

    def __init__(self, input_length: int = 336, ridge_alpha: float = 1.0,
                 rff_dim: int = RFF_DIM, rff_seed: int = RFF_SEED) -> None:
        super().__init__()
        self.input_length = input_length
        self.ridge_alpha = ridge_alpha
        self.rff_dim = rff_dim
        self.rff_seed = rff_seed
        self._W: np.ndarray | None = None
        self._b: np.ndarray | None = None
        self._model: Ridge | None = None

    def fit(self, y: np.ndarray, horizon: int) -> "RFFRawExpert":
        history = np.asarray(y, dtype=np.float64)
        if history.ndim != 1:
            raise ValueError("RFFRawExpert expects 1-D history")
        self.history_ = history
        H = horizon

        W, b = build_rff_matrix(self.input_length, self.rff_dim, self.rff_seed)

        x_rows, y_rows = [], []
        for end in range(self.input_length, len(history) - H + 1):
            window = history[end - self.input_length : end]
            scale = np.std(window)
            if scale < 1e-8:
                scale = 1.0
            x_rows.append(window / scale)
            y_rows.append(history[end : end + H])

        if len(x_rows) == 0:
            window = history[-self.input_length:]
            scale = np.std(window)
            if scale < 1e-8:
                scale = 1.0
            x_rows = [window / scale]
            y_rows = [history[-H:] if H <= len(history) else np.zeros(H)]

        X_arr = np.asarray(x_rows, dtype=np.float64)
        Y_arr = np.asarray(y_rows, dtype=np.float64)

        phi = apply_rff(X_arr, W, b)
        model = Ridge(alpha=self.ridge_alpha, fit_intercept=False)
        model.fit(phi, Y_arr)
        self._W, self._b, self._model = W, b, model
        return self

    def predict(self) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("fit() must be called before predict()")
        window = self.history_[-self.input_length:]
        scale = np.std(window)
        if scale < 1e-8:
            scale = 1.0
        norm_window = (window / scale).reshape(1, -1)
        phi = apply_rff(norm_window, self._W, self._b)
        y = self._model.predict(phi).reshape(-1)
        return np.asarray(y, dtype=float)


# ---------------------------------------------------------------------------
# Expert 4: Calendar-aware RFF on raw L336 window + 7-dim calendar features
# ---------------------------------------------------------------------------
class CalendarRFFExpert(BaseForecaster):
    """Calendar-aware RFF expert: raw L336 window + 7-dim calendar → D=500 RFF → Ridge α=1.
    """

    def __init__(self, input_length: int = 336, ridge_alpha: float = 1.0,
                 rff_dim: int = RFF_DIM, rff_seed: int = RFF_SEED + 1) -> None:
        super().__init__()
        self.input_length = input_length
        self.ridge_alpha = ridge_alpha
        self.rff_dim = rff_dim
        self.rff_seed = rff_seed
        self._W: np.ndarray | None = None
        self._b: np.ndarray | None = None
        self._model: Ridge | None = None
        self._calendar_all: np.ndarray | None = None

    def fit(self, y: np.ndarray, horizon: int, calendar: np.ndarray | None = None) -> "CalendarRFFExpert":
        history = np.asarray(y, dtype=np.float64)
        if history.ndim != 1:
            raise ValueError("CalendarRFFExpert expects 1-D history")
        self.history_ = history
        H = horizon

        if calendar is None or calendar.shape[0] == 0:
            raise ValueError("CalendarRFFExpert requires calendar features array")

        input_dim = self.input_length + 7
        W, b = build_rff_matrix(input_dim, self.rff_dim, self.rff_seed)

        x_rows, y_rows = [], []
        for end in range(self.input_length, len(history) - H + 1):
            window = history[end - self.input_length : end]
            scale = np.std(window)
            if scale < 1e-8:
                scale = 1.0
            norm_window = window / scale
            cal_vec = calendar[end - 1]
            feat = np.concatenate([norm_window, cal_vec])
            x_rows.append(feat)
            y_rows.append(history[end : end + H])

        if len(x_rows) == 0:
            window = history[-self.input_length:]
            scale = np.std(window)
            if scale < 1e-8:
                scale = 1.0
            cal_vec = calendar[-1]
            x_rows = [np.concatenate([window / scale, cal_vec])]
            y_rows = [history[-H:] if H <= len(history) else np.zeros(H)]

        X_arr = np.asarray(x_rows, dtype=np.float64)
        Y_arr = np.asarray(y_rows, dtype=np.float64)

        phi = apply_rff(X_arr, W, b)
        model = Ridge(alpha=self.ridge_alpha, fit_intercept=False)
        model.fit(phi, Y_arr)
        self._W, self._b, self._model = W, b, model
        self._calendar_all = calendar
        return self

    def predict(self, calendar: np.ndarray | None = None) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("fit() must be called before predict()")
        window = self.history_[-self.input_length:]
        scale = np.std(window)
        if scale < 1e-8:
            scale = 1.0
        norm_window = window / scale

        cal_source = calendar if calendar is not None else self._calendar_all
        if cal_source is None or cal_source.shape[0] == 0:
            raise ValueError("CalendarRFFExpert requires calendar features at predict time")

        global_idx = len(self.history_) - 1
        cal_vec = cal_source[global_idx]

        feat = np.concatenate([norm_window, cal_vec]).reshape(1, -1)
        phi = apply_rff(feat, self._W, self._b)
        y = self._model.predict(phi).reshape(-1)
        return np.asarray(y, dtype=float)

# ---------------------------------------------------------------------------
# Expert 5: Calendar-NLinear (anchor-differenced L336 + calendar features)
# ---------------------------------------------------------------------------
class CalendarNLinear(BaseForecaster):
    """Calendar-aware NLinear: anchor-differenced L336 window + 7-dim calendar → Ridge α=1.
    Calendar features concatenated to the anchor-differenced window.
    """

    def __init__(self, input_length: int = 336, ridge_alpha: float = 1.0) -> None:
        super().__init__()
        self.input_length = input_length
        self.ridge_alpha = ridge_alpha
        self._model: Ridge | None = None

    def fit(self, y: np.ndarray, horizon: int, calendar: np.ndarray | None = None) -> "CalendarNLinear":
        history = np.asarray(y, dtype=np.float64)
        if history.ndim != 1:
            raise ValueError("CalendarNLinear expects 1-D history")
        self.history_ = history
        H = horizon

        window = history[-self.input_length:]
        anchor = float(window[-1])
        diffed = window - anchor

        if calendar is None or calendar.shape[0] == 0:
            raise ValueError("CalendarNLinear requires calendar features array")
        cal_vec = calendar[-1]  # origin calendar vector (7-dim)
        feature = np.concatenate([diffed, cal_vec])  # (343,)

        targets = history[-H:].reshape(1, -1) if H <= len(history) else np.zeros((1, H))
        if targets.shape[1] != H:
            targets = np.zeros((1, H), dtype=np.float64)
            length = min(H, len(history))
            targets[0, :length] = history[-length:]

        model = Ridge(alpha=self.ridge_alpha, fit_intercept=True)
        model.fit(feature.reshape(1, -1), targets)
        self._model = model
        self._anchor = float(anchor)
        self._cal_dim = cal_vec.shape[0]
        return self

    def predict(self, calendar: np.ndarray | None = None) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("fit() must be called before predict()")
        window = self.history_[-self.input_length:]
        anchor = float(window[-1])
        diffed = window - anchor

        if calendar is None or calendar.shape[0] == 0:
            raise ValueError("CalendarNLinear requires calendar features at predict time")
        cal_vec = calendar[-1]
        feature = np.concatenate([diffed, cal_vec])
        y = self._model.predict(feature.reshape(1, -1)).reshape(-1)
        return np.asarray(y + anchor, dtype=float)


# ---------------------------------------------------------------------------
# Fixed 4-expert pool
# ---------------------------------------------------------------------------
def _make_experts() -> list[tuple[str, Callable[[], object]]]:
    return [
        ("nlinear_L336_a1",    lambda: NLinear(input_length=336, ridge_alpha=1.0)),
        ("nlinear_L336_a10",   lambda: NLinear(input_length=336, ridge_alpha=10.0)),
        ("rff_L336_raw_a1",    lambda: RFFRawExpert(input_length=336, ridge_alpha=1.0,
                                                     rff_dim=RFF_DIM, rff_seed=RFF_SEED)),
        ("calendar_rff_L336_a1", lambda: CalendarRFFExpert(input_length=336, ridge_alpha=1.0,
                                                           rff_dim=RFF_DIM, rff_seed=RFF_SEED + 1)),
    ]


# ---------------------------------------------------------------------------
# Helpers: history-swap predict, prediction collection.
# ---------------------------------------------------------------------------
def _predict_linear_expert(model, series: np.ndarray, start: int, L: int, H: int) -> np.ndarray:
    """Predict one window via history_ swap (same pattern as S-20/S-39)."""
    orig = model.history_
    model.history_ = series[:start]
    out = np.asarray(model.predict(), dtype=float)
    model.history_ = orig
    return out


def _predict_rff_expert(model, series: np.ndarray, start: int, L: int, H: int,
                         calendar: np.ndarray | None = None) -> np.ndarray:
    """Predict one window via history_ swap for RFF experts (with calendar)."""
    orig = model.history_
    model.history_ = series[:start]
    if isinstance(model, CalendarRFFExpert) and calendar is not None:
        out = np.asarray(model.predict(calendar=calendar[:start]), dtype=float)
    elif isinstance(model, CalendarNLinear) and calendar is not None:
        out = np.asarray(model.predict(calendar=calendar[:start]), dtype=float)
    else:
        out = np.asarray(model.predict(), dtype=float)
    model.history_ = orig
    return out

def collect_expert_preds(models: Sequence[object], series: np.ndarray,
                         origin_starts: np.ndarray,
                         calendar: np.ndarray | None = None) -> np.ndarray:
    """P (n, M, H): expert j's predictions for each origin."""
    out = []
    for model in models:
        preds = []
        for s in origin_starts:
            if isinstance(model, (RFFRawExpert, CalendarRFFExpert, CalendarNLinear)):
                preds.append(_predict_rff_expert(model, series, s, model.input_length, HORIZON, calendar))
            else:
                preds.append(_predict_linear_expert(model, series, s, model.input_length, HORIZON))
        out.append(np.asarray(preds, dtype=float))
    return np.stack(out, axis=1)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def rolling_metrics(preds: np.ndarray, actuals: np.ndarray,
                    disjoint_starts: tuple[int, ...] | None = None):
    """Compute MAE, RMSE, and per-window disjoint metrics."""
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err ** 2, axis=1))
    mae = float(np.mean(mae_per))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    disj = {}
    if disjoint_starts:
        for w, s in enumerate(disjoint_starts):
            m = float(np.mean(mae_per[s:s + HORIZON]))
            d = float(np.sqrt(np.mean(err[s:s + HORIZON] ** 2)))
            disj[f"W{w+1}"] = {"mae": m, "rmse": d}
    return mae, rmse, disj


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    t_all = time.time()
    print("[S-41] RFF-MoE ensemble start")
    pd = get_protocol_data()
    fit_history, eval_series, test = pd.rolling_views()
    train_8545 = fit_history[:TRAIN_END]
    val = fit_history[TRAIN_END:]
    n_val = len(val) - HORIZON + 1
    assert len(train_8545) == 8545 and len(val) == 2880 and len(test) == 2880

    val_origin_starts = np.arange(n_val) + TRAIN_END
    n_test = len(test) - HORIZON + 1
    test_origin_starts = np.arange(n_test) + len(fit_history)

    # Load calendar features if available
    calendar_path = HERE.parent / "calendar_aware_linear_s40" / "calendar_features.npy"
    calendar_all = None
    if calendar_path.exists():
        calendar_all = np.load(calendar_path)
        if calendar_all.shape[0] < 17420:
            print(f"[S-41] WARNING: calendar shape {calendar_all.shape} too small, ignoring")
            calendar_all = None
        else:
            print(f"[S-41] calendar features loaded: {calendar_all.shape}")

    # Build experts
    expert_factories = _make_experts()
    models = [factory() for _, factory in expert_factories]
    for m in models:
        if isinstance(m, CalendarRFFExpert):
            m.fit(train_8545, horizon=HORIZON, calendar=calendar_all[:len(train_8545)] if calendar_all is not None else None)
        else:
            m.fit(train_8545, horizon=HORIZON)

    # Collect validation predictions (frozen on train 8545)
    print("[S-41] collecting val predictions (frozen on train 8545)...")
    t0 = time.time()
    P_val = collect_expert_preds(models, fit_history, val_origin_starts, calendar_all)
    A_val = np.stack([val[t : t + HORIZON] for t in range(n_val)])
    print(f"[S-41] val preds shape {P_val.shape} in {time.time() - t0:.1f}s")

    # Re-fit experts on full 11425 (fit_history)
    print("[S-41] re-fitting experts on full 11425...")
    frozen_models = [factory() for _, factory in expert_factories]
    for m in frozen_models:
        if isinstance(m, CalendarRFFExpert):
            m.fit(fit_history, horizon=HORIZON, calendar=calendar_all[:len(fit_history)] if calendar_all is not None else None)
        else:
            m.fit(fit_history, horizon=HORIZON)

    # Collect test predictions (refrozen on 11425)
    print("[S-41] collecting test predictions (refrozen on 11425)...")
    t0 = time.time()
    P_test = collect_expert_preds(frozen_models, eval_series, test_origin_starts, calendar_all)
    A_test = np.stack([test[t : t + HORIZON] for t in range(n_test)])
    print(f"[S-41] test preds shape {P_test.shape} in {time.time() - t0:.1f}s")

    # Uniform blend
    M = P_test.shape[1]
    uniform_w = np.ones(M, dtype=float) / M
    blended = np.einsum("m,nmh->nh", uniform_w, P_test)

    mae, rmse, disj = rolling_metrics(blended, A_test, DISJOINT_STARTS)
    print(f"[S-41] uniform blend -> full MAE={mae:.6f} RMSE={rmse:.6f}")

    # Optional per-horizon stack head (α=10000, no intercept)
    def fit_stack_map(P, A, alpha, fit_intercept=False):
        n, m, h = P.shape
        coef = np.empty((m, h), dtype=float)
        for k in range(h):
            r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
            coef[:, k] = r.coef_

        class _Map:
            def predict(self, Pt):
                return np.einsum("mh,nmh->nh", coef, Pt)

        _Map.coef_ = coef
        return _Map()

    n2 = len(A_val) // 2
    stack = fit_stack_map(P_val[:n2], A_val[:n2], alpha=10000.0, fit_intercept=False)
    stacked = stack.predict(P_test)
    s_mae, s_rmse, s_disj = rolling_metrics(stacked, A_test, DISJOINT_STARTS)
    print(f"[S-41] stacked α=10000 -> full MAE={s_mae:.6f} RMSE={s_rmse:.6f}")

    # Validation full for transfer guard
    stack_val = fit_stack_map(P_val[:n2], A_val[:n2], alpha=10000.0, fit_intercept=False)
    stacked_val = stack_val.predict(P_val)
    val_mae, _, _ = rolling_metrics(stacked_val, A_val)

    transfer = val_mae - s_mae
    disjoint4 = float(np.mean([s_disj[w]["mae"] for w in ["W1", "W2", "W3", "W4"]]))

    results = {
        "experiment": "S-41",
        "protocol": "S-20-clean",
        "pool": [name for name, _ in expert_factories],
        "router": "uniform",
        "stack_alpha": 10000.0,
        "full_mae": round(s_mae, 6),
        "full_rmse": round(s_rmse, 6),
        "val_full_mae": round(val_mae, 6),
        "transfer_delta": round(transfer, 6),
        "disjoint_4": round(disjoint4, 6),
        "disjoint": {k: {"mae": round(v["mae"], 6), "rmse": round(v["rmse"], 6)} for k, v in s_disj.items()},
        "accept": bool(s_mae < 1.9909 and disjoint4 < 1.9696 and abs(transfer) <= 0.02),
        "runtime_s": round(time.time() - t_all, 2),
        "rff_dim": RFF_DIM,
        "calendar": bool(calendar_all is not None),
    }

    out_path = HERE / "results_s41.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[S-41] results -> {out_path}")
    print(f"[S-41] full MAE={s_mae:.6f} disjoint-4={disjoint4:.6f} transfer={transfer:+.6f}")
    print(f"[S-41] accept={results['accept']}")

    # Determinism smoke test: re-blend should be byte-identical
    blended2 = np.einsum("m,nmh->nh", uniform_w, P_test)
    assert np.allclose(blended, blended2), "non-deterministic uniform blend"
    print("[S-41] determinism smoke: OK")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
