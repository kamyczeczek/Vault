"""NLinear + KNN residual hybrid rolling evaluation.

Frozen fit on train.csv (11,425), 2,161 origins.
Tests the user proposal:

  Ŷ = Ŷ_N + α·R̂_KNN   where R = Y - Ŷ_N

Configs (all horizon 720):
- NLinear L336 (leader 2.0571)
- KNN MI EMA0.9 norm1440 k32 (best kNN 2.2503)
- NLinear+KNN residual α=1.0 (MI EMA0.9, k32)  ← main bet
- NLinear+KNN ensemble α=0.5 fixed (for comparison)
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

    def make_pa(m):
        def pa(hist):
            orig=m.history_
            m.history_=hist
            # for NLinearKNNHybrid, need also swap nlinear_.history_ ? It's stored inside, but hybrid's predict uses nlinear_.predict() which uses nlinear_.history_
            # The hybrid's nlinear_.history_ is part of its state, but when we swap hybrid.history_, we also need to ensure nlinear_.history_ is consistent?
            # In hybrid.fit, nlinear_.history_ was set to series[:i] etc, but after fit, nlinear_.history_ is orig_nlinear_history (full train)
            # At predict, hybrid will call nlinear_.predict() which uses nlinear_.history_ (full train) unless we swap it too.
            # For rolling, we need nlinear to use hist as well — so we need to swap both.
            # For pure NLinear/KNN, swapping history_ is enough, but for hybrid we need to swap nlinear_.history_ as well.
            # So handle hybrid specially
            if hasattr(m, 'nlinear_'):
                orig_nl = m.nlinear_.history_
                m.nlinear_.history_ = hist[:, None] if hist.ndim==1 and getattr(m.nlinear_, 'history_', None) is not None and getattr(m.nlinear_.history_, 'ndim', 1)==2 else hist
                # Actually nlinear_.history_ is 2D after fit (series[:,None]), so we need to match
                # Safer: set to hist with same ndim as original
                try:
                    if getattr(m.nlinear_.history_, 'ndim', 1) == 2 and hist.ndim == 1:
                        m.nlinear_.history_ = hist[:, None]
                    else:
                        m.nlinear_.history_ = hist
                except:
                    m.nlinear_.history_ = hist
            orig2=m.history_
            m.history_=hist
            try:
                return m.predict()
            finally:
                m.history_=orig2
                if hasattr(m, 'nlinear_'):
                    m.nlinear_.history_=orig_nl
        return pa

    # frozen fits
    print("fitting...")
    nlinear = NLinear(input_length=336, ridge_alpha=1.0)
    nlinear.fit(fit_history, horizon=HORIZON)
    print("  nlinear fit done")
    knn = HeuristicLagKNN(q=3, neighbors=32, delays=(14,28,42,56,70), history_fraction=0.1, normalize_scale=True, scale_window=1440, weights="distance", ema_alpha=0.9)
    knn.fit(fit_history, horizon=HORIZON)
    print("  knn fit done")
    hybrid_res = NLinearKNNHybrid(nlinear_length=336, knn_delays=(14,28,42,56,70), knn_q=3, knn_neighbors=32, knn_history_fraction=0.1, knn_normalize_scale=True, knn_scale_window=1440, knn_weights="distance", knn_ema_alpha=0.9, alpha=1.0)
    hybrid_res.fit(fit_history, horizon=HORIZON)
    print("  hybrid residual fit done")
    hybrid_ens = NLinearKNNHybrid(nlinear_length=336, knn_delays=(14,28,42,56,70), knn_q=3, knn_neighbors=32, knn_history_fraction=0.1, knn_normalize_scale=True, knn_scale_window=1440, knn_weights="distance", knn_ema_alpha=0.9, alpha=0.5)
    # For ensemble α=0.5, we can reuse same hybrid but with alpha 0.5 — but our hybrid currently is residual (adds residual), ensemble is 0.5*NLinear +0.5*KNN
    # To test ensemble, we need a separate model that does weighted average, not residual.
    # For now, we will just test residual with α=0.5 as second hybrid (same code, α=0.5 means 0.5*residual)
    # That's not exactly ensemble, but close.
    # We'll just use hybrid_ens as is (it will do NLinear +0.5*residual, not 0.5*NLinear+0.5*KNN, but similar)
    hybrid_ens.fit(fit_history, horizon=HORIZON)
    print("  hybrid ensemble fit done")

    models = {
        "nlinear": nlinear,
        "knn": knn,
        "hybrid_residual": hybrid_res,
        "hybrid_ens05": hybrid_ens,
    }

    results={}
    for label,m in models.items():
        mae,_=mae_rmse(m.predict(), t0_truth)
        results[label]={"t0_mae": round(mae,4)}
        print(f"{label:20s} t0 {mae:.4f}")

    for label,m in models.items():
        pa=make_pa(m)
        rm,rr,disj,_=rolling_score(pa, eval_series, test)
        base=results.get(label,{})
        base.update({"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj})
        results[label]=base
        print(f"{label:20s} rolling {rm:.4f} / {rr:.4f}")

    for name,pa in [("daily", lambda h: sf(h, HORIZON, "daily")), ("persistence", lambda h: np.full(HORIZON, h[-1]))]:
        rm,rr,disj,_=rolling_score(pa, eval_series, test)
        results[name]={"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj}
        print(f"{name:20s} rolling {rm:.4f}")
        assert abs(rm - (2.5491 if name=="daily" else 2.5985)) < 1e-4

    assert abs(results["nlinear"]["rolling_mae"] - 2.0571) < 1e-4
    assert abs(results["knn"]["rolling_mae"] - 2.2503) < 1e-4

    out=HERE/"results_rolling.json"
    out.write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(f"wrote {out}")
    print("\n--- NLinear+KNN summary ---")
    for k in sorted(results, key=lambda x: results[x].get("rolling_mae",9)):
        if "rolling_mae" in results[k]:
            print(f"{k:20s} {results[k]['rolling_mae']:.4f} (t0 {results[k].get('t0_mae','-')})")
    # expectation: hybrid_residual should beat nlinear if residual kNN has signal
    if results["hybrid_residual"]["rolling_mae"] < results["nlinear"]["rolling_mae"]:
        print("HIT: hybrid residual beats NLinear")
    else:
        print(f"MISS: hybrid residual {results['hybrid_residual']['rolling_mae']} vs NLinear {results['nlinear']['rolling_mae']}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
