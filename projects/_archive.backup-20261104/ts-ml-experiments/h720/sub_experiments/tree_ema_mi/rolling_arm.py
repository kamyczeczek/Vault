"""Tree EMA + MI vs heuristic lags.

HeuristicLagDecisionTree (pure tree, no ELM hidden) with max_depth=4
(S-09 winner depth) — test if MI lags + EMA anchor help tree as it did kNN.

Frozen fit 11,425, 2,161 origins, norm not used for tree (tree is scale-invariant,
so scale_window irrelevant — keep raw). But we keep same lag sets as kNN.

Configs (q=3, max_depth=4, history 0.1):
- heuristic SMA q3
- heuristic EMA 0.9, 0.7, 0.5, 0.3
- MI SMA q3
- MI EMA 0.9, 0.7, 0.5, 0.3
"""

from __future__ import annotations

import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, VALIDATION_END, get_protocol_data
from methods.knn_models import HeuristicLagDecisionTree
from methods.baselines import seasonal_forecast as sf

DISJOINT_STARTS = (0,720,1440,2160)

def mae_rmse(pred, actual):
    err = np.asarray(pred,float)-np.asarray(actual,float)
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))

def rolling_score(predict_at, eval_series, test):
    n=len(test)-HORIZON+1
    assert n==2161
    per=np.empty((n,2),float)
    for t in range(n):
        hist=eval_series[:VALIDATION_END+t]
        pred=predict_at(hist)
        per[t]=mae_rmse(pred, test[t:t+HORIZON])
    return float(np.mean(per[:,0])), float(np.mean(per[:,1])), {
        f"window_{i+1}": {"mae": float(per[t,0]), "rmse": float(per[t,1])}
        for i,t in enumerate(DISJOINT_STARTS)
    }, per

HEURISTIC_DELAYS=(1,2,3,6,12,24)
MI_DELAYS=(14,28,42,56,70)

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

    configs=[]
    configs.append(("heur_SMA_q3", HeuristicLagDecisionTree(q=3, delays=HEURISTIC_DELAYS, max_depth=4, history_fraction=0.1, ema_alpha=None)))
    for a in [0.9,0.7,0.5,0.3]:
        configs.append((f"heur_EMA_{a}", HeuristicLagDecisionTree(q=3, delays=HEURISTIC_DELAYS, max_depth=4, history_fraction=0.1, ema_alpha=a)))
    configs.append(("mi_SMA_q3", HeuristicLagDecisionTree(q=3, delays=MI_DELAYS, max_depth=4, history_fraction=0.1, ema_alpha=None)))
    for a in [0.9,0.7,0.5,0.3]:
        configs.append((f"mi_EMA_{a}", HeuristicLagDecisionTree(q=3, delays=MI_DELAYS, max_depth=4, history_fraction=0.1, ema_alpha=a)))

    print("fitting trees...")
    for label,m in configs:
        t0=time.time()
        m.fit(fit_history, horizon=HORIZON)
        print(f"  fit {label:18s} {time.time()-t0:.1f}s")

    results={}
    for label,m in configs:
        mae,_=mae_rmse(m.predict(), t0_truth)
        results[label]={"t0_mae": round(mae,4)}
        print(f"{label:18s} t0 {mae:.4f}")

    for label,m in configs:
        pa=make_pa(m)
        rm,rr,disj,_=rolling_score(pa, eval_series, test)
        base=results.get(label,{})
        base.update({"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj})
        results[label]=base
        print(f"{label:18s} rolling {rm:.4f} / {rr:.4f}")

    # anchors
    def daily_pa(hist): return sf(hist, HORIZON, "daily")
    def pers_pa(hist): return np.full(HORIZON, hist[-1])
    for name,pa in [("daily", daily_pa), ("persistence", pers_pa)]:
        rm,rr,disj,_=rolling_score(pa, eval_series, test)
        results[name]={"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj}
        print(f"{name:18s} rolling {rm:.4f}")
        assert abs(rm - (2.5491 if name=="daily" else 2.5985)) < 1e-4

    # gate: heur SMA should be around 2.6-2.8 (tree baseline)
    print(f"heur_SMA rolling {results['heur_SMA_q3']['rolling_mae']}")

    out=HERE/"results_rolling.json"
    out.write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(f"wrote {out}")
    print("\n--- tree EMA+MI sorted ---")
    for k in sorted(results, key=lambda x: results[x].get("rolling_mae",9)):
        if "rolling_mae" in results[k]:
            print(f"{k:18s} {results[k]['rolling_mae']:.4f} (t0 {results[k].get('t0_mae','-')})")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
