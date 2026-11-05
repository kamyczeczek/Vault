"""S-27 — Horizon-band alpha ablation over S-26 2-member incumbent.

Incumbent: [NLinear L336 a=1 + NLinear L336 a=10], alpha=10000, MAE 1.9909.
This slice: split H=720 into 3 bands (0-239/240-479/480-719), per-band alpha
selection on held-out n2=1081 (S-20-clean), refit-all-val, frozen test.

Map-level only — no _lag_dataset change.
Graph hotspot _lag_dataset @ base.py:197 d27 — this file touches only the
stack map banding (fit_stack_map_banded/score_banded), no feature/lag path.
See MONITORING/reflection/2026-09-11_graph-aware-overall-reflection.next_direction.md Rank 1.

Protocol guards (S-20-clean):
- preds_for_train_fit: fit on train 8545, score on val 2161  (leakage-free val)
- preds_for_full_fit:  fit on full  11425, score on test 2161 (leakage-free test)
- Same ALPHAS 11-grid, no-intercept per-horizon ridge, chronological n2=1080/1081 split
- Full 2161 is selector; disjoint-4 diagnostic only (scar [9] P3 S-16c)

Refs: sub_experiments/greedy_linear_mixture_s26/rolling_arm.py:52-82 fit_stack_map/score_full
      sub_experiments/greedy_linear_mixture_s26/rolling_arm.py:84-118 collect_val/collect_test
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear

TRAIN_END = 8545
ALPHAS = [0.1,1.0,3.0,10.0,30.0,100.0,300.0,1000.0,3000.0,10000.0,30000.0]
DISJOINT_STARTS = (0,720,1440,2160)
BANDS = [(0,240),(240,480),(480,720)]  # half-open [lo,hi)
INCUMBENT_MAE = 1.9909

# Fixed S-26 incumbent members
CANDIDATES = [
    ("nlinear_L336_a1",  lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
]
INC_IDX = [0,1]

def fit_stack_map(P, A, alpha, fit_intercept=False):
    n,m,h=P.shape; coef=np.empty((m,h)); inter=np.zeros(h)
    for k in range(h):
        r=Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:,:,k], A[:,k]); coef[:,k]=r.coef_
    class _Map:
        def predict(self, Pt): return np.einsum("mh,nmh->nh", coef, Pt) + inter[None,:]
    _Map.coef_=coef; _Map.inter_=inter
    return _Map()

def fit_stack_map_banded(P, A, alphas_per_band):
    """Per-horizon ridge with banded alpha: alphas_per_band length 3, one per BANDS."""
    n,m,h=P.shape; coef=np.empty((m,h)); inter=np.zeros(h)
    for b,(lo,hi) in enumerate(BANDS):
        a = alphas_per_band[b]
        for k in range(lo, hi):
            r=Ridge(alpha=a, fit_intercept=False).fit(P[:,:,k], A[:,k]); coef[:,k]=r.coef_
    class _Map:
        def predict(self, Pt): return np.einsum("mh,nmh->nh", coef, Pt) + inter[None,:]
    _Map.coef_=coef; _Map.inter_=inter
    return _Map()

def score_full(P_val, A_val, idx):
    if len(idx)==0: return float("inf"), None
    if len(idx)==1:
        n=len(A_val); n2=n//2
        mae=float(np.mean(np.mean(np.abs(P_val[n2:, idx[0], :]-A_val[n2:]),axis=1)))
        return mae, None
    Psub=P_val[:, idx, :]; n=len(A_val); n2=n//2
    best=None; best_a=None
    for a in ALPHAS:
        r=fit_stack_map(Psub[:n2], A_val[:n2], a)
        sel=float(np.mean(np.mean(np.abs(r.predict(Psub[n2:])-A_val[n2:]),axis=1)))
        if best is None or sel<best: best=sel; best_a=a
    return best, best_a

def score_banded(P_val, A_val, idx):
    """Per-band alpha search: independent ALPHAS scan per band on held-out n2."""
    Psub=P_val[:, idx, :]; n=len(A_val); n2=n//2
    P_tr, P_sel = Psub[:n2], Psub[n2:]
    A_tr, A_sel = A_val[:n2], A_val[n2:]
    best_alphas=[]
    for lo,hi in BANDS:
        best=None; best_a=None
        for a in ALPHAS:
            # fit band horizons with a, score only that band's horizons
            coef_b=np.empty((Psub.shape[1], hi-lo))
            for k in range(lo, hi):
                r=Ridge(alpha=a, fit_intercept=False).fit(P_tr[:,:,k], A_tr[:,k])
                coef_b[:, k-lo]=r.coef_
            # predict band slice
            pred = np.einsum("mh,nmh->nh", coef_b, P_sel[:,:,lo:hi])
            mae=float(np.mean(np.mean(np.abs(pred - A_sel[:, lo:hi]),axis=1)))
            if best is None or mae<best: best=mae; best_a=a
        best_alphas.append(best_a)
    # overall held-out MAE for the banded vector
    r=fit_stack_map_banded(P_tr, A_tr, best_alphas)
    sel=float(np.mean(np.mean(np.abs(r.predict(P_sel)-A_sel),axis=1)))
    return sel, best_alphas

def preds_for_train_fit(factory, train_series, full_series, starts, L, H):
    """Fit on train_series, predict origins in full_series via history swap (S-20 protocol)."""
    m=factory(); m.fit(train_series, horizon=H)
    out=[]; hist=m.history_
    for s in starts:
        m.history_=full_series[:s]
        out.append(np.asarray(m.predict(),dtype=float))
    m.history_=hist
    return np.asarray(out)

def preds_for_full_fit(factory, full_series, concat_series, starts, L, H):
    """Fit on full_series (11425), predict origins in concat via history swap."""
    m=factory(); m.fit(full_series, horizon=H)
    out=[]; hist=m.history_
    for s in starts:
        m.history_=concat_series[:s]
        out.append(np.asarray(m.predict(),dtype=float))
    m.history_=hist
    return np.asarray(out)

def collect_val(train_series, full_series, starts):
    cols=[]
    for name,factory in CANDIDATES:
        L=factory().input_length
        p=preds_for_train_fit(factory, train_series, full_series, starts, L, HORIZON)
        cols.append(p); print(f"  {name:20s} L={L:3d} ok {p.shape}")
    return np.stack(cols, axis=1)

def collect_test(full_series, concat_series, starts):
    cols=[]
    for name,factory in CANDIDATES:
        L=factory().input_length
        p=preds_for_full_fit(factory, full_series, concat_series, starts, L, HORIZON)
        cols.append(p); print(f"  {name:20s} L={L:3d} ok {p.shape}")
    return np.stack(cols, axis=1)

def rolling_metrics(preds, actuals):
    err=preds-actuals
    mae_per=np.mean(np.abs(err),axis=1); rmse_per=np.sqrt(np.mean(err**2,axis=1))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err**2))), mae_per, rmse_per

def main():
    t_all=time.time()
    pd=get_protocol_data()
    fit_series, _, test_series = pd.rolling_views()
    train_series = fit_series[:TRAIN_END]
    val_series=fit_series[TRAIN_END:]; n_val=len(val_series)-HORIZON+1
    assert n_val==2161
    assert len(train_series)==8545 and len(fit_series)==11425
    print(f"fingerprint check: train {len(train_series)} fit {len(fit_series)} val {n_val} H={HORIZON}")
    val_starts=np.arange(n_val)+TRAIN_END
    print(f"collecting P_val {len(CANDIDATES)} members frozen on {TRAIN_END} (S-20-clean)...")
    P_val=collect_val(train_series, fit_series, val_starts)
    A_val=np.stack([val_series[t:t+HORIZON] for t in range(n_val)])

    # Baseline pooled alpha
    base_sel, base_alpha = score_full(P_val, A_val, INC_IDX)
    print(f"\npooled best alpha*={base_alpha} held-out MAE {base_sel:.4f}")
    # Banded selection
    band_sel, band_alphas = score_banded(P_val, A_val, INC_IDX)
    print(f"banded alphas {band_alphas} held-out MAE {band_sel:.4f}")

    # Refit all val with each, evaluate frozen test
    n=len(A_val); n2=n//2
    # pooled stack refit all val
    stack_pooled = fit_stack_map(P_val[:, INC_IDX, :], A_val, base_alpha if base_alpha is not None else 3000.0)
    # banded stack refit all val
    stack_banded = fit_stack_map_banded(P_val[:, INC_IDX, :], A_val, band_alphas)

    val_full_pooled=float(np.mean(np.mean(np.abs(stack_pooled.predict(P_val[:,INC_IDX,:])-A_val),axis=1)))
    val_full_banded=float(np.mean(np.mean(np.abs(stack_banded.predict(P_val[:,INC_IDX,:])-A_val),axis=1)))
    print(f"refit-all-val pooled MAE {val_full_pooled:.4f}  banded MAE {val_full_banded:.4f}")

    concat=np.concatenate([fit_series, test_series])
    # disjoint-4
    disj_starts=np.array([len(fit_series)+s for s in DISJOINT_STARTS])
    P_disj_all=collect_test(fit_series, concat, disj_starts)
    P_disj=P_disj_all[:, INC_IDX, :]
    A_disj=np.stack([test_series[s:s+HORIZON] for s in DISJOINT_STARTS])
    mae_d_p, rmse_d_p, _, _ = rolling_metrics(stack_pooled.predict(P_disj), A_disj)
    mae_d_b, rmse_d_b, _, _ = rolling_metrics(stack_banded.predict(P_disj), A_disj)
    # full 2161
    n_test=len(test_series)-HORIZON+1
    test_starts=np.arange(n_test)+len(fit_series)
    P_test_all=collect_test(fit_series, concat, test_starts)
    P_test=P_test_all[:, INC_IDX, :]
    A_test=np.stack([test_series[t:t+HORIZON] for t in range(n_test)])
    mae_f_p, rmse_f_p, _, _ = rolling_metrics(stack_pooled.predict(P_test), A_test)
    mae_f_b, rmse_f_b, _, _ = rolling_metrics(stack_banded.predict(P_test), A_test)
    print(f"\npooled:  disjoint {mae_d_p:.4f}/{rmse_d_p:.4f}  full {mae_f_p:.4f}/{rmse_f_p:.4f}")
    print(f"banded:  disjoint {mae_d_b:.4f}/{rmse_d_b:.4f}  full {mae_f_b:.4f}/{rmse_f_b:.4f}")
    print(f"incumbent 1.9909  delta pooled {mae_f_p-INCUMBENT_MAE:+.4f}  delta banded {mae_f_b-INCUMBENT_MAE:+.4f}")

    # Verdict per Rank 1 acceptance
    interior = not all(a==10000 for a in band_alphas)
    beats = (INCUMBENT_MAE - mae_f_b) > 0.005
    disjoint_improves = mae_d_b < mae_d_p - 1e-9  # and implicitly vs pooled; full selector is mae_f_b vs incumbent
    # strict: disjoint also vs pooled incumbent path's disjoint
    verdict = "ACCEPT" if (beats and interior and disjoint_improves) else "REJECT"
    reason=[]
    if not beats: reason.append(f"banded full {mae_f_b:.4f} not >0.005 better than {INCUMBENT_MAE}")
    if not interior: reason.append(f"banded alphas {band_alphas} all 10000 (not interior)")
    if not disjoint_improves: reason.append(f"disjoint {mae_d_b:.4f} not < pooled disjoint {mae_d_p:.4f}")
    print(f"\nverdict: {verdict}  interior={interior} beats={beats} disjoint_improves={disjoint_improves}")
    if reason: print("  reasons: " + "; ".join(reason))

    out={
        "slice":"S-27-horizon-band-alpha",
        "bands": BANDS,
        "alphas_grid": ALPHAS,
        "incumbent_mae": INCUMBENT_MAE,
        "pooled": {"alpha": base_alpha, "held_out_mae": base_sel, "val_full": val_full_pooled, "disjoint": {"mae": mae_d_p, "rmse": rmse_d_p}, "full": {"mae": mae_f_p, "rmse": rmse_f_p, "n": n_test}},
        "banded": {"alphas": band_alphas, "held_out_mae": band_sel, "val_full": val_full_banded, "disjoint": {"mae": mae_d_b, "rmse": rmse_d_b}, "full": {"mae": mae_f_b, "rmse": rmse_f_b, "n": n_test}},
        "verdict": verdict,
        "reasons": reason,
        "protocol": "S-20-clean: preds_for_train_fit for val (members frozen 8545), preds_for_full_fit for test (refrozen 11425); bands 0-240/240-480/480-720; 11-alpha grid interior check; full 2161 selector, disjoint diagnostic only",
        "fingerprint": str(pd.fingerprint) if hasattr(pd, 'fingerprint') else None,
    }
    with open(HERE/"results_s27.json","w") as f: json.dump(out,f,indent=2)
    print(f"\nwrote {HERE/'results_s27.json'} elapsed {time.time()-t_all:.1f}s")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
