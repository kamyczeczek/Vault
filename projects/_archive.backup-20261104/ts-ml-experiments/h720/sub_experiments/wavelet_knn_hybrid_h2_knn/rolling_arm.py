"""H2-KNN — Wavelet + KNN Hybrid (Haar J=3, weighted distance, S-20-clean)."""
from __future__ import annotations
import json, sys, time, collections
from pathlib import Path
import numpy as np
import pywt
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
SEARCH_ALPHA = 3000.0
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]


class WaveletKNN:
    """Wavelet coefficient KNN: anchored Haar J=3 -> subband-weighted KNN -> delta forecast."""
    def __init__(self, input_length: int = 336, wavelet: str = "haar", levels: int = 3,
                 neighbors: int = 15, weights: str = "distance"):
        self.input_length = input_length
        self.wavelet = wavelet
        self.levels = levels
        self.neighbors = neighbors
        self.weights = weights
        self.model_ = None
        self.subband_energy_ = None
        self.history_ = None
        self.target_index = None
        self.horizon_ = None

    def fit(self, y, *, horizon: int, target_index: int = 0):
        series = np.asarray(y, dtype=float)
        if series.ndim == 1:
            series = series[:, None]
        L = self.input_length
        target = series[:, target_index]
        X, Y = [], []
        for end in range(L, len(target) - horizon + 1):
            window = target[end - L : end]
            anchor = window[-1]
            anchored = window - anchor
            coeffs = pywt.wavedec(anchored, self.wavelet, level=self.levels)
            flat = np.concatenate([c.ravel() for c in coeffs])
            X.append(flat)
            Y.append(series[end : end + horizon, target_index] - anchor)
        X = np.asarray(X)
        Y = np.asarray(Y)
        # Compute subband energies for weighted distance
        energies = []
        idx = 0
        for c in pywt.wavedec(np.zeros(L), self.wavelet, level=self.levels):
            length = len(c)
            energies.append(np.mean(X[:, idx : idx + length] ** 2, axis=0).mean())
            idx += length
        energies = np.array(energies)
        energies = energies / (energies.sum() + 1e-12)
        self.subband_energy_ = energies
        # Build weighted distance metric via feature scaling
        scale = np.zeros(X.shape[1])
        idx = 0
        for e, c in zip(energies, pywt.wavedec(np.zeros(L), self.wavelet, level=self.levels)):
            length = len(c)
            scale[idx : idx + length] = 1.0 / (e + 1e-12)
            idx += length
        X_weighted = X * scale[None, :]
        self.model_ = KNeighborsRegressor(
            n_neighbors=min(self.neighbors, len(X)),
            weights=self.weights,
        ).fit(X_weighted, Y)
        self.history_ = series
        self.target_index = target_index
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self):
        raw = self.history_[-self.input_length :]
        window = raw[:, None] if raw.ndim == 1 else raw
        anchor = window[-1, self.target_index]
        anchored = window[:, self.target_index] - anchor
        coeffs = pywt.wavedec(anchored, self.wavelet, level=self.levels)
        flat = np.concatenate([c.ravel() for c in coeffs]).reshape(1, -1)
        scale = np.zeros(flat.shape[1])
        idx = 0
        for e, c in zip(self.subband_energy_, pywt.wavedec(np.zeros(self.input_length), self.wavelet, level=self.levels)):
            length = len(c)
            scale[idx : idx + length] = 1.0 / (e + 1e-12)
            idx += length
        x_weighted = flat * scale[None, :]
        return np.asarray(self.model_.predict(x_weighted)[0]) + anchor


CANDIDATES = [
    ("nlinear_L336_a1",    lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10",   lambda: NLinear(input_length=336, ridge_alpha=10.0)),
    ("wavelet_knn_haar_L336", lambda: WaveletKNN(input_length=336, wavelet="haar", levels=3, neighbors=15, weights="distance")),
]


def fit_stack_map(P, A, alpha, fit_intercept=False):
    n, m, h = P.shape
    coef = np.empty((m, h))
    for k in range(h):
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
    inter = np.zeros(h)
    class _Map:
        def predict(self, Pt):
            return np.einsum("nmh,mh->nh", Pt, coef) + inter[None, :]
    _Map.coef_ = coef
    _Map.inter_ = inter
    return _Map()

def score_fast(P_val, A_val, idx, alpha=SEARCH_ALPHA):
    if len(idx) == 0:
        return float("inf")
    n2 = 1080
    Psub = P_val[:, idx, :]
    r = fit_stack_map(Psub[:n2], A_val[:n2], alpha)
    return float(np.mean(np.mean(np.abs(r.predict(Psub[n2:]) - A_val[n2:]), axis=1)))

def score_full(P_val, A_val, idx):
    if len(idx) == 0:
        return float("inf"), None
    n2 = 1080
    Psub = P_val[:, idx, :]
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
    hist = m.history_
    out = []
    t0 = time.time()
    for s in starts:
        m.history_ = full_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
        if s % 500 == 0:
            print(f"    preds_for_train_fit {s}/{len(starts)} ...")
    print(f"    preds_for_train_fit done in {time.time()-t0:.1f}s")
    m.history_ = hist
    return np.asarray(out)

def preds_for_full_fit(factory, full_series, concat_series, starts, L, H):
    m = factory()
    m.fit(full_series, horizon=H)
    hist = m.history_
    out = []
    t0 = time.time()
    for s in starts:
        m.history_ = concat_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
        if s % 500 == 0:
            print(f"    preds_for_full_fit {s}/{len(starts)} ...")
    print(f"    preds_for_full_fit done in {time.time()-t0:.1f}s")
    m.history_ = hist
    return np.asarray(out)

def collect_val(train_series, full_series, starts):
    cols = []
    for name, factory in CANDIDATES:
        L = factory().input_length
        print(f"  collecting val member {name} L={L} ...")
        p = preds_for_train_fit(factory, train_series, full_series, starts, L, HORIZON)
        cols.append(p)
    return np.stack(cols, axis=1)

def collect_test(full_series, concat_series, starts):
    cols = []
    for name, factory in CANDIDATES:
        L = factory().input_length
        print(f"  collecting test member {name} L={L} ...")
        p = preds_for_full_fit(factory, full_series, concat_series, starts, L, HORIZON)
        cols.append(p)
    return np.stack(cols, axis=1)

def rolling_metrics(preds, actuals):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err ** 2, axis=1))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err ** 2))), mae_per, rmse_per

def main():
    t_all = time.time()
    pd = get_protocol_data()
    fit_series, _, test_series = pd.rolling_views()
    train_series = fit_series[:TRAIN_END]
    val_series = fit_series[TRAIN_END:]
    n_val = len(val_series) - HORIZON + 1
    assert n_val == 2161
    val_starts = np.arange(n_val) + TRAIN_END

    print("H2-KNN — Wavelet + KNN Hybrid — S-20-clean protocol")
    print(f"train={len(train_series)} fit={len(fit_series)} test={len(test_series)}")

    P_val = collect_val(train_series, fit_series, val_starts)
    A_val = np.stack([val_series[t : t + HORIZON] for t in range(n_val)])

    single = [score_fast(P_val, A_val, [j]) for j in range(len(CANDIDATES))]
    cur_idx = [int(np.argmin(single))]
    cur_score = single[cur_idx[0]]
    best_idx = list(cur_idx)
    best_score = cur_score

    true_s, true_a = score_full(P_val, A_val, cur_idx)
    print(f"\ninit singleton {[CANDIDATES[i][0] for i in cur_idx]} fast {cur_score:.4f} true {true_s:.4f} a={true_a}")

    max_iter = 25
    no_improve = 0
    trace = []
    tabu = set()
    tabu.add(tuple(sorted(cur_idx)))
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
            "best_set": [CANDIDATES[i][0] for i in best_idx],
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

    concat = np.concatenate([fit_series, test_series])
    disj_starts = np.array([len(fit_series) + s for s in DISJOINT_STARTS])
    P_disj_all = collect_test(fit_series, concat, disj_starts)
    P_disj = P_disj_all[:, best_idx, :]
    A_disj = np.stack([test_series[s : s + HORIZON] for s in DISJOINT_STARTS])
    preds_disj = stack.predict(P_disj)
    mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)

    n_test = len(test_series) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_series)
    P_test_all = collect_test(fit_series, concat, test_starts)
    P_test = P_test_all[:, best_idx, :]
    A_test = np.stack([test_series[t : t + HORIZON] for t in range(n_test)])
    preds_full = stack.predict(P_test)
    mae_full, rmse_full, _, _ = rolling_metrics(preds_full, A_test)
    for j, i in enumerate(best_idx):
        m = float(np.mean(np.mean(np.abs(P_test[:, j, :] - A_test), axis=1)))
        print(f"  member {CANDIDATES[i][0]:20s} full {m:.4f}")

    accept = (mae_full < 1.9859) and (mae_disj <= 1.9696)
    out = {
        "slice": "H2-KNN-wavelet-knn-hybrid",
        "pool": [n for n, _ in CANDIDATES],
        "trace": trace,
        "best_subset": [CANDIDATES[i][0] for i in best_idx],
        "best_idx": best_idx,
        "best_fast": best_score,
        "best_alpha": best_alpha,
        "val_full": val_full,
        "test_disjoint": {"mae": mae_disj, "rmse": rmse_disj},
        "test_full": {
            "mae": mae_full,
            "rmse": rmse_full,
            "n": n_test,
            "delta_vs_s26": mae_full - 1.9909,
        },
        "accept": accept,
        "acceptance_criteria": {
            "full_mae_threshold": 1.9859,
            "disjoint_mae_cap": 1.9696,
            "incumbent_full": 1.9909,
            "incumbent_disjoint": 1.9696,
        },
        "protocol": "S-20-clean: val members frozen on 8545, test members refrozen on 11425",
    }
    with open(HERE / "results_h2_knn.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nACCEPT={accept}")
    print(f"wrote {HERE / 'results_h2_knn.json'} elapsed {time.time()-t_all:.1f}s")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
