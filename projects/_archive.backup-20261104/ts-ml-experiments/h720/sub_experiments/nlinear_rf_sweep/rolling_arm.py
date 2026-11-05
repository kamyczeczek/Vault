"""NLinearRF rolling evaluation — NLinear window (336/96) + RF readout.

Frozen fit 11,425, 2,161 origins, compare vs NLinear Ridge 2.0571.
Configs: L=336 trees=100, L=96 trees=100 (like NLinear L sweep).
"""

from __future__ import annotations

import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, VALIDATION_END, get_protocol_data
from methods.nlinear_rf import NLinearRF
from methods.neural_models import NLinear
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
            try:
                return m.predict()
            finally:
                m.history_=orig
        return pa

    configs=[
        ("nlinear_rf_L336_t100", NLinearRF(input_length=336, trees=100)),
        ("nlinear_rf_L96_t100", NLinearRF(input_length=96, trees=100)),
        ("nlinear_L336", NLinear(input_length=336, ridge_alpha=1.0)),
        ("nlinear_L96", NLinear(input_length=96, ridge_alpha=1.0)),
    ]
    print("fitting...")
    for label,m in configs:
        t0=time.time()
        m.fit(fit_history, horizon=HORIZON)
        print(f"  fit {label:20s} {time.time()-t0:.1f}s")

    results={}
    for label,m in configs:
        mae,_=mae_rmse(m.predict(), t0_truth)
        results[label]={"t0_mae": round(mae,4)}
        print(f"{label:20s} t0 {mae:.4f}")

    for label,m in configs:
        pa=make_pa(m)
        rm,rr,disj,_=rolling_score(pa, eval_series, test)
        base=results.get(label,{})
        base.update({"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj})
        results[label]=base
        print(f"{label:20s} rolling {rm:.4f} / {rr:.4f}")

    # anchors
    for name,pa in [("daily", lambda h: sf(h, HORIZON, "daily")), ("persistence", lambda h: np.full(HORIZON, h[-1]))]:
        rm,rr,disj,_=rolling_score(pa, eval_series, test)
        results[name]={"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj}
        print(f"{name:20s} rolling {rm:.4f}")
        assert abs(rm - (2.5491 if name=="daily" else 2.5985)) < 1e-4

    # gate
    assert abs(results["nlinear_L336"]["rolling_mae"] - 2.0571) < 1e-4
    assert abs(results["nlinear_L96"]["rolling_mae"] - 2.0925) < 1e-4

    out=HERE/"results_rolling.json"
    out.write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(f"wrote {out}")
    print("\n--- NLinearRF summary ---")
    for k in sorted(results, key=lambda x: results[x].get("rolling_mae",9)):
        if "rolling_mae" in results[k]:
            print(f"{k:20s} {results[k]['rolling_mae']:.4f} (t0 {results[k].get('t0_mae','-')})")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
