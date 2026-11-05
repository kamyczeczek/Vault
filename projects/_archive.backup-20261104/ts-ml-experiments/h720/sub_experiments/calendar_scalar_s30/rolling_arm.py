"""S-30 Calendar Phase Scalar — Data Scout Bet 1 vs S-26 2-member incumbent.

Incumbent: [NLinear L336 a=1 + NLinear L336 a=10], per-horizon ridge alpha=10000 => 1.9909.
This slice: M=2 -> M=3 where 3rd feature is single calendar scalar c_{t,h}
  = sin(2*pi*(hour_t + h)/24), hour_t = t % 24 (ETTh1 starts 2016-07-01 00:00, so
  t%24 is hour-of-day), per-horizon ridge with same 11-alpha grid 0.1..30000,
  held-out n2 selection, refit-all-val, frozen 11425->concat test (S-20-clean).

Map-level + 1 scalar aux only — no _lag_dataset/base.py change.
Graph hotspot guard: _lag_dataset @ base.py:197 d27 — untouched here; only stack
map widens from m=2 to m=3 (fit_stack_map already generic).

Protocol guards (S-20-clean):
- preds_for_train_fit: fit on train 8545, score on val 2161 (leakage-free val)
- preds_for_full_fit:  fit on full 11425, score on test 2161 (leakage-free test)
- Same ALPHAS 11-grid, no-intercept per-horizon Ridge, chronological n2=1080/1081
- Full 2161 is selector; disjoint-4 diagnostic only (scar [9] P3)
- [10] P4 flip gate: held-out must beat no-intercept ridge delta before frozen test
- c_t derived from history timestamp only (t = origin index), no future peeking

Refs: sub_experiments/horizon_band_alpha_s27/rolling_arm.py (S-20-clean factories)
      sub_experiments/greedy_linear_mixture_s26/rolling_arm.py:52-118
Hotspots: fit @ methods/nlinear_knn.py:65 degree 48 — not touched
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear

TRAIN_END = 8545
ALPHAS = [0.1,1.0,3.0,10.0,30.0,100.0,300.0,1000.0,3000.0,10000.0,30000.0]
DISJOINT_STARTS = (0,720,1440,2160)
INCUMBENT_MAE = 1.9909
# S-26 disjoint incumbent per CONTEXT ref (for context, not gating pooled itself)
# task says disjoint-4 also improves vs S-26 1.9696 OR not worse by >0.002
DISJOINT_INCUMBENT = 1.9696  # CONTEXT diagnostic

CANDIDATES = [
    ("nlinear_L336_a1",  lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
]
INC_IDX = [0,1]

def fit_stack_map(P, A, alpha, fit_intercept=False):
    n,m,h = P.shape
    coef = np.empty((m,h)); inter = np.zeros(h)
    if fit_intercept:
        for k in range(h):
            r = Ridge(alpha=alpha, fit_intercept=True).fit(P[:,:,k], A[:,k])
            coef[:,k] = r.coef_; inter[k] = r.intercept_
    else:
        for k in range(h):
            r = Ridge(alpha=alpha, fit_intercept=False).fit(P[:,:,k], A[:,k])
            coef[:,k] = r.coef_
    class _Map:
        def predict(self, Pt):
            return np.einsum("mh,nmh->nh", coef, Pt) + inter[None,:]
    _Map.coef_=coef; _Map.inter_=inter
    return _Map()

def score_full(P_val, A_val, idx):
    if len(idx)==0:
        return float("inf"), None
    if len(idx)==1:
        n=len(A_val); n2=n//2
        mae=float(np.mean(np.mean(np.abs(P_val[n2:, idx[0], :]-A_val[n2:]),axis=1)))
        return mae, None
    Psub=P_val[:, idx, :]; n=len(A_val); n2=n//2
    best=None; best_a=None
    for a in ALPHAS:
        r=fit_stack_map(Psub[:n2], A_val[:n2], a)
        sel=float(np.mean(np.mean(np.abs(r.predict(Psub[n2:])-A_val[n2:]),axis=1)))
        if best is None or sel < best:
            best=sel; best_a=a
    return best, best_a

def preds_for_train_fit(factory, train_series, full_series, starts, L, H):
    m=factory(); m.fit(train_series, horizon=H)
    out=[]; hist=m.history_
    for s in starts:
        m.history_=full_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_=hist
    return np.asarray(out)

def preds_for_full_fit(factory, full_series, concat_series, starts, L, H):
    m=factory(); m.fit(full_series, horizon=H)
    out=[]; hist=m.history_
    for s in starts:
        m.history_=concat_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_=hist
    return np.asarray(out)

def collect_val(train_series, full_series, starts):
    cols=[]
    for name,factory in CANDIDATES:
        L=factory().input_length
        p=preds_for_train_fit(factory, train_series, full_series, starts, L, HORIZON)
        cols.append(p); print(f"  {name:20s} L={L:3d} ok {p.shape}")
    return np.stack(cols, axis=1)

def collect_test(full_series, concat_series, starts):
    cols=[]
    for name,factory in CANDIDATES:
        L=factory().input_length
        p=preds_for_full_fit(factory, full_series, concat_series, starts, L, HORIZON)
        cols.append(p); print(f"  {name:20s} L={L:3d} ok {p.shape}")
    return np.stack(cols, axis=1)

def calendar_feature(starts, H):
    """Single scalar per (origin,h): sin(2*pi*(hour+h)/24), hour = t%24, strictly history."""
    starts = np.asarray(starts, dtype=int)
    n = len(starts)
    feat = np.empty((n, H))
    for i, t in enumerate(starts):
        hour = int(t) % 24
        h = np.arange(H)
        feat[i] = np.sin(2*np.pi*(hour + h)/24.0)
    return feat

def augment_with_calendar(P, starts, H):
    """P (n,m,H) -> (n,m+1,H) with calendar scalar as last member."""
    cal = calendar_feature(starts, H)  # (n,H)
    return np.concatenate([P, cal[:, None, :]], axis=1)

def rolling_metrics(preds, actuals):
    err=preds-actuals
    mae_per=np.mean(np.abs(err),axis=1); rmse_per=np.sqrt(np.mean(err**2,axis=1))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err**2))), mae_per, rmse_per

def main():
    t_all=time.time()
    pd=get_protocol_data()
    fit_series, _, test_series = pd.rolling_views()
    train_series = fit_series[:TRAIN_END]
    val_series = fit_series[TRAIN_END:]; n_val=len(val_series)-HORIZON+1
    assert n_val==2161
    assert len(train_series)==8545 and len(fit_series)==11425
    print(f"fingerprint check: train {len(train_series)} fit {len(fit_series)} val {n_val} H={HORIZON}")
    # hotspots header cite
    print("hotspot cite: fit @ projects/ts-ml-experiments/h720/methods/nlinear_knn.py:65 degree 48 (ask.py --hotspots)")
    val_starts=np.arange(n_val)+TRAIN_END
    print(f"collecting P_val {len(CANDIDATES)} members frozen on {TRAIN_END} (S-20-clean)...")
    P_val=collect_val(train_series, fit_series, val_starts)
    A_val=np.stack([val_series[t:t+HORIZON] for t in range(n_val)])
    P_val_cal = augment_with_calendar(P_val, val_starts, HORIZON)
    print(f"P_val {P_val.shape} -> P_val_cal {P_val_cal.shape}  feature: sin(2*pi*(hour+h)/24) hour=t%24")

    # Pooled baseline (m=2) and calendar (m=3) selection on held-out n2
    n=len(A_val); n2=n//2
    # pooled
    best_pooled, alpha_pooled = score_full(P_val, A_val, INC_IDX)
    print(f"\npooled  (m=2) held-out MAE {best_pooled:.4f} alpha*={alpha_pooled}")
    # calendar: indices 0,1,2  (all three)
    cal_idx = [0,1,2]
    best_cal, alpha_cal = score_full(P_val_cal, A_val, cal_idx)
    print(f"calendar(m=3) held-out MAE {best_cal:.4f} alpha*={alpha_cal}")
    delta_held = best_cal - best_pooled
    print(f"held-out delta calendar-pooled {delta_held:+.4f}  (negative means calendar wins)")

    # Refit all val
    stack_pooled = fit_stack_map(P_val[:, INC_IDX, :], A_val, alpha_pooled if alpha_pooled is not None else 3000.0)
    stack_cal = fit_stack_map(P_val_cal[:, cal_idx, :], A_val, alpha_cal if alpha_cal is not None else 3000.0)
    val_full_pooled=float(np.mean(np.mean(np.abs(stack_pooled.predict(P_val[:,INC_IDX,:])-A_val),axis=1)))
    val_full_cal=float(np.mean(np.mean(np.abs(stack_cal.predict(P_val_cal[:,cal_idx,:])-A_val),axis=1)))
    print(f"refit-all-val pooled {val_full_pooled:.4f}  calendar {val_full_cal:.4f}")

    concat=np.concatenate([fit_series, test_series])
    # disjoint-4
    disj_starts=np.array([len(fit_series)+s for s in DISJOINT_STARTS])
    P_disj_all=collect_test(fit_series, concat, disj_starts)
    P_disj_cal = augment_with_calendar(P_disj_all, disj_starts, HORIZON)
    P_disj = P_disj_all[:, INC_IDX, :]
    P_disj_c = P_disj_cal[:, cal_idx, :]
    A_disj=np.stack([test_series[s:s+HORIZON] for s in DISJOINT_STARTS])
    mae_d_p, rmse_d_p, _, _ = rolling_metrics(stack_pooled.predict(P_disj), A_disj)
    mae_d_c, rmse_d_c, _, _ = rolling_metrics(stack_cal.predict(P_disj_c), A_disj)
    # full 2161
    n_test=len(test_series)-HORIZON+1
    test_starts=np.arange(n_test)+len(fit_series)
    P_test_all=collect_test(fit_series, concat, test_starts)
    P_test_cal = augment_with_calendar(P_test_all, test_starts, HORIZON)
    P_test=P_test_all[:, INC_IDX, :]
    P_test_c=P_test_cal[:, cal_idx, :]
    A_test=np.stack([test_series[t:t+HORIZON] for t in range(n_test)])
    mae_f_p, rmse_f_p, _, _ = rolling_metrics(stack_pooled.predict(P_test), A_test)
    mae_f_c, rmse_f_c, _, _ = rolling_metrics(stack_cal.predict(P_test_c), A_test)
    print(f"\npooled:   disjoint {mae_d_p:.4f}/{rmse_d_p:.4f}  full {mae_f_p:.4f}/{rmse_f_p:.4f}")
    print(f"calendar: disjoint {mae_d_c:.4f}/{rmse_d_c:.4f}  full {mae_f_c:.4f}/{rmse_f_c:.4f}")
    print(f"incumbent 1.9909  delta pooled {mae_f_p-INCUMBENT_MAE:+.4f}  delta calendar {mae_f_c-INCUMBENT_MAE:+.4f}")

    # Acceptance per task
    interior = (alpha_cal not in (ALPHAS[0], ALPHAS[-1])) if alpha_cal is not None else False
    # held-out beats no-intercept delta: task says "held-out beats no-intercept delta"
    # we interpret as calendar held-out < pooled held-out (delta negative) — the flip gate
    held_beats = best_cal < best_pooled - 1e-9
    full_beats = (INCUMBENT_MAE - mae_f_c) > 0.005  # <1.9909 by >0.005 => <=1.9859
    disjoint_not_worse = (mae_d_c - mae_d_p) <= 0.002 + 1e-9  # not worse by >0.002
    # also for context vs incumbent disjoint
    verdict = "ACCEPT" if (full_beats and disjoint_not_worse and interior and held_beats) else "REJECT"
    reasons=[]
    if not full_beats: reasons.append(f"full {mae_f_c:.4f} not >0.005 better than {INCUMBENT_MAE} (need <=1.9859)")
    if not disjoint_not_worse: reasons.append(f"disjoint {mae_d_c:.4f} worse than pooled {mae_d_p:.4f} by {(mae_d_c-mae_d_p):.4f} >0.002")
    if not interior: reasons.append(f"alpha* {alpha_cal} not interior {ALPHAS}")
    if not held_beats: reasons.append(f"held-out {best_cal:.4f} not < pooled {best_pooled:.4f} (flip gate)")
    print(f"\nverdict: {verdict}  interior={interior} held_beats={held_beats} full_beats={full_beats} disjoint_not_worse={disjoint_not_worse}")
    if reasons: print("  reasons: " + "; ".join(reasons))

    out={
        "slice": "S-30-calendar-scalar",
        "feature": "sin(2*pi*(hour+h)/24) hour=t%24 per horizon scalar, m=2->m=3, per-horizon Ridge no-intercept",
        "alphas_grid": ALPHAS,
        "incumbent_mae": INCUMBENT_MAE,
        "pooled": {"alpha": alpha_pooled, "held_out_mae": best_pooled, "val_full": val_full_pooled, "disjoint": {"mae": mae_d_p, "rmse": rmse_d_p}, "full": {"mae": mae_f_p, "rmse": rmse_f_p, "n": n_test}},
        "calendar": {"alpha": alpha_cal, "held_out_mae": best_cal, "val_full": val_full_cal, "disjoint": {"mae": mae_d_c, "rmse": rmse_d_c}, "full": {"mae": mae_f_c, "rmse": rmse_f_c, "n": n_test}},
        "checks": {"interior": interior, "held_beats": held_beats, "full_beats_0.005": full_beats, "disjoint_not_worse_0.002": disjoint_not_worse, "delta_held": delta_held, "delta_full_vs_incumbent": mae_f_c-INCUMBENT_MAE, "delta_disjoint_cal_minus_pooled": mae_d_c-mae_d_p},
        "verdict": verdict,
        "reasons": reasons,
        "protocol": "S-20-clean: preds_for_train_fit for val (8545 frozen), preds_for_full_fit for test (11425 refrozen); calendar scalar from history t%24 only; full 2161 selector, disjoint-4 diagnostic only; no _lag_dataset change",
        "hotspot_guard": "_lag_dataset @ base.py:197 untouched — map-level +1 scalar only",
    }
    with open(HERE/"results_s30.json","w") as f: json.dump(out,f,indent=2)
    print(f"\nwrote {HERE/'results_s30.json'} elapsed {time.time()-t_all:.1f}s")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
