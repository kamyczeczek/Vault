"""S-28 — Per-horizon intercept probe over S-26 2-member incumbent.
Rank 2 from 2026-09-11 next_direction.md. Same 2 members, same 11-alpha grid,
same n2=1080/1081 split, same S-20-clean factories.

Variant: per-horizon Ridge with intercept=True vs incumbent intercept=False.
Fully map-level: no change to _lag_dataset @ base.py:197 (d27 hotspot, 14 in/13 out)
— graph hotspots: _lag_dataset d27 warns any lag/norm change fans to all members,
so this stays as a stack-level Ridge flag only (fit_stack_map intercept branch).

Accept: full 2161 MAE <1.9909 by >0.005 AND held-out also wins vs 2.5191;
else REJECT — no-intercept stands per scar [8] P1 level-memorization guard.

Hotspots cite (2026-09-11): python ../../brains/graph_brain/ask.py --hotspots | head -n 5
  _lag_dataset  projects/ts-ml-experiments/h720/methods/base.py:197  in=14 out=13 degree=27
  — therefore map-level only, no base.py touch.

Protocol: S-20-clean (preds_for_train_fit for val, preds_for_full_fit for test),
frozen test 2161 + disjoint-4 diagnostic.
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
INCUMBENT_MAE = 1.9909
HELD_OUT_BASELINE = 2.51907740175763  # S-27 pooled no-intercept held-out (reference)

CANDIDATES = [
    ("nlinear_L336_a1",  lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
]
INC_IDX = [0,1]

def fit_stack_map(P, A, alpha, fit_intercept=False):
    n,m,h=P.shape; coef=np.empty((m,h)); inter=np.zeros(h)
    for k in range(h):
        r=Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:,:,k], A[:,k])
        coef[:,k]=r.coef_
        if fit_intercept:
            inter[k]=r.intercept_
    class _Map:
        def predict(self, Pt): return np.einsum("mh,nmh->nh", coef, Pt) + inter[None,:]
    _Map.coef_=coef; _Map.inter_=inter
    return _Map()

def score_full(P_val, A_val, idx, fit_intercept=False):
    if len(idx)==0: return float("inf"), None
    if len(idx)==1:
        n=len(A_val); n2=n//2
        mae=float(np.mean(np.mean(np.abs(P_val[n2:, idx[0], :]-A_val[n2:]),axis=1)))
        return mae, None
    Psub=P_val[:, idx, :]; n=len(A_val); n2=n//2
    best=None; best_a=None
    for a in ALPHAS:
        r=fit_stack_map(Psub[:n2], A_val[:n2], a, fit_intercept=fit_intercept)
        sel=float(np.mean(np.mean(np.abs(r.predict(Psub[n2:])-A_val[n2:]),axis=1)))
        if best is None or sel<best: best=sel; best_a=a
    return best, best_a

def preds_for_train_fit(factory, train_series, full_series, starts, L, H):
    m=factory(); m.fit(train_series, horizon=H)
    out=[]; hist=m.history_
    for s in starts:
        m.history_=full_series[:s]
        out.append(np.asarray(m.predict(),dtype=float))
    m.history_=hist
    return np.asarray(out)

def preds_for_full_fit(factory, full_series, concat_series, starts, L, H):
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

    # Pooled selection both ways
    base_sel, base_alpha = score_full(P_val, A_val, INC_IDX, fit_intercept=False)
    print(f"\npooled no-intercept  best alpha*={base_alpha} held-out MAE {base_sel:.4f}")
    int_sel, int_alpha = score_full(P_val, A_val, INC_IDX, fit_intercept=True)
    print(f"pooled intercept     best alpha*={int_alpha} held-out MAE {int_sel:.4f}")

    # Refit all val
    stack_pooled = fit_stack_map(P_val[:, INC_IDX, :], A_val, base_alpha if base_alpha is not None else 3000.0, fit_intercept=False)
    stack_inter  = fit_stack_map(P_val[:, INC_IDX, :], A_val, int_alpha if int_alpha is not None else 3000.0, fit_intercept=True)

    val_full_pooled=float(np.mean(np.mean(np.abs(stack_pooled.predict(P_val[:,INC_IDX,:])-A_val),axis=1)))
    val_full_inter=float(np.mean(np.mean(np.abs(stack_inter.predict(P_val[:,INC_IDX,:])-A_val),axis=1)))
    print(f"refit-all-val pooled MAE {val_full_pooled:.4f}  intercept MAE {val_full_inter:.4f}")

    concat=np.concatenate([fit_series, test_series])
    disj_starts=np.array([len(fit_series)+s for s in DISJOINT_STARTS])
    P_disj_all=collect_test(fit_series, concat, disj_starts)
    P_disj=P_disj_all[:, INC_IDX, :]
    A_disj=np.stack([test_series[s:s+HORIZON] for s in DISJOINT_STARTS])
    mae_d_p, rmse_d_p, _, _ = rolling_metrics(stack_pooled.predict(P_disj), A_disj)
    mae_d_i, rmse_d_i, _, _ = rolling_metrics(stack_inter.predict(P_disj), A_disj)

    n_test=len(test_series)-HORIZON+1
    test_starts=np.arange(n_test)+len(fit_series)
    P_test_all=collect_test(fit_series, concat, test_starts)
    P_test=P_test_all[:, INC_IDX, :]
    A_test=np.stack([test_series[t:t+HORIZON] for t in range(n_test)])
    mae_f_p, rmse_f_p, _, _ = rolling_metrics(stack_pooled.predict(P_test), A_test)
    mae_f_i, rmse_f_i, _, _ = rolling_metrics(stack_inter.predict(P_test), A_test)
    print(f"\npooled:     disjoint {mae_d_p:.4f}/{rmse_d_p:.4f}  full {mae_f_p:.4f}/{rmse_f_p:.4f}")
    print(f"intercept:  disjoint {mae_d_i:.4f}/{rmse_d_i:.4f}  full {mae_f_i:.4f}/{rmse_f_i:.4f}")
    print(f"incumbent 1.9909  delta pooled {mae_f_p-INCUMBENT_MAE:+.4f}  delta intercept {mae_f_i-INCUMBENT_MAE:+.4f}")

    beats_full = (INCUMBENT_MAE - mae_f_i) > 0.005
    beats_held = int_sel < base_sel - 1e-9  # also vs HELD_OUT_BASELINE implicitly since base_sel should match it
    held_vs_ref = int_sel < HELD_OUT_BASELINE - 1e-9
    verdict = "ACCEPT" if (beats_full and beats_held) else "REJECT"
    reason=[]
    if not beats_full: reason.append(f"intercept full {mae_f_i:.4f} not >0.005 better than {INCUMBENT_MAE}")
    if not beats_held: reason.append(f"held-out intercept {int_sel:.4f} not < no-intercept {base_sel:.4f}")
    if verdict=="REJECT" and beats_full and not beats_held:
        reason.append("held-out guard fails — level-memorization risk [8] P1")
    print(f"\nverdict: {verdict}  beats_full={beats_full} beats_held={beats_held} held_vs_ref={held_vs_ref}")
    if reason: print("  reasons: " + "; ".join(reason))

    out={
        "slice":"S-28-per-horizon-intercept",
        "candidates": [c[0] for c in CANDIDATES],
        "alphas_grid": ALPHAS,
        "incumbent_mae": INCUMBENT_MAE,
        "held_out_baseline_ref": HELD_OUT_BASELINE,
        "pooled_no_intercept": {"fit_intercept": False, "alpha": base_alpha, "held_out_mae": base_sel, "val_full": val_full_pooled, "disjoint": {"mae": mae_d_p, "rmse": rmse_d_p}, "full": {"mae": mae_f_p, "rmse": rmse_f_p, "n": n_test}},
        "pooled_intercept": {"fit_intercept": True, "alpha": int_alpha, "held_out_mae": int_sel, "val_full": val_full_inter, "disjoint": {"mae": mae_d_i, "rmse": rmse_d_i}, "full": {"mae": mae_f_i, "rmse": rmse_f_i, "n": n_test}},
        "verdict": verdict,
        "reasons": reason,
        "acceptance": "full 2161 MAE <1.9909 by >0.005 AND held-out intercept < no-intercept (2.5191 ref)",
        "protocol": "S-20-clean: preds_for_train_fit for val (members frozen 8545), preds_for_full_fit for test (refrozen 11425); 11-alpha grid; chronological n2=1080/1081 split",
        "graph_note": "_lag_dataset @ base.py:197 d27 — map-level only, no base.py change; hotspots via ask.py --hotspots",
        "fingerprint": str(pd.fingerprint) if hasattr(pd, 'fingerprint') else None,
    }
    with open(HERE/"results_s28.json","w") as f: json.dump(out,f,indent=2)
    print(f"\nwrote {HERE/'results_s28.json'} elapsed {time.time()-t_all:.1f}s")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
