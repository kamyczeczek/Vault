"""P0 STANDARDIZATION CONTROL - BigDict 'wavelet-detail toxicity' claim.

Is the Thomas catastrophe caused by the detail coeffs THEMSELVES, or by the raw
scale mismatch (detail coeffs ~10x lower variance)?
Modes: none / all / detail_only (z-score SWT db4 L2 subbands cA1,cD1,cA2,cD2;
stats fit on train windows, applied at test).  Pipeline mirrors BIG_DICT_ELM_
DESIGN.md fast defaults (anchor=last, cos RFF hidden=512, ridge alpha=10,
L=96, 5 rolling origins, seed 42).  References (root ablation):
thomas_H24 full_none=0.2281 compact_none=0.0139 | trending_H48 0.95 / 1.11.
Output: results/results_bigdict_std_control.{json,md}
"""
import json, sys, time
import numpy as np
import pywt
import _workspace_paths
from _workspace_paths import BENCHMARK_CORE
sys.path.insert(0, str(BENCHMARK_CORE / "members"))
from bigdict_ablation import gen_thomas, gen_trending, TRAIN_END, INPUT_LEN
from numpy.lib.stride_tricks import as_strided

L, H_T, H_R, ALPHA, HIDDEN, SEED = INPUT_LEN, 24, 48, 10.0, 512, 42
ND = 4 * L
REF = {"thomas_H24": {"full": 0.2281, "compact": 0.0139},
       "trending_H48": {"full": 0.95, "compact": 1.11}}

def _ma(w, X):
    n = X.shape[0]
    c = np.concatenate([np.zeros((1, X.shape[1])), X], axis=0).cumsum(axis=0)
    st = np.maximum(np.arange(n) - w + 1, 0)
    return (c[1:n + 1] - c[st]) / np.minimum(np.arange(n) + 1, w)[:, None]

def _ema(a, X):
    e = np.empty_like(X); e[0] = X[0]
    for i in range(1, len(X)): e[i] = a * X[i] + (1 - a) * e[i - 1]
    return e

def _d1(X):
    d = np.zeros_like(X); d[:, 1:] = np.diff(X, axis=1); return d

def _swt(X):
    out = []
    for r in X:
        try: out.append(np.concatenate([c for c in pywt.swt(r, "db4", 2) if len(c) == L]))
        except Exception: out.append(np.zeros(ND))
    return np.array(out)

def feats(Xa, use_wav):
    p = [Xa, _ma(3, Xa), _ma(6, Xa), _ma(12, Xa), _ma(24, Xa),
         _ema(0.3, Xa), _ema(0.7, Xa)]
    if use_wav:
        p += [_d1(Xa), _d1(_d1(Xa)), Xa - _ma(12, Xa), Xa - _ma(24, Xa)]
    return np.concatenate(p, axis=1)

def run(series, H, task, bank, std):
    s = np.asarray(series, float)
    ntr = TRAIN_END - H - L + 1
    wtr = np.ascontiguousarray(as_strided(s[:TRAIN_END][:ntr + L - 1],
          shape=(ntr, L), strides=(s.itemsize, s.itemsize)))
    a_tr = wtr[:, -1:]
    origins = [TRAIN_END + i * H for i in range(5)]
    wte = np.array([s[max(0, o - L):o] for o in origins])
    a_te = wte[:, -1:]
    btr, bte = feats(wtr - a_tr, bank == "full"), feats(wte - a_te, bank == "full")
    wav_tr, wav_te = (_swt(wtr - a_tr), _swt(wte - a_te)) if bank == "full" else (None, None)
    X = np.concatenate([btr, wav_tr], 1) if bank == "full" else btr
    Xt = np.concatenate([bte, wav_te], 1) if bank == "full" else bte
    n = X.shape[0]
    if std in ("all", "detail_only"):
        mu, sd = X.mean(0), X.std(0); sd[sd < 1e-8] = 1.0
        if std == "all": X, Xt = (X - mu) / sd, (Xt - mu) / sd
        else:
            X, Xt = X.copy(), Xt.copy()
            X[:, -ND:] = (X[:, -ND:] - mu[-ND:]) / sd[-ND:]
            Xt[:, -ND:] = (Xt[:, -ND:] - mu[-ND:]) / sd[-ND:]
    D0 = X.shape[1]
    rng = np.random.default_rng(SEED)
    Wr = rng.standard_normal((D0, HIDDEN)) / np.sqrt(D0)
    b = rng.uniform(0, 2 * np.pi, HIDDEN)
    st_ = max(1, D0 // 64)
    Phi = np.concatenate([X, np.cos(X @ Wr + b), X[:, ::st_][:, :64] ** 2], 1)
    Phit = np.concatenate([Xt, np.cos(Xt @ Wr + b), Xt[:, ::st_][:, :64] ** 2], 1)
    ends = np.arange(L, TRAIN_END - H + 1)
    Yd = np.stack([s[e:e + H] - s[e - 1] for e in ends])
    G = np.linalg.cholesky(Phi.T @ Phi + ALPHA * np.eye(Phi.shape[1]))
    W = np.linalg.solve(G.T, np.linalg.solve(G, Phi.T @ Yd))
    P = Phit @ W + a_te[:, 0][:, None]
    A = np.stack([s[TRAIN_END + i * H:TRAIN_END + i * H + H] for i in range(5)])
    mae = float(np.mean(np.abs(P - A)))
    print(f"  {task:14s} bank={bank:8s} std={std:11s} D0={D0:5d} MAE={mae:.4f}")
    return {"task": task, "bank": bank, "std": std, "D0": D0, "mae": round(mae, 4)}

def main():
    t0 = time.time()
    out = []
    for task, gen, H in (("thomas_H24", gen_thomas, H_T), ("trending_H48", lambda n: gen_trending(n, 1), H_R)):
        series = gen(2600)
        for bank in ("full", "compact"):
            for std in (["none", "all", "detail_only"] if bank == "full" else ["none"]):
                out.append(run(series, H, task, bank, std))
    m = {f"{r['task']}|{r['bank']}|{r['std']}": r["mae"] for r in out}
    repro_ok = all(abs(m.get(f"{t}|{bank}|none", 9e9) - v) <= 0.25 * v
                   for t in REF for bank, v in (("full", REF[t]["full"]), ("compact", REF[t]["compact"])))
    th, tr = m["thomas_H24|full|none"], m["thomas_H24|full|detail_only"]
    tf = m["thomas_H24|full|all"]
    if th > 5 * min(tf, tr):
        verdict = "SCALE_MISMATCH_CONFIRMED: standardizing detail coeffs (and/or all features) recovers Thomas; the 'toxicity' is a normalization artifact, not an intrinsic property of detail subbands. Keep all features + z-score bank."
    elif tf <= th / 2:
        verdict = "PARTIAL: standardization helps but full bank still far from compact; recommend removing details for chaotic regimes (signal-adaptive routing)."
    else:
        verdict = "DETAILS_INTRINSICALLY_TOXIC: even standardized detail coeffs do not fix Thomas; keep the compact/full signal-adaptive split."
    res = {"generated": time.ctime(), "repro_ok": repro_ok,
           "note": "REPRO_MISMATCH vs root-ablation refs -> directional control, not magnitude" if not repro_ok else "baseline configs reproduce references within 25%",
           "wall_s": round(time.time() - t0, 1), "results": out, "verdict": verdict}
    outdir = _workspace_paths.RESULTS_DIR
    json.dump(res, open(outdir / "results_bigdict_std_control.json", "w"), indent=1)
    with open(outdir / "results_bigdict_std_control.md", "w") as f:
        f.write(f"# BigDict Standardization Control\n\nrepro_ok={repro_ok} (vs root-ablation refs, 25% tol.)\n\n"
                + "\n".join(f"| {r['task']} | {r['bank']} | {r['std']} | D0={r['D0']} | MAE={r['mae']} |" for r in out)
                + f"\n\n## Verdict\n{verdict}\n")
    print(f"\nrepro_ok={repro_ok}\n{verdict}\n(wall {res['wall_s']}s)")

if __name__ == "__main__":
    main()
