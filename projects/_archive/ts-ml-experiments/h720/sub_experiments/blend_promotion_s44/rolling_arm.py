"""S-44 — Blend-Promotion Re-registration of the Bet 3 PatchTST-Delta Blend (h720 ETTh1 H=720).

Pre-registration contract: S44_DESIGN.md in this directory (D1-D11) — FINAL and BINDING;
implemented verbatim. This is a re-registration of GATE SEMANTICS (S-43 P1) over Bet 3's
frozen, already-executed pool/protocol/seed — NOT a new search, NOT a new member, NOT a
re-opening of the patch-attention family (D3/D5/D11).

The harness is structurally the Bet 3 pipeline (sub_experiments/patchtst_delta_bet3/
rolling_arm.py) with the S-44 gate semantics:

  - Binding gate is BLEND-based (D2): the frozen-test stacked blend of the tabu-selected
    subset must beat the S-26 incumbent:
        G1  MAE_full(2161) <= 1.9859     (H2 bound: >= 0.0050 vs S-26 1.9909)
        G2  MAE_full       <  1.9909     (strictly better than the incumbent)
        G3  MAE_disjoint-4 <= 1.9696     (S-26 stability cap)
        G4  paired-bootstrap delta CI upper < 0 (B=2000, seed 0, resample origins;
            convention identical to Bet 3 bootstrap_paired_diff_ci)
  - Singleton / regularity conditions are DEMOTED to non-binding diagnostics (D5); they
    cannot flip PASS -> FAIL. The Bet 3 member-capability family close stands
    independently of the promotion outcome (D5/D11).
  - Close conditions, any one -> REJECTED (D5): C1 no-PatchTST member in the selected
    subset; C2 held-out gain <= 0.005 (plan-time precondition to the frozen test, D4);
    C3 paired CI upper >= 0; C4 any of G1-G3 fails.
  - Parity clause (D8): the harness MUST reproduce every section-5 quantity from
    results_patchtst_bet3.json to 1e-4 (sets/sequences exact). Any failure means the
    HARNESS is wrong: print the failing rows, write results_s44.json with
    parity.all_pass=false and verdict="ABORT_PARITY"; no promotion verdict is emitted.
  - Fail-loud S-26 anchor (D9): re-derived in-harness; all four values within 1e-4 of
    Bet 3's full-precision s26_anchor (1.990897 / 2.470999 / 1.969617 / 1.957937),
    tightened from Bet 3's 0.002 tolerance; abort otherwise.
  - Per-window W1-W4 and horizon terciles are reported vs the IN-HARNESS S-26 anchor
    (S-43 P2 / D7) — non-binding diagnostics, reported honestly (W1 expected +0.0274
    worse; W2 +0.0000, W3 -0.0656, W4 -0.0683 better).

PatchTST members import the encoder VERBATIM from the sibling Bet 3 directory
(patchtst_delta_bet3/patchtst_encoder.py — see the sys.path.insert below and the
harness.log audit line), guaranteeing architecture-identical code by construction
rather than by transcription. NLinear anchors import from methods/neural_models.py
exactly as Bet 3 imported them.

Determinism: torch.manual_seed(0) + np.random.seed(0) at harness start (the Bet 3
encoder additionally re-seeds inside every fit), CPU only,
torch.use_deterministic_algorithms(True, warn_only=True).
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import Ridge

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
# S-44 (D3/D8): the PatchTST members import the Bet 3 encoder module VERBATIM from the
# sibling directory — architecture-identical code by construction, not by transcription.
# This import is also recorded in harness.log (see main()).
sys.path.insert(0, str(HERE.parent / "patchtst_delta_bet3"))

from data import HORIZON, get_protocol_data  # noqa: E402
from methods.neural_models import NLinear  # noqa: E402
from patchtst_encoder import PatchTSTDelta, PatchTSTModel, ffn_for  # noqa: E402  <- sibling Bet 3 module

BET3_DIR = HERE.parent / "patchtst_delta_bet3"
BET3_RESULTS = BET3_DIR / "results_patchtst_bet3.json"
HARNESS_COMMAND = (
    "C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe "
    "projects/ts-ml-experiments/h720/sub_experiments/blend_promotion_s44/rolling_arm.py"
)

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
SEARCH_ALPHA = 3000.0
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]
S26_ANCHOR_MAE = 1.9909   # G2 threshold / incumbent delta reference (D2)
S26_DISJOINT = 1.9696     # G3 threshold (D2)
S26_ANCHOR_TOL = 1e-4     # D9 fail-loud anchor tolerance (Bet 3 shipped 0.002; S-44 tightens)
PARITY_TOL = 1e-4         # D8 parity tolerance (design section 5)
G1_FULL_BOUND = 1.9859    # G1 (H2 bound: >= 0.0050 vs S-26 1.9909)
CLOSE_CONDITION = "no-PatchTST subset OR heldout_gain<=0.005 OR paired_ci_upper>=0 OR any G1-G3 fails"

# M=4 pool — FROZEN = the Bet 3 pool exactly (D3): NO new members, NO hyperparameter changes.
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
# Stack machinery (per-horizon ridge no-intercept) — verbatim Bet 3
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


def _verify_s26_anchor(expected):
    """Fail-loud S-26 anchor on frozen 11425 — D9: all four values within 1e-4 of Bet 3."""
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

    # disjoint-4 (S-26 anchor stability reference)
    disj_starts = np.array([len(fit_series) + s for s in DISJOINT_STARTS])
    P1d = preds_for_full_fit(make_a1, fit_series, concat_series, disj_starts, HORIZON)
    P2d = preds_for_full_fit(make_a10, fit_series, concat_series, disj_starts, HORIZON)
    Pd = np.stack([P1d, P2d], axis=1)
    Ad = np.stack([test_series[s:s + HORIZON] for s in DISJOINT_STARTS])
    preds_d = stack_val.predict(Pd)
    mae_d, rmse_d, _, _ = rolling_metrics(preds_d, Ad)

    # W4 = hardest disjoint window (start 2160); this is the S-26 anchor's OWN W4,
    # computed in-harness (D7: the incumbent-relative reference, never a leaderboard constant)
    w4 = float(np.mean(np.abs(preds_d[3] - Ad[3])))

    got = {"mae": mae_full, "rmse": rmse_full, "disjoint": mae_d, "w4": w4}
    for k, v in got.items():
        if abs(v - float(expected[k])) > S26_ANCHOR_TOL:
            raise RuntimeError(
                f"S-26 anchor FAIL (D9, tol 1e-4): {k} got {v!r} expected {expected[k]!r} "
                f"(abs diff {abs(v - float(expected[k])):.3e}) — aborting; "
                f"Bet 3 numbers are ground truth")
    return mae_full, rmse_full, mae_d, w4, mae_per_full_anchor, preds_full


# ------------------------------------------------------------------
# Parity machinery (D8) — every section-5 row vs results_patchtst_bet3.json
# ------------------------------------------------------------------
def _num_check(quantity, bet3_v, s44_v, tol=PARITY_TOL):
    b, s = float(bet3_v), float(s44_v)
    d = abs(b - s)
    return {"quantity": quantity, "bet3": b, "s44": s, "abs_diff": d, "pass": bool(d <= tol)}


def _exact_check(quantity, bet3_v, s44_v):
    if isinstance(bet3_v, (list, tuple)) or isinstance(s44_v, (list, tuple)):
        b = [list(x) if isinstance(x, (list, tuple)) else x for x in bet3_v]
        s = [list(x) if isinstance(x, (list, tuple)) else x for x in s44_v]
        ok = b == s
        mism = abs(len(b) - len(s)) + sum(1 for x, y in zip(b, s) if x != y)
        return {"quantity": quantity, "bet3": b, "s44": s, "abs_diff": float(mism), "pass": bool(ok)}
    b, s = float(bet3_v), float(s44_v)
    d = abs(b - s)
    return {"quantity": quantity, "bet3": b, "s44": s, "abs_diff": d, "pass": bool(d == 0.0)}


def _list_num_check(quantity, bet3_list, s44_list, tol=PARITY_TOL):
    b = [float(x) for x in bet3_list]
    s = [float(x) for x in s44_list]
    if len(b) != len(s):
        return {"quantity": quantity, "bet3": b, "s44": s,
                "abs_diff": float(abs(len(b) - len(s)) + 1), "pass": False}
    d = max((abs(x - y) for x, y in zip(b, s)), default=0.0)
    return {"quantity": quantity, "bet3": b, "s44": s, "abs_diff": float(d), "pass": bool(d <= tol)}


def main(argv=None) -> int:
    t_all = time.time()
    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(msg)

    def _write_outputs(out):
        with open(HERE / "results_s44.json", "w") as f:
            json.dump(out, f, indent=2)
        with open(HERE / "harness.log", "w") as f:
            f.write("\n".join(log_lines) + "\n")

    # ---- Determinism: seed-0, CPU only (the Bet 3 encoder re-seeds inside every fit) ----
    torch.manual_seed(0)
    np.random.seed(0)
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    if not BET3_RESULTS.exists():
        raise RuntimeError(f"Bet 3 ground truth missing: {BET3_RESULTS} — D8 parity requires it")
    with open(BET3_RESULTS) as f:
        bet3 = json.load(f)
    b_anchor = bet3["s26_anchor"]

    log("S-44 blend-promotion re-registration of the Bet 3 PatchTST-Delta blend (S44_DESIGN.md, binding).")
    log("Identical frozen pool/seed/protocol as Bet 3 (D3/D4); binding gate BLEND-based per S-43 P1 (D2);")
    log("singleton & regularity conditions demoted to non-binding diagnostics (D5); W1-W4 vs in-harness S-26 anchor (D7).")
    log(f"PatchTST members import the encoder from the sibling Bet 3 dir (architecture-identical code): "
        f"{BET3_DIR / 'patchtst_encoder.py'}")

    pd = get_protocol_data()
    fit_series, concat_series, test_series = pd.rolling_views()
    train_series = fit_series[:TRAIN_END]
    val_series = fit_series[TRAIN_END:]
    n_val = len(val_series) - HORIZON + 1
    assert n_val == 2161, n_val
    assert len(train_series) == 8545 and len(fit_series) == 11425
    val_starts = np.arange(n_val) + TRAIN_END

    # ---- Fail-loud S-26 anchor (D9: all four values vs Bet 3 full precision, tol 1e-4) ----
    log("Verifying S-26 anchor (D9: MAE/RMSE/disjoint/W4 vs Bet 3 full precision, tol 1e-4)...")
    anchor_mae, anchor_rmse, anchor_disj, anchor_w4, anchor_mae_per, anchor_preds = _verify_s26_anchor(b_anchor)
    anchor_got = {"mae": anchor_mae, "rmse": anchor_rmse, "disjoint": anchor_disj, "w4": anchor_w4}
    anchor_pass = {k: bool(abs(anchor_got[k] - float(b_anchor[k])) <= S26_ANCHOR_TOL) for k in anchor_got}
    log(f"S-26 anchor OK: MAE {anchor_mae:.4f} RMSE {anchor_rmse:.4f} disjoint {anchor_disj:.4f} W4 {anchor_w4:.4f}")

    # ---- Collect P_val for all 4 candidates (members frozen on 8545) — verbatim Bet 3 ----
    log(f"Collecting P_val for {N_CAND} candidates (val {n_val} origins, members frozen on {TRAIN_END})...")
    P_val_cols = []
    pt_models = {}  # name -> fitted PatchTSTModel (demoted-diagnostics source, D5)
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

    # ---- Held-out control: 2-member S-26 delta-ridge, re-derived in-harness (D4) ----
    # chronological split val[0:1080) fit / val[1080:2161) select (pooled MAE)
    n2 = n_val // 2  # 1080
    ctrl_P = P_val[:, [0, 1], :]
    ctrl_stack = fit_stack_map(ctrl_P[:n2], A_val[:n2], SEARCH_ALPHA)
    held_out_mae = float(np.mean(np.mean(np.abs(ctrl_stack.predict(ctrl_P[n2:]) - A_val[n2:]), axis=1)))
    # also best-alpha on full val for reference
    _, ctrl_best_a = score_full(ctrl_P, A_val, [0, 1])
    log(f"Held-out S-26 delta-ridge control MAE (val[1080:2161)) = {held_out_mae:.4f} (alpha {ctrl_best_a})")

    # ---- Tabu-7 search over M=4 (fixed-alpha fast 3000, aspiration, no_improve=5) — verbatim Bet 3 ----
    single_scores = [score_fast(P_val, A_val, [j]) for j in range(N_CAND)]
    cur_idx = [int(np.argmin(single_scores))]
    cur_score = single_scores[cur_idx[0]]
    best_idx = list(cur_idx)
    best_score = cur_score
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
    # val_full: chronological hold-out (fit on val[0:n2), score val[n2:)) — matches held-out control protocol.
    # `stack` is THE frozen-test blend stack (D4): per-horizon ridge no-intercept fitted on
    # val[0:1080) at the selected alpha, applied to the 11425-refit members' test predictions
    # (mirror Bet 3 rolling_arm.py:364-367, 419 — no different refit).
    n2 = P_val.shape[0] // 2
    stack = fit_stack_map(P_val[:n2, best_idx, :], A_val[:n2], best_alpha if best_alpha is not None else SEARCH_ALPHA)
    val_full = float(np.mean(np.mean(np.abs(stack.predict(P_val[n2:, best_idx, :]) - A_val[n2:]), axis=1)))
    log(f"refit half-split val MAE {val_full:.4f} alpha {best_alpha}")

    # ---- Held-out precondition (D4/D5-b, close C2): > 0.005 to proceed to frozen test ----
    has_patchtst = any(i in PT_IDX for i in best_idx)
    heldout_gain = held_out_mae - best_score  # positive => subset beats control
    heldout_precondition_pass = heldout_gain > 0.005
    log(f"\nHeld-out precondition: control {held_out_mae:.4f}  best_subset fast {best_score:.4f}  gain {heldout_gain:+.4f}")

    # ---- Demoted regularity audit (D5/D6: non-binding diagnostics; cannot flip the verdict) ----
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
    log(f"Regularity (non-binding diagnostics, D5): max train-val gap {max_gap:.4f} (>0.15={gap_flag})  entropy_collapse(<0.5)={entropy_collapse}")
    if gap_flag or entropy_collapse:
        log("  REGULARITY FLAG (D5/D6): train-val gap > 0.15 or entropy collapse — reported, non-binding; cannot flip the verdict.")

    # ---- Core (val-phase-complete) artifact portion ----
    core = {
        "slice": "S-44-blend-promotion",
        "harness_command": HARNESS_COMMAND,
        "device": f"cpu (torch {torch.__version__})",
        "protocol": "S-20-clean re-registration of Bet 3 (identical frozen pool/seed/protocol); "
                    "binding gate BLEND-based per S-43 P1; singleton/regularity conditions "
                    "demoted to diagnostics",
        "pool": [n for n, _ in CANDIDATES],
        "params": {
            "L": 336, "patch_sizes": [24, 48], "D": [32, 16], "layers": [2, 1],
            "heads": 2, "ffn": [ffn_for(24, 32), ffn_for(48, 16)], "dropout": 0.30,
            "stochastic_depth": 0.10, "weight_decay": 1e-2, "attn_dropout": 0.2,
            "lr": 3e-4, "batch": 64, "grad_clip": 1.0, "H": HORIZON,
            "capacity_primary_params": int(PatchTSTDelta(P=24, D=32, n_layers=2, H=HORIZON).count_params()),
            "capacity_ablation_params": int(PatchTSTDelta(P=48, D=16, n_layers=1, H=HORIZON).count_params()),
        },
        "s26_anchor": {
            "mae": anchor_mae, "rmse": anchor_rmse, "disjoint": anchor_disj, "w4": anchor_w4,
            "tol": S26_ANCHOR_TOL,
            "expected": {"mae": float(b_anchor["mae"]), "rmse": float(b_anchor["rmse"]),
                         "disjoint": float(b_anchor["disjoint"]), "w4": float(b_anchor["w4"])},
            "pass": bool(all(anchor_pass.values())),
        },
        "held_out_control": {
            "type": "2-member S-26 delta-ridge, no-intercept, fit val[0:1080) at fast-alpha 3000",
            "mae_val_heldout": held_out_mae,
            "alpha_reference": ctrl_best_a,
        },
        "singleton_val": singleton_val,
        "trace": trace,
        "best_subset": [CANDIDATES[i][0] for i in best_idx],
        "best_idx": best_idx,
        "best_fast": best_score,
        "best_alpha": best_alpha,
        "val_full": val_full,
        "heldout_gain_over_control": heldout_gain,
        "heldout_precondition_pass": heldout_precondition_pass,
    }

    def emit_parity_abort(checks, stage):
        fails = [c for c in checks if not c["pass"]]
        log(f"\nPARITY FAILURE (D8, {stage}): {len(fails)}/{len(checks)} checks failed — the HARNESS is wrong "
            f"(Bet 3 numbers are ground truth); no promotion verdict is emitted:")
        for c in fails:
            log(f"  FAIL {c['quantity']}: bet3={c['bet3']!r} s44={c['s44']!r} abs_diff={c['abs_diff']!r}")
        out = {**core,
               "parity": {"tol": PARITY_TOL, "checks": checks, "all_pass": False},
               "binding_gate": None, "test_full": None, "bootstrap": None, "stratified": None,
               "test_disjoint": None, "test_w4": None,
               "close": {"condition": CLOSE_CONDITION, "trigger": None,
                         "message": "parity failure (D8) - harness bug; no promotion verdict emitted"},
               "verdict": "ABORT_PARITY",
               "plan_impact": {"invalidates": None, "confirms": None, "opens": None,
                               "note": "harness bug per D8 - fix the harness and re-run; "
                                       "results_patchtst_bet3.json is ground truth"},
               "elapsed_s": float(time.time() - t_all)}
        log(f"Overall VERDICT=ABORT_PARITY ({stage} parity failure; fix harness and re-run)")
        _write_outputs(out)
        print(f"\nwrote {HERE / 'results_s44.json'} (ABORT_PARITY) elapsed {time.time() - t_all:.1f}s")
        return 1

    # ---- VAL-PHASE PARITY (D8): section-5 rows computable before the frozen test ----
    b_trace = bet3["trace"]
    checks = [
        _exact_check("best_subset", bet3["best_subset"], [CANDIDATES[i][0] for i in best_idx]),
        _exact_check("best_alpha", bet3["best_alpha"], best_alpha),
        _num_check("best_fast", bet3["best_fast"], best_score),
        _num_check("held_out_control_mae", bet3["held_out_control"]["mae_val_heldout"], held_out_mae),
        _num_check("heldout_gain", bet3["heldout_gain_over_control"], heldout_gain),
        _num_check("val_full", bet3["val_full"], val_full),
    ]
    for name, _ in CANDIDATES:
        checks.append(_num_check(f"singleton_val_{name}", bet3["singleton_val"][name], singleton_val[name]))
    for k in ("mae", "rmse", "disjoint", "w4"):
        checks.append(_num_check(f"s26_anchor_{k}", b_anchor[k], anchor_got[k]))
    checks.append(_exact_check("held_out_control_alpha_reference", bet3["held_out_control"]["alpha"], ctrl_best_a))
    checks.append(_exact_check("tabu_trace_iter_count", len(b_trace), len(trace)))
    checks.append(_exact_check("tabu_trace_cur_sequence", [t["cur"] for t in b_trace],
                               [t["cur"] for t in trace]))
    checks.append(_exact_check("tabu_trace_best_set_sequence", [t["best_set"] for t in b_trace],
                               [t["best_set"] for t in trace]))
    checks.append(_exact_check("tabu_trace_alpha_sequence", [t["alpha"] for t in b_trace],
                               [t["alpha"] for t in trace]))
    checks.append(_list_num_check("tabu_trace_fast_per_iter", [t["fast"] for t in b_trace],
                                  [t["fast"] for t in trace]))
    checks.append(_list_num_check("tabu_trace_true_per_iter", [t["true"] for t in b_trace],
                                  [t["true"] for t in trace]))
    checks.append(_list_num_check("tabu_trace_best_fast_per_iter", [t["best_fast"] for t in b_trace],
                                  [t["best_fast"] for t in trace]))
    for name, _ in PATCHTST_CANDIDATES:
        checks.append(_num_check(f"train_val_gap_{name}", bet3["regularity"]["train_val_gap"][name],
                                 gap_report[name]))
        checks.append(_num_check(f"attention_entropy_last_{name}",
                                 bet3["regularity"]["attention_entropy_last"][name],
                                 ent_report[name][-1] if ent_report[name] else float("nan")))
    val_parity_pass = all(c["pass"] for c in checks)
    log(f"VAL-PHASE PARITY (D8): {len(checks)} checks vs Bet 3, all_pass={val_parity_pass} (tol 1e-4)")
    if not val_parity_pass:
        return emit_parity_abort(checks, "val-phase")

    # ---- Held-out precondition gate (close C2, D4/D5-b) ----
    # Under D8 parity (gain pinned to 0.020368 within 1e-4) this branch is unreachable;
    # it is the declared procedural gate to the frozen test and is kept explicit per the design.
    if heldout_gain <= 0.005:
        log(f"CLOSE C2: held-out gain {heldout_gain:.4f} <= 0.005 — REJECT at plan time (no frozen test)")
        out = {**core,
               "parity": {"tol": PARITY_TOL, "checks": checks, "all_pass": True},
               "binding_gate": None, "test_full": None, "bootstrap": None, "stratified": None,
               "test_disjoint": None, "test_w4": None,
               "close": {"condition": CLOSE_CONDITION, "trigger": True,
                         "message": "C2: held-out gain <= 0.005 - REJECT at plan time before frozen test"},
               "verdict": "REJECTED",
               "plan_impact": {"invalidates": None,
                               "confirms": "S-26 remains terminal; patch-attention member-capability close (Bet 3) stands (D5)",
                               "opens": None},
               "elapsed_s": float(time.time() - t_all)}
        log("Overall VERDICT=REJECTED")
        _write_outputs(out)
        print(f"\nwrote {HERE / 'results_s44.json'} (REJECTED, C2) elapsed {time.time() - t_all:.1f}s")
        return 0

    # ---- Frozen test (members refrozen on 11425) — verbatim Bet 3 ----
    n_test = len(test_series) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_series)

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
    disj_local = [int(s) for s in DISJOINT_STARTS]  # P_test row k -> full-origin len(fit)+k
    P_disj = P_test[disj_local]
    A_disj = np.stack([test_series[s:s + HORIZON] for s in DISJOINT_STARTS])

    # ---- Metrics: full, disjoint-4, W4 (test stack = the SAME val half-split `stack`, D4) ----
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
    w4_vs_s26 = w4_mae - anchor_w4

    # ---- Bootstrap 95% CI (convention: resample origins, B=2000, seed 0) — verbatim Bet 3 ----
    bs_mean_s44, bs_lo_s44, bs_hi_s44, bs_B = bootstrap_mean_ci(mae_per_full, seed=0)
    bs_mean_s26, bs_lo_s26, bs_hi_s26, _ = bootstrap_mean_ci(anchor_mae_per, seed=0)
    delta_mean, d_lo, d_hi, _ = bootstrap_paired_diff_ci(mae_per_full, anchor_mae_per, seed=0)
    log(f"Bootstrap 95% CI (B={bs_B}): S-44 full [{bs_lo_s44:.4f}, {bs_hi_s44:.4f}] mean {bs_mean_s44:.4f}; "
        f"S-26 [{bs_lo_s26:.4f}, {bs_hi_s26:.4f}] mean {bs_mean_s26:.4f}")
    log(f"Paired delta (S44-S26) mean {delta_mean:+.4f} 95% CI [{d_lo:+.4f}, {d_hi:+.4f}] "
        f"({'UPPER BOUND < 0 => promotion-supported' if d_hi < 0 else 'upper bound >= 0 => not decisive'})")
    # Stratified breakdown by disjoint W1-W4 and horizon tercile — vs the IN-HARNESS anchor (D7)
    strat_disj = []
    for k, s in enumerate(DISJOINT_STARTS):
        seg = mae_per_full[s:s + 720]
        sa = anchor_mae_per[s:s + 720]
        seg_d = float(np.mean(seg - sa))
        strat_disj.append({"window": f"W{k+1}", "start": int(s), "s44_mae": float(np.mean(seg)),
                           "s26_mae": float(np.mean(sa)), "delta": seg_d})
        log(f"  strat W{k+1} (origin {s:4d}): S-44 {np.mean(seg):.4f}  S-26 {np.mean(sa):.4f}  delta {seg_d:+.4f}")
    # horizon tercile within each origin: first/mid/last 240 steps (per-origin 2-D MAE)
    s44_terr = np.abs(preds_full - A_test)  # (n_test, 720)
    s26_terr = np.abs(anchor_preds - A_test)
    n_h = HORIZON // 3
    terc = []
    for t, lbl in enumerate(["h1_first240", "h2_mid240", "h3_last240"]):
        sl = slice(t * n_h, (t + 1) * n_h)
        seg = s44_terr[:, sl].mean()
        sa = s26_terr[:, sl].mean()
        seg_d = float(seg - sa)
        terc.append({"horizon_tercile": lbl, "s44_mae": float(seg),
                     "s26_mae": float(sa), "delta": seg_d})
        log(f"  horizon {lbl}: S-44 {seg:.4f}  S-26 {sa:.4f}  delta {seg_d:+.4f}")
    log(f"\nS-26 incumbent (in-harness): full {anchor_mae:.4f} / {S26_DISJOINT} disjoint / W4 {anchor_w4:.4f}")
    log(f"S-44 blend best full {mae_full:.4f} / {rmse_full:.4f} disjoint {mae_disj:.4f} W4 {w4_mae:.4f} val_full {val_full:.4f}")
    log(f"W4 (non-binding diagnostic, D7): S-44 {w4_mae:.4f} vs in-harness S-26 anchor {anchor_w4:.4f} -> {w4_vs_s26:+.4f}")

    # ---- FULL PARITY (D8): frozen-test rows appended to the val-phase checks ----
    checks += [
        _num_check("test_full_mae", bet3["test_full"]["mae"], mae_full),
        _num_check("test_full_rmse", bet3["test_full"]["rmse"], rmse_full),
        _num_check("test_disjoint_mae", bet3["test_disjoint"]["mae"], mae_disj),
        _num_check("test_disjoint_rmse", bet3["test_disjoint"]["rmse"], rmse_disj),
        _num_check("test_w4_mae", bet3["test_w4"]["mae"], w4_mae),
        _num_check("paired_ci_lower", bet3["bootstrap"]["paired_delta"]["ci_95"][0], d_lo),
        _num_check("paired_ci_upper", bet3["bootstrap"]["paired_delta"]["ci_95"][1], d_hi),
        _num_check("bootstrap_paired_delta_mean", bet3["bootstrap"]["paired_delta"]["mean"], delta_mean),
        _num_check("bootstrap_s44_full_ci_lower", bet3["bootstrap"]["bet3_full"]["ci_95"][0], bs_lo_s44),
        _num_check("bootstrap_s44_full_ci_upper", bet3["bootstrap"]["bet3_full"]["ci_95"][1], bs_hi_s44),
        _num_check("bootstrap_s26_full_ci_lower", bet3["bootstrap"]["s26_full"]["ci_95"][0], bs_lo_s26),
        _num_check("bootstrap_s26_full_ci_upper", bet3["bootstrap"]["s26_full"]["ci_95"][1], bs_hi_s26),
    ]
    for r_b, r_s in zip(bet3["stratified"]["disjoint_windows"], strat_disj):
        checks.append(_num_check(f"strat_{r_b['window']}_s44_mae", r_b["bet3_mae"], r_s["s44_mae"]))
        checks.append(_num_check(f"strat_{r_b['window']}_s26_mae", r_b["s26_mae"], r_s["s26_mae"]))
        checks.append(_num_check(f"strat_{r_b['window']}_delta", r_b["delta"], r_s["delta"]))
    for r_b, r_s in zip(bet3["stratified"]["horizon_terciles"], terc):
        checks.append(_num_check(f"tercile_{r_b['horizon_tercile']}_s44_mae", r_b["bet3_mae"], r_s["s44_mae"]))
        checks.append(_num_check(f"tercile_{r_b['horizon_tercile']}_s26_mae", r_b["s26_mae"], r_s["s26_mae"]))
        checks.append(_num_check(f"tercile_{r_b['horizon_tercile']}_delta", r_b["delta"], r_s["delta"]))
    all_parity_pass = all(c["pass"] for c in checks)
    log(f"PARITY (D8): {len(checks)} checks vs Bet 3, all_pass={all_parity_pass} (tol 1e-4)")
    if not all_parity_pass:
        return emit_parity_abort(checks, "test-phase")

    # ---- Binding gate (D2) + close conditions (D5) + verdict (D11) ----
    g1 = mae_full <= G1_FULL_BOUND
    g2 = mae_full < S26_ANCHOR_MAE
    g3 = mae_disj <= S26_DISJOINT
    g4 = d_hi < 0.0
    all_binding = g1 and g2 and g3 and g4
    close_c1 = not has_patchtst
    close_c2 = heldout_gain <= 0.005
    close_c3 = d_hi >= 0.0
    close_c4 = not (g1 and g2 and g3)
    close_trigger = close_c1 or close_c2 or close_c3 or close_c4
    verdict = "PROMOTED" if (all_binding and not close_trigger) else "REJECTED"

    log(f"Binding gate (D2): G1 full<={G1_FULL_BOUND} {g1} ({mae_full:.4f})  "
        f"G2 full<{S26_ANCHOR_MAE} {g2}  G3 disjoint<={S26_DISJOINT} {g3} ({mae_disj:.4f})  "
        f"G4 paired-CI-upper<0 {g4} ({d_hi:+.4f})  all_binding_pass={all_binding}")
    log(f"Close conditions (D5): C1 no-PatchTST {close_c1}  C2 heldout_gain<=0.005 {close_c2}  "
        f"C3 CI-upper>=0 {close_c3}  C4 any-G1-G3-fails {close_c4}  trigger={close_trigger}")
    log(f"Overall VERDICT={verdict}")

    if close_trigger:
        close_message = ("close condition fired - S-26 remains terminal; patch-attention "
                         "member-capability close (Bet 3) stands (D5)")
        plan_impact = {"invalidates": None,
                       "confirms": "S-26 remains terminal; patch-attention member-capability close (Bet 3) stands (D5)",
                       "opens": None}
    else:
        close_message = "no close condition fired"
        plan_impact = {"invalidates": "S-26 incumbent status (moves to second place) on PROMOTION",
                       "confirms": "patch-attention member-capability close (S-43 P3 record updated)",
                       "opens": "blend-incumbent frontier: future bets must beat the S-44 blend under a declared gate"}

    out = {**core,
           "parity": {"tol": PARITY_TOL, "checks": checks, "all_pass": all_parity_pass},
           "binding_gate": {
               "full_le_19859": {"value": mae_full, "pass": bool(g1)},
               "full_lt_s26": {"value": mae_full, "s26": S26_ANCHOR_MAE, "pass": bool(g2)},
               "disjoint_le_19696": {"value": mae_disj, "pass": bool(g3)},
               "paired_ci_upper_lt_0": {"ci_95": [d_lo, d_hi], "upper": d_hi, "pass": bool(g4)},
               "all_binding_pass": bool(all_binding),
           },
           "demoted_diagnostics": {
               "patchtst_singleton_vals": patchtst_singleton_vals,
               "best_patchtst_val": best_patchtst_val,
               "best_patchtst_name": best_patchtst_name,
               "train_val_gap": gap_report,
               "gap_flag": gap_flag,
               "attention_entropy_last": {k: (v[-1] if v else float("nan")) for k, v in ent_report.items()},
               "entropy_collapse": entropy_collapse,
               "w1_w4_deltas": [{"window": r["window"], "s44_mae": r["s44_mae"],
                                 "s26_mae": r["s26_mae"], "delta": r["delta"]} for r in strat_disj],
               "w1_regression_note": f"W1 {strat_disj[0]['delta']:+.4f} vs in-harness S-26 anchor — reported, non-binding",
               "horizon_terciles": terc,
           },
           "test_full": {"mae": mae_full, "rmse": rmse_full, "n": n_test,
                         "delta_vs_s26": mae_full - S26_ANCHOR_MAE},
           "bootstrap": {
               "convention": "resample origins, B=2000, seed 0, percentile 2.5/97.5",
               "s44_full": {"mean": bs_mean_s44, "ci_95": [bs_lo_s44, bs_hi_s44], "B": bs_B},
               "s26_full": {"mean": bs_mean_s26, "ci_95": [bs_lo_s26, bs_hi_s26], "B": bs_B},
               "paired_delta": {"mean": delta_mean, "ci_95": [d_lo, d_hi], "B": bs_B,
                                "upper_bound_negative": bool(d_hi < 0)},
           },
           "stratified": {"disjoint_windows": strat_disj, "horizon_terciles": terc},
           "test_disjoint": {"mae": mae_disj, "rmse": rmse_disj},
           "test_w4": {"mae": w4_mae, "s26_incumbent_w4": anchor_w4,
                       "w4_delta_vs_s26": w4_vs_s26, "binding": False},
           "close": {"condition": CLOSE_CONDITION,
                     "c1_no_patchtst": bool(close_c1), "c2_heldout_gain": bool(close_c2),
                     "c3_ci_upper_ge_0": bool(close_c3), "c4_any_g1_g3_fails": bool(close_c4),
                     "trigger": bool(close_trigger), "message": close_message},
           "verdict": verdict,
           "plan_impact": plan_impact,
           "elapsed_s": float(time.time() - t_all)}
    _write_outputs(out)
    print(f"\nwrote {HERE / 'results_s44.json'} elapsed {time.time() - t_all:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
