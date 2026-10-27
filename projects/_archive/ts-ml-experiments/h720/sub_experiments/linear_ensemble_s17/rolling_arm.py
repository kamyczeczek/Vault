"""S-17 — validation-weighted convex ensemble of the top-3 linear models.

Question: do the top-3 linear leaderboard rows, which differ in lookback
and structural transform (and hence carry partially-decorrelated
extrapolation errors), admit a validation-selected convex blend that beats
the incumbent NLinear L336 (2.0571) on the test region?

Members (all frozen-fit, no refit in the weight search):
  0  nlinear_L336_a1   NLinear(input_length=336, ridge_alpha=1.0)   2.0571 (incumbent)
  1  nlinear_L96_a1    NLinear(input_length=96,  ridge_alpha=1.0)   2.0925
  2  dlinear_L96_k25   DLinear(input_length=96, kernel_size=25, ridge_alpha=0.0)  2.1163

Protocol (S-02, identical to S-08 / S-16c):
  - Members frozen-fit ONCE on the full fit history for the weight search
    (here: train 8,545 rows, so the weight search sees only the 8,545-row
    train prefix and NEVER the 2,880-row validation segment's future).
  - Weight search on VALIDATION windows only: the validation segment is the
    trailing 2,880 rows of train.csv (rows 8,545..11,425). Origins roll
    stride-1 (2,161 origins); per-origin history = all rows strictly before
    the scored window = train_8545 ++ val[:t]. Members stay frozen
    (only model.history_ is swapped; no refit).
  - Two weight sets, both deterministic, both fit on val windows only
    (reused from methods.ensemble — identical to S-08):
      L2   — equality-constrained least-squares solve + Euclidean simplex
             projection (Duchi et al. 2008).
      L1   — the L1 (MAE) optimum over the simplex via pairwise coordinate
             descent + exact ternary line search (global, deterministic).
    Validation MAE is also recorded for each member alone and for the best
    member, so the outcome (blend beats / loses to the vertex) is attributed
    to the data, not to a surrogate choice.
  - Selection: the frozen config scored on test is the argmin over
    {L2-blend, L1-blend, best-member} on VALIDATION MAE (a fixed 3-way
    menu, val-only — same shape as the S-16c α/k selection).
  - Test: members re-frozen on the full 11,425-row train.csv (the canonical
    frozen-fit protocol), blended with the selected weight vector, scored
    rolling (2,161 origins) against test.csv; disjoint windows incl. W4.
  - Test is never consulted for weighting or selection.

Outputs: results_s17.json + CONTEXT.md.
"""

from __future__ import annotations

import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, DLinear
from methods.ensemble import _simplex_project, _minimize_mae_weights

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545   # train.csv train prefix (fit region for weight search)
VALIDATION_ROWS = 2880

# (name, factory) — members are constructed fresh and frozen-fit in fit_members()
MEMBERS = (
    ("nlinear_L336_a1", lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L96_a1",  lambda: NLinear(input_length=96,  ridge_alpha=1.0)),
    ("dlinear_L96_k25", lambda: DLinear(input_length=96, kernel_size=25, ridge_alpha=0.0)),
)


def mae_rmse(p, a):
    err = np.asarray(p, float) - np.asarray(a, float)
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))


def fit_members(series):
    """Frozen-fit every member on ``series`` exactly once."""
    models = []
    for _, factory in MEMBERS:
        m = factory()
        m.fit(series, horizon=HORIZON)
        models.append(m)
    return models


def member_pred(models, idx, hist):
    """Swap the member's trailing history and predict (no refit)."""
    m = models[idx]
    orig = m.history_
    try:
        if m.history_.ndim == 2 and hist.ndim == 1:
            m.history_ = hist[:, None]
        else:
            m.history_ = hist
        return np.asarray(m.predict(), dtype=float)
    finally:
        m.history_ = orig


def member_preds_all(models, hist):
    return [member_pred(models, i, hist) for i in range(len(MEMBERS))]


def l2_weights(P, A):
    """Equality-constrained L2 solve + simplex projection (S-08 primary)."""
    n = P.shape[1]
    R = (P - A[:, None, :]).transpose(0, 2, 1).reshape(-1, n)
    G = R.T @ R / len(R)
    ones = np.ones(n)
    try:
        w_dir = np.linalg.solve(G + 1e-9 * np.eye(n), ones)
        w_dir = w_dir / np.sum(w_dir)
    except np.linalg.LinAlgError:
        w_dir = ones / n
    w = _simplex_project(w_dir)
    if not np.isclose(w.sum(), 1.0):
        w = ones / n
    return w


def blended(val_maes_members, w):
    return float(sum(wi * mi for wi, mi in zip(w, val_maes_members)))


def select_val(models, series, val_start):
    """Roll validation windows; fit L2 + L1 weights; return record + preds."""
    val = series[val_start:]
    n_origins = len(val) - HORIZON + 1
    preds, actuals = [], []
    for t in range(n_origins):
        hist = series[:val_start + t]
        preds.append(member_preds_all(models, hist))
        actuals.append(val[t:t + HORIZON])
    P = np.asarray(preds)     # (n, M, H)
    A = np.asarray(actuals)   # (n, H)

    # per-member val MAE (rolling, per-origin mean, then origin-mean)
    member_mae = np.empty(P.shape[1])
    for j in range(P.shape[1]):
        per = [np.mean(np.abs(P[t, j] - A[t])) for t in range(n_origins)]
        member_mae[j] = float(np.mean(per))
    best_member = int(np.argmin(member_mae))

    w_l2 = l2_weights(P, A)
    w_l1, l1_val = _minimize_mae_weights(P, A)

    # val MAE of each candidate blend config
    # L2 blend (closed-form w) and L1 blend (convex-MAE optimum w)
    R = (P - A[:, None, :]).transpose(0, 2, 1).reshape(-1, P.shape[1])
    l2_val = float(np.mean(np.abs(R @ w_l2)))
    l1_val = float(l1_val)
    best_member_val = float(member_mae[best_member])

    # select argmin over the fixed 3-way menu on val MAE
    menu = [
        ("l2_blend",  l2_val,  w_l2),
        ("l1_blend",  l1_val,  w_l1),
        ("member",    best_member_val,
         np.eye(len(MEMBERS))[best_member]),
    ]
    sel_name, sel_val, sel_w = min(menu, key=lambda x: x[1])

    return {
        "member_names": [n for n, _ in MEMBERS],
        "member_val_mae": [round(float(x), 4) for x in member_mae],
        "best_member": best_member,
        "best_member_name": MEMBERS[best_member][0],
        "w_l2": [round(float(x), 6) for x in w_l2],
        "w_l1": [round(float(x), 6) for x in w_l1],
        "l2_val_mae": round(l2_val, 4),
        "l1_val_mae": round(l1_val, 4),
        "best_member_val_mae": round(best_member_val, 4),
        "selected_config": sel_name,
        "selected_val_mae": round(sel_val, 4),
        "selected_weights": [round(float(x), 6) for x in sel_w],
    }, (P, A)


def rolling_test(models, w, eval_series, test):
    """Frozen members + fixed weights -> rolling test MAE/RMSE + disjoint."""
    n = len(test) - HORIZON + 1
    per = np.empty((n, 2), float)
    for t in range(n):
        hist = eval_series[:11425 + t]
        ps = member_preds_all(models, hist)
        pred = sum(wi * p for wi, p in zip(w, ps))
        per[t] = mae_rmse(pred, test[t:t + HORIZON])
    disj = {
        f"window_{i+1}": {"mae": float(per[t, 0]), "rmse": float(per[t, 1])}
        for i, t in enumerate(DISJOINT_STARTS)
    }
    return float(np.mean(per[:, 0])), float(np.mean(per[:, 1])), disj


def rolling_member_test(models, idx, eval_series, test):
    """A single frozen member -> rolling test MAE (for the delta)."""
    n = len(test) - HORIZON + 1
    per = np.empty((n, 2), float)
    for t in range(n):
        hist = eval_series[:11425 + t]
        per[t] = mae_rmse(member_pred(models, idx, hist), test[t:t + HORIZON])
    disj = {
        f"window_{i+1}": {"mae": float(per[t, 0]), "rmse": float(per[t, 1])}
        for i, t in enumerate(DISJOINT_STARTS)
    }
    return float(np.mean(per[:, 0])), float(np.mean(per[:, 1])), disj


def main():
    pd = get_protocol_data()
    fit_history, eval_series, test = pd.rolling_views()
    train_8545 = fit_history[:TRAIN_END]
    val = fit_history[TRAIN_END:]
    assert len(train_8545) == 8545 and len(val) == 2880 and len(test) == 2880
    print(f"train {len(train_8545)} val {len(val)} test {len(test)}")

    # --- weight search: freeze members on train 8545, select on val ------
    sel_models = fit_members(train_8545)
    print("members frozen on train 8545")
    sel, (P, A) = select_val(sel_models, fit_history, TRAIN_END)
    print(json.dumps({k: v for k, v in sel.items() if k != "member_val_mae"}, indent=2))
    print("member val MAE:", dict(zip(sel["member_names"], sel["member_val_mae"])))

    # error-decorrelation diagnostic: pairwise correlation of member
    # validation residuals (explains why/why-not a blend beats the vertex).
    R = (P - A[:, None, :]).transpose(0, 2, 1).reshape(-1, P.shape[1])
    corr = np.corrcoef(R.T)
    print("val residual pairwise corr:\n" +
          "\n".join(f"  {sel['member_names'][i]} / {sel['member_names'][j]} = {corr[i][j]:.4f}"
                   for i in range(P.shape[1]) for j in range(i + 1, P.shape[1])))

    sel_w = np.asarray(sel["selected_weights"], dtype=float)

    # --- test: re-freeze members on full 11,425, blend with selected w ---
    frozen = fit_members(fit_history)
    print("members re-frozen on full train 11425")

    rm, rr, disj = rolling_test(frozen, sel_w, eval_series, test)
    print(f"SELECTED blend ({sel['selected_config']}, w={sel_w.tolist()}) on test "
          f"rolling {rm:.4f} / {rr:.4f}  W4 {disj['window_4']['mae']:.4f}")

    # reference members on test (delta vs incumbent NLinear L336)
    ref = {}
    for i, (name, _) in enumerate(MEMBERS):
        mi, ri, _ = rolling_member_test(frozen, i, eval_series, test)
        ref[name] = {"test_mae": round(mi, 4), "test_rmse": round(ri, 4)}
        print(f"  {name:18s} test {mi:.4f}")
    incumbent = ref["nlinear_L336_a1"]["test_mae"]
    print(f"incumbent nlinear_L336_a1 test {incumbent:.4f}   "
          f"delta selected-incumbent {rm - incumbent:+.4f}")

    out = {
        "slice": "S-17",
        "protocol": {
            "members": [n for n, _ in MEMBERS],
            "members_fit": "frozen; weight search on train 8,545, test on full 11,425",
            "weights": "validation windows only (2,161 origins, train 8,545 fit); test never consulted",
            "selection": "argmin over {L2-blend, L1-blend, best-member} on validation MAE",
            "scoring": "rolling stride-1, 2,161 origins, full test region",
            "horizon": HORIZON,
        },
        "validation": sel,
        "residual_pairwise_corr": {
            f"{sel['member_names'][i]}|{sel['member_names'][j]}": round(float(corr[i][j]), 4)
            for i in range(P.shape[1]) for j in range(i + 1, P.shape[1])
        },
        "test": {
            "selected_config": sel["selected_config"],
            "selected_weights": sel["selected_weights"],
            "rolling_mae": round(rm, 4),
            "rolling_rmse": round(rr, 4),
            "disjoint_windows": disj,
            "members": ref,
            "incumbent_nlinear_L336": incumbent,
            "delta_vs_incumbent": round(rm - incumbent, 4),
        },
    }
    out_path = HERE / "results_s17.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
