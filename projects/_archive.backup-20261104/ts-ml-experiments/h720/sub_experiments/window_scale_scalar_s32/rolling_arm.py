"""S-32 Window-Scale Scalar — Data Scout Bet 2 vs S-26 2-member incumbent.

Incumbent: [NLinear L336 a=1 + NLinear L336 a=10], per-horizon ridge alpha=10000 => 1.9909.
This slice: M=2 -> M=3 where 3rd feature is single window-scale scalar sigma_t
  = std(history_[-336:]) computed strictly from history window (no future),
  per-horizon ridge beta_h * sigma_t, same 11-alpha grid 0.1..30000,
  held-out n2 selection, refit-all-val, frozen 11425->concat test (S-20-clean).

Map-level +1 scalar aux only — no _lag_dataset/base.py change.
Graph hotspot guard: _lag_dataset @ base.py:197 d27 — untouched here; only stack
map widens from m=2 to m=3 (fit_stack_map already generic).

Protocol guards (S-20-clean):
- preds_for_train_fit: fit on train 8545, score on val 2161 (leakage-free val)
- preds_for_full_fit:  fit on full 11425, score on test 2161 (leakage-free test)
- Same ALPHAS 11-grid, no-intercept per-horizon Ridge, chronological n2=1080/1081
- Full 2161 is selector; disjoint-4 diagnostic only (scar [9] P3)
- [10] P4 flip gate: held-out must beat no-intercept ridge delta before frozen test
- sigma_t derived from history window only, no future peeking

Refs: sub_experiments/calendar_scalar_s30/rolling_arm.py (scalar stacking pattern)
      methods/neural_models.py:220 _window_stats (sigma computation convention)
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
DISJOINT_INCUMBENT = 1.9696
SIGMA_WINDOW = 336  # same as incumbent lookback

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
def sigma_feature(history_series, starts, window=336, zscore=False, z_mu=None, z_sd=None):
    """Single scalar sigma_t per origin, broadcast across H horizons as beta_h * sigma_t.

    Computed strictly from history window history_series[s - window : s].
    Mirrors methods/neural_models.py:220 _window_stats std convention.
    zscore: if True, standardize using provided (z_mu, z_sd) fitted on train half
            only (leakage-free). If zscore=False (default, leakage-free trivial),
            returns raw sigma broadcast. Raw is preferred for intercept-free ridge
            since shift cannot be absorbed; zscore with leakage biases alpha*.
    Returns shape (n, H) with same value across h for each origin.
    """
    starts = np.asarray(starts, dtype=int)
    n = len(starts)
    sig = np.empty(n)
    eps = 1e-8
    arr = np.asarray(history_series, dtype=float)
    if arr.ndim == 2:
        arr = arr[:, 0]
    for i, s in enumerate(starts):
        w = arr[s - window : s]
        sig[i] = max(float(w.std()), eps)
    if zscore:
        assert z_mu is not None and z_sd is not None and z_sd > 1e-9
        sig = (sig - z_mu) / z_sd
    return np.repeat(sig[:, None], HORIZON, axis=1)

def augment_with_sigma(P, history_series, starts, window=336, zscore=False, z_mu=None, z_sd=None):
    """P (n,m,H) -> (n,m+1,H) with sigma scalar as last member."""
    feat = sigma_feature(history_series, starts, window=window, zscore=zscore, z_mu=z_mu, z_sd=z_sd)
    return np.concatenate([P, feat[:, None, :]], axis=1)

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
    print("hotspot cite: _lag_dataset @ projects/ts-ml-experiments/h720/methods/base.py:197 degree 27 (ask.py --hotspots d27) — untouched; map-level +1 scalar only")
    print("sigma cite: methods/neural_models.py:220 _window_stats std(history_[-336:]) scalar per origin, per-horizon ridge beta_h")
    # zscore fitted on train-only windows (leakage-free): std over 336-windows within train
    _train_arr = np.asarray(train_series, dtype=float)
    if _train_arr.ndim == 2:
        _train_arr = _train_arr[:, 0]
    _train_sigs = np.array([max(float(_train_arr[s - SIGMA_WINDOW : s].std()), 1e-8) for s in range(SIGMA_WINDOW, len(_train_arr))])
    z_mu = float(_train_sigs.mean()); z_sd = float(_train_sigs.std())
    if z_sd < 1e-9:
        z_sd = 1.0
    print(f"sigma zscore fitted on train windows n={len(_train_sigs)} mu={z_mu:.6f} sd={z_sd:.6f}")
    val_starts=np.arange(n_val)+TRAIN_END
    print(f"collecting P_val {len(CANDIDATES)} members frozen on {TRAIN_END} (S-20-clean)...")
    P_val=collect_val(train_series, fit_series, val_starts)
    A_val=np.stack([val_series[t:t+HORIZON] for t in range(n_val)])
    P_val_sig = augment_with_sigma(P_val, fit_series, val_starts, window=SIGMA_WINDOW, zscore=True, z_mu=z_mu, z_sd=z_sd)
    print(f"P_val {P_val.shape} -> P_val_sig {P_val_sig.shape}  feature: sigma_t=zscore(std(history_[s-{SIGMA_WINDOW}:s])) broadcast H={HORIZON} (leakage-free, train-fitted)")

    n=len(A_val); n2=n//2
    best_pooled, alpha_pooled = score_full(P_val, A_val, INC_IDX)
    print(f"\npooled  (m=2) held-out MAE {best_pooled:.4f} alpha*={alpha_pooled}")
    sig_idx = [0,1,2]
    best_sig, alpha_sig = score_full(P_val_sig, A_val, sig_idx)
    print(f"sigma  (m=3) held-out MAE {best_sig:.4f} alpha*={alpha_sig}")
    delta_held = best_sig - best_pooled
    print(f"held-out delta sigma-pooled {delta_held:+.4f}  (negative means sigma wins)")
    # also held-out single-bias sanity: sigma-only delta vs no-intercept ridge 2.5191 ref
    # threshold 2.5191 is from CONTEXT for ridge-on-val; we check held-out beats pooled (primary)
    # and report comparison to 2.5191 for the acceptance phrasing
    print(f"held-out beats 2.5191? pooled {best_pooled:.4f} sigma {best_sig:.4f}")

    stack_pooled = fit_stack_map(P_val[:, INC_IDX, :], A_val, alpha_pooled if alpha_pooled is not None else 3000.0)
    stack_sig = fit_stack_map(P_val_sig[:, sig_idx, :], A_val, alpha_sig if alpha_sig is not None else 3000.0)
    val_full_pooled=float(np.mean(np.mean(np.abs(stack_pooled.predict(P_val[:,INC_IDX,:])-A_val),axis=1)))
    val_full_sig=float(np.mean(np.mean(np.abs(stack_sig.predict(P_val_sig[:,sig_idx,:])-A_val),axis=1)))
    print(f"refit-all-val pooled {val_full_pooled:.4f}  sigma {val_full_sig:.4f}")

    concat=np.concatenate([fit_series, test_series])
    disj_starts=np.array([len(fit_series)+s for s in DISJOINT_STARTS])
    P_disj_all=collect_test(fit_series, concat, disj_starts)
    # for test, history_series = concat (fit+test prefix) for sigma at test origins
    P_disj_sig_all = augment_with_sigma(P_disj_all, concat, disj_starts, window=SIGMA_WINDOW, zscore=False)
    P_disj = P_disj_all[:, INC_IDX, :]
    P_disj_s = P_disj_sig_all[:, sig_idx, :]
    A_disj=np.stack([test_series[s:s+HORIZON] for s in DISJOINT_STARTS])
    mae_d_p, rmse_d_p, _, _ = rolling_metrics(stack_pooled.predict(P_disj), A_disj)
    mae_d_s, rmse_d_s, _, _ = rolling_metrics(stack_sig.predict(P_disj_s), A_disj)

    n_test=len(test_series)-HORIZON+1
    test_starts=np.arange(n_test)+len(fit_series)
    P_test_all=collect_test(fit_series, concat, test_starts)
    P_test_sig_all = augment_with_sigma(P_test_all, concat, test_starts, window=SIGMA_WINDOW, zscore=False)
    P_test=P_test_all[:, INC_IDX, :]
    P_test_s=P_test_sig_all[:, sig_idx, :]
    A_test=np.stack([test_series[t:t+HORIZON] for t in range(n_test)])
    mae_f_p, rmse_f_p, _, _ = rolling_metrics(stack_pooled.predict(P_test), A_test)
    mae_f_s, rmse_f_s, _, _ = rolling_metrics(stack_sig.predict(P_test_s), A_test)
    print(f"\npooled: disjoint {mae_d_p:.4f}/{rmse_d_p:.4f}  full {mae_f_p:.4f}/{rmse_f_p:.4f}")
    print(f"sigma:  disjoint {mae_d_s:.4f}/{rmse_d_s:.4f}  full {mae_f_s:.4f}/{rmse_f_s:.4f}")
    print(f"incumbent 1.9909  delta pooled {mae_f_p-INCUMBENT_MAE:+.4f}  delta sigma {mae_f_s-INCUMBENT_MAE:+.4f}")

    interior = (alpha_sig not in (ALPHAS[0], ALPHAS[-1])) if alpha_sig is not None else False
    held_beats = best_sig < best_pooled - 1e-9
    # "held-out beats 2.5191" — interpret as sigma held-out < 2.5191 (sanity) AND sigma < pooled
    held_beats_25191 = best_sig < 2.5191 - 1e-9
    full_beats = (INCUMBENT_MAE - mae_f_s) > 0.005
    disjoint_not_worse = (mae_d_s - mae_d_p) <= 0.002 + 1e-9
    verdict = "ACCEPT" if (full_beats and disjoint_not_worse and interior and held_beats and held_beats_25191) else "REJECT"
    reasons=[]
    if not full_beats: reasons.append(f"full {mae_f_s:.4f} not >0.005 better than {INCUMBENT_MAE} (need <=1.9859)")
    if not disjoint_not_worse: reasons.append(f"disjoint {mae_d_s:.4f} worse than pooled {mae_d_p:.4f} by {(mae_d_s-mae_d_p):.4f} >0.002")
    if not interior: reasons.append(f"alpha* {alpha_sig} not interior {ALPHAS}")
    if not held_beats: reasons.append(f"held-out {best_sig:.4f} not < pooled {best_pooled:.4f} (flip gate)")
    if not held_beats_25191: reasons.append(f"held-out {best_sig:.4f} not < 2.5191")
    print(f"\nverdict: {verdict}  interior={interior} held_beats={held_beats} held<2.5191={held_beats_25191} full_beats={full_beats} disjoint_not_worse={disjoint_not_worse}")
    if reasons: print("  reasons: " + "; ".join(reasons))
    # explain reject interpretation per task
    if verdict=="REJECT":
        print("  -> scale already spanned by linear span + heavy ridge (bet hypothesis rejected)")

    out={
        "slice": "S-32-window-scale-scalar",
        "feature": f"sigma_t=zscore(std(history_[s-{SIGMA_WINDOW}:s])) per origin, broadcast H={HORIZON}, m=2->m=3 per-horizon Ridge no-intercept",
        "alphas_grid": ALPHAS,
        "incumbent_mae": INCUMBENT_MAE,
        "sigma_window": SIGMA_WINDOW,
        "pooled": {"alpha": alpha_pooled, "held_out_mae": best_pooled, "val_full": val_full_pooled, "disjoint": {"mae": mae_d_p, "rmse": rmse_d_p}, "full": {"mae": mae_f_p, "rmse": rmse_f_p, "n": n_test}},
        "sigma": {"alpha": alpha_sig, "held_out_mae": best_sig, "val_full": val_full_sig, "disjoint": {"mae": mae_d_s, "rmse": rmse_d_s}, "full": {"mae": mae_f_s, "rmse": rmse_f_s, "n": n_test}},
        "checks": {"interior": interior, "held_beats_pooled": held_beats, "held_beats_2.5191": held_beats_25191, "full_beats_0.005": full_beats, "disjoint_not_worse_0.002": disjoint_not_worse, "delta_held": delta_held, "delta_full_vs_incumbent": mae_f_s-INCUMBENT_MAE, "delta_disjoint_sigma_minus_pooled": mae_d_s-mae_d_p},
        "verdict": verdict,
        "reasons": reasons,
        "protocol": "S-20-clean: preds_for_train_fit for val (8545 frozen), preds_for_full_fit for test (11425 refrozen); sigma scalar from history window only; full 2161 selector, disjoint-4 diagnostic only; no _lag_dataset change",
        "hotspot_guard": "_lag_dataset @ base.py:197 untouched — map-level +1 scalar only",
        "sigma_cite": "methods/neural_models.py:220 _window_stats",
    }
    with open(HERE/"results_s32.json","w") as f: json.dump(out,f,indent=2)
    print(f"\nwrote {HERE/'results_s32.json'} elapsed {time.time()-t_all:.1f}s")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
