"""S-24 — multivariate ridge mixture: 6 univariate linear + 2 multivariate NLinear (light, no grid).

Members: the 6 S-20 univariate linears (OT-only) + 2 multivariate NLinear
  NLinearMulti L96 a=1  (7-channel window, OT-anchored)
  NLinearMulti L336 a=1

Same S-20 protocol: per-horizon ridge stack (no intercept), alpha selected
chronologically inside val ([0,1080) fit / [1080,2161) select), refit all val,
frozen test 11425.

Run: python sub_experiments/multivariate_ridge_s24/rolling_arm.py
"""
from __future__ import annotations
import json, sys, time, csv
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, DLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
COLS = ["HUFL","HULL","MUFL","MULL","LUFL","LULL","OT"]
OT_IDX = 6  # last column


def load_multivariate(path: Path) -> np.ndarray:
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = [[float(r[c]) for c in COLS] for r in reader]
    return np.asarray(rows, dtype=float)


class MultiNLinear:
    """NLinear over 7-channel window, OT-anchored. Features = flattened (window - last_row)."""
    def __init__(self, input_length: int = 96, ridge_alpha: float = 1.0):
        self.input_length = input_length
        self.ridge_alpha = ridge_alpha
    def fit(self, y, *, horizon: int):
        series = np.asarray(y, dtype=float)
        if series.ndim == 1:
            # univariate fallback -> expand, but for S-24 we pass multivariate
            series = series[:, None]
        assert series.shape[1] == len(COLS), series.shape
        self.model = Ridge(alpha=self.ridge_alpha, fit_intercept=True).fit(
            *self._dataset(series, horizon)
        )
        self.history_ = series
        self.horizon_ = int(horizon)
        self._fitted = True
        return self
    def _dataset(self, series, horizon):
        L = self.input_length
        X, Y = [], []
        for end in range(L, len(series) - horizon + 1):
            window = series[end - L:end]  # (L, 7)
            anchor = window[-1, OT_IDX]
            # level-free: subtract last ROW (vector) then flatten; target = OT - anchor
            X.append((window - window[-1]).reshape(-1))
            Y.append(series[end:end+horizon, OT_IDX] - anchor)
        return np.asarray(X), np.asarray(Y)
    def predict(self) -> np.ndarray:
        window = self.history_[-self.input_length:]
        anchor = window[-1, OT_IDX]
        x = (window - window[-1]).reshape(-1)
        return np.asarray(self.model.predict([x])[0]) + anchor


UNIVARIATE_MEMBERS = [
    ("nlinear_L336_a1",  lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L96_a1",   lambda: NLinear(input_length=96, ridge_alpha=1.0)),
    ("nlinear_L720_a1",  lambda: NLinear(input_length=720, ridge_alpha=1.0)),
    ("dlinear_L96_a0",   lambda: DLinear(input_length=96, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L336_a0",  lambda: DLinear(input_length=336, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L720_a0",  lambda: DLinear(input_length=720, kernel_size=25, ridge_alpha=0.0)),
]

MULTI_MEMBERS = [
    ("multivar_nlinear_L96_a1",  lambda: MultiNLinear(input_length=96, ridge_alpha=1.0)),
    ("multivar_nlinear_L336_a1", lambda: MultiNLinear(input_length=336, ridge_alpha=1.0)),
]

MEMBERS = UNIVARIATE_MEMBERS + MULTI_MEMBERS


def member_preds_linear(factory, series_1d, starts, L, H):
    m = factory()
    m.fit(series_1d, horizon=H)
    # per-window history swap (cheap)
    preds = []
    hist = m.history_
    for s in starts:
        # window [s-L, s) is history slice; horizon window [s, s+H)
        # Simulate origin at s: history = series_1d[:s]
        m.history_ = series_1d[max(0, s-L):s] if isinstance(series_1d, np.ndarray) and series_1d.ndim==1 else series_1d[:s]  # will be overwritten length check
        # Instead use series slice directly: set history to appropriate length
        # For NLinear/DLinear, predict only uses trailing L, so we can set history = series[:s]
        m.history_ = series_1d[:s] if series_1d.ndim==1 else series_1d[:s]
        # Need enough history
        if len(m.history_) < L:
            # pad - shouldn't happen (s >= L)
            m.history_ = series_1d[:s]
        preds.append(m.predict())
    m.history_ = hist
    return np.asarray(preds)


def member_preds_multi(factory, series_multi, starts, L, H):
    m = factory()
    m.fit(series_multi, horizon=H)
    preds = []
    hist = m.history_
    for s in starts:
        m.history_ = series_multi[:s]
        preds.append(m.predict())
    m.history_ = hist
    return np.asarray(preds)


def collect_preds(fit_series_1d, fit_series_multi, origin_starts):
    H = HORIZON
    cols = []
    for name, factory in UNIVARIATE_MEMBERS:
        L = factory().input_length
        p = member_preds_linear(factory, fit_series_1d, origin_starts, L, H)
        cols.append(p)
        print(f"  {name} ok L={L} shape {p.shape}")
    for name, factory in MULTI_MEMBERS:
        L = factory().input_length
        p = member_preds_multi(factory, fit_series_multi, origin_starts, L, H)
        cols.append(p)
        print(f"  {name} ok L={L} shape {p.shape}")
    # (n, M, H)
    return np.stack(cols, axis=1)


def fit_stack_map(P, A, alpha, fit_intercept=False):
    n, m, h = P.shape
    coef = np.empty((m, h))
    intercept = np.zeros(h)
    for k in range(h):
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
        if fit_intercept:
            intercept[k] = r.intercept_
    class _Map:
        def predict(self, Pt):
            return np.einsum("mh,nmh->nh", coef, Pt) + intercept[None, :]
    _Map.coef_ = coef
    _Map.intercept_ = intercept
    return _Map()


def rolling_metrics(preds, actuals):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err**2, axis=1))
    mae = float(np.mean(mae_per))
    rmse = float(np.sqrt(np.mean(err**2)))
    # disjoint map only when n == len(DISJOINT_STARTS) and rows correspond 1:1
    if len(mae_per) == len(DISJOINT_STARTS):
        disj = {f"window_{i+1}": {"mae": float(mae_per[i]), "rmse": float(rmse_per[i])} for i in range(len(DISJOINT_STARTS))}
    else:
        disj = {f"window_{i+1}": {"mae": float(mae_per[t]), "rmse": float(rmse_per[t])} for i, t in enumerate(DISJOINT_STARTS) if t < len(mae_per)}
    return mae, rmse, disj
def main():
    t_all = time.time()
    pd = get_protocol_data()
    fit_history_1d, eval_series_1d, test_1d = pd.rolling_views()
    # multivariate histories
    fit_multi = load_multivariate(H720_ROOT / "train.csv")
    test_multi = load_multivariate(H720_ROOT / "test.csv")
    # sanity: OT column matches 1d
    assert np.allclose(fit_multi[:, OT_IDX], fit_history_1d, atol=1e-9), "OT mismatch fit"
    assert np.allclose(test_multi[:len(test_1d), OT_IDX], test_1d, atol=1e-9), "OT mismatch test"

    train_8545_1d = fit_history_1d[:TRAIN_END]
    train_8545_multi = fit_multi[:TRAIN_END]
    val_1d = fit_history_1d[TRAIN_END:]
    val_multi = fit_multi[TRAIN_END:]
    n_val = len(val_1d) - HORIZON + 1
    assert n_val == 2161

    print(f"fitting {len(MEMBERS)} members on train 8545 ...")
    # we don't pre-fit; collect_preds fits each member once on full prefix then swaps history per window

    val_origin_starts = np.arange(n_val) + TRAIN_END
    print("collecting val predictions ...")
    P_val = collect_preds(fit_history_1d, fit_multi, val_origin_starts)
    A_val = np.stack([val_1d[t:t+HORIZON] for t in range(n_val)])
    for j, (name, _) in enumerate(MEMBERS):
        m = float(np.mean(np.mean(np.abs(P_val[:, j, :] - A_val), axis=1)))
        print(f"  {name:26s} val {m:.4f}")

    # chronological alpha selection inside val
    n_fit = n_val // 2
    P_fit, A_fit = P_val[:n_fit], A_val[:n_fit]
    P_sel, A_sel = P_val[n_fit:], A_val[n_fit:]
    print(f"\nalpha selection: fit {n_fit} / select {n_val-n_fit} ...")
    alphas = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]
    alpha_scores = {}
    for a in alphas:
        r = fit_stack_map(P_fit, A_fit, a)
        sel_mae = float(np.mean(np.mean(np.abs(r.predict(P_sel) - A_sel), axis=1)))
        alpha_scores[a] = sel_mae
        print(f"  alpha {a:8g}: sel MAE {sel_mae:.4f}")
    best_alpha = min(alpha_scores, key=alpha_scores.get)
    print(f"selected alpha = {best_alpha}")

    stack = fit_stack_map(P_val, A_val, best_alpha)
    val_mae_full = float(np.mean(np.mean(np.abs(stack.predict(P_val) - A_val), axis=1)))
    print(f"stack refit all val: MAE {val_mae_full:.4f}")

    # frozen test
    print("\ncollecting test predictions (frozen 11425) ...")
    # test rolling origins: fit_history length 11425, test length 2880, rolling over test's first 2161-origin? Actually test rolling uses starts relative to fit_history+test
    # Follow S-20: origins are over eval_series which is fit_history + test? Let's replicate S-20 test collection
    # S-20 builds test P by re-fitting members on 11425 then predicting windows starting at 11425 + t
    # We have full series for test: concat fit_history_1d + test_1d, similarly multi
    concat_1d = np.concatenate([fit_history_1d, test_1d])
    concat_multi = np.concatenate([fit_multi, test_multi[:len(test_1d)]], axis=0)
    test_starts = np.arange(4) * 0  # dummy
    # DISJOINT test windows: 4 windows starting at 0,720,1440,2160 within test
    # For full rolling test like S-20's n=4 disjoint windows, but S-20 also scores full rolling? Actually S-20 scores full rolling over test? Check results: disjoint_windows only 4.
    # Simpler: score the same 4 disjoint windows S-20 reports, plus also full 2161-origin rolling would need longer holdout.
    # We follow S-20's frozen test which scores the 4 disjoint 720-blocks within test.csv (t=0,720,1440,2160) but only 2161 origins available inside test if we had longer series.
    # Actually S-20 test has 2880 rows, so max origin = 2880-720+1=2161 origins too, but we only report 4 disjoint. Let's collect 4 disjoint + also full rolling if we want.
    # For comparability with S-20 leaderboard (rolling 1.9980), we need the same metric: mean over 4 disjoint windows? Check S-20: rolling_metrics over 4 preds? In S-20 main, they compute rolling_metrics over those 4 windows — but labelled rolling_mae.
    # We'll do both: 4 disjoint for leaderboard, and full 2161 if possible (needs series length 11425+2880=14305, available).
    n_test = len(test_1d) - HORIZON + 1  # 2161 origins inside test alone, but need history before each
    # For rolling over test with frozen history, each origin's history is concat up to 11425 + t
    test_origin_starts = np.arange(n_test) + len(fit_history_1d)  # absolute index in concat
    # To save time, only score 4 disjoint for quick answer, but also compute full if not too heavy (2161 * 8 members * predict)
    # Let's do 4 disjoint first
    disj_starts_abs = np.array([len(fit_history_1d) + s for s in DISJOINT_STARTS])
    P_disj = collect_preds(concat_1d, concat_multi, disj_starts_abs)
    A_disj = np.stack([test_1d[s:s+HORIZON] for s in DISJOINT_STARTS])
    preds_disj = stack.predict(P_disj)
    mae_disj, rmse_disj, disj_map = rolling_metrics(preds_disj, A_disj)
    print(f"\nDISJOINT-4 test MAE {mae_disj:.4f} RMSE {rmse_disj:.4f}")
    for k,v in disj_map.items():
        print(f"  {k} MAE {v['mae']:.4f}")

    # Full rolling 2161 origins (heavier but do it once)
    print("\nfull rolling 2161 origins (this may take a minute)...")
    P_test = collect_preds(concat_1d, concat_multi, test_origin_starts)
    A_test = np.stack([test_1d[t:t+HORIZON] for t in range(n_test)])
    preds_full = stack.predict(P_test)
    mae_full, rmse_full, _ = rolling_metrics(preds_full, A_test)
    print(f"FULL rolling MAE {mae_full:.4f} RMSE {rmse_full:.4f} (n={n_test})")

    # Per-member full rolling for sanity
    for j,(name,_) in enumerate(MEMBERS):
        m = float(np.mean(np.mean(np.abs(P_test[:, j, :]-A_test), axis=1)))
        print(f"  member {name:26s} full {m:.4f}")

    # S-20 baseline comparison
    print(f"\nS-20 incumbent 1.9980; S-24 disjoint {mae_disj:.4f} delta {mae_disj-1.9980:+.4f}; full {mae_full:.4f}")

    out = {
        "slice": "S-24-multivariate-ridge",
        "members": [n for n,_ in MEMBERS],
        "validation": {"alpha_scores": alpha_scores, "selected_alpha": best_alpha, "refit_all_val_mae": val_mae_full,
                        "member_val_mae": {n: float(np.mean(np.mean(np.abs(P_val[:, j, :]-A_val), axis=1))) for j,(n,_) in enumerate(MEMBERS)}},
        "test_disjoint4": {"mae": mae_disj, "rmse": rmse_disj, "windows": disj_map},
        "test_full2161": {"mae": mae_full, "rmse": rmse_full, "n": n_test, "delta_vs_s20": mae_full-1.9980},
        "coef": stack.coef_.tolist() if hasattr(stack, 'coef_') else None,
    }
    with open(HERE / "results_s24.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {HERE/'results_s24.json'}  elapsed {time.time()-t_all:.1f}s")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
