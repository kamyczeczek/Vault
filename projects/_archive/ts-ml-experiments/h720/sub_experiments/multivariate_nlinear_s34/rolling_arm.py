"""S-34 — Exogenous-Channel Multivariate Linear Members (Multivariate Expansion)
under S-20-clean protocol.

Pool:
  - 12 univariate linear members from S-26 (NLinear, DLinear, RLinear)
  - 9 multivariate NLinear members operating across all 7 ETTh1 channels (OT, HUFL, HULL, MUFL, MULL, LUW, LUL)
    with L in {96, 336, 720} and ridge_alpha in {1.0, 10.0, 100.0}, level-free via last-row subtraction.

Protocol:
  - S-20-clean: members frozen on train (8,545 rows) for validation prediction collection;
    refit on full fit history (11,425 rows) for test predictions.
  - Chronological validation search: fit per-horizon ridge stack on val first half (1080 origins),
    select/score on val second half (1081 origins).
  - Tabu search over candidate pool with fixed alpha=3000 fast score, then full 11-alpha scan on winner.
  - Strict validation-to-test transfer check and performance comparison against S-26 incumbent (1.9909).

Run: python projects/ts-ml-experiments/h720/sub_experiments/multivariate_nlinear_s34/rolling_arm.py
"""
from __future__ import annotations
import json, sys, time, csv, collections
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, DLinear, RLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
SEARCH_ALPHA = 3000.0
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]

COLS = ["HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL", "OT"]
OT_IDX = 6

class MultiNLinear:
    """NLinear over 7-channel window, OT-anchored. Features = flattened (window - last_row)."""
    def __init__(self, input_length: int = 96, ridge_alpha: float = 1.0):
        self.input_length = input_length
        self.ridge_alpha = ridge_alpha
    def fit(self, y, *, horizon: int):
        series = np.asarray(y, dtype=float)
        if series.ndim == 1:
            series = series[:, None]
        assert series.shape[1] == len(COLS), series.shape
        self.model = Ridge(alpha=self.ridge_alpha, fit_intercept=False).fit(
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
            X.append((window - window[-1]).reshape(-1))
            Y.append(series[end:end+horizon, OT_IDX] - anchor)
        return np.asarray(X), np.asarray(Y)
    def predict(self) -> np.ndarray:
        window = self.history_[-self.input_length:]
        anchor = window[-1, OT_IDX]
        x = (window - window[-1]).reshape(-1)
        return np.asarray(self.model.predict([x])[0]) + anchor

UNIVARIATE_CANDIDATES = [
    ("nlinear_L96_a1",    lambda: NLinear(input_length=96, ridge_alpha=1.0)),
    ("nlinear_L96_a10",   lambda: NLinear(input_length=96, ridge_alpha=10.0)),
    ("nlinear_L96_a100",  lambda: NLinear(input_length=96, ridge_alpha=100.0)),
    ("nlinear_L336_a1",   lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10",  lambda: NLinear(input_length=336, ridge_alpha=10.0)),
    ("nlinear_L720_a1",   lambda: NLinear(input_length=720, ridge_alpha=1.0)),
    ("dlinear_L96_k25_a0",  lambda: DLinear(input_length=96, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L96_k49_a0",  lambda: DLinear(input_length=96, kernel_size=49, ridge_alpha=0.0)),
    ("dlinear_L336_k25_a0", lambda: DLinear(input_length=336, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L336_k49_a0", lambda: DLinear(input_length=336, kernel_size=49, ridge_alpha=0.0)),
    ("rlinear_L96_a0",    lambda: RLinear(input_length=96, ridge_alpha=0.0)),
    ("rlinear_L336_a0",   lambda: RLinear(input_length=336, ridge_alpha=0.0)),
]

MULTIVARIATE_CANDIDATES = [
    ("multivar_nlinear_L96_a1",   lambda: MultiNLinear(input_length=96, ridge_alpha=1.0)),
    ("multivar_nlinear_L96_a10",  lambda: MultiNLinear(input_length=96, ridge_alpha=10.0)),
    ("multivar_nlinear_L96_a100", lambda: MultiNLinear(input_length=96, ridge_alpha=100.0)),
    ("multivar_nlinear_L336_a1",  lambda: MultiNLinear(input_length=336, ridge_alpha=1.0)),
    ("multivar_nlinear_L336_a10", lambda: MultiNLinear(input_length=336, ridge_alpha=10.0)),
    ("multivar_nlinear_L336_a100",lambda: MultiNLinear(input_length=336, ridge_alpha=100.0)),
    ("multivar_nlinear_L720_a1",  lambda: MultiNLinear(input_length=720, ridge_alpha=1.0)),
    ("multivar_nlinear_L720_a10", lambda: MultiNLinear(input_length=720, ridge_alpha=10.0)),
    ("multivar_nlinear_L720_a100",lambda: MultiNLinear(input_length=720, ridge_alpha=100.0)),
]

CANDIDATES = UNIVARIATE_CANDIDATES + MULTIVARIATE_CANDIDATES

def fit_stack_map(P, A, alpha, fit_intercept=False):
    n, m, h = P.shape
    coef = np.empty((m, h))
    inter = np.zeros(h)
    for k in range(h):
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
    class _Map:
        def predict(self, Pt):
            return np.einsum("mh,nmh->nh", coef, Pt) + inter[None, :]
    _Map.coef_ = coef
    _Map.inter_ = inter
    return _Map()

def score_fast(P_val, A_val, idx, alpha=SEARCH_ALPHA):
    if len(idx) == 0:
        return float("inf")
    if len(idx) == 1:
        n = len(A_val)
        n2 = n // 2
        return float(np.mean(np.mean(np.abs(P_val[n2:, idx[0], :] - A_val[n2:]), axis=1)))
    Psub = P_val[:, idx, :]
    n = len(A_val)
    n2 = n // 2
    r = fit_stack_map(Psub[:n2], A_val[:n2], alpha)
    return float(np.mean(np.mean(np.abs(r.predict(Psub[n2:]) - A_val[n2:]), axis=1)))

def score_full(P_val, A_val, idx):
    if len(idx) == 0:
        return float("inf"), None
    if len(idx) == 1:
        n = len(A_val)
        n2 = n // 2
        mae = float(np.mean(np.mean(np.abs(P_val[n2:, idx[0], :] - A_val[n2:]), axis=1)))
        return mae, None
    Psub = P_val[:, idx, :]
    n = len(A_val)
    n2 = n // 2
    best = None
    best_a = None
    for a in ALPHAS:
        r = fit_stack_map(Psub[:n2], A_val[:n2], a)
        sel = float(np.mean(np.mean(np.abs(r.predict(Psub[n2:]) - A_val[n2:]), axis=1)))
        if best is None or sel < best:
            best = sel
            best_a = a
    return best, best_a

def preds_for_train_fit(factory, train_series, full_series, starts, L, H):
    m = factory()
    m.fit(train_series, horizon=H)
    out = []
    for s in starts:
        m.history_ = full_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    return np.asarray(out)

def preds_for_full_fit(factory, full_series, concat_series, starts, L, H):
    m = factory()
    m.fit(full_series, horizon=H)
    out = []
    for s in starts:
        m.history_ = concat_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    return np.asarray(out)

def load_multivariate_split():
    train_path = H720_ROOT / "train.csv"
    test_path = H720_ROOT / "test.csv"
    with open(train_path) as f:
        reader = csv.DictReader(f)
        train_rows = [[float(r[c]) for c in COLS] for r in reader]
    with open(test_path) as f:
        reader = csv.DictReader(f)
        test_rows = [[float(r[c]) for c in COLS] for r in reader]
    train_multi = np.asarray(train_rows, dtype=float)
    test_multi = np.asarray(test_rows, dtype=float)
    fit_multi = train_multi
    concat_multi = np.concatenate([fit_multi, test_multi], axis=0)
    return fit_multi, concat_multi, test_multi

def collect_val(train_1d, fit_1d, train_multi, fit_multi, starts):
    cols = []
    for name, factory in CANDIDATES:
        m = factory()
        L = m.input_length
        is_multi = isinstance(m, MultiNLinear)
        if is_multi:
            p = preds_for_train_fit(factory, train_multi, fit_multi, starts, L, HORIZON)
        else:
            p = preds_for_train_fit(factory, train_1d, fit_1d, starts, L, HORIZON)
        cols.append(p)
        print(f"  {name:25s} L={L:3d} multi={is_multi} ok {p.shape}")
    return np.stack(cols, axis=1)

def collect_test(fit_1d, concat_1d, fit_multi, concat_multi, starts):
    cols = []
    for name, factory in CANDIDATES:
        m = factory()
        L = m.input_length
        is_multi = isinstance(m, MultiNLinear)
        if is_multi:
            p = preds_for_full_fit(factory, fit_multi, concat_multi, starts, L, HORIZON)
        else:
            p = preds_for_full_fit(factory, fit_1d, concat_1d, starts, L, HORIZON)
        cols.append(p)
    return np.stack(cols, axis=1)

def rolling_metrics(preds, actuals):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err**2, axis=1))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err**2))), mae_per, rmse_per

def main():
    t_all = time.time()
    pd = get_protocol_data()
    fit_1d, _, test_1d = pd.rolling_views()
    train_1d = fit_1d[:TRAIN_END]
    val_1d = fit_1d[TRAIN_END:]

    fit_multi, concat_multi, test_multi = load_multivariate_split()
    train_multi = fit_multi[:TRAIN_END]
    val_multi = fit_multi[TRAIN_END:]

    n_val = len(val_1d) - HORIZON + 1
    assert n_val == 2161
    val_starts = np.arange(n_val) + TRAIN_END

    print(f"collecting P_val for {len(CANDIDATES)} candidates (val {n_val} origins)...")
    P_val = collect_val(train_1d, fit_1d, train_multi, fit_multi, val_starts)
    A_val = np.stack([val_1d[t:t+HORIZON] for t in range(n_val)])

    for j, (name, _) in enumerate(CANDIDATES):
        mae = float(np.mean(np.mean(np.abs(P_val[:, j, :] - A_val), axis=1)))
        print(f"  {name:25s} val {mae:.4f}")

    single = [score_fast(P_val, A_val, [j]) for j in range(len(CANDIDATES))]
    cur_idx = [int(np.argmin(single))]
    cur_score = single[cur_idx[0]]
    best_idx = list(cur_idx)
    best_score = cur_score
    ts, _ = score_full(P_val, A_val, cur_idx)
    print(f"\ninit singleton {[CANDIDATES[i][0] for i in cur_idx]} fast {cur_score:.4f} true {ts:.4f}")

    tabu = set()
    q = collections.deque(maxlen=7)
    def key(idx): return tuple(sorted(idx))
    tabu.add(key(cur_idx))
    q.append(key(cur_idx))
    max_iter = 25
    no_improve = 0
    trace = []

    for it in range(max_iter):
        cur_set = set(cur_idx)
        all_set = set(range(len(CANDIDATES)))
        neigh = []
        for j in sorted(all_set - cur_set):
            neigh.append(sorted(cur_set | {j}))
        if len(cur_set) > 1:
            for j in sorted(cur_set):
                neigh.append(sorted(cur_set - {j}))
        for oj in sorted(cur_set):
            for ij in sorted(all_set - cur_set):
                neigh.append(sorted((cur_set - {oj}) | {ij}))
        uniq = []
        seen = set()
        for nb in neigh:
            k = tuple(nb)
            if k not in seen:
                seen.add(k)
                uniq.append(nb)
        scored = [(score_fast(P_val, A_val, nb), SEARCH_ALPHA, nb) for nb in uniq]
        scored.sort(key=lambda x: x[0])
        picked = None
        for s, a, nb in scored:
            k = tuple(nb)
            if k not in tabu or s < best_score - 1e-9:
                picked = (s, a, nb)
                break
        if picked is None:
            picked = scored[0]
        s, a, nb = picked
        cur_idx = nb
        cur_score = s
        k = tuple(nb)
        tabu.add(k)
        q.append(k)
        improved = s < best_score - 1e-9
        if improved:
            best_idx = list(nb)
            best_score = s
            no_improve = 0
        else:
            no_improve += 1
        true_s, true_a = score_full(P_val, A_val, nb) if (improved or it % 3 == 0) else (s, SEARCH_ALPHA)
        trace.append({
            "iter": it,
            "cur": [CANDIDATES[i][0] for i in nb],
            "fast": float(s),
            "true": float(true_s),
            "alpha": true_a,
            "best_fast": float(best_score),
            "best_set": [CANDIDATES[i][0] for i in best_idx]
        })
        print(f"iter {it:2d} cur {[CANDIDATES[i][0] for i in nb]} fast {s:.4f} true {true_s:.4f} a={true_a} best_fast {best_score:.4f} {[CANDIDATES[i][0] for i in best_idx]}")
        if no_improve >= 5:
            print("  no improve 5 iters -> stop")
            break

    print(f"\nbest subset fast {best_score:.4f}: {[CANDIDATES[i][0] for i in best_idx]}")
    _, best_alpha = score_full(P_val, A_val, best_idx)
    P_best = P_val[:, best_idx, :]
    stack = fit_stack_map(P_best, A_val, best_alpha if best_alpha is not None else SEARCH_ALPHA)
    val_full = float(np.mean(np.mean(np.abs(stack.predict(P_best) - A_val), axis=1)))
    print(f"refit all val MAE {val_full:.4f} alpha {best_alpha}")

    # Test evaluation
    disj_starts = np.array([len(fit_1d) + s for s in DISJOINT_STARTS])
    P_disj_all = collect_test(fit_1d, np.concatenate([fit_1d, test_1d]), fit_multi, concat_multi, disj_starts)
    P_disj = P_disj_all[:, best_idx, :]
    A_disj = np.stack([test_1d[s:s+HORIZON] for s in DISJOINT_STARTS])
    preds_disj = stack.predict(P_disj)
    mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)

    n_test = len(test_1d) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_1d)
    P_test_all = collect_test(fit_1d, np.concatenate([fit_1d, test_1d]), fit_multi, concat_multi, test_starts)
    P_test = P_test_all[:, best_idx, :]
    A_test = np.stack([test_1d[t:t+HORIZON] for t in range(n_test)])
    preds_full = stack.predict(P_test)
    mae_full, rmse_full, _, _ = rolling_metrics(preds_full, A_test)

    print(f"\nS-26 Incumbent MAE 1.9909 / RMSE 2.4710")
    print(f"S-34 Multivariate Best Subset: {[CANDIDATES[i][0] for i in best_idx]}")
    print(f"S-34 Test Disjoint MAE {mae_disj:.4f}, Full Rolling MAE {mae_full:.4f} / RMSE {rmse_full:.4f}")
    delta = mae_full - 1.9909
    print(f"Delta vs S-26: {delta:+.4f}")

    out = {
        "slice": "S-34-multivariate-nlinear",
        "pool": [n for n, _ in CANDIDATES],
        "trace": trace,
        "best_subset": [CANDIDATES[i][0] for i in best_idx],
        "best_idx": best_idx,
        "best_fast": best_score,
        "best_alpha": best_alpha,
        "val_full": val_full,
        "test_disjoint": {"mae": mae_disj, "rmse": rmse_disj},
        "test_full": {"mae": mae_full, "rmse": rmse_full, "n": n_test, "delta_vs_s26": delta},
        "protocol": "S-20-clean: val members frozen on 8545, test members refrozen on 11425"
    }
    with open(HERE / "results_s34.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {HERE / 'results_s34.json'} elapsed {time.time()-t_all:.1f}s")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
