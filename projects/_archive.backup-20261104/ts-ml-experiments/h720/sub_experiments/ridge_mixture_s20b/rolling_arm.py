"""S-20b — Per-horizon ridge mixture extended with the top non-linear members.

User proposal: add the most promising non-linear models from previous runs to
the S-20 ridge mixture. The ridge map shrinks each member's per-horizon
coefficient toward zero, so a non-linear member either contributes orthogonal
error information (win) or is harmlessly zeroed — a safer home than the
val-weighting that sank S-19.

Members (8): the 6 linear rows of S-20 plus the two best non-linear rows:
  0  nlinear_L336_a1    2.0571 (S-06)
  1  nlinear_L96_a1     2.0925 (S-06)
  2  nlinear_L720_a1    2.1534 (S-06)
  3  dlinear_L96_a0     2.1163 (S-05)
  4  dlinear_L336_a0    2.1220 (S-05)
  5  dlinear_L720_a0    2.1687 (S-06)
  6  elm_tree_d4_l5     2.1706 (S-09, h256, MI lags 14,28,42,56,70)
  7  knn_mi_ema09       2.2503 (S-15, q3 k32 recent10% norm1440 distance)

Protocol (identical to S-20, M 6 -> 8):
  - Members frozen-fit on train 8,545 for val; re-frozen on full 11,425 for
    test (the exact leaderboard protocol — every member is pinned to its
    leaderboard number with a fail-loud anchor on the test pass).
  - ONE history protocol for all members: history_ = full prefix strictly
    before the scored window (canonical rolling). Linears read only their
    trailing window, so the prefix swap is a no-op for them; KNN/ELMTree
    read the full prefix (EMA anchor, lag features) — the same data their
    leaderboard numbers were scored on.
  - Per-horizon ridge stacking, NO intercept (S-20 P1: the intercept stores
    the fitted sub-half's level offset), alpha selected chronologically
    inside val (fit [0,1080), select [1080,2161)); refit on all val; test
    never consulted.
  - Alpha grid extended to 1e5 (M up -> alpha up, S-20 open risk).
  - Internal baselines on the same member predictions: the S-20 6-member
    map (expect ~1.9980), equal-mean-8, best member.
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
from methods.neural_models import NLinear, DLinear, HeuristicLagELMTree
from methods.knn_models import HeuristicLagKNN

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
VALIDATION_END = 11425

MI_LAGS = (14, 28, 42, 56, 70)

MEMBERS = [
    ("nlinear_L336_a1", lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L96_a1",  lambda: NLinear(input_length=96,  ridge_alpha=1.0)),
    ("nlinear_L720_a1", lambda: NLinear(input_length=720, ridge_alpha=1.0)),
    ("dlinear_L96_a0",   lambda: DLinear(input_length=96,  kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L336_a0",  lambda: DLinear(input_length=336, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L720_a0",  lambda: DLinear(input_length=720, kernel_size=25, ridge_alpha=0.0)),
    ("elm_tree_d4_l5",   lambda: HeuristicLagELMTree(hidden_dim=256,
                                                     tree_kwargs={"max_depth": 4, "min_samples_leaf": 5})),
    ("knn_mi_ema09",     lambda: HeuristicLagKNN(q=3, neighbors=32, delays=MI_LAGS,
                                                 history_fraction=0.1, normalize_scale=True,
                                                 scale_window=1440, weights="distance", ema_alpha=0.9)),
]

ANCHOR_TEST_MAE = {
    "nlinear_L336_a1": 2.0571,
    "nlinear_L96_a1": 2.0925,
    "nlinear_L720_a1": 2.1534,
    "dlinear_L96_a0": 2.1163,
    "dlinear_L336_a0": 2.1220,
    "dlinear_L720_a0": 2.1687,
    "elm_tree_d4_l5": 2.1706,
    "knn_mi_ema09": 2.2503,
}

ALPHAS = [10.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0, 100000.0]


def collect_preds(models, series, n, base) -> np.ndarray:
    """P (n, M, H). Every member gets history_ = series[:base+t] (the full
    prefix strictly before the scored window) — the canonical rolling
    protocol; linears are unaffected (they read only the trailing window)."""
    P = np.empty((n, len(models), HORIZON))
    for j, m in enumerate(models):
        for t in range(n):
            hist = series[: base + t]
            orig = m.history_
            try:
                m.history_ = hist
                P[t, j, :] = np.asarray(m.predict(), dtype=float)
            finally:
                m.history_ = orig
    return P


def fit_stack_map(P: np.ndarray, A: np.ndarray, alpha: float, m: int = None):
    """Per-horizon single-output ridge, no intercept (S-20 P1), over the
    first ``m`` member columns (m=None -> all)."""
    m = m or P.shape[1]
    coef = np.empty((m, HORIZON))
    for k in range(HORIZON):
        r = Ridge(alpha=alpha, fit_intercept=False).fit(P[:, :m, k], A[:, k])
        coef[:, k] = r.coef_

    class _Map:
        def predict(self, Pt: np.ndarray) -> np.ndarray:
            return np.einsum("mh,nmh->nh", coef, Pt[:, :m, :])

    _Map.coef = coef
    return _Map()


def rolling_metrics(preds: np.ndarray, actuals: np.ndarray):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err**2, axis=1))
    disj = {f"window_{i+1}": {"mae": float(mae_per[t]), "rmse": float(rmse_per[t])}
            for i, t in enumerate(DISJOINT_STARTS)}
    return float(mae_per.mean()), float(np.sqrt(np.mean(err**2))), disj


def main():
    t_all = time.time()
    pd = get_protocol_data()
    fit_history, eval_series, test = pd.rolling_views()
    train_8545 = fit_history[:TRAIN_END]
    n_val = len(fit_history) - TRAIN_END - HORIZON + 1     # 2161
    n_test = len(test) - HORIZON + 1                       # 2161
    assert n_val == 2161 and n_test == 2161

    # 1) members frozen on train 8,545 (val pass)
    print("fitting 8 members on train 8545 ...")
    t0 = time.time()
    models = [f().fit(train_8545, horizon=HORIZON) for _, f in MEMBERS]
    print(f"  fit done ({time.time() - t0:.1f}s)")

    # 2) val predictions (history_ = fit_history[:8545+t])
    print("collecting val predictions ...")
    t0 = time.time()
    P_val = collect_preds(models, fit_history, n_val, TRAIN_END)
    A_val = np.stack([fit_history[TRAIN_END + t: TRAIN_END + t + HORIZON] for t in range(n_val)])
    print(f"  val pass done ({time.time() - t0:.1f}s)")
    for j, (name, _) in enumerate(MEMBERS):
        print(f"  {name:16s} val {float(np.mean(np.abs(P_val[:, j, :] - A_val))):.4f}")

    # 3) chronological alpha selection inside val (M=8, and M=6 for the
    #    internal S-20 baseline at its own selection)
    n_fit = n_val // 2
    P_fit, A_fit = P_val[:n_fit], A_val[:n_fit]
    P_sel, A_sel = P_val[n_fit:], A_val[n_fit:]
    print(f"\nalpha selection (M=8): fit {n_fit}, select {n_val - n_fit} ...")
    alpha_scores = {}
    for a in ALPHAS:
        r = fit_stack_map(P_fit, A_fit, a)
        alpha_scores[a] = float(np.mean(np.abs(r.predict(P_sel) - A_sel)))
        print(f"  alpha {a:8g}: second-half val MAE {alpha_scores[a]:.4f}")
    best_alpha = min(alpha_scores, key=alpha_scores.get)
    print(f"selected alpha = {best_alpha}")

    # 4) refit on all val
    stack8 = fit_stack_map(P_val, A_val, best_alpha)
    val_mae8 = float(np.mean(np.abs(stack8.predict(P_val) - A_val)))
    print(f"8-member map (alpha={best_alpha}) refit all val: MAE {val_mae8:.4f}")

    # internal baseline: the S-20 6-member map under the same protocol
    alpha6_scores = {}
    for a in ALPHAS:
        r = fit_stack_map(P_fit, A_fit, a, m=6)
        alpha6_scores[a] = float(np.mean(np.abs(r.predict(P_sel) - A_sel)))
    best_alpha6 = min(alpha6_scores, key=alpha6_scores.get)
    stack6 = fit_stack_map(P_val, A_val, best_alpha6, m=6)
    val_mae6 = float(np.mean(np.abs(stack6.predict(P_val) - A_val)))
    print(f"6-member map (S-20 re-derived, alpha={best_alpha6}): refit all val MAE {val_mae6:.4f}")

    # 5) frozen test: members re-fit on 11,425
    print("\nre-fitting 8 members on full 11425 ...")
    t0 = time.time()
    frozen = [f().fit(fit_history, horizon=HORIZON) for _, f in MEMBERS]
    print(f"  fit done ({time.time() - t0:.1f}s)")
    print("collecting test predictions ...")
    t0 = time.time()
    P_test = collect_preds(frozen, eval_series, n_test, VALIDATION_END)
    A_test = np.stack([test[t: t + HORIZON] for t in range(n_test)])
    print(f"  test pass done ({time.time() - t0:.1f}s)")

    # fail-loud: every member must reproduce its leaderboard rolling MAE
    anchor_fail = []
    for j, (name, _) in enumerate(MEMBERS):
        m = float(np.mean(np.abs(P_test[:, j, :] - A_test)))
        exp = ANCHOR_TEST_MAE[name]
        ok = abs(m - exp) < 8e-4
        print(f"anchor {name:16s}: {m:.4f} expected {exp} -> {'OK' if ok else 'FAIL'}")
        if not ok:
            anchor_fail.append(name)
    if anchor_fail:
        print(f"ANCHOR CHECK FAILED: {anchor_fail} — results_s20b.json MUST NOT be trusted")
        return 1

    # scored candidates on the frozen test
    mae8, rmse8, disj8 = rolling_metrics(stack8.predict(P_test), A_test)
    mae6, rmse6, disj6 = rolling_metrics(stack6.predict(P_test), A_test)
    mae_best_member, _, _ = rolling_metrics(P_test[:, 0, :], A_test)
    mae_mean8, _, _ = rolling_metrics(P_test.mean(axis=1), A_test)

    print(f"\n===============================================")
    print(f"8-MEMBER RIDGE MIXTURE (alpha={best_alpha})")
    print(f"  test rolling: {mae8:.4f} / {rmse8:.4f}")
    print(f"  disjoint: " + ", ".join(f"W{i+1} {disj8[f'window_{i+1}']['mae']:.4f}" for i in range(4)))
    print(f"  vs S-20 6-member incumbent 1.9980: {mae8 - 1.9980:+.4f}")
    print(f"  vs NLinear L336 2.0571:            {mae8 - 2.0571:+.4f}")
    print(f"internal baselines (same harness):")
    print(f"  6-member map (S-20 re-derived, alpha={best_alpha6}): {mae6:.4f} (expect ~1.9980)")
    print(f"  best member (NLinear L336):                  {mae_best_member:.4f}")
    print(f"  equal-mean-8:                                {mae_mean8:.4f}")
    print(f"===============================================")

    mean_coef = np.empty(P_test.shape[1])
    for j in range(P_test.shape[1]):
        mean_coef[j] = float(np.mean(stack8.coef[j, :]))

    out = {
        "slice": "S-20b",
        "protocol": {
            "members": [n for n, _ in MEMBERS],
            "map": "per-horizon multi-output ridge stacking, no intercept (S-20 P1)",
            "alpha_selection": "chronological: fit val origins [0,1080), select [1080,2161)",
            "alpha_candidates": ALPHAS,
            "history": "canonical full prefix (history_ = series[:origin]) for ALL members",
        },
        "validation": {
            "member_val_mae": {n: round(float(np.mean(np.abs(P_val[:, j, :] - A_val))), 4)
                               for j, (n, _) in enumerate(MEMBERS)},
            "alpha8_scores_second_half": {str(a): round(s, 4) for a, s in alpha_scores.items()},
            "selected_alpha": best_alpha,
            "refit_all_val_mae": round(val_mae8, 4),
            "alpha6_scores_second_half": {str(a): round(s, 4) for a, s in alpha6_scores.items()},
            "selected_alpha_6member": best_alpha6,
            "refit_all_val_mae_6member": round(val_mae6, 4),
        },
        "test": {
            "anchors": {n: round(float(np.mean(np.abs(P_test[:, j, :] - A_test))), 4)
                        for j, (n, _) in enumerate(MEMBERS)},
            "rolling_mae": round(mae8, 4),
            "rolling_rmse": round(rmse8, 4),
            "disjoint_windows": disj8,
            "delta_vs_s20_six_member": round(mae8 - 1.9980, 4),
            "delta_vs_nlinear": round(mae8 - 2.0571, 4),
            "baseline_6member_same_harness": round(mae6, 4),
            "baseline_best_member": round(mae_best_member, 4),
            "baseline_equal_mean_8": round(mae_mean8, 4),
            "mean_coef_per_member": {n: round(float(mean_coef[j]), 4)
                                     for j, (n, _) in enumerate(MEMBERS)},
        },
    }
    out_path = HERE / "results_s20b.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {out_path} (total {time.time() - t_all:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
