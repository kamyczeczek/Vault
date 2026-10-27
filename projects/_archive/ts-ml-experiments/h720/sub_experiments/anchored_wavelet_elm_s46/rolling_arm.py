"""S-46 — Anchored Wavelet → ELM Dictionary → Sparse Readout (h720 ETTh1 H=720).

Implements S46_DESIGN.md (pre-registration, binding). Pool M=6:
  [nlinear_L336_a1, nlinear_L336_a10, patchtst_P24_D32_2L, patchtst_P48_D16_1L,
   wavelet_elm_swt_db4_h200, wavelet_elm_swt_db4_h400]

Stages 0->4 are inside anchored_wavelet_elm.AnchoredWaveletELM.
Harness: S-20-clean tabu-7 (fixed-α 3000, no_improve=5) + per-horizon ridge
no-intercept 11-grid, chronological half-split val[0:1080)/val[1080:2161).
Binding gate BLEND-based vs in-harness S-44 incumbent re-derivation (G1-G4).

Self-contained: defines tabu + ridge head locally (no shared refactor).
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import torch  # needed for PatchTST members' deterministic seed toggling inside patchtst_encoder
from sklearn.linear_model import Ridge

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
# PatchTST members import the Bet 3 encoder verbatim (S-44/S-45 precedent)
sys.path.insert(0, str(HERE.parent / "patchtst_delta_bet3"))

from data import HORIZON, get_protocol_data  # noqa: E402
from methods.neural_models import NLinear  # noqa: E402
from patchtst_encoder import PatchTSTModel  # noqa: E402  (audit)
from anchored_wavelet_elm import AnchoredWaveletELM  # noqa: E402  (sibling member module)

S44_DIR = HERE.parent / "blend_promotion_s44"
S44_RESULTS = S44_DIR / "results_s44.json"
BET3_DIR = HERE.parent / "patchtst_delta_bet3"

HARNESS_COMMAND = "python projects/ts-ml-experiments/h720/sub_experiments/anchored_wavelet_elm_s46/rolling_arm.py"

CANDIDATES = [
    ("nlinear_L336_a1", lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
    ("patchtst_P24_D32_2L", lambda: PatchTSTModel(patch_size=24, D=32, n_layers=2, H=HORIZON)),
    ("patchtst_P48_D16_1L", lambda: PatchTSTModel(patch_size=48, D=16, n_layers=1, H=HORIZON)),
    ("wavelet_elm_swt_db4_h200", lambda: AnchoredWaveletELM(
        input_length=336, wavelet="db4", levels=3, transform="swt",
        mode="periodization", threshold="universal", hidden=200, activation="tanh", seed=42)),
    ("wavelet_elm_swt_db4_h400", lambda: AnchoredWaveletELM(
        input_length=336, wavelet="db4", levels=3, transform="swt",
        mode="periodization", threshold="universal", hidden=400, activation="tanh", seed=42)),
]
S44_DIR = HERE.parent / "blend_promotion_s44"
S44_RESULTS = S44_DIR / "results_s44.json"
BET3_DIR = HERE.parent / "patchtst_delta_bet3"

TRAIN_END = 8545
DISJOINT_STARTS = (0, 720, 1440, 2160)
SEARCH_ALPHA = 3000.0
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]
PARITY_TOL = 1e-4

# G1-G4 thresholds computed from the in-harness S-44 incumbent (D7),
# but also check hard-coded parity values to detect harness drift.
# Close condition text (schema)
CLOSE_CONDITION = (
    "subset-of-S44-pool OR heldout_gain<=0.005 OR paired_ci_upper>=0 "
    "OR any G1-G3 fails (+ family-close when both wavelet singletons >2.90 "
    "and no wavelet-subset beats the held-out control)"
)

N_CAND = len(CANDIDATES)
# Indices that count as "new" vs the S-44 pool (first 4 are S-44)
S44_IDX = [0, 1, 2, 3]
NEW_IDX = [4, 5]
PT_IDX = [2, 3]  # patchtst members (for audit, not gating)


# ------------------------------------------------------------------
# Stack machinery (per-horizon ridge no-intercept) — verbatim S-44/Bet3
# ------------------------------------------------------------------
def fit_stack_map(P, A, alpha, fit_intercept=False):
    n, m, h = P.shape
    coef = np.empty((m, h))
    for k in range(h):
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
    return _Map(coef)


class _Map:
    def __init__(self, coef):
        self.coef_ = coef
        self.inter_ = np.zeros(coef.shape[1])

    def predict(self, Pt):
        return np.einsum("mh,nmh->nh", self.coef_, Pt) + self.inter_[None, :]


def score_fast(P_val, A_val, idx, alpha=SEARCH_ALPHA):
    if len(idx) == 0:
        return float("inf")
    n2 = P_val.shape[0] // 2
    Psub = P_val[:, idx, :]
    r = fit_stack_map(Psub[:n2], A_val[:n2], alpha)
    return float(np.mean(np.mean(np.abs(r.predict(Psub[n2:]) - A_val[n2:]), axis=1)))


def score_full(P_val, A_val, idx):
    if len(idx) == 0:
        return float("inf"), None
    n2 = P_val.shape[0] // 2
    best = float("inf")
    best_a = None
    for a in ALPHAS:
        s = score_fast(P_val, A_val, idx, alpha=a)
        # fast score at fixed alpha vs full scan — follow S-44 convention
        # score_full does a proper per-alpha fit on the half-split
        Psub = P_val[:, idx, :]
        r = fit_stack_map(Psub[:n2], A_val[:n2], a)
        sc = float(np.mean(np.mean(np.abs(r.predict(Psub[n2:]) - A_val[n2:]), axis=1)))
        if sc < best:
            best = sc
            best_a = a
    return best, best_a


def preds_for_train_fit(factory, train_series, full_series, starts, H):
    m = factory()
    m.fit(train_series, horizon=H)
    hist = m.history_
    out = []
    for s in starts:
        m.history_ = full_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_ = hist
    return np.asarray(out), m


def preds_for_full_fit(factory, full_series, concat_series, starts, H):
    m = factory()
    m.fit(full_series, horizon=H)
    hist = m.history_
    out = []
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
    rng = np.random.default_rng(seed)
    n = len(per_origin_mae)
    boot = [float(np.mean(rng.choice(per_origin_mae, size=n, replace=True))) for _ in range(B)]
    return float(np.mean(per_origin_mae)), float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)), B


def bootstrap_paired_diff_ci(d_new, d_inc, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    diff = d_new - d_inc
    n = len(diff)
    boot = [float(np.mean(rng.choice(diff, size=n, replace=True))) for _ in range(B)]
    return float(np.mean(diff)), float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)), B


def _num_check(quantity, expected_v, got_v, tol=PARITY_TOL):
    b, s = float(expected_v), float(got_v)
    d = abs(b - s)
    return {"quantity": quantity, "s44": b, "s46": s, "abs_diff": d, "pass": bool(d <= tol)}


def _exact_check(quantity, expected_v, got_v):
    if isinstance(expected_v, (list, tuple)) or isinstance(got_v, (list, tuple)):
        b = list(expected_v) if isinstance(expected_v, (list, tuple)) else expected_v
        s = list(got_v) if isinstance(got_v, (list, tuple)) else got_v
        d = 0.0 if b == s else 1.0
        return {"quantity": quantity, "s44": b, "s46": s, "abs_diff": d, "pass": bool(d == 0.0)}
    b, s = expected_v, got_v
    d = 0.0 if b == s else 1.0
    return {"quantity": quantity, "s44": b, "s46": s, "abs_diff": d, "pass": bool(d == 0.0)}


def _list_num_check(quantity, expected_list, got_list, tol=PARITY_TOL):
    b = [float(x) for x in expected_list]
    s = [float(x) for x in got_list]
    if len(b) != len(s):
        return {"quantity": quantity, "s44": b, "s46": s, "abs_diff": float("inf"), "pass": False}
    d = max(abs(x - y) for x, y in zip(b, s)) if b else 0.0
    return {"quantity": quantity, "s44": b, "s46": s, "abs_diff": float(d), "pass": bool(d <= tol)}


def main(argv=None) -> int:
    t_all = time.time()
    log_lines: list[str] = []

    def log(msg: str):
        print(msg)
        log_lines.append(msg)

    def _write_outputs(out):
        with open(HERE / "results_s46.json", "w") as f:
            json.dump(out, f, indent=2)
        with open(HERE / "harness.log", "w") as f:
            f.write("\n".join(log_lines) + "\n")

    # Determinism: numpy seed 0 for harness-level ops; torch seed 0 for PatchTST
    # (AnchoredWaveletELM uses its own seed=42 internally).
    torch.manual_seed(0)
    np.random.seed(0)
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except Exception:
        pass

    if not S44_RESULTS.exists():
        raise RuntimeError(f"S-44 ground truth missing: {S44_RESULTS} — D8 parity requires it")
    with open(S44_RESULTS) as f:
        s44 = json.load(f)

    # S-44 ground truth fields (parity expected values)
    # New gate is vs S-44 incumbent; old S-26 values are kept for secondary checks.
    s44_test_full_mae = float(s44["test_full"]["mae"])
    s44_test_full_rmse = float(s44["test_full"]["rmse"])
    s44_disjoint = float(s44["test_disjoint"]["mae"])
    s44_w4 = float(s44["test_w4"]["mae"])
    s44_val_full = float(s44["val_full"])
    s44_best_fast = float(s44["best_fast"])

    log("S-46 anchored wavelet → ELM dictionary → sparse readout (S46_DESIGN.md, binding).")
    log("Stages 0/4: NLinear-style per-origin last-value anchor (level-free deltas).")
    log("Stage 1: SWT db4 J=3 periodization + VisuShrink soft threshold per detail band, pooled F features.")
    log("Stage 2: fixed random tanh ELM (seed 42) h200/h400; Stage 3: per-horizon Lasso (no-intercept).")
    log(f"Pool M=6: {[n for n,_ in CANDIDATES]} ;  S-44 incumbent blend target  {s44_test_full_mae:.4f}/{s44_disjoint:.4f}")
    log(f"S-44 ground truth: {S44_RESULTS}")
    log(f"PatchTST encoder audit: {BET3_DIR / 'patchtst_encoder.py'} (architecture-identical import)")
    try:
        import pywt as _pywt
        import sklearn as _skl
        log(f"Library versions: pywt {_pywt.__version__}  sklearn {_skl.__version__}  torch {torch.__version__}")
    except Exception as e:
        log(f"Version probe: {e}")

    pd = get_protocol_data()
    fit_series, concat_series, test_series = pd.rolling_views()
    train_series = fit_series[:TRAIN_END]
    val_series = fit_series[TRAIN_END:]
    n_val = len(val_series) - HORIZON + 1
    assert n_val == 2161, n_val
    assert len(train_series) == 8545 and len(fit_series) == 11425
    val_starts = np.arange(n_val) + TRAIN_END

    # ---- Collect P_val for all 6 candidates (members frozen on 8545) ----
    log(f"\nCollecting P_val for {N_CAND} candidates (val {n_val} origins, members frozen on {TRAIN_END})...")
    P_val_cols = []
    fitted_models = {}  # name -> fitted instance (for diagnostics)
    for name, factory in CANDIDATES:
        t0 = time.time()
        if name.startswith("patchtst"):
            log(f"  training {name} on train 8545 (small encoder, minutes)...")
        elif name.startswith("wavelet_elm"):
            log(f"  training {name} on train 8545 (SWT → ELM → Lasso over {HORIZON} horizons)...")
        p, m = preds_for_train_fit(factory, train_series, fit_series, val_starts, HORIZON)
        P_val_cols.append(p)
        fitted_models[name] = m
        log(f"  {name:30s} ok {p.shape} ({time.time()-t0:.1f}s)")
    P_val = np.stack(P_val_cols, axis=1)  # (n_val, 6, 720)
    A_val = np.stack([val_series[t:t + HORIZON] for t in range(n_val)])

    # singleton val per candidate
    singleton_val = {}
    for j, (name, _) in enumerate(CANDIDATES):
        mae = float(np.mean(np.mean(np.abs(P_val[:, j, :] - A_val), axis=1)))
        singleton_val[name] = mae
        log(f"  singleton {name:30s} val {mae:.4f}")
    # Wavelet-specific singleton subset
    wavelet_singleton_vals = {n: singleton_val[n] for n in [CANDIDATES[i][0] for i in NEW_IDX]}
    best_wavelet_val = min(wavelet_singleton_vals.values()) if wavelet_singleton_vals else float("inf")

    # ---- Held-out control: S-44 incumbent 3-member half-split, re-derived in-harness ----
    # The control is the S-44 blend's per-horizon ridge no-intercept α=30000
    # fitted on val[0:1080) and scored on val[1080:2161) — equals s44["val_full"].
    n2 = n_val // 2  # 1080
    # Re-derive via the S-44 subset indices within the M=6 pool (0,1,2 map to same factories)
    s44_idx_in_m6 = [0, 1, 2]  # nlinear a1/a10 + patchtst P24
    ctrl_P = P_val[:, s44_idx_in_m6, :]
    # The incumbent's frozen best_alpha is 30000; fit that alpha on the half-split
    # (val_full parity convention is half-split, see S-44 harness lines 454-458).
    import pywt as _pywt_probe  # noqa: F401 (used in log above)
    s44_best_alpha = 30000.0
    ctrl_stack = fit_stack_map(ctrl_P[:n2], A_val[:n2], s44_best_alpha)
    held_out_control_mae = float(np.mean(np.mean(np.abs(ctrl_stack.predict(ctrl_P[n2:]) - A_val[n2:]), axis=1)))
    # Also compute the search-alpha (3000) variant for log reference
    ctrl_fast = score_fast(P_val, A_val, s44_idx_in_m6, alpha=SEARCH_ALPHA)
    log(f"Held-out S-44 control (3-member, half-split alpha 30000) MAE val[1080:2161) = {held_out_control_mae:.4f} "
        f"(fast@3000 {ctrl_fast:.4f}; parity s44 val_full {s44_val_full:.4f})")

    # ---- Tabu-7 search over M=6 (fixed-α fast 3000, aspiration, no_improve=5) ----
    single_scores = [score_fast(P_val, A_val, [j]) for j in range(N_CAND)]
    cur_idx = [int(np.argmin(single_scores))]
    cur_score = single_scores[cur_idx[0]]
    best_idx = list(cur_idx)
    best_score = cur_score
    log(f"\ninit singleton {[CANDIDATES[i][0] for i in cur_idx]} fast {cur_score:.4f}")

    tabu: set[tuple] = set()
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
        seen: set[tuple] = set()
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
    # val_full: half-split at best_alpha (parity convention)
    stack = fit_stack_map(P_val[:n2, best_idx, :], A_val[:n2], best_alpha if best_alpha is not None else SEARCH_ALPHA)
    val_full = float(np.mean(np.mean(np.abs(stack.predict(P_val[n2:, best_idx, :]) - A_val[n2:]), axis=1)))
    log(f"refit half-split val MAE {val_full:.4f} alpha {best_alpha}")

    # ---- Held-out precondition (must beat control by >0.005 to reach frozen test as PROMOTION-candidate) ----
    heldout_gain = held_out_control_mae - best_score
    heldout_precondition_pass = heldout_gain > 0.005
    log(f"\nHeld-out precondition: control {held_out_control_mae:.4f}  best_subset fast {best_score:.4f}  gain {heldout_gain:+.4f}  "
        f"{'PASS' if heldout_precondition_pass else 'FAIL (<=0.005)'}")

    # ---- Wavelet diagnostics (S46 demoted) ----
    wavelet_feature_dim = None
    lasso_alpha_selected = {}
    lasso_nnz_mean = {}
    lasso_uses_elastic = {}
    for name in [CANDIDATES[i][0] for i in NEW_IDX]:
        m = fitted_models.get(name)
        if m is not None and hasattr(m, "feature_dim_"):
            wavelet_feature_dim = int(getattr(m, "feature_dim_", wavelet_feature_dim or 0))
            lasso_alpha_selected[name] = float(getattr(m, "lasso_alpha_selected_", float("nan")))
            lasso_nnz_mean[name] = float(getattr(m, "lasso_nnz_mean_", float("nan")))
            lasso_uses_elastic[name] = bool(getattr(m, "uses_elastic_", False))
            log(f"  WAVELET AUDIT {name}: F={getattr(m,'feature_dim_', '?')}  lasso_alpha* {getattr(m,'lasso_alpha_selected_', '?')}  "
                f"nnz_mean {getattr(m,'lasso_nnz_mean_', '?'):.1f}  elastic={getattr(m,'uses_elastic_', False)}")

    # ---- Core artifact (val-phase-complete) ----
    core = {
        "slice": "S-46-anchored-wavelet-elm",
        "harness_command": HARNESS_COMMAND,
        "device": f"cpu (torch {torch.__version__})",
        "protocol": "S-20-clean anchored-wavelet-ELM-sparse expansion of the S-44 incumbent blend; "
                    "binding gate BLEND-based vs the in-harness S-44 incumbent re-derivation (S-43 P1 / S-44 P2); "
                    "parity block per S-44 P1",
        "pool": [n for n, _ in CANDIDATES],
        "new_members": {
            "wavelet_elm_swt_db4_h200": {"transform": "SWT db4 J=3 periodization, VisuShrink soft threshold per subband, pooled F features",
                                         "hidden": 200, "activation": "tanh", "seed": 42},
            "wavelet_elm_swt_db4_h400": {"transform": "SWT db4 J=3 periodization, VisuShrink soft threshold per subband, pooled F features",
                                         "hidden": 400, "activation": "tanh", "seed": 42},
        },
        "params": {"L": 336, "J": 3, "wavelet": "db4", "mode": "periodization", "threshold": "universal",
                   "H": HORIZON, "lasso_alphas": [1e-4, 5e-4, 1e-3, 5e-3, 1e-2],
                   "H_hidden": [200, 400], "seed": 42},
        "singleton_val": singleton_val,
        "wavelet_diagnostics": {"feature_dim": wavelet_feature_dim,
                                "lasso_alpha_selected": lasso_alpha_selected,
                                "lasso_nnz_mean": lasso_nnz_mean,
                                "lasso_uses_elastic": lasso_uses_elastic},
        "incumbent_s44_rederived": {
            "subset": [CANDIDATES[i][0] for i in s44_idx_in_m6],
            "alpha": s44_best_alpha,
            "best_fast": ctrl_fast,
            "val_full": held_out_control_mae,
            "val_full_expected": s44_val_full,
            "val_full_abs_diff": abs(held_out_control_mae - s44_val_full),
            "val_full_pass": bool(abs(held_out_control_mae - s44_val_full) <= PARITY_TOL),
        },
        "s44_anchor": {"mae": s44_test_full_mae, "rmse": s44_test_full_rmse,
                       "disjoint": s44_disjoint, "w4": s44_w4},
        "held_out_control": {"type": "S-44 incumbent 3-member half-split alpha=30000",
                             "mae_val_heldout": held_out_control_mae, "alpha": s44_best_alpha},
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
        log(f"\nPARITY FAILURE (S-44 P1, {stage}): {len(fails)}/{len(checks)} checks failed — harness bug; no verdict emitted:")
        for c in fails:
            log(f"  FAIL {c['quantity']}: s44={c['s44']!r} s46={c['s46']!r} abs_diff={c['abs_diff']!r}")
        out = {**core,
               "parity": {"tol": PARITY_TOL, "checks": checks, "all_pass": False},
               "binding_gate": None, "test_full": None, "bootstrap": None, "stratified": None,
               "test_disjoint": None, "test_w4": None,
               "close": {"condition": CLOSE_CONDITION, "trigger": None,
                         "message": "parity failure — harness bug; no verdict emitted"},
               "verdict": "ABORT_PARITY",
               "plan_impact": {"invalidates": None, "confirms": None, "opens": None,
                               "note": "harness bug per S-44 P1 — fix and re-run; results_s44.json is ground truth"},
               "elapsed_s": float(time.time() - t_all)}
        log(f"Overall VERDICT=ABORT_PARITY ({stage} parity failure)")
        _write_outputs(out)
        print(f"\nwrote {HERE / 'results_s46.json'} (ABORT_PARITY) elapsed {time.time() - t_all:.1f}s")
        return 1

    # ---- VAL-PHASE PARITY (S-44 P1): rows computable before frozen test ----
    checks: list[dict] = []
    # Re-derive S-44 singleton vals for parity (first 4 candidates share factories with S-44)
    for name in [CANDIDATES[i][0] for i in [0, 1, 2, 3]]:
        if name in s44.get("singleton_val", {}):
            checks.append(_num_check(f"singleton_val_{name}", s44["singleton_val"][name], singleton_val[name]))
    checks.append(_num_check("incumbent_val_full_half_split", s44_val_full, held_out_control_mae))
    # Also check S-44-reported val_full mean if present
    # Best-subset parity is not expected to match (M=6 vs M=4), so only the incumbent
    # half-split and the 4 shared singletons are parity-checked at val phase.
    val_parity_pass = all(c["pass"] for c in checks)
    log(f"VAL-PHASE PARITY (S-44 P1): {len(checks)} checks vs S-44, all_pass={val_parity_pass} (tol 1e-4)")
    if not val_parity_pass:
        return emit_parity_abort(checks, "val-phase")

    # ---- Held-out precondition: if fail, still do frozen test as diagnostic but verdict is already REJECT ----
    # (We proceed to frozen test regardless for the artifact; verdict branch handles C2.)

    # ---- Frozen test (members refrozen on 11425) ----
    n_test = len(test_series) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_series)

    P_test_cols = []
    import pickle, hashlib
    cache_dir = HERE / ".cache_test"
    cache_dir.mkdir(exist_ok=True)
    for name, factory in CANDIDATES:
        # Wavelet ELM test preds can be recomputed quickly (vectorized)
        if name.startswith("wavelet_elm"):
            t0 = time.time()
            log(f"  training {name} on full 11425 (frozen test, SWT→ELM→Ridge)...")
            p = preds_for_full_fit(factory, fit_series, concat_series, test_starts, HORIZON)
            P_test_cols.append(p)
            log(f"  {name:30s} test ok ({time.time()-t0:.1f}s)")
            continue
        cpath = cache_dir / f"P_test_{name}.npz"
        if cpath.exists():
            try:
                p = __import__('numpy').load(cpath)['P']
                # verify shape
                assert p.shape == (len(test_starts), HORIZON)
                P_test_cols.append(p)
                log(f"  {name:30s} test CACHED {p.shape}")
                continue
            except Exception as e:
                log(f"  {name} cache miss: {e}")
        t0 = time.time()
        if name.startswith("patchtst"):
            log(f"  training {name} on full 11425 (frozen test) [will cache]...")
        p = preds_for_full_fit(factory, fit_series, concat_series, test_starts, HORIZON)
        try:
            __import__('numpy').savez_compressed(cpath, P=p)
            log(f"  {name:30s} test ok + cached ({time.time()-t0:.1f}s) -> {cpath}")
        except Exception as e:
            log(f"  {name:30s} test ok ({time.time()-t0:.1f}s) cache fail {e}")
        P_test_cols.append(p)
    P_test = np.stack(P_test_cols, axis=1)  # (n_test, 6, 720)
    A_test = np.stack([test_series[t:t + HORIZON] for t in range(n_test)])

    disj_local = [int(s) for s in DISJOINT_STARTS]
    P_disj = P_test[disj_local]
    A_disj = np.stack([test_series[s:s + HORIZON] for s in DISJOINT_STARTS])

    # Metrics: full, disjoint-4, W4 — test stack = SAME val half-split `stack`
    preds_full = stack.predict(P_test[:, best_idx, :])
    mae_full, rmse_full, mae_per_full, rmse_per_full = rolling_metrics(preds_full, A_test)
    for j, i in enumerate(best_idx):
        m = float(np.mean(np.mean(np.abs(P_test[:, i, :] - A_test), axis=1)))
        log(f"  member {CANDIDATES[i][0]:30s} full {m:.4f}")

    preds_disj = stack.predict(P_disj[:, best_idx, :])
    mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)
    w4_pred = stack.predict(P_disj[3:4, best_idx, :])[0]
    w4_actual = A_disj[3]
    w4_mae = float(np.mean(np.abs(w4_pred - w4_actual)))

    # In-harness S-44 incumbent test metrics (same 11425 fit, same test origins) for deltas
    inc_P_test = P_test[:, s44_idx_in_m6, :]
    inc_P_disj = P_disj[:, s44_idx_in_m6, :]
    inc_stack = fit_stack_map(ctrl_P[:n2], A_val[:n2], s44_best_alpha)  # same half-split stack
    inc_preds_full = inc_stack.predict(inc_P_test)
    inc_mae_full, inc_rmse_full, inc_mae_per, _ = rolling_metrics(inc_preds_full, A_test)
    inc_preds_disj = inc_stack.predict(inc_P_disj)
    inc_mae_disj, _, _, _ = rolling_metrics(inc_preds_disj, A_disj)
    inc_w4_mae = float(np.mean(np.abs(inc_preds_disj[3] - A_disj[3])))

    log(f"\nIn-harness S-44 incumbent (re-derived): full {inc_mae_full:.4f}/{inc_rmse_full:.4f}  disjoint {inc_mae_disj:.4f}  W4 {inc_w4_mae:.4f}")
    log(f"S-46 blend best full {mae_full:.4f}/{rmse_full:.4f}  disjoint {mae_disj:.4f}  W4 {w4_mae:.4f}  val_full {val_full:.4f}")

    # Bootstrap 95% CI — resample origins, seeded (S-44 convention)
    bs_mean_s46, bs_lo_s46, bs_hi_s46, bs_B = bootstrap_mean_ci(mae_per_full, seed=0)
    bs_mean_inc, bs_lo_inc, bs_hi_inc, _ = bootstrap_mean_ci(inc_mae_per, seed=0)
    delta_mean, d_lo, d_hi, _ = bootstrap_paired_diff_ci(mae_per_full, inc_mae_per, seed=0)
    log(f"Bootstrap 95% CI (B={bs_B}): S-46 full [{bs_lo_s46:.4f}, {bs_hi_s46:.4f}] mean {bs_mean_s46:.4f}; "
        f"S-44 re-derived [{bs_lo_inc:.4f}, {bs_hi_inc:.4f}] mean {bs_mean_inc:.4f}")
    log(f"Paired delta (S46 - S44 re-derived) mean {delta_mean:+.4f} 95% CI [{d_lo:+.4f}, {d_hi:+.4f}] "
        f"({'UPPER < 0 => promotion-supported' if d_hi < 0 else 'upper >= 0 => not decisive'})")

    # Stratified W1-W4 + horizon terciles — vs in-harness S-44 incumbent
    strat_disj = []
    for k, s in enumerate(DISJOINT_STARTS):
        seg = mae_per_full[s:s + 720]
        sa = inc_mae_per[s:s + 720]
        seg_d = float(np.mean(seg - sa))
        strat_disj.append({"window": f"W{k+1}", "start": int(s), "s46_mae": float(np.mean(seg)),
                           "s44_mae": float(np.mean(sa)), "delta": seg_d})
        log(f"  strat W{k+1} (origin {s:4d}): S-46 {np.mean(seg):.4f}  S-44 {np.mean(sa):.4f}  delta {seg_d:+.4f}")
    s46_terr = np.abs(preds_full - A_test)
    s44_terr = np.abs(inc_preds_full - A_test)
    n_h = HORIZON // 3
    terc = []
    for t, lbl in enumerate(["h1_first240", "h2_mid240", "h3_last240"]):
        sl = slice(t * n_h, (t + 1) * n_h)
        seg = s46_terr[:, sl].mean()
        sa = s44_terr[:, sl].mean()
        seg_d = float(seg - sa)
        terc.append({"horizon_tercile": lbl, "s46_mae": float(seg), "s44_mae": float(sa), "delta": seg_d})
        log(f"  horizon {lbl}: S-46 {seg:.4f}  S-44 {sa:.4f}  delta {seg_d:+.4f}")

    # ---- FULL PARITY: frozen-test incumbent rows appended ----
    checks += [
        _num_check("incumbent_test_full_mae", s44_test_full_mae, inc_mae_full),
        _num_check("incumbent_test_full_rmse", s44_test_full_rmse, inc_rmse_full),
        _num_check("incumbent_test_disjoint_mae", s44_disjoint, inc_mae_disj),
        _num_check("incumbent_test_w4_mae", s44_w4, inc_w4_mae),
    ]
    all_parity_pass = all(c["pass"] for c in checks)
    log(f"PARITY (S-44 P1): {len(checks)} checks vs S-44, all_pass={all_parity_pass} (tol 1e-4)")
    if not all_parity_pass:
        return emit_parity_abort(checks, "test-phase")

    # ---- Binding gate (D2 §4) — vs in-harness S-44 re-derived incumbent ----
    g1 = mae_full <= inc_mae_full - 0.0050  # <= incumbent - 0.0050
    g2 = mae_full < inc_mae_full
    g3 = mae_disj <= inc_mae_disj
    g4 = d_hi < 0.0
    all_binding = bool(g1 and g2 and g3 and g4)

    # Close conditions
    c1 = not any(i in NEW_IDX for i in best_idx)  # no new member selected
    c2 = heldout_gain <= 0.005
    c3 = d_hi >= 0.0
    c4 = not (g1 and g2 and g3)
    # Family-close: BOTH new singletons > 2.90 AND no wavelet-subset beats held-out control
    both_wavelet_bad = all(singleton_val[CANDIDATES[i][0]] > 2.90 for i in NEW_IDX)
    # Does any singleton wavelet already beat control? If not, check best wavelet-inclusive
    # subset fast score — we approximate by the best wavelet singleton; if that fails,
    # no larger wavelet subset can beat control without being selected (conservative).
    best_wavelet_singleton_fast = min(score_fast(P_val, A_val, [i]) for i in NEW_IDX)
    no_wavelet_beats_control = best_wavelet_singleton_fast >= held_out_control_mae
    family_close = bool(both_wavelet_bad and no_wavelet_beats_control)

    close_trigger = bool(c1 or c2 or c3 or c4)
    verdict = "PROMOTED" if (all_binding and not close_trigger) else "REJECTED"

    log(f"\nBinding gate (vs in-harness S-44 {inc_mae_full:.4f}/{inc_mae_disj:.4f}): "
        f"G1 full<={inc_mae_full - 0.0050:.4f} {g1} ({mae_full:.4f})  "
        f"G2 full<{inc_mae_full:.4f} {g2}  G3 disjoint<={inc_mae_disj:.4f} {g3} ({mae_disj:.4f})  "
        f"G4 paired-CI-upper<0 {g4} ({d_hi:+.4f})  all_binding={all_binding}")
    log(f"Close: C1 no-wavelet {c1}  C2 heldout_gain<=0.005 {c2} ({heldout_gain:+.4f})  "
        f"C3 CI-upper>=0 {c3}  C4 any-G1-G3-fails {c4}  trigger={close_trigger}")
    log(f"Family-close S-20-clean: both_wavelet>2.90 {both_wavelet_bad}  "
        f"no_wavelet_beats_control({best_wavelet_singleton_fast:.4f}>={held_out_control_mae:.4f})={no_wavelet_beats_control}  "
        f"family_close={family_close}")
    log(f"Overall VERDICT={verdict}")

    if close_trigger:
        if family_close:
            close_message = ("close condition fired and family-close (S-20-clean): "
                             "anchored wavelets + fixed ELM dictionary + sparse per-horizon selection "
                             "add no orthogonal signal beyond the L336 linear map and the S-44 attention blend "
                             "at this horizon and data budget — no further wavelet→ELM→sparse on OT alone without exogenous channels.")
        else:
            close_message = "close condition fired — S-44 remains incumbent (diagnostics below)"
        plan_impact = {"invalidates": None,
                       "confirms": "S-44 remains incumbent; anchored-wavelet-ELM-sparse diagnostics recorded",
                       "opens": None}
        if family_close:
            plan_impact["family_close"] = "anchored-wavelet-ELM-sparse family closed under S-20-clean"
    else:
        close_message = "no close condition fired"
        plan_impact = {"invalidates": "S-44 incumbent status (moves to second place) on PROMOTION",
                       "confirms": "anchored-wavelet-ELM-sparse family: this representation carries orthogonal signal",
                       "opens": "re-anchored blend-incumbent frontier (S-44 P2 turnover applies)"}

    w4_vs_s44 = float(w4_mae - inc_w4_mae)

    out = {**core,
           "parity": {"tol": PARITY_TOL, "checks": checks, "all_pass": all_parity_pass},
           "binding_gate": {
               "full_le_incumbent_minus_005": {"value": mae_full, "threshold": inc_mae_full - 0.0050, "incumbent": inc_mae_full, "pass": bool(g1)},
               "full_lt_incumbent": {"value": mae_full, "incumbent": inc_mae_full, "pass": bool(g2)},
               "disjoint_le_incumbent": {"value": mae_disj, "incumbent": inc_mae_disj, "pass": bool(g3)},
               "paired_ci_upper_lt_0": {"ci_95": [d_lo, d_hi], "upper": d_hi, "pass": bool(g4)},
               "all_binding_pass": bool(all_binding),
           },
           "secondary_checks": {"disjoint_le_s26_cap_19696": {"value": mae_disj, "cap": 1.9696, "pass": bool(mae_disj <= 1.9696), "binding": False}},
           "demoted_diagnostics": {
               "new_member_singleton_vals": wavelet_singleton_vals,
               "best_wavelet_val": best_wavelet_val,
               "wavelet_feature_dim": wavelet_feature_dim,
               "lasso_alpha_selected": lasso_alpha_selected,
               "lasso_nnz_mean": lasso_nnz_mean,
               "w1_w4_deltas": [{"window": r["window"], "s46_mae": r["s46_mae"],
                                 "s44_mae": r["s44_mae"], "delta": r["delta"]} for r in strat_disj],
               "horizon_terciles": terc,
           },
           "test_full": {"mae": mae_full, "rmse": rmse_full, "n": n_test, "delta_vs_s44": mae_full - inc_mae_full},
           "bootstrap": {
               "convention": "resample origins, B=2000, seed 0, percentile 2.5/97.5",
               "s46_full": {"mean": bs_mean_s46, "ci_95": [bs_lo_s46, bs_hi_s46], "B": bs_B},
               "s44_full": {"mean": bs_mean_inc, "ci_95": [bs_lo_inc, bs_hi_inc], "B": bs_B},
               "paired_delta": {"mean": delta_mean, "ci_95": [d_lo, d_hi], "B": bs_B, "upper_bound_negative": bool(d_hi < 0)},
           },
           "stratified": {"disjoint_windows": strat_disj, "horizon_terciles": terc},
           "test_disjoint": {"mae": mae_disj, "rmse": rmse_disj},
           "test_w4": {"mae": w4_mae, "s44_incumbent_w4": inc_w4_mae, "w4_delta_vs_s44": w4_vs_s44, "binding": False},
           "close": {"condition": CLOSE_CONDITION,
                     "c1_no_wavelet": bool(c1), "c2_heldout_gain": bool(c2),
                     "c3_ci_upper_ge_0": bool(c3), "c4_any_g1_g3_fails": bool(c4),
                     "both_wavelet_gt_290": bool(both_wavelet_bad),
                     "no_wavelet_beats_control": bool(no_wavelet_beats_control),
                     "family_close_s20_clean": bool(family_close),
                     "trigger": bool(close_trigger), "message": close_message},
           "verdict": verdict,
           "plan_impact": plan_impact,
           "elapsed_s": float(time.time() - t_all)}
    _write_outputs(out)
    print(f"\nwrote {HERE / 'results_s46.json'} elapsed {time.time() - t_all:.1f}s  VERDICT={verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
