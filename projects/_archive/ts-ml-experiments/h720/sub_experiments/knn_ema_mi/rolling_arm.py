"""kNN EMA anchor + MI lags vs heuristic lags.

Tests user request: knn with anchor based on EMA plus lags set via
FNN/MI heuristic (τ=14, m=5 → 14,28,42,56,70) vs heuristic fast lags
(1,2,3,6,12,24). Both with SMA q=3 baseline vs EMA α sweep.

Frozen fit on train.csv (11,425 rows), 2,161 stride-1 origins.
Best kNN prior: 2.3466 @1440 distance, q3 heuristic, SMA.

Configs (all k=32, recent10%, norm1440 distance, weights distance):
- heuristic SMA q3 (baseline 2.3466)
- heuristic EMA 0.9, 0.7, 0.5, 0.3
- MI lags (14,28,42,56,70) SMA q3
- MI lags EMA 0.9, 0.7, 0.5, 0.3
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

HEURISTIC_DELAYS = (1,2,3,6,12,24)
MI_DELAYS = (14,28,42,56,70)

def main() -> int:
    fit_history, eval_series, test = get_protocol_data().rolling_views()
    _, t0_truth = get_protocol_data().forecast_views()
    assert len(fit_history)==11425

    def make_predictor(model):
        def pa(hist):
            orig = model.history_
            # for EMA, model.ema_ is stale if we swap history, but predict recomputes EMA from hist on the fly, so swapping history_ is enough
            # also need to handle that model.ema_ was computed from fit series, but predict will recompute — no need to swap ema_
            model.history_ = hist
            try:
                return model.predict()
            finally:
                model.history_ = orig
        return pa

    configs = []
    # heuristic baseline + EMA variants
    configs.append(("heur_SMA_q3", HeuristicLagKNN(q=3, neighbors=32, delays=HEURISTIC_DELAYS, history_fraction=0.1, normalize_scale=True, scale_window=1440, weights="distance", ema_alpha=None)))
    for a in [0.9, 0.7, 0.5, 0.3]:
        configs.append((f"heur_EMA_{a}", HeuristicLagKNN(q=3, neighbors=32, delays=HEURISTIC_DELAYS, history_fraction=0.1, normalize_scale=True, scale_window=1440, weights="distance", ema_alpha=a)))
    # MI lags
    configs.append(("mi_SMA_q3", HeuristicLagKNN(q=3, neighbors=32, delays=MI_DELAYS, history_fraction=0.1, normalize_scale=True, scale_window=1440, weights="distance", ema_alpha=None)))
    for a in [0.9, 0.7, 0.5, 0.3]:
        configs.append((f"mi_EMA_{a}", HeuristicLagKNN(q=3, neighbors=32, delays=MI_DELAYS, history_fraction=0.1, normalize_scale=True, scale_window=1440, weights="distance", ema_alpha=a)))

    print("fitting...")
    for label, m in configs:
        t0=time.time()
        m.fit(fit_history, horizon=HORIZON)
        print(f"  fit {label:18s} {time.time()-t0:.1f}s")

    results = {}
    # t0
    for label, m in configs:
        mae,_ = mae_rmse(m.predict(), t0_truth)
        results[label] = {"t0_mae": round(mae,4)}
        print(f"{label:18s} t0 {mae:.4f}")

    # rolling
    for label, m in configs:
        pa = make_predictor(m)
        rm, rr, disj, _ = rolling_score(pa, eval_series, test)
        base = results.get(label, {})
        base.update({"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj})
        results[label] = base
        print(f"{label:18s} rolling {rm:.4f} / {rr:.4f}")

    # anchors for sanity
    def daily_pa(hist): return sf(hist, HORIZON, "daily")
    def pers_pa(hist): return np.full(HORIZON, hist[-1])
    for name, pa in [("daily", daily_pa), ("persistence", pers_pa)]:
        rm, rr, disj, _ = rolling_score(pa, eval_series, test)
        results[name] = {"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj}
        print(f"{name:18s} rolling {rm:.4f}")

    # gate: heuristic SMA q3 must reproduce 2.3466
    assert abs(results["heur_SMA_q3"]["rolling_mae"] - 2.3466) < 1e-4, results["heur_SMA_q3"]
    assert abs(results["daily"]["rolling_mae"] - 2.5491) < 1e-4

    out = HERE / "results_rolling.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    print("\n--- EMA+MI summary sorted ---")
    for k in sorted(results, key=lambda x: results[x].get("rolling_mae", 9)):
        if "rolling_mae" in results[k]:
            print(f"{k:18s} {results[k]['rolling_mae']:.4f} (t0 {results[k].get('t0_mae','-')})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
