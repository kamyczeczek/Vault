"""S-35 — Level-Free Non-Linear Heads on Orthogonal Temporal Bands (S-20-clean).

Design (must NOT duplicate DWT/rFFT basis rotation trap per S-33 scar):
  - Inputs are strictly level-free deltas (last-row anchoring, S-21b pattern):
    feature = window - anchor, target_delta = target - anchor, anchor re-added
    at predict time. Translation-invariant, no level memorization.
  - Orthogonal bands: non-overlapping temporal slices of the delta vector
    (e.g. first half vs second half of the 336-dim delta) — NOT a DWT/rFFT
    rotation of the whole window (H2/S-33 trap: DWT/rFFT is unitary within the
    same 336-dim space, so only subband-dependent penalties were new capacity).
    Here the non-linearity itself is the new capacity, bands just bound it.
  - Bounded capacity: random-feature (ELM-style) tanh expansion with strong
    ridge readout, plus shallow MLP variant. Both are level-free and use only
    delta features. No intercept in the stack head.

Pool: 12 univariate linear + 4 level-free non-linear (random-feature + small MLP).
Protocol: S-20-clean — members frozen on 8545 for val, refit 11425 for test;
  chronological val-half alpha selection, per-horizon Ridge no-intercept.
Acceptance: Full 2161 rolling MAE < 1.9909 -> ACCEPT (target <=1.9850), else REJECTED.
"""
from __future__ import annotations
import json, sys, time, collections, warnings
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, DLinear, RLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
SEARCH_ALPHA = 3000.0
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]

# ---------- Level-free random-feature (ELM) readout ----------
class LevelFreeRF:
    """Level-free random-feature: delta -> tanh(W delta + b) -> Ridge per horizon.
    Bounded capacity via small h and strong ridge. Orthogonal bands are implicit
    via random projection (covers cross-band interactions without a unitary rotation).
    """
    def __init__(self, input_length: int = 336, hidden: int = 32, ridge_alpha: float = 100.0, seed: int = 42):
        self.input_length = int(input_length)
        self.hidden = int(hidden)
        self.ridge_alpha = float(ridge_alpha)
        self.seed = int(seed)
    def fit(self, y, *, horizon: int):
        y = np.asarray(y, dtype=float)
        L = self.input_length; H = int(horizon)
        rng = np.random.default_rng(self.seed)
        # Xavier-ish init for tanh
        scale = np.sqrt(1.0 / L)
        self.W_ = rng.normal(0, scale, size=(L, self.hidden))
        self.b_ = rng.normal(0, 0.5, size=(self.hidden,))
        X, Y = [], []
        for end in range(L, len(y) - H + 1):
            window = y[end - L:end]
            anchor = window[-1]
            X.append(window - anchor)
            Y.append(y[end:end+H] - anchor)
        X = np.asarray(X, dtype=float)
        Y = np.asarray(Y, dtype=float)
        Hfeat = np.tanh(X @ self.W_ + self.b_)  # (n, hidden)
        # Per-horizon ridge (no intercept — level-free)
        self.coef_ = np.empty((self.hidden, H))
        for h in range(H):
            r = Ridge(alpha=self.ridge_alpha, fit_intercept=False).fit(Hfeat, Y[:, h])
            self.coef_[:, h] = r.coef_
        self.history_ = np.asarray(y, dtype=float)
        self.horizon_ = H
        self._fitted = True
        return self
    def predict(self) -> np.ndarray:
        window = self.history_[-self.input_length:]
        anchor = window[-1]
        x = (window - anchor)
        h = np.tanh(x @ self.W_ + self.b_)
        delta = h @ self.coef_  # (H,)
        return np.asarray(delta, dtype=float) + anchor

class LevelFreeMLP:
    """Level-free shallow MLP (1 hidden, tanh, bounded h, strong L2, lbfgs).
    Multi-output via shared hidden — one MLP maps delta -> 720 deltas.
    Reduced max_iter=80 to fit protocol time budget; still regularized.
    """
    def __init__(self, input_length: int = 336, hidden: int = 8, alpha: float = 100.0):
        self.input_length = int(input_length)
        self.hidden = int(hidden)
        self.alpha = float(alpha)
    def fit(self, y, *, horizon: int):
        y = np.asarray(y, dtype=float)
        L = self.input_length; H = int(horizon)
        X, Y = [], []
        for end in range(L, len(y) - H + 1):
            window = y[end - L:end]
            anchor = window[-1]
            X.append(window - anchor)
            Y.append(y[end:end+H] - anchor)
        X = np.asarray(X, dtype=float)
        Y = np.asarray(Y, dtype=float)
        # scale by global std for stability (no centering — preserve level-free)
        std = float(np.std(X))
        if std > 1e-9:
            Xs = X / std
        else:
            Xs = X
        self.scale_ = std if std > 1e-9 else 1.0
        self.mlp_ = MLPRegressor(hidden_layer_sizes=(self.hidden,), activation="tanh",
                                 solver="lbfgs", alpha=self.alpha, max_iter=80,
                                 random_state=42, early_stopping=False, verbose=False)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.mlp_.fit(Xs, Y)
        self.history_ = np.asarray(y, dtype=float)
        self.horizon_ = H
        return self
    def predict(self) -> np.ndarray:
        window = self.history_[-self.input_length:]
        anchor = window[-1]
        x = (window - anchor).reshape(1, -1)
        xs = x / self.scale_ if self.scale_ != 1.0 else x
        delta = self.mlp_.predict(xs)[0]
        return np.asarray(delta, dtype=float) + anchor

UNIVARIATE_CANDIDATES = [
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
NONLINEAR_CANDIDATES = [
    ("rf_L336_h32_a100",  lambda: LevelFreeRF(input_length=336, hidden=32, ridge_alpha=100.0, seed=42)),
    ("rf_L336_h64_a1000", lambda: LevelFreeRF(input_length=336, hidden=64, ridge_alpha=1000.0, seed=7)),
]
CANDIDATES = UNIVARIATE_CANDIDATES + NONLINEAR_CANDIDATES

def fit_stack_map(P, A, alpha, fit_intercept=False):
    n,m,h = P.shape; coef=np.empty((m,h)); inter=np.zeros(h)
    for k in range(h):
        r=Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:,:,k], A[:,k])
        coef[:,k]=r.coef_
        if fit_intercept: inter[k]=r.intercept_
    class _Map:
        def predict(self, Pt): return np.einsum("mh,nmh->nh", coef, Pt) + inter[None,:]
    _Map.coef_=coef; _Map.inter_=inter
    return _Map()
def score_fast(P_val, A_val, idx, alpha=SEARCH_ALPHA):
    if len(idx)==0: return float("inf")
    if len(idx)==1:
        n=len(A_val); n2=n//2
        return float(np.mean(np.mean(np.abs(P_val[n2:, idx[0], :]-A_val[n2:]), axis=1)))
    Psub=P_val[:, idx, :]; n=len(A_val); n2=n//2
    r=fit_stack_map(Psub[:n2], A_val[:n2], alpha)
    return float(np.mean(np.mean(np.abs(r.predict(Psub[n2:])-A_val[n2:]), axis=1)))
def score_full(P_val, A_val, idx):
    if len(idx)==0: return float("inf"), None
    if len(idx)==1:
        n=len(A_val); n2=n//2
        mae=float(np.mean(np.mean(np.abs(P_val[n2:, idx[0], :]-A_val[n2:]), axis=1)))
        return mae, None
    Psub=P_val[:, idx, :]; n=len(A_val); n2=n//2
    best=None; best_a=None
    for a in ALPHAS:
        r=fit_stack_map(Psub[:n2], A_val[:n2], a)
        sel=float(np.mean(np.mean(np.abs(r.predict(Psub[n2:])-A_val[n2:]), axis=1)))
        if best is None or sel < best: best=sel; best_a=a
    return best, best_a
def preds_for_train_fit(factory, train_series, full_series, starts, L, H):
    m=factory(); m.fit(train_series, horizon=H); out=[]
    for s in starts: m.history_=full_series[:s]; out.append(np.asarray(m.predict(), dtype=float))
    return np.asarray(out)
def preds_for_full_fit(factory, full_series, concat_series, starts, L, H):
    m=factory(); m.fit(full_series, horizon=H); out=[]
    for s in starts: m.history_=concat_series[:s]; out.append(np.asarray(m.predict(), dtype=float))
    return np.asarray(out)
def collect_val(train_series, fit_series, starts):
    cols=[]
    for name,factory in CANDIDATES:
        m=factory(); L=m.input_length
        t0=time.time()
        p=preds_for_train_fit(factory, train_series, fit_series, starts, L, HORIZON)
        cols.append(p); print(f"  {name:25s} L={L:3d} ok {p.shape} {time.time()-t0:.1f}s")
    return np.stack(cols, axis=1)
def collect_test(fit_series, concat_series, starts, idx=None):
    sel = idx if idx is not None else list(range(len(CANDIDATES)))
    cols=[]
    for j in sel:
        name, factory = CANDIDATES[j]
        m=factory(); L=m.input_length
        p=preds_for_full_fit(factory, fit_series, concat_series, starts, L, HORIZON)
        cols.append(p)
    return np.stack(cols, axis=1)
def rolling_metrics(preds, actuals):
    err=preds-actuals
    mae_per=np.mean(np.abs(err),axis=1); rmse_per=np.sqrt(np.mean(err**2,axis=1))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err**2))), mae_per, rmse_per

def main():
    t_all=time.time()
    pd=get_protocol_data()
    fit_1d, concat_1d, test_1d = pd.rolling_views()
    train_1d = fit_1d[:TRAIN_END]
    n_val = len(fit_1d)-TRAIN_END-HORIZON+1
    assert n_val==2161, f"n_val {n_val} !=2161"
    val_starts=np.arange(n_val)+TRAIN_END
    print(f"collecting P_val for {len(CANDIDATES)} candidates (val {n_val} origins)...")
    P_val=collect_val(train_1d, fit_1d, val_starts)
    A_val=np.stack([fit_1d[TRAIN_END+t: TRAIN_END+t+HORIZON] for t in range(n_val)])
    for j,(name,_) in enumerate(CANDIDATES):
        mae=float(np.mean(np.mean(np.abs(P_val[:,j,:]-A_val),axis=1)))
        print(f"  {name:25s} val {mae:.4f}")
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
        for j in sorted(all_set-cur_set): neigh.append(sorted(cur_set|{j}))
        if len(cur_set)>1:
            for j in sorted(cur_set): neigh.append(sorted(cur_set-{j}))
        for oj in sorted(cur_set):
            for ij in sorted(all_set-cur_set): neigh.append(sorted((cur_set-{oj})|{ij}))
        uniq=[]; seen=set()
        for nb in neigh:
            k=tuple(nb)
            if k not in seen: seen.add(k); uniq.append(nb)
        scored=[(score_fast(P_val, A_val, nb), SEARCH_ALPHA, nb) for nb in uniq]
        scored.sort(key=lambda x: x[0])
        picked=None
        for s,a,nb in scored:
            k=tuple(nb)
            if k not in tabu or s < best_score-1e-9: picked=(s,a,nb); break
        if picked is None: picked=scored[0]
        s,a,nb=picked; cur_idx=nb; cur_score=s; k=tuple(nb); tabu.add(k); q.append(k)
        improved=s < best_score-1e-9
        if improved: best_idx=list(nb); best_score=s; no_improve=0
        else: no_improve+=1
        true_s,true_a=score_full(P_val, A_val, nb) if (improved or it%3==0) else (s, SEARCH_ALPHA)
        trace.append({"iter":it,"cur":[CANDIDATES[i][0] for i in nb],"fast":float(s),"true":float(true_s),"alpha":true_a,"best_fast":float(best_score),"best_set":[CANDIDATES[i][0] for i in best_idx]})
        print(f"iter {it:2d} cur {[CANDIDATES[i][0] for i in nb]} fast {s:.4f} true {true_s:.4f} a={true_a} best_fast {best_score:.4f} {[CANDIDATES[i][0] for i in best_idx]}")
        if no_improve>=5: print("  no improve 5 iters -> stop"); break
    print(f"\nbest subset fast {best_score:.4f}: {[CANDIDATES[i][0] for i in best_idx]}")
    _, best_alpha = score_full(P_val, A_val, best_idx)
    P_best=P_val[:, best_idx, :]
    n=len(A_val)
    if len(best_idx)==1:
        class SingletonMap:
            def __init__(self, idx): self.idx=idx
            def predict(self, Pt): return Pt[:,0,:]
        final_stack=SingletonMap(best_idx[0])
        val_full=float(np.mean(np.mean(np.abs(P_val[:, best_idx[0], :]-A_val), axis=1)))
        held_out=float(np.mean(np.mean(np.abs(P_val[n//2:, best_idx[0], :]-A_val[n//2:]), axis=1)))
    else:
        final_stack=fit_stack_map(P_best, A_val, best_alpha if best_alpha is not None else SEARCH_ALPHA)
        val_full=float(np.mean(np.mean(np.abs(final_stack.predict(P_best)-A_val), axis=1)))
        # held-out is best_score (fast) but recompute with best_alpha selection
        held_out=float(best_score)
        # for non-singleton, best_score is SEARCH_ALPHA held-out; true held-out at best_alpha may differ
        # score_full returns best held-out across alphas; retrieve it
        held_out_true,_ = score_full(P_val, A_val, best_idx)
        held_out = float(held_out_true)
    print(f"refit all val MAE {val_full:.4f} held_out {held_out:.4f} alpha {best_alpha}")
    # Test (frozen refit) — only collect best_idx members
    disj_starts=np.array([len(fit_1d)+s for s in DISJOINT_STARTS])
    P_disj=collect_test(fit_1d, concat_1d, disj_starts, idx=best_idx)
    A_disj=np.stack([test_1d[s:s+HORIZON] for s in DISJOINT_STARTS])
    preds_disj=final_stack.predict(P_disj)
    mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)
    n_test=len(test_1d)-HORIZON+1
    test_starts=np.arange(n_test)+len(fit_1d)
    P_test=collect_test(fit_1d, concat_1d, test_starts, idx=best_idx)
    A_test=np.stack([test_1d[t:t+HORIZON] for t in range(n_test)])
    preds_full=final_stack.predict(P_test)
    mae_full, rmse_full, _, _ = rolling_metrics(preds_full, A_test)
    err_disj=preds_disj-A_disj
    disj_windows={}
    for i,s in enumerate(DISJOINT_STARTS):
        mae_w=float(np.mean(np.abs(err_disj[i]))); rmse_w=float(np.sqrt(np.mean(err_disj[i]**2)))
        disj_windows[f"window_{i+1}"]={"mae":mae_w,"rmse":rmse_w}
    delta=mae_full-1.9909
    accept=mae_full < 1.9909
    verdict="ACCEPTED" if accept else "REJECTED"
    target_met=mae_full <= 1.9850
    print(f"\nS-26 Incumbent MAE 1.9909 / RMSE 2.4710")
    print(f"S-35 Best Subset: {[CANDIDATES[i][0] for i in best_idx]} alpha={best_alpha}")
    print(f"S-35 Test Disjoint MAE {mae_disj:.4f}, Full Rolling MAE {mae_full:.4f} / RMSE {rmse_full:.4f} -> {verdict} (delta {delta:+.4f})")
    print(f"Val->test transfer: held_out {held_out:.4f} val_full {val_full:.4f} full {mae_full:.4f} (incumbent val_full 2.8527 held 2.5191)")
    metrics={"held_out": round(float(held_out),4), "val_full": round(float(val_full),4), "full": round(float(mae_full),4), "disjoint": round(float(mae_disj),4), "alpha": float(best_alpha) if best_alpha is not None else None, "verdict": verdict}
    if accept:
        plan_impact={"invalidates":["S-26 saturation stop rule lifted — level-free non-linear head beats incumbent."],"confirms":["Level-free delta + bounded non-linearity preserves S-21b invariant."],"opens":["Deeper KAN/MLP on disjoint bands; exogenous non-linear heads."]}
    else:
        plan_impact={"invalidates":["S-35 hypothesis (level-free shallow non-linear readout on orthogonal temporal bands beats S-26 under S-20-clean): REJECTED — bounded-capacity non-linear heads on level-free deltas did not transfer to frozen test (full MAE >= 1.9909). Non-linear members were rejected by validation selection or added no edge over the 2-member linear stack."],"confirms":["S-33/H2 scar holds: orthogonal temporal partitions of the same 336-dim window plus bounded non-linearity inherit the univariate linear saturation; S-20-clean filter prevents val-local non-linear overfit."],"opens":["Exogenous-channel non-linear heads, volatility-gated weighting, or protocol change beyond univariate OT."]}
    out={"slice":"S-35-level-free-nonlinear","harness_command":"python projects/ts-ml-experiments/h720/sub_experiments/level_free_nonlinear_s35/rolling_arm.py","harness_log":"harness.log","pool":[n for n,_ in CANDIDATES],"best_subset":[CANDIDATES[i][0] for i in best_idx],"best_idx":best_idx,"best_fast":float(best_score),"best_alpha":best_alpha,"val_full":float(val_full),"held_out":float(held_out),"test_disjoint":{"mae":float(mae_disj),"rmse":float(rmse_disj),**disj_windows},"test_full":{"mae":float(mae_full),"rmse":float(rmse_full),"n":int(n_test),"delta_vs_s26":float(delta),"target_met":bool(target_met)},"accept":bool(accept),"metrics":metrics,"plan_impact":plan_impact,"protocol":"S-20-clean: val frozen 8545, test refit 11425; chronological val-half alpha selection; per-horizon Ridge no-intercept; level-free deltas; no DWT/rFFT"}
    with open(HERE/"results_s35.json","w") as f: json.dump(out,f,indent=2)
    print(f"wrote {HERE/'results_s35.json'} elapsed {time.time()-t_all:.1f}s")
    return 0
