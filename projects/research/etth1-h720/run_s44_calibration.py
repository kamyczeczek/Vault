"""S44 blend calibration on the S49 protocol — a pure measurement.

This script does NOT resume S49, does NOT tune, and does NOT promote anything.
It answers one question with one number: what would the S44 blend

    NLinear L336 a=1 + NLinear L336 a=10 + PatchTST-Delta P24 D32 2L
    per-horizon ridge, no intercept, alpha=30000

score under the S49 protocol (12 locked origins, step 720 h, 8640..16560), so
that the ADR 0001 threshold-comparability caveat becomes a number.

Everything below is pre-registered in GATES-s44-calibration.md; the protocol
constants are asserted against that file at run time so a silent drift cannot
happen between registration and execution.

Code provenance (where the S44 object comes from — nothing is re-implemented):

* ``NLinear`` is imported VERBATIM from
  ``projects/_archive/ts-ml-experiments/h720/methods/neural_models.py``
  (class ``NLinear``, ``input_length=336``, ``ridge_alpha`` 1.0 / 10.0).
* ``PatchTSTModel`` / ``PatchTSTDelta`` are imported VERBATIM from
  ``projects/_archive/ts-ml-experiments/h720/sub_experiments/patchtst_delta_bet3/patchtst_encoder.py``
  (P=24, D=32, n_layers=2, H=720).
* ``fit_stack_map`` (per-horizon ridge, no intercept) is a transcription of
  ``.../blend_promotion_s44/rolling_arm.py::fit_stack_map``.
* The S49 protocol (origins, 360-day fit window, full-history context, raw MAE)
  and the two references (``BigDictELM(input_length=96, seed=42)``, DLinear) are
  taken from ``run_amr_h720_final.py`` / ``run_h2k_h720_final.py``.

Seed discipline: S44's PatchTST member runs on seed 0 (``_set_deterministic``
inside ``fit``). S49's stochastic-method seed set is {42,43,44,45,46}, so this
calibration re-seeds that single call site — the same one-change mirror the S45
seed-1 twin used, done by patching the module global rather than by copying the
100-line ``fit`` body. NLinear is closed-form and deterministic; BigDictELM and
DLinear run once, exactly as in S49's locked run.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
SIBLINGS = Path(os.environ.get("WORKSPACE_ROOT", str(ROOT.parent)))
BENCHMARK_CORE = SIBLINGS / "benchmark-core"
ARCHIVE = SIBLINGS.parent / "_archive"

# S49's data file (the protocol under calibration).
S49_CSV = ARCHIVE / "datasets" / "data" / "ETTh1_h1.csv"
# S44's own data file (used only by the reproduction control).
S44_CSV = ARCHIVE / "ts-ml-experiments" / "h720" / "ETTh1.csv"
S44_H720 = ARCHIVE / "ts-ml-experiments" / "h720"
S44_BET3 = S44_H720 / "sub_experiments" / "patchtst_delta_bet3"

for _p in (ROOT, BENCHMARK_CORE, S44_BET3, S44_H720):
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from methods.neural_models import NLinear  # noqa: E402  (S44 code, verbatim)
import patchtst_encoder as _pte  # noqa: E402  (S44 code, verbatim)
from patchtst_encoder import PatchTSTModel  # noqa: E402
from members.big_dict_elm import BigDictELM  # noqa: E402  (S49 reference)
from members.sota_baselines import fit_dlinear, pred_dlinear  # noqa: E402  (S49 reference)

# ----------------------------------------------------------------------
# Pre-registered constants (GATES-s44-calibration.md). Hard-asserted below.
# ----------------------------------------------------------------------
H = 720
CAP = 8640
ORIGINS = [CAP + k * H for k in range(12)]           # 8640 .. 16560, step 720
SEEDS = [42, 43, 44, 45, 46]                          # S49's stochastic seed set
BLEND_ALPHA = 30000.0                                 # S44 frozen alpha
S44_REPORTED_FULL_MAE = 1.9781264265828236            # context only, never a gate
REPRODUCTION_TOL = 0.01                               # 1% — pre-registered
REFERENCE_BIGDICT = 2.4777                            # pre-registered comparison point

BLEND_MEMBERS = ["nlinear_L336_a1", "nlinear_L336_a10", "patchtst_P24_D32_2L"]
S44_N_ORIGINS = 2161
S44_TRAIN_END = 8545
S44_FIT_ROWS = 11425
S44_CONCAT_ROWS = 14305


def _assert_preregistration() -> None:
    """Fail loud if this file drifts from the ledger written before any run."""
    gates = ROOT / "GATES-s44-calibration.md"
    text = gates.read_text(encoding="utf-8")
    for token in ("8640, 9360, 10080, 10800, 11520, 12240, 12960, 13680, 14400, 15120,",
                  "15840, 16560", "42, 43, 44, 45, 46", "alpha=30000",
                  "fit_intercept=False", "2.4777"):
        if token not in text:
            raise RuntimeError(f"pre-registration token missing from GATES file: {token!r}")
    assert ORIGINS == [8640 + 720 * k for k in range(12)]
    assert len(ORIGINS) == 12
    assert BLEND_ALPHA == 30000.0


# ----------------------------------------------------------------------
# Stack machinery — transcription of blend_promotion_s44/rolling_arm.py::fit_stack_map
# ----------------------------------------------------------------------
def fit_stack_map(P, A, alpha, fit_intercept=False):
    """Per-horizon ridge over the member predictions P (n, m, h)."""
    from sklearn.linear_model import Ridge

    n, m, h = P.shape
    coef = np.empty((m, h))
    inter = np.zeros(h)

    class _Map:
        def predict(self, Pq):
            out = np.einsum("qmh,mh->qh", Pq, coef)
            if fit_intercept:
                out = out + inter
            return out

    for hi in range(h):
        X = P[:, :, hi]
        y = A[:, hi]
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept)
        r.fit(X, y)
        coef[:, hi] = r.coef_
        if fit_intercept:
            inter[hi] = r.intercept_
    mobj = _Map()
    mobj.coef_ = coef
    mobj.inter_ = inter
    mobj.alpha = alpha
    return mobj


def rolling_metrics(preds, actuals):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err ** 2))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err ** 2))), mae_per, rmse_per


def _nlinear_factory(alpha):
    return lambda: NLinear(input_length=336, ridge_alpha=alpha)


def _patchtst_factory(seed=None):
    return lambda: PatchTSTModel(patch_size=24, D=32, n_layers=2, H=H)


def _seed_module(seed):
    """Re-seed the single seeded call site inside PatchTSTModel.fit.

    S45 precedent: a line-for-line mirror of ``_set_deterministic`` with exactly
    one change — the seed constant. Implemented by patching the module global so
    the 100-line ``fit`` body is never transcribed.
    """
    original = _pte._set_deterministic

    def _seeded():
        import torch
        torch.manual_seed(seed)
        np.random.seed(seed)
        torch.use_deterministic_algorithms(True, warn_only=True)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    return original, _seeded


def _fit_member(factory, train, seed=None):
    """Fit one member on ``train``; optionally re-seed PatchTST's fit."""
    m = factory()
    if seed is None:
        m.fit(train, horizon=H)
        return m
    original, seeded = _seed_module(seed)
    _pte._set_deterministic = seeded
    try:
        m.fit(train, horizon=H)
    finally:
        _pte._set_deterministic = original
    return m


def _predict_at(m, train, ends):
    """Predict at each end index e with ``history_ = train[:e]`` (S44 machinery)."""
    if isinstance(m, PatchTSTModel):
        import torch
        L = 336
        windows = np.stack([train[e - L:e] for e in ends])
        tokens = np.stack([m._make_tokens(w) for w in windows])
        xb = torch.tensor(tokens, dtype=torch.float32, device=m.device)
        m.net.eval()
        with torch.no_grad():
            deltas = m.net(xb).cpu().numpy()
        anchors = windows[:, -1, None]
        return deltas + anchors

    out = np.empty((len(ends), H), dtype=float)
    for i, e in enumerate(ends):
        m.history_ = train[:e]
        out[i] = np.asarray(m.predict(), dtype=float)[:H]
    return out


# ----------------------------------------------------------------------
# Stage 1 — reproduction control: re-run S44's frozen test verbatim
# ----------------------------------------------------------------------
def reproduce_s44(series, label, alpha=BLEND_ALPHA, seed=0):
    """Re-run the S44 frozen test: members on rows 0..11424, stack fitted on
    val[0:1080) at the selected alpha, scored on the 2161 step-1 test origins."""
    t0 = time.time()
    fit_series = series[:S44_FIT_ROWS]
    concat = series[:S44_CONCAT_ROWS]
    test = series[S44_FIT_ROWS:S44_CONCAT_ROWS]
    assert len(fit_series) == S44_FIT_ROWS and len(test) == 2880

    n_val = len(fit_series) - S44_TRAIN_END - H + 1
    val_starts = np.arange(n_val) + S44_TRAIN_END
    n_test = len(test) - H + 1
    test_starts = np.arange(n_test) + S44_FIT_ROWS
    assert n_val == S44_N_ORIGINS and n_test == S44_N_ORIGINS, (n_val, n_test)

    # ---- val phase: members FROZEN on 8545 (train_series), history from the
    # 11425-row fit series — exactly S44's preds_for_train_fit ----
    train_series = fit_series[:S44_TRAIN_END]
    p1v = _predict_at(_fit_member(_nlinear_factory(1.0), train_series), fit_series, val_starts)
    p10v = _predict_at(_fit_member(_nlinear_factory(10.0), train_series), fit_series, val_starts)
    ppv = _predict_at(_fit_member(_patchtst_factory(), train_series, seed=seed),
                      fit_series, val_starts)
    P_val = np.stack([p1v, p10v, ppv], axis=1)
    A_val = np.stack([fit_series[t:t + H] for t in val_starts])

    # ---- frozen test: same members, history from the concatenation ----
    m1 = _fit_member(_nlinear_factory(1.0), fit_series)
    m10 = _fit_member(_nlinear_factory(10.0), fit_series)
    mpt = _fit_member(_patchtst_factory(), fit_series, seed=seed)
    cols = []
    for m in (m1, m10, mpt):
        c = np.empty((n_test, H), dtype=float)
        for i, s in enumerate(test_starts):
            m.history_ = concat[:s]
            c[i] = np.asarray(m.predict(), dtype=float)[:H]
        cols.append(c)
    P_test = np.stack(cols, axis=1)
    A_test = np.stack([test[t - S44_FIT_ROWS:t - S44_FIT_ROWS + H] for t in test_starts])

    n2 = n_val // 2
    stack = fit_stack_map(P_val[:n2, :, :], A_val[:n2], alpha)
    blend = stack.predict(P_test)
    mae, rmse, _, _ = rolling_metrics(blend, A_test)

    singles = {}
    for j, name in enumerate(BLEND_MEMBERS):
        s_mae, _, _, _ = rolling_metrics(P_test[:, j, :], A_test)
        singles[name] = s_mae

    rel = abs(mae - S44_REPORTED_FULL_MAE) / S44_REPORTED_FULL_MAE
    return {
        "label": label,
        "data_file": str(S44_CSV if label == "s44_data_file" else S49_CSV),
        "patchtst_seed": seed,
        "n_val_origins": int(n_val), "n_test_origins": int(n_test),
        "stack_fit_origins": int(n2), "alpha": alpha,
        "test_full_mae": mae, "test_full_rmse": rmse,
        "s44_reported_mae": S44_REPORTED_FULL_MAE,
        "abs_diff": abs(mae - S44_REPORTED_FULL_MAE), "rel_diff": rel,
        "within_1pct": bool(rel <= REPRODUCTION_TOL),
        "singleton_test_mae": singles,
        "elapsed_s": round(time.time() - t0, 1),
    }


# ----------------------------------------------------------------------
# Stage 2 — calibration on the 12 locked S49 origins
# ----------------------------------------------------------------------
# Ridge-fit origin sets. Under the out-of-sample discipline the members used to
# build the ridge design matrix are frozen on the FIRST 5760 rows of the training
# slice, so a ridge-fit origin is admissible only if it starts at or after index
# 5760 — otherwise its member forecast is in-sample for those members (the exact
# defect this calibration must not reproduce).
#
# PRIMARY   = the 2161 origins of the 2880-row tail (5760..7920); fit on the
#             chronological first 1080. This is the exact structural mirror of S44:
#             members frozen at row 8545, val origins 8545..11425 (2161), ridge on
#             val[0:1080). Translated: frozen at 5760, OOS origins 5760..8640 (2161),
#             ridge on the first 1080.
# SENSITIVITY = the disjoint second half of the same 2161 out-of-sample origins.
#             Same member forecasts, no extra training, no overlap with PRIMARY.
_TAIL_ENDS = list(range(CAP - 2880, CAP - H + 1))               # 2161 origins (5760..7920)
_TAIL_FIT_ENDS = _TAIL_ENDS[:len(_TAIL_ENDS) // 2]              # 1080 — PRIMARY
_TAIL_FIT_ENDS_SENS = _TAIL_ENDS[len(_TAIL_ENDS) // 2:len(_TAIL_ENDS) - 1]  # 1080 — SENSITIVITY
_NEEDED_ENDS = sorted(set(_TAIL_ENDS) | {CAP})

RIDGE_TRAIN_CAP = CAP - 2880  # 5760 rows — members frozen here yield OOS ridge forecasts

_STATE: dict = {}


def _init_worker(series):
    import os
    import torch
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    torch.set_num_threads(1)
    _STATE["series"] = series


def _calibrate_one_origin(series, origin):
    """One origin: fit validation members on s[o-CAP:o-2880], fit ridge on OOS predictions,
    fit test members on s[o-CAP:o], apply ridge at origin o."""
    train = series[origin - CAP:origin]
    train_sub = train[:CAP - 2880]  # 5760 rows
    ctx = series[:origin]
    actual = series[origin:origin + H]
    assert len(train) == CAP and len(train_sub) == CAP - 2880 and len(ctx) == origin and len(actual) == H

    idx = {e: i for i, e in enumerate(_NEEDED_ENDS)}
    tail_idx = [idx[e] for e in _TAIL_FIT_ENDS]
    sens_idx = [idx[e] for e in _TAIL_FIT_ENDS_SENS]

    A_tail = np.stack([train[e:e + H] for e in _TAIL_FIT_ENDS])
    A_sens = np.stack([train[e:e + H] for e in _TAIL_FIT_ENDS_SENS])

    # 1. Validation members frozen on train_sub (5760 rows)
    m1_val = _fit_member(_nlinear_factory(1.0), train_sub)
    m10_val = _fit_member(_nlinear_factory(10.0), train_sub)
    P1_val = _predict_at(m1_val, train, _NEEDED_ENDS)
    P10_val = _predict_at(m10_val, train, _NEEDED_ENDS)

    # 2. Scored members refitted on full train (8640 rows)
    m1_full = _fit_member(_nlinear_factory(1.0), train)
    m10_full = _fit_member(_nlinear_factory(10.0), train)
    p1_o = m1_full.predict()[:H]
    p10_o = m10_full.predict()[:H]

    per_seed = {}
    for seed in SEEDS:
        # Val PatchTST member frozen on 5760 rows
        mpt_val = _fit_member(_patchtst_factory(), train_sub, seed=seed)
        Pp_val = _predict_at(mpt_val, train, _NEEDED_ENDS)
        P_val = np.concatenate([P1_val[:, None, :], P10_val[:, None, :], Pp_val[:, None, :]], axis=1)

        # Fit ridge on OOS member predictions (primary + disjoint sensitivity half)
        stack_tail = fit_stack_map(P_val[tail_idx], A_tail, BLEND_ALPHA)
        stack_sens = fit_stack_map(P_val[sens_idx], A_sens, BLEND_ALPHA)

        # Full PatchTST member refitted on 8640 rows
        mpt_full = _fit_member(_patchtst_factory(), train, seed=seed)
        pp_o = mpt_full.predict()[:H]
        P_o = np.stack([p1_o, p10_o, pp_o], axis=0)  # shape (3, H)

        blend_tail = stack_tail.predict(P_o[None, :])[0]
        mae_tail = float(np.mean(np.abs(blend_tail - actual)))

        blend_sens = stack_sens.predict(P_o[None, :])[0]
        mae_sens = float(np.mean(np.abs(blend_sens - actual)))

        per_seed[str(seed)] = {
            "blend_mae_raw": mae_tail,
            "blend_mae_raw_variant_sensitivity_secondhalf": mae_sens,
            "member_mae_raw": {
                "nlinear_L336_a1": float(np.mean(np.abs(p1_o - actual))),
                "nlinear_L336_a10": float(np.mean(np.abs(p10_o - actual))),
                "patchtst_P24_D32_2L": float(np.mean(np.abs(pp_o - actual))),
            },
        }
        del mpt_val, Pp_val, P_val, mpt_full, P_o
        import gc; gc.collect()

    refs = _references(series, origin)
    base = per_seed[str(SEEDS[0])]["member_mae_raw"]
    return {
        "origin": origin,
        "train_std": float(train.std()),
        "member_mae_raw_deterministic": {
            "nlinear_L336_a1": base["nlinear_L336_a1"],
            "nlinear_L336_a10": base["nlinear_L336_a10"],
        },
        "references": refs,
        "per_seed": per_seed,
    }


def _references(series, origin):
    """BigDictELM L96 (seed 42) and DLinear, exactly as S49's locked run scored them."""
    train = series[origin - CAP:origin]
    ctx = series[:origin]
    actual = series[origin:origin + H]
    out = {}
    bd = BigDictELM(input_length=96, seed=42).fit(train, horizon=H).predict_hist(ctx)
    out["bigdict_elm_L96"] = float(np.mean(np.abs(np.asarray(bd, dtype=float)[:H] - actual)))
    dl = pred_dlinear(fit_dlinear(train, H), ctx)
    out["dlinear"] = float(np.mean(np.abs(np.asarray(dl, dtype=float)[:H] - actual)))
    return out


def _origin_cell(job):
    origin = job
    series = _STATE["series"]
    try:
        row = _calibrate_one_origin(series, origin)
        return origin, row
    except Exception as exc:
        import traceback
        print(f"Error in origin {origin}:\n{traceback.format_exc()}", flush=True)
        raise exc


def run_calibration(series, workers):
    per_origin = []
    done = set()
    t0 = time.time()

    def _record(origin, row):
        per_origin.append(row)
        done.add(origin)
        print(f"  origin {origin} done "
              f"blend(seed42)={row['per_seed']['42']['blend_mae_raw']:.4f} "
              f"({time.time() - t0:.0f}s elapsed)", flush=True)

    try:
        with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker,
                                 initargs=(series,)) as pool:
            for origin, row in pool.map(_origin_cell, ORIGINS):
                _record(origin, row)
    except Exception as exc:
        print(f"  pool failed ({type(exc).__name__}: {exc}); "
              f"finishing {len(ORIGINS) - len(done)} origins in-process", flush=True)

    for origin in ORIGINS:
        if origin in done:
            continue
        _record(origin, _calibrate_one_origin(series, origin))

    per_origin.sort(key=lambda r: r["origin"])
    return per_origin, round(time.time() - t0, 1)


def _summarise(per_origin):
    dlinear = [r["references"]["dlinear"] for r in per_origin]
    bigdict = [r["references"]["bigdict_elm_L96"] for r in per_origin]
    summary = {}

    def block(vals, ref):
        return {
            "mae_raw_mean": float(np.mean(vals)), "mae_raw_std": float(np.std(vals)),
            "mae_raw_median": float(np.median(vals)),
            "wins_vs_dlinear": int(sum(1 for b, d in zip(vals, dlinear) if b < d)),
            "per_origin": [round(float(v), 6) for v in vals],
            "delta_vs_dlinear_mean": float(np.mean(vals) - np.mean(dlinear)),
            "delta_vs_bigdict_mean": float(np.mean(vals) - np.mean(bigdict)),
        }

    for seed in SEEDS:
        summary[f"blend_seed{seed}"] = block(
            [r["per_seed"][str(seed)]["blend_mae_raw"] for r in per_origin], dlinear)
    for name in ("nlinear_L336_a1", "nlinear_L336_a10", "patchtst_P24_D32_2L"):
        summary[name] = block(
            [r["per_seed"]["42"]["member_mae_raw"][name] for r in per_origin], dlinear)
    summary["bigdict_elm_L96"] = block(bigdict, dlinear)
    summary["dlinear"] = block(dlinear, dlinear)

    pt = np.array([[r["per_seed"][str(s)]["member_mae_raw"]["patchtst_P24_D32_2L"]
                    for s in SEEDS] for r in per_origin])
    summary["patchtst_P24_D32_2L_across_seeds"] = {
        "per_seed_mean": {str(s): float(pt[:, i].mean()) for i, s in enumerate(SEEDS)},
        "mae_raw_mean_of_seed_means": float(pt.mean(axis=0).mean()),
        "mae_raw_std_of_seed_means": float(pt.mean(axis=0).std()),
        "per_origin_spread_std": [round(float(v), 6) for v in pt.std(axis=1)],
    }
    blend = np.array([[r["per_seed"][str(s)]["blend_mae_raw"] for s in SEEDS]
                      for r in per_origin])
    summary["blend_across_seeds"] = {
        "per_seed_mean": {str(s): float(blend[:, i].mean()) for i, s in enumerate(SEEDS)},
        "mae_raw_mean_of_seed_means": float(blend.mean(axis=0).mean()),
        "mae_raw_std_of_seed_means": float(blend.mean(axis=0).std()),
        "per_origin_spread_std": [round(float(v), 6) for v in blend.std(axis=1)],
        "pooled_mae_raw_mean": float(blend.mean()),
    }
    var = np.array([[r["per_seed"][str(s)]["blend_mae_raw_variant_sensitivity_secondhalf"]
                     for s in SEEDS] for r in per_origin])
    summary["blend_variant_sensitivity_secondhalf"] = {
        "mae_raw_mean": float(var.mean()), "mae_raw_std": float(var.std()),
        "per_seed_mean": {str(s): float(var[:, i].mean()) for i, s in enumerate(SEEDS)},
    }
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", choices=["reproduction", "calibration", "all"],
                    default="all")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--skip-s49-repro", action="store_true",
                    help="reproduce only on S44's own data file")
    args = ap.parse_args(argv)

    _assert_preregistration()
    out_dir = ROOT / "results"
    out_dir.mkdir(exist_ok=True)

    if args.stage in ("reproduction", "all"):
        print("== stage 1: S44 frozen-test reproduction control ==", flush=True)
        repro = []
        for label, path in (("s44_data_file", S44_CSV), ("s49_data_file", S49_CSV)):
            if label == "s49_data_file" and args.skip_s49_repro:
                continue
            series = pd.read_csv(path)["OT"].to_numpy(float)
            r = reproduce_s44(series, label, seed=0)
            print(f"  {label}: full MAE {r['test_full_mae']:.6f} "
                  f"(reported {S44_REPORTED_FULL_MAE:.6f}, rel diff "
                  f"{r['rel_diff']:.2e}, within 1%: {r['within_1pct']})", flush=True)
            repro.append(r)
        payload = {
            "stage": "s44_reproduction_control",
            "tolerance": REPRODUCTION_TOL,
            "reported": S44_REPORTED_FULL_MAE,
            "runs": repro,
            "all_within_1pct": all(r["within_1pct"] for r in repro),
        }
        (out_dir / "s44_calibration_reproduction.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8")
        print(f"  wrote {out_dir / 's44_calibration_reproduction.json'}", flush=True)

    if args.stage in ("calibration", "all"):
        print("== stage 2: S44 blend on the 12 locked S49 origins ==", flush=True)
        series = pd.read_csv(S49_CSV)["OT"].to_numpy(float)
        t0 = time.time()
        per_origin, elapsed = run_calibration(series, args.workers)
        summary = _summarise(per_origin)
        payload = {
            "stage": "s44_blend_calibration_on_s49_protocol",
            "pre_registered_in": "GATES-s44-calibration.md",
            "protocol": {
                "H": H, "train_cap_hours": CAP, "mode": "sliding_fixed_360d",
                "origins": ORIGINS, "n_origins": len(ORIGINS),
                "fit": "fit on s[o-CAP:o] only", "context": "full s[:o]",
                "metric": "raw MAE over the 720-step horizon",
                "blend_alpha": BLEND_ALPHA, "blend_intercept": False,
                "members": BLEND_MEMBERS, "seeds": SEEDS,
                "ridge_fit_rule_primary": (
                    "per-horizon ridge no-intercept alpha=30000 fitted on the "
                    "chronological first 1080 of the 2161 out-of-sample origins in "
                    "the 2880-row tail of s[o-8640:o] (origins 5760..7920; members "
                    "frozen at 5760) — a structurally identical translation of "
                    "S44's val[0:1080)"),
                "ridge_fit_rule_sensitivity": (
                    "same stack fitted on the disjoint second half of the same 2161 "
                    "out-of-sample origins (1080..2160)"),
                "ridge_member_freeze_point": RIDGE_TRAIN_CAP,
                "s44_ridge_fit_discovery": (
                    "S44 fitted ridge weights on strictly out-of-sample member forecasts: "
                    "validation members were frozen on train rows 0..8545 via preds_for_train_fit, "
                    "their predictions over val origins 8545..11425 were used to fit the ridge "
                    "stack (val[0:1080)), and members were refitted on 0..11425 via preds_for_full_fit "
                    "only to generate scored forecasts over test origins 11425..14305. "
                    "This calibration mirrors that exact out-of-sample stacking discipline: "
                    "for each origin o, validation members are frozen on s[o-8640:o-2880] (5760 rows) "
                    "to generate out-of-sample forecasts over the tail window to fit the ridge stack, "
                    "while scored predictions at origin o come from members refitted on the full "
                    "s[o-8640:o] (8640 rows)."),
            },
            "data": {"file": str(S49_CSV), "n": int(len(series))},
            "per_origin": per_origin,
            "summary": summary,
            "context_only": {"s44_reported_full_mae": S44_REPORTED_FULL_MAE,
                             "reference_bigdict_L96": REFERENCE_BIGDICT},
            "elapsed_s": elapsed,
            "wall_total_s": round(time.time() - t0, 1),
        }
        (out_dir / "s44_calibration.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8")
        print(f"  wrote {out_dir / 's44_calibration.json'}", flush=True)
        print(f"  blend mean (seed 42) = "
              f"{summary['blend_seed42']['mae_raw_mean']:.4f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
