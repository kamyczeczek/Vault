"""S-29 — Horizon-Weighted Ridge over S-26 2-member incumbent [NLinear L336 a=1+a=10].

Map-level guard (graph-brain hotspots, fingerprint 627189679626):
  fit  projects/ts-ml-experiments/h720/methods/nlinear_knn.py:65  in=0 out=48 degree=48
No _lag_dataset/base.py change — only reweights held-out selector.

Protocol S-20-clean:
  P_val: members frozen on train 8545, origins in fit_series (11425) val slice (2161 origins)
  P_test: members refrozen on full fit_series 11425, origins in concat (fit+test)
  n2 = 1080/1081 split (held-out half), 11-alpha grid, gamma grid {-0.5,0,0.5,1.0}
  Loss for selection: weighted L2  sum_h u_h(gamma)*|r_h|^2  (mean over n) on held-out half;
  pooled MAE still reported for comparison.  u_h(gamma) = exp(gamma*h/H) / mean(exp(...))  so gamma=0 is flat.
  Refit-all-val on full 2161 val with winning alpha, frozen test Full 2161 is selector, disjoint-4 diagnostic.
"""
from __future__ import annotations
import collections, json, sys, time
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
GAMMAS = [-0.5, 0.0, 0.5, 1.0]
DISJOINT_STARTS = (0,720,1440,2160)
INCUMBENT_MAE = 1.9909
INCUMBENT_DISJOINT = 1.9696

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

def horizon_weights(gamma, H):
    h = np.arange(H, dtype=float)
    w = np.exp(gamma * h / H)
    w = w / np.mean(w)  # mean 1 so gamma=0 => 1
    return w  # (H,)

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
    val_starts=np.arange(n_val)+TRAIN_END
    print(f"collecting P_val {len(CANDIDATES)} members frozen on {TRAIN_END}, val {n_val} origins...")
    P_val=collect_val(train_series, fit_series, val_starts)
    A_val=np.stack([val_series[t:t+HORIZON] for t in range(n_val)])
    print(f"P_val {P_val.shape} A_val {A_val.shape}")
    for j,(name,_) in enumerate(CANDIDATES):
        mae=float(np.mean(np.mean(np.abs(P_val[:,j,:]-A_val),axis=1)))
        print(f"  {name:20s} val {mae:.4f}")

    n=len(A_val); n2=n//2
    P_tr, P_sel = P_val[:n2], P_val[n2:]
    A_tr, A_sel = A_val[:n2], A_val[n2:]
    H = HORIZON

    # Pooled (flat) best alpha (baseline reproduction of S-26 selector)
    best_pooled=None; best_pooled_a=None
    for a in ALPHAS:
        r=fit_stack_map(P_tr, A_tr, a)
        sel=float(np.mean(np.mean(np.abs(r.predict(P_sel)-A_sel),axis=1)))
        if best_pooled is None or sel<best_pooled: best_pooled=sel; best_pooled_a=a
    print(f"\npooled best: alpha {best_pooled_a} held_out MAE {best_pooled:.4f}")

    # Weighted grid search
    best_w = None; best_gamma=None; best_alpha=None; best_pooled_at_best=None
    records=[]
    for g in GAMMAS:
        w = horizon_weights(g, H)  # (H,)
        for a in ALPHAS:
            r=fit_stack_map(P_tr, A_tr, a)
            pred = r.predict(P_sel)
            err = pred - A_sel
            weighted_mse = float(np.mean(np.sum((err**2) * w[None,:], axis=1) / H))  # mean over n of weighted mean over h
            # also pooled MAE for reporting
            pooled_mae = float(np.mean(np.mean(np.abs(err),axis=1)))
            records.append({"gamma":g,"alpha":a,"weighted_mse":weighted_mse,"pooled_mae":pooled_mae})
            if best_w is None or weighted_mse < best_w:
                best_w=weighted_mse; best_gamma=g; best_alpha=a; best_pooled_at_best=pooled_mae
    print(f"weighted best: gamma {best_gamma} alpha {best_alpha} weighted_mse {best_w:.6f} pooled_mae {best_pooled_at_best:.4f}")
    # also report pooled MAE at pooled best vs weighted best's pooled
    print(f"  pooled best alpha {best_pooled_a} pooled MAE {best_pooled:.4f} vs weighted pick pooled {best_pooled_at_best:.4f} delta {best_pooled_at_best-best_pooled:+.4f}")

    # Refit-all-val with weighted winner alpha (coef unchanged, just selected alpha)
    # Also refit pooled winner for comparison
    sel_gamma, sel_alpha = best_gamma, best_alpha
    # S-20-clean refit: stack trained on full P_val/A_val with winning alpha
    stack_w = fit_stack_map(P_val, A_val, sel_alpha)
    stack_pooled = fit_stack_map(P_val, A_val, best_pooled_a)
    val_full_w = float(np.mean(np.mean(np.abs(stack_w.predict(P_val)-A_val),axis=1)))
    val_full_pooled = float(np.mean(np.mean(np.abs(stack_pooled.predict(P_val)-A_val),axis=1)))
    print(f"refit all val: weighted pick alpha {sel_alpha} val_full {val_full_w:.4f} | pooled pick alpha {best_pooled_a} val_full {val_full_pooled:.4f}")

    # Frozen test evaluation (members refrozen on full 11425)
    concat=np.concatenate([fit_series, test_series])
    disj_starts=np.array([len(fit_series)+s for s in DISJOINT_STARTS])
    P_disj_all=collect_test(fit_series, concat, disj_starts)
    A_disj=np.stack([test_series[s:s+HORIZON] for s in DISJOINT_STARTS])
    n_test=len(test_series)-HORIZON+1
    test_starts=np.arange(n_test)+len(fit_series)
    P_test_all=collect_test(fit_series, concat, test_starts)
    A_test=np.stack([test_series[t:t+HORIZON] for t in range(n_test)])

    # Score both stacks
    def score_stack(stack):
        preds_disj=stack.predict(P_disj_all[:, INC_IDX, :] if P_disj_all.shape[1]==len(CANDIDATES) else P_disj_all)
        # P_disj_all is (4, M, H) already 2 members, no indexing needed if M==2
        if P_disj_all.shape[1]==len(CANDIDATES):
            preds_disj=stack.predict(P_disj_all)
            preds_full=stack.predict(P_test_all)
        else:
            preds_disj=stack.predict(P_disj_all)
            preds_full=stack.predict(P_test_all)
        mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)
        mae_full, rmse_full, _, _ = rolling_metrics(preds_full, A_test)
        return mae_disj, rmse_disj, mae_full, rmse_full

    mae_disj_w, rmse_disj_w, mae_full_w, rmse_full_w = score_stack(stack_w)
    mae_disj_p, rmse_disj_p, mae_full_p, rmse_full_p = score_stack(stack_pooled)
    print(f"\n--- Test results (frozen) ---")
    print(f"weighted pick (g={sel_gamma} a={sel_alpha}): disjoint {mae_disj_w:.4f} full2161 {mae_full_w:.4f} (delta vs S-26 {mae_full_w-INCUMBENT_MAE:+.4f})")
    print(f"pooled pick            (a={best_pooled_a}): disjoint {mae_disj_p:.4f} full2161 {mae_full_p:.4f} (delta vs S-26 {mae_full_p-INCUMBENT_MAE:+.4f})")
    print(f"S-26 incumbent: full {INCUMBENT_MAE:.4f} disjoint {INCUMBENT_DISJOINT:.4f}")
    print(f"Acceptance: full < {INCUMBENT_MAE-0.005:.4f} ({INCUMBENT_MAE:.4f}-0.005) AND disjoint <= {INCUMBENT_DISJOINT:.4f} AND gamma*!=0 interior alpha")

    # Verdict per spec: full selector is weighted pick's full2161
    full_mae = mae_full_w
    disj_mae = mae_disj_w
    interior_alpha = sel_alpha not in (ALPHAS[0], ALPHAS[-1])
    passed_full = full_mae < (INCUMBENT_MAE - 0.005 - 1e-9)
    passed_disj = disj_mae <= INCUMBENT_DISJOINT + 1e-9
    passed_gamma = sel_gamma != 0.0
    # For guard, also require weighted best not same as pooled best if gamma0 would imply no effect
    verdict = "ACCEPT" if (passed_full and passed_disj and passed_gamma and interior_alpha) else "REJECT"
    reason=[]
    if not passed_full: reason.append(f"full {full_mae:.4f} not < {INCUMBENT_MAE-0.005:.4f}")
    if not passed_disj: reason.append(f"disjoint {disj_mae:.4f} > {INCUMBENT_DISJOINT:.4f}")
    if not passed_gamma: reason.append(f"gamma*={sel_gamma} ==0 (flat)")
    if not interior_alpha: reason.append(f"alpha {sel_alpha} at boundary")
    print(f"\nVerdict: {verdict} — {'; '.join(reason) if reason else 'all guards pass'}")
    print(f"  gamma* {sel_gamma} alpha* {sel_alpha} held_out_weighted {best_w:.6f} held_out_pooled {best_pooled_at_best:.4f} val_full {val_full_w:.4f} full2161 {full_mae:.4f} disjoint {disj_mae:.4f}")

    out={
        "slice":"S-29-horizon-weighted-ridge",
        "protocol":"S-20-clean: val members frozen on 8545, test members refrozen on 11425, n2=1080/1081, 2-member [NLinear L336 a1+a10]",
        "incumbent":{"full_mae":INCUMBENT_MAE, "disjoint_mae":INCUMBENT_DISJOINT},
        "gamma_grid":GAMMAS,
        "alphas":ALPHAS,
        "weight_form":"exp(gamma*h/H) normalized mean 1",
        "held_out":{"n_tr":int(n2),"n_sel":int(n-n2),"pooled_best":{"alpha":best_pooled_a,"mae":best_pooled},"weighted_best":{"gamma":best_gamma,"alpha":best_alpha,"weighted_mse":best_w,"pooled_mae":best_pooled_at_best}},
        "records":records,
        "refit_all_val":{"weighted_pick_val_full":val_full_w, "pooled_pick_val_full":val_full_pooled},
        "test":{"weighted_pick":{"full_mae":mae_full_w,"full_rmse":rmse_full_w,"disjoint_mae":mae_disj_w,"disjoint_rmse":rmse_disj_w},
                "pooled_pick":{"full_mae":mae_full_p,"full_rmse":rmse_full_p,"disjoint_mae":mae_disj_p,"disjoint_rmse":rmse_disj_p},
                "n_test":int(n_test)},
        "verdict":verdict,
        "reason":reason,
        "guards":{"passed_full":passed_full,"passed_disj":passed_disj,"passed_gamma":passed_gamma,"interior_alpha":interior_alpha}
    }
    with open(HERE/"results_s29.json","w") as f: json.dump(out,f,indent=2)
    print(f"\nwrote {HERE/'results_s29.json'} elapsed {time.time()-t_all:.1f}s")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
