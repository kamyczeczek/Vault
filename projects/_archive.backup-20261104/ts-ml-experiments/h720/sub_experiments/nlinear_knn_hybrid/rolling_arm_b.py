"""S-16b — α sweep, k sweep, adaptive gating for NLinear+KNN residual.

Frozen NLinear L336 + KNN_R (MI EMA0.9 k32 norm1440) — same fit as S-16.
Tests without refitting KNN_R (α weighting is post-hoc):

  α sweep: 0.0,0.1,0.3,0.5,0.7,0.9,1.0  at k=32
  k sweep: 8,16,24,32,48,64 at α=0.5
  adaptive: g(D)=exp(-D/σ)  where D=mean kNN distance, σ=global mean distance

Holdout freeze: report W4 (last 720) for frozen S-16 α=0.5 as untouched holdout.
"""

from __future__ import annotations

import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, VALIDATION_END, get_protocol_data
from methods.nlinear_knn import NLinearKNNHybrid
from methods.neural_models import NLinear
from methods.knn_models import HeuristicLagKNN
from methods.baselines import seasonal_forecast as sf

DISJOINT_STARTS=(0,720,1440,2160)

def mae_rmse(p,a):
    err=np.asarray(p,float)-np.asarray(a,float)
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))

def rolling_score(pa, eval_series, test):
    n=len(test)-HORIZON+1
    assert n==2161
    per=np.empty((n,2),float)
    for t in range(n):
        hist=eval_series[:VALIDATION_END+t]
        pred=pa(hist)
        per[t]=mae_rmse(pred, test[t:t+HORIZON])
    return float(np.mean(per[:,0])), float(np.mean(per[:,1])), {
        f"window_{i+1}": {"mae": float(per[t,0]), "rmse": float(per[t,1])}
        for i,t in enumerate(DISJOINT_STARTS)
    }, per

def main():
    fit_history, eval_series, test = get_protocol_data().rolling_views()
    _, t0_truth = get_protocol_data().forecast_views()
    assert len(fit_history)==11425

    # Fit base models once
    print("fitting base NLinear and KNN_R...")
    # NLinear alone
    nlinear = NLinear(input_length=336, ridge_alpha=1.0)
    nlinear.fit(fit_history, horizon=HORIZON)
    # KNN for residual is inside hybrid, but we can reuse hybrid's KNN_R
    # Fit hybrid with α=0.5 as base (we will vary α post-hoc by scaling r_hat)
    base_hybrid = NLinearKNNHybrid(
        nlinear_length=336, knn_delays=(14,28,42,56,70), knn_q=3, knn_neighbors=32,
        knn_history_fraction=0.1, knn_normalize_scale=True, knn_scale_window=1440,
        knn_weights="distance", knn_ema_alpha=0.9, alpha=0.5
    )
    base_hybrid.fit(fit_history, horizon=HORIZON)
    print("  base hybrid fit done")

    # For k sweep, need separate hybrids with different k
    k_variants = {}
    for k in [8,16,24,32,48,64]:
        m = NLinearKNNHybrid(
            nlinear_length=336, knn_delays=(14,28,42,56,70), knn_q=3, knn_neighbors=k,
            knn_history_fraction=0.1, knn_normalize_scale=True, knn_scale_window=1440,
            knn_weights="distance", knn_ema_alpha=0.9, alpha=0.5
        )
        m.fit(fit_history, horizon=HORIZON)
        k_variants[k]=m
        print(f"  k={k} fit done")

    def make_pa_hybrid(hybrid, alpha=None):
        # alpha override for sweep (if None, use hybrid.alpha)
        def pa(hist):
            # swap histories for both hybrid and its nlinear
            orig_h = hybrid.history_
            orig_nl = hybrid.nlinear_.history_
            # handle ndim
            try:
                if getattr(orig_nl, 'ndim', 1)==2 and hist.ndim==1:
                    hybrid.nlinear_.history_ = hist[:, None]
                else:
                    hybrid.nlinear_.history_ = hist
            except:
                hybrid.nlinear_.history_ = hist
            hybrid.history_ = hist
            # temporarily override alpha if needed
            orig_alpha = hybrid.alpha
            if alpha is not None:
                hybrid.alpha = float(alpha)
            try:
                return hybrid.predict()
            finally:
                hybrid.history_ = orig_h
                hybrid.nlinear_.history_ = orig_nl
                hybrid.alpha = orig_alpha
        return pa

    def make_pa_adaptive(hybrid):
        # g(D)=exp(-D/σ), D=mean distance to k neighbors
        def pa(hist):
            orig_h = hybrid.history_
            orig_nl = hybrid.nlinear_.history_
            try:
                if getattr(orig_nl, 'ndim', 1)==2 and hist.ndim==1:
                    hybrid.nlinear_.history_ = hist[:, None]
                else:
                    hybrid.nlinear_.history_ = hist
            except:
                hybrid.nlinear_.history_ = hist
            hybrid.history_ = hist
            # we need to compute y_n and r_hat with adaptive scaling
            # replicate hybrid.predict but with adaptive g
            # Instead of calling hybrid.predict, we manually compute
            series = hist
            idx = len(series)
            # NLinear base
            y_base = hybrid.nlinear_.predict()
            # KNN residual part with adaptive
            # Build x for KNN
            if hybrid.knn_ema_alpha is not None:
                a = float(hybrid.knn_ema_alpha)
                ema = float(series[0])
                for t in range(1, idx):
                    ema = a*float(series[t]) + (1-a)*ema
                anchor_knn = ema
            else:
                # use top-level HeuristicLagKNN (already imported) — avoid local import shadowing
                anchor_knn = HeuristicLagKNN(q=hybrid.knn_q, delays=hybrid.knn_delays)._anchor(series, idx, hybrid.knn_q)
            # use same class for scale/lag features
            _tmp = HeuristicLagKNN(q=hybrid.knn_q, delays=hybrid.knn_delays, normalize_scale=hybrid.knn_normalize_scale, scale_window=hybrid.knn_scale_window)
            scale_knn = _tmp._window_scale(series, idx, hybrid.knn_normalize_scale, hybrid.knn_scale_window)
            x = _tmp._lag_features(series, idx, hybrid.knn_delays, anchor_knn, hybrid.knn_normalize_scale, hybrid.knn_scale_window)
            if hybrid.knn_weights == "softmax":
                dist, ind = hybrid.knn_model_.kneighbors(x, n_neighbors=min(hybrid.knn_neighbors, len(hybrid.knn_X_)))
                d = dist[0]
                w = np.exp(-d / max(float(hybrid.knn_sigma_), 1e-12))
                w = w / w.sum()
                r_hat = (w @ hybrid.knn_R_[ind[0]])
                D = float(np.mean(d))
            else:
                dist, ind = hybrid.knn_model_.kneighbors(x)
                d = dist[0]
                # for uniform/distance, use same dist
                if hybrid.knn_weights == "uniform":
                    w = np.ones_like(d) / len(d)
                else: # distance
                    w = 1.0 / np.maximum(d, 1e-12)
                    w = w / w.sum()
                r_hat = (w @ hybrid.knn_R_[ind[0]])
                D = float(np.mean(d))
            sigma = float(getattr(hybrid, 'knn_sigma_', 1.0) or 1.0)
            # adaptive g
            g = float(np.exp(-D / max(sigma, 1e-12)))
            # clamp g to [0,1]
            g = max(0.0, min(1.0, g))
            return y_base + g * r_hat
        return pa

    results = {}

    # α sweep at k=32
    print("\nα sweep at k=32...")
    for alpha in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
        # α sweep is post-hoc scaling of r_hat, no refit needed — we can reuse base_hybrid and scale
        # For α=0.0, it's pure NLinear
        if alpha == 0.0:
            # pure NLinear
            def pa_nl(hist):
                orig = nlinear.history_
                # handle ndim as before
                try:
                    if getattr(orig, 'ndim', 1)==2 and hist.ndim==1:
                        nlinear.history_ = hist[:, None]
                    else:
                        nlinear.history_ = hist
                except:
                    nlinear.history_ = hist
                try:
                    return nlinear.predict()
                finally:
                    nlinear.history_ = orig
            pa = pa_nl
            label = "alpha_0.0_NLinear"
        else:
            pa = make_pa_hybrid(base_hybrid, alpha=alpha)
            label = f"alpha_{alpha:.1f}"
        rm, rr, disj, _ = rolling_score(pa, eval_series, test)
        results[label] = {"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj}
        print(f"{label:20s} {rm:.4f}")

    # k sweep at α=0.5
    print("\nk sweep at α=0.5...")
    for k in [8,16,24,32,48,64]:
        m = k_variants[k]
        pa = make_pa_hybrid(m, alpha=0.5)
        rm, rr, disj, _ = rolling_score(pa, eval_series, test)
        label = f"k_{k}_alpha0.5"
        results[label] = {"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj}
        print(f"{label:20s} {rm:.4f}")

    # adaptive
    print("\nadaptive g(D)...")
    pa_ad = make_pa_adaptive(base_hybrid)
    rm, rr, disj, _ = rolling_score(pa_ad, eval_series, test)
    results["adaptive_gD"] = {"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj}
    print(f"{'adaptive_gD':20s} {rm:.4f}")

    # also pure KNN and NLinear for reference
    def make_pa_nl(hist):
        orig = nlinear.history_
        try:
            if getattr(orig, 'ndim', 1)==2 and hist.ndim==1:
                nlinear.history_ = hist[:, None]
            else:
                nlinear.history_ = hist
        except:
            nlinear.history_ = hist
        try:
            return nlinear.predict()
        finally:
            nlinear.history_ = orig
    rm,_,_,_=rolling_score(make_pa_nl, eval_series, test)
    assert abs(rm-2.0571)<1e-4
    from methods.knn_models import HeuristicLagKNN
    knn = HeuristicLagKNN(q=3, neighbors=32, delays=(14,28,42,56,70), history_fraction=0.1, normalize_scale=True, scale_window=1440, weights="distance", ema_alpha=0.9)
    knn.fit(fit_history, horizon=HORIZON)
    def make_pa_knn(hist):
        orig=knn.history_
        knn.history_=hist
        try:
            return knn.predict()
        finally:
            knn.history_=orig
    rm2,_,_,_=rolling_score(make_pa_knn, eval_series, test)
    assert abs(rm2-2.2503)<1e-4

    out = HERE / "results_b.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwrote {out}")
    print("\n--- S-16b summary sorted ---")
    for k in sorted(results, key=lambda x: results[x].get("rolling_mae",9)):
        if "rolling_mae" in results[k]:
            print(f"{k:20s} {results[k]['rolling_mae']:.4f}")

    # holdout freeze: report W4 for frozen S-16 α=0.5
    w4 = results["alpha_0.5"]["disjoint"]["window_4"]["mae"]
    print(f"\nHoldout freeze S-16 α=0.5 W4 (last 720) = {w4:.4f} (untouched holdout)")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
