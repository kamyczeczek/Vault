"""S-47 Diverse Mini Suite — fast cross-domain probe.
6 tasks (ETTh1 H96 + 5 synthetic), W=5 rolling origins, frozen-fit per task.
Compares Pool A (linear+RFF), Pool B (+SWT subband experts), Pool C (+pooled-ELM).
"""
from __future__ import annotations
import json, time, pathlib, sys
import numpy as np
import pywt
from sklearn.linear_model import Ridge

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent))
sys.path.insert(0, str(HERE.parent / "anchored_wavelet_elm_s46"))
from data import get_protocol_data
from anchored_wavelet_elm import AnchoredWaveletELM, _ridge_multioutput

SEARCH_ALPHA = 3000.0

TASKS = [
    ("etth1_H96", 96, "real"),
    ("seasonal_H48", 48, "synthetic"),
    ("trending_H48", 48, "synthetic"),
    ("spiky_H48", 48, "synthetic"),
    ("ou_H24", 24, "synthetic"),
    ("multiscale_H96", 96, "synthetic"),
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

def get_series(name):
    if name=="etth1_H96":
        s=get_protocol_data().rolling_views()[0][:2600].astype(float)
        if s.ndim>1: s=s[:,0]
        return s
    return {"seasonal_H48":gen_seasonal,"trending_H48":gen_trending,"spiky_H48":gen_spiky,"ou_H24":gen_ou,"multiscale_H96":gen_multiscale}[name](2600)

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
    h=64; rng=np.random.default_rng(0); Wr=rng.standard_normal((L,h))*0.5; b=rng.uniform(0,2*np.pi,h)
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

def fit_pooled(train,H):
    m=AnchoredWaveletELM(hidden=96, input_length=96, wavelet="db4", levels=1, seed=42)
    m.fit(train, horizon=H)
    return m

def pred_pooled(model, hist):
    model.history_=hist
    return model.predict()

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
                blended[w,h]=float(np.mean(Ph[w]))
            else:
                m=Ridge(alpha=SEARCH_ALPHA, fit_intercept=False)
                m.fit(Ph[mask], Ah[mask])
                blended[w,h]=float(Ph[w] @ m.coef_)
    return float(np.mean(np.abs(blended-A)))

def main():
    t0=time.time(); log=[]
    def out(s): print(s); log.append(s)
    out("S-47 Diverse Mini Suite (6 tasks, W=5, 5+subband/pooled contrasts)")
    for n,H,_ in TASKS: out(f" task {n:18s} H={H:3d} n=2600")

    per_task={}
    fits={
        "nlinear_a1": (lambda tr,H: fit_nlinear(tr,H,1.0), pred_nlinear),
        "nlinear_a10": (lambda tr,H: fit_nlinear(tr,H,10.0), pred_nlinear),
        "rff_h64": (fit_rff, pred_rff),
        "subband_cA1": (fit_subbands, lambda m,h: pred_subband(m,h,"cA1")),
        "subband_d1": (fit_subbands, lambda m,h: pred_subband(m,h,"d1")),
        "wavelet_pooled": (fit_pooled, pred_pooled),
    }

    for task_name,H,_ in TASKS:
        series=get_series(task_name)
        out(f"\n-- {task_name} H={H} --")
        P_dict={}; A_ref=None; singleton={}
        for name,(ff,pf) in fits.items():
            try:
                P,A,_=rolling_preds(series,H,ff,pf)
                P_dict[name]=P;
                if A_ref is None: A_ref=A
                singleton[name]=float(np.mean(np.abs(P-A_ref)))
                out(f"  {name:22s} MAE {singleton[name]:.4f}")
            except Exception as e:
                out(f"  {name:22s} FAIL {e}")
        poolA=["nlinear_a1","nlinear_a10","rff_h64"]
        poolB=poolA+["subband_cA1","subband_d1"]
        poolC=poolA+["wavelet_pooled"]
        poolA=[n for n in poolA if n in P_dict]
        poolB=[n for n in poolB if n in P_dict]
        poolC=[n for n in poolC if n in P_dict]
        maeA=pool_blend_mae(P_dict,A_ref,poolA); maeB=pool_blend_mae(P_dict,A_ref,poolB); maeC=pool_blend_mae(P_dict,A_ref,poolC)
        out(f"  Pool A {poolA} blend {maeA:.4f}")
        out(f"  Pool B {poolB} blend {maeB:.4f}")
        out(f"  Pool C {poolC} blend {maeC:.4f}")
        per_task[task_name]={"H":H,"singleton":singleton,"pool_blend":{"A":maeA,"B":maeB,"C":maeC},"pool_names":{"A":poolA,"B":poolB,"C":poolC}}

    maesA=[per_task[n]["pool_blend"]["A"] for n,_,_ in TASKS]
    maesB=[per_task[n]["pool_blend"]["B"] for n,_,_ in TASKS]
    maesC=[per_task[n]["pool_blend"]["C"] for n,_,_ in TASKS]
    meanA=float(np.nanmean(maesA)); meanB=float(np.nanmean(maesB)); meanC=float(np.nanmean(maesC))
    winsB=sum(1 for a,b in zip(maesA,maesB) if b<a)
    # rank B
    ranks=[]
    for a,b,c in zip(maesA,maesB,maesC):
        order=sorted([(a,"A"),(b,"B"),(c,"C")])
        r={name:i+1 for i,(_,name) in enumerate(order)}
        ranks.append(r.get("B",2))
    mean_rankB=float(np.mean(ranks))
    out("\n=== Aggregate ===")
    out(f"meanA {meanA:.4f} meanB {meanB:.4f} meanC {meanC:.4f}")
    out(f"wins B over A {winsB}/6  mean_rankB {mean_rankB:.2f}")
    G1=meanB < meanA - 0.005; G2=mean_rankB < 2.0; G3=winsB>=4
    all_binding=bool(G1 and G2 and G3)
    verdict="PROMOTE subband family" if all_binding else "REJECTED"
    out(f"Gates G1 {G1} G2 {G2} G3 {G3} all {all_binding} -> {verdict}")
    res={"slice":"S-47-diverse-mini","suite":"6-task synthetic+ETTh1 H96/W=5 frozen-fit","harness_command":"python projects/ts-ml-experiments/h720/sub_experiments/diverse_mini_s47/rolling_arm.py","per_task":{k:{"H":v["H"],"singleton":v["singleton"],"pool_blend":v["pool_blend"]} for k,v in per_task.items()},"aggregate":{"meanA":meanA,"meanB":meanB,"meanC":meanC,"winsB":winsB,"mean_rankB":mean_rankB},"gates":{"G1":G1,"G2":G2,"G3":G3,"all_binding":all_binding},"verdict":verdict,"elapsed_s":time.time()-t0}
    with open(HERE/"results_s47.json","w") as f: json.dump(res,f,indent=2)
    with open(HERE/"harness.log","w") as f: f.write("\n".join(log)+"\n")
    out(f"wrote results_s47.json elapsed {time.time()-t0:.1f}s")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
