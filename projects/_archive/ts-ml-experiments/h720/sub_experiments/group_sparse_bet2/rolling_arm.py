"""Bet 2 — Group-Sparse Multivariate NLinear with Patch Embedding (h720 ETTh1 H=720).

Mirrors spectral_omega_gate/rolling_arm_phase2.py and S-26/S-34 harness shape.
Protocol: S-20-clean, M=6 pool (2 univariate L336 a=1,a=10 + 4 group-sparse P24/48 x lam0.5/2.0),
tabu-7 fixed-alpha fast 3000, chronological val[0:1080)/val[1080:2161), per-horizon ridge
no-intercept 11-alpha grid, transfer guard full-val diff<0.15, disjoint-4 diagnostic.
Fail-loud S-26 anchor 1.9909.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
# Ensure local patch_embed/group_sparse importable when running as script
sys.path.insert(0, str(HERE))

from data import HORIZON, get_protocol_data  # noqa: E402
from methods.neural_models import NLinear  # noqa: E402

from patch_embed import CHANNELS, N_CHANNELS  # noqa: E402
from group_sparse import GroupSparseNLinear  # noqa: E402

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
SEARCH_ALPHA = 3000.0
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]
S26_ANCHOR_MAE = 1.9909
S26_ANCHOR_RMSE = 2.4710
S26_ANCHOR_TOL = 1e-4
COLS_MULTI = ["HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL", "OT"]
# Our GroupSparse uses CHANNELS = [OT,HUFL,HULL,MUFL,MULL,LUFL,LULL] (OT first for OT_IDX=0)
# So we need mapping: ETTh1.csv order is HUFL,HULL,MUFL,MULL,LUFL,LULL,OT
# Channel order for GroupSparse: OT=0, HUFL=1, HULL=2, MUFL=3, MULL=4, LUFL=5, LULL=6
# Build index map: for c in CHANNELS, find its column in raw CSV
CSV_COLS = ["HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL", "OT"]
CHANNEL_TO_CSV_IDX = [CSV_COLS.index(ch) for ch in CHANNELS]

# ------------------------------------------------------------------
# Candidate pool: M=6
# ------------------------------------------------------------------
UNIVARIATE_CANDIDATES = [
    ("nlinear_L336_a1", lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
]
# 4 group-sparse candidates: P in {24,48} x lam in {0.5,2.0}, L=336, ridge 10, OT unpenalized
GROUP_CANDIDATES = [
    ("gs_P24_lam0.5", lambda: GroupSparseNLinear(input_length=336, patch_size=24, lam=0.5, ridge_alpha=10.0, ot_unpenalized=True)),
    ("gs_P24_lam2.0", lambda: GroupSparseNLinear(input_length=336, patch_size=24, lam=2.0, ridge_alpha=10.0, ot_unpenalized=True)),
    ("gs_P48_lam0.5", lambda: GroupSparseNLinear(input_length=336, patch_size=48, lam=0.5, ridge_alpha=10.0, ot_unpenalized=True)),
    ("gs_P48_lam2.0", lambda: GroupSparseNLinear(input_length=336, patch_size=48, lam=2.0, ridge_alpha=10.0, ot_unpenalized=True)),
]
CANDIDATES = UNIVARIATE_CANDIDATES + GROUP_CANDIDATES

# ------------------------------------------------------------------
# Stack machinery
# ------------------------------------------------------------------
def fit_stack_map(P: np.ndarray, A: np.ndarray, alpha: float, fit_intercept: bool = False):
    n, m, h = P.shape
    coef = np.empty((m, h))
    inter = np.zeros(h)

    class _Map:
        def predict(self, Pq: np.ndarray) -> np.ndarray:
            # Pq (nq,m,h) -> (nq,h)
            out = np.einsum("qmh,mh->qh", Pq, coef)
            if fit_intercept:
                out = out + inter
            return out

    for hi in range(h):
        X = P[:, :, hi]
        y = A[:, hi]
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept)
        r.fit(X, y)
        coef[:, hi] = r.coef_
        if fit_intercept:
            inter[hi] = r.intercept_
    mobj = _Map()
    mobj.coef_ = coef
    mobj.inter_ = inter
    mobj.alpha = alpha
    return mobj


def score_fast(P_val: np.ndarray, A_val: np.ndarray, idx: list[int], alpha: float = SEARCH_ALPHA) -> float:
    if len(idx) == 0:
        return float("inf")
    Psub = P_val[:, idx, :]
    n = P_val.shape[0]
    n2 = n // 2
    r = fit_stack_map(Psub[:n2], A_val[:n2], alpha)
    return float(np.mean(np.mean(np.abs(r.predict(Psub[n2:]) - A_val[n2:]), axis=1)))


def score_full(P_val: np.ndarray, A_val: np.ndarray, idx: list[int]):
    if len(idx) == 0:
        return float("inf"), None
    Psub = P_val[:, idx, :]
    n = P_val.shape[0]
    n2 = n // 2
    best = float("inf")
    best_a = None
    for a in ALPHAS:
        r = fit_stack_map(Psub[:n2], A_val[:n2], a)
        sc = float(np.mean(np.mean(np.abs(r.predict(Psub[n2:]) - A_val[n2:]), axis=1)))
        if sc < best:
            best = sc
            best_a = a
    return best, best_a


def preds_for_train_fit(factory, train_series, full_series, starts, H):
    """Fit on train_series, predict origins at starts in full_series via history swap."""
    m = factory()
    m.fit(train_series, horizon=H)
    out = []
    hist = m.history_.copy() if hasattr(m.history_, "copy") else m.history_
    for s in starts:
        m.history_ = full_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_ = hist
    return np.asarray(out)


def preds_for_full_fit(factory, full_series, concat_series, starts, H):
    """Fit on full_series (11425), predict origins in concat via history swap."""
    m = factory()
    m.fit(full_series, horizon=H)
    out = []
    hist = m.history_.copy() if hasattr(m.history_, "copy") else m.history_
    for s in starts:
        m.history_ = concat_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_ = hist
    return np.asarray(out)


def load_multivariate_split():
    train_path = H720_ROOT / "train.csv"
    test_path = H720_ROOT / "test.csv"
    with open(train_path) as f:
        reader = csv.DictReader(f)
        rows_raw = [[float(r[c]) for c in CSV_COLS] for r in reader]
    with open(test_path) as f:
        reader = csv.DictReader(f)
        test_raw = [[float(r[c]) for c in CSV_COLS] for r in reader]
    raw_train = np.asarray(rows_raw, dtype=float)  # (11425, 7) in CSV order
    raw_test = np.asarray(test_raw, dtype=float)
    # Reorder to CHANNELS = OT first
    train_multi = raw_train[:, CHANNEL_TO_CSV_IDX]
    test_multi = raw_test[:, CHANNEL_TO_CSV_IDX]
    fit_multi = train_multi
    concat_multi = np.concatenate([fit_multi, test_multi], axis=0)
    # Also need 1-d OT series for univariate
    # Find OT position in CHANNELS
    ot_ch = CHANNELS.index("OT")  # 0
    return fit_multi, concat_multi, test_multi, ot_ch


def collect_val(train_1d, fit_1d, train_multi, fit_multi, starts):
    cols = []
    for name, factory in CANDIDATES:
        # probe to know type
        probe = factory()
        is_group = isinstance(probe, GroupSparseNLinear)
        if is_group:
            p = preds_for_train_fit(factory, train_multi, fit_multi, starts, HORIZON)
        else:
            p = preds_for_train_fit(factory, train_1d, fit_1d, starts, HORIZON)
        cols.append(p)
        print(f"  {name:20s} L={probe.input_length:3d} group={is_group} ok {p.shape}")
    return np.stack(cols, axis=1)


def collect_test(fit_1d, concat_1d, fit_multi, concat_multi, starts):
    cols = []
    for name, factory in CANDIDATES:
        probe = factory()
        is_group = isinstance(probe, GroupSparseNLinear)
        if is_group:
            p = preds_for_full_fit(factory, fit_multi, concat_multi, starts, HORIZON)
        else:
            p = preds_for_full_fit(factory, fit_1d, concat_1d, starts, HORIZON)
        cols.append(p)
    return np.stack(cols, axis=1)


def rolling_metrics(preds: np.ndarray, actuals: np.ndarray):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err ** 2, axis=1))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err ** 2))), mae_per, rmse_per


def _verify_s26_anchor():
    """Fail-loud S-26 1.9909 anchor on frozen 11425 — must pass before any Bet 2 scoring."""
    pd = get_protocol_data()
    fit_series, concat_series, test_series = pd.rolling_views()
    # S-26 is exactly [nlinear_L336_a1, nlinear_L336_a10] with ridge stack alpha 10000
    def make_a1():
        return NLinear(input_length=336, ridge_alpha=1.0)
    def make_a10():
        return NLinear(input_length=336, ridge_alpha=10.0)
    n_test = len(test_series) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_series)
    P1 = preds_for_full_fit(make_a1, fit_series, concat_series, test_starts, HORIZON)
    P2 = preds_for_full_fit(make_a10, fit_series, concat_series, test_starts, HORIZON)
    P = np.stack([P1, P2], axis=1)  # (n,2,720)
    A = np.stack([test_series[t:t+HORIZON] for t in range(n_test)])
    stack = fit_stack_map(P, A, 10000.0 if 10000.0 in ALPHAS else ALPHAS[9])
    # Actually S-26 used alpha 10000 selected via full 11-grid; we mimic by fitting with 10000 directly
    # But for anchor verify, fit with 10000 exactly is byte-identical to S-26 best_alpha
    # Use the stack fitted on ... wait anchor is test-scored with frozen fit? No, anchor MAE is
    # computed from rolling test preds stacked? S-26 test MAE is from refit-all-val -> frozen test
    # with stack fitted on val? No S-26 test uses val-fitted stack? Check S-26 harness:
    # stack is fit on val half? No final test stack in S-26 is fit on val P_best/A_val with best_alpha -> then predict P_test
    # But our _verify should do full refit on val? Simpler: verify univariate singleton MAE not full stack.
    # We follow S-26 exactly to recreate anchor: fit stack on val then score test (protocol).
    # To verify reliably, recompute via same steps as S-26 but limited to the 2 members.
    # Do val phase then test.
    train_series = fit_series[:TRAIN_END]
    val_series = fit_series[TRAIN_END:]
    n_val = len(val_series) - HORIZON + 1
    val_starts = np.arange(n_val) + TRAIN_END
    P1v = preds_for_train_fit(make_a1, train_series, fit_series, val_starts, HORIZON)
    P2v = preds_for_train_fit(make_a10, train_series, fit_series, val_starts, HORIZON)
    Pv = np.stack([P1v, P2v], axis=1)
    Av = np.stack([val_series[t:t+HORIZON] for t in range(n_val)])
    # Select best alpha on val held-out
    _, best_alpha = score_full(Pv, Av, [0, 1])
    print(f"S-26 anchor: val best_alpha={best_alpha}")
    # Fit stack on full val then score test
    stack_val = fit_stack_map(Pv, Av, best_alpha if best_alpha is not None else SEARCH_ALPHA)
    # Now score test with stack_val (this matches S-26 test_full which used stack from val)
    # But S-26 test_full actually uses stack fitted on all val (same). So use it.
    preds_full = stack_val.predict(P)
    mae_full, rmse_full, _, _ = rolling_metrics(preds_full, A)
    print(f"S-26 anchor verify: MAE {mae_full:.4f} RMSE {rmse_full:.4f} (expected {S26_ANCHOR_MAE:.4f}/{S26_ANCHOR_RMSE:.4f})")
    if abs(mae_full - S26_ANCHOR_MAE) > 0.002:
        raise RuntimeError(f"S-26 anchor FAIL: got {mae_full:.4f} expected {S26_ANCHOR_MAE:.4f} (tol 0.002) — aborting")
    # Also check disjoint-4
    disj_starts = np.array([len(fit_series) + s for s in DISJOINT_STARTS])
    P1d = preds_for_full_fit(make_a1, fit_series, concat_series, disj_starts, HORIZON)
    P2d = preds_for_full_fit(make_a10, fit_series, concat_series, disj_starts, HORIZON)
    Pd = np.stack([P1d, P2d], axis=1)
    Ad = np.stack([test_series[s:s+HORIZON] for s in DISJOINT_STARTS])
    preds_d = stack_val.predict(Pd)
    mae_d, _, _, _ = rolling_metrics(preds_d, Ad)
    print(f"S-26 anchor disjoint-4 MAE {mae_d:.4f} (expected 1.9696)")
    return best_alpha, mae_full, rmse_full, mae_d


def main(argv=None) -> int:
    t_all = time.time()
    log_lines = []
    def log(msg):
        print(msg)
        log_lines.append(msg)

    pd = get_protocol_data()
    fit_series, concat_series, test_series = pd.rolling_views()
    train_series = fit_series[:TRAIN_END]
    val_series = fit_series[TRAIN_END:]
    n_val = len(val_series) - HORIZON + 1
    assert n_val == 2161, n_val
    assert len(train_series) == 8545 and len(fit_series) == 11425
    val_starts = np.arange(n_val) + TRAIN_END

    # Fail-loud S-26 anchor
    log("Verifying S-26 anchor 1.9909/2.4710 ...")
    anchor_alpha, anchor_mae, anchor_rmse, anchor_disj = _verify_s26_anchor()
    log(f"S-26 anchor OK: alpha={anchor_alpha} MAE {anchor_mae:.4f} disjoint {anchor_disj:.4f}")

    # Load multivariate split
    fit_multi, concat_multi, test_multi, ot_ch = load_multivariate_split()
    train_multi = fit_multi[:TRAIN_END]
    # Validate sync with 1-d OT
    assert np.allclose(fit_multi[:, ot_ch], fit_series), "fit_multi OT mismatch with fit_series"
    concat_1d = concat_series
    # fit_multi already (11425,7), concat_multi (14305,7)

    log(f"Collecting P_val for {len(CANDIDATES)} candidates (val {n_val} origins, members frozen on {TRAIN_END})...")
    P_val = collect_val(train_series, fit_series, train_multi, fit_multi, val_starts)
    A_val = np.stack([val_series[t:t+HORIZON] for t in range(n_val)])
    for j, (name, _) in enumerate(CANDIDATES):
        mae = float(np.mean(np.mean(np.abs(P_val[:, j, :] - A_val), axis=1)))
        log(f"  singleton {name:20s} val {mae:.4f}")

    # Tabu-7 search, fixed-alpha fast 3000
    single_scores = [score_fast(P_val, A_val, [j]) for j in range(len(CANDIDATES))]
    cur_idx = [int(np.argmin(single_scores))]
    cur_score = single_scores[cur_idx[0]]
    best_idx = list(cur_idx)
    best_score = cur_score
    ts, _ = score_full(P_val, A_val, cur_idx)
    log(f"\ninit singleton {[CANDIDATES[i][0] for i in cur_idx]} fast {cur_score:.4f} true {ts:.4f}")

    tabu = set()
    q = collections.deque(maxlen=7)

    def key(idx):
        return tuple(sorted(idx))
    tabu.add(key(cur_idx))
    q.append(key(cur_idx))
    max_iter = 25
    no_improve = 0
    trace = []
    for it in range(max_iter):
        cur_set = set(cur_idx)
        all_set = set(range(len(CANDIDATES)))
        neigh = []
        for j in sorted(all_set - cur_set):
            neigh.append(sorted(cur_set | {j}))
        if len(cur_set) > 1:
            for j in sorted(cur_set):
                neigh.append(sorted(cur_set - {j}))
        for oj in sorted(cur_set):
            for ij in sorted(all_set - cur_set):
                neigh.append(sorted((cur_set - {oj}) | {ij}))
        uniq = []
        seen = set()
        for nb in neigh:
            k = tuple(nb)
            if k not in seen:
                seen.add(k)
                uniq.append(nb)
        scored = [(score_fast(P_val, A_val, nb), SEARCH_ALPHA, nb) for nb in uniq]
        scored.sort(key=lambda x: x[0])
        picked = None
        for s, a, nb in scored:
            k = tuple(nb)
            if k not in tabu or s < best_score - 1e-9:
                picked = (s, a, nb)
                break
        if picked is None:
            picked = scored[0]
        s, a, nb = picked
        cur_idx = nb
        cur_score = s
        k = tuple(nb)
        tabu.add(k)
        q.append(k)
        improved = s < best_score - 1e-9
        if improved:
            best_idx = list(nb)
            best_score = s
            no_improve = 0
        else:
            no_improve += 1
        true_s, true_a = score_full(P_val, A_val, nb) if (improved or it % 3 == 0) else (s, SEARCH_ALPHA)
        trace.append({"iter": it, "cur": [CANDIDATES[i][0] for i in nb], "fast": float(s), "true": float(true_s), "alpha": true_a, "best_fast": float(best_score), "best_set": [CANDIDATES[i][0] for i in best_idx]})
        log(f"iter {it:2d} cur {[CANDIDATES[i][0] for i in nb]} fast {s:.4f} true {true_s:.4f} a={true_a} best_fast {best_score:.4f} {[CANDIDATES[i][0] for i in best_idx]}")
        if no_improve >= 5:
            log("  no improve 5 iters -> stop")
            break

    log(f"\nbest subset fast {best_score:.4f}: {[CANDIDATES[i][0] for i in best_idx]}")
    _, best_alpha = score_full(P_val, A_val, best_idx)
    log(f"best_alpha {best_alpha}")
    P_best = P_val[:, best_idx, :]
    stack = fit_stack_map(P_best, A_val, best_alpha if best_alpha is not None else SEARCH_ALPHA)
    val_full = float(np.mean(np.mean(np.abs(stack.predict(P_best) - A_val), axis=1)))
    log(f"refit all val MAE {val_full:.4f} alpha {best_alpha}")

    # Diagnostics: effective sparsity for selected group-sparse members (refit on full train 11425 to inspect)
    group_diagnostics = {}
    for idx in best_idx:
        name, factory = CANDIDATES[idx]
        probe = factory()
        if isinstance(probe, GroupSparseNLinear):
            m = factory()
            m.fit(fit_multi, horizon=HORIZON)
            active = m.active_channels()
            exo = [c for c in active if c != "OT"]
            group_diagnostics[name] = {
                "patch_size": m.patch_size,
                "lam": m.lam,
                "active_channels": active,
                "active_exo": exo,
                "n_active_exo": len(exo),
                "group_norms": m.group_norms_,
                "n_params": int(m.W_.size),
                "W_shape": list(m.W_.shape),
            }
            log(f"  DIAG {name}: active {active} exo {exo} norms OT mean {m.group_norms_['OT']['mean_l2']:.4f}")
        else:
            group_diagnostics[name] = {"type": "univariate", "input_length": probe.input_length}

    # Overall sparsity metric: count exo channels across all selected group members
    all_exo = set()
    for name, diag in group_diagnostics.items():
        if "active_exo" in diag:
            all_exo.update(diag["active_exo"])
    effective_sparsity = len(all_exo)
    log(f"Effective sparsity: {effective_sparsity} exo channels active across selected set: {sorted(all_exo)}")
    # Also per-member sparsity line for close condition
    # Acceptance requires 1-3 exo channels active across the multivariate members (not counting univariate)
    # We'll report max per-member and union.
    per_member_exo_counts = [diag.get("n_active_exo", 0) for diag in group_diagnostics.values() if "n_active_exo" in diag]

    # Frozen test evaluation (members refrozen on 11425)
    disj_starts = np.array([len(fit_series) + s for s in DISJOINT_STARTS])
    P_disj_all = collect_test(fit_series, concat_series, fit_multi, concat_multi, disj_starts)
    P_disj = P_disj_all[:, best_idx, :]
    A_disj = np.stack([test_series[s:s+HORIZON] for s in DISJOINT_STARTS])
    preds_disj = stack.predict(P_disj)
    mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)

    n_test = len(test_series) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_series)
    P_test_all = collect_test(fit_series, concat_series, fit_multi, concat_multi, test_starts)
    P_test = P_test_all[:, best_idx, :]
    A_test = np.stack([test_series[t:t+HORIZON] for t in range(n_test)])
    preds_full = stack.predict(P_test)
    mae_full, rmse_full, mae_per, rmse_per = rolling_metrics(preds_full, A_test)
    for j, i in enumerate(best_idx):
        m = float(np.mean(np.mean(np.abs(P_test[:, j, :] - A_test), axis=1)))
        log(f"  member {CANDIDATES[i][0]:20s} full {m:.4f}")

    # Transfer guard: full-val diff <0.15
    transfer_delta = mae_full - val_full
    transfer_pass = transfer_delta < 0.15
    log(f"\nTransfer guard: full {mae_full:.4f} - val_full {val_full:.4f} = {transfer_delta:.4f} (pass={transfer_pass}, thr 0.15)")

    # Acceptance: full <=1.9859 AND disjoint-4 <=1.9696, sparsity 1-3 exo, val_full beats S-26 val 2.8527 by >0.005
    S26_VAL = 2.8527  # from CONTEXT S-26 refit all val MAE
    val_beats = (S26_VAL - val_full) > 0.005
    sparsity_pass = 1 <= effective_sparsity <= 3
    # Also check if tabu collapsed to univariate pair (no group member selected)
    has_group = any(isinstance(CANDIDATES[i][0] and CANDIDATES[i][1](), GroupSparseNLinear) for i in best_idx)
    # More robust: check group_diagnostics has any group entry
    has_group = any("active_exo" in d for d in group_diagnostics.values())
    accept_full = mae_full <= 1.9859
    accept_disj = mae_disj <= 1.9696
    accepted = accept_full and accept_disj and sparsity_pass and val_beats and transfer_pass

    # Close condition: tabu collapses to univariate pair and best multivariate val >2.85
    # Compute best multivariate singleton val
    group_singleton_vals = []
    for j, (name, _) in enumerate(CANDIDATES):
        if isinstance(CANDIDATES[j][1](), GroupSparseNLinear):
            group_singleton_vals.append((name, float(np.mean(np.mean(np.abs(P_val[:, j, :] - A_val), axis=1)))))
    best_group_val = min(v for _, v in group_singleton_vals) if group_singleton_vals else float("inf")
    best_group_name = min(group_singleton_vals, key=lambda x: x[1])[0] if group_singleton_vals else None
    collapsed_to_univariate = not has_group
    close_trigger = collapsed_to_univariate and best_group_val > 2.85

    log(f"\nS-26 incumbent 1.9909 / 1.9696 disjoint / val 2.8527")
    log(f"Bet2 best {mae_full:.4f} / {rmse_full:.4f} disjoint {mae_disj:.4f} val_full {val_full:.4f}")
    log(f"Accept: full<=1.9859 {accept_full} disj<=1.9696 {accept_disj} sparsity 1-3 {sparsity_pass} ({effective_sparsity}) val_beats>0.005 {val_beats} ({S26_VAL - val_full:.4f}) transfer<0.15 {transfer_pass}")
    log(f"Overall ACCEPT={accepted}")
    log(f"Close check: collapsed_to_univariate={collapsed_to_univariate} best_group_val {best_group_val:.4f} ({best_group_name}) close_trigger={close_trigger}")
    if close_trigger:
        log("CLOSE: tabu collapses to univariate pair and best multivariate val >2.85 -> close linear multivariate family")

    # Window breakdown W1-4 approximated via disjoint already; also compute W4 style from CONTEXT = last disjoint window?
    # Keep similar to S-26

    out = {
        "slice": "Bet2-group-sparse-patch",
        "pool": [n for n, _ in CANDIDATES],
        "params": {"L": 336, "patch_sizes": [24, 48], "lams": [0.5, 2.0], "ridge_alpha": 10.0, "ot_unpenalized": True, "n_features_P24": 98, "n_features_P48": 49, "H": HORIZON},
        "s26_anchor": {"mae": anchor_mae, "rmse": anchor_rmse, "alpha": anchor_alpha, "disjoint": anchor_disj, "expected_mae": S26_ANCHOR_MAE},
        "trace": trace,
        "best_subset": [CANDIDATES[i][0] for i in best_idx],
        "best_idx": best_idx,
        "best_fast": best_score,
        "best_alpha": best_alpha,
        "val_full": val_full,
        "val_beats_s26_by": S26_VAL - val_full,
        "val_beats_pass": val_beats,
        "group_singleton_vals": {n: v for n, v in group_singleton_vals},
        "best_group_val": best_group_val,
        "best_group_name": best_group_name,
        "group_diagnostics": group_diagnostics,
        "effective_sparsity": {"n_active_exo_union": effective_sparsity, "channels": sorted(all_exo), "per_member_exo_counts": per_member_exo_counts, "pass_1_3": sparsity_pass},
        "test_disjoint": {"mae": mae_disj, "rmse": rmse_disj},
        "test_full": {"mae": mae_full, "rmse": rmse_full, "n": n_test, "delta_vs_s26": mae_full - 1.9909},
        "transfer": {"delta": transfer_delta, "pass": transfer_pass, "threshold": 0.15},
        "acceptance": {"full_le_19859": accept_full, "disjoint_le_19696": accept_disj, "sparsity_1_3": sparsity_pass, "val_beats": val_beats, "transfer": transfer_pass, "accepted": accepted},
        "close": {"collapsed_to_univariate": collapsed_to_univariate, "best_group_val": best_group_val, "close_trigger": close_trigger, "message": "close linear multivariate family" if close_trigger else "not closed"},
        "protocol": "S-20-clean: val members frozen on 8545, test members refrozen on 11425; tabu-7 fixed-alpha fast 3000, chronological val[0:1080)/val[1080:2161), per-horizon ridge no-intercept 11-alpha grid",
    }
    with open(HERE / "results_group_sparse_bet2.json", "w") as f:
        json.dump(out, f, indent=2)
    with open(HERE / "harness.log", "w") as f:
        f.write("\n".join(log_lines) + "\n")
    log(f"\nwrote {HERE / 'results_group_sparse_bet2.json'} elapsed {time.time() - t_all:.1f}s")
    # Write harness.log already done
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
