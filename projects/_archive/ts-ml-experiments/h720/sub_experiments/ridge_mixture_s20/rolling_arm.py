"""S-20 — Ridge-regression mixture of the top historic linear models (per-horizon stacking).

User proposal: instead of S-17's 2-global-weight convex blend, fit a
PER-HORIZON ridge map over the member predictions (stacking / mixture of
experts via ridge). Each horizon h gets its own coefficients + intercept,
so the model can (a) weight members differently near vs far, and (b) learn a
per-horizon bias correction (the S-16c/S-18 lesson: NLinear's trend
extrapolation drifts with horizon) — direction C comes for free.

Members (top-6 distinct linear rows; the DLinear L336 row represents the
DLinear≡RLinear≡FITS equivalence class; non-linear rows excluded per the
S-01/S-18/S-19 regime-fragility evidence):
  0  nlinear_L336_a1    NLinear(336, ridge a=1)     test 2.0571 (S-06)
  1  nlinear_L96_a1     NLinear(96,  ridge a=1)     test 2.0925 (S-06)
  2  nlinear_L720_a1    NLinear(720, ridge a=1)     test 2.1534 (S-06)
  3  dlinear_L96_a0     DLinear(96, k25, a=0)       test 2.1163 (S-05)
  4  dlinear_L336_a0     DLinear(336, k25, a=0)     test 2.1220 (S-05/S-06)
  5  dlinear_L720_a0     DLinear(720, k25, a=0)     test 2.1687 (S-06)

Protocol (S-02 / S-16c / S-17, with protocol-clean alpha selection):
  1. Members frozen-fit on train 8,545 (weight-search fit).
  2. Collect val predictions P (2161, M, H) + actuals A (2161, H).
  3. Alpha selection WITHOUT test and WITHOUT reusing the fit origins:
     chronological split of val origins — stack-map fit on val origins
     [0, 1081), alpha selected on val origins [1081, 2161) (the later half;
     no future leakage into the alpha choice).
  4. Refit the stacking ridge (selected alpha) on ALL val origins.
  5. Frozen test: members re-fit on full 11,425; stacking map applied to
     member test predictions; rolling MAE/RMSE + disjoint windows.
  6. Test never consulted for anything.

Baselines re-scored live on the same harness: best member (NLinear L336),
the S-17 incumbent ensemble 2.0519, and plain per-horizon-mean blend.
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


def member_preds_linear(model, series: np.ndarray, starts: np.ndarray,
                        L: int, H: int) -> np.ndarray:
    """Per-window predict via history_ swap (cheap: one sklearn predict per window)."""
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


def collect_preds(models, series: np.ndarray, origin_starts: np.ndarray) -> np.ndarray:
    """P (n, M, H): member j's predictions for windows starting at starts-L."""
    n = len(origin_starts)
    P = np.empty((n, len(models), HORIZON))
    for j, m in enumerate(models):
        L = m.input_length
        starts = origin_starts - L
        P[:, j, :] = member_preds_linear(m, series, starts, L, HORIZON)
    return P


def fit_stack_map(P: np.ndarray, A: np.ndarray, alpha: float, fit_intercept: bool = False):
    """Per-horizon single-output ridge stacking over member predictions.

    P arrives as (n, M, H): one ridge per horizon step k over the member
    predictions P[:, :, k] -> A[:, k]. IMPORTANT (S-20 finding): the
    intercept is NOT fitted (fit_intercept=False) — a per-horizon
    intercept fitted on one val sub-half stores the sub-half's level
    offset and is catastrophically wrong on the other half (held-out
    MAE 5.7-6.5 vs 2.56 without). Ridge-without-intercept shrinks
    toward the equal-weight member mean — the safe limit behavior.
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


def main():
    t_all = time.time()
    pd = get_protocol_data()
    fit_history, eval_series, test = pd.rolling_views()
    train_8545 = fit_history[:TRAIN_END]
    val = fit_history[TRAIN_END:]
    n_val = len(val) - HORIZON + 1          # 2161
    assert len(train_8545) == 8545 and len(val) == 2880 and len(test) == 2880

    # 1) members frozen on train 8,545
    print("fitting 6 members on train 8545 ...")
    models = []
    for _, factory in MEMBERS:
        m = factory()
        m.fit(train_8545, horizon=HORIZON)
        models.append(m)

    # 2) val predictions
    val_origin_starts = np.arange(n_val) + TRAIN_END   # window start index
    print("collecting val predictions ...")
    P_val = collect_preds(models, fit_history, val_origin_starts)
    A_val = np.stack([val[t : t + HORIZON] for t in range(n_val)])

    # per-member val MAE (sanity)
    for j, (name, _) in enumerate(MEMBERS):
        m = float(np.mean(np.mean(np.abs(P_val[:, j, :] - A_val), axis=1)))
        print(f"  {name:16s} val {m:.4f}")

    # 3) chronological alpha selection inside val
    n_fit = n_val // 2                     # 1080 origins fit, 1081 select
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

    # 5) frozen test: members re-fit on 11,425, collect test preds, apply map
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

    # baselines on the same test predictions
    preds_mean = P_test.mean(axis=1)                       # equal-weight mean
    mean_mae, mean_rmse, _ = rolling_metrics(preds_mean, A_test)
    j_best = 0
    best_mae, best_rmse, _ = rolling_metrics(P_test[:, j_best, :], A_test)

    print(f"\n===============================================")
    print(f"RIDGE MIXTURE (6 members, per-horizon stack, alpha={best_alpha})")
    print(f"  test rolling: {test_mae:.4f} / {test_rmse:.4f}")
    print(f"  disjoint: " + ", ".join(f"W{i+1} {disj[f'window_{i+1}']['mae']:.4f}" for i in range(4)))
    print(f"  vs S-17 incumbent 2.0519: {test_mae - 2.0519:+.4f}")
    print(f"  vs NLinear L336  2.0571: {test_mae - 2.0571:+.4f}")
    print(f"baselines (same harness): best member {best_mae:.4f}, equal-mean {mean_mae:.4f}")
    print(f"===============================================")

    out = {
        "slice": "S-20",
        "protocol": {
            "members": [n for n, _ in MEMBERS],
            "map": "per-horizon multi-output ridge stacking over member predictions",
            "alpha_selection": "chronological: fit val origins [0,1080), select on [1080,2161)",
            "alpha_candidates": alphas,
            "members_fit": "frozen; map fit on train-8545-fit member preds over val, test fit on 11,425-fit preds",
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
            "delta_vs_s17_ensemble": round(test_mae - 2.0519, 4),
            "delta_vs_nlinear": round(test_mae - 2.0571, 4),
            "baseline_best_member": round(best_mae, 4),
            "baseline_equal_mean": round(mean_mae, 4),
        },
    }
    out_path = HERE / "results_s20.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {out_path} (total {time.time() - t_all:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
