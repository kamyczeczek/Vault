"""kNN scale-window × weights sweep — direction #1 for kNN family.

Tests the scale-sensitive distance hypothesis: instance norm helps kNN
strongly (S-04: 2.5583 → 2.3815 at window 720) but window 720 vs 168
difference was 0.06; windows 24/336/1440 are untried. Also tests
neighbour weighting (uniform vs distance 1/d vs softmax exp(-d/σ)).

Frozen fit on train.csv (11,425 rows), 2,161 stride-1 origins.
Anchors: kNN raw 2.5583, kNN norm720 2.3815, daily 2.5491, persistence 2.5985.

Configs (all q=3, k=32, recent 10%, delays 1,2,3,6,12,24):
- raw (no norm)
- norm 24/72/168/336/720/1440 × distance
- norm720 × uniform, softmax
"""

from __future__ import annotations

import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, VALIDATION_END, get_protocol_data
from methods.knn_models import HeuristicLagKNN
from methods.baselines import seasonal_forecast as sf

DISJOINT_STARTS = (0, 720, 1440, 2160)

ROLLING_ANCHORS = {
    "knn_raw": 2.5583,
    "knn_norm720": 2.3815,
    "daily": 2.5491,
    "persistence": 2.5985,
}

def mae_rmse(pred, actual):
    err = np.asarray(pred, float) - np.asarray(actual, float)
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))

def rolling_score(predict_at, eval_series, test):
    n = len(test) - HORIZON + 1
    assert n == 2161
    per = np.empty((n,2), float)
    for t in range(n):
        hist = eval_series[: VALIDATION_END + t]
        pred = predict_at(hist)
        assert len(pred)==HORIZON
        per[t] = mae_rmse(pred, test[t:t+HORIZON])
    return float(np.mean(per[:,0])), float(np.mean(per[:,1])), {
        f"window_{i+1}": {"mae": float(per[t,0]), "rmse": float(per[t,1])}
        for i,t in enumerate(DISJOINT_STARTS)
    }, per

def main() -> int:
    fit_history, eval_series, test = get_protocol_data().rolling_views()
    _, t0_truth = get_protocol_data().forecast_views()
    assert len(fit_history)==11425

    def make_predictor(model):
        def pa(hist):
            orig = model.history_
            model.history_ = hist
            try:
                return model.predict()
            finally:
                model.history_ = orig
        return pa

    configs = []
    # raw baseline
    configs.append(("knn_raw", HeuristicLagKNN(q=3, neighbors=32, delays=(1,2,3,6,12,24), history_fraction=0.1, normalize_scale=False)))
    # scale windows × distance
    for w in [24,72,168,336,720,1440]:
        configs.append((f"knn_norm{w}_distance", HeuristicLagKNN(q=3, neighbors=32, delays=(1,2,3,6,12,24), history_fraction=0.1, normalize_scale=True, scale_window=w, weights="distance")))
    # weights variants at best window 720
    configs.append(("knn_norm720_uniform", HeuristicLagKNN(q=3, neighbors=32, delays=(1,2,3,6,12,24), history_fraction=0.1, normalize_scale=True, scale_window=720, weights="uniform")))
    configs.append(("knn_norm720_softmax", HeuristicLagKNN(q=3, neighbors=32, delays=(1,2,3,6,12,24), history_fraction=0.1, normalize_scale=True, scale_window=720, weights="softmax")))

    # frozen fits
    print("fitting kNN variants...")
    for label, m in configs:
        t0=time.time()
        m.fit(fit_history, horizon=HORIZON)
        print(f"  fit {label:25s} {time.time()-t0:.1f}s")

    results = {}
    # t0
    for label, m in configs:
        mae,_ = mae_rmse(m.predict(), t0_truth)
        results[label] = {"t0_mae": round(mae,4)}
        print(f"{label:25s} t0 {mae:.4f}")

    # rolling
    for label, m in configs:
        pa = make_predictor(m)
        rm, rr, disj, _ = rolling_score(pa, eval_series, test)
        base = results.get(label, {})
        base.update({"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj})
        results[label] = base
        print(f"{label:25s} rolling {rm:.4f} / {rr:.4f}")

    # anchors daily/persistence
    def daily_pa(hist): return sf(hist, HORIZON, "daily")
    def pers_pa(hist): return np.full(HORIZON, hist[-1])
    for name, pa in [("daily", daily_pa), ("persistence", pers_pa)]:
        rm, rr, disj, _ = rolling_score(pa, eval_series, test)
        results[name] = {"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj}
        print(f"{name:25s} rolling {rm:.4f}")
        assert abs(rm - ROLLING_ANCHORS[name]) < 1e-4

    # anchor checks for knn
    assert abs(results["knn_raw"]["rolling_mae"] - 2.5583) < 1e-4, results["knn_raw"]
    # knn_norm720 distance should reproduce 2.3815
    assert abs(results["knn_norm720_distance"]["rolling_mae"] - 2.3815) < 1e-4, results["knn_norm720_distance"]

    out = HERE / "results_rolling.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    print("\n--- kNN scale summary (rolling MAE) sorted ---")
    for k in sorted(results, key=lambda x: results[x].get("rolling_mae", 9)):
        if "rolling_mae" in results[k]:
            print(f"{k:25s} {results[k]['rolling_mae']:.4f}  (t0 {results[k].get('t0_mae','-')})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
