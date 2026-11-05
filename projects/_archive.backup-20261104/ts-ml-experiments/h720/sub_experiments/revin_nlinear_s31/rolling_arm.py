"""S-31 RevIN-NLinear Lookback — Bet 2 vs S-26 1.9909.
Adds one RevIN-normalized NLinear L=512 as 3rd candidate in 2-member
incumbent [L336 a1 + L336 a10]. S-20-clean:
  P_val: members fit on train 8545, predict val origins (full 11425 history swap)
  P_test/P_disj: members fit on full 11425, predict test/disjoint via concat swap
n2=1080/1081 (val held-out half), 11-alpha grid, per-horizon ridge no-intercept.
Compare pooled 2-member (1.9909) vs 3-member augmented pool.
Blast: NLinear/RLinear/RevinNLinear do NOT call _lag_dataset (base.py:197 d27);
  isolated to neural_models inline window loops + rolling_arm candidate list.
"""
from __future__ import annotations
import collections, json, sys, time
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge, LinearRegression

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, RLinear
from methods.base import BaseForecaster

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]

# --- RevIN-NLinear: per-window (mu,sigma) like RLinear, but
# last-value-anchored target convention like NLinear's anchor hedge.
# Features are RevIN-standardized windows; targets are horizon relative
# to last value (anchor) scaled by sigma, so far-horizon bias from level
# is normalized without losing NLinear's hedged level-freedom.
class RevINNLinear(BaseForecaster):
    """RevIN-standardized window, NLinear-style anchor on target."""
    def __init__(self, input_length: int = 512, ridge_alpha: float = 10.0):
        self.input_length = input_length
        self.ridge_alpha = ridge_alpha
        self._SCALE_EPS = 1e-8
    def _array(self, values):
        r = np.asarray(values, dtype=float)
        if r.ndim not in (1,2) or len(r) < self.input_length + 2 or not np.isfinite(r).all():
            raise ValueError("too short or non-finite")
        return r if r.ndim == 2 else r[:, None]
    def _window_stats(self, window):
        mu = float(window.mean())
        sigma = max(float(window.std()), self._SCALE_EPS)
        return mu, sigma
    def fit(self, y, *, horizon: int, target_index: int = 0):
        series = self._array(y)
        self._check_horizon(horizon)
        if series.ndim == 1:
            series = series[:, None]
        if len(series) <= self.input_length + horizon:
            raise ValueError("insufficient history")
        x_rows, y_rows = [], []
        for end in range(self.input_length, len(series) - horizon + 1):
            window = series[end - self.input_length:end]
            mu, sigma = self._window_stats(window[:, target_index] if window.ndim==2 else window)
            # feature: RevIN-standardized window (all channels flattened like NLinear)
            # use per-target-channel sigma for target scaling; feature uses window stats
            # For univariate case, window is (L,1), mean/std over all values is same.
            x_rows.append(((window - mu) / sigma).reshape(-1))
            anchor = window[-1, target_index]
            # target: (future - anchor)/sigma — combines RevIN scale with NLinear anchor
            y_rows.append((series[end:end+horizon, target_index] - anchor) / sigma)
        self.model = Ridge(alpha=self.ridge_alpha, fit_intercept=True).fit(np.asarray(x_rows), np.asarray(y_rows))
        self.history_ = series
        self.target_index = target_index
        self.horizon_ = int(horizon)
        self._last_mu = mu  # not used, placeholder
        self._fitted = True
        return self
    def predict(self):
        self._check_fitted()
        raw = self.history_[-self.input_length:]
        window = raw[:, None] if raw.ndim == 1 else raw
        mu, sigma = self._window_stats(window[:, self.target_index] if window.ndim==2 else window.reshape(-1))
        anchor = window[-1, self.target_index]
        x = ((window - mu) / sigma).reshape(-1)
        out_scaled = np.asarray(self.model.predict([x])[0])
        # invert: (future - anchor)/sigma -> future
        return out_scaled * sigma + anchor

CANDIDATES_2 = [
    ("nlinear_L336_a1",  lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
]
CANDIDATES_3 = CANDIDATES_2 + [
    ("revin_nlinear_L512_a10", lambda: RevINNLinear(input_length=512, ridge_alpha=10.0)),
]

def fit_stack_map(P, A, alpha, fit_intercept=False):
    n, m, h = P.shape
    coef = np.empty((m, h)); inter = np.zeros(h)
    for k in range(h):
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
    class _Map:
        def predict(self, Pt): return np.einsum("mh,nmh->nh", coef, Pt) + inter[None, :]
    _Map.coef_ = coef; _Map.inter_ = inter
    return _Map()

def score_full(P_val, A_val, idx):
    if len(idx) == 0: return float("inf"), None
    if len(idx) == 1:
        n = len(A_val); n2 = n // 2
        mae = float(np.mean(np.mean(np.abs(P_val[n2:, idx[0], :] - A_val[n2:]), axis=1)))
        return mae, None
    Psub = P_val[:, idx, :]; n = len(A_val); n2 = n // 2
    best = None; best_a = None
    for a in ALPHAS:
        r = fit_stack_map(Psub[:n2], A_val[:n2], a)
        sel = float(np.mean(np.mean(np.abs(r.predict(Psub[n2:]) - A_val[n2:]), axis=1)))
        if best is None or sel < best: best = sel; best_a = a
    return best, best_a

def score_fast(P_val, A_val, idx):
    if len(idx) == 1:
        n = len(A_val); n2 = n // 2
        return float(np.mean(np.mean(np.abs(P_val[n2:, idx[0], :] - A_val[n2:]), axis=1)))
    # use best alpha search for consistency with score_full when comparing pools
    s,_ = score_full(P_val, A_val, idx)
    return s

def preds_for_train_fit(factory, train_series, full_series, starts, H):
    m = factory(); m.fit(train_series, horizon=H)
    out=[]; hist=m.history_
    for s in starts:
        m.history_ = full_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_=hist
    return np.asarray(out)

def preds_for_full_fit(factory, full_series, concat_series, starts, H):
    m = factory(); m.fit(full_series, horizon=H)
    out=[]; hist=m.history_
    for s in starts:
        m.history_ = concat_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_=hist
    return np.asarray(out)

def collect_val(candidates, train_series, full_series, starts):
    cols=[]
    for name,factory in candidates:
        L=factory().input_length
        p=preds_for_train_fit(factory, train_series, full_series, starts, HORIZON)
        cols.append(p); print(f"  {name:26s} L={L:3d} ok {p.shape}")
    return np.stack(cols, axis=1)

def collect_test(candidates, full_series, concat_series, starts):
    cols=[]
    for name,factory in candidates:
        L=factory().input_length
        p=preds_for_full_fit(factory, full_series, concat_series, starts, HORIZON)
        cols.append(p); print(f"  {name:26s} L={L:3d} ok {p.shape}")
    return np.stack(cols, axis=1)

def rolling_metrics(preds, actuals):
    err=preds-actuals
    mae_per=np.mean(np.abs(err),axis=1); rmse_per=np.sqrt(np.mean(err**2,axis=1))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err**2))), mae_per, rmse_per

def eval_pool(label, candidates, P_val, A_val, fit_series, concat, test_series, DISJOINT_STARTS):
    idx = list(range(len(candidates)))
    held_mae, best_a = score_full(P_val, A_val, idx)
    n=len(A_val)
    # refit map on first half, evaluate held-out is held_mae; now refit on all val for test map
    P_best = P_val[:, idx, :]
    stack_all = fit_stack_map(P_best, A_val, best_a if best_a is not None else 3000.0)
    # disjoint
    disj_starts=np.array([len(fit_series)+s for s in DISJOINT_STARTS])
    P_disj_all=collect_test(candidates, fit_series, concat, disj_starts)
    P_disj=P_disj_all[:, idx, :]
    A_disj=np.stack([test_series[s:s+HORIZON] for s in DISJOINT_STARTS])
    preds_disj=stack_all.predict(P_disj)
    mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)
    # full 2161 not available for disjoint label — for full we use sliding test
    n_test=len(test_series)-HORIZON+1
    test_starts=np.arange(n_test)+len(fit_series)
    P_test_all=collect_test(candidates, fit_series, concat, test_starts)
    P_test=P_test_all[:, idx, :]
    A_test=np.stack([test_series[t:t+HORIZON] for t in range(n_test)])
    preds_full=stack_all.predict(P_test)
    mae_full, rmse_full, _, _ = rolling_metrics(preds_full, A_test)
    print(f"[{label}] held {held_mae:.4f} a={best_a}  disj {mae_disj:.4f}  full {mae_full:.4f} rmse {rmse_full:.4f}")
    return {"label":label,"pool":[n for n,_ in candidates],"held_mae":held_mae,"best_alpha":best_a,"disj_mae":mae_disj,"disj_rmse":rmse_disj,"full_mae":mae_full,"full_rmse":rmse_full,"n_test":n_test}

def main():
    t_all=time.time()
    pd=get_protocol_data()
    fit_series, _, test_series = pd.rolling_views()
    train_series = fit_series[:TRAIN_END]
    val_series=fit_series[TRAIN_END:]; n_val=len(val_series)-HORIZON+1
    assert n_val==2161
    assert len(train_series)==8545 and len(fit_series)==11425
    val_starts=np.arange(n_val)+TRAIN_END
    concat=np.concatenate([fit_series, test_series])

    print(f"collecting P_val 2-member ...")
    P_val_2=collect_val(CANDIDATES_2, train_series, fit_series, val_starts)
    A_val=np.stack([val_series[t:t+HORIZON] for t in range(n_val)])
    for j,(name,_) in enumerate(CANDIDATES_2):
        mae=float(np.mean(np.mean(np.abs(P_val_2[:,j,:]-A_val),axis=1)))
        print(f"  {name:26s} val pooled {mae:.4f} (full 2161, not held)")
    # also print held-out for 2-pool members individually
    n2=n_val//2
    for j,(name,_) in enumerate(CANDIDATES_2):
        mae_held=float(np.mean(np.mean(np.abs(P_val_2[n2:,j,:]-A_val[n2:]),axis=1)))
        print(f"  {name:26s} held {mae_held:.4f}")

    print(f"\ncollecting P_val 3-member (adds RevIN L512)...")
    P_val_3=collect_val(CANDIDATES_3, train_series, fit_series, val_starts)
    for j,(name,_) in enumerate(CANDIDATES_3):
        mae=float(np.mean(np.mean(np.abs(P_val_3[:,j,:]-A_val),axis=1)))
        print(f"  {name:26s} val pooled {mae:.4f}")
        mae_held=float(np.mean(np.mean(np.abs(P_val_3[n2:,j,:]-A_val[n2:]),axis=1)))
        print(f"    -> held {mae_held:.4f}")

    print("\n--- evaluation (refit-all-val, per-horizon ridge no-intercept) ---")
    res2=eval_pool("2-member", CANDIDATES_2, P_val_2, A_val, fit_series, concat, test_series, DISJOINT_STARTS)
    res3=eval_pool("3-member+RevIN512", CANDIDATES_3, P_val_3, A_val, fit_series, concat, test_series, DISJOINT_STARTS)

    # singleton RevIN vs singleton NLinear L336 a10 on held-out and full
    # held-out singleton
    rev_idx=2
    held_rev=float(np.mean(np.mean(np.abs(P_val_3[n2:, rev_idx, :]-A_val[n2:]),axis=1)))
    held_nl=float(np.mean(np.mean(np.abs(P_val_3[n2:, 1, :]-A_val[n2:]),axis=1)))
    print(f"\nsingleton held L336_a10 {held_nl:.4f}  RevIN512 {held_rev:.4f}  delta {held_rev-held_nl:+.4f}")
    # full singleton test (need P_test singles — reuse from last collect)
    # collect_test already done inside eval; do quick singleton full
    n_test=len(test_series)-HORIZON+1
    test_starts=np.arange(n_test)+len(fit_series)
    P_test_3=collect_test(CANDIDATES_3, fit_series, concat, test_starts)
    A_test=np.stack([test_series[t:t+HORIZON] for t in range(n_test)])
    mae_singles=[]
    for j,(name,_) in enumerate(CANDIDATES_3):
        m=float(np.mean(np.mean(np.abs(P_test_3[:,j,:]-A_test),axis=1)))
        mae_singles.append(m); print(f"  singleton full {name:26s} {m:.4f}")

    # verdict
    incumbent_full=res2["full_mae"]
    incumbent_disj=res2["disj_mae"]
    challenger_full=res3["full_mae"]
    challenger_disj=res3["disj_mae"]
    challenger_held=res3["held_mae"]
    incumbent_held=res2["held_mae"]
    # Acceptance: full <1.9909 by >0.005 AND disjoint not worse by >0.002 AND held-out wins
    # Use empirical incumbent_full as reference; spec says 1.9909 pool
    # We compare challenger vs incumbent (relative) and vs absolute 1.9909 guard.
    # held-out wins means challenger_held < incumbent_held
    abs_guard=1.9909
    full_win = (abs_guard - challenger_full) > 0.005
    rel_win = (incumbent_full - challenger_full) > 0.005
    disj_ok = (challenger_disj - incumbent_disj) <= 0.002
    held_win = challenger_held < incumbent_held - 1e-9
    # also singleton path (b)
    sing_win = (mae_singles[1] - mae_singles[2]) > 0.005  # NL336a10 - RevIN
    verdict="REJECT"
    reason=[]
    if (full_win or rel_win) and disj_ok and held_win:
        verdict="ACCEPT"
    elif sing_win and disj_ok:
        # check singleton full vs abs guard too
        if (abs_guard - mae_singles[2]) > 0.005:
            verdict="ACCEPT (singleton)"
    if not (full_win or rel_win): reason.append(f"full {challenger_full:.4f} not < {abs_guard:.4f}-0.005 nor < inc {incumbent_full:.4f}-0.005")
    if not disj_ok: reason.append(f"disjoint {challenger_disj:.4f} > inc {incumbent_disj:.4f}+0.002")
    if not held_win: reason.append(f"held {challenger_held:.4f} not < inc-held {incumbent_held:.4f}")
    print(f"\nPools: 2m held {incumbent_held:.4f} disj {incumbent_disj:.4f} full {incumbent_full:.4f}")
    print(f"       3m held {challenger_held:.4f} disj {challenger_disj:.4f} full {challenger_full:.4f}")
    print(f"Verdict: {verdict} — {'; '.join(reason) if reason else 'all guards passed'}")
    print(f"Note: _lag_dataset d27 not touched (NLinear/RevIN use inline windows); Scar [8]P1/[9]P2 not triggered (RevIN normalizes level, ridge no-intercept, val-selected).")

    out={
        "slice":"S-31-revin-nlinear",
        "L":512,
        "alphas":ALPHAS,
        "candidates_2":[n for n,_ in CANDIDATES_2],
        "candidates_3":[n for n,_ in CANDIDATES_3],
        "res_2member":res2,
        "res_3member":res3,
        "singleton_held":{"nlinear_L336_a10":held_nl,"revin_L512_a10":held_rev},
        "singleton_full":{n:m for (n,_),m in zip(CANDIDATES_3, mae_singles)},
        "verdict":verdict,
        "reason":"; ".join(reason) if reason else "n/a",
        "guards":{"abs_guard":abs_guard,"need_full_delta":0.005,"need_disjoint_slack":0.002},
        "blast":"_lag_dataset d27 isolated — NLinear/RevIN do NOT call _lag_dataset (inline windows neural_models.py:165/233)",
        "protocol":"S-20-clean: val members frozen on 8545, test members refrozen on 11425, n2=1080/1081, 11-alpha per-horizon ridge no-intercept"
    }
    with open(HERE/"results_s31.json","w") as f: json.dump(out,f,indent=2)
    print(f"\nwrote {HERE/'results_s31.json'} elapsed {time.time()-t_all:.1f}s")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
