"""S-26 — Greedy-Tabu over UNIVARIATE LINEAR pool (no grid, no 7-ch, no trees).

Pool 12 univariate linear only:
  NLinear L96  a=1,10,100
  NLinear L336 a=1,10
  NLinear L720 a=1
  DLinear L96  k25/k49 a=0
  DLinear L336 k25/k49 a=0
  RLinear L96  a=0, L336 a=0   (Toner-Darlow tie expected vs DLinear)

Reuses S-25 scoring exactly: fast score = fit 1080 / select 1081 @ fixed α=3000
(full 11-α scan only on improved/×3 + final). Tabu 7, moves add/drop/swap1,
init best singleton, aspiration new global best, stop no-improve 5.
Frozen test selector = full 2161 rolling (disjoint-4 diagnostic only).
Protocol matches S-20 exactly: val predictions from members frozen on TRAIN_END=8545,
test predictions from members refrozen on 11425.

Run: python projects/ts-ml-experiments/h720/sub_experiments/greedy_linear_mixture_s26/rolling_arm.py
"""
from __future__ import annotations
import json, sys, time, collections
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, DLinear, RLinear

DISJOINT_STARTS = (0,720,1440,2160)
TRAIN_END = 8545
SEARCH_ALPHA = 3000.0
ALPHAS = [0.1,1.0,3.0,10.0,30.0,100.0,300.0,1000.0,3000.0,10000.0,30000.0]

CANDIDATES = [
    ("nlinear_L96_a1",    lambda: NLinear(input_length=96, ridge_alpha=1.0)),
    ("nlinear_L96_a10",   lambda: NLinear(input_length=96, ridge_alpha=10.0)),
    ("nlinear_L96_a100",  lambda: NLinear(input_length=96, ridge_alpha=100.0)),
    ("nlinear_L336_a1",   lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10",  lambda: NLinear(input_length=336, ridge_alpha=10.0)),
    ("nlinear_L720_a1",   lambda: NLinear(input_length=720, ridge_alpha=1.0)),
    ("dlinear_L96_k25_a0",  lambda: DLinear(input_length=96, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L96_k49_a0",  lambda: DLinear(input_length=96, kernel_size=49, ridge_alpha=0.0)),
    ("dlinear_L336_k25_a0", lambda: DLinear(input_length=336, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L336_k49_a0", lambda: DLinear(input_length=336, kernel_size=49, ridge_alpha=0.0)),
    ("rlinear_L96_a0",    lambda: RLinear(input_length=96, ridge_alpha=0.0)),
    ("rlinear_L336_a0",   lambda: RLinear(input_length=336, ridge_alpha=0.0)),
]

def fit_stack_map(P, A, alpha, fit_intercept=False):
    n,m,h=P.shape; coef=np.empty((m,h)); inter=np.zeros(h)
    for k in range(h):
        r=Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:,:,k], A[:,k]); coef[:,k]=r.coef_
    class _Map:
        def predict(self, Pt): return np.einsum("mh,nmh->nh", coef, Pt) + inter[None,:]
    _Map.coef_=coef; _Map.inter_=inter
    return _Map()

def score_fast(P_val, A_val, idx, alpha=SEARCH_ALPHA):
    if len(idx)==0: return float("inf")
    if len(idx)==1:
        n=len(A_val); n2=n//2
        return float(np.mean(np.mean(np.abs(P_val[n2:, idx[0], :]-A_val[n2:]),axis=1)))
    Psub=P_val[:, idx, :]; n=len(A_val); n2=n//2
    r=fit_stack_map(Psub[:n2], A_val[:n2], alpha)
    return float(np.mean(np.mean(np.abs(r.predict(Psub[n2:])-A_val[n2:]),axis=1)))

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
    val_starts=np.arange(n_val)+TRAIN_END
    print(f"collecting P_val {len(CANDIDATES)} univariate linear (val {n_val} origins, members frozen on {TRAIN_END})...")
    P_val=collect_val(train_series, fit_series, val_starts)
    A_val=np.stack([val_series[t:t+HORIZON] for t in range(n_val)])
    for j,(name,_) in enumerate(CANDIDATES):
        mae=float(np.mean(np.mean(np.abs(P_val[:,j,:]-A_val),axis=1)))
        print(f"  {name:20s} val {mae:.4f}")

    single=[score_fast(P_val, A_val, [j]) for j in range(len(CANDIDATES))]
    cur_idx=[int(np.argmin(single))]
    cur_score=single[cur_idx[0]]
    best_idx=list(cur_idx); best_score=cur_score
    ts,_=score_full(P_val, A_val, cur_idx)
    print(f"\ninit singleton {[CANDIDATES[i][0] for i in cur_idx]} fast {cur_score:.4f} true {ts:.4f}")

    tabu=set(); q=collections.deque(maxlen=7)
    def key(idx): return tuple(sorted(idx))
    tabu.add(key(cur_idx)); q.append(key(cur_idx))
    max_iter=25; no_improve=0; trace=[]
    for it in range(max_iter):
        cur_set=set(cur_idx); all_set=set(range(len(CANDIDATES)))
        neigh=[]
        for j in sorted(all_set - cur_set): neigh.append(sorted(cur_set|{j}))
        if len(cur_set)>1:
            for j in sorted(cur_set): neigh.append(sorted(cur_set-{j}))
        for oj in sorted(cur_set):
            for ij in sorted(all_set - cur_set): neigh.append(sorted((cur_set-{oj})|{ij}))
        uniq=[]; seen=set()
        for nb in neigh:
            k=tuple(nb)
            if k not in seen: seen.add(k); uniq.append(nb)
        scored=[(score_fast(P_val, A_val, nb), SEARCH_ALPHA, nb) for nb in uniq]
        scored.sort(key=lambda x: x[0])
        picked=None
        for s,a,nb in scored:
            k=tuple(nb)
            if k not in tabu or s < best_score - 1e-9:
                picked=(s,a,nb); break
        if picked is None: picked=scored[0]
        s,a,nb=picked
        cur_idx=nb; cur_score=s; k=tuple(nb); tabu.add(k); q.append(k)
        improved=s < best_score - 1e-9
        if improved: best_idx=list(nb); best_score=s; no_improve=0
        else: no_improve+=1
        true_s, true_a = score_full(P_val, A_val, nb) if (improved or it%3==0) else (s, SEARCH_ALPHA)
        trace.append({"iter":it,"cur":[CANDIDATES[i][0] for i in nb],"fast":float(s),"true":float(true_s),"alpha":true_a,"best_fast":float(best_score),"best_set":[CANDIDATES[i][0] for i in best_idx]})
        print(f"iter {it:2d} cur {[CANDIDATES[i][0] for i in nb]} fast {s:.4f} true {true_s:.4f} a={true_a} best_fast {best_score:.4f} { [CANDIDATES[i][0] for i in best_idx]}")
        if no_improve>=5:
            print("  no improve 5 iters -> stop"); break

    print(f"\nbest subset fast {best_score:.4f}: {[CANDIDATES[i][0] for i in best_idx]}")
    _, best_alpha = score_full(P_val, A_val, best_idx)
    P_best=P_val[:, best_idx, :]
    stack=fit_stack_map(P_best, A_val, best_alpha if best_alpha is not None else SEARCH_ALPHA)
    val_full=float(np.mean(np.mean(np.abs(stack.predict(P_best)-A_val),axis=1)))
    print(f"refit all val MAE {val_full:.4f} alpha {best_alpha}")

    concat=np.concatenate([fit_series, test_series])
    disj_starts=np.array([len(fit_series)+s for s in DISJOINT_STARTS])
    P_disj_all=collect_test(fit_series, concat, disj_starts)
    P_disj=P_disj_all[:, best_idx, :]
    A_disj=np.stack([test_series[s:s+HORIZON] for s in DISJOINT_STARTS])
    preds_disj=stack.predict(P_disj)
    mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)
    n_test=len(test_series)-HORIZON+1
    test_starts=np.arange(n_test)+len(fit_series)
    P_test_all=collect_test(fit_series, concat, test_starts)
    P_test=P_test_all[:, best_idx, :]
    A_test=np.stack([test_series[t:t+HORIZON] for t in range(n_test)])
    preds_full=stack.predict(P_test)
    mae_full, rmse_full, _, _ = rolling_metrics(preds_full, A_test)
    for j,i in enumerate(best_idx):
        m=float(np.mean(np.mean(np.abs(P_test[:,j,:]-A_test),axis=1)))
        print(f"  member {CANDIDATES[i][0]:20s} full {m:.4f}")
    print(f"\nS-20 incumbent 1.9980")
    print(f"S-26 best disjoint {mae_disj:.4f} full {mae_full:.4f} (delta {mae_full-1.9980:+.4f})")
    out={"slice":"S-26-greedy-linear","pool":[n for n,_ in CANDIDATES],"trace":trace,"best_subset":[CANDIDATES[i][0] for i in best_idx],"best_idx":best_idx,"best_fast":best_score,"best_alpha":best_alpha,"val_full":val_full,"test_disjoint":{"mae":mae_disj,"rmse":rmse_disj},"test_full":{"mae":mae_full,"rmse":rmse_full,"n":n_test,"delta_vs_s20":mae_full-1.9980},"protocol":"S-20-clean: val members frozen on 8545, test members refrozen on 11425"}
    with open(HERE/"results_s26.json","w") as f: json.dump(out,f,indent=2)
    print(f"\nwrote {HERE/'results_s26.json'} elapsed {time.time()-t_all:.1f}s")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
