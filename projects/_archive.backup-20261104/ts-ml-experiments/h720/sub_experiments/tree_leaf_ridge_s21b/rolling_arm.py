"""S-21b — Level-free tree heads with leaf-wise linear mixtures of member deltas.

User design (two corrections to S-21):
  1. every model in the mixture is level-anchored (NLinear trick: prediction =
     anchor + delta), so the head must be level-free too - S-21 stored per-leaf
     LEVELS of raw (level-inclusive) predictions;
  2. tree leaves must NOT hold constants - each leaf holds a LINEAR MIXTURE of
     the members.

Construction:
  anchor(t) = last history value at origin t (NLinear anchor; all 6 members
  are level-anchored: NLinear at last value, DLinear at window mean, so all
  member deltas are level-free and mutually consistent).
  delta_j(t,h) = P_j(t,h) - anchor(t)     (member-delta features)
  d*(t,h)      = A(t,h) - anchor(t)       (target delta)
  per-horizon head: 720 trees over 6 delta features; each leaf stores the
  RIDGE solution (with intercept, alpha=10) of d* on member deltas for origins
  falling in that leaf => leaf prediction = anchor + leaf-linear-mix.
  shared head: ONE tree over [6 deltas, horizon step]; same leaf-ridge readout.
  The delta SPREAD carries regime signal level-free; horizon step carries
  per-horizon structure.

Protocol (S-20/S-21 exactly): members frozen on train 8,545; grid selected on
held-out SECOND val half (pooled MAE, all horizons); refit all val; members
re-frozen on 11,425; test never consulted. In-harness control: S-20 per-horizon
ridge on delta features (alpha 3000). Fail-loud member anchors (6).
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.tree import DecisionTreeRegressor

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, DLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
VALIDATION_END = 11425
MEMBERS = [
    ("nlinear_L336_a1", lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L96_a1",  lambda: NLinear(input_length=96,  ridge_alpha=1.0)),
    ("nlinear_L720_a1", lambda: NLinear(input_length=720, ridge_alpha=1.0)),
    ("dlinear_L96_a0",   lambda: DLinear(input_length=96,  kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L336_a0",  lambda: DLinear(input_length=336, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L720_a0",  lambda: DLinear(input_length=720, kernel_size=25, ridge_alpha=0.0)),
]
ANCHOR_TEST_MAE = {
    "nlinear_L336_a1": 2.0571, "nlinear_L96_a1": 2.0925, "nlinear_L720_a1": 2.1534,
    "dlinear_L96_a0": 2.1163, "dlinear_L336_a0": 2.1220, "dlinear_L720_a0": 2.1687,
}
LEAF_RIDGE_ALPHA = 10.0
PER_HORIZON_GRID = [(2,25),(3,25),(4,25),(5,25),(6,25)]
SHARED_GRID = [(4,25),(6,25),(8,25),(10,25),(12,25)]
RIDGE_ALPHA_CONTROL = 3000.0

def collect_preds(models, series, n, base):
    P = np.empty((n, len(models), HORIZON))
    for j,m in enumerate(models):
        for t in range(n):
            orig=m.history_
            try:
                m.history_=series[:base+t]
                P[t,j,:]=np.asarray(m.predict(),dtype=float)
            finally:
                m.history_=orig
    return P

def rolling_metrics(preds, actuals):
    err=preds-actuals
    mae_per=np.mean(np.abs(err),axis=1)
    disj={f"window_{i+1}":{"mae":float(mae_per[t])} for i,t in enumerate(DISJOINT_STARTS)}
    return float(mae_per.mean()), float(np.sqrt(np.mean(err**2))), disj

def _leaf_ridge_for_tree(tree, X, y, alpha):
    ids=tree.apply(X)
    uniq=np.unique(ids)
    max_id=int(ids.max())+1
    coefs=[None]*max_id
    inters=[0.0]*max_id
    M=X.shape[1]
    for lid in uniq:
        sel=ids==lid
        if sel.sum() < 2:
            coefs[lid]=np.zeros(M); inters[lid]=float(y[sel].mean()) if sel.sum()==1 else 0.0
        else:
            r=Ridge(alpha=alpha, fit_intercept=True).fit(X[sel], y[sel])
            coefs[lid]=np.asarray(r.coef_); inters[lid]=float(r.intercept_)
    for lid in range(max_id):
        if coefs[lid] is None:
            coefs[lid]=np.zeros(M)
    return coefs, inters

def fit_per_horizon_leaf_ridge(Pd, Ad, at_dummy, depth, leaf, alpha=LEAF_RIDGE_ALPHA):
    # Pd (n,M,H), Ad (n,H) deltas; at not needed for fit
    n,M,H = Pd.shape
    heads=[]
    for h in range(H):
        X=Pd[:,:,h]; y=Ad[:,h]
        tree=DecisionTreeRegressor(max_depth=depth, min_samples_leaf=leaf, random_state=42).fit(X,y)
        coefs,inters=_leaf_ridge_for_tree(tree,X,y,alpha)
        heads.append((tree,coefs,inters))
    max_leaves = max(int(np.sum(t.tree_.node_count) if False else np.sum(t.tree_.children_left!=-1)) for t,_,_ in heads)
    # predict closure
    def predict(Pd2, at2):
        n2=Pd2.shape[0]
        out=np.empty((n2, H))
        for h,(tree,coefs,inters) in enumerate(heads):
            X=Pd2[:,:,h]
            ids=tree.apply(X)
            C=np.stack(coefs)[ids]  # (n2,M)
            I=np.array(inters)[ids]
            out[:,h]=at2 + np.einsum("nm,nm->n", X, C) + I
        return out
    predict.n_heads=len(heads)
    predict.max_leaves_approx=max_leaves
    return predict

def fit_shared_leaf_ridge(Pd, Ad, depth, leaf, alpha=LEAF_RIDGE_ALPHA):
    n,M,H = Pd.shape
    X=np.empty((n*H, M+1))
    X[:,:M]=Pd.transpose(0,2,1).reshape(-1,M)
    X[:,M]=np.tile(np.arange(H), n)
    y=Ad.reshape(-1)
    tree=DecisionTreeRegressor(max_depth=depth, min_samples_leaf=leaf, random_state=42).fit(X,y)
    # fit leaf ridges on delta features: need leaf ids from full (M+1) tree fit, not re-apply on 6-col X
    ids_full=tree.apply(X)
    coefs=[None]* (int(ids_full.max())+1 if len(ids_full)>0 else 1)
    inters=[0.0]*len(coefs)
    for lid in np.unique(ids_full):
        sel=ids_full==lid
        Xl=X[:,:M][sel]
        yl=y[sel]
        if sel.sum()<2:
            coefs[lid]=np.zeros(M); inters[lid]=float(yl.mean()) if sel.sum()==1 else 0.0
        else:
            r=Ridge(alpha=alpha, fit_intercept=True).fit(Xl, yl)
            coefs[lid]=np.asarray(r.coef_); inters[lid]=float(r.intercept_)
    for lid in range(len(coefs)):
        if coefs[lid] is None: coefs[lid]=np.zeros(M)
    n_leaves=int(np.sum(tree.tree_.children_left!=-1))
    def predict(Pd2, at2):
        n2=Pd2.shape[0]
        Xf=np.empty((n2*H, M))
        Xf[:,:M]=Pd2.transpose(0,2,1).reshape(-1,M)
        # for routing need full X with horizon
        Xfull=np.empty((n2*H, M+1))
        Xfull[:,:M]=Xf
        Xfull[:,M]=np.tile(np.arange(H), n2)
        ids=tree.apply(Xfull)
        C=np.stack(coefs)[ids]
        I=np.array(inters)[ids]
        d_pred=np.einsum("km,km->k", Xf, C) + I
        d_pred=d_pred.reshape(n2,H)
        return at2[:,None] + d_pred
    predict.n_leaves=n_leaves
    return predict

def main():
    t_all=time.time()
    pd=get_protocol_data()
    fit_history, eval_series, test = pd.rolling_views()
    train_8545=fit_history[:TRAIN_END]
    n_val=len(fit_history)-TRAIN_END-HORIZON+1
    n_test=len(test)-HORIZON+1
    assert n_val==2161 and n_test==2161
    print("fitting 6 members on train 8545 ...")
    models=[f().fit(train_8545, horizon=HORIZON) for _,f in MEMBERS]
    print("collecting val predictions ...")
    P_val=collect_preds(models, fit_history, n_val, TRAIN_END)
    A_val=np.stack([fit_history[TRAIN_END+t: TRAIN_END+t+HORIZON] for t in range(n_val)])
    at_val=np.array([fit_history[TRAIN_END+t-1] for t in range(n_val)], dtype=float)
    Pd_val=P_val - at_val[:,None,None]
    Ad_val=A_val - at_val[:,None]
    for j,(name,_) in enumerate(MEMBERS):
        print(f"  {name:16s} val {float(np.mean(np.abs(P_val[:,j,:]-A_val))):.4f}")
    n_fit=n_val//2
    Pd_fit=Pd_val[:n_fit]; Ad_fit=Ad_val[:n_fit]; at_fit=at_val[:n_fit]
    Pd_sel=Pd_val[n_fit:]; Ad_sel=Ad_val[n_fit:]; at_sel=at_val[n_fit:]
    A_sel=A_val[n_fit:]

    # ridge control on deltas
    print(f"\nridge control on deltas (alpha={RIDGE_ALPHA_CONTROL:g}) ...")
    t0=time.time()
    ridge_coef=np.empty((6, HORIZON))
    for h in range(HORIZON):
        r=Ridge(alpha=RIDGE_ALPHA_CONTROL, fit_intercept=False).fit(Pd_fit[:,:,h], Ad_fit[:,h])
        ridge_coef[:,h]=r.coef_
    # delta ridge predicts Ad, raw = at + delta
    pred_sel_delta=np.einsum("mh,nmh->nh", ridge_coef, Pd_sel.transpose(0,2,1).transpose(1,2,0) if False else Pd_sel.transpose(0,2,1)) if False else None
    # correct einsum: ridge_coef (M,H), Pd_sel (n,M,H) -> (n,H)
    pred_sel_raw = at_sel[:,None] + np.einsum("mh,nmh->nh", ridge_coef, Pd_sel.transpose(0,2,1).transpose(0,2,1) if False else np.einsum("nmh->nmh",Pd_sel) ) if False else None
    # simple loop for correctness
    pred_sel_raw = at_sel[:,None] + np.stack([Pd_sel[:,:,h] @ ridge_coef[:,h] for h in range(HORIZON)], axis=1)
    ridge_sel=float(np.mean(np.abs(pred_sel_raw - A_sel)))
    print(f"  2nd-half val MAE {ridge_sel:.4f} ({time.time()-t0:.1f}s)  [S-20 raw map 1.9980]")

    print("\nPER-HORIZON leaf-ridge tree grid (fit 1080, select 1081) ...")
    ph_scores={}
    ph_heads={}
    for depth,leaf in PER_HORIZON_GRID:
        t0=time.time()
        head=fit_per_horizon_leaf_ridge(Pd_fit, Ad_fit, at_fit, depth, leaf)
        pred= head(Pd_sel, at_sel)
        s=float(np.mean(np.abs(pred - A_sel)))
        ph_scores[(depth,leaf)]=s; ph_heads[(depth,leaf)]=head
        print(f"  depth {depth} leaf {leaf}: 2nd-half val MAE {s:.4f} ({time.time()-t0:.1f}s)")
    best_ph=min(ph_scores, key=ph_scores.get)
    print(f"best per-horizon: depth {best_ph[0]} leaf {best_ph[1]} ({ph_scores[best_ph]:.4f})")

    print("\nSHARED leaf-ridge tree grid ...")
    sh_scores={}
    for depth,leaf in SHARED_GRID:
        t0=time.time()
        head=fit_shared_leaf_ridge(Pd_fit, Ad_fit, depth, leaf)
        pred=head(Pd_sel, at_sel)
        s=float(np.mean(np.abs(pred - A_sel)))
        sh_scores[(depth,leaf)]=s
        print(f"  depth {depth} leaf {leaf}: 2nd-half val MAE {s:.4f} ({time.time()-t0:.1f}s) leaves {head.n_leaves}")
    best_sh=min(sh_scores, key=sh_scores.get)
    print(f"best shared: depth {best_sh[0]} leaf {best_sh[1]} ({sh_scores[best_sh]:.4f})")

    # refit winners on ALL val
    head_ph=fit_per_horizon_leaf_ridge(Pd_val, Ad_val, at_val, *best_ph)
    head_sh=fit_shared_leaf_ridge(Pd_val, Ad_val, *best_sh)
    for h in range(HORIZON):
        r=Ridge(alpha=RIDGE_ALPHA_CONTROL, fit_intercept=False).fit(Pd_val[:,:,h], Ad_val[:,h])
        ridge_coef[:,h]=r.coef_
    pred_all_ph=head_ph(Pd_val, at_val)
    pred_all_sh=head_sh(Pd_val, at_val)
    pred_all_rg=at_val[:,None] + np.stack([Pd_val[:,:,h] @ ridge_coef[:,h] for h in range(HORIZON)], axis=1)
    print(f"\nrefit all val (in-sample): per-horizon {float(np.mean(np.abs(pred_all_ph-A_val))):.4f} / shared {float(np.mean(np.abs(pred_all_sh-A_val))):.4f} / ridge {float(np.mean(np.abs(pred_all_rg-A_val))):.4f}")

    print("\nre-fitting 6 members on full 11425 ...")
    frozen=[f().fit(fit_history, horizon=HORIZON) for _,f in MEMBERS]
    print("collecting test predictions ...")
    P_test=collect_preds(frozen, eval_series, n_test, VALIDATION_END)
    A_test=np.stack([test[t:t+HORIZON] for t in range(n_test)])
    at_test=np.array([eval_series[VALIDATION_END+t-1] for t in range(n_test)], dtype=float)
    Pd_test=P_test - at_test[:,None,None]
    fail=[]
    for j,(name,_) in enumerate(MEMBERS):
        m=float(np.mean(np.abs(P_test[:,j,:]-A_test)))
        ok=abs(m-ANCHOR_TEST_MAE[name])<8e-4
        print(f"anchor {name:16s}: {m:.4f} expected {ANCHOR_TEST_MAE[name]} -> {'OK' if ok else 'FAIL'}")
        if not ok: fail.append(name)
    if fail:
        print(f"ANCHOR CHECK FAILED: {fail}"); return 1

    preds_ph=head_ph(Pd_test, at_test)
    preds_sh=head_sh(Pd_test, at_test)
    preds_rg=at_test[:,None] + np.stack([Pd_test[:,:,h] @ ridge_coef[:,h] for h in range(HORIZON)], axis=1)
    mae_ph,rmse_ph,disj_ph=rolling_metrics(preds_ph, A_test)
    mae_sh,rmse_sh,disj_sh=rolling_metrics(preds_sh, A_test)
    mae_rg,rmse_rg,disj_rg=rolling_metrics(preds_rg, A_test)
    mae_best,_,_=rolling_metrics(P_test[:,0,:], A_test)
    mae_mean,_,_=rolling_metrics(P_test.mean(axis=1), A_test)
    print(f"\n===============================================")
    print(f"PER-HORIZON leaf-ridge tree (d{best_ph[0]}/l{best_ph[1]})")
    print(f"  test rolling: {mae_ph:.4f} / {rmse_ph:.4f}")
    print(f"  disjoint: " + ", ".join(f"W{i+1} {disj_ph[f'window_{i+1}']['mae']:.4f}" for i in range(4)))
    print(f"  vs S-20 1.9980: {mae_ph-1.9980:+.4f}")
    print(f"SHARED leaf-ridge tree (d{best_sh[0]}/l{best_sh[1]}), leaves {head_sh.n_leaves}")
    print(f"  test rolling: {mae_sh:.4f} / {rmse_sh:.4f}")
    print(f"  disjoint: " + ", ".join(f"W{i+1} {disj_sh[f'window_{i+1}']['mae']:.4f}" for i in range(4)))
    print(f"  vs S-20 1.9980: {mae_sh-1.9980:+.4f}")
    print(f"RIDGE CONTROL on deltas (alpha={RIDGE_ALPHA_CONTROL:g}): {mae_rg:.4f} (expect ~1.9980)")
    print(f"baselines: best member {mae_best:.4f}, equal-mean {mae_mean:.4f}")
    print(f"===============================================")
    winner="per_horizon" if mae_ph < mae_sh else "shared"
    out={
        "slice":"S-21b",
        "protocol":{
            "members":[n for n,_ in MEMBERS],
            "anchor":"last history value per origin (NLinear anchor; level-free)",
            "features":"member deltas P_j-anchor; shared adds horizon step",
            "heads":["per-horizon tree with per-leaf ridge (linear mixture)","shared tree with per-leaf ridge"],
            "leaf_ridge_alpha":LEAF_RIDGE_ALPHA,
            "selection":"held-out second val half pooled MAE",
            "test":"frozen members refit 11425",
        },
        "validation":{
            "ridge_control_delta_second_half":round(ridge_sel,4),
            "per_horizon_grid":{f"d{d}_l{l}":round(s,4) for (d,l),s in ph_scores.items()},
            "shared_grid":{f"d{d}_l{l}":round(s,4) for (d,l),s in sh_scores.items()},
        },
        "test":{
            "anchors":{n:round(float(np.mean(np.abs(P_test[:,j,:]-A_test))),4) for j,(n,_) in enumerate(MEMBERS)},
            "per_horizon":{"config":list(best_ph),"rolling_mae":round(mae_ph,4),"rolling_rmse":round(rmse_ph,4),"disjoint_windows":disj_ph,"delta_vs_s20":round(mae_ph-1.9980,4)},
            "shared":{"config":list(best_sh),"rolling_mae":round(mae_sh,4),"rolling_rmse":round(rmse_sh,4),"disjoint_windows":disj_sh,"delta_vs_s20":round(mae_sh-1.9980,4)},
            "ridge_control_delta":{"rolling_mae":round(mae_rg,4),"delta_vs_s20":round(mae_rg-1.9980,4)},
            "baseline_best_member":round(mae_best,4),"baseline_equal_mean":round(mae_mean,4),
            "winner_by_rolling":winner,
        }
    }
    out_path=HERE/"results_s21b.json"
    out_path.write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(f"wrote {out_path} (total {time.time()-t_all:.1f}s)")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
