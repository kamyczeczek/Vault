"""S-19 — Validation-weighted 4-member ensemble: 3 linear rows + CycleESN.

Hypothesis (from S-18): CycleESN wins 3/4 disjoint test windows (W1 by -0.18,
NLinear's worst window) but loses the rolling mean. As a 4th member of the
S-17-style val-weighted ensemble, its long-memory reservoir features may hedge
the NLinear members' worst regimes — the L1/MAE-optimal sparse blend decides.

Members (all frozen-fit, no refit in the weight search):
  0  nlinear_L336_a1   NLinear(336, a=1)      2.0571 test (S-06)
  1  nlinear_L96_a1    NLinear(96,  a=1)      2.0925 test (S-06)
  2  dlinear_L96_k25   DLinear(96, k25, a=0)  2.1163 test (S-05)
  3  cycleesn_N32      CycleESN(336, N32, rc0.99, v0.05, skip, a=1)
                       val-rejected flip in S-18 (val 2.8593 / test 2.1063)

Protocol (identical to S-17):
  - Weight search: members frozen-fit on train 8,545 (CycleESN config from the
    S-18 val sweep — NO new hyperparameter search), 2,161 val origins, test
    never consulted.
  - Weight candidates: L2/Duchi blend and L1/MAE-optimal blend (both from
    methods.ensemble, S-08 solvers), plus each single member as a vertex.
  - Selection: argmin over {L2-blend, L1-blend, best-member} on VALIDATION MAE.
  - Frozen test: members re-fit on full 11,425, blended with selected weights,
    scored rolling 2,161 origins + disjoint windows.

Reuses the batch reservoir evaluation from cycle_esn_s18/fast_sweep.py
(vectorized over all origins) — CycleESN member predictions are computed in
ONE bulk pass, not per-origin predict() loops.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, DLinear
from methods.cycle_esn import CycleESN
from methods.ensemble import _simplex_project, _minimize_mae_weights

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545

CYCLE_ESN_CFG = dict(
    input_length=336, n_reservoir=32, rc=0.99, v=0.05,
    linear_skip=True, ridge_alpha=1.0,
)


def member_pred_batch_cesn(model: CycleESN, series: np.ndarray,
                           starts: np.ndarray) -> np.ndarray:
    """Vectorized CycleESN predictions for many window start indices.

    starts[i] = index in `series` where the L-length window begins.
    Returns (len(starts), H) predictions.
    """
    L = model.input_length
    H = model.horizon_
    win_idx = starts[:, None] + np.arange(L)
    windows = series[win_idx]                      # (n, L)
    anchors = windows[:, -1:]                      # (n, 1)
    windows_norm = windows - anchors

    N = model.n_reservoir
    V = model.V_[None, :]
    rc = model.rc
    states = np.zeros((len(starts), N), dtype=float)
    for k in range(L):
        u_k = windows_norm[:, k : k + 1]
        states = np.tanh(u_k * V + rc * np.roll(states, shift=1, axis=1))
    feats = np.hstack([windows_norm, states])      # skip=True always
    preds = model.model_.predict(feats) + anchors  # (n, H)
    return preds, anchors.squeeze(-1)


def member_pred_linear(model, series: np.ndarray, starts: np.ndarray,
                       L: int, H: int) -> np.ndarray:
    """Vectorized linear-member predictions (NLinear/DLinear) for many starts."""
    win_idx = starts[:, None] + np.arange(L)
    windows = series[win_idx]                      # (n, L)
    preds = []
    for w in windows:
        # NLinear/DLinear predict() consumes history_; swap-in pattern
        # is per-window but cheap (single sklearn predict per window).
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


def main():
    t_all = time.time()
    pd = get_protocol_data()
    fit_history, eval_series, test = pd.rolling_views()
    train_8545 = fit_history[:TRAIN_END]
    val = fit_history[TRAIN_END:]
    n_val = len(val) - HORIZON + 1
    assert len(train_8545) == 8545 and len(val) == 2880 and len(test) == 2880

    # ---------------------------------------------------------------
    # 1) Freeze all 4 members on train 8,545 (weight-search fit)
    # ---------------------------------------------------------------
    print("fitting members on train 8545 ...")
    members = []
    members.append(NLinear(input_length=336, ridge_alpha=1.0))
    members.append(NLinear(input_length=96, ridge_alpha=1.0))
    members.append(DLinear(input_length=96, kernel_size=25, ridge_alpha=0.0))
    members.append(CycleESN(**CYCLE_ESN_CFG))
    for m in members:
        m.fit(train_8545, horizon=HORIZON)
    print("  4 members fitted")

    member_names = ["nlinear_L336_a1", "nlinear_L96_a1",
                     "dlinear_L96_k25", "cycleesn_N32"]

    # ---------------------------------------------------------------
    # 2) Validation predictions: P (n_val, M, H), A (n_val, H)
    #    Window for val origin t starts at TRAIN_END + t - L.
    # ---------------------------------------------------------------
    print("collecting validation predictions ...")
    val_starts = np.arange(n_val) + TRAIN_END      # window start index
    P_val = np.empty((n_val, len(members), HORIZON))
    for j, m in enumerate(members):
        L = m.input_length
        starts = val_starts - L
        if isinstance(m, CycleESN):
            preds, _ = member_pred_batch_cesn(m, fit_history, starts)
        else:
            preds = member_pred_linear(m, fit_history, starts, L, HORIZON)
        P_val[:, j, :] = preds
    A_val = np.stack([val[t : t + HORIZON] for t in range(n_val)])

    # per-member val MAE (rolling mean over origins)
    member_val_mae = np.array([
        float(np.mean(np.mean(np.abs(P_val[:, j, :] - A_val), axis=1)))
        for j in range(len(members))
    ])
    for n_, m_ in zip(member_names, member_val_mae):
        print(f"  {n_:18s} val {m_:.4f}")
    best_member_j = int(np.argmin(member_val_mae))

    # residual correlation matrix (M x M) over val cells
    R_val = (P_val - A_val[:, None, :]).transpose(0, 2, 1).reshape(-1, len(members))
    corr = np.corrcoef(R_val.T)
    print("val residual pairwise corr:")
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            print(f"  {member_names[i]} | {member_names[j]} = {corr[i, j]:.4f}")

    # ---------------------------------------------------------------
    # 3) Weight candidates: L2 blend + L1/MAE optimum (S-08 solvers)
    # ---------------------------------------------------------------
    n_members = len(members)
    ones = np.ones(n_members)
    G = R_val.T @ R_val / len(R_val)
    try:
        w_dir = np.linalg.solve(G + 1e-9 * np.eye(n_members), ones)
        w_dir = w_dir / np.sum(w_dir)
    except np.linalg.LinAlgError:
        w_dir = ones / n_members
    w_l2 = _simplex_project(w_dir)
    if not np.isclose(w_l2.sum(), 1.0):
        w_l2 = ones / n_members

    w_l1, l1_val = _minimize_mae_weights(P_val, A_val)
    l2_val = float(np.mean(np.abs(R_val @ w_l2)))
    best_member_val = float(member_val_mae[best_member_j])

    print(f"\nL2 blend  w={np.round(w_l2, 4).tolist()}  val {l2_val:.4f}")
    print(f"L1 blend  w={np.round(w_l1, 4).tolist()}  val {l1_val:.4f}")
    print(f"best member {member_names[best_member_j]} val {best_member_val:.4f}")

    menu = [
        ("l2_blend", l2_val, w_l2),
        ("l1_blend", l1_val, w_l1),
        ("member", best_member_val, np.eye(n_members)[best_member_j]),
    ]
    sel_name, sel_val, sel_w = min(menu, key=lambda x: x[1])
    print(f"\nSELECTED: {sel_name} (val {sel_val:.4f}) w={np.round(sel_w, 4).tolist()}")

    # ---------------------------------------------------------------
    # 4) Frozen test: re-fit members on full 11,425, roll on test
    # ---------------------------------------------------------------
    print("\nre-fitting members on full 11425 ...")
    frozen = []
    frozen.append(NLinear(input_length=336, ridge_alpha=1.0))
    frozen.append(NLinear(input_length=96, ridge_alpha=1.0))
    frozen.append(DLinear(input_length=96, kernel_size=25, ridge_alpha=0.0))
    frozen.append(CycleESN(**CYCLE_ESN_CFG))
    for m in frozen:
        m.fit(fit_history, horizon=HORIZON)

    n_test = len(test) - HORIZON + 1
    test_starts = np.arange(n_test) + 11425        # window start in eval_series
    P_test = np.empty((n_test, n_members, HORIZON))
    for j, m in enumerate(frozen):
        L = m.input_length
        starts = test_starts - L
        if isinstance(m, CycleESN):
            preds, _ = member_pred_batch_cesn(m, eval_series, starts)
        else:
            preds = member_pred_linear(m, eval_series, starts, L, HORIZON)
        P_test[:, j, :] = preds

    A_test = np.stack([test[t : t + HORIZON] for t in range(n_test)])

    # blended test predictions
    pred_sel = np.einsum("m,nmh->nh", np.asarray(sel_w, dtype=float), P_test)
    err = pred_sel - A_test
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err**2, axis=1))
    test_mae = float(np.mean(mae_per))
    test_rmse = float(np.sqrt(np.mean(err**2)))
    disj = {
        f"window_{i+1}": {"mae": float(mae_per[t]), "rmse": float(rmse_per[t])}
        for i, t in enumerate(DISJOINT_STARTS)
    }

    # per-member test (for the record)
    member_test = {}
    for j, n_ in enumerate(member_names):
        me = P_test[:, j, :] - A_test
        member_test[n_] = {
            "rolling_mae": round(float(np.mean(np.mean(np.abs(me), axis=1))), 4),
            "rolling_rmse": round(float(np.sqrt(np.mean(me**2))), 4),
        }

    incumbent = 2.0519  # S-17 ensemble
    print(f"\n=================================================")
    print(f"SELECTED blend on TEST rolling: {test_mae:.4f} / {test_rmse:.4f}")
    print(f"disjoint: " + ", ".join(f"W{i+1} {disj[f'window_{i+1}']['mae']:.4f}" for i in range(4)))
    print(f"vs S-17 ensemble incumbent 2.0519: {test_mae - incumbent:+.4f}")
    print(f"vs NLinear L336 2.0571:            {test_mae - 2.0571:+.4f}")
    for n_ in member_names:
        print(f"  member {n_:18s} test {member_test[n_]['rolling_mae']:.4f}")
    print(f"=================================================")

    out = {
        "slice": "S-19",
        "protocol": {
            "members": member_names,
            "cycle_esn_cfg": CYCLE_ESN_CFG,
            "members_fit": "frozen; weight search on train 8,545, test fit on 11,425",
            "weights": "validation windows only (2,161 origins); test never consulted",
            "selection": "argmin over {L2-blend, L1-blend, best-member} on validation MAE",
        },
        "validation": {
            "member_val_mae": {n_: round(float(x), 4) for n_, x in zip(member_names, member_val_mae)},
            "w_l2": [round(float(x), 6) for x in w_l2],
            "w_l1": [round(float(x), 6) for x in w_l1],
            "l2_val_mae": round(l2_val, 4),
            "l1_val_mae": round(l1_val, 4),
            "best_member": member_names[best_member_j],
            "best_member_val_mae": round(best_member_val, 4),
            "selected_config": sel_name,
            "selected_val_mae": round(sel_val, 4),
            "selected_weights": [round(float(x), 6) for x in sel_w],
        },
        "residual_pairwise_corr": {
            f"{member_names[i]}|{member_names[j]}": round(float(corr[i, j]), 4)
            for i in range(n_members) for j in range(i + 1, n_members)
        },
        "test": {
            "selected_config": sel_name,
            "selected_weights": [round(float(x), 6) for x in sel_w],
            "rolling_mae": round(test_mae, 4),
            "rolling_rmse": round(test_rmse, 4),
            "disjoint_windows": disj,
            "members": member_test,
            "delta_vs_s17_ensemble": round(test_mae - incumbent, 4),
            "delta_vs_nlinear": round(test_mae - 2.0571, 4),
        },
    }
    out_path = HERE / "results_s19.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {out_path}  (total {time.time() - t_all:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
