"""S-16c — validation-correct α*/k selection for NLinear+KNN residual.

Train 8545 / Val 2880 / Test 2880 split (S-02).
Fit NLinear + KNN_R on train 8545 only.
On val 2880 rolling (2,161 origins), compute for each k:
  e_t = y_val[t] - y_N(t)   (NLinear error)
  r_t = R̂_KNN(t)            (KNN residual prediction)
  α* = clip( sum e·r / sum r² , 0,1)
  also fixed α {0.05,0.10,0.15,0.20} at each k
Select best (k,α) on val mean MAE, freeze, score on test (and W4 holdout).

Configs: k {16,32,48,64} × MI EMA0.9 norm1440, delays 14,28...
"""

from __future__ import annotations

import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods.nlinear_knn import NLinearKNNHybrid
from methods.neural_models import NLinear
from methods.knn_models import HeuristicLagKNN
from methods.baselines import seasonal_forecast as sf

DISJOINT_STARTS=(0,720,1440,2160)
TRAIN_END=8545
VAL_END=11425

def mae_rmse(p,a):
    err=np.asarray(p,float)-np.asarray(a,float)
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))

def rolling_on_val(train_8545, val, hybrid, alphas, ks):
    """Returns per-k per-alpha val MAE and per-origin e,r for α*."""
    # hybrid is already fit on train_8545, but we need to test different k and alpha
    # For each k, we need a separate hybrid fitted with that k
    # Instead, we fit hybrids per k outside and pass them in
    pass

def main():
    pd = get_protocol_data()
    fit_history, eval_series, test = pd.rolling_views()  # fit 11425, eval 14305, test 2880
    train_8545 = fit_history[:TRAIN_END]  # 8545
    val = fit_history[TRAIN_END:]  # 2880
    assert len(train_8545)==8545 and len(val)==2880 and len(test)==2880
    print(f"train {len(train_8545)} val {len(val)} test {len(test)}")

    # Fit NLinear on train 8545 for validation
    from methods.neural_models import NLinear
    nlinear_val = NLinear(input_length=336, ridge_alpha=1.0)
    nlinear_val.fit(train_8545, horizon=HORIZON)
    print("nlinear val fit done")

    # Fit hybrids per k on train 8545
    k_list=[16,32,48,64]
    hybrids_val={}
    for k in k_list:
        m = NLinearKNNHybrid(
            nlinear_length=336, knn_delays=(14,28,42,56,70), knn_q=3, knn_neighbors=k,
            knn_history_fraction=0.1, knn_normalize_scale=True, knn_scale_window=1440,
            knn_weights="distance", knn_ema_alpha=0.9, alpha=0.5
        )
        m.fit(train_8545, horizon=HORIZON)
        hybrids_val[k]=m
        print(f"  hybrid k={k} fit done")

    # Validation rolling: for each k, compute per-origin predictions for NLinear and KNN_R
    # We need to generate for each val origin t: history = train_8545 + val[:t], y_true = val[t:t+H]
    # For each hybrid k, we need y_n(t) and r_hat(t)
    # We can reuse the hybrid's predict logic but need to capture r_hat separately

    # Helper to get y_n and r_hat for a given hybrid and history
    def predict_components(hybrid, hist):
        # returns y_n and r_hat
        # need to swap histories as in previous rolling_arm_b
        orig_h = hybrid.history_
        orig_nl = hybrid.nlinear_.history_
        # handle ndim for nlinear
        try:
            if getattr(orig_nl, 'ndim', 1)==2 and hist.ndim==1:
                hybrid.nlinear_.history_ = hist[:, None]
            else:
                hybrid.nlinear_.history_ = hist
        except:
            hybrid.nlinear_.history_ = hist
        hybrid.history_ = hist
        try:
            series = hist
            idx = len(series)
            y_base = hybrid.nlinear_.predict()
            # KNN residual part
            # need to replicate hybrid's KNN predict for residual
            # Use same logic as hybrid.predict but separate r_hat
            if hybrid.knn_ema_alpha is not None:
                a = float(hybrid.knn_ema_alpha)
                ema = float(series[0])
                for t_ in range(1, idx):
                    ema = a*float(series[t_]) + (1-a)*ema
                anchor_knn = ema
            else:
                anchor_knn = HeuristicLagKNN(q=hybrid.knn_q, delays=hybrid.knn_delays)._anchor(series, idx, hybrid.knn_q)
            tmp = HeuristicLagKNN(q=hybrid.knn_q, delays=hybrid.knn_delays, normalize_scale=hybrid.knn_normalize_scale, scale_window=hybrid.knn_scale_window)
            scale_knn = tmp._window_scale(series, idx, hybrid.knn_normalize_scale, hybrid.knn_scale_window)
            x = tmp._lag_features(series, idx, hybrid.knn_delays, anchor_knn, hybrid.knn_normalize_scale, hybrid.knn_scale_window)
            # KNN residual
            if hybrid.knn_weights == "softmax":
                dist, ind = hybrid.knn_model_.kneighbors(x, n_neighbors=min(hybrid.knn_neighbors, len(hybrid.knn_X_)))
                d = dist[0]
                w = np.exp(-d / max(float(hybrid.knn_sigma_), 1e-12))
                w = w / w.sum()
                r_hat = (w @ hybrid.knn_R_[ind[0]])
            else:
                # for distance/uniform, use model predict
                # but model was trained on residual, so predict gives r_hat directly
                # Use kneighbors for distance-weighted, but for uniform/distance we can just call predict
                # To keep consistent, use predict
                r_hat = hybrid.knn_model_.predict(x)[0]
            return y_base, r_hat
        finally:
            hybrid.history_ = orig_h
            hybrid.nlinear_.history_ = orig_nl

    # For each k, collect val per-origin e and r
    val_results = {}
    for k in k_list:
        hybrid = hybrids_val[k]
        # collect per-origin
        per_origin_e = []
        per_origin_r = []
        per_origin_y_true = []
        for t in range(len(val)-HORIZON+1):  # 2161 origins
            hist = np.concatenate([train_8545, val[:t]]) if t>0 else train_8545
            # hist length = 8545 + t
            y_true = val[t:t+HORIZON]
            y_base, r_hat = predict_components(hybrid, hist)
            e = y_true - y_base
            per_origin_e.append(e)
            per_origin_r.append(r_hat)
            per_origin_y_true.append(y_true)
        # stack
        # per_origin_e and r are lists of (720,) arrays
        # For alpha sweep, we need per-origin MAE for each alpha: Ŷ = y_base + alpha*r_hat
        # So we can compute MAE for each alpha across all origins
        # Also compute analytical alpha*
        # Analytical: alpha* = sum(e·r)/sum(r²) per origin? Actually global alpha* across all origins: sum over all t and h of e_{t,h}*r_{t,h} / sum r²
        # Compute global
        e_all = np.concatenate(per_origin_e)  # (2161*720,)
        r_all = np.concatenate(per_origin_r)
        denom = float(np.sum(r_all*r_all))
        numer = float(np.sum(e_all*r_all))
        alpha_star = float(np.clip(numer/denom if denom>1e-12 else 0.0, 0, 1))
        print(f"k={k} alpha*={alpha_star:.4f} numer {numer:.1f} denom {denom:.1f}")

        # Evaluate fixed alphas and alpha*
        alphas = [0.05,0.10,0.15,0.20]
        for alpha in alphas + [alpha_star]:
            # compute MAE for this alpha across val origins
            maes=[]
            for e,r in zip(per_origin_e, per_origin_r):
                pred = e - alpha*r  # wait e = y - y_base, so y - (y_base+alpha*r) = e - alpha*r
                # Actually residual error after correction: y - (y_base+alpha*r) = e - alpha*r
                maes.append(np.mean(np.abs(e - alpha*r)))
            val_mae = float(np.mean(maes))
            key = f"k{k}_alpha{alpha:.2f}" if alpha!=alpha_star else f"k{k}_alpha_star_{alpha_star:.3f}"
            val_results[key] = {"val_mae": round(val_mae,4), "alpha_star": round(alpha_star,4) if "star" in key else None}
            print(f"  {key:25s} val {val_mae:.4f}")

        # also store per-origin for later test evaluation of best
        # keep best alpha for this k (lowest val mae)
        # find best fixed alpha
        best_fixed = min([a for a in alphas], key=lambda a: np.mean([np.mean(np.abs(e - a*r)) for e,r in zip(per_origin_e, per_origin_r)]))
        # also consider alpha*
        # we will not yet select global best across k, just per k
        val_results[f"k{k}_best"] = {"best_fixed_alpha": best_fixed, "alpha_star": round(alpha_star,4)}

    # Find global best (k, alpha) on val
    # Among all val_results entries that are fixed alphas, find lowest val_mae
    best_key = min([k for k in val_results if "alpha" in k and "best" not in k], key=lambda k: val_results[k]["val_mae"])
    print(f"\nGlobal best on val: {best_key} {val_results[best_key]}")
    # Also best k overall (lowest among best_fixed per k)
    # For simplicity, best is k with lowest val mae among its best fixed alpha
    best_k = min(k_list, key=lambda k: min(val_results[f"k{k}_alpha{a:.2f}"]["val_mae"] for a in [0.05,0.10,0.15,0.20]))
    print(f"Best k on val: {best_k}")

    # Freeze best config and score on test (and W4 holdout)
    # Best config is best_key, which encodes k and alpha
    # Parse k and alpha from best_key
    # best_key example: k32_alpha0.10 or k32_alpha_star_0.123
    # For holdout, we need to fit hybrid on full train 11425 (like S-16) with that k/alpha and score on test
    # But per your protocol, we should fit on train 8545+val (i.e., 11425) as frozen, then score on test, to match S-16's fit history
    # Actually S-16 fit on 11425, val was 8545 for selection, now test scoring should be on test with fit on 11425 (frozen)
    # So we fit a new hybrid on fit_history (11425) with best k/alpha and score rolling on test

    # Parse best k and alpha
    import re
    m=re.search(r"k(\d+)_alpha([\d\.]+)", best_key)
    if m:
        best_k_val=int(m.group(1))
        best_alpha_val=float(m.group(2))
    else:
        # star case
        m=re.search(r"k(\d+)_alpha_star_([\d\.]+)", best_key)
        best_k_val=int(m.group(1))
        best_alpha_val=float(m.group(2))
    print(f"Freeze best k={best_k_val} alpha={best_alpha_val} on full train 11425 and score on test...")

    # Fit frozen hybrid on full train
    frozen = NLinearKNNHybrid(
        nlinear_length=336, knn_delays=(14,28,42,56,70), knn_q=3, knn_neighbors=best_k_val,
        knn_history_fraction=0.1, knn_normalize_scale=True, knn_scale_window=1440,
        knn_weights="distance", knn_ema_alpha=0.9, alpha=best_alpha_val
    )
    fit_history_full, eval_series_full, test_full = get_protocol_data().rolling_views()
    frozen.fit(fit_history_full, horizon=HORIZON)
    print("  frozen fit done")

    def make_pa_frozen(m):
        def pa(hist):
            orig_h=m.history_
            orig_nl=m.nlinear_.history_
            try:
                if getattr(orig_nl, 'ndim',1)==2 and hist.ndim==1:
                    m.nlinear_.history_=hist[:,None]
                else:
                    m.nlinear_.history_=hist
                m.history_=hist
                return m.predict()
            finally:
                m.history_=orig_h
                m.nlinear_.history_=orig_nl
        return pa

    # Rolling on test
    def rolling_score(pa, eval_series, test):
        n=len(test)-HORIZON+1
        per=np.empty((n,2),float)
        for t in range(n):
            hist=eval_series[:11425+t]
            pred=pa(hist)
            per[t]=mae_rmse(pred, test[t:t+HORIZON])
        return float(np.mean(per[:,0])), float(np.mean(per[:,1])), {
            f"window_{i+1}": {"mae": float(per[t,0]), "rmse": float(per[t,1])}
            for i,t in enumerate(DISJOINT_STARTS)
        }, per

    pa_frozen = make_pa_frozen(frozen)
    rm, rr, disj, _ = rolling_score(pa_frozen, eval_series_full, test_full)
    print(f"Frozen best on test rolling {rm:.4f} / {rr:.4f}")
    print(f" W4 holdout (window_4) {disj['window_4']['mae']:.4f}")

    # Also score NLinear alone on test for delta
    nlin = NLinear(input_length=336, ridge_alpha=1.0)
    nlin.fit(fit_history_full, horizon=HORIZON)
    def make_pa_nl(m):
        def pa(hist):
            orig=m.history_
            try:
                if getattr(orig, 'ndim',1)==2 and hist.ndim==1:
                    m.history_=hist[:,None]
                else:
                    m.history_=hist
                return m.predict()
            finally:
                m.history_=orig
        return pa
    rm_nl,_,_,_=rolling_score(make_pa_nl(nlin), eval_series_full, test_full)
    print(f"NLinear on test {rm_nl:.4f}  delta hybrid-NLinear {rm - rm_nl:.4f}")

    out = HERE / "results_s16c.json"
    out.write_text(json.dumps({
        "val_results": val_results,
        "best_key": best_key,
        "best_k": best_k_val,
        "best_alpha": best_alpha_val,
        "test_rolling_mae": round(rm,4),
        "test_w4_mae": round(disj["window_4"]["mae"],4),
        "nlinear_test_mae": round(rm_nl,4),
        "delta": round(rm - rm_nl,4)
    }, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
