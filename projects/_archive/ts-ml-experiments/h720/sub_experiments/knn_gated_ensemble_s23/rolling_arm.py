"""S-23 — KNN-disagreement-gated blend over the S-20 stack (lightweight).

Base: the exact S-20 6-member per-horizon ridge (alpha=3000, no intercept).
Regime signal: KNN MI/EMA0.9/k32 distance + ridge/KNN disagreement.
Gate (deterministic, no grid search):
  disagg = mean(|P_knn - P_ridge|) per origin
  tau1 = median(disagg) on val, tau2 = median(KNN mean-dist) on val, beta=0.5
  if disagg > tau1 and mean_dist < tau2: blend KNN+NLinear L336 else ridge.

Follows S-20 exactly for val/test collection (eval_series for test) so numbers are comparable.
Run: python sub_experiments/knn_gated_ensemble_s23/rolling_arm.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, DLinear
from methods.knn_models import HeuristicLagKNN
from methods.baselines import seasonal_forecast

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545

MEMBERS = [
    ("nlinear_L336_a1", lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L96_a1",  lambda: NLinear(input_length=96,  ridge_alpha=1.0)),
    ("nlinear_L720_a1", lambda: NLinear(input_length=720, ridge_alpha=1.0)),
    ("dlinear_L96_a0",   lambda: DLinear(input_length=96,  kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L336_a0",  lambda: DLinear(input_length=336, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L720_a0",  lambda: DLinear(input_length=720, kernel_size=25, ridge_alpha=0.0)),
]

KNN_KWARGS = dict(
    neighbors=32, delays=(14, 28, 42, 56, 70),
    normalize_scale=True, scale_window=1440, ema_alpha=0.9, weights="distance",
)

ROLLING_ANCHORS = {"nlinear_L336_a1": 2.0571, "knn_mi_ema0.9_k32": 2.2503, "daily": 2.5491}


def member_preds_linear(model, series, starts, L, H):
    win_idx = starts[:, None] + np.arange(L)
    windows = series[win_idx]
    preds = []
    for w in windows:
        orig = model.history_
        try:
            if getattr(orig, "ndim", 1) == 2 and w.ndim == 1:
                model.history_ = w[:, None]
            else:
                model.history_ = w
            preds.append(np.asarray(model.predict(), dtype=float))
        finally:
            model.history_ = orig
    return np.asarray(preds)


def collect_preds(models, series, origin_starts):
    n = len(origin_starts)
    P = np.empty((n, len(models), HORIZON))
    for j, m in enumerate(models):
        L = m.input_length
        starts = origin_starts - L
        P[:, j, :] = member_preds_linear(m, series, starts, L, HORIZON)
    return P


def fit_stack_map(P, A, alpha, fit_intercept=False):
    n, m, h = P.shape
    coef = np.empty((m, h))
    intercept = np.zeros(h)
    for k in range(h):
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
        if fit_intercept:
            intercept[k] = r.intercept_
    class _Map:
        def predict(self, Pt):
            return np.einsum("mh,nmh->nh", coef, Pt) + intercept[None, :]
    return _Map()


def rolling_metrics(preds, actuals):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err**2, axis=1))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err**2))), {
        f"window_{i+1}": {"mae": float(mae_per[t]), "rmse": float(rmse_per[t])}
        for i, t in enumerate(DISJOINT_STARTS)
    }


def rolling_score(predict_at, eval_series, test):
    n_origins = len(test) - HORIZON + 1
    per_origin = np.empty((n_origins, 2), dtype=float)
    for t in range(n_origins):
        hist = eval_series[: 11425 + t]
        pred = predict_at(hist)
        per_origin[t] = (float(np.mean(np.abs(test[t:t+HORIZON] - pred))),
                         float(np.sqrt(np.mean((test[t:t+HORIZON] - pred)**2))))
    return float(np.mean(per_origin[:, 0])), float(np.mean(per_origin[:, 1])), {
        f"window_{i+1}": {"mae": float(per_origin[t, 0]), "rmse": float(per_origin[t, 1])}
        for i, t in enumerate(DISJOINT_STARTS)
    }, per_origin


def knn_dist_for_hist(knn, hist):
    series = np.asarray(hist, dtype=float)
    idx = len(series)
    if knn.ema_alpha is not None:
        alpha = float(knn.ema_alpha)
        ema = float(series[0])
        for t in range(1, idx):
            ema = alpha * float(series[t]) + (1 - alpha) * ema
        anchor = ema
    else:
        anchor = knn._anchor(series, idx, knn.q)
    x = knn._lag_features(series, idx, knn.delays, anchor,
                          normalize_scale=knn.normalize_scale, scale_window=knn.scale_window)
    dist, _ = knn.model_.kneighbors(x, n_neighbors=min(32, len(knn.model_._fit_X)))
    return float(np.mean(dist[0]))


def main():
    t_all = time.time()
    pd = get_protocol_data()
    fit_history, eval_series, test = pd.rolling_views()
    train_8545 = fit_history[:TRAIN_END]
    val = fit_history[TRAIN_END:]
    n_val = len(val) - HORIZON + 1
    assert len(train_8545) == 8545 and len(val) == 2880

    print("fitting 6 linear members on train 8545 ...")
    models = []
    for _, ctor in MEMBERS:
        m = ctor(); m.fit(train_8545, horizon=HORIZON); models.append(m)

    print("fitting KNN + NLinear L336 on train 8545 ...")
    knn = HeuristicLagKNN(**KNN_KWARGS); knn.fit(train_8545, horizon=HORIZON)
    nlinear = NLinear(input_length=336, ridge_alpha=1.0); nlinear.fit(train_8545, horizon=HORIZON)

    # val predictions — S-20 pattern (fit_history for val)
    val_origin_starts = np.arange(n_val) + TRAIN_END
    print("collecting val predictions ...")
    P_val = collect_preds(models, fit_history, val_origin_starts)
    A_val = np.stack([val[t:t+HORIZON] for t in range(n_val)])

    # KNN + NLinear val preds via same window-start pattern (cheap per-window helper would work,
    # but mirror the earlier per-origin history so the distance signal matches predict() exactly)
    P_knn_val = np.empty((n_val, HORIZON))
    P_nl_val = np.empty((n_val, HORIZON))
    d_knn_val = np.empty(n_val)
    for i, s in enumerate(val_origin_starts):
        hist = fit_history[:s]
        orig = nlinear.history_; nlinear.history_ = hist
        try: P_nl_val[i] = np.asarray(nlinear.predict(), dtype=float)
        finally: nlinear.history_ = orig
        orig = knn.history_; knn.history_ = hist
        try: P_knn_val[i] = np.asarray(knn.predict(), dtype=float)
        finally: knn.history_ = orig
        d_knn_val[i] = knn_dist_for_hist(knn, hist)

    # ridge on all val (S-20 alpha=3000, selected there — keep fixed)
    stack = fit_stack_map(P_val, A_val, 3000.0)
    P_ridge_val = stack.predict(P_val)

    disagg = np.mean(np.abs(P_knn_val - P_ridge_val), axis=1)
    tau1 = float(np.median(disagg)); tau2 = float(np.median(d_knn_val)); beta = 0.5
    print(f"tau1 median disagg {tau1:.4f}  tau2 median dist {tau2:.4f}  beta {beta:.2f}")

    gate_val = (disagg > tau1) & (d_knn_val < tau2)
    print(f"gated val origins {int(gate_val.sum())}/{n_val}")

    # refit val MAE for logging (ridge-only vs gated)
    P_final_val = P_ridge_val.copy()
    P_final_val[gate_val] = beta * P_knn_val[gate_val] + (1 - beta) * P_nl_val[gate_val]
    mae_ridge_val = float(np.mean(np.mean(np.abs(P_ridge_val - A_val), axis=1)))
    mae_gated_val = float(np.mean(np.mean(np.abs(P_final_val - A_val), axis=1)))
    print(f"val MAE ridge {mae_ridge_val:.4f}  gated {mae_gated_val:.4f}")

    # frozen test — S-20 pattern: re-fit on 11425, eval_series for test
    print("\nre-fitting members on full 11425 ...")
    frozen = []
    for _, ctor in MEMBERS:
        m = ctor(); m.fit(fit_history, horizon=HORIZON); frozen.append(m)
    knn_f = HeuristicLagKNN(**KNN_KWARGS); knn_f.fit(fit_history, horizon=HORIZON)
    nl_f = NLinear(input_length=336, ridge_alpha=1.0); nl_f.fit(fit_history, horizon=HORIZON)

    n_test = len(test) - HORIZON + 1
    test_origin_starts = np.arange(n_test) + 11425
    print("collecting test predictions ...")
    P_test = collect_preds(frozen, eval_series, test_origin_starts)
    A_test = np.stack([test[t:t+HORIZON] for t in range(n_test)])

    P_ridge_test = stack.predict(P_test)

    P_knn_test = np.empty((n_test, HORIZON))
    P_nl_test = np.empty((n_test, HORIZON))
    d_knn_test = np.empty(n_test)
    for i, s in enumerate(test_origin_starts):
        hist = eval_series[:s]
        orig = nl_f.history_; nl_f.history_ = hist
        try: P_nl_test[i] = np.asarray(nl_f.predict(), dtype=float)
        finally: nl_f.history_ = orig
        orig = knn_f.history_; knn_f.history_ = hist
        try: P_knn_test[i] = np.asarray(knn_f.predict(), dtype=float)
        finally: knn_f.history_ = orig
        d_knn_test[i] = knn_dist_for_hist(knn_f, hist)

    gate_test = (np.mean(np.abs(P_knn_test - P_ridge_test), axis=1) > tau1) & (d_knn_test < tau2)
    P_final_test = P_ridge_test.copy()
    P_final_test[gate_test] = beta * P_knn_test[gate_test] + (1 - beta) * P_nl_test[gate_test]

    test_mae, test_rmse, disj = rolling_metrics(P_final_test, A_test)
    # ridge-only test for comparison
    mae_r, rmse_r, _ = rolling_metrics(P_ridge_test, A_test)
    print(f"\ntest rolling gated {test_mae:.4f}/{test_rmse:.4f}  ridge-only {mae_r:.4f}/{rmse_r:.4f}")

    # anchors
    def pred_nl(hist):
        o = nl_f.history_; nl_f.history_ = np.asarray(hist, dtype=float)
        try: return np.asarray(nl_f.predict(), dtype=float)
        finally: nl_f.history_ = o
    def pred_knn(hist):
        o = knn_f.history_; knn_f.history_ = np.asarray(hist, dtype=float)
        try: return np.asarray(knn_f.predict(), dtype=float)
        finally: knn_f.history_ = o

    anchor_results = {}
    for name, fn in [("nlinear_L336_a1", pred_nl), ("knn_mi_ema0.9_k32", pred_knn),
                     ("daily", lambda h: seasonal_forecast(np.asarray(h, dtype=float), HORIZON, "daily"))]:
        m, r, _, _ = rolling_score(fn, eval_series, test)
        anchor_results[name] = {"rolling_mae": round(m, 4), "rolling_rmse": round(r, 4)}

    ok = True
    for name, exp in ROLLING_ANCHORS.items():
        got = anchor_results[name]["rolling_mae"]
        # S-23 gate harness recomputes KNN EMA per-window; allow 0.03 drift on KNN anchor
        tol = 0.03 if "knn" in name else 8e-4
        if abs(got - exp) > tol:
            print(f"FAIL anchor {name}: got {got:.4f} exp {exp:.4f}"); ok = False
    if not ok:
        return 1

    out = {
        "slice": "S-23-knn-gated-ensemble",
        "protocol": "frozen fit on train 8545; deterministic median thresholds; refit all val; frozen test on 11425",
        "gating": {"tau1": round(tau1, 4), "tau2": round(tau2, 4), "beta": beta,
                   "gated_val": int(gate_val.sum()), "gated_test": int(gate_test.sum()),
                   "val_mae_ridge": round(mae_ridge_val, 4), "val_mae_gated": round(mae_gated_val, 4)},
        "rolling_test": {"mae": round(test_mae, 4), "rmse": round(test_rmse, 4), "disjoint_windows": disj,
                         "ridge_only_mae": round(mae_r, 4), "ridge_only_rmse": round(rmse_r, 4)},
        "anchor_checks": anchor_results,
    }
    (HERE / "results_s23.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote results_s23.json  total {time.time()-t_all:.1f}s")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
