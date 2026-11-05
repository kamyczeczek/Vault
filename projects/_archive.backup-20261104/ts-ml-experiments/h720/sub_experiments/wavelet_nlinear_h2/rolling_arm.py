"""H2 — Dyadic Wavelet NLinear (J=3) under the S-20-clean protocol.

Hypothesis (CONTEXT.md H2 slice spec): decompose the last-value-anchored
336-step OT window with a J=3 dyadic orthogonal DWT (Haar / db2,
periodization) into A3 (scale 8h), D3, D2, D1, and map each subband to
the 720-step horizon with a dedicated linear head, using subband-
dependent Ridge shrinkage — heavier on the fine detail bands D1/D2
(A3 << D3 < D2 < D1 penalty).

Member realization: a per-subband block-scaled Ridge solved in closed
form — one shared global intercept, weights per feature penalised as
||y - Xw - b||^2 + sum_k alpha_k * ||w_k||^2 with alpha_k = base *
ratio^k, k = subband level (k=0 A3 .. k=3 D1). Uniform-alpha limit
(ratio=1) is rotation-invariant => exactly NLinear(336, alpha): the
wavelet member is a strict generalisation of NLinear L336.

Protocol — mirrors S-26 (greedy_linear_mixture_s26/rolling_arm.py) exactly:
  * val member preds: fit on train 8545 (preds_for_train_fit), predict the
    2161 rolling val origins via history swap;
  * test member preds: refit on full train 11425 (preds_for_full_fit),
    predict over concat(fit, test) origins — zero leakage;
  * chronological val split: fast score fits stack on val[0:1080),
    score_full / final selection on held-out val[1080:2161);
  * greedy-tabu search (tabu 7, add/drop/swap1, init best singleton,
    aspiration, stop after 5 no-improve) over the 4-member pool;
  * frozen test selector = full 2161 rolling MAE, disjoint-4 diagnostic.

Acceptance: Full 2161 MAE < 1.9859 AND disjoint-4 <= 1.9696 vs S-26
incumbent 1.9909 / 1.9696. Anchors: NLinear L336 a=1 singleton 2.0571
(t=0 leaderboard row); S-26 = 1.9909 / 2.4710 (disjoint-4 1.9696).

Run: python projects/ts-ml-experiments/h720/sub_experiments/wavelet_nlinear_h2/rolling_arm.py
"""
from __future__ import annotations
import json, sys, time, collections
from pathlib import Path
import numpy as np
import pywt
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
SEARCH_ALPHA = 3000.0
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]
N_VAL_SPLIT = 1080  # chronological: fit stack on val[0:1080), select on val[1080:2161)
WAVELET_LEVELS = 3

# subband alpha profiles: (name, wavelet, base, ratio) -> alpha_k = base * ratio^k, k=0(A3)..3(D1)
WAVELET_PROFILES = [
    ("w_haar_base100_r3",  "haar", 100.0,  3.0),
    ("w_haar_base10_r30",  "haar", 10.0,  30.0),
    ("w_db2_base100_r3",   "db2",  100.0,  3.0),
    ("w_db2_base10_r30",   "db2",  10.0,  30.0),
    ("w_haar_base100_r10", "haar", 100.0, 10.0),
    ("w_db2_base100_r10",  "db2",  100.0, 10.0),
    ("w_haar_base1000_r10", "haar", 1000.0, 10.0),
]


class WaveletNLinear:
    """Dyadic J=3 wavelet member: anchored window -> DWT subbands ->
    block-scaled Ridge with per-subband alpha ladder + global intercept.

    Closed form: center X, Y; W = (S + diag(a))^-1 Xc^T Yc with
    S = Xc^T Xc; b = ym - xm W. alpha_k = base * ratio^k per subband k
    (A3, D3, D2, D1 order; ratio > 1 => heavier shrinkage on fine details).
    """

    def __init__(self, input_length: int = 336, wavelet: str = "haar",
                 levels: int = 3, base: float = 100.0, ratio: float = 3.0):
        self.input_length = input_length
        self.wavelet = wavelet
        self.levels = levels
        self.base = base
        self.ratio = ratio

    def _features(self, target: np.ndarray, ends: np.ndarray):
        L = self.input_length
        idx = np.asarray(ends)[:, None] + np.arange(-L, 0)[None, :]
        SW = target[idx]
        anchors = SW[:, -1].copy()
        X = SW - anchors[:, None]
        coeffs = pywt.wavedec(X, self.wavelet, level=self.levels,
                             mode="periodization", axis=-1)
        flat = np.concatenate(coeffs, axis=-1)
        return flat, anchors

    def fit(self, y, *, horizon: int, target_index: int = 0):
        series = np.asarray(y, dtype=float)
        if series.ndim == 1:
            series = series[:, None]
        target = series[:, target_index]
        if len(target) <= self.input_length + horizon:
            raise ValueError("insufficient history")
        ends = np.arange(self.input_length, len(target) - horizon + 1)
        X, _ = self._features(target, ends)
        Y = np.stack([target[e:e + horizon] - target[e - 1] for e in ends])
        lens = [len(c) for c in pywt.wavedec(np.zeros(self.input_length),
                self.wavelet, level=self.levels, mode="periodization")]
        apf = np.concatenate([np.full(n, self.base * self.ratio ** k)
                              for k, n in enumerate(lens)])
        xm = X.mean(axis=0); ym = Y.mean(axis=0)
        Xc = X - xm; Yc = Y - ym
        self.W_ = np.linalg.solve(Xc.T @ Xc + np.diag(apf), Xc.T @ Yc)
        self.b_ = ym - xm @ self.W_
        self.history_ = series
        self.target_index = target_index
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def _check_fitted(self):
        if not getattr(self, "_fitted", False):
            raise RuntimeError("fit must be called before predict")

    def predict(self):
        self._check_fitted()
        raw = self.history_[-self.input_length:]
        w = raw if raw.ndim == 1 else raw[:, self.target_index]
        anchor = w[-1]
        coeffs = pywt.wavedec(w - anchor, self.wavelet, level=self.levels,
                              mode="periodization")
        flat = np.concatenate([np.asarray(c).ravel() for c in coeffs]).reshape(1, -1)
        return np.asarray((flat @ self.W_ + self.b_)[0] + anchor, dtype=float)


class _Map:
    def __init__(self, coef):
        self.coef_ = coef
        self.inter_ = np.zeros(coef.shape[1])

    def predict(self, Pt):
        return np.einsum("mh,nmh->nh", self.coef_, Pt) + self.inter_[None, :]


def fit_stack_map(P, A, alpha, fit_intercept=False):
    n, m, h = P.shape
    coef = np.empty((m, h))
    for k in range(h):
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
    return _Map(coef)


def preds_for_train_fit(factory, train_series, full_series, starts, L, H):
    """Fit on train_series (8545), predict origins in full_series via history swap."""
    m = factory()
    m.fit(train_series, horizon=H)
    hist = m.history_
    out = []
    for s in starts:
        m.history_ = full_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_ = hist
    return np.asarray(out)


def preds_for_full_fit(factory, full_series, concat_series, starts, L, H):
    """Fit on full_series (11425), predict origins in concat via history swap."""
    m = factory()
    m.fit(full_series, horizon=H)
    hist = m.history_
    out = []
    for s in starts:
        m.history_ = concat_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_ = hist
    return np.asarray(out)


def rolling_metrics(preds, actuals):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err ** 2, axis=1))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err ** 2))), mae_per, rmse_per


def main():
    t_all = time.time()
    pd_ = get_protocol_data()
    fit_series, _, test_series = pd_.rolling_views()
    train_series = fit_series[:TRAIN_END]
    val_series = fit_series[TRAIN_END:]
    n_val = len(val_series) - HORIZON + 1
    assert n_val == 2161
    assert len(train_series) == 8545 and len(fit_series) == 11425
    val_starts = np.arange(n_val) + TRAIN_END

    # candidate pool: S-26 incumbent members + wavelet members (alpha ladder)
    candidates = [
        ("nlinear_L336_a1",  lambda: NLinear(input_length=336, ridge_alpha=1.0)),
        ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
    ]
    candidates += [
        (n, (lambda w=w, b=b, r=r: WaveletNLinear(
            input_length=336, wavelet=w, levels=WAVELET_LEVELS, base=b, ratio=r)))
        for (n, w, b, r) in WAVELET_PROFILES
    ]

    print("H2 — Dyadic Wavelet NLinear J=3 — S-20-clean protocol")
    print(f"pool {len(candidates)}: " + ", ".join(n for n, _ in candidates))
    print(f"train={len(train_series)} fit={len(fit_series)} test={len(test_series)}")
    print(f"val split: search [0:{N_VAL_SPLIT}) / select [{N_VAL_SPLIT}:{n_val})")

    # ---- val member predictions (members frozen on 8545) ----
    print("collecting P_val (val members frozen on 8545)...")
    cols = []
    for name, factory in candidates:
        L = factory().input_length
        p = preds_for_train_fit(factory, train_series, fit_series, val_starts, L, HORIZON)
        cols.append(p)
        print(f"  {name:22s} L={L:3d} ok {p.shape}")
    P_val = np.stack(cols, axis=1)
    A_val = np.stack([val_series[t:t + HORIZON] for t in range(n_val)])

    # chronological split (S-26): stacks fit on val[0:1080), scored on held-out val[1080:2161)
    n2 = n_val // 2
    assert n2 == N_VAL_SPLIT

    print("\nsingleton val MAE (raw members, held-out half [1080:2161)):")
    singleton_sel = {}
    for j, (name, _) in enumerate(candidates):
        sel = float(np.mean(np.abs(P_val[n2:, j, :] - A_val[n2:])))
        singleton_sel[name] = sel
        full = float(np.mean(np.abs(P_val[:, j, :] - A_val)))
        print(f"  {name:22s} held-out {sel:.4f}  full {full:.4f}")

    def score_fast(idx):
        if len(idx) == 0:
            return float("inf")
        if len(idx) == 1:
            return float(np.mean(np.abs(P_val[n2:, idx[0], :] - A_val[n2:])))
        Psub = P_val[:, idx, :]
        r = fit_stack_map(Psub[:n2], A_val[:n2], SEARCH_ALPHA)
        return float(np.mean(np.abs(r.predict(Psub[n2:]) - A_val[n2:])))

    def score_full(idx):
        if len(idx) == 0:
            return float("inf"), None
        if len(idx) == 1:
            return float(np.mean(np.abs(P_val[n2:, idx[0], :] - A_val[n2:]))), None
        Psub = P_val[:, idx, :]
        best, best_a = None, None
        for a in ALPHAS:
            r = fit_stack_map(Psub[:n2], A_val[:n2], a)
            sel = float(np.mean(np.abs(r.predict(Psub[n2:]) - A_val[n2:])))
            if best is None or sel < best:
                best, best_a = sel, a
        return best, best_a

    # ---- greedy-tabu (S-26 loop structure) ----
    single = [score_fast([j]) for j in range(len(candidates))]
    cur_idx = [int(np.argmin(single))]
    cur_score = single[cur_idx[0]]
    best_idx = list(cur_idx)
    best_score = cur_score
    ts, ta = score_full(cur_idx)
    print(f"\ninit singleton {[candidates[i][0] for i in cur_idx]} fast {cur_score:.4f} true {ts:.4f} a={ta}")

    tabu = set()
    q = collections.deque(maxlen=7)
    def key(idx): return tuple(sorted(idx))
    tabu.add(key(cur_idx)); q.append(key(cur_idx))
    max_iter = 25; no_improve = 0; trace = []
    for it in range(max_iter):
        cur_set = set(cur_idx); all_set = set(range(len(candidates)))
        neigh = []
        for j in sorted(all_set - cur_set):
            neigh.append(sorted(cur_set | {j}))
        if len(cur_set) > 1:
            for j in sorted(cur_set):
                neigh.append(sorted(cur_set - {j}))
        for oj in sorted(cur_set):
            for ij in sorted(all_set - cur_set):
                neigh.append(sorted((cur_set - {oj}) | {ij}))
        uniq = []; seen = set()
        for nb in neigh:
            k = tuple(nb)
            if k not in seen:
                seen.add(k); uniq.append(nb)
        scored = [(score_fast(nb), nb) for nb in uniq]
        scored.sort(key=lambda x: x[0])
        picked = None
        for s, nb in scored:
            if tuple(nb) not in tabu or s < best_score - 1e-9:
                picked = (s, nb); break
        if picked is None:
            picked = scored[0]
        s, nb = picked
        cur_idx = nb; cur_score = s
        k = tuple(nb); tabu.add(k); q.append(k)
        improved = s < best_score - 1e-9
        if improved:
            best_idx = list(nb); best_score = s; no_improve = 0
        else:
            no_improve += 1
        true_s, true_a = score_full(nb) if (improved or it % 3 == 0) else (s, SEARCH_ALPHA)
        trace.append({"iter": it, "cur": [candidates[i][0] for i in nb],
                      "fast": float(s), "true": float(true_s), "alpha": true_a,
                      "best_fast": float(best_score),
                      "best_set": [candidates[i][0] for i in best_idx]})
        print(f"iter {it:2d} cur {[candidates[i][0] for i in nb]} fast {s:.4f} true {true_s:.4f} a={true_a} best_fast {best_score:.4f} {[candidates[i][0] for i in best_idx]}")
        if no_improve >= 5:
            print("  no improve 5 iters -> stop")
            break

    print(f"\nbest subset fast {best_score:.4f}: {[candidates[i][0] for i in best_idx]}")
    best_sel_mae, best_alpha = score_full(best_idx)
    print(f"best subset held-out select-half MAE {best_sel_mae:.4f} alpha {best_alpha}")

    # final stack (S-26): refit on the full 2161 val origins at the selected alpha
    P_best = P_val[:, best_idx, :]
    stack = fit_stack_map(P_best, A_val,
                          best_alpha if best_alpha is not None else SEARCH_ALPHA)
    val_full = float(np.mean(np.abs(stack.predict(P_best) - A_val)))
    print(f"refit-all-val MAE {val_full:.4f} alpha {best_alpha}")

    # acceptance #3: subband coefficient stability under refit-all-val —
    # refit each wavelet member on all 2161 val origins and compare per-subband
    # weight norms against the frozen-8545 fit (no explosion in D1/D2/D3)
    print("\nsubband coefficient stability (refit-all-val vs frozen-8545):")
    subband_stability = {}
    for (pname, wname, base_, ratio_) in WAVELET_PROFILES:
        m_frozen = WaveletNLinear(input_length=336, wavelet=wname,
                                  levels=WAVELET_LEVELS, base=base_, ratio=ratio_)
        m_frozen.fit(train_series, horizon=HORIZON)
        m_refit = WaveletNLinear(input_length=336, wavelet=wname,
                                 levels=WAVELET_LEVELS, base=base_, ratio=ratio_)
        m_refit.fit(fit_series, horizon=HORIZON)
        lens = [len(c) for c in pywt.wavedec(np.zeros(336), wname,
                 level=WAVELET_LEVELS, mode="periodization")]
        entry = {"subband_lens": lens}
        stable = True
        off = 0
        for k, n_ in enumerate(lens):  # k=0 A3 .. k=3 D1
            nf = float(np.sqrt(np.mean(m_frozen.W_[off:off + n_, :] ** 2)))
            nr = float(np.sqrt(np.mean(m_refit.W_[off:off + n_, :] ** 2)))
            ratio_k = nr / max(nf, 1e-12)
            entry[f"norm_A3D3D2D1_{k}"] = {"frozen": nf, "refit": nr, "ratio": ratio_k}
            if not np.isfinite(ratio_k) or ratio_k > 10.0:
                stable = False
            off += n_
        entry["stable"] = stable
        subband_stability[pname] = entry
        worst = max(entry[f"norm_A3D3D2D1_{k}"]["ratio"] for k in range(4))
        print(f"  {pname:22s} worst subband norm ratio (refit/frozen) {worst:.3f} stable={stable}")

    # ---- frozen test pass (members refrozen on 11425) ----
    concat = np.concatenate([fit_series, test_series])
    disj_starts = np.array([len(fit_series) + s for s in DISJOINT_STARTS])
    n_test = len(test_series) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_series)
    all_starts = np.concatenate([disj_starts, test_starts])
    print(f"\ncollecting P_test (members refrozen on 11425; {len(disj_starts)} disjoint + {n_test} full)...")
    cols = []
    for name, factory in candidates:
        L = factory().input_length
        p = preds_for_full_fit(factory, fit_series, concat, all_starts, L, HORIZON)
        cols.append(p)
        print(f"  {name:22s} L={L:3d} ok {p.shape}")
    P_all = np.stack(cols, axis=1)
    P_disj = P_all[:len(disj_starts)][:, best_idx, :]
    P_test = P_all[len(disj_starts):][:, best_idx, :]
    A_disj = np.stack([test_series[s:s + HORIZON] for s in DISJOINT_STARTS])
    A_test = np.stack([test_series[t:t + HORIZON] for t in range(n_test)])

    preds_disj = stack.predict(P_disj)
    mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)
    preds_full = stack.predict(P_test)
    mae_full, rmse_full, _, _ = rolling_metrics(preds_full, A_test)
    for j, i in enumerate(best_idx):
        m = float(np.mean(np.abs(P_test[:, j, :] - A_test)))
        print(f"  member {candidates[i][0]:22s} full {m:.4f}")

    # singleton full-test metrics for every pool member (frozen-11425 pass)
    sing_test = {}
    for j, (name, _) in enumerate(candidates):
        mae_s, rmse_s, _, _ = rolling_metrics(P_all[len(disj_starts):][:, j, :], A_test)
        sing_test[name] = {"mae": mae_s, "rmse": rmse_s}
        print(f"  singleton {name:22s} full-test {mae_s:.4f} / rmse {rmse_s:.4f}")

    # ---- verdict ----
    accept = (mae_full < 1.9859) and (mae_disj <= 1.9696)
    print(f"\nS-26 incumbent full 1.9909 / disjoint 1.9696; NLinear L336 a1 singleton 2.0571")
    print(f"H2 best full {mae_full:.4f} disjoint {mae_disj:.4f} (delta vs S-26 {mae_full - 1.9909:+.4f})")
    print(f"ACCEPT={accept}")

    metrics = {
        "singleton_wavelet": sing_test,
        "singleton_val_held_out": {n: v for n, v in singleton_sel.items()},
        "best_ensemble": {
            "members": [candidates[i][0] for i in best_idx],
            "val_full_mae": val_full,
            "full_mae": mae_full, "full_rmse": rmse_full, "full_n": n_test,
            "disjoint4_mae": mae_disj, "disjoint4_rmse": rmse_disj,
            "held_out_select_mae": best_sel_mae,
            "alpha": best_alpha,
        },
        "subband_stability": subband_stability,
        "verdict": "ACCEPT" if accept else "REJECT",
    }

    # wavelet-vs-nlinear val spread over pool members (drives plan_impact text)
    nlin_sel = min(singleton_sel[n] for n, _ in candidates if n.startswith("nlinear"))
    w_sel = [v for n, v in singleton_sel.items() if n.startswith("w_")]
    w_best_sel = min(w_sel); w_worst_sel = max(w_sel)
    w_test = {n: sing_test[n]["mae"] for n in sing_test if n.startswith("w_")}
    w_best_test = min(w_test.values())

    plan_impact = {
        "invalidates": [],
        "confirms": [
            "Univariate linear family remains the ceiling: the J=3 dyadic orthogonal "
            "wavelet basis (Haar/db2, periodization) spans the same 336-dim "
            "anchored-window space as NLinear L336 — a uniform-alpha wavelet Ridge is "
            "exactly NLinear(alpha) by rotation invariance, so the family adds no new "
            "hypothesis capacity. Observed: best wavelet member held-out val "
            f"{w_best_sel:.4f} vs best NLinear member {nlin_sel:.4f}; best wavelet "
            f"singleton full-test {w_best_test:.4f} vs pinned NLinear L336 a=1 "
            "singleton 2.0571. Basis change alone cannot move the needle.",
            "S-26 greedy-tabu protocol reproducibility: chronological val split "
            "(stack fit on val[0:1080), held-out select on val[1080:2161)), "
            "frozen-8545/refrozen-11425 member factories, disjoint-4 diagnostic and "
            "acceptance thresholds transfer unchanged to a new member family.",
        ],
        "opens": [],
    }
    if accept:
        plan_impact["opens"].append(
            "H2 ACCEPT: per-subband shrinkage generalised the incumbent — explore "
            "J>3 levels and non-dyadic/biorthogonal bases under the same protocol."
        )
    else:
        plan_impact["invalidates"].append(
            "H2 hypothesis (dyadic J=3 wavelet decomposition with subband-dependent "
            "Ridge shrinkage beats the S-26 incumbent under S-20-clean): REJECTED — "
            f"full rolling MAE {mae_full:.4f} vs threshold 1.9859 (S-26 1.9909), "
            f"disjoint-4 {mae_disj:.4f} vs cap 1.9696. Per the CONTEXT.md stop rule, "
            "the univariate linear family is declared saturated under current "
            "protocol limits; next gains require leaving the linear/level-free "
            "univariate regime (non-linear readouts, exogenous channels, or a "
            "protocol change)."
        )
        plan_impact["opens"].append(
            "Per the CONTEXT.md H2 stop rule, close the univariate-linear frontier "
            "line: no further basis/shrinkage variants (wavelet, FITS, per-horizon "
            "penalties) on OT alone; redirect to the frontier's remaining steps."
        )

    out = {
        "slice": "H2-wavelet-nlinear",
        "harness_command": "python projects/ts-ml-experiments/h720/sub_experiments/wavelet_nlinear_h2/rolling_arm.py",
        "harness_log": str((HERE / "harness.log").resolve()),
        "pool": [n for n, _ in candidates],
        "wavelet_profiles": [{"name": n, "wavelet": w, "base": b, "ratio": r}
                             for (n, w, b, r) in WAVELET_PROFILES],
        "levels": WAVELET_LEVELS,
        "trace": trace,
        "best_subset": [candidates[i][0] for i in best_idx],
        "best_idx": best_idx,
        "best_fast": best_score,
        "best_alpha": best_alpha,
        "held_out_select_mae": best_sel_mae,
        "val_full": val_full,
        "metrics": metrics,
        "test_disjoint": {"mae": mae_disj, "rmse": rmse_disj},
        "test_full": {"mae": mae_full, "rmse": rmse_full, "n": n_test,
                      "delta_vs_s26": mae_full - 1.9909},
        "accept": accept,
        "acceptance_criteria": {
            "full_mae_threshold": 1.9859,
            "disjoint_mae_cap": 1.9696,
            "incumbent_full": 1.9909,
            "incumbent_disjoint": 1.9696,
            "nlinear_L336_a1_singleton": 2.0571,
        },
        "plan_impact": plan_impact,
        "protocol": "S-20-clean: val members frozen on 8545, test members refrozen on 11425; chronological val split fit [0:1080) / select [1080:2161); frozen 11425 test; disjoint-4 diagnostic only",
    }
    with open(HERE / "results_h2.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {HERE / 'results_h2.json'} elapsed {time.time() - t_all:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
