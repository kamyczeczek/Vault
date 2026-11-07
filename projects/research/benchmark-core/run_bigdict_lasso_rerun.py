#!/usr/bin/env python3
"""Re-run the BigDict-LASSO experiment with the rewritten member.

Why this exists
---------------
`members/big_dict_lasso.py` was rewritten (fixed-length anchored windows with an
asserted feature schema, train-window-only feature and target scaling, a shared
multi-task LASSO fit) but **no runner imports it**. The two summary documents
that still report numbers for it —

* `results_bigdict_lasso_final.md`
* `results_ultimate_summary.md` Part 2

— are stale: they carry the *old* run's numbers (thomas_H24 0.7961), produced
before the rewrite, on data where the pywt even-length bug silently dropped
365 of 665 windows (55%). `CONTEXT.md` §Open work names this gap and
`REFLECTION_PROMISING_METHODS.md` §5 records "the LASSO result is on
inconsistent data and must be regenerated".

This script regenerates them under the protocol this project already declares
in `CONTEXT.md` §Evaluation protocol and implements in `bench.rolling_preds`
(`bench.py:320`):

* W = 5 rolling origins, stride H, starting at the fit cutoff 2000;
* the fit is frozen once, on `series[:2000]` only, and never repeated per
  origin — so nothing from any origin's prediction window reaches the fit;
* a 96-step causal context per origin, horizons scored independently;
* MAE is the metric the stale documents report, so the new numbers are
  directly comparable to them.

Arms
----
* `bigdict_elm_default` — `members.big_dict_elm.BigDictELM(input_length=96,
  seed=42)`, the harness's stock BigDict-Ridge arm (`bench.fit_bigdict`,
  `bench.py:253`). NOT the "BigDict-Ridge (Opt)" of the stale documents: that
  arm was an optimized configuration whose recipe is not recorded, so the new
  comparison is named for what it actually is.
* `lasso_<profile>` — `members.big_dict_lasso.BigDictLASSO(profile=...)`.
* `--alphas` sweeps the LASSO regularization on top of the profiles.

Output: `results/bigdict_lasso_rerun.json` (written after every task, so an
interrupted run keeps its progress) plus a printed table. Nothing here touches
`results_s47.json` / `harness.log`, the committed evidence `CLAUDE.md` §Rules
protects.

Usage
-----
    python run_bigdict_lasso_rerun.py --smoke      # 1 task, 1 arm, timing probe
    python run_bigdict_lasso_rerun.py              # the 3 documented tasks
    python run_bigdict_lasso_rerun.py --tasks thomas_H24 --alphas 0.01
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from bench import get_series  # noqa: E402  (task generators + data loaders)

DEFAULT_OUT = HERE / "results" / "bigdict_lasso_rerun.json"

# The three tasks the stale documents report numbers for. Order matches them.
DOCUMENTED_TASKS = ["thomas_H24", "seasonal_H48", "multiscale_H96"]


def task_horizons() -> dict:
    """Task -> horizon, read from bench.TASKS rather than hard-coded."""
    # Imported lazily so --help works without the numpy stack fully warm.
    from bench import TASKS
    return {name: H for name, H, _ in TASKS}


def series_for(name: str) -> np.ndarray:
    return np.asarray(get_series(name), dtype=float).ravel()


def rolling_origins(n: int, H: int, cutoff: int, width: int = 5) -> list:
    """Same origin rule as `bench.rolling_preds` (bench.py:323)."""
    return [cutoff + i * H for i in range(width) if cutoff + i * H + H <= n]


def score(preds: np.ndarray, actual: np.ndarray) -> dict:
    """Point MAE plus the per-origin and per-horizon decompositions."""
    err = np.abs(preds - actual)                       # (W, H)
    finite = np.isfinite(err)
    per_origin = [float(np.nanmean(err[w])) if np.isfinite(err[w]).any() else float("nan")
                  for w in range(err.shape[0])]
    per_horizon = [float(np.nanmean(err[:, h])) if np.isfinite(err[:, h]).any() else float("nan")
                   for h in range(err.shape[1])]
    return {
        "mae": float(np.nanmean(err)) if finite.any() else float("nan"),
        "per_origin_mae": per_origin,
        "per_horizon_mae": per_horizon,
    }


def run_arm(train: np.ndarray, series: np.ndarray, H: int, arm: dict) -> dict:
    """Fit one arm once on `train`, then score it at every rolling origin."""
    cutoff = len(train)
    origins = rolling_origins(len(series), H, cutoff)
    fitter, predictor = arm["build"]()
    t_fit = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model = fitter(train, H)
    fit_seconds = time.perf_counter() - t_fit
    fit_warnings = [f"{w.category.__name__}: {w.message}" for w in caught]

    preds, actual = [], []
    for o in origins:
        hist = series[max(0, o - 96):o]
        p = np.asarray(predictor(model, hist), dtype=float).ravel()[:H]
        if p.size < H:
            p = np.concatenate([p, np.full(H - p.size, np.nan)])
        if arm.get("delta"):
            # members/big_dict_lasso.py is a delta forecaster: fit()'s target is
            # `values[e:e+H] - values[e-1]` (members/big_dict_lasso.py:245) and
            # predict_hist returns that delta without re-adding the anchor
            # (members/big_dict_lasso.py:297). Undo the differencing here.
            p = p + float(hist[-1])
        preds.append(p)
        actual.append(series[o:o + H])
    P = np.stack(preds, axis=0)
    A = np.stack(actual, axis=0)

    out = score(P, A)
    out.update({
        "arm": arm["name"],
        "fit_seconds": round(fit_seconds, 4),
        "origins": origins,
        "cutoff": cutoff,
    })
    n_iter = getattr(getattr(model, "model_", None), "n_iter_", None)
    if n_iter is not None:
        # Recorded because the old experiment's own recommendation #2 was
        # "increase max_iter" — an unconverged coordinate-descent fit makes the
        # reported MAE a solution at the iteration budget, not the optimum.
        out["lasso_iterations"] = [int(v) for v in np.ravel(np.asarray(n_iter))]
        out["max_iter"] = int(getattr(model, "max_iter", 0) or 0)
        out["converged"] = not any("ConvergenceWarning" in w for w in fit_warnings)
    if fit_warnings:
        out["fit_warnings"] = fit_warnings[:3]
    if getattr(model, "feature_mask_", None) is not None:
        # feature_mask_ is (H, width): count distinct features the LASSO used,
        # not the number of non-zero coefficient entries.
        out["selected_features"] = int(np.count_nonzero(model.feature_mask_.any(axis=0)))
        out["nonzero_coefficients"] = int(np.count_nonzero(model.feature_mask_))
        out["feature_width"] = int(getattr(model, "base_width_", 0) or 0)
    return out


def build_arms(profiles, alphas):
    from members.big_dict_elm import BigDictELM
    from members.big_dict_lasso import BigDictLASSO

    arms = [{
        "name": "bigdict_elm_default",
        "spec": {"member": "members/big_dict_elm.py", "input_length": 96, "seed": 42},
        "build": lambda: (
            lambda train, H: BigDictELM(input_length=96, seed=42).fit(train, horizon=H),
            lambda model, hist: model.predict_hist(hist),
        ),
    }]
    for profile in profiles:
        for alpha in alphas:
            name = f"lasso_{profile}_a{alpha:g}"
            arms.append({
                "name": name,
                "delta": True,
                "spec": {
                    "member": "members/big_dict_lasso.py",
                    "profile": profile,
                    "alpha": alpha,
                    "lookback": 96,
                    "max_iter": 10000,
                    "random_state": 42,
                    "use_expansion": False,
                    "output": "delta from the last context value; the runner re-adds the anchor",
                },
                "build": lambda p=profile, a=alpha: (
                    lambda train, H, _p=p, _a=a: BigDictLASSO(
                        input_length=96, alpha=_a, profile=_p).fit(train, horizon=H),
                    lambda model, hist: model.predict_hist(hist),
                ),
            })
    return arms


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tasks", nargs="*", default=None,
                    help="task names; default = the 3 the stale documents report")
    ap.add_argument("--all-tasks", action="store_true",
                    help="run every task bench.py declares")
    ap.add_argument("--profiles", nargs="*", default=["approx"],
                    help="BigDict-LASSO filter-bank profiles (compact/approx/full)")
    ap.add_argument("--alphas", nargs="*", type=float, default=[0.01],
                    help="BigDict-LASSO alpha (regularization) values")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--smoke", action="store_true",
                    help="one task, one arm: measure wall time before committing")
    a = ap.parse_args()

    horizons = task_horizons()
    if a.smoke:
        tasks = ["thomas_H24"]
        profiles, alphas = ["approx"], [a.alphas[0]]
        arms = build_arms(profiles, alphas)
    else:
        if a.all_tasks:
            tasks = [t for t in ALL_TASKS if t in horizons]
        else:
            tasks = [t for t in (a.tasks or DOCUMENTED_TASKS) if t in horizons]
        arms = build_arms(a.profiles, a.alphas)
    unknown = [t for t in (a.tasks or []) if t not in horizons]
    if unknown:
        raise SystemExit(f"unknown tasks: {unknown}; known: {sorted(horizons)}")

    print(f"arms: {[x['name'] for x in arms]}")
    print(f"tasks: {tasks}")

    artifact = {
        "experiment": "bigdict_lasso_rerun",
        "purpose": "regenerate the BigDict-LASSO numbers that results_bigdict_lasso_final.md "
                   "and results_ultimate_summary.md Part 2 still report from the pre-rewrite run",
        "protocol": {
            "origins": "W=5 rolling origins, stride H, fit frozen on series[:2000] "
                       "(identical rule to bench.rolling_preds, bench.py:320-330)",
            "context": "96-step causal context per origin",
            "metric": "MAE, point estimate (the stale documents' metric)",
            "scaling": "fit-time only; no statistic from an origin's window reaches the fit",
        },
        "arms": [{ "name": x["name"], "spec": x["spec"]} for x in arms],
        "tasks": [],
    }

    t_start = time.time()
    out_path = Path(a.out)
    for name in tasks:
        H = horizons[name]
        series = series_for(name)
        record = {
            "task_id": name,
            "horizon": H,
            "n_points": int(series.size),
            "arms": [],
        }
        for arm in arms:
            t0 = time.time()
            try:
                rec = run_arm(series[:2000], series, H, arm)
            except Exception as err:
                rec = {"arm": arm["name"], "error": f"{type(err).__name__}: {err}"}
            rec["wall_seconds"] = round(time.time() - t0, 2)
            record["arms"].append(rec)
            status = rec.get("mae", rec.get("error"))
            extra = (f" feats={rec.get('selected_features')}/{rec.get('feature_width')}"
                     f" conv={rec.get('converged')}" if "selected_features" in rec else "")
            print(f"{name:16s} {arm['name']:34s} mae={status!r:>22} fit={rec['fit_seconds'] if 'fit_seconds' in rec else '-'}s{extra}",
                  flush=True)
        artifact["tasks"].append(record)
        artifact["elapsed_seconds"] = round(time.time() - t_start, 1)
        out_path.write_text(json.dumps(artifact, indent=1), encoding="utf-8")
        if a.smoke:
            break

    print(f"\nwrote {out_path} ({time.time() - t_start:.1f}s)")
    if a.smoke:
        worst = max(r.get("fit_seconds", 0) for r in artifact["tasks"][0]["arms"])
        print(f"SMOKE: slowest single fit = {worst:.3f}s → "
              f"full grid ≈ {worst * len(arms) * len(tasks):.0f}s over {len(arms)} arms x {len(tasks)} tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
