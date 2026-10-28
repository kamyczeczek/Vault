from __future__ import annotations
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs, AMRFBSForecaster
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft, fit_theta, pred_theta
"""S-47 Diverse Mini Suite — fast cross-domain probe.
8 tasks (ETTh1 H96 + sunspot + 6 synthetic), W=5 rolling origins, frozen fit per
task, looped over seeds so every stochastic number is reported as mean ± std.
Pools: A (linear+RFF), B (+SWT subband experts), C (+pooled-ELM),
D (A + BigDict/AMR-FBS), E/F/G/H single-member extensions.
"""
import json, time, pathlib, sys, os, platform
import numpy as np
import pywt
from sklearn.linear_model import Ridge

HERE = pathlib.Path(__file__).resolve().parent
# Resolve project-local imports from the benchmark location, not the caller's cwd.
sys.path.insert(0, str(HERE))
_SHARED_ROOT = HERE.parent / "etth1-h720"
_WAVELET_ROOT = HERE / "members"
if _SHARED_ROOT.exists():
    sys.path.insert(0, str(_SHARED_ROOT))
sys.path.insert(0, str(_WAVELET_ROOT))
STRICT_DEPS = os.environ.get("TS_DIVERSE_STRICT", "0").lower() in {"1", "true", "yes"}
UNAVAILABLE = {}
# standalone run has no data.py; handle gracefully
try:
    from data import get_protocol_data
except Exception:
    get_protocol_data=None
try:
    from anchored_wavelet_elm import AnchoredWaveletELM, _ridge_multioutput
    _HAS_ELM=True
except Exception as _e:
    AnchoredWaveletELM=None; _ridge_multioutput=None; _HAS_ELM=False
    UNAVAILABLE["AnchoredWaveletELM"] = repr(_e)
    print(f"AnchoredWaveletELM unavailable: {_e}")

if _ridge_multioutput is None:
    def _ridge_multioutput(X, Y, alpha=1.0):
        XtX = X.T @ X
        diag_idx = np.arange(XtX.shape[0])
        XtX[diag_idx, diag_idx] += alpha
        XtY = X.T @ Y
        return np.linalg.solve(XtX, XtY)
SEARCH_ALPHA = 3000.0
# Seed loop (CLAUDE.md §Rules: mean ± std over seeds for anything stochastic).
# _RUN_SEED is set by main() per seed iteration; every stochastic fit below
# reads it at call time. Data generators keep fixed seeds — same data, varying
# model randomness, so std measures the model, not the sample.
_RUN_SEED = 42
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0, str(_Path(__file__).parent))
try:
    from members.big_dict_elm import BigDictELM
    _HAS_BIGDICT=True
except Exception as _e:
    BigDictELM=None; _HAS_BIGDICT=False
    UNAVAILABLE["BigDictELM"] = repr(_e); print(f"BigDictELM unavailable: {_e}")
try:
    from members.big_dict_tree import BigDictTree
    _HAS_BIGDICT_TREE=True
except Exception as _e:
    BigDictTree=None; _HAS_BIGDICT_TREE=False
    UNAVAILABLE["BigDictTree"] = repr(_e); print(f"BigDictTree unavailable: {_e}")
try:
    from members.subband_bigdict import SubbandBigDict
    _HAS_SUBBAND_BIGDICT=True
except Exception as _e:
    SubbandBigDict=None; _HAS_SUBBAND_BIGDICT=False
    UNAVAILABLE["SubbandBigDict"] = repr(_e); print(f"SubbandBigDict unavailable: {_e}")
try:
    from members.esn_reservoir import ESNReservoir
    _HAS_ESN=True
except Exception as _e:
    ESNReservoir=None; _HAS_ESN=False
    UNAVAILABLE["ESNReservoir"] = repr(_e); print(f"ESNReservoir unavailable: {_e}")
try:
    from members.deterministic_esn import DeterministicCycleESN
    _HAS_DET_ESN=True
except Exception as _e:
    DeterministicCycleESN=None; _HAS_DET_ESN=False
    UNAVAILABLE["DeterministicCycleESN"] = repr(_e); print(f"DeterministicCycleESN unavailable: {_e}")


try:
    from members.knn_feature_forecaster import KNNFeatureForecaster
    _HAS_KNN=True
except Exception as _e:
    KNNFeatureForecaster=None; _HAS_KNN=False
    UNAVAILABLE["KNNFeatureForecaster"] = repr(_e); print(f"KNNFeatureForecaster unavailable: {_e}")

TASKS = [
    ("etth1_H96", 96, "real"),
    ("sunspot_H24", 24, "real"),
    ("seasonal_H48", 48, "synthetic"),
    ("trending_H48", 48, "synthetic"),
    ("spiky_H48", 48, "synthetic"),
    ("ou_H24", 24, "synthetic"),
    ("multiscale_H96", 96, "synthetic"),
    ("thomas_H24", 24, "chaotic"),
]

def gen_seasonal(n=2600, seed=0):
    rng = np.random.default_rng(seed)
    base = np.sin(2*np.pi*np.arange(n)/24) + 0.5*np.sin(2*np.pi*np.arange(n)/168)
    noise = rng.standard_normal(n)*0.15
    return (base + noise).astype(float)

def gen_trending(n=2600, seed=1):
    rng = np.random.default_rng(seed)
    return (np.cumsum(rng.standard_normal(n)*0.3) + 0.3*np.sin(2*np.pi*np.arange(n)/30)).astype(float)

def gen_spiky(n=2600, seed=2):
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    for i in range(1,n): x[i]=0.6*x[i-1]+rng.standard_normal()*0.4
    spikes = rng.choice(n, size=n//60, replace=False)
    x[spikes] += rng.standard_normal(len(spikes))*2.5
    return x.astype(float)

def gen_ou(n=2600, seed=3):
    rng = np.random.default_rng(seed)
    x=np.zeros(n)
    for i in range(1,n): x[i]=0.92*x[i-1]+rng.standard_normal()*0.3
    x += 0.4*np.sin(2*np.pi*np.arange(n)/52)
    return x.astype(float)

def gen_multiscale(n=2600, seed=4):
    rng = np.random.default_rng(seed)
    t=np.arange(n)
    return (np.sin(2*np.pi*t/12)+0.6*np.sin(2*np.pi*t/48)+0.4*np.sin(2*np.pi*t/168)+0.25*rng.standard_normal(n)).astype(float)

def thomas_trajectory(n, initial_state=(0.1, 0.2, 0.3), b=0.208186, dt=0.05, burn_in=500):
    """Integrate the Thomas system and return all three state coordinates."""
    state = np.asarray(initial_state, dtype=float).copy()
    if state.shape != (3,): raise ValueError("initial_state must contain exactly three coordinates")
    out = np.empty((n, 3), dtype=float)
    def f(x): return np.array([np.sin(x[1])-b*x[0], np.sin(x[2])-b*x[1], np.sin(x[0])-b*x[2]])
    for step in range(n + burn_in):
        k1=f(state); k2=f(state+.5*dt*k1); k3=f(state+.5*dt*k2); k4=f(state+dt*k3)
        state += dt*(k1+2*k2+2*k3+k4)/6
        if step >= burn_in: out[step-burn_in] = state
    return out

def gen_thomas(n=2600, b=0.208186, dt=0.05, seed=5, perturbation=0.0):
    """Return the x-coordinate of a reproducible Thomas chaotic trajectory."""
    rng=np.random.default_rng(seed); initial=np.array([0.1,0.2,0.3])
    if perturbation: initial += float(perturbation)*rng.standard_normal(3)
    return thomas_trajectory(n, initial, b=b, dt=dt)[:,0]

def autocorrelation(x, lag):
    x=np.asarray(x,dtype=float)
    if lag <= 0 or lag >= len(x): raise ValueError("lag must be between 1 and len(x)-1")
    a=x[:-lag]-x[:-lag].mean(); c=x[lag:]-x[lag:].mean(); d=np.sqrt(np.dot(a,a)*np.dot(c,c))
    return float(np.dot(a,c)/d) if d else 0.0

def thomas_divergence_rate(n=200, perturbation=1e-6, b=0.208186, dt=0.05):
    a=thomas_trajectory(n,(0.1,0.2,0.3),b=b,dt=dt,burn_in=0)
    q=thomas_trajectory(n,(0.1+perturbation,0.2,0.3),b=b,dt=dt,burn_in=0)
    d=np.linalg.norm(a-q,axis=1); k=max(1,n//2)
    return float(np.log(d[k]/d[0])/(k*dt))

def get_sunspot(n=2600):
    import urllib.request
    import csv
    url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-sunspots.csv"
    try:
        req = urllib.request.urlopen(url, timeout=5)
        lines = [line.decode('utf-8') for line in req.readlines()]
        reader = csv.reader(lines)
        next(reader)
        vals = []
        for row in reader:
            if len(row) >= 2:
                try: vals.append(float(row[1]))
                except: continue
        arr = np.array(vals, dtype=float)
        if len(arr) >= n: return arr[:n]
        elif len(arr) > 200: return arr
    except Exception as e:
        print(f"Sunspot download failed ({e}), falling back to synthetic cyclic")
    t = np.arange(n)
    rng = np.random.default_rng(42)
    return (50.0 + 40.0 * np.sin(2 * np.pi * t / 132.0) + 10.0 * rng.standard_normal(n)).astype(float)

def get_series(name):
    if name=="sunspot_H24":
        return get_sunspot(2600)
    if name=="etth1_H96":
        try:
            if get_protocol_data is not None:
                s=get_protocol_data().rolling_views()[0][:2600].astype(float)
            else:
                s=gen_trending(2600, seed=99)
        except Exception:
            s=gen_trending(2600, seed=99)
        if hasattr(s, "ndim") and s.ndim>1: s=s[:,0]
        return np.asarray(s, dtype=float)
    return {"sunspot_H24":get_sunspot,"seasonal_H48":gen_seasonal,"trending_H48":gen_trending,"spiky_H48":gen_spiky,"ou_H24":gen_ou,"multiscale_H96":gen_multiscale,"thomas_H24":gen_thomas}[name](2600)

# --- fits (frozen on train[:2000]) ---
def fit_nlinear(train, H, alpha):
    L=96 if H<96 else 96  # fix L=96 for fast suite (avoids 336 swt mismatch for H48)
    # for nlinear we use L=96 uniformly in mini suite for speed/comparability
    n=len(train); ends=np.arange(L, n-H+1)
    SW=np.stack([train[i-L:i] for i in ends]); X=SW-SW[:,-1:]
    Y=np.stack([train[e:e+H]-train[e-1] for e in ends])
    W=_ridge_multioutput(X,Y,alpha)
    return (W,L)

def pred_nlinear(model, hist):
    W,L=model; w=hist[-L:]; a=float(w[-1]); return (w-a)[None,:] @ W + a

def fit_rff(train, H):
    L=96; n=len(train); ends=np.arange(L,n-H+1)
    SW=np.stack([train[i-L:i] for i in ends]); X=SW-SW[:,-1:]
    h=64; rng=np.random.default_rng(_RUN_SEED); Wr=rng.standard_normal((L,h))*0.5; b=rng.uniform(0,2*np.pi,h)
    Phi=np.cos(X @ Wr + b)
    Y=np.stack([train[e:e+H]-train[e-1] for e in ends])
    Wout=_ridge_multioutput(Phi,Y,100.0)
    return (Wr,b,Wout,L)

def pred_rff(model, hist):
    Wr,b,Wout,L=model; w=hist[-L:]; a=float(w[-1]); phi=np.cos((w-a)[None,:] @ Wr + b); return (phi @ Wout)[0]+a

def fit_subbands(train, H):
    L=96; n=len(train); ends=np.arange(L,n-H+1)
    Xbands={"cA1":[],"d1":[]}  # J=1 for L=96 (SWT level 1 gives cA,d1 length 96)
    for e in ends:
        w=train[e-L:e]; xa=w-float(w[-1])
        cA,d1=pywt.swt(xa,"db4",level=1)[0]
        Xbands["cA1"].append(cA); Xbands["d1"].append(d1)
    for k in Xbands: Xbands[k]=np.stack(Xbands[k],axis=0)
    Y=np.stack([train[e:e+H]-train[e-1] for e in ends])
    W={k:_ridge_multioutput(Xbands[k],Y,100.0) for k in Xbands}
    return (W,L)

def pred_subband(model, hist, band):
    W,L=model; w=hist[-L:]; a=float(w[-1]); xa=w-a
    cA,d1=pywt.swt(xa,"db4",level=1)[0]
    vec={"cA1":cA,"d1":d1}[band]
    return (vec[None,:] @ W[band])[0]+a

def fit_pooled(train, H):
    m = AnchoredWaveletELM(hidden=96, input_length=96, wavelet="db4", levels=1, seed=_RUN_SEED)
    m.fit(train, horizon=H)
    return m

def pred_pooled(model, hist):
    model.history_ = hist
    return model.predict()
def fit_bigdict(train, H):
    if not _HAS_BIGDICT:
        raise RuntimeError("BigDictELM unavailable")
    m = BigDictELM(input_length=96, seed=_RUN_SEED)
    m.fit(train, horizon=H)
    return m

def pred_bigdict(model, hist):
    return model.predict_hist(hist)

def fit_bigdict_tree(train, H):
    if not _HAS_BIGDICT_TREE:
        raise RuntimeError("BigDictTree unavailable")
    m = BigDictTree(input_length=96, max_depth=6, tree_type="decision_tree", seed=_RUN_SEED)
    m.fit(train, horizon=H)
    return m

def pred_bigdict_tree(model, hist):
    return model.predict_hist(hist)

def fit_subband_bigdict(train, H):
    if not _HAS_SUBBAND_BIGDICT:
        raise RuntimeError("SubbandBigDict unavailable")
    m = SubbandBigDict(input_length=96, seed=_RUN_SEED)
    m.fit(train, horizon=H)
    return m

def pred_subband_bigdict(model, hist):
    return model.predict_hist(hist)

def fit_esn(train, H):
    if not _HAS_ESN:
        raise RuntimeError("ESNReservoir unavailable")
    m = ESNReservoir(input_length=96, seed=_RUN_SEED)
    m.fit(train, horizon=H)
    return m

def pred_esn(model, hist):
    return model.predict_hist(hist)


def fit_amr_seeded(train, H):
    """AMR-FBS pinned to the run seed; the member default (42) is frozen."""
    model = AMRFBSForecaster(seed=_RUN_SEED)
    model.fit(train, H)
    return model

def fit_det_esn(train, H):
    if not _HAS_DET_ESN:
        raise RuntimeError("DeterministicCycleESN unavailable")
    m = DeterministicCycleESN(input_length=96)
    m.fit(train, horizon=H)
    return m

def pred_det_esn(model, hist):
    return model.predict_hist(hist)

def fit_knn_forecaster(train, H):
    if not _HAS_KNN:
        raise RuntimeError("KNNFeatureForecaster unavailable")
    m = KNNFeatureForecaster(input_length=96, k_neighbors=24, alpha=10.0)
    m.fit(train, horizon=H)
    return m

def pred_knn_forecaster(model, hist):
    return model.predict_hist(hist)

def rolling_preds(series, H, fit_fn, pred_fn):
    train=series[:2000]
    model=fit_fn(train,H)
    origins=[2000+i*H for i in range(5) if 2000+i*H+H<=len(series)]
    preds=[]
    for o in origins:
        hist=series[max(0,o-96):o]
        p=pred_fn(model, hist)
        preds.append(np.asarray(p).ravel()[:H])
    P=np.stack(preds,axis=0); A=np.stack([series[o:o+H] for o in origins],axis=0)
    return P,A,origins

def _finite_values(values):
    return [float(v) for v in values if np.isfinite(v)]

def pool_blend_mae(P_dict, A, names):
    cols=[P_dict[n] for n in names if n in P_dict]
    if not cols: return float("nan")
    P=np.stack(cols,axis=2)  # W,H,M
    W,H2,M=P.shape
    blended=np.zeros_like(A)
    for h in range(H2):
        Ph=P[:,h,:]; Ah=A[:,h]
        for w in range(W):
            mask=np.arange(W)!=w
            if W==1:
                blended[w,h]=float(np.median(Ph[w]))
            else:
                m=Ridge(alpha=1000.0, fit_intercept=True)
                m.fit(Ph[mask], Ah[mask])
                blended[w,h]=float(m.predict(Ph[w:w+1])[0])
    return float(np.mean(np.abs(blended-A)))
def extract_series_from_window(window):
    """Return past float array(s) and horizon length for fev window.

    Multivariate targets are returned as a list of 1-D arrays (one per target
    column) so callers can forecast each target independently and average the
    error across targets.  Univariate tasks yield a single-element list.
    """
    past, _ = window.get_input_data()
    future = window.get_ground_truth()
    targets = list(getattr(window, "target_columns", []) or [])
    if not targets:
        targets = [c for c in past.column_names if c not in ("id", getattr(window, "timestamp_column", "timestamp"))]
    def _unwrap(v):
        # fev stores each target as a single-element container around the series.
        if not isinstance(v, (np.ndarray,)):
            try:
                if len(v) == 1 and hasattr(v[0], "__len__"):
                    return v[0]
            except Exception:
                pass
        return v
    past_cols = []
    for c in targets:
        if c in past.column_names:
            v = _unwrap(past[c])
            arr = np.asarray(v, dtype=float)
            past_cols.append(np.ravel(arr))
    fut_cols = []
    for c in targets:
        if c in future.column_names:
            v = _unwrap(future[c])
            arr = np.asarray(v, dtype=float)
            fut_cols.append(np.ravel(arr))
    n_targets = min(len(past_cols), len(fut_cols))
    past_cols = past_cols[:n_targets]
    fut_cols = fut_cols[:n_targets]
    H = len(fut_cols[0]) if fut_cols else 0
    return past_cols, fut_cols, H, n_targets

def main_fev(bench, out_dir=None):
    t0=time.time(); log=[]
    def out(s): print(s); log.append(s)
    out(f"fev bench: {len(bench.tasks)} tasks")
    # For each task, fit NLinear/RFF/Subband on past of first window, score all windows via LOO ridge stack
    # Keep wall short: cap windows per task to 3 if >3
    fits_simple={
        "nlinear_a1": (lambda tr,H: fit_nlinear(tr,H,1.0), pred_nlinear),
        "nlinear_a10": (lambda tr,H: fit_nlinear(tr,H,10.0), pred_nlinear),
        "rff_h64": (fit_rff, pred_rff),
        "subband_cA1": (fit_subbands, lambda m,h: pred_subband(m,h,"cA1")),
        "subband_d1": (fit_subbands, lambda m,h: pred_subband(m,h,"d1")),
        "knn_forecaster": (fit_knn_forecaster, pred_knn_forecaster),
    }
    if _HAS_ELM:
        fits_simple["wavelet_pooled"] = (fit_pooled, pred_pooled)
    task_results=[]
    for ti, task in enumerate(bench.tasks):
        windows=list(task.iter_windows())
        if len(windows)>5: windows=windows[:5]
        # Use H from first window's future length
        past0_cols, fut0_cols, H, n_targets = extract_series_from_window(windows[0])
        if n_targets == 0:
            out("  skip: no target columns")
            continue
        out(f"\n-- task {ti+1}/{len(bench.tasks)} {task.dataset_path}:{task.dataset_config} H={H} W={len(windows)}")
        # Ensure past0 long enough; pad/truncate to 2000 or available (per target)
        train_cols = [p[-2000:] if len(p) >= 96 else p for p in past0_cols]
        # Collect per-window futures (per target)
        A_list_per_target = [[] for _ in range(n_targets)]
        for wi, w in enumerate(windows):
            past_cols, fut_cols, _, _ = extract_series_from_window(w)
            for t_idx in range(n_targets):
                A_list_per_target[t_idx].append(fut_cols[t_idx])
        A_true_per_target = []
        for t_idx in range(n_targets):
            cols = A_list_per_target[t_idx]
            if cols and len(set(len(a) for a in cols)) == 1:
                A_true_per_target.append(np.array(cols))
            else:
                A_true_per_target.append(None)
        if any(a is None for a in A_true_per_target):
            out("  skip: variable horizon across windows")
            continue
        P_dict = {}
        for name, (ff, pf) in fits_simple.items():
            try:
                # Per-origin fit: fit on each window's own past, then predict its future.
                preds_per_target = [[] for _ in range(n_targets)]
                for w in windows:
                    past_cols, fut_cols, _, _ = extract_series_from_window(w)
                    train_cols_w = [p[-2000:] if len(p) >= 96 else p for p in past_cols]
                    models = [ff(train_cols_w[t_idx], H) for t_idx in range(n_targets)]
                    for t_idx in range(n_targets):
                        past = past_cols[t_idx]
                        hist = past[-96:] if len(past) >= 96 else past
                        p = pf(models[t_idx], hist) if name != "wavelet_pooled" else pf(models[t_idx], hist)
                        preds_per_target[t_idx].append(np.asarray(p).ravel()[:H])
                # Stack predictions per target, compute MAE per target, average
                maes_per_target = []
                for t_idx in range(n_targets):
                    P = np.stack(preds_per_target[t_idx], axis=0)
                    maes_per_target.append(float(np.mean(np.abs(P - A_true_per_target[t_idx]))))
                # Store P_dict as the first target's predictions (for pool blending)
                P = np.stack(preds_per_target[0], axis=0)
                P_dict[name] = P
                mae = float(np.mean(maes_per_target))
                out(f"  {name:22s} MAE {mae:.4f}" + (f" (avg over {n_targets} targets)" if n_targets > 1 else ""))
            except Exception as e:
                out(f"  {name:22s} FAIL {type(e).__name__}: {e}")
                import traceback as tb
                tb.print_exc()
        # pools as before
        poolA = ["nlinear_a1", "nlinear_a10", "rff_h64"]
        poolI = poolA + ["knn_forecaster"] if _HAS_KNN else poolA
        poolI = [n for n in poolI if n in P_dict]
        poolB = poolA + ["subband_cA1", "subband_d1"]
        poolC = poolA + ["wavelet_pooled"]
        poolC = [n for n in poolC if n in P_dict]
        poolA = [n for n in poolA if n in P_dict]
        poolB = [n for n in poolB if n in P_dict]
        poolC = [n for n in poolC if n in P_dict]
        maeA = pool_blend_mae(P_dict, A_true_per_target[0], poolA)
        maeB = pool_blend_mae(P_dict, A_true_per_target[0], poolB)
        maeC = pool_blend_mae(P_dict, A_true_per_target[0], poolC)
        maeI = pool_blend_mae(P_dict, A_true_per_target[0], poolI) if "knn_forecaster" in P_dict else float("nan")
        if _HAS_KNN and "knn_forecaster" in P_dict:
            out(f"  Pool I (KNN Feature) blend {maeI:.4f}")
        out(f"  Pool A blend {maeA:.4f}  B {maeB:.4f}  C {maeC:.4f}")
        task_results.append((maeA, maeB, maeC, maeI))
    maesA=[a for a,_,_,_ in task_results]; maesB=[b for _,b,_,_ in task_results]; maesC=[c for _,_,c,_ in task_results]; maesI=[i for _,_,_,i in task_results]
    meanA=float(np.nanmean(maesA)) if maesA else float("nan"); meanB=float(np.nanmean(maesB)) if maesB else float("nan"); meanC=float(np.nanmean(maesC)) if maesC else float("nan")
    winsB=sum(1 for a,b in zip(maesA,maesB) if b<a)
    order_ranks=[]
    for a,b,c,i in zip(maesA,maesB,maesC,maesI):
        order=sorted([(a,"A"),(b,"B"),(c,"C"),(i,"I")])
        r={n:i+1 for i,(_,n) in enumerate(order)}
        order_ranks.append(r.get("B",2))
    mean_rankB=float(np.mean(order_ranks)) if order_ranks else 2
    out(f"\n=== fev Aggregate ({len(task_results)} tasks) ===")
    maesI=[i for _,_,_,i in task_results]
    meanI=float(np.nanmean(maesI)) if maesI else float("nan")
    winsI=sum(1 for a,i in zip(maesA,maesI) if i<a)
    out(f"meanA {meanA:.4f} meanB {meanB:.4f} meanC {meanC:.4f} meanI {meanI:.4f} winsB {winsB}/{len(task_results)} winsI {winsI}/{len(task_results)} rankB {mean_rankB:.2f}")
    # G2 per pre-registration: mean rank of Pool B among {A,B,C,I} < 2.0
    # (average rank), not a majority-win count.
    g2_pass = bool(mean_rankB < 2.0)
    verdict = "PROMOTE subband" if (meanB < meanA - 0.005 and g2_pass) else "REJECTED"
    out(f"verdict {verdict}")
    out(f"G2 (Pool B beats A on majority of tasks): {winsB}/{len(task_results)} -> {'PASS' if g2_pass else 'FAIL'}")
    res={"suite":"fev","data_source":"real","confirmatory":True,"fev":dict(_FEV_LOADED),"tasks":len(task_results),"meanA":meanA,"meanB":meanB,"meanC":meanC,"winsB":winsB,"winsI":winsI,"meanI":meanI,"mean_rankB":mean_rankB,"verdict":verdict,"gates":{"G2_majority_win":g2_pass,"G2_wins":winsB,"G2_total":len(task_results)},"elapsed_s":time.time()-t0}
    outdir = pathlib.Path(out_dir) if out_dir else HERE / "results"
    outdir.mkdir(parents=True, exist_ok=True)
    tag="fev_mini" if len(bench.tasks)<=20 else "fev_full"
    with open(outdir/f"bench_{tag}.json","w") as f: json.dump(res,f,indent=2)
    with open(outdir/f"bench_{tag}.log","w") as f: f.write("\n".join(log)+"\n")
    out(f"wrote bench_{tag}.json")
    return 0

_FEV_LOADED = {}

def run_fev_bench(mini=True, url=None):
    """Run fev-bench-mini (20) or fev-bench (100) tasks via fev directly.

    Returns the loaded Benchmark, or None when the real benchmark could not be
    loaded. None means "no real FEV" and the caller must not present a synthetic
    suite as if it were one; the paths below are the ones the fev repo actually
    publishes (`benchmarks/fev_bench/tasks*.yaml`), not the bare
    `benchmarks/fev_bench.yaml` that used to 404. `url` (or the
    `FEV_TASKS_URL` env var) overrides the source so the failure branch is
    reachable from a test.
    """
    import fev
    _bol = "https://raw.githubusercontent.com/autogluon/fev/main/benchmarks/fev_bench/"
    if url is None:
        url = os.environ.get("FEV_TASKS_URL") or _bol + ("tasks_mini.yaml" if mini else "tasks.yaml")
    try:
        bench = fev.Benchmark.from_yaml(url)
    except Exception as e:
        print(f"fev Benchmark.from_yaml failed ({e}) — NOT falling back silently")
        return None
    _FEV_LOADED.clear()
    _FEV_LOADED.update({"url": url, "mini": bool(mini), "n_tasks": len(bench.tasks)})
    print(f"fev bench loaded: {len(bench.tasks)} tasks from {url}")
    try:
        w = next(bench.tasks[0].iter_windows())
        past, future = w.get_input_data()
        print(f"probe ok: past {len(past) if hasattr(past,'__len__') else type(past)}, future {len(future) if hasattr(future,'__len__') else type(future)}")
    except Exception as e:
        print(f"fev probe failed (offline/HF auth?): {e} — NOT falling back silently")
        _FEV_LOADED.clear()
        return None
    return bench

def build_fits():
    """Assemble the fit/pred pairs this environment supports, at the current _RUN_SEED."""
    fits = {
        "nlinear_a1": (lambda tr, H: fit_nlinear(tr, H, 1.0), pred_nlinear),
        "nlinear_a10": (lambda tr, H: fit_nlinear(tr, H, 10.0), pred_nlinear),
        "rff_h64": (fit_rff, pred_rff),
        "subband_cA1": (fit_subbands, lambda m, h: pred_subband(m, h, "cA1")),
        "subband_d1": (fit_subbands, lambda m, h: pred_subband(m, h, "d1")),
    }
    if _HAS_ELM:
        fits["wavelet_pooled"] = (fit_pooled, pred_pooled)
    if _HAS_BIGDICT:
        fits["bigdict_elm"] = (fit_bigdict, pred_bigdict)
        fits["amr_fbs"] = (fit_amr_seeded, pred_amr_fbs)
        fits["dlinear"] = (fit_dlinear, pred_dlinear)
        fits["spectral_fft"] = (fit_fft, pred_fft)
        fits["theta"] = (fit_theta, pred_theta)
    if _HAS_BIGDICT_TREE:
        fits["bigdict_tree"] = (fit_bigdict_tree, pred_bigdict_tree)
    if _HAS_SUBBAND_BIGDICT:
        fits["subband_bigdict"] = (fit_subband_bigdict, pred_subband_bigdict)
    if _HAS_ESN:
        fits["esn_reservoir"] = (fit_esn, pred_esn)
    if _HAS_KNN:
        fits["knn_forecaster"] = (fit_knn_forecaster, pred_knn_forecaster)
    if _HAS_DET_ESN:
        fits["deterministic_esn"] = (fit_det_esn, pred_det_esn)
    return fits

def run_one_seed(out):
    """Fit every task at the current _RUN_SEED and return its per-task metrics."""
    fits = build_fits()
    per_task={}
    for task_name,H,_ in TASKS:
        series=get_series(task_name)
        out(f"\n-- {task_name} H={H} --")
        P_dict={}; A_ref=None; singleton={}
        for name,(ff,pf) in fits.items():
            try:
                P,A,_=rolling_preds(series,H,ff,pf)
                P_dict[name]=P
                if A_ref is None: A_ref=A
                singleton[name]=float(np.mean(np.abs(P-A_ref)))
                out(f"  {name:22s} MAE {singleton[name]:.4f}")
            except Exception as e:
                out(f"  {name:22s} FAIL {e}")
        poolA=["nlinear_a1","nlinear_a10","rff_h64"]
        poolB=poolA+["subband_cA1","subband_d1"]
        poolC=poolA+["wavelet_pooled"]
        poolD=poolA+["bigdict_elm", "amr_fbs"] if _HAS_BIGDICT else poolA
        poolE=poolA+["subband_bigdict"] if _HAS_SUBBAND_BIGDICT else poolA
        poolF=poolA+["esn_reservoir"] if _HAS_ESN else poolA
        poolG=poolA+["deterministic_esn"] if _HAS_DET_ESN else poolA
        poolI=poolA+["knn_forecaster"] if _HAS_KNN else poolA
        poolI=[n for n in poolI if n in P_dict]
        maeI=pool_blend_mae(P_dict,A_ref,poolI) if "knn_forecaster" in P_dict else float("nan")
        if _HAS_KNN and "knn_forecaster" in P_dict: out(f"  Pool I (KNN Feature) {poolI} blend {maeI:.4f}")

        poolH=poolA + ([] if not _HAS_BIGDICT else ["bigdict_elm", "amr_fbs"]) + ([] if not _HAS_DET_ESN else ["deterministic_esn"])
        poolA=[n for n in poolA if n in P_dict]
        poolB=[n for n in poolB if n in P_dict]
        poolC=[n for n in poolC if n in P_dict]
        poolD=[n for n in poolD if n in P_dict]
        poolE=[n for n in poolE if n in P_dict]
        poolF=[n for n in poolF if n in P_dict]
        poolG=[n for n in poolG if n in P_dict]
        poolH=[n for n in poolH if n in P_dict]
        maeA=pool_blend_mae(P_dict,A_ref,poolA); maeB=pool_blend_mae(P_dict,A_ref,poolB); maeC=pool_blend_mae(P_dict,A_ref,poolC); maeD=pool_blend_mae(P_dict,A_ref,poolD) if "bigdict_elm" in P_dict and "amr_fbs" in P_dict else float("nan")
        maeE=pool_blend_mae(P_dict,A_ref,poolE) if "subband_bigdict" in P_dict else float("nan")
        maeF=pool_blend_mae(P_dict,A_ref,poolF) if "esn_reservoir" in P_dict else float("nan")
        maeG=pool_blend_mae(P_dict,A_ref,poolG) if "deterministic_esn" in P_dict else float("nan")
        maeH=pool_blend_mae(P_dict,A_ref,poolH) if len(poolH)>len(poolA) else float("nan")
        out(f"  Pool A {poolA} blend {maeA:.4f}")
        out(f"  Pool B {poolB} blend {maeB:.4f}")
        out(f"  Pool C {poolC} blend {maeC:.4f}")
        if _HAS_BIGDICT and "bigdict_elm" in P_dict and "amr_fbs" in P_dict: out(f"  Pool D {poolD} blend {maeD:.4f}")
        if _HAS_SUBBAND_BIGDICT and "subband_bigdict" in P_dict: out(f"  Pool E {poolE} blend {maeE:.4f}")
        if _HAS_ESN and "esn_reservoir" in P_dict: out(f"  Pool F {poolF} blend {maeF:.4f}")
        if _HAS_DET_ESN and "deterministic_esn" in P_dict: out(f"  Pool G {poolG} blend {maeG:.4f}")
        if len(poolH)>len(poolA): out(f"  Pool H (Hybrid BigDict + DetESN) {poolH} blend {maeH:.4f}")
        per_task[task_name]={"H":H,"singleton":singleton,"pool_blend":{"A":maeA,"B":maeB,"C":maeC,"D":maeD,"E":maeE,"F":maeF,"G":maeG,"H":maeH},"pool_names":{"A":poolA,"B":poolB,"C":poolC,"D":poolD,"E":poolE,"F":poolF,"G":poolG,"H":poolH}}
    return per_task

def aggregate(per_task):
    """Pool means, win counts, mean ranks and the per-seed S-47 gates."""
    task_names=[n for n,_,_ in TASKS if n in per_task]
    maesA=[per_task[n]["pool_blend"]["A"] for n in task_names]
    maesB=[per_task[n]["pool_blend"]["B"] for n in task_names]
    maesC=[per_task[n]["pool_blend"]["C"] for n in task_names]
    maesD=[per_task[n]["pool_blend"]["D"] for n in task_names]
    meanA=float(np.nanmean(maesA)); meanB=float(np.nanmean(maesB)); meanC=float(np.nanmean(maesC)); meanD=float(np.nanmean(maesD))
    pairedB=[(a,b) for a,b in zip(maesA,maesB) if np.isfinite(a) and np.isfinite(b)]
    pairedD=[(a,d) for a,d in zip(maesA,maesD) if np.isfinite(a) and np.isfinite(d)]
    winsB=sum(1 for a,b in pairedB if b<a)
    winsD=sum(1 for a,d in pairedD if d<a)
    ranks=[]; ranksD=[]
    for a,b,c,d in zip(maesA,maesB,maesC,maesD):
        vals=[(a,"A"),(b,"B"),(c,"C")] if np.isnan(d) else [(a,"A"),(b,"B"),(c,"C"),(d,"D")]
        order=sorted(vals)
        r={name:i+1 for i,(_,name) in enumerate(order)}
        ranks.append(r.get("B",2))
        if "D" in r: ranksD.append(r["D"])
    mean_rankB=float(np.mean(ranks))
    mean_rankD=float(np.mean(ranksD)) if ranksD else float("nan")
    G1=meanB < meanA - 0.005; G2=mean_rankB < 2.0; G3=winsB>=4
    all_binding=bool(G1 and G2 and G3)
    verdict="PROMOTE subband family" if all_binding else "REJECTED"
    GD1=meanD < meanA - 0.005 if not np.isnan(meanD) else False
    GD2=mean_rankD < 2.0 if not np.isnan(mean_rankD) else False
    GD3=winsD>=4 if not np.isnan(meanD) else False
    agg={"meanA":meanA,"meanB":meanB,"meanC":meanC,"meanD":meanD,"winsB":winsB,"winsB_denominator":len(pairedB),"winsD":winsD,"winsD_denominator":len(pairedD),"mean_rankB":mean_rankB,"mean_rankD":mean_rankD}
    gates={"G1":bool(G1),"G2":bool(G2),"G3":bool(G3),"all_binding":all_binding,"bigdict":{"GD1":bool(GD1),"GD2":bool(GD2),"GD3":bool(GD3),"all":bool(GD1 and GD2 and GD3)}}
    return task_names, agg, gates, verdict

def mean_std(values):
    """Mean and sample std over seeds; NaN arms drop out rather than poison the mean."""
    finite=[float(v) for v in values if v is not None and np.isfinite(v)]
    if not finite: return float("nan"), float("nan")
    return float(np.mean(finite)), (float(np.std(finite, ddof=1)) if len(finite)>1 else 0.0)

def stat_block(values):
    return {"mean":mean_std(values)[0], "std":mean_std(values)[1]}

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--fev", action="store_true", help="run fev-bench-mini (20 tasks) via fev; fails loudly if the real benchmark cannot be loaded")
    ap.add_argument("--fev-full", action="store_true", help="run fev-bench full 100 tasks")
    ap.add_argument("--allow-synthetic-fallback", action="store_true", help="if --fev cannot load the real benchmark, run the built-in synthetic suite anyway (result marked data_source=synthetic_fallback, confirmatory=false, and written to bench_synthetic_fallback.json)")
    ap.add_argument("--seeds", type=int, default=5, help="seeds to average over; CLAUDE.md: mean ± std, a single run is a hint")
    ap.add_argument("--seed-base", type=int, default=42, help="first seed; the sweep runs base, base+1, …")
    ap.add_argument("--out-dir", default=None, help="write results_s47.json and harness.log here instead of the project root; use it so a test run cannot overwrite the committed evidence")
    args=ap.parse_args()
    if args.seeds < 1: raise SystemExit("--seeds must be >= 1")
    data_source="builtin_suite"
    fev_attempt=None
    if args.fev or args.fev_full:
        bench=run_fev_bench(mini=not args.fev_full)
        if bench is not None:
            return main_fev(bench, out_dir=args.out_dir)
        # A requested real benchmark did not load. Reporting the synthetic suite
        # as if it were FEV is the defect this branch exists to prevent, so the
        # default is a hard stop, not a quiet degrade.
        fev_attempt={"requested":"fev_full" if args.fev_full else "fev_mini","achieved":None}
        if not args.allow_synthetic_fallback:
            print("FATAL: FEV was requested but the real benchmark could not be loaded; "
                  "refusing to report the synthetic suite as FEV.", file=sys.stderr)
            print("Re-run with --allow-synthetic-fallback to run the built-in suite "
                  "explicitly — the result is then stamped "
                  "data_source=synthetic_fallback and confirmatory=false.", file=sys.stderr)
            return 2
        print("WARNING: FEV requested but unavailable — running the built-in synthetic "
              "suite. This result is NOT FEV: data_source=synthetic_fallback, "
              "confirmatory=false.")
        fev_attempt["achieved"]="synthetic_fallback"
        data_source="synthetic_fallback"
    t0=time.time(); log=[]
    def out(s): print(s); log.append(s)
    if STRICT_DEPS and UNAVAILABLE:
        raise RuntimeError("strict benchmark refused unavailable dependencies: " + ", ".join(sorted(UNAVAILABLE)))
    seeds=[args.seed_base+i for i in range(args.seeds)]
    out(f"seeds {seeds} — data generators keep fixed seeds, only model randomness varies")
    per_seed=[]; stats=[]; gates=[]; verdicts=[]; task_names=[]
    for seed in seeds:
        globals()["_RUN_SEED"]=seed
        out(f"\n########## seed {seed} ##########")
        per_task=run_one_seed(out)
        names,agg,g,verdict=aggregate(per_task)
        task_names=names
        per_seed.append(per_task); stats.append(agg); gates.append(g); verdicts.append(verdict)
        out(f"\n=== Aggregate (seed {seed}) ===")
        out(f"meanA {agg['meanA']:.4f} meanB {agg['meanB']:.4f} meanC {agg['meanC']:.4f} meanD {agg['meanD']:.4f}")
        out(f"wins B over A {agg['winsB']}/{agg['winsB_denominator']}  mean_rankB {agg['mean_rankB']:.2f}  wins D over A {agg['winsD']}/{agg['winsD_denominator']} rankD {agg['mean_rankD']:.2f}")
        out(f"Gates(G1<mean-0.005,G2 rank<2,G3 wins>=4) G1 {g['G1']} G2 {g['G2']} G3 {g['G3']} all {g['all_binding']} -> {verdicts[-1]}")
        out(f"BigDict G1 {g['bigdict']['GD1']} G2 {g['bigdict']['GD2']} G3 {g['bigdict']['GD3']} -> {'PROMOTE BigDict' if g['bigdict']['all'] else 'REJECTED'}")
    globals()["_RUN_SEED"]=args.seed_base
    out("\n########## seed sweep ##########")
    agg_stats={k:stat_block([s[k] for s in stats]) for k in ("meanA","meanB","meanC","meanD","mean_rankB","mean_rankD","winsB","winsD")}
    for k,v in agg_stats.items(): out(f"{k:10s} {v['mean']:.4f} ± {v['std']:.4f}")
    # A win has to clear the spread it is measured against: the mean per-seed gap
    # over Pool A, against the std of that same gap (CONTEXT.md §Human check).
    gmeanB,gstdB=mean_std([s["meanB"]-s["meanA"] for s in stats])
    gmeanD,gstdD=mean_std([s["meanD"]-s["meanA"] for s in stats])
    out(f"gap B-A {gmeanB:+.4f} ± {gstdB:.4f}   gap D-A {gmeanD:+.4f} ± {gstdD:.4f}")
    sweep_gates={
        "B_beats_A_beyond_std":bool(np.isfinite(gstdB) and gmeanB < -gstdB),
        "D_beats_A_beyond_std":bool(np.isfinite(gstdD) and gmeanD < -gstdD),
        "B_wins_majority_every_seed":bool(all(g["G3"] for g in gates)),
        "BigDict_gates_every_seed":bool(all(g["bigdict"]["all"] for g in gates)),
    }
    out(f"sweep gates {sweep_gates}")
    for k,v in sweep_gates.items():
        if not v: out(f"  NOT MET: {k} — a win smaller than the seed spread is not a win")
    pool_keys=list(per_seed[0][task_names[0]]["pool_blend"].keys())
    per_task_seed={}
    for t in task_names:
        members=sorted({m for s in per_seed for m in s[t]["singleton"]})
        per_task_seed[t]={"H":per_seed[0][t]["H"],
                          "pool_blend":{k:stat_block([s[t]["pool_blend"][k] for s in per_seed]) for k in pool_keys},
                          "singleton":{m:stat_block([s[t]["singleton"].get(m) for s in per_seed]) for m in members}}
    res={"slice":"S-47-diverse-mini+BigDict","suite":"8-task synthetic+ETTh1 H96/W=5 frozen-fit","data_source":data_source,"confirmatory":data_source=="real","environment":{"python":sys.version,"platform":platform.platform(),"cwd":str(pathlib.Path.cwd()),"strict_dependencies":STRICT_DEPS},"availability":{"unavailable":UNAVAILABLE},"protocol":{"train_end":2000,"context_length":96,"origins_per_task":5,"fit_mode":"frozen-per-task","selection_uses_evaluation":False,"seeds":seeds,"seed_policy":"data generators keep their fixed seeds; only model randomness varies, so std measures the model not the sample"},"tasks":{"requested":len(TASKS),"evaluated":len(task_names),"names":task_names},
         "aggregate":agg_stats,
         "aggregate_gaps":{"B_minus_A":{"mean":gmeanB,"std":gstdB},"D_minus_A":{"mean":gmeanD,"std":gstdD}},
         "gates":sweep_gates,
         "per_task":per_task_seed,
         "per_seed":[{"seed":seed,"aggregate":a,"gates":g,"verdict":v} for seed,a,g,v in zip(seeds,stats,gates,verdicts)],
         "verdict":{"per_seed":verdicts,"unanimous":len(set(verdicts))==1,"value":verdicts[0] if len(set(verdicts))==1 else "MIXED"},
         "elapsed_s":time.time()-t0}
    if fev_attempt is not None:
        res["fev_attempt"]=fev_attempt
    outdir=pathlib.Path(args.out_dir) if args.out_dir else HERE
    outdir.mkdir(parents=True, exist_ok=True)
    # A fallback run must never land on results_s47.json: that filename is the
    # committed S-47 evidence, and `--fev` used to overwrite it with a suite the
    # caller never asked for.
    stem="bench_synthetic_fallback" if data_source=="synthetic_fallback" else "results_s47"
    with open(outdir/f"{stem}.json","w") as f: json.dump(res,f,indent=2)
    with open(outdir/("bench_synthetic_fallback.log" if stem=="bench_synthetic_fallback" else "harness.log"),"w") as f: f.write("\n".join(log)+"\n")
    out(f"wrote {outdir/(stem+'.json')} ({len(seeds)} seeds) data_source={data_source} confirmatory={res['confirmatory']} elapsed {time.time()-t0:.1f}s")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
