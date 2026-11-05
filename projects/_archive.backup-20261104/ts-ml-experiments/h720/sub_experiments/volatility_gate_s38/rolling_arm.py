"""S-38 — Volatility-Gated Conditional Weighting over S-26 2-Member Base.

Prototype S-38: volatility-gated conditional weighting over the S-26 2-member
base (NLinear L336 a=1 + NLinear L336 a=10), using rolling window std as the
gating signal.

Protocol (S-20-clean):
  1. Members frozen on train 8,545.
  2. Collect val predictions P (2161, 2, H) + actuals A (2161, H).
  3. Compute rolling std over history window (tested across windows 96, 336, 720).
  4. Split origins into low / medium / high sigma terciles on validation
     (thresholds computed on val training half n2=1080).
  5. Fit a separate per-horizon Ridge mixture weight for each tercile
     (fit_intercept=False), using only the S-26 2 members.
  6. Select alpha and window on held-out val half (n2=1081).
  7. Refit per-tercile stacking maps on all val origins.
  8. Frozen test: members refrozen on full 11,425; routed stacking map applied
     to test predictions; report full MAE, disjoint-4 MAE, and per-tercile MAE.
  9. Acceptance: full MAE < 1.9909 AND disjoint-4 < 1.9696 AND no tercile
     weight collapses to 0/1 degenerate simplex.
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
from methods.neural_models import NLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]
VOL_WINDOWS = [96, 336, 720]
INCUMBENT_MAE = 1.9909
INCUMBENT_DISJOINT = 1.9696

CANDIDATES = [
    ("nlinear_L336_a1",  lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
]


def fit_stack_map(P: np.ndarray, A: np.ndarray, alpha: float, fit_intercept: bool = False):
    """Per-horizon single-output ridge stacking over member predictions (no intercept)."""
    n, m, h = P.shape
    coef = np.empty((m, h))
    inter = np.zeros(h)
    for k in range(h):
        if n == 0:
            coef[:, k] = 0.5
            continue
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
    class _Map:
        def predict(self, Pt: np.ndarray) -> np.ndarray:
            return np.einsum("mh,nmh->nh", coef, Pt) + inter[None, :]
    _Map.coef_ = coef
    return _Map()


def preds_for_train_fit(factory, train_series, full_series, starts, L, H):
    m = factory()
    m.fit(train_series, horizon=H)
    out = []
    hist = m.history_
    for s in starts:
        m.history_ = full_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_ = hist
    return np.asarray(out)


def preds_for_full_fit(factory, full_series, concat_series, starts, L, H):
    m = factory()
    m.fit(full_series, horizon=H)
    out = []
    hist = m.history_
    for s in starts:
        m.history_ = concat_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_ = hist
    return np.asarray(out)


def collect_val(train_series, full_series, starts):
    cols = []
    for name, factory in CANDIDATES:
        L = factory().input_length
        p = preds_for_train_fit(factory, train_series, full_series, starts, L, HORIZON)
        cols.append(p)
    return np.stack(cols, axis=1)


def collect_test(full_series, concat_series, starts):
    cols = []
    for name, factory in CANDIDATES:
        L = factory().input_length
        p = preds_for_full_fit(factory, full_series, concat_series, starts, L, HORIZON)
        cols.append(p)
    return np.stack(cols, axis=1)


def rolling_metrics(preds: np.ndarray, actuals: np.ndarray, is_disjoint: bool = False):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err**2, axis=1))
    mae = float(np.mean(mae_per))
    rmse = float(np.sqrt(np.mean(err**2)))
    if is_disjoint:
        disj = {
            f"window_{i+1}": {"mae": float(mae_per[i]), "rmse": float(rmse_per[i])}
            for i in range(len(preds))
        }
    else:
        disj = {
            f"window_{i+1}": {"mae": float(mae_per[t]), "rmse": float(rmse_per[t])}
            for i, t in enumerate(DISJOINT_STARTS) if t < len(mae_per)
        }
    return mae, rmse, disj


def compute_sigmas(series: np.ndarray, starts: np.ndarray, window: int) -> np.ndarray:
    sigmas = []
    for s in starts:
        sub = series[max(0, s - window): s]
        sigmas.append(float(np.std(sub)) if len(sub) > 0 else 0.0)
    return np.array(sigmas, dtype=float)


def assign_terciles(sigmas: np.ndarray, p33: float, p66: float) -> np.ndarray:
    t = np.zeros(len(sigmas), dtype=int)
    t[sigmas > p33] = 1
    t[sigmas > p66] = 2
    return t


def main():
    t_all = time.time()
    log_lines = []
    def log(msg):
        print(msg)
        log_lines.append(msg)

    log("=== S-38 Volatility-Gated Conditional Weighting Harness ===")
    pd = get_protocol_data()
    fit_series, eval_series, test_series = pd.rolling_views()
    train_series = fit_series[:TRAIN_END]
    val_series = fit_series[TRAIN_END:]
    n_val = len(val_series) - HORIZON + 1
    assert n_val == 2161
    assert len(train_series) == 8545 and len(fit_series) == 11425

    val_starts = np.arange(n_val) + TRAIN_END
    log(f"Collecting validation predictions for 2 S-26 members over {n_val} origins...")
    P_val = collect_val(train_series, fit_series, val_starts)
    A_val = np.stack([val_series[t: t + HORIZON] for t in range(n_val)])

    n2 = n_val // 2  # 1080 training half, 1081 held-out half
    P_tr, P_sel = P_val[:n2], P_val[n2:]
    A_tr, A_sel = A_val[:n2], A_val[n2:]

    best_held = None
    best_config = None  # (window, alpha, p33, p66)
    best_stacks = None

    for w in VOL_WINDOWS:
        sigmas_val = compute_sigmas(fit_series, val_starts, window=w)
        sigmas_tr = sigmas_val[:n2]
        p33, p66 = np.percentile(sigmas_tr, [33.333, 66.666])
        terc_tr = assign_terciles(sigmas_tr, p33, p66)
        terc_sel = assign_terciles(sigmas_val[n2:], p33, p66)

        for alpha in ALPHAS:
            preds_sel_list = []
            stacks_tr = {}
            valid_config = True
            for t in range(3):
                idx_tr = np.where(terc_tr == t)[0]
                idx_sel = np.where(terc_sel == t)[0]
                if len(idx_tr) == 0:
                    valid_config = False
                    break
                stack_t = fit_stack_map(P_tr[idx_tr], A_tr[idx_tr], alpha)
                stacks_tr[t] = stack_t
                if len(idx_sel) > 0:
                    preds_sel_list.append((idx_sel, stack_t.predict(P_sel[idx_sel])))

            if not valid_config or not preds_sel_list:
                continue

            preds_sel_all = np.empty_like(A_sel)
            for idx_sel, p_part in preds_sel_list:
                preds_sel_all[idx_sel] = p_part

            mae_sel, _, _ = rolling_metrics(preds_sel_all, A_sel)
            if best_held is None or mae_sel < best_held:
                best_held = mae_sel
                best_config = (w, alpha, p33, p66)

    log(f"Best held-out val MAE: {best_held:.4f} with window={best_config[0]}, alpha={best_config[1]}")
    best_w, best_alpha, p33_tr, p66_tr = best_config

    # Refit on all validation origins using best_w and best_alpha
    sigmas_all_val = compute_sigmas(fit_series, val_starts, window=best_w)
    p33_all, p66_all = np.percentile(sigmas_all_val, [33.333, 66.666])
    terc_all_val = assign_terciles(sigmas_all_val, p33_all, p66_all)

    stacks_val = {}
    tercile_val_coefs = {}
    for t in range(3):
        idx_v = np.where(terc_all_val == t)[0]
        stack_t = fit_stack_map(P_val[idx_v], A_val[idx_v], best_alpha)
        stacks_val[t] = stack_t
        tercile_val_coefs[f"tercile_{t}"] = stack_t.coef_.tolist()
        log(f"  Val Tercile {t} (n={len(idx_v)}): mean coefs = {stack_t.coef_.mean(axis=1).tolist()}")

    preds_val_all = np.empty_like(A_val)
    for t in range(3):
        idx_v = np.where(terc_all_val == t)[0]
        preds_val_all[idx_v] = stacks_val[t].predict(P_val[idx_v])

    val_mae, val_rmse, _ = rolling_metrics(preds_val_all, A_val)
    log(f"Refit all val MAE: {val_mae:.4f}, RMSE: {val_rmse:.4f}")

    # Frozen test evaluation
    log("Fitting members on full train 11425 for test evaluation...")
    test_models = []
    for _, factory in CANDIDATES:
        m = factory()
        m.fit(fit_series, horizon=HORIZON)
        test_models.append(m)

    concat_series = np.concatenate([fit_series, test_series])
    n_test = len(test_series) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_series)
    assert n_test == 2161

    log(f"Collecting test predictions on {n_test} test origins...")
    P_test = collect_test(fit_series, concat_series, test_starts)
    A_test = np.stack([test_series[t: t + HORIZON] for t in range(n_test)])

    sigmas_test = compute_sigmas(concat_series, test_starts, window=best_w)
    terc_test = assign_terciles(sigmas_test, p33_all, p66_all)

    preds_test_all = np.empty_like(A_test)
    tercile_test_maes = {}
    for t in range(3):
        idx_t = np.where(terc_test == t)[0]
        if len(idx_t) > 0:
            p_t = stacks_val[t].predict(P_test[idx_t])
            preds_test_all[idx_t] = p_t
            t_mae, t_rmse, _ = rolling_metrics(p_t, A_test[idx_t])
            tercile_test_maes[f"tercile_{t}"] = {"mae": t_mae, "rmse": t_rmse, "count": len(idx_t)}
            log(f"  Test Tercile {t} (n={len(idx_t)}): MAE={t_mae:.4f}, RMSE={t_rmse:.4f}")

    test_mae, test_rmse, _ = rolling_metrics(preds_test_all, A_test)

    # Disjoint-4 test evaluation
    disj_starts = np.array([len(fit_series) + s for s in DISJOINT_STARTS])
    P_disj = collect_test(fit_series, concat_series, disj_starts)
    A_disj = np.stack([test_series[s: s + HORIZON] for s in DISJOINT_STARTS])
    sigmas_disj = compute_sigmas(concat_series, disj_starts, window=best_w)
    terc_disj = assign_terciles(sigmas_disj, p33_all, p66_all)

    preds_disj_all = np.empty_like(A_disj)
    for t in range(3):
        idx_t = np.where(terc_disj == t)[0]
        if len(idx_t) > 0:
            preds_disj_all[idx_t] = stacks_val[t].predict(P_disj[idx_t])

    disj_mae, disj_rmse, disj_windows = rolling_metrics(preds_disj_all, A_disj, is_disjoint=True)

    log(f"\nS-38 Results:")
    log(f"  Full MAE: {test_mae:.4f} (Incumbent: {INCUMBENT_MAE})")
    log(f"  Disjoint-4 MAE: {disj_mae:.4f} (Incumbent: {INCUMBENT_DISJOINT})")

    # Acceptance checks
    no_collapse = True
    for t in range(3):
        coef = stacks_val[t].coef_
        # check if weights collapse to 0 or 1 degenerate simplex (e.g., all 0, all 1, or one member is 1.0 and other 0.0)
        # Here we check if weights are reasonable (neither member is 1.0 everywhere or 0.0 everywhere)
        if np.allclose(coef[0], 1.0) or np.allclose(coef[0], 0.0):
            no_collapse = False

    accept = (test_mae < INCUMBENT_MAE) and (disj_mae < INCUMBENT_DISJOINT) and no_collapse
    log(f"Acceptance: {accept} (MAE < {INCUMBENT_MAE}: {test_mae < INCUMBENT_MAE}, Disj < {INCUMBENT_DISJOINT}: {disj_mae < INCUMBENT_DISJOINT}, No Collapse: {no_collapse})")

    results = {
        "slice": "S-38-volatility-gate-tercile",
        "protocol": "S-20-clean: val members frozen on 8545, test members refrozen on 11425",
        "pool": [name for name, _ in CANDIDATES],
        "gate_design": {
            "window": int(best_w),
            "alpha": float(best_alpha),
            "tercile_thresholds": [float(p33_all), float(p66_all)],
            "tercile_counts": [int(np.sum(terc_all_val == t)) for t in range(3)],
        },
        "metrics": {
            "val_held": float(best_held),
            "val_full": float(val_mae),
            "full": float(test_mae),
            "rmse": float(test_rmse),
            "disjoint": float(disj_mae),
            "disjoint_rmse": float(disj_rmse),
            "incumbent_full": float(INCUMBENT_MAE),
            "incumbent_disjoint": float(INCUMBENT_DISJOINT),
            "delta_full": float(test_mae - INCUMBENT_MAE),
            "delta_disjoint": float(disj_mae - INCUMBENT_DISJOINT),
        },
        "tercile_test_maes": tercile_test_maes,
        "tercile_val_coefs": tercile_val_coefs,
        "disjoint_windows": disj_windows,
        "no_collapse": bool(no_collapse),
        "accept": bool(accept),
        "verdict": "ACCEPTED" if accept else "REJECTED",
        "harness_command": "python projects/ts-ml-experiments/h720/sub_experiments/volatility_gate_s38/rolling_arm.py",
        "harness_log": "harness.log",
        "plan_impact": {
            "invalidates": [],
            "confirms": [
                f"Volatility-gated tercile conditional weighting (window={best_w}, alpha={best_alpha}) achieves full MAE {test_mae:.4f} and disjoint-4 MAE {disj_mae:.4f}."
            ],
            "opens": ["Continued conditional weighting or volatility routing over linear mixture bases."]
        },
        "elapsed_s": float(time.time() - t_all)
    }

    results_path = HERE / "results_s38.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    log_path = HERE / "harness.log"
    with open(log_path, "w") as f:
        f.write("\n".join(log_lines) + "\n")

    log(f"Wrote results to {results_path} and log to {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
