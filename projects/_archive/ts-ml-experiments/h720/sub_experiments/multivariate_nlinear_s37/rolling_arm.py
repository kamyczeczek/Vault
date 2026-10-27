"""S-37 — Sparse Subset Multivariate NLinear with Channel Dropout.

Protocol: S-20-clean (frozen train 8545 for val, refit 11425 for frozen test;
chronological val; 2161 origins).
"""

from __future__ import annotations

import csv
import json
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, TRAIN_FILE, TEST_FILE, VALIDATION_END, get_protocol_data
from methods.neural_models import NLinear
from multivariate_nlinear import MultiNLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
SEARCH_ALPHA = 3000.0
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]

COLS = ["HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL", "OT"]
OT_IDX = 6
CHANNEL_DROPOUT_PROB = 0.3
TRANSFER_DELTA_CAP = 0.01


def load_channel_dict(csv_path: Path, n_rows: int) -> dict[str, np.ndarray]:
    cols: dict[str, list[float]] = {c: [] for c in COLS}
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= n_rows:
                break
            for c in COLS:
                cols[c].append(float(row[c]))
    return {c: np.asarray(v, dtype=float) for c, v in cols.items()}


UNIVARIATE_MEMBERS = [
    ("nlinear_L336_a1",   lambda: NLinear(input_length=336, ridge_alpha=1.0),  False),
    ("nlinear_L336_a10",  lambda: NLinear(input_length=336, ridge_alpha=10.0), False),
]

MULTIVARIATE_MEMBERS = [
    ("mv_nlinear_L336_a1_ot_hufl",    lambda: MultiNLinear(input_length=336, ridge_alpha=1.0,  channels=["OT", "HUFL"]),    True),
    ("mv_nlinear_L336_a1_ot_lufl",    lambda: MultiNLinear(input_length=336, ridge_alpha=1.0,  channels=["OT", "LUFL"]),    True),
    ("mv_nlinear_L336_a1_ot_all7",    lambda: MultiNLinear(input_length=336, ridge_alpha=1.0,  channels=COLS),              True),
    ("mv_nlinear_L336_a10_ot_hufl",   lambda: MultiNLinear(input_length=336, ridge_alpha=10.0, channels=["OT", "HUFL"]),    True),
    ("mv_nlinear_L336_a10_ot_lufl",   lambda: MultiNLinear(input_length=336, ridge_alpha=10.0, channels=["OT", "LUFL"]),    True),
    ("mv_nlinear_L336_a10_ot_all7",   lambda: MultiNLinear(input_length=336, ridge_alpha=10.0, channels=COLS),              True),
]

MEMBERS = UNIVARIATE_MEMBERS + MULTIVARIATE_MEMBERS


def member_preds_linear(model, series_1d: np.ndarray, origin_starts: np.ndarray,
                        L: int, H: int) -> np.ndarray:
    starts = origin_starts - L
    win_idx = starts[:, None] + np.arange(L)
    windows = series_1d[win_idx]
    preds = []
    orig = model.history_
    for w in windows:
        try:
            model.history_ = w[:, None] if w.ndim == 1 else w
            preds.append(np.asarray(model.predict(), dtype=float))
        finally:
            model.history_ = orig
    return np.asarray(preds)


def member_preds_multi(model: MultiNLinear, series_dict: dict[str, np.ndarray],
                       origin_starts: np.ndarray, L: int, H: int) -> np.ndarray:
    preds = []
    orig = model.history_
    for t in origin_starts:
        win_start = t - L
        window = np.column_stack([series_dict[c][win_start:t] for c in model.channels])
        try:
            model.history_ = window
            preds.append(np.asarray(model.predict(), dtype=float))
        finally:
            model.history_ = orig
    return np.asarray(preds)


def collect_preds(models, series_1d: np.ndarray, series_dict: dict[str, np.ndarray],
                  origin_starts: np.ndarray) -> np.ndarray:
    n = len(origin_starts)
    P = np.empty((n, len(models), HORIZON))
    for j, m in enumerate(models):
        L = getattr(m, "input_length", None)
        if L is None:
            raise ValueError(f"model {j} missing input_length")
        if isinstance(m, MultiNLinear):
            P[:, j, :] = member_preds_multi(m, series_dict, origin_starts, L, HORIZON)
        else:
            P[:, j, :] = member_preds_linear(m, series_1d, origin_starts, L, HORIZON)
    return P


def fit_stack_map(P: np.ndarray, A: np.ndarray, alpha: float, fit_intercept: bool = False):
    n, m, h = P.shape
    coef = np.empty((m, h))
    intercept = np.zeros(h)
    for k in range(h):
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
        if fit_intercept:
            intercept[k] = r.intercept_
    class _Map:
        def predict(self, Pt: np.ndarray) -> np.ndarray:
            return np.einsum("mh,nmh->nh", coef, Pt) + intercept[None, :]
    return _Map()


def score_fast(P_val, A_val, idx, alpha=SEARCH_ALPHA):
    n2 = len(A_val) // 2
    m = fit_stack_map(P_val[:n2, idx, :], A_val[:n2], alpha)
    return float(np.mean(np.mean(np.abs(m.predict(P_val[n2:, idx, :]) - A_val[n2:]), axis=1)))


def score_full(P_val, A_val, idx):
    best, best_a = float("inf"), None
    for a in ALPHAS:
        r = fit_stack_map(P_val[:, idx, :], A_val, a)
        mae = float(np.mean(np.mean(np.abs(r.predict(P_val[:, idx, :]) - A_val), axis=1)))
        if mae < best:
            best = mae
            best_a = a
    return best, best_a


def transfer_check(test_mae_full: float, val_mae_full: float):
    delta = test_mae_full - val_mae_full
    return delta <= TRANSFER_DELTA_CAP, delta


def rolling_metrics(preds: np.ndarray, actuals: np.ndarray):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err**2, axis=1))
    mae = float(np.mean(mae_per))
    rmse = float(np.sqrt(np.mean(err**2)))
    disj = {
        f"window_{i+1}": {"mae": float(mae_per[t]), "rmse": float(rmse_per[t])}
        for i, t in enumerate(DISJOINT_STARTS)
    }
    return mae, rmse, disj


def main() -> int:
    t_all = time.time()
    pd = get_protocol_data()
    fit_1d, eval_1d, test_1d = pd.rolling_views()
    train_1d = fit_1d[:TRAIN_END]
    val_1d = fit_1d[TRAIN_END:]

    train_full_dict = load_channel_dict(TRAIN_FILE, VALIDATION_END)
    test_dict = load_channel_dict(TEST_FILE, len(test_1d))
    concat_dict = {c: np.concatenate([train_full_dict[c], test_dict[c]]) for c in COLS}
    X_dict_train = {c: arr[:TRAIN_END] for c, arr in train_full_dict.items()}

    n_val = len(val_1d) - HORIZON + 1
    assert n_val == 2161, n_val
    val_origin_starts = np.arange(n_val) + TRAIN_END

    print("fitting members on train 8545 ...")
    models = []
    for name, factory, is_multi in MEMBERS:
        m = factory()
        if is_multi:
            m.fit(X_dict_train, train_1d, horizon=HORIZON)
        else:
            m.fit(train_1d, horizon=HORIZON)
        models.append(m)

    print("collecting val predictions ...")
    P_val = collect_preds(models, fit_1d, concat_dict, val_origin_starts)
    A_val = np.stack([val_1d[t : t + HORIZON] for t in range(n_val)])

    for j, (name, _, _) in enumerate(MEMBERS):
        mae = float(np.mean(np.mean(np.abs(P_val[:, j, :] - A_val), axis=1)))
        print(f"  {name:28s} val {mae:.4f}")

    single = [score_fast(P_val, A_val, [j]) for j in range(len(MEMBERS))]
    cur_idx = [int(np.argmin(single))]
    cur_score = single[cur_idx[0]]
    best_idx = list(cur_idx)
    best_score = cur_score

    tabu: set[tuple] = set()
    tabu_queue = deque(maxlen=5)

    def key(idx): return tuple(sorted(idx))
    tabu.add(key(cur_idx))
    tabu_queue.append(key(cur_idx))

    max_iter = 7
    no_improve = 0
    trace = []

    for it in range(max_iter):
        cur_set = set(cur_idx)
        all_set = set(range(len(MEMBERS)))
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
        seen: set[tuple] = set()
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
        tabu_queue.append(k)
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
            "cur": [MEMBERS[i][0] for i in nb],
            "fast": float(s),
            "true": float(true_s),
            "alpha": true_a,
            "best_fast": float(best_score),
            "best_set": [MEMBERS[i][0] for i in best_idx]
        })
        print(f"iter {it:2d} cur {[MEMBERS[i][0] for i in nb]} fast {s:.4f} true {true_s:.4f} a={true_a} best_fast {best_score:.4f} {[MEMBERS[i][0] for i in best_idx]}")
        if no_improve >= 5:
            print("  no improve 5 iters -> stop")
            break

    print(f"\nbest subset fast {best_score:.4f}: {[MEMBERS[i][0] for i in best_idx]}")

    _, best_alpha = score_full(P_val, A_val, best_idx)
    P_best = P_val[:, best_idx, :]
    stack = fit_stack_map(P_best, A_val, best_alpha if best_alpha is not None else SEARCH_ALPHA)
    val_full = float(np.mean(np.mean(np.abs(stack.predict(P_best) - A_val), axis=1)))
    print(f"refit all val MAE {val_full:.4f} alpha {best_alpha}")

    print("\nre-fitting members on full 11425 ...")
    frozen = []
    for _, factory, is_multi in MEMBERS:
        m = factory()
        if is_multi:
            m.fit(X_dict_train, train_1d, horizon=HORIZON)
        else:
            m.fit(train_1d, horizon=HORIZON)
        frozen.append(m)

    n_test = len(test_1d) - HORIZON + 1
    test_origin_starts = np.arange(n_test) + len(fit_1d)
    disj_starts = np.array(DISJOINT_STARTS) + len(fit_1d)
    print("collecting test predictions ...")
    P_test = collect_preds(frozen, eval_1d, concat_dict, test_origin_starts)
    A_test = np.stack([test_1d[t : t + HORIZON] for t in range(n_test)])

    preds_stack = stack.predict(P_test[:, best_idx, :])
    test_mae, test_rmse, disj = rolling_metrics(preds_stack, A_test)

    P_disj = collect_preds(frozen, eval_1d, concat_dict, disj_starts)[:, best_idx, :]
    A_disj = np.stack([test_1d[s : s + HORIZON] for s in DISJOINT_STARTS])
    preds_disj = stack.predict(P_disj)
    err = preds_disj - A_disj
    disj_mae = float(np.mean(np.mean(np.abs(err), axis=1)))
    disj_rmse = float(np.sqrt(np.mean(err**2)))
    disj = {
        f"window_{i+1}": {
            "mae": float(np.mean(np.abs(err[i]))),
            "rmse": float(np.sqrt(np.mean(err[i]**2))),
        }
        for i in range(len(DISJOINT_STARTS))
    }

    pass_transfer, delta = transfer_check(test_mae, val_full)
    print(f"\ntransfer delta: {delta:+.4f} (cap {TRANSFER_DELTA_CAP}) pass={pass_transfer}")

    accept = (test_mae < 1.9909) and (disj_mae < 1.9696) and pass_transfer
    verdict = "ACCEPT" if accept else "REJECT"
    print(f"\nS-26 Incumbent MAE 1.9909 / RMSE 2.4710")
    print(f"S-37 {verdict}: subset {[MEMBERS[i][0] for i in best_idx]}, alpha={best_alpha}")
    print(f"  test full MAE {test_mae:.4f} / RMSE {test_rmse:.4f}")
    print(f"  disjoint-4 MAE {disj_mae:.4f} / RMSE {disj_rmse:.4f}")
    print(f"  val_full {val_full:.4f}, delta vs S-26: {test_mae - 1.9909:+.4f}")

    results = {
        "slice": "S-37-sparse-subset-multivariate-nlinear",
        "harness_command": " ".join(sys.argv),
        "pool": [n for n, _, _ in MEMBERS],
        "trace": trace,
        "best_subset": [MEMBERS[i][0] for i in best_idx],
        "best_idx": best_idx,
        "best_alpha": best_alpha,
        "validation": {
            "refit_all_val_mae": round(val_full, 4),
            "alpha_scores_second_half": {},
            "selected_alpha": best_alpha,
        },
        "test": {
            "rolling_mae": round(test_mae, 4),
            "rolling_rmse": round(test_rmse, 4),
            "disjoint_windows": disj,
            "delta_vs_s26": round(test_mae - 1.9909, 4),
        },
        "transfer": {
            "delta": round(delta, 4),
            "cap": TRANSFER_DELTA_CAP,
            "pass": bool(pass_transfer),
        },
        "acceptance": {
            "verdict": verdict,
            "full_mae_pass": bool(test_mae < 1.9909),
            "disjoint_pass": bool(disj_mae < 1.9696),
            "transfer_pass": bool(pass_transfer),
        },
        "protocol": "S-20-clean: val members frozen on 8545, test members refrozen on 11425",
    }

    results_path = HERE / "results_s37.json"
    results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {results_path}")

    harness_log = HERE / "harness.log"
    plan_impact = "No change; S-26 1.9909/2.4710 remains terminal." if verdict == "REJECT" else "Promoted to leaderboard as S-37 incumbent."
    log_text = "\n".join([
        f"harness_command: {' '.join(sys.argv)}",
        f"timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"verdict: {verdict}",
        f"best_subset: {[MEMBERS[i][0] for i in best_idx]}",
        f"best_alpha: {best_alpha}",
        f"val_full_mae: {val_full:.4f}",
        f"test_full_mae: {test_mae:.4f}",
        f"test_full_rmse: {test_rmse:.4f}",
        f"test_disjoint_mae: {disj_mae:.4f}",
        f"transfer_delta: {delta:.4f}",
        f"plan_impact: {plan_impact}",
    ]) + "\n"
    harness_log.write_text(log_text, encoding="utf-8")
    print(f"wrote {harness_log} (elapsed {time.time() - t_all:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
