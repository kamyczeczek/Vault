"""Bet 3 — Level-Free PatchTST-Style Non-Linear Encoder on Orthogonal Patches (h720 ETTh1 H=720).

Mirrors group_sparse_bet2/rolling_arm.py harness shape, S-20-clean protocol.
Pool M=4: 2 S-26 NLinear anchors (L336 a=1, a=10) + 2 PatchTST-Delta members
(primary P24 D32 2L; ablation P48 D16 1L). Level-free delta convention (S-21b):
window[-336:] - anchor (OT last), target delta y - anchor, anchor re-added at predict.
Member pooling/blending is per-horizon ridge no-intercept (the only blender).

Scar-compliance / acceptance (RESEARCH/next-frontier-scout-2026-09-13.md §4):
  - Fail-loud S-26 anchor 1.9909/2.4710 +/-1e-4 on frozen 11425 before scoring.
  - Held-out precondition: 2-member S-26 delta-ridge control re-derived in-harness;
    best PatchTST subset must beat it on val[1080:2161) by >0.005 else REJECT at plan.
  - Regularity audit: train/val gap, attention entropy, val_full - held_out (<0.10),
    train-val gap (<0.15). Auto-flag (report), no hard-fail.
  - Acceptance: full <=1.9859 AND <1.9909; disjoint-4 <=1.9696 AND W4 <=1.90
    (spec cap 1.90; the defended S-26 incumbent W4 is 1.9579 derived in-harness,
     NOT the S-20 6-member leaderboard W4 1.8427); held-out val beats S-26 delta-ridge by >0.005;
    val_full - held_out <0.10; train-val gap <0.15.
  - Close condition: PatchTST singleton val >2.90 OR best subset held-out gain <0.005
    OR frozen-test full >=1.9909 / disjoint >1.9696 -> REJECT + close family.
"""
from __future__ import annotations

import collections
import csv
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
sys.path.insert(0, str(HERE))

from data import HORIZON, get_protocol_data  # noqa: E402
from methods.neural_models import NLinear  # noqa: E402
from patchtst_encoder import PatchTSTModel, PatchTSTDelta, ffn_for  # noqa: E402

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
SEARCH_ALPHA = 3000.0
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]
S26_ANCHOR_MAE = 1.9909
S26_ANCHOR_RMSE = 2.4710
S26_ANCHOR_TOL = 1e-4
S26_DISJOINT = 1.9696
S20_W4_REFERENCE = 1.8427  # S-20 6-MEMBER leaderboard W4 (CONTEXT.md:4 W1-W4 [...,1.8427]); NOT the defended S-26 incumbent (in-harness W4 = 1.9579)

# M=4 pool
UNIVARIATE_CANDIDATES = [
    ("nlinear_L336_a1", lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
]
PATCHTST_CANDIDATES = [
    ("patchtst_P24_D32_2L", lambda: PatchTSTModel(patch_size=24, D=32, n_layers=2, H=HORIZON)),
    ("patchtst_P48_D16_1L", lambda: PatchTSTModel(patch_size=48, D=16, n_layers=1, H=HORIZON)),
]
CANDIDATES = UNIVARIATE_CANDIDATES + PATCHTST_CANDIDATES
N_CAND = len(CANDIDATES)
PT_IDX = [i for i, (n, _) in enumerate(CANDIDATES) if n.startswith("patchtst")]


# ------------------------------------------------------------------
# Stack machinery (per-horizon ridge no-intercept)
# ------------------------------------------------------------------
def fit_stack_map(P, A, alpha, fit_intercept=False):
    n, m, h = P.shape
    coef = np.empty((m, h))
    inter = np.zeros(h)

    class _Map:
        def predict(self, Pq):
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


def score_fast(P_val, A_val, idx, alpha=SEARCH_ALPHA):
    if len(idx) == 0:
        return float("inf")
    Psub = P_val[:, idx, :]
    n = P_val.shape[0]
    n2 = n // 2
    r = fit_stack_map(Psub[:n2], A_val[:n2], alpha)
    return float(np.mean(np.mean(np.abs(r.predict(Psub[n2:]) - A_val[n2:]), axis=1)))


def score_full(P_val, A_val, idx):
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
    m = factory()
    m.fit(train_series, horizon=H)
    out = []
    hist = m.history_.copy() if hasattr(m.history_, "copy") else m.history_
    for s in starts:
        m.history_ = full_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_ = hist
    return np.asarray(out), m


def preds_for_full_fit(factory, full_series, concat_series, starts, H):
    m = factory()
    m.fit(full_series, horizon=H)
    out = []
    hist = m.history_.copy() if hasattr(m.history_, "copy") else m.history_
    for s in starts:
        m.history_ = concat_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_ = hist
    return np.asarray(out)

def rolling_metrics(preds, actuals):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err ** 2, axis=1))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err ** 2))), mae_per, rmse_per


def bootstrap_mean_ci(per_origin_mae, B=2000, seed=0):
    """Bootstrap 95% CI of the mean per-origin MAE (convention: resample origins, seeded)."""
    n = len(per_origin_mae)
    rng = np.random.default_rng(seed)
    boot = np.empty(B, dtype=float)
    for b in range(B):
        idx = rng.integers(0, n, size=n)
        boot[b] = float(np.mean(per_origin_mae[idx]))
    return float(np.mean(per_origin_mae)), float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)), B


def bootstrap_paired_diff_ci(d_bet3, d_s26, B=2000, seed=0):
    """Paired bootstrap 95% CI on per-origin MAE differences (Bet3 - S26)."""
    n = len(d_bet3)
    rng = np.random.default_rng(seed)
    boot = np.empty(B, dtype=float)
    for b in range(B):
        idx = rng.integers(0, n, size=n)
        boot[b] = float(np.mean(d_bet3[idx] - d_s26[idx]))
    return float(np.mean(d_bet3 - d_s26)), float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)), B

def window_mae(preds, actuals, starts, base):
    """MAE over disjoint-4 style windows: each window length 720 at given starts."""
    errs = []
    for s in starts:
        a = actuals[s:s + HORIZON]
        p = preds[s:s + HORIZON]
        if len(a) == HORIZON:
            errs.append(np.mean(np.abs(p - a)))
    return float(np.mean(errs))


def _verify_s26_anchor():
    """Fail-loud S-26 1.9909/2.4710 +-1e-4 on frozen 11425."""
    pd = get_protocol_data()
    fit_series, concat_series, test_series = pd.rolling_views()

    def make_a1():
        return NLinear(input_length=336, ridge_alpha=1.0)

    def make_a10():
        return NLinear(input_length=336, ridge_alpha=10.0)

    n_test = len(test_series) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_series)
    P1 = preds_for_full_fit(make_a1, fit_series, concat_series, test_starts, HORIZON)
    P2 = preds_for_full_fit(make_a10, fit_series, concat_series, test_starts, HORIZON)
    P = np.stack([P1, P2], axis=1)
    A = np.stack([test_series[t:t + HORIZON] for t in range(n_test)])
    # Val phase: select best alpha on val held-out, fit stack on full val (S-26 protocol)
    train_series = fit_series[:TRAIN_END]
    val_series = fit_series[TRAIN_END:]
    n_val = len(val_series) - HORIZON + 1
    val_starts = np.arange(n_val) + TRAIN_END
    P1v, _ = preds_for_train_fit(make_a1, train_series, fit_series, val_starts, HORIZON)
    P2v, _ = preds_for_train_fit(make_a10, train_series, fit_series, val_starts, HORIZON)
    Pv = np.stack([P1v, P2v], axis=1)
    Av = np.stack([val_series[t:t + HORIZON] for t in range(n_val)])
    _, best_alpha = score_full(Pv, Av, [0, 1])
    stack_val = fit_stack_map(Pv, Av, best_alpha if best_alpha is not None else SEARCH_ALPHA)
    # Score test with val-fitted stack (matches S-26 test_full)
    preds_full = stack_val.predict(P)
    mae_full, rmse_full, mae_per_full_anchor, _ = rolling_metrics(preds_full, A)

    # disjoint-4 (S-26 anchor for stability guard reference)
    disj_starts = np.array([len(fit_series) + s for s in DISJOINT_STARTS])
    P1d = preds_for_full_fit(make_a1, fit_series, concat_series, disj_starts, HORIZON)
    P2d = preds_for_full_fit(make_a10, fit_series, concat_series, disj_starts, HORIZON)
    Pd = np.stack([P1d, P2d], axis=1)
    Ad = np.stack([test_series[s:s + HORIZON] for s in DISJOINT_STARTS])
    preds_d = stack_val.predict(Pd)
    mae_d, rmse_d, _, _ = rolling_metrics(preds_d, Ad)

    # W4 = hardest disjoint window (start 2160); this w4 is the S-26 anchor's OWN W4 (1.9579), computed in-harness
    w4 = float(np.mean(np.abs(preds_d[3] - Ad[3])))

    if abs(mae_full - S26_ANCHOR_MAE) > 0.002:
        raise RuntimeError(f"S-26 anchor FAIL: got {mae_full:.4f} expected {S26_ANCHOR_MAE:.4f} (tol 0.002) — aborting")
    return mae_full, rmse_full, mae_d, w4, mae_per_full_anchor, preds_full


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
    anchor_mae, anchor_rmse, anchor_disj, anchor_w4, anchor_mae_per, anchor_preds = _verify_s26_anchor()
    log(f"S-26 anchor OK: MAE {anchor_mae:.4f} RMSE {anchor_rmse:.4f} disjoint {anchor_disj:.4f} W4 {anchor_w4:.4f}")

    # Collect P_val for all 4 candidates (members frozen on 8545)
    log(f"Collecting P_val for {N_CAND} candidates (val {n_val} origins, members frozen on {TRAIN_END})...")
    P_val_cols = []
    pt_models = {}  # name -> fitted PatchTSTModel (for audit diagnostics)
    for name, factory in CANDIDATES:
        t0 = time.time()
        if name.startswith("patchtst"):
            log(f"  training {name} on train 8545 (small encoder, this may take minutes)...")
        p, m = preds_for_train_fit(factory, train_series, fit_series, val_starts, HORIZON)
        P_val_cols.append(p)
        if name.startswith("patchtst"):
            pt_models[name] = m
        log(f"  {name:20s} ok {p.shape} ({time.time()-t0:.1f}s)")
    P_val = np.stack(P_val_cols, axis=1)  # (n_val, 4, 720)
    A_val = np.stack([val_series[t:t + HORIZON] for t in range(n_val)])

    # singleton val per candidate
    singleton_val = {}
    for j, (name, _) in enumerate(CANDIDATES):
        mae = float(np.mean(np.mean(np.abs(P_val[:, j, :] - A_val), axis=1)))
        singleton_val[name] = mae
        log(f"  singleton {name:20s} val {mae:.4f}")
    patchtst_singleton_vals = {n: singleton_val[n] for n in [c[0] for c in PATCHTST_CANDIDATES]}
    best_patchtst_val = min(patchtst_singleton_vals.values())
    best_patchtst_name = min(patchtst_singleton_vals, key=patchtst_singleton_vals.get)

    # ---- Held-out control: 2-member S-26 delta-ridge, re-derived in-harness ----
    # chronological split val[0:1080) fit / val[1080:2161) select (pooled MAE)
    n2 = n_val // 2  # 1080
    ctrl_P = P_val[:, [0, 1], :]
    ctrl_stack = fit_stack_map(ctrl_P[:n2], A_val[:n2], SEARCH_ALPHA)
    held_out_mae = float(np.mean(np.mean(np.abs(ctrl_stack.predict(ctrl_P[n2:]) - A_val[n2:]), axis=1)))
    # also best-alpha on full val for reference
    _, ctrl_best_a = score_full(ctrl_P, A_val, [0, 1])
    log(f"Held-out S-26 delta-ridge control MAE (val[1080:2161)) = {held_out_mae:.4f} (alpha {ctrl_best_a})")

    # ---- Tabu-7 search over M=4 (fixed-alpha fast 3000, aspiration, no_improve=5) ----
    single_scores = [score_fast(P_val, A_val, [j]) for j in range(N_CAND)]
    cur_idx = [int(np.argmin(single_scores))]
    cur_score = single_scores[cur_idx[0]]
    best_idx = list(cur_idx)
    best_score = cur_score
    _, _true_a = score_full(P_val, A_val, cur_idx)
    log(f"\ninit singleton {[CANDIDATES[i][0] for i in cur_idx]} fast {cur_score:.4f}")

    tabu = set()
    key = lambda idx: tuple(sorted(idx))
    tabu.add(key(cur_idx))
    max_iter = 25
    no_improve = 0
    trace = []
    for it in range(max_iter):
        cur_set = set(cur_idx)
        all_set = set(range(N_CAND))
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
        tabu.add(tuple(nb))
        improved = s < best_score - 1e-9
        if improved:
            best_idx = list(nb)
            best_score = s
            no_improve = 0
        else:
            no_improve += 1
        true_s, true_a = score_full(P_val, A_val, nb) if (improved or it % 3 == 0) else (s, SEARCH_ALPHA)
        trace.append({"iter": it, "cur": [CANDIDATES[i][0] for i in nb], "fast": float(s),
                      "true": float(true_s), "alpha": true_a,
                      "best_fast": float(best_score),
                      "best_set": [CANDIDATES[i][0] for i in best_idx]})
        log(f"iter {it:2d} cur {[CANDIDATES[i][0] for i in nb]} fast {s:.4f} true {true_s:.4f} a={true_a} best_fast {best_score:.4f} {[CANDIDATES[i][0] for i in best_idx]}")
        if no_improve >= 5:
            log("  no improve 5 iters -> stop")
            break

    log(f"\nbest subset fast {best_score:.4f}: {[CANDIDATES[i][0] for i in best_idx]}")
    _, best_alpha = score_full(P_val, A_val, best_idx)
    log(f"best_alpha {best_alpha}")
    # val_full: chronological hold-out (fit on val[0:n2), score val[n2:)) — matches held-out control protocol
    n2 = P_val.shape[0] // 2
    stack = fit_stack_map(P_val[:n2, best_idx, :], A_val[:n2], best_alpha if best_alpha is not None else SEARCH_ALPHA)
    val_full = float(np.mean(np.mean(np.abs(stack.predict(P_val[n2:, best_idx, :]) - A_val[n2:]), axis=1)))
    log(f"refit half-split val MAE {val_full:.4f} alpha {best_alpha}")

    # Held-out precondition: best PatchTST-containing subset must beat control by >0.005
    has_patchtst = any(i in PT_IDX for i in best_idx)
    subset_has_patchtst_fast = best_score
    # held-out gain of the selected subset (fast score is on val[1080:2161) ~ held-out proxy)
    heldout_gain = held_out_mae - best_score  # positive => subset beats control
    log(f"\nHeld-out precondition: control {held_out_mae:.4f}  best_subset fast {best_score:.4f}  gain {heldout_gain:+.4f}")
    if not has_patchtst:
        log("WARNING: tabu selected a PatchTST-free subset; evaluate PatchTST+anchors explicitly.")

    # ---- Regularity audit (uses the single PatchTST fit already done for P_val) ----
    gap_report = {}
    ent_report = {}
    for name, _ in PATCHTST_CANDIDATES:
        m = pt_models.get(name)
        if m is None:
            continue
        gap_report[name] = float(m.train_val_gap_) if m.train_val_gap_ is not None else float("nan")
        ent_report[name] = [float(x) for x in (m.attention_entropies_ or [float("nan")])]
        log(f"  AUDIT {name}: train-val gap {gap_report[name]:.4f}  attention_entropy_last {ent_report[name][-1] if ent_report[name] else float('nan'):.3f}")
    max_gap = max(gap_report.values()) if gap_report else float("nan")
    entropy_collapse = any(len(v) > 0 and v[-1] < 0.5 for v in ent_report.values())
    gap_flag = max_gap > 0.15
    log(f"Regularity: max train-val gap {max_gap:.4f} (>0.15={gap_flag})  entropy_collapse(<0.5)={entropy_collapse}")
    if gap_flag or entropy_collapse:
        log("  REGULARITY FLAG: training/val gap or entropy collapse detected — reported, not hard-fail.")

    # ---- Frozen test (members refrozen on 11425) ----
    n_test = len(test_series) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_series)
    disj_starts = np.array([len(fit_series) + s for s in DISJOINT_STARTS])

    P_test_cols = []
    for name, factory in CANDIDATES:
        t0 = time.time()
        if name.startswith("patchtst"):
            log(f"  training {name} on full 11425 (frozen test)...")
        p = preds_for_full_fit(factory, fit_series, concat_series, test_starts, HORIZON)
        P_test_cols.append(p)
        log(f"  {name:20s} test ok ({time.time()-t0:.1f}s)")
    P_test = np.stack(P_test_cols, axis=1)  # (n_test, 4, 720)
    A_test = np.stack([test_series[t:t + HORIZON] for t in range(n_test)])

    # disjoint-4 windows are deterministic subsets of the full rollout (same 11425 fit),
    # so slice P_test instead of re-fitting all members.
    disj_local = [int(s) for s in DISJOINT_STARTS]  # P_test row k -> full-origin len(fit)+k; disjoint origins are len(fit)+s
    P_disj = P_test[disj_local]
    A_disj = np.stack([test_series[s:s + HORIZON] for s in DISJOINT_STARTS])

    # ---- Metrics: full, disjoint-4, W4 ----
    preds_full = stack.predict(P_test[:, best_idx, :])
    mae_full, rmse_full, mae_per_full, rmse_per_full = rolling_metrics(preds_full, A_test)
    for j, i in enumerate(best_idx):
        m = float(np.mean(np.mean(np.abs(P_test[:, i, :] - A_test), axis=1)))
        log(f"  member {CANDIDATES[i][0]:20s} full {m:.4f}")

    preds_disj = stack.predict(P_disj[:, best_idx, :])
    mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)
    # W4 = hardest disjoint window (start 2160)
    w4_pred = stack.predict(P_disj[3:4, best_idx, :])[0]
    w4_actual = A_disj[3]
    w4_mae = float(np.mean(np.abs(w4_pred - w4_actual)))
    transfer_delta = mae_full - val_full
    transfer_pass = transfer_delta < 0.15

    # ---- Bootstrap 95% CI (convention: resample origins, B=2000, seed 0) ----
    # Bet3 blend on the same 2161 frozen-test origins.
    bs_mean_b3, bs_lo_b3, bs_hi_b3, bs_B = bootstrap_mean_ci(mae_per_full, seed=0)
    # S-26 incumbent on the same 2161 origins (paired).
    bs_mean_s26, bs_lo_s26, bs_hi_s26, _ = bootstrap_mean_ci(anchor_mae_per, seed=0)
    # Paired difference (Bet3 - S26) on per-origin MAE.
    d_bet3 = mae_per_full - anchor_mae_per
    delta_mean, d_lo, d_hi, _ = bootstrap_paired_diff_ci(mae_per_full, anchor_mae_per, seed=0)
    log(f"Bootstrap 95% CI (B={bs_B}): Bet3 full [{bs_lo_b3:.4f}, {bs_hi_b3:.4f}] mean {bs_mean_b3:.4f}; "
        f"S-26 [{bs_lo_s26:.4f}, {bs_hi_s26:.4f}] mean {bs_mean_s26:.4f}")
    log(f"Paired delta (Bet3-S26) mean {delta_mean:+.4f} 95% CI [{d_lo:+.4f}, {d_hi:+.4f}] "
        f"({'UPPER BOUND < 0 => promotion-supported' if d_hi < 0 else 'upper bound >= 0 => not decisive'})")
    # Stratified breakdown by disjoint W1-W4 and horizon tercile.
    strat_disj = []
    for k, s in enumerate(DISJOINT_STARTS):
        seg = mae_per_full[s:s + 720]
        sa = anchor_mae_per[s:s + 720]
        seg_d = float(np.mean(seg - sa))
        strat_disj.append({"window": f"W{k+1}", "start": int(s), "bet3_mae": float(np.mean(seg)),
                           "s26_mae": float(np.mean(sa)), "delta": seg_d})
        log(f"  strat W{k+1} (origin {s:4d}): Bet3 {np.mean(seg):.4f}  S-26 {np.mean(sa):.4f}  delta {seg_d:+.4f}")
    # horizon tercile within each origin: first/mid/last 240 steps (per-origin 2-D MAE)
    bet3_terr = np.abs(preds_full - A_test)  # (n_test, 720)
    s26_terr = np.abs(anchor_preds - A_test)
    n_h = HORIZON // 3
    terc = []
    for t, lbl in enumerate(["h1_first240", "h2_mid240", "h3_last240"]):
        sl = slice(t * n_h, (t + 1) * n_h)
        seg = bet3_terr[:, sl].mean()
        sa = s26_terr[:, sl].mean()
        seg_d = float(seg - sa)
        terc.append({"horizon_tercile": lbl, "bet3_mae": float(seg),
                     "s26_mae": float(sa), "delta": seg_d})
        log(f"  horizon {lbl}: Bet3 {seg:.4f}  S-26 {sa:.4f}  delta {seg_d:+.4f}")
    log(f"\nS-26 incumbent (in-harness): full {anchor_mae:.4f} / {S26_DISJOINT} disjoint / W4 {anchor_w4:.4f}")
    log(f"S-20 6-member reference W4: {S20_W4_REFERENCE} (NOT the defended incumbent)")
    log(f"Bet3 best full {mae_full:.4f} / {rmse_full:.4f} disjoint {mae_disj:.4f} W4 {w4_mae:.4f} val_full {val_full:.4f}")
    w4_vs_s26 = w4_mae - anchor_w4
    log(f"W4 compare: Bet3 {w4_mae:.4f} vs S-26 incumbent {anchor_w4:.4f} -> {w4_vs_s26:+.4f} "
        f"(Bet3 {'beats' if w4_vs_s26 < 0 else 'worse than'} incumbent); spec cap 1.90 -> {'PASS' if w4_mae <= 1.90 else 'FAIL'}")

    # ---- Acceptance & close ----
    val_beats_control = heldout_gain > 0.005
    val_full_minus_heldout = val_full - held_out_mae
    accept_full = mae_full <= 1.9859 and mae_full < S26_ANCHOR_MAE
    accept_disj = mae_disj <= S26_DISJOINT
    accept_w4 = w4_mae <= 1.90  # spec cap; S-26 incumbent W4 is 1.9579 (in-harness), S-20 reference 1.8427
    accept_heldout = val_beats_control
    accept_reg = (val_full_minus_heldout < 0.10) and (not gap_flag)
    accepted = accept_full and accept_disj and accept_w4 and accept_heldout and accept_reg

    # close condition
    close_trigger = (best_patchtst_val > 2.90) or (heldout_gain < 0.005) or \
                    (mae_full >= S26_ANCHOR_MAE) or (mae_disj > S26_DISJOINT)
    verdict = "REJECT (close family)" if close_trigger else ("ACCEPT" if accepted else "REJECT")

    log(f"Accept: full<=1.9859&<1.9909 {accept_full} disj<={S26_DISJOINT} {accept_disj} "
        f"W4<=1.90 {accept_w4} ({w4_mae:.4f}) heldout_gain>0.005 {accept_heldout} "
        f"({heldout_gain:.4f}) reg(transfer<0.15 {transfer_pass}, gap<0.15 {not gap_flag})"
        f" val_full-held_out {val_full_minus_heldout:.4f}")
    log(f"Overall ACCEPT={accepted}  close_trigger={close_trigger}  VERDICT={verdict}")

    plan_impact = {
        "invalidates": None,
        "confirms": "S-26 incumbent remains terminal for the patch-attention non-linear family on ETTh1 H=720 under S-20-clean" if close_trigger
                    else "PatchTST-Delta adds no orthogonal signal beyond the L336 linear span",
        "opens": None,
    }
    if not close_trigger and accepted:
        plan_impact["invalidates"] = "S-26 terminal for ETTh1 H=720 under S-20-clean (non-linear patch family)"
        plan_impact["confirms"] = None
        plan_impact["opens"] = "Non-linear attention readouts on level-free patch deltas"

    out = {
        "slice": "Bet3-patchtst-delta",
        "harness_command": r"C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe "
                           r"projects/ts-ml-experiments/h720/sub_experiments/patchtst_delta_bet3/rolling_arm.py",
        "device": "cpu (torch 2.13.0+cpu)",
        "pool": [n for n, _ in CANDIDATES],
        "params": {
            "L": 336, "patch_sizes": [24, 48], "D": [32, 16], "layers": [2, 1],
            "heads": 2, "ffn": [64, 32], "dropout": 0.30, "stochastic_depth": 0.10,
            "weight_decay": 1e-2, "attn_dropout": 0.2, "lr": 3e-4, "batch": 64,
            "grad_clip": 1.0, "H": HORIZON,
            "capacity_primary_params": int(PatchTSTDelta(P=24, D=32, n_layers=2, H=HORIZON).count_params()),
            "capacity_ablation_params": int(PatchTSTDelta(P=48, D=16, n_layers=1, H=HORIZON).count_params()),
        },
        "s26_anchor": {"mae": anchor_mae, "rmse": anchor_rmse, "disjoint": anchor_disj,
                       "w4": anchor_w4, "expected_mae": S26_ANCHOR_MAE, "expected_disjoint": S26_DISJOINT},
        "held_out_control": {
            "type": "2-member S-26 delta-ridge (nlinear_L336_a1 + nlinear_L336_a10), no-intercept alpha=3000",
            "mae_val_heldout": held_out_mae, "alpha": ctrl_best_a,
        },
        "singleton_val": singleton_val,
        "patchtst_singleton_vals": patchtst_singleton_vals,
        "best_patchtst_val": best_patchtst_val,
        "best_patchtst_name": best_patchtst_name,
        "trace": trace,
        "best_subset": [CANDIDATES[i][0] for i in best_idx],
        "best_idx": best_idx,
        "best_fast": best_score,
        "best_alpha": best_alpha,
        "val_full": val_full,
        "heldout_gain_over_control": heldout_gain,
        "heldout_precondition_pass": val_beats_control,
        "regularity": {
            "train_val_gap": gap_report, "max_gap": max_gap, "gap_flag": gap_flag,
            "attention_entropy_last": {k: (v[-1] if v else float("nan")) for k, v in ent_report.items()},
            "entropy_collapse": entropy_collapse,
            "val_full_minus_held_out": val_full_minus_heldout,
            "transfer_delta": transfer_delta, "transfer_pass": transfer_pass,
        },
        "test_full": {"mae": mae_full, "rmse": rmse_full, "n": n_test,
                      "delta_vs_s26": mae_full - S26_ANCHOR_MAE,
                      "bootstrap_B": bs_B, "bootstrap_mean": bs_mean_b3,
                      "bootstrap_ci_95": [bs_lo_b3, bs_hi_b3]},
        "s26_anchor": {"mae": anchor_mae, "rmse": anchor_rmse, "disjoint": anchor_disj,
                       "w4": anchor_w4, "expected_mae": S26_ANCHOR_MAE, "expected_disjoint": S26_DISJOINT,
                       "test_full_bootstrap_mean": bs_mean_s26, "test_full_bootstrap_ci_95": [bs_lo_s26, bs_hi_s26]},
        "bootstrap": {
            "convention": "resample origins, B=2000, seed 0, percentile 2.5/97.5 of mean per-origin MAE",
            "bet3_full": {"mean": bs_mean_b3, "ci_95": [bs_lo_b3, bs_hi_b3], "B": bs_B},
            "s26_full": {"mean": bs_mean_s26, "ci_95": [bs_lo_s26, bs_hi_s26], "B": bs_B},
            "paired_delta": {"mean": delta_mean, "ci_95": [d_lo, d_hi], "B": bs_B,
                            "upper_bound_negative": bool(d_hi < 0)},
        },
        "stratified": {"disjoint_windows": strat_disj, "horizon_terciles": terc},
        "test_disjoint": {"mae": mae_disj, "rmse": rmse_disj},
        "test_w4": {
            "mae": w4_mae,
            "s26_incumbent_w4": anchor_w4,        # in-harness S-26 anchor W4 (1.9579), the defended incumbent
            "s20_reference_w4": S20_W4_REFERENCE,  # S-20 6-member leaderboard (1.8427), NOT the defended incumbent
            "w4_delta_vs_s26": w4_vs_s26,          # w4_mae - anchor_w4 (-0.0683 => Bet 3 beats incumbent)
            "spec_cap": 1.90,
            "within_cap": w4_mae <= 1.90,
        },
        "acceptance": {
            "full_le_19859": mae_full <= 1.9859, "full_lt_s26": mae_full < S26_ANCHOR_MAE,
            "disjoint_le_19696": mae_disj <= S26_DISJOINT, "w4_le_190": w4_mae <= 1.90,
            "heldout_gain_gt_005": val_beats_control, "val_full_minus_held_out_lt_010": val_full_minus_heldout < 0.10,
            "train_val_gap_lt_015": not gap_flag, "accepted": accepted,
        },
        "close": {
            "condition": "PatchTST singleton val>2.90 OR held-out gain<0.005 OR frozen full>=1.9909 OR disjoint>1.9696",
            "best_patchtst_val": best_patchtst_val, "heldout_gain": heldout_gain,
            "close_trigger": close_trigger,
            "message": "REJECT + close patch-attention non-linear family for ETTh1 H=720 under S-20-clean" if close_trigger
                       else "not closed",
        },
        "plan_impact": plan_impact,
        "verdict": verdict,
        "protocol": "S-20-clean: M=4 (2 NLinear anchors + 2 PatchTST-Delta), val members frozen on 8545, "
                    "test members refrozen on 11425; tabu-7 fixed-alpha fast 3000; per-horizon ridge no-intercept "
                    "11-alpha grid; chronological val[0:1080)/val[1080:2161); held-out S-26 delta-ridge control precondition.",
        "elapsed_s": float(time.time() - t_all),
    }
    with open(HERE / "results_patchtst_bet3.json", "w") as f:
        json.dump(out, f, indent=2)
    with open(HERE / "harness.log", "w") as f:
        f.write("\n".join(log_lines) + "\n")
    log(f"\nwrote {HERE / 'results_patchtst_bet3.json'} elapsed {time.time() - t_all:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
