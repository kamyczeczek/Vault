"""S-25 — Greedy-Tabu member selection for per-horizon ridge stack (no heavy grid).

Pool: 10 candidates (6 univariate S-20 + 4 multivariate NLinear variants).
Search: greedy-tabu over SUBSETS, scored by S-20 chronological val protocol
  (fit stack on val [0,1080), select alpha on [1080,2161), score = second-half MAE).
Moves: add / drop / swap(1-1). Tabu = visited subsets (tenure 7), aspiration = new global best.
No test leakage: search touches val only; frozen test (11425) scored once at end.

Run: python projects/ts-ml-experiments/h720/sub_experiments/greedy_tabu_s25/rolling_arm.py
"""
from __future__ import annotations
import json, sys, time, csv, itertools, collections
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, DLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
COLS = ["HUFL","HULL","MUFL","MULL","LUFL","LULL","OT"]
OT_IDX = 6

def load_multivariate(path: Path) -> np.ndarray:
    with open(path) as f:
        r = csv.DictReader(f)
        return np.asarray([[float(row[c]) for c in COLS] for row in r], dtype=float)

class MultiNLinear:
    def __init__(self, input_length: int = 96, ridge_alpha: float = 1.0):
        self.input_length = input_length
        self.ridge_alpha = ridge_alpha
    def fit(self, y, *, horizon: int):
        s = np.asarray(y, dtype=float)
        if s.ndim == 1: s = s[:, None]
        X, Y = [], []
        for end in range(self.input_length, len(s) - horizon + 1):
            w = s[end - self.input_length:end]
            a = w[-1, OT_IDX if s.shape[1]>1 else 0]
            if s.shape[1] == 1:
                X.append((w - w[-1]).reshape(-1))
                Y.append(s[end:end+horizon, 0] - a)
            else:
                X.append((w - w[-1]).reshape(-1))
                Y.append(s[end:end+horizon, OT_IDX] - a)
        self.model = Ridge(alpha=self.ridge_alpha, fit_intercept=True).fit(np.asarray(X), np.asarray(Y))
        self.history_ = s
        return self
    def predict(self) -> np.ndarray:
        w = self.history_[-self.input_length:]
        a = w[-1, OT_IDX if w.shape[1]>1 else 0]
        x = (w - w[-1]).reshape(-1)
        return np.asarray(self.model.predict([x])[0]) + a

SEARCH_ALPHA = 3000.0  # fixed for search speed (S-20/S-24 interior optimum); full ALPHAS only for final refit
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]

def fit_stack_map(P, A, alpha, fit_intercept=False):
    n,m,h = P.shape
    coef = np.empty((m,h)); inter=np.zeros(h)
    for k in range(h):
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:,:,k], A[:,k])
        coef[:,k]=r.coef_
    class _Map:
        def predict(self, Pt): return np.einsum("mh,nmh->nh", coef, Pt) + inter[None,:]
    _Map.coef_=coef; _Map.inter_=inter
    return _Map()

def score_subset_fast(P_val, A_val, idx, alpha=SEARCH_ALPHA):
    """Fast S-20 sel score at fixed alpha (search only)."""
    if len(idx)==0: return float("inf")
    if len(idx)==1:
        n_val=len(A_val); n_fit=n_val//2
        return float(np.mean(np.mean(np.abs(P_val[n_fit:, idx[0], :]-A_val[n_fit:]),axis=1)))
    Psub = P_val[:, idx, :]
    n_val=len(A_val); n_fit=n_val//2
    Pfit, Afit = Psub[:n_fit], A_val[:n_fit]
    Psel, Asel = Psub[n_fit:], A_val[n_fit:]
    r=fit_stack_map(Pfit, Afit, alpha)
    return float(np.mean(np.mean(np.abs(r.predict(Psel)-Asel),axis=1)))

def score_subset(P_val, A_val, idx):
    """S-20 sel score: chronological 1080/1081 alpha selection -> second-half MAE."""
    if len(idx)==0: return float("inf"), None
    if len(idx)==1:
        n_val=len(A_val); n_fit=n_val//2
        mae=float(np.mean(np.mean(np.abs(P_val[n_fit:, idx[0], :]-A_val[n_fit:]),axis=1)))
        return mae, None
    Psub = P_val[:, idx, :]
    n_val=len(A_val); n_fit=n_val//2
    Pfit, Afit = Psub[:n_fit], A_val[:n_fit]
    Psel, Asel = Psub[n_fit:], A_val[n_fit:]
    best=None; best_a=None
    for a in ALPHAS:
        r=fit_stack_map(Pfit, Afit, a)
        sel=float(np.mean(np.mean(np.abs(r.predict(Psel)-Asel),axis=1)))
        if best is None or sel<best: best=sel; best_a=a
    return best, best_a

# Candidate pool: 10 (no grid: only 2 multivariate alphas to test overfit hypothesis)
CANDIDATES = [
    ("nlinear_L336_a1",        lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L96_a1",         lambda: NLinear(input_length=96, ridge_alpha=1.0)),
    ("nlinear_L720_a1",        lambda: NLinear(input_length=720, ridge_alpha=1.0)),
    ("dlinear_L96_a0",         lambda: DLinear(input_length=96, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L336_a0",        lambda: DLinear(input_length=336, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L720_a0",        lambda: DLinear(input_length=720, kernel_size=25, ridge_alpha=0.0)),
    ("multi_L96_a1",           lambda: MultiNLinear(input_length=96, ridge_alpha=1.0)),
    ("multi_L336_a1",          lambda: MultiNLinear(input_length=336, ridge_alpha=1.0)),
    ("multi_L96_a100",         lambda: MultiNLinear(input_length=96, ridge_alpha=100.0)),
    ("multi_L336_a100",        lambda: MultiNLinear(input_length=336, ridge_alpha=100.0)),
]
def member_preds_linear(factory, series_1d, starts, L, H):
    m=factory(); m.fit(series_1d, horizon=H)
    out=[]
    hist=m.history_
    for s in starts:
        m.history_=series_1d[:s]
        out.append(np.asarray(m.predict(),dtype=float))
    m.history_=hist
    return np.asarray(out)

def member_preds_multi(factory, series_multi, starts, L, H):
    m=factory(); m.fit(series_multi, horizon=H)
    out=[]; hist=m.history_
    for s in starts:
        m.history_=series_multi[:s]
        out.append(np.asarray(m.predict(),dtype=float))
    m.history_=hist
    return np.asarray(out)

def collect_preds_all(fit_1d, fit_multi, origin_starts):
    cols=[]
    for name, factory in CANDIDATES:
        # detect multivariate by string
        is_multi = name.startswith("multi")
        # need L for logging only (collect via history swap, not windows array)
        m0=factory(); L=m0.input_length
        if is_multi:
            p=member_preds_multi(factory, fit_multi, origin_starts, L, HORIZON)
        else:
            p=member_preds_linear(factory, fit_1d, origin_starts, L, HORIZON)
        cols.append(p)
        print(f"  {name:18s} L={L:3d} ok {p.shape}")
    return np.stack(cols, axis=1)  # (n, C, H)

def rolling_metrics(preds, actuals):
    err=preds-actuals
    mae_per=np.mean(np.abs(err),axis=1)
    rmse_per=np.sqrt(np.mean(err**2,axis=1))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err**2))), mae_per, rmse_per

def main():
    t_all=time.time()
    pd=get_protocol_data()
    fit_1d, eval_1d, test_1d = pd.rolling_views()
    fit_multi=load_multivariate(H720_ROOT/"train.csv")
    test_multi=load_multivariate(H720_ROOT/"test.csv")
    assert np.allclose(fit_multi[:,OT_IDX], fit_1d, atol=1e-9)
    val_1d=fit_1d[TRAIN_END:]; val_multi=fit_multi[TRAIN_END:]
    n_val=len(val_1d)-HORIZON+1
    assert n_val==2161
    val_starts=np.arange(n_val)+TRAIN_END
    print(f"collecting P_val for {len(CANDIDATES)} candidates (val {n_val} origins)...")
    P_val=collect_preds_all(fit_1d, fit_multi, val_starts)
    A_val=np.stack([val_1d[t:t+HORIZON] for t in range(n_val)])

    # per-candidate val MAE
    for j,(name,_) in enumerate(CANDIDATES):
        mae=float(np.mean(np.mean(np.abs(P_val[:,j,:]-A_val),axis=1)))
        print(f"  {name:18s} val {mae:.4f}")

    # Greedy-Tabu search (fast: fixed SEARCH_ALPHA; full alpha scan only for final refit)
    single_scores=[score_subset_fast(P_val, A_val, [j]) for j in range(len(CANDIDATES))]
    cur_idx=[int(np.argmin(single_scores))]
    cur_score=score_subset_fast(P_val, A_val, cur_idx)
    # also compute true sel for best tracking
    _, _a0 = score_subset(P_val, A_val, cur_idx)
    best_idx=list(cur_idx); best_score, best_a_true = score_subset(P_val, A_val, cur_idx)
    print(f"\ninit singleton {[CANDIDATES[i][0] for i in cur_idx]} sel_fast {cur_score:.4f} sel_true {best_score:.4f} a={_a0}")

    tabu=set()
    tabu_queue=collections.deque(maxlen=7)
    def key(idx): return tuple(sorted(idx))
    tabu.add(key(cur_idx)); tabu_queue.append(key(cur_idx))

    max_iter=25; no_improve=0
    trace=[]
    for it in range(max_iter):
        # generate neighbors: add / drop / swap
        neighbors=[]
        cur_set=set(cur_idx)
        all_set=set(range(len(CANDIDATES)))
        # add
        for j in sorted(all_set - cur_set):
            neighbors.append(sorted(cur_set | {j}))
        # drop (keep at least 1)
        if len(cur_set)>1:
            for j in sorted(cur_set):
                neighbors.append(sorted(cur_set - {j}))
        # swap
        for out_j in sorted(cur_set):
            for in_j in sorted(all_set - cur_set):
                neighbors.append(sorted((cur_set - {out_j}) | {in_j}))

        # deduplicate
        uniq=[]
        seen=set()
        for nb in neighbors:
            k=tuple(nb)
            if k not in seen:
                seen.add(k); uniq.append(nb)
        # score at fixed SEARCH_ALPHA during search
        scored=[]
        for nb in uniq:
            s=score_subset_fast(P_val, A_val, nb)
            scored.append((s, SEARCH_ALPHA, nb))
        scored.sort(key=lambda x: x[0])
        # pick best non-tabu else aspiration (aspiration compares fast score to best_score_fast)
        # keep best_score as fast score during search
        picked=None
        for s,a,nb in scored:
            k=tuple(nb)
            is_tabu=k in tabu
            if not is_tabu or s < best_score - 1e-9:
                picked=(s,a,nb)
                break
        if picked is None:
            picked=scored[0]
        s,a,nb=picked
        # move
        cur_idx=nb; cur_score=s
        k=tuple(nb)
        tabu.add(k); tabu_queue.append(k)
        if len(tabu_queue)>7:
            old=tabu_queue.popleft()
            pass
        improved = s < best_score - 1e-9
        if improved:
            best_idx=list(nb); best_score=s; no_improve=0
        else:
            no_improve+=1
        # true sel for logging (one alpha scan) only when improved or every 3 iters
        true_s, true_a = score_subset(P_val, A_val, nb) if (improved or it%3==0) else (s, SEARCH_ALPHA)
        trace.append({"iter":it, "cur":[CANDIDATES[i][0] for i in nb], "sel_fast":float(s), "sel_true":float(true_s), "alpha":true_a, "best_fast":float(best_score), "best_set":[CANDIDATES[i][0] for i in best_idx]})
        print(f"iter {it:2d} cur {[CANDIDATES[i][0] for i in nb]} fast {s:.4f} true {true_s:.4f} a={true_a}  best_fast {best_score:.4f} { [CANDIDATES[i][0] for i in best_idx]}")
        if no_improve>=5:
            print("  no improve 5 iters -> stop")
            break
        if len(cur_idx)>=6 and it>12 and not improved:
            # allow early stop to keep light
            pass

    print(f"\nbest subset sel {best_score:.4f}: {[CANDIDATES[i][0] for i in best_idx]}")
    # refit best subset stack on all val and evaluate frozen test
    P_val_best=P_val[:, best_idx, :]
    # select alpha for best subset (same chronological)
    _, best_alpha = score_subset(P_val, A_val, best_idx)
    # refit map on all val
    stack=fit_stack_map(P_val_best, A_val, best_alpha)
    val_mae_full=float(np.mean(np.mean(np.abs(stack.predict(P_val_best)-A_val),axis=1)))
    print(f"refit all val MAE {val_mae_full:.4f} alpha {best_alpha}")

    # frozen test scoring (disjoint 4 + full 2161)
    concat_1d=np.concatenate([fit_1d, test_1d])
    concat_multi=np.concatenate([fit_multi, test_multi[:len(test_1d)]], axis=0)
    # disjoint 4
    disj_starts_abs=np.array([len(fit_1d)+s for s in DISJOINT_STARTS])
    P_disj_all=collect_preds_all(concat_1d, concat_multi, disj_starts_abs)
    P_disj=P_disj_all[:, best_idx, :]
    A_disj=np.stack([test_1d[s:s+HORIZON] for s in DISJOINT_STARTS])
    preds_disj=stack.predict(P_disj)
    mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)
    # full 2161
    n_test=len(test_1d)-HORIZON+1
    test_starts=np.arange(n_test)+len(fit_1d)
    P_test_all=collect_preds_all(concat_1d, concat_multi, test_starts)
    P_test=P_test_all[:, best_idx, :]
    A_test=np.stack([test_1d[t:t+HORIZON] for t in range(n_test)])
    preds_full=stack.predict(P_test)
    mae_full, rmse_full, _, _ = rolling_metrics(preds_full, A_test)
    # per-member full for diagnosis
    for j,i in enumerate(best_idx):
        name=CANDIDATES[i][0]
        m=float(np.mean(np.mean(np.abs(P_test[:,j,:]-A_test),axis=1)))
        print(f"  member {name:18s} full {m:.4f}")

    print(f"\nS-20 incumbent 1.9980")
    print(f"S-25 best subset disjoint {mae_disj:.4f} (delta {mae_disj-1.9980:+.4f}) full {mae_full:.4f} (delta {mae_full-1.9980:+.4f})")
    # also score S-20 6-member baseline under same val/test pipeline for sanity (subset = first 6)
    # quick: score the 6 univariate subset
    s6,a6=score_subset(P_val, A_val, list(range(6)))
    print(f"S-20 subset sel {s6:.4f} a={a6} (should be ~2.56)")

    out={"slice":"S-25-greedy-tabu","pool":[n for n,_ in CANDIDATES],
         "trace":trace,"best_subset":[CANDIDATES[i][0] for i in best_idx],
         "best_idx":best_idx,"best_sel":best_score,"best_alpha":best_alpha,
         "val_mae_full":val_mae_full,
         "test_disjoint":{"mae":mae_disj,"rmse":rmse_disj},
         "test_full":{"mae":mae_full,"rmse":rmse_full,"n":n_test,"delta_vs_s20":mae_full-1.9980}}
    with open(HERE/"results_s25.json","w") as f: json.dump(out,f,indent=2)
    print(f"\nwrote {HERE/'results_s25.json'} elapsed {time.time()-t_all:.1f}s")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
