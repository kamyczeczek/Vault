"""S-21 — Decision-tree heads on the S-20 six-linear-member stack.

User proposal: replace the per-horizon ridge head with a decision tree.
The ridge map is a weighted sum — on collinear linear members it can only
express "member mix X at horizon h". A tree can express REGIME SWITCHING:
e.g. "when the members disagree (high spread), trust the member whose
pattern matches the current regime; when they agree, the blend is fine" —
non-linear interactions over the same 6 predictions that ridge cannot.

Two tree forms (both on the SAME 6 linear members, NO non-linears — S-20b
proved them dead weight):
  A) per-horizon trees: 720 small trees, tree_h fit on P[:, :, h] (the
     direct replacement of S-20's 720 ridge maps); grid (depth, leaf).
  B) shared tree: ONE tree with 7 features = [6 member preds, horizon
     step]; the per-horizon split structure is expressible inside it at a
     fraction of the DOF; grid depth.

Protocol (S-20 exactly): members frozen on train 8,545; grid selected on
the held-out SECOND val half (fit first [0,1080), select [1080,2161),
pooled MAE over all horizons); selected config refit on ALL val; members
re-frozen on 11,425; test never consulted. Control: the S-20 per-horizon
ridge map (alpha=3000) re-derived in-harness (expect ~1.9980 test).
Fail-loud member anchors: all 6 leaderboard numbers.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.tree import DecisionTreeRegressor

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, DLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
VALIDATION_END = 11425

MEMBERS = [
    ("nlinear_L336_a1", lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L96_a1",  lambda: NLinear(input_length=96,  ridge_alpha=1.0)),
    ("nlinear_L720_a1", lambda: NLinear(input_length=720, ridge_alpha=1.0)),
    ("dlinear_L96_a0",   lambda: DLinear(input_length=96,  kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L336_a0",  lambda: DLinear(input_length=336, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L720_a0",  lambda: DLinear(input_length=720, kernel_size=25, ridge_alpha=0.0)),
]

ANCHOR_TEST_MAE = {
    "nlinear_L336_a1": 2.0571,
    "nlinear_L96_a1": 2.0925,
    "nlinear_L720_a1": 2.1534,
    "dlinear_L96_a0": 2.1163,
    "dlinear_L336_a0": 2.1220,
    "dlinear_L720_a0": 2.1687,
}

PER_HORIZON_GRID = [(2, 10), (3, 10), (3, 25), (4, 10), (4, 25), (5, 25)]
SHARED_GRID = [(3, 25), (4, 25), (5, 25), (6, 25), (7, 25), (8, 25)]
RIDGE_ALPHA_CONTROL = 3000.0


def collect_preds(models, series, n, base) -> np.ndarray:
    """P (n, M, H); history_ = full prefix before the scored window
    (canonical rolling; linears read only their trailing window)."""
    P = np.empty((n, len(models), HORIZON))
    for j, m in enumerate(models):
        for t in range(n):
            orig = m.history_
            try:
                m.history_ = series[: base + t]
                P[t, j, :] = np.asarray(m.predict(), dtype=float)
            finally:
                m.history_ = orig
    return P


def fit_per_horizon_trees(P, A, depth, leaf):
    """720 DecisionTreeRegressor, one per horizon step. Returns predict fn."""
    trees = []
    for h in range(HORIZON):
        trees.append(DecisionTreeRegressor(
            max_depth=depth, min_samples_leaf=leaf, random_state=42
        ).fit(P[:, :, h], A[:, h]))

    def predict(Pt):
        out = np.empty((Pt.shape[0], HORIZON))
        for h, tr in enumerate(trees):
            out[:, h] = tr.predict(Pt[:, :, h])
        return out

    predict.n_leaves = [int(t.tree_.node_count) for t in trees]
    predict.max_depth = [int(getattr(t, "get_depth()", 0)) for t in trees]
    return predict


def shared_X(P):
    """(n, H, 7): member preds + horizon step, flattened to (n*H, 7)."""
    n = P.shape[0]
    X = np.empty((n * HORIZON, P.shape[1] + 1))
    X[:, :P.shape[1]] = P.transpose(0, 2, 1).reshape(-1, P.shape[1])
    X[:, P.shape[1]] = np.tile(np.arange(HORIZON), n)
    return X


def fit_shared_tree(P, A, depth, leaf):
    tree = DecisionTreeRegressor(
        max_depth=depth, min_samples_leaf=leaf, random_state=42
    ).fit(shared_X(P), A.reshape(-1))
    n_leaves = int(tree.tree_.node_count)

    def predict(Pt):
        out = tree.predict(shared_X(Pt)).reshape(Pt.shape[0], HORIZON)
        return out

    predict.n_leaves = [n_leaves]
    return predict


def rolling_metrics(preds, actuals):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    disj = {f"window_{i+1}": {"mae": float(mae_per[t])}
            for i, t in enumerate(DISJOINT_STARTS)}
    return float(mae_per.mean()), float(np.sqrt(np.mean(err**2))), disj


def main():
    t_all = time.time()
    pd = get_protocol_data()
    fit_history, eval_series, test = pd.rolling_views()
    train_8545 = fit_history[:TRAIN_END]
    n_val = len(fit_history) - TRAIN_END - HORIZON + 1
    n_test = len(test) - HORIZON + 1
    assert n_val == 2161 and n_test == 2161

    print("fitting 6 members on train 8545 ...")
    models = [f().fit(train_8545, horizon=HORIZON) for _, f in MEMBERS]
    print("collecting val predictions ...")
    P_val = collect_preds(models, fit_history, n_val, TRAIN_END)
    A_val = np.stack([fit_history[TRAIN_END + t: TRAIN_END + t + HORIZON] for t in range(n_val)])
    for j, (name, _) in enumerate(MEMBERS):
        print(f"  {name:16s} val {float(np.mean(np.abs(P_val[:, j, :] - A_val))):.4f}")

    n_fit = n_val // 2
    P_fit, A_fit = P_val[:n_fit], A_val[:n_fit]
    P_sel, A_sel = P_val[n_fit:], A_val[n_fit:]

    def pooled_second_half(pred_fn):
        return float(np.mean(np.abs(pred_fn(P_sel) - A_sel)))

    # --- grid selection on held-out second val half ---------------------
    print(f"\nPER-HORIZON tree grid (fit {n_fit} origins, select {n_val - n_fit}) ...")
    ph_scores = {}
    for depth, leaf in PER_HORIZON_GRID:
        t0 = time.time()
        ph_scores[(depth, leaf)] = pooled_second_half(
            fit_per_horizon_trees(P_fit, A_fit, depth, leaf))
        print(f"  depth {depth} leaf {leaf}: 2nd-half val MAE {ph_scores[(depth, leaf)]:.4f} ({time.time() - t0:.1f}s)")
    best_ph = min(ph_scores, key=ph_scores.get)
    print(f"best per-horizon: depth {best_ph[0]} leaf {best_ph[1]} ({ph_scores[best_ph]:.4f})")

    print("\nSHARED tree grid (horizon step as 7th feature) ...")
    sh_scores = {}
    for depth, leaf in SHARED_GRID:
        t0 = time.time()
        sh_scores[(depth, leaf)] = pooled_second_half(
            fit_shared_tree(P_fit, A_fit, depth, leaf))
        print(f"  depth {depth} leaf {leaf}: 2nd-half val MAE {sh_scores[(depth, leaf)]:.4f} ({time.time() - t0:.1f}s)")
    best_sh = min(sh_scores, key=sh_scores.get)
    print(f"best shared: depth {best_sh[0]} leaf {best_sh[1]} ({sh_scores[best_sh]:.4f})")

    # ridge control (S-20) at its selected alpha, same fit/select halves
    t0 = time.time()
    ridge_coef = np.empty((6, HORIZON))
    for h in range(HORIZON):
        r = Ridge(alpha=RIDGE_ALPHA_CONTROL, fit_intercept=False).fit(P_fit[:, :, h], A_fit[:, h])
        ridge_coef[:, h] = r.coef_
    ridge_sel = float(np.mean(np.abs(
        np.einsum("mh,nmh->nh", ridge_coef, P_sel) - A_sel)))
    print(f"ridge control (alpha={RIDGE_ALPHA_CONTROL:g}, S-20 config): "
          f"2nd-half val MAE {ridge_sel:.4f} ({time.time() - t0:.1f}s)")

    # --- refit winners on ALL val, freeze --------------------------------
    pred_ph = fit_per_horizon_trees(P_val, A_val, *best_ph)
    pred_sh = fit_shared_tree(P_val, A_val, *best_sh)
    for h in range(HORIZON):
        r = Ridge(alpha=RIDGE_ALPHA_CONTROL, fit_intercept=False).fit(P_val[:, :, h], A_val[:, h])
        ridge_coef[:, h] = r.coef_

    val_mae_ph = float(np.mean(np.abs(pred_ph(P_val) - A_val)))
    val_mae_sh = float(np.mean(np.abs(pred_sh(P_val) - A_val)))
    val_mae_rg = float(np.mean(np.abs(np.einsum("mh,nmh->nh", ridge_coef, P_val) - A_val)))
    print(f"\nrefit all val (in-sample): per-horizon {val_mae_ph:.4f} / "
          f"shared {val_mae_sh:.4f} / ridge {val_mae_rg:.4f}")

    # --- frozen test ------------------------------------------------------
    print("\nre-fitting 6 members on full 11425 ...")
    frozen = [f().fit(fit_history, horizon=HORIZON) for _, f in MEMBERS]
    print("collecting test predictions ...")
    P_test = collect_preds(frozen, eval_series, n_test, VALIDATION_END)
    A_test = np.stack([test[t: t + HORIZON] for t in range(n_test)])

    anchor_fail = []
    for j, (name, _) in enumerate(MEMBERS):
        m = float(np.mean(np.abs(P_test[:, j, :] - A_test)))
        ok = abs(m - ANCHOR_TEST_MAE[name]) < 8e-4
        print(f"anchor {name:16s}: {m:.4f} expected {ANCHOR_TEST_MAE[name]} -> {'OK' if ok else 'FAIL'}")
        if not ok:
            anchor_fail.append(name)
    if anchor_fail:
        print(f"ANCHOR CHECK FAILED: {anchor_fail} — results_s21.json MUST NOT be trusted")
        return 1

    t0 = time.time()
    preds_ph = pred_ph(P_test)
    t_ph = time.time() - t0
    t0 = time.time()
    preds_sh = pred_sh(P_test)
    t_sh = time.time() - t0
    preds_rg = np.einsum("mh,nmh->nh", ridge_coef, P_test)

    mae_ph, rmse_ph, disj_ph = rolling_metrics(preds_ph, A_test)
    mae_sh, rmse_sh, disj_sh = rolling_metrics(preds_sh, A_test)
    mae_rg, rmse_rg, disj_rg = rolling_metrics(preds_rg, A_test)
    mae_best, _, _ = rolling_metrics(P_test[:, 0, :], A_test)
    mae_mean, _, _ = rolling_metrics(P_test.mean(axis=1), A_test)

    print(f"\n===============================================")
    print(f"PER-HORIZON TREE (d{best_ph[0]}/l{best_ph[1]}), {len(pred_ph.n_leaves)} trees, "
          f"max leaves {max(pred_ph.n_leaves)}, predict {t_ph:.1f}s")
    print(f"  test rolling: {mae_ph:.4f} / {rmse_ph:.4f}")
    print(f"  disjoint: " + ", ".join(f"W{i+1} {disj_ph[f'window_{i+1}']['mae']:.4f}" for i in range(4)))
    print(f"  vs S-20 ridge incumbent 1.9980: {mae_ph - 1.9980:+.4f}")
    print(f"SHARED TREE (d{best_sh[0]}/l{best_sh[1]}), leaves {pred_sh.n_leaves[0]}, predict {t_sh:.1f}s")
    print(f"  test rolling: {mae_sh:.4f} / {rmse_sh:.4f}")
    print(f"  disjoint: " + ", ".join(f"W{i+1} {disj_sh[f'window_{i+1}']['mae']:.4f}" for i in range(4)))
    print(f"  vs S-20 ridge incumbent 1.9980: {mae_sh - 1.9980:+.4f}")
    print(f"RIDGE CONTROL (alpha={RIDGE_ALPHA_CONTROL:g}, S-20 re-derived): {mae_rg:.4f} (expect ~1.9980)")
    print(f"baselines: best member {mae_best:.4f}, equal-mean {mae_mean:.4f}")
    print(f"===============================================")

    winner = "per_horizon" if mae_ph < mae_sh else "shared"
    out = {
        "slice": "S-21",
        "protocol": {
            "members": [n for n, _ in MEMBERS],
            "heads": ["per-horizon DecisionTreeRegressor (720 trees)",
                      "shared DecisionTreeRegressor (horizon step as feature)"],
            "selection": "grid on held-out second val half, pooled MAE over horizons",
            "test": "frozen; members refit on 11,425; test never consulted",
        },
        "validation": {
            "per_horizon_grid": {f"d{d}_l{l}": round(s, 4) for (d, l), s in ph_scores.items()},
            "shared_grid": {f"d{d}_l{l}": round(s, 4) for (d, l), s in sh_scores.items()},
            "ridge_control_second_half": round(ridge_sel, 4),
            "refit_all_val_insample": {
                "per_horizon": round(val_mae_ph, 4),
                "shared": round(val_mae_sh, 4),
                "ridge": round(val_mae_rg, 4),
            },
        },
        "test": {
            "anchors": {n: round(float(np.mean(np.abs(P_test[:, j, :] - A_test))), 4)
                        for j, (n, _) in enumerate(MEMBERS)},
            "per_horizon": {
                "config": list(best_ph),
                "rolling_mae": round(mae_ph, 4), "rolling_rmse": round(rmse_ph, 4),
                "disjoint_windows": disj_ph,
                "delta_vs_s20": round(mae_ph - 1.9980, 4),
            },
            "shared": {
                "config": list(best_sh),
                "rolling_mae": round(mae_sh, 4), "rolling_rmse": round(rmse_sh, 4),
                "disjoint_windows": disj_sh,
                "delta_vs_s20": round(mae_sh - 1.9980, 4),
            },
            "ridge_control": {
                "rolling_mae": round(mae_rg, 4),
                "delta_vs_s20": round(mae_rg - 1.9980, 4),
            },
            "baseline_best_member": round(mae_best, 4),
            "baseline_equal_mean": round(mae_mean, 4),
            "winner_by_rolling": winner,
        },
    }
    out_path = HERE / "results_s21.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {out_path} (total {time.time() - t_all:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
