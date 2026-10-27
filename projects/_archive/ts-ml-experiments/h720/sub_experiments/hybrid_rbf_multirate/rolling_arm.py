"""Hybrid MultiRateRBF rolling evaluation (S-13).

Frozen fit on train.csv (11,425 rows), 2,161 stride-1 origins.
Tests complementarity hypothesis: RBF W4 drift robustness + multirate mean
correction → hybrid should beat both parents and approach NLinear.

Configs:
- hybrid (1,)      ≡ RBFELM identity (should be 2.2812)
- hybrid (1,2)
- hybrid (1,4)
- hybrid (1,2,4)   ← main bet (S-10 winner rates + RBF)
- hybrid (1,2,4,8) ← check if 8 still hurts hybrid (S-10: 8 hurt)
- anchors: RBFELM raw, MultiRateELM (1,2,4), NLinear L336, ELM, daily, persistence

Gates: identity hybrid(1,)==RBFELM 0.0 diff, rolling anchors fail-loud,
      shape 720, determinism (second fit byte-identical for hybrid 1,2,4).
"""

from __future__ import annotations

import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, VALIDATION_END, get_protocol_data
from methods.baselines import seasonal_forecast
from methods.multirate_rbf import MultiRateRBF
from methods.rbf import RBFELM
from methods.multirate import MultiRateELM
from methods.neural_models import HeuristicLagELM, NLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)

ROLLING_ANCHORS = {
    "rbf_raw": 2.2812,
    "multirate_R1_2_4": 2.2744,
    "elm_h64_full": 2.3092,
    "nlinear_L336": 2.0571,
    "daily": 2.5491,
    "persistence": 2.5985,
}

def mae_rmse(pred, actual):
    err = np.asarray(pred, float) - np.asarray(actual, float)
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))

def rolling_score(predict_at, eval_series, test):
    n_origins = len(test) - HORIZON + 1
    assert n_origins == 2161, n_origins
    per = np.empty((n_origins, 2), float)
    for t in range(n_origins):
        hist = eval_series[: VALIDATION_END + t]
        pred = predict_at(hist)
        assert len(pred) == HORIZON
        per[t] = mae_rmse(pred, test[t:t+HORIZON])
    return float(np.mean(per[:,0])), float(np.mean(per[:,1])), {
        f"window_{i+1}": {"mae": float(per[t,0]), "rmse": float(per[t,1])}
        for i,t in enumerate(DISJOINT_STARTS)
    }, per

def main() -> int:
    fit_history, eval_series, test = get_protocol_data().rolling_views()
    assert len(fit_history)==11425 and len(test)==2880, f"{len(fit_history)} {len(test)}"
    # t=0 ground truth for sanity
    _, t0_truth = get_protocol_data().forecast_views()
    assert t0_truth.shape==(HORIZON,)

    # helpers to build predict_at closure that swaps history_
    def make_predictor(model):
        def predict_at(hist):
            # swap history_, keep fitted model weights, call predict
            orig = model.history_
            model.history_ = hist
            try:
                return model.predict()
            finally:
                model.history_ = orig
        return predict_at

    # --- frozen fits ----------------------------------------------------
    print("fitting hybrids...")
    hybrids = {
        "hybrid_R1": MultiRateRBF(rates=(1,), hidden_dim=64, ridge_alpha=1.0),
        "hybrid_R1_2": MultiRateRBF(rates=(1,2), hidden_dim=64),
        "hybrid_R1_4": MultiRateRBF(rates=(1,4), hidden_dim=64),
        "hybrid_R1_2_4": MultiRateRBF(rates=(1,2,4), hidden_dim=64),
        "hybrid_R1_2_4_8": MultiRateRBF(rates=(1,2,4,8), hidden_dim=64),
    }
    for k,m in hybrids.items():
        m.fit(fit_history, horizon=HORIZON)
        print(f"  fit {k} done")

    print("fitting anchors...")
    rbf = RBFELM(hidden_dim=64, ridge_alpha=1.0)
    rbf.fit(fit_history, horizon=HORIZON)
    mr = MultiRateELM(rates=(1,2,4), hidden_dim=64, lags_per_rate=(1,2,3,6,12))
    mr.fit(fit_history, horizon=HORIZON)
    nlin = NLinear(input_length=336, ridge_alpha=1.0)
    nlin.fit(fit_history, horizon=HORIZON)
    elm = HeuristicLagELM(hidden_dim=64, history_fraction=1.0)
    elm.fit(fit_history, horizon=HORIZON)

    # identity gate: hybrid (1,) vs RBFELM byte-identical
    hb_r1 = hybrids["hybrid_R1"]
    diff = float(np.max(np.abs(hb_r1.predict() - rbf.predict())))
    print(f"identity hybrid(1,) vs RBFELM max diff {diff:.2e}")
    assert diff == 0.0, f"hybrid(1,) not identical to RBFELM: {diff}"

    # determinism: refit hybrid 1,2,4 second time byte-identical
    h2 = MultiRateRBF(rates=(1,2,4), hidden_dim=64)
    h2.fit(fit_history, horizon=HORIZON)
    diff2 = float(np.max(np.abs(hybrids["hybrid_R1_2_4"].predict() - h2.predict())))
    print(f"determinism hybrid(1,2,4) refit diff {diff2:.2e}")
    assert diff2 == 0.0

    models = {
        **hybrids,
        "rbf_raw": rbf,
        "multirate_R1_2_4": mr,
        "nlinear_L336": nlin,
        "elm_h64": elm,
    }

    results = {}
    # t=0 sanity for hybrids
    for label, model in hybrids.items():
        mae, rmse = mae_rmse(model.predict(), t0_truth)
        results[label] = {"t0_mae": round(mae,4), "t0_rmse": round(rmse,4)}
        print(f"{label} t0 {mae:.4f}")

    # rolling
    for label, model in models.items():
        pa = make_predictor(model)
        rm, rr, disj, per = rolling_score(pa, eval_series, test)
        # keep t0 if already there
        base = results.get(label, {})
        base.update({"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj})
        results[label] = base
        print(f"{label} rolling {rm:.4f} / {rr:.4f}")

    # anchors daily/persistence
    from methods.baselines import seasonal_forecast as sf
    def daily_predict_at(hist):
        return sf(hist, HORIZON, "daily")
    def pers_predict_at(hist):
        return np.full(HORIZON, hist[-1])
    for name, pa in [("daily", daily_predict_at), ("persistence", pers_predict_at)]:
        rm, rr, disj, _ = rolling_score(pa, eval_series, test)
        results[name] = {"rolling_mae": round(rm,4), "rolling_rmse": round(rr,4), "disjoint": disj}
        print(f"{name} rolling {rm:.4f}")
        if name in ROLLING_ANCHORS:
            assert abs(rm - ROLLING_ANCHORS[name]) < 0.02, f"{name} anchor {rm} vs {ROLLING_ANCHORS[name]}"
    out = HERE / "results_rolling.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {out}")

    # summary
    print("\n--- hybrid summary (rolling MAE) ---")
    for k in ["nlinear_L336","hybrid_R1_2_4","hybrid_R1_2","hybrid_R1_4","hybrid_R1_2_4_8","hybrid_R1","rbf_raw","multirate_R1_2_4","elm_h64","daily"]:
        if k in results:
            print(f"{k:20s} {results[k].get('rolling_mae','-')}  (t0 {results[k].get('t0_mae','-')})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
