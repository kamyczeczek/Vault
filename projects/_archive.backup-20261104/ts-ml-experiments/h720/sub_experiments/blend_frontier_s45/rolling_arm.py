"""S-45 — Blend-Frontier Expansion vs the S-44 Incumbent Blend (h720 ETTh1 H=720).

Pre-registration contract: S45_DESIGN.md in this directory (D1-D10, §4, §5, §6) —
FINAL and BINDING; implemented verbatim. This is a NEW bet (first against the
S-44 blend incumbent): the tabu-selected subset's frozen-test blend must beat the
S-44 incumbent blend RE-DERIVED IN-HARNESS (not S-26), under a blend-based gate
declared per S-43 P1 / S-44 P2.

  - Binding gate (D2) vs the in-harness S-44 incumbent re-derivation:
        G1  MAE_full <= incumbent_full - 0.0050  (= 1.978126 - 0.0050 = 1.9731)
        G2  MAE_full <  incumbent_full           (= 1.9781)
        G3  MAE_disjoint-4 <= incumbent disjoint  (= 1.8634, incumbent-relative,
            the honest bar; the S-26 cap 1.9696 is a secondary non-binding check)
        G4  paired-bootstrap delta CI upper < 0 (B=2000, seed 0, resample origins;
            convention identical to S-44/Bet 3 bootstrap_paired_diff_ci)
  - Pool M=6 frozen (D3, FIXED order — tabu tie-breaking depends on it):
        [nlinear_L336_a1, nlinear_L336_a10, patchtst_P24_D32_2L, patchtst_P48_D16_1L,
         patchtst_P24_D32_2L_s1, patchtst_cross_P24_D32_2L]
        The first 4 are the S-44 pool verbatim (encoder imported VERBATIM from the
        sibling Bet 3 dir, seed 0 — they MUST reproduce parity). The twin trains
        under seed 1 via the PatchTSTModelS1 mirror (patchtst_cross.py, D1); the
        cross member under seed 0 (patchtst_cross.py, D3).
  - Held-out control (D4) = the S-44 incumbent 3-member blend re-derived on val
    (per-horizon ridge no-intercept alpha=30000, fit val[0:1080), scored
    val[1080:2161)) = the incumbent's val_full 2.493567 (§5 parity row).
    Precondition: selected subset's score_full must beat it by > 0.005.
  - Close conditions (D5, any -> REJECTED): C1 subset ⊆ S-44 pool (no new member);
    C2 held-out gain <= 0.005; C3 paired CI upper >= 0; C4 any of G1-G3 fails.
    Family close (additional): BOTH new-member singleton vals > 2.90 AND no
    new-member subset beats the incumbent held-out control (2.493567) on
    val[1080:2161) -> blend-frontier-expansion family closed under S-20-clean.
  - Parity block (D6, S-44 P1): the S-44 incumbent is re-derived as a subset
    evaluation in this SAME run (its 3 members are in the pool; its stack at its
    alpha=30000) and parity-checked vs results_s44.json on every §5 row at tol
    1e-4, plus the fail-loud S-26 anchor (1.990897/2.470999/1.969617/1.957937,
    ±1e-4). Any failure -> verdict ABORT_PARITY (harness bug; fix, re-run).
  - Incumbent anchor discipline (D7, S-44 P2): every comparison/bootstrap/W-window
    delta is vs the IN-HARNESS S-44 blend derivation from this run; the only
    copied constants are the §5 parity expected-values themselves (read from
    results_s44.json at run start).

Determinism (D9): torch.manual_seed(0) + np.random.seed(0) at harness start (the
Bet 3 encoder additionally re-seeds to 0 inside every fit; the twin re-seeds to 1
inside its fit), CPU only, torch.use_deterministic_algorithms(True, warn_only=True).
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from itertools import combinations
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import Ridge

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "patchtst_delta_bet3"))

from data import HORIZON, get_protocol_data  # noqa: E402
from methods.neural_models import NLinear  # noqa: E402
from patchtst_encoder import PatchTSTDelta, PatchTSTModel, ffn_for  # noqa: E402  <- sibling Bet 3 module
from patchtst_cross import (  # noqa: E402  <- S-45 new members (D1/D3)
    PatchTSTCrossDelta,
    PatchTSTCrossModel,
    PatchTSTModelS1,
    CROSS_N_TOKENS,
)

S44_DIR = HERE.parent / "blend_promotion_s44"
S44_RESULTS = S44_DIR / "results_s44.json"
BET3_DIR = HERE.parent / "patchtst_delta_bet3"
HARNESS_COMMAND = (
    "C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe "
    "projects/ts-ml-experiments/h720/sub_experiments/blend_frontier_s45/rolling_arm.py"
)

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
SEARCH_ALPHA = 3000.0
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]
S26_ANCHOR_TOL = 1e-4     # D6 fail-loud anchor tolerance
PARITY_TOL = 1e-4         # D6 parity tolerance (design section 5)
S26_DISJOINT_CAP = 1.9696  # secondary non-binding check (D2)
G1_MARGIN = 0.0050        # H2 >= 0.0050 improvement bound applied to the incumbent
CLOSE_CONDITION = ("subset-of-S44-pool OR heldout_gain<=0.005 OR paired_ci_upper>=0 "
                   "OR any G1-G3 fails")
CSV_COLS = ["HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL", "OT"]
CHANNELS = ["OT", "HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL"]
CHANNEL_TO_CSV_IDX = [CSV_COLS.index(ch) for ch in CHANNELS]

# M=6 pool — FROZEN (D3, FIXED order; tabu neighbor enumeration and stable-sort
# tie-breaking depend on it). First 4 = the S-44 pool verbatim (seed 0).
CANDIDATES = [
    ("nlinear_L336_a1", lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
    ("patchtst_P24_D32_2L", lambda: PatchTSTModel(patch_size=24, D=32, n_layers=2, H=HORIZON)),
    ("patchtst_P48_D16_1L", lambda: PatchTSTModel(patch_size=48, D=16, n_layers=1, H=HORIZON)),
    ("patchtst_P24_D32_2L_s1", lambda: PatchTSTModelS1(patch_size=24, D=32, n_layers=2, H=HORIZON)),
    ("patchtst_cross_P24_D32_2L", lambda: PatchTSTCrossModel(patch_size=24, D=32, n_layers=2, H=HORIZON)),
]
UNIVARIATE_1D = {0, 1, 2, 3, 4}          # indices trained on the 1-D OT series
INCUMBENT_IDX = [0, 1, 2]                # the S-44 incumbent's 3-member subset (D6)
INCUMBENT_ALPHA = 30000.0                # the S-44 incumbent's stack alpha (D4/D6)
NEW_MEMBER_IDX = [4, 5]                  # twin, cross
N_CAND = len(CANDIDATES)


# ------------------------------------------------------------------
# Stack machinery (per-horizon ridge no-intercept) — verbatim Bet 3/S-44
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


def bootstrap_paired_diff_ci(d_new, d_inc, B=2000, seed=0):
    """Paired bootstrap 95% CI on per-origin MAE differences (new - incumbent)."""
    n = len(d_new)
    rng = np.random.default_rng(seed)
    boot = np.empty(B, dtype=float)
    for b in range(B):
        idx = rng.integers(0, n, size=n)
        boot[b] = float(np.mean(d_new[idx] - d_inc[idx]))
    return float(np.mean(d_new - d_inc)), float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)), B


# ------------------------------------------------------------------
# Multivariate loading (D3: mirror Bet 2's load_multivariate_split)
# ------------------------------------------------------------------
def load_multivariate_split():
    import csv

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
    train_multi = raw_train[:, CHANNEL_TO_CSV_IDX]  # reorder to CHANNELS (OT first)
    test_multi = raw_test[:, CHANNEL_TO_CSV_IDX]
    fit_multi = train_multi
    concat_multi = np.concatenate([fit_multi, test_multi], axis=0)
    ot_ch = CHANNELS.index("OT")  # 0
    return fit_multi, concat_multi, test_multi, ot_ch


# ------------------------------------------------------------------
# Parity machinery (D6) — every §5 row vs results_s44.json
# ------------------------------------------------------------------
def _num_check(quantity, s44_v, s45_v, tol=PARITY_TOL):
    b, s = float(s44_v), float(s45_v)
    d = abs(b - s)
    return {"quantity": quantity, "s44": b, "s45": s, "abs_diff": d, "pass": bool(d <= tol)}


def _exact_check(quantity, s44_v, s45_v):
    if isinstance(s44_v, (list, tuple)) or isinstance(s45_v, (list, tuple)):
        b = [list(x) if isinstance(x, (list, tuple)) else x for x in s44_v]
        s = [list(x) if isinstance(x, (list, tuple)) else x for x in s45_v]
        ok = b == s
        mism = abs(len(b) - len(s)) + sum(1 for x, y in zip(b, s) if x != y)
        return {"quantity": quantity, "s44": b, "s45": s, "abs_diff": float(mism), "pass": bool(ok)}
    b, s = float(s44_v), float(s45_v)
    d = abs(b - s)
    return {"quantity": quantity, "s44": b, "s45": s, "abs_diff": d, "pass": bool(d == 0.0)}


# ------------------------------------------------------------------
# Fail-loud S-26 anchor (D6) — verbatim S-44 _verify_s26_anchor
# ------------------------------------------------------------------
def _verify_s26_anchor(expected):
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
    preds_full = stack_val.predict(P)
    mae_full, rmse_full, mae_per_full_anchor, _ = rolling_metrics(preds_full, A)

    disj_starts = np.array([len(fit_series) + s for s in DISJOINT_STARTS])
    P1d = preds_for_full_fit(make_a1, fit_series, concat_series, disj_starts, HORIZON)
    P2d = preds_for_full_fit(make_a10, fit_series, concat_series, disj_starts, HORIZON)
    Pd = np.stack([P1d, P2d], axis=1)
    Ad = np.stack([test_series[s:s + HORIZON] for s in DISJOINT_STARTS])
    preds_d = stack_val.predict(Pd)
    mae_d, rmse_d, _, _ = rolling_metrics(preds_d, Ad)

    w4 = float(np.mean(np.abs(preds_d[3] - Ad[3])))

    got = {"mae": mae_full, "rmse": rmse_full, "disjoint": mae_d, "w4": w4}
    for k, v in got.items():
        if abs(v - float(expected[k])) > S26_ANCHOR_TOL:
            raise RuntimeError(
                f"S-26 anchor FAIL (D6, tol 1e-4): {k} got {v!r} expected {expected[k]!r} "
                f"(abs diff {abs(v - float(expected[k])):.3e}) — aborting; "
                f"results_s44.json numbers are ground truth")
    return mae_full, rmse_full, mae_d, w4, mae_per_full_anchor, preds_full


def main(argv=None) -> int:
    t_all = time.time()
    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(msg)

    def _write_outputs(out):
        with open(HERE / "results_s45.json", "w") as f:
            json.dump(out, f, indent=2)
        with open(HERE / "harness.log", "w") as f:
            f.write("\n".join(log_lines) + "\n")

    # ---- Determinism: seed-0 harness level, CPU only (D9) ----
    torch.manual_seed(0)
    np.random.seed(0)
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    if not S44_RESULTS.exists():
        raise RuntimeError(f"S-44 ground truth missing: {S44_RESULTS} — D6 parity requires it")
    with open(S44_RESULTS) as f:
        s44 = json.load(f)
    b_anchor = s44["s26_anchor"]  # the ONLY permitted copied constants (D7): §5 expected values

    log("S-45 blend-frontier expansion vs the S-44 incumbent blend (S45_DESIGN.md, binding).")
    log("Binding gate BLEND-based vs the IN-HARNESS S-44 incumbent re-derivation per S-43 P1 / S-44 P2 (D2);")
    log("singleton/regularity conditions demoted to diagnostics (D5); parity block per S-44 P1 (D6).")
    log(f"Bet 3 encoder imported VERBATIM from the sibling dir (architecture-identical code): "
        f"{BET3_DIR / 'patchtst_encoder.py'}")
    log("S-45 new members from patchtst_cross.py: PatchTSTModelS1 (seed-1 twin, ONE-DELTA mirror of "
        "PatchTSTModel.fit — only the fit()-start determinism call differs) + PatchTSTCrossModel "
        f"({CROSS_N_TOKENS}-token 7-channel cross-attention member, seed 0).")

    # ---- Data: 1-D OT protocol views + Bet 2's multivariate split (D3) ----
    pd = get_protocol_data()
    fit_series, concat_series, test_series = pd.rolling_views()
    train_series = fit_series[:TRAIN_END]
    val_series = fit_series[TRAIN_END:]
    n_val = len(val_series) - HORIZON + 1
    assert n_val == 2161, n_val
    assert len(train_series) == 8545 and len(fit_series) == 11425
    val_starts = np.arange(n_val) + TRAIN_END

    fit_multi, concat_multi, test_multi, ot_ch = load_multivariate_split()
    assert fit_multi.shape == (11425, 7), fit_multi.shape
    # Fail-loud multivariate sync (D3, Bet 2 rolling_arm.py:289 pattern) —
    # the cross member's OT column MUST be the same series as the protocol OT
    assert np.allclose(fit_multi[:, ot_ch], fit_series), "fit_multi OT mismatch with fit_series"
    assert np.allclose(test_multi[:, ot_ch], test_series), "test_multi OT mismatch with test_series"
    train_multi = fit_multi[:TRAIN_END]
    log(f"Multivariate split loaded (Bet 2 path, CHANNELS order OT-first): fit {fit_multi.shape}, "
        f"test {test_multi.shape} — OT sync asserts PASS")

    # ---- Fail-loud S-26 anchor (D6: ±1e-4 vs results_s44.json full precision) ----
    log("Verifying S-26 anchor (D6: MAE/RMSE/disjoint/W4 vs results_s44.json, tol 1e-4)...")
    anchor_mae, anchor_rmse, anchor_disj, anchor_w4, anchor_mae_per, anchor_preds = _verify_s26_anchor(b_anchor)
    anchor_got = {"mae": anchor_mae, "rmse": anchor_rmse, "disjoint": anchor_disj, "w4": anchor_w4}
    anchor_pass = {k: bool(abs(anchor_got[k] - float(b_anchor[k])) <= S26_ANCHOR_TOL) for k in anchor_got}
    log(f"S-26 anchor OK: MAE {anchor_mae:.4f} RMSE {anchor_rmse:.4f} disjoint {anchor_disj:.4f} W4 {anchor_w4:.4f}")

    # ---- Collect P_val for all 6 candidates (members frozen on 8545) ----
    log(f"Collecting P_val for {N_CAND} candidates (val {n_val} origins, members frozen on {TRAIN_END})...")
    P_val_cols = []
    pt_models = {}  # name -> fitted PatchTST-family member (demoted-diagnostics source, D5)
    for j, (name, factory) in enumerate(CANDIDATES):
        t0 = time.time()
        if name.startswith("patchtst"):
            log(f"  training {name} on train 8545 (this may take minutes)...")
        if j in UNIVARIATE_1D:
            p, m = preds_for_train_fit(factory, train_series, fit_series, val_starts, HORIZON)
        else:
            p, m = preds_for_train_fit(factory, train_multi, fit_multi, val_starts, HORIZON)
        P_val_cols.append(p)
        if name.startswith("patchtst"):
            pt_models[name] = m
        log(f"  {name:24s} ok {p.shape} ({time.time()-t0:.1f}s)")
    P_val = np.stack(P_val_cols, axis=1)  # (n_val, 6, 720)
    A_val = np.stack([val_series[t:t + HORIZON] for t in range(n_val)])

    # singleton val per candidate
    singleton_val = {}
    for j, (name, _) in enumerate(CANDIDATES):
        mae = float(np.mean(np.mean(np.abs(P_val[:, j, :] - A_val), axis=1)))
        singleton_val[name] = mae
        log(f"  singleton {name:24s} val {mae:.4f}")

    # ---- Twin-vs-seed0 divergence tripwire (D1/D9: exact 0 => seed discipline violated => VOID) ----
    twin_div_abs = float(np.mean(np.abs(P_val[:, 4, :] - P_val[:, 2, :])))
    tv_a, tv_b = P_val[:, 4, :].ravel(), P_val[:, 2, :].ravel()
    twin_corr = float(np.corrcoef(tv_a, tv_b)[0, 1])
    log(f"Twin divergence vs seed-0 P24 member (val, D1 tripwire): mean |delta pred| {twin_div_abs:.6f}  corr {twin_corr:.6f}")
    twin_exact_zero = bool(twin_div_abs == 0.0)

    # ---- Held-out control (D4): the S-44 incumbent 3-member blend re-derived on val ----
    # Its stack: per-horizon ridge no-intercept at ITS alpha (30000), fit val[0:1080),
    # scored val[1080:2161) — by construction equals the incumbent's val_full (§5 parity row).
    n2 = n_val // 2  # 1080
    inc_P = P_val[:, INCUMBENT_IDX, :]
    inc_ctrl_stack = fit_stack_map(inc_P[:n2], A_val[:n2], INCUMBENT_ALPHA)
    held_out_mae = float(np.mean(np.mean(np.abs(inc_ctrl_stack.predict(inc_P[n2:]) - A_val[n2:]), axis=1)))
    log(f"Held-out S-44 incumbent-blend control MAE (val[1080:2161)) = {held_out_mae:.4f} (alpha {INCUMBENT_ALPHA:.0f})")

    # ---- Tabu-7 search over M=6 (fixed-alpha fast 3000, aspiration, no_improve=5) — verbatim Bet 3 ----
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
    # `stack` is THE frozen-test blend stack (D4): per-horizon ridge no-intercept
    # fitted on val[0:1080) at the selected alpha, applied to the 11425-refit
    # members' test predictions (Bet 3/S-44 convention exactly).
    stack = fit_stack_map(P_val[:n2, best_idx, :], A_val[:n2], best_alpha if best_alpha is not None else SEARCH_ALPHA)
    val_full = float(np.mean(np.mean(np.abs(stack.predict(P_val[n2:, best_idx, :]) - A_val[n2:]), axis=1)))
    log(f"refit half-split val MAE {val_full:.4f} alpha {best_alpha}")

    # ---- Held-out precondition (D4/C2): > 0.005 vs the incumbent control to reach test ----
    heldout_gain = held_out_mae - best_score  # positive => subset beats incumbent control
    heldout_precondition_pass = heldout_gain > 0.005
    log(f"\nHeld-out precondition: incumbent control {held_out_mae:.4f}  best_subset fast {best_score:.4f}  gain {heldout_gain:+.4f}")

    # ---- Demoted regularity audit (D5: non-binding diagnostics; cannot flip the verdict) ----
    gap_report = {}
    ent_report = {}
    for name, _ in CANDIDATES:
        if not name.startswith("patchtst"):
            continue
        m = pt_models.get(name)
        if m is None:
            continue
        gap_report[name] = float(m.train_val_gap_) if m.train_val_gap_ is not None else float("nan")
        ent_report[name] = [float(x) for x in (m.attention_entropies_ or [float("nan")])]
        log(f"  AUDIT {name:24s} train-val gap {gap_report[name]:+.4f}  attention_entropy_last {ent_report[name][-1] if ent_report[name] else float('nan'):.3f}")
    max_gap = max(gap_report.values()) if gap_report else float("nan")
    entropy_collapse = any(len(v) > 0 and v[-1] < 0.5 for v in ent_report.values())
    gap_flag = max_gap > 0.15
    log(f"Regularity (non-binding diagnostics, D5): max train-val gap {max_gap:.4f} (>0.15={gap_flag})  entropy_collapse(<0.5)={entropy_collapse}")

    # ---- Core (val-phase-complete) artifact portion ----
    core = {
        "slice": "S-45-blend-frontier",
        "harness_command": HARNESS_COMMAND,
        "device": f"cpu (torch {torch.__version__})",
        "protocol": "S-20-clean blend-frontier expansion of the S-44 incumbent; binding gate "
                    "BLEND-based vs the in-harness S-44 incumbent re-derivation (S-43 P1 / "
                    "S-44 P2); parity block per S-44 P1",
        "pool": [n for n, _ in CANDIDATES],
        "new_members": {
            "patchtst_P24_D32_2L_s1": {
                "type": "seed-1 twin of the incumbent's univariate PatchTST-Delta member "
                        "(Bet 3 architecture verbatim; ONE-DELTA mirror of PatchTSTModel.fit — "
                        "only the fit()-start determinism call differs, patchtst_cross.py)",
                "seed": 1},
            "patchtst_cross_P24_D32_2L": {
                "type": f"7-channel level-free cross-attention PatchTST: {CROSS_N_TOKENS} tokens "
                        "(7ch x 14 patches), channel-shared proj P24->D32 + channel embedding "
                        "+ pos encoding, 2-layer Transformer heads=2 FFN=64, no causal mask",
                "seed": 0},
        },
        "params": {
            "L": 336, "P": 24, "D": 32, "layers": 2, "heads": 2, "ffn": ffn_for(24, 32),
            "dropout": 0.30, "stochastic_depth": 0.10, "weight_decay": 1e-2,
            "attn_dropout": 0.2, "lr": 3e-4, "batch": 64, "grad_clip": 1.0, "H": HORIZON,
            "capacity_cross_params": int(PatchTSTCrossDelta(P=24, D=32, n_layers=2, H=HORIZON).count_params()),
            "capacity_twin_params": int(PatchTSTDelta(P=24, D=32, n_layers=2, H=HORIZON).count_params()),
            "early_stop": "patience 40, max_epochs 400, internal n//8 chronological tail split "
                          "(Bet 3 shipped discipline)",
        },
        "s26_anchor": {
            "mae": anchor_mae, "rmse": anchor_rmse, "disjoint": anchor_disj, "w4": anchor_w4,
            "tol": S26_ANCHOR_TOL,
            "expected": {"mae": float(b_anchor["mae"]), "rmse": float(b_anchor["rmse"]),
                         "disjoint": float(b_anchor["disjoint"]), "w4": float(b_anchor["w4"])},
            "pass": bool(all(anchor_pass.values())),
        },
        "held_out_control": {
            "type": "S-44 incumbent 3-member blend re-derived: per-horizon ridge no-intercept "
                    "alpha=30000, fit val[0:1080), scored val[1080:2161)",
            "mae_val_heldout": held_out_mae,
            "alpha": INCUMBENT_ALPHA,
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
        log(f"\nPARITY FAILURE (D6, {stage}): {len(fails)}/{len(checks)} checks failed — the HARNESS is wrong "
            f"(results_s44.json numbers are ground truth); no verdict is emitted:")
        for c in fails:
            log(f"  FAIL {c['quantity']}: s44={c['s44']!r} s45={c['s45']!r} abs_diff={c['abs_diff']!r}")
        out = {**core,
               "parity": {"tol": PARITY_TOL, "checks": checks, "all_pass": False},
               "binding_gate": None, "secondary_checks": None, "test_full": None,
               "bootstrap": None, "stratified": None, "test_disjoint": None,
               "test_w4": None, "incumbent_s44_rederived": None,
               "close": {"condition": CLOSE_CONDITION, "trigger": None,
                         "message": "parity failure (D6) - harness bug; no verdict emitted"},
               "verdict": "ABORT_PARITY",
               "plan_impact": {"invalidates": None, "confirms": None, "opens": None,
                               "note": "harness bug per D6 - fix the harness and re-run; "
                                       "results_s44.json is ground truth"},
               "elapsed_s": float(time.time() - t_all)}
        log(f"Overall VERDICT=ABORT_PARITY ({stage} parity failure; fix harness and re-run)")
        _write_outputs(out)
        print(f"\nwrote {HERE / 'results_s45.json'} (ABORT_PARITY) elapsed {time.time() - t_all:.1f}s")
        return 1

    # ---- VAL-PHASE PARITY (D6): §5 rows computable before the frozen test ----
    # §5 full-precision expected values READ from results_s44.json (not retyped).
    inc_best_fast = score_fast(P_val, A_val, INCUMBENT_IDX)  # 3-member fast @ alpha=3000
    b_strat = s44["stratified"]
    checks = [
        _exact_check("incumbent_subset", s44["best_subset"], [CANDIDATES[i][0] for i in INCUMBENT_IDX]),
        _exact_check("incumbent_stack_alpha", s44["best_alpha"], INCUMBENT_ALPHA),
        _num_check("incumbent_best_fast", s44["best_fast"], inc_best_fast),
        _num_check("incumbent_val_full", s44["val_full"], held_out_mae),  # = held-out control (D4)
    ]
    for name in [c[0] for c in CANDIDATES[:4]]:
        checks.append(_num_check(f"singleton_val_{name}", s44["singleton_val"][name], singleton_val[name]))
    for k in ("mae", "rmse", "disjoint", "w4"):
        checks.append(_num_check(f"s26_anchor_{k}", b_anchor[k], anchor_got[k]))
    val_parity_pass = all(c["pass"] for c in checks)
    log(f"VAL-PHASE PARITY (D6): {len(checks)} checks vs results_s44.json, all_pass={val_parity_pass} (tol 1e-4)")
    if not val_parity_pass:
        return emit_parity_abort(checks, "val-phase")

    # ---- Twin seed-discipline tripwire (D1/D9): exact-0 divergence => VOID ----
    if twin_exact_zero:
        log("SEED-DISCIPLINE VIOLATION (D1/D9): twin predictions exactly equal the seed-0 member's "
            "(divergence 0.0) — the twin trained under seed 0; run VOID.")
        out = {**core,
               "parity": {"tol": PARITY_TOL, "checks": checks, "all_pass": val_parity_pass},
               "binding_gate": None, "secondary_checks": None, "test_full": None,
               "bootstrap": None, "stratified": None, "test_disjoint": None,
               "test_w4": None, "incumbent_s44_rederived": None,
               "close": {"condition": "seed-discipline violation (twin divergence 0)", "trigger": None,
                         "message": "VOID: twin-vs-seed0 divergence exactly 0 — seed mechanism failed (D9)"},
               "verdict": "VOID_SEED_DISCIPLINE",
               "plan_impact": {"invalidates": None, "confirms": None, "opens": None,
                               "note": "seed-discipline violation per D9 — fix and re-run"},
               "elapsed_s": float(time.time() - t_all)}
        log("Overall VERDICT=VOID_SEED_DISCIPLINE")
        _write_outputs(out)
        return 1

    # ---- C2 precondition to reach the frozen test (D4/D5) ----
    if not heldout_precondition_pass:
        log(f"CLOSE C2: held-out gain {heldout_gain:.4f} <= 0.005 — REJECT at plan time (no frozen test)")
        out = {**core,
               "parity": {"tol": PARITY_TOL, "checks": checks, "all_pass": val_parity_pass},
               "binding_gate": None, "secondary_checks": None, "test_full": None,
               "bootstrap": None, "stratified": None, "test_disjoint": None,
               "test_w4": None, "incumbent_s44_rederived": None,
               "close": {"condition": CLOSE_CONDITION, "trigger": True,
                         "message": "C2: held-out gain <= 0.005 - REJECT at plan time before frozen test"},
               "verdict": "REJECTED",
               "plan_impact": {"invalidates": None,
                               "confirms": "S-44 remains incumbent; cross-channel-attention and "
                                           "seed-diversity directions recorded with their numbers (D5)",
                               "opens": None},
               "elapsed_s": float(time.time() - t_all)}
        log("Overall VERDICT=REJECTED")
        _write_outputs(out)
        print(f"\nwrote {HERE / 'results_s45.json'} (REJECTED, C2) elapsed {time.time() - t_all:.1f}s")
        return 0

    # ---- Frozen test (members refrozen on 11425) — verbatim Bet 3/S-44 ----
    n_test = len(test_series) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_series)

    P_test_cols = []
    for j, (name, factory) in enumerate(CANDIDATES):
        t0 = time.time()
        if name.startswith("patchtst"):
            log(f"  training {name} on full 11425 (frozen test)...")
        if j in UNIVARIATE_1D:
            p = preds_for_full_fit(factory, fit_series, concat_series, test_starts, HORIZON)
        else:
            p = preds_for_full_fit(factory, fit_multi, concat_multi, test_starts, HORIZON)
        P_test_cols.append(p)
        log(f"  {name:24s} test ok ({time.time()-t0:.1f}s)")
    P_test = np.stack(P_test_cols, axis=1)  # (n_test, 6, 720)
    A_test = np.stack([test_series[t:t + HORIZON] for t in range(n_test)])

    disj_local = [int(s) for s in DISJOINT_STARTS]
    P_disj = P_test[disj_local]
    A_disj = np.stack([test_series[s:s + HORIZON] for s in DISJOINT_STARTS])

    # ---- Incumbent S-44 blend re-derivation on test (D6/D7): its 3 members, ITS OWN stack ----
    # The incumbent's test stack = per-horizon ridge no-intercept at alpha=30000 fit on
    # val[0:1080) (the same half-split `stack` convention as the candidate, D4) —
    # `inc_ctrl_stack` is exactly that object; applied to the 11425-refit incumbent members.
    inc_preds_full = inc_ctrl_stack.predict(P_test[:, INCUMBENT_IDX, :])
    inc_mae_full, inc_rmse_full, inc_mae_per, _ = rolling_metrics(inc_preds_full, A_test)
    inc_preds_disj = inc_ctrl_stack.predict(P_disj[:, INCUMBENT_IDX, :])
    inc_mae_disj, inc_rmse_disj, _, _ = rolling_metrics(inc_preds_disj, A_disj)
    inc_w4_mae = float(np.mean(np.abs(inc_preds_disj[3] - A_disj[3])))
    log(f"\nS-44 incumbent re-derived (in-harness, D6/D7): full {inc_mae_full:.6f}/{inc_rmse_full:.6f} "
        f"disjoint {inc_mae_disj:.6f} W4 {inc_w4_mae:.6f}")

    # ---- Candidate metrics: full, disjoint-4, W4 (test stack = the SAME val half-split `stack`) ----
    preds_full = stack.predict(P_test[:, best_idx, :])
    mae_full, rmse_full, mae_per_full, rmse_per_full = rolling_metrics(preds_full, A_test)
    for j, i in enumerate(best_idx):
        m = float(np.mean(np.mean(np.abs(P_test[:, i, :] - A_test), axis=1)))
        log(f"  member {CANDIDATES[i][0]:24s} full {m:.4f}")

    preds_disj = stack.predict(P_disj[:, best_idx, :])
    mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)
    w4_pred = stack.predict(P_disj[3:4, best_idx, :])[0]
    w4_actual = A_disj[3]
    w4_mae = float(np.mean(np.abs(w4_pred - w4_actual)))
    w4_vs_incumbent = w4_mae - inc_w4_mae

    # ---- Bootstrap 95% CI (B=2000, seed 0, resample origins) — candidate vs IN-HARNESS incumbent ----
    bs_mean_s45, bs_lo_s45, bs_hi_s45, bs_B = bootstrap_mean_ci(mae_per_full, seed=0)
    # Incumbent-vs-S-26 paired bootstrap (re-derived for the §5 parity row; the
    # same pairing S-44 recorded: incumbent blend per-origin MAEs vs the
    # in-harness S-26 anchor per-origin MAEs, B=2000, seed 0).
    inc_vs_s26_mean, inc_vs_s26_lo, inc_vs_s26_hi, _ = bootstrap_paired_diff_ci(inc_mae_per, anchor_mae_per, seed=0)
    bs_mean_inc, bs_lo_inc, bs_hi_inc, _ = bootstrap_mean_ci(inc_mae_per, seed=0)
    delta_mean, d_lo, d_hi, _ = bootstrap_paired_diff_ci(mae_per_full, inc_mae_per, seed=0)
    log(f"Bootstrap 95% CI (B={bs_B}): S-45 full [{bs_lo_s45:.4f}, {bs_hi_s45:.4f}] mean {bs_mean_s45:.4f}; "
        f"incumbent [{bs_lo_inc:.4f}, {bs_hi_inc:.4f}] mean {bs_mean_inc:.4f}")
    log(f"Paired delta (S45-incumbent) mean {delta_mean:+.4f} 95% CI [{d_lo:+.4f}, {d_hi:+.4f}] "
        f"({'UPPER BOUND < 0 => promotion-supported' if d_hi < 0 else 'upper bound >= 0 => not decisive'})")

    # ---- Stratified W1-W4 + horizon terciles vs the in-harness incumbent (D5/D7) ----
    strat_disj = []
    for k, s in enumerate(DISJOINT_STARTS):
        seg = mae_per_full[s:s + 720]
        si = inc_mae_per[s:s + 720]
        seg_d = float(np.mean(seg - si))
        strat_disj.append({"window": f"W{k+1}", "start": int(s), "s45_mae": float(np.mean(seg)),
                           "incumbent_mae": float(np.mean(si)), "delta": seg_d})
        log(f"  strat W{k+1} (origin {s:4d}): S-45 {np.mean(seg):.4f}  incumbent {np.mean(si):.4f}  delta {seg_d:+.4f}")
    s45_terr = np.abs(preds_full - A_test)      # (n_test, 720)
    inc_terr = np.abs(inc_preds_full - A_test)
    n_h = HORIZON // 3
    terc = []
    for t, lbl in enumerate(["h1_first240", "h2_mid240", "h3_last240"]):
        sl = slice(t * n_h, (t + 1) * n_h)
        seg = s45_terr[:, sl].mean()
        si = inc_terr[:, sl].mean()
        seg_d = float(seg - si)
        terc.append({"horizon_tercile": lbl, "s45_mae": float(seg),
                     "incumbent_mae": float(si), "delta": seg_d})
        log(f"  horizon {lbl}: S-45 {seg:.4f}  incumbent {si:.4f}  delta {seg_d:+.4f}")
    log(f"\nS-44 incumbent (in-harness): full {inc_mae_full:.4f} / disjoint {inc_mae_disj:.4f} / W4 {inc_w4_mae:.4f}")
    log(f"S-45 best blend: full {mae_full:.4f} / {rmse_full:.4f}  disjoint {mae_disj:.4f}  W4 {w4_mae:.4f}  val_full {val_full:.4f}")

    # ---- FULL PARITY (D6): incumbent frozen-test rows appended ----
    checks += [
        _num_check("incumbent_test_full_mae", s44["test_full"]["mae"], inc_mae_full),
        _num_check("incumbent_test_full_rmse", s44["test_full"]["rmse"], inc_rmse_full),
        _num_check("incumbent_test_disjoint_mae", s44["test_disjoint"]["mae"], inc_mae_disj),
        _num_check("incumbent_test_disjoint_rmse", s44["test_disjoint"]["rmse"], inc_rmse_disj),
        _num_check("incumbent_test_w4_mae", s44["test_w4"]["mae"], inc_w4_mae),
        # Incumbent paired Δ-vs-S-26 CI re-derived in-harness (§5 row): the
        # incumbent blend's per-origin MAEs vs the in-harness S-26 anchor's
        # (anchor_mae_per), B=2000 seed 0 — identical pairing convention to S-44.
        _num_check("incumbent_paired_ci_lower", s44["bootstrap"]["paired_delta"]["ci_95"][0],
                   inc_vs_s26_lo),
        _num_check("incumbent_paired_ci_upper", s44["bootstrap"]["paired_delta"]["ci_95"][1],
                   inc_vs_s26_hi),
        _num_check("incumbent_paired_delta_mean", s44["bootstrap"]["paired_delta"]["mean"],
                   inc_vs_s26_mean),
    ]
    inc_w1_w4 = [r["s44_mae"] for r in b_strat["disjoint_windows"]]
    checks.append(_num_check("incumbent_w1_mae", inc_w1_w4[0], float(np.mean(inc_mae_per[0:720]))))
    checks.append(_num_check("incumbent_w2_mae", inc_w1_w4[1], float(np.mean(inc_mae_per[720:1440]))))
    checks.append(_num_check("incumbent_w3_mae", inc_w1_w4[2], float(np.mean(inc_mae_per[1440:2160]))))
    checks.append(_num_check("incumbent_w4_mae", inc_w1_w4[3], float(np.mean(inc_mae_per[2160:2880]))))
    inc_terc = [r["s44_mae"] for r in b_strat["horizon_terciles"]]
    checks.append(_num_check("incumbent_tercile_h1_mae", inc_terc[0], float(inc_terr[:, :240].mean())))
    checks.append(_num_check("incumbent_tercile_h2_mae", inc_terc[1], float(inc_terr[:, 240:480].mean())))
    checks.append(_num_check("incumbent_tercile_h3_mae", inc_terc[2], float(inc_terr[:, 480:720].mean())))
    all_parity_pass = all(c["pass"] for c in checks)
    log(f"PARITY (D6): {len(checks)} checks vs results_s44.json, all_pass={all_parity_pass} (tol 1e-4)")
    if not all_parity_pass:
        return emit_parity_abort(checks, "test-phase")

    # ---- Binding gate (D2) vs the in-harness incumbent + secondary + close (D5) ----
    g1_threshold = inc_mae_full - G1_MARGIN
    g1 = mae_full <= g1_threshold
    g2 = mae_full < inc_mae_full
    g3 = mae_disj <= inc_mae_disj
    g4 = d_hi < 0.0
    all_binding = g1 and g2 and g3 and g4
    s26_cap_pass = mae_disj <= S26_DISJOINT_CAP

    close_c1 = set(best_idx).issubset(set(range(4)))  # subset-of-S-44-pool (no new member)
    close_c2 = heldout_gain <= 0.005
    close_c3 = d_hi >= 0.0
    close_c4 = not (g1 and g2 and g3)
    close_trigger = close_c1 or close_c2 or close_c3 or close_c4
    verdict = "PROMOTED" if (all_binding and not close_trigger) else "REJECTED"

    log(f"Binding gate (D2) vs in-harness incumbent: G1 full<={g1_threshold:.4f} {g1} ({mae_full:.4f})  "
        f"G2 full<{inc_mae_full:.4f} {g2}  G3 disjoint<={inc_mae_disj:.4f} {g3} ({mae_disj:.4f})  "
        f"G4 paired-CI-upper<0 {g4} ({d_hi:+.4f})  all_binding_pass={all_binding}")
    log(f"Secondary check (non-binding, D2): disjoint<={S26_DISJOINT_CAP} {s26_cap_pass} ({mae_disj:.4f})")
    log(f"Close conditions (D5): C1 subset-of-S44-pool {close_c1}  C2 heldout_gain<=0.005 {close_c2}  "
        f"C3 CI-upper>=0 {close_c3}  C4 any-G1-G3-fails {close_c4}  trigger={close_trigger}")
    # ---- Family-close clause (D5): BOTH new-member singleton vals > 2.90 AND no
    # subset containing a new member beats the incumbent held-out control
    # (held_out_mae) on val[1080:2161) — EXHAUSTIVE over every subset that
    # contains at least one new member (48 of the 64 pool subsets).
    new_singletons = [singleton_val[CANDIDATES[i][0]] for i in NEW_MEMBER_IDX]
    new_member_subsets = [sorted(combo) for r in range(1, N_CAND + 1)
                          for combo in combinations(range(N_CAND), r)
                          if 4 in combo or 5 in combo]
    best_new_subset_fast = min(score_fast(P_val, A_val, sub) for sub in new_member_subsets)
    family_close = (all(v > 2.90 for v in new_singletons)) and (best_new_subset_fast >= held_out_mae)
    if family_close:
        log(f"FAMILY CLOSE (D5): both new-member singleton vals > 2.90 "
            f"({new_singletons[0]:.4f} / {new_singletons[1]:.4f}) AND best new-member-subset fast "
            f"{best_new_subset_fast:.4f} does not beat incumbent control {held_out_mae:.4f} -> "
            f"blend-frontier-expansion family closed under S-20-clean (licensing clauses spent)")
    else:
        log(f"Family close (D5): new-member singleton vals {new_singletons[0]:.4f} / {new_singletons[1]:.4f}, "
            f"best new-member-subset fast {best_new_subset_fast:.4f} vs control {held_out_mae:.4f} -> not closed")

    log(f"Overall VERDICT={verdict}")

    if close_trigger:
        close_message = ("close condition fired - S-44 remains incumbent; cross-channel-attention "
                         "and seed-diversity directions recorded with their numbers (D5)")
        plan_impact = {"invalidates": None,
                       "confirms": "S-44 remains incumbent; cross-channel-attention and "
                                   "seed-diversity directions recorded with their numbers (D5)",
                       "opens": None}
    else:
        close_message = "no close condition fired"
        plan_impact = {"invalidates": "S-44 incumbent status on PROMOTION (S-44 row demoted with "
                                      "dethroned annotation; S-26 drops to third)",
                       "confirms": "on REJECT: S-44 remains incumbent; cross-channel-attention and "
                                   "seed-diversity directions recorded with numbers",
                       "opens": "on PROMOTION: re-anchored blend-incumbent frontier (S-44 P2 turnover applies)"}

    out = {**core,
           "incumbent_s44_rederived": {
               "subset": [CANDIDATES[i][0] for i in INCUMBENT_IDX], "alpha": INCUMBENT_ALPHA,
               "best_fast": inc_best_fast, "val_full": held_out_mae,
               "test_full_mae": inc_mae_full, "test_full_rmse": inc_rmse_full,
               "test_disjoint_mae": inc_mae_disj, "test_w4_mae": inc_w4_mae,
               "w1_w4": [float(np.mean(inc_mae_per[s:s + 720])) for s in DISJOINT_STARTS],
               "horizon_terciles": [float(inc_terr[:, sl].mean()) for sl in
                                    (slice(0, 240), slice(240, 480), slice(480, 720))],
           },
           "parity": {"tol": PARITY_TOL, "checks": checks, "all_pass": all_parity_pass},
           "binding_gate": {
               "full_le_incumbent_minus_005": {"value": mae_full, "threshold": g1_threshold, "pass": bool(g1)},
               "full_lt_incumbent": {"value": mae_full, "incumbent": inc_mae_full, "pass": bool(g2)},
               "disjoint_le_incumbent": {"value": mae_disj, "incumbent": inc_mae_disj, "pass": bool(g3)},
               "paired_ci_upper_lt_0": {"ci_95": [d_lo, d_hi], "upper": d_hi, "pass": bool(g4)},
               "all_binding_pass": bool(all_binding),
           },
           "secondary_checks": {
               "disjoint_le_s26_cap_19696": {"value": mae_disj, "cap": S26_DISJOINT_CAP,
                                              "pass": bool(s26_cap_pass), "binding": False},
           },
           "demoted_diagnostics": {
               "new_member_singleton_vals": {CANDIDATES[i][0]: singleton_val[CANDIDATES[i][0]]
                                             for i in NEW_MEMBER_IDX},
               "train_val_gap": gap_report, "gap_flag": bool(gap_flag),
               "attention_entropy_last": {k: (v[-1] if v else float("nan")) for k, v in ent_report.items()},
               "entropy_collapse": bool(entropy_collapse),
               "twin_vs_seed0_divergence_val": {"mean_abs_delta_pred": twin_div_abs,
                                                 "corr": twin_corr,
                                                 "exact_zero": twin_exact_zero},
               "w1_w4_deltas_vs_incumbent": strat_disj,
               "horizon_terciles": terc,
           },
           "test_full": {"mae": mae_full, "rmse": rmse_full, "n": n_test,
                         "delta_vs_incumbent": mae_full - inc_mae_full},
           "bootstrap": {
               "convention": "resample origins, B=2000, seed 0, percentile 2.5/97.5",
               "s45_full": {"mean": bs_mean_s45, "ci_95": [bs_lo_s45, bs_hi_s45], "B": bs_B},
               "incumbent_full": {"mean": bs_mean_inc, "ci_95": [bs_lo_inc, bs_hi_inc], "B": bs_B},
               "paired_delta": {"mean": delta_mean, "ci_95": [d_lo, d_hi], "B": bs_B,
                                "upper_bound_negative": bool(d_hi < 0)},
           },
           "stratified": {"disjoint_windows": strat_disj, "horizon_terciles": terc},
           "test_disjoint": {"mae": mae_disj, "rmse": rmse_disj},
           "test_w4": {"mae": w4_mae, "incumbent_w4": inc_w4_mae,
                       "delta_vs_incumbent": w4_vs_incumbent, "binding": False},
           "close": {"condition": CLOSE_CONDITION,
                     "c1_subset_of_s44_pool": bool(close_c1), "c2_heldout_gain": bool(close_c2),
                     "c3_ci_upper_ge_0": bool(close_c3), "c4_any_g1_g3_fails": bool(close_c4),
                     "family_close_s20_clean": bool(family_close),
                     "new_member_singleton_vals": {CANDIDATES[i][0]: singleton_val[CANDIDATES[i][0]]
                                                   for i in NEW_MEMBER_IDX},
                     "best_new_member_subset_fast": best_new_subset_fast,
                     "trigger": bool(close_trigger), "message": close_message},
           "verdict": verdict,
           "plan_impact": plan_impact,
           "elapsed_s": float(time.time() - t_all)}
    _write_outputs(out)
    print(f"\nwrote {HERE / 'results_s45.json'} elapsed {time.time() - t_all:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
