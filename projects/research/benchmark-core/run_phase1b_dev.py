"""Phase 1b dry run on Dev: Seasonal Naive / NLinear / DLinear.

Scope, fixed by PROTOCOL.md §14 (Faza 1b) and by the owner's instruction:

- Dev only. The task list is read from `results/manifest.json["dev_tasks"]` and
  nothing else; every entry is asserted to have a `dev_` id. No Lockbox task, no
  quarantine task, no `bench.py --fev-full`.
- The three locked origins per task are the manifest's own `window_indices`
  (rule [-3:] over the task's window budget). They are reproduced by rebuilding
  the task with `num_windows = len(window_indices)` and
  `initial_cutoff = cutoffs[window_indices[0]]`, then asserting the new cutoffs
  are identical to the manifest's ones.
- Per-origin fit: each origin is fitted only on the history that precedes it.
- MASE comes from fev 0.10.0 itself (`EvaluationWindow.compute_metrics` for
  per-origin values, `Task.evaluation_summary` for the task value), so every
  item of every target column is scored — never item 0 only.

Nothing here is simulated: no synthetic series, no random seeds, no fallbacks
that invent a number. A series whose history cannot support a fit is counted and
reported as `not_computable`.

Output: results/phase1b_dev_dryrun.json (written after every task, so an
interrupted run keeps its progress; --resume continues from it).

Usage:
    python run_phase1b_dev.py                 # full Dev dry run
    python run_phase1b_dev.py --resume        # continue an interrupted run
    python run_phase1b_dev.py --tasks dev_13_rossmann_1W --out x.json
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
MANIFEST = RESULTS / "manifest.json"
DEFAULT_OUT = RESULTS / "phase1b_dev_dryrun.json"

import fev  # noqa: E402
import fev.constants  # noqa: E402

fev.constants.DEFAULT_NUM_PROC = 1

import numpy as np  # noqa: E402
from datasets import Dataset, DatasetDict  # noqa: E402

from phase1b_baselines import (  # noqa: E402
    DEFAULT_ALPHA,
    DEFAULT_KERNEL,
    DEFAULT_LOOKBACK,
    InsufficientHistoryError,
    build_baselines,
    clean_history,
)

MODEL_NAMES = ["SeasonalNaive", "NLinear", "DLinear"]


def build_locked_task(entry: dict) -> "fev.Task":
    """Rebuild the task restricted to exactly the manifest's locked origins."""
    kwargs = dict(entry["task_kwargs"])
    full = fev.Task(**kwargs)
    full.load_full_dataset()
    cutoffs = full.cutoffs
    idxs = list(entry["window_indices"])
    if not idxs:
        raise ValueError(f"{entry['task_id']}: empty window_indices")
    locked = fev.Task(**{**kwargs, "num_windows": len(idxs),
                         "initial_cutoff": cutoffs[idxs[0]]})
    locked.load_full_dataset()
    expected = [cutoffs[i] for i in idxs]
    if locked.cutoffs != expected:
        raise AssertionError(
            f"{entry['task_id']}: rebuilt cutoffs {locked.cutoffs} != manifest cutoffs {expected}")
    return locked


def item_series(column) -> list[np.ndarray]:
    """One 1-D float array per item of a fev target column."""
    if isinstance(column, np.ndarray) and column.ndim <= 1:
        seq = [column]
    else:
        seq = list(column)
    out = []
    for v in seq:
        a = np.asarray(v, dtype=float)
        out.append(np.ravel(a) if a.ndim > 1 else a)
    return out


def make_predictions(window, per_target: dict[str, list[np.ndarray]]) -> DatasetDict:
    """fev prediction payload: one row per item, per target column."""
    future = window.get_ground_truth()
    out = DatasetDict()
    for target, per_item in per_target.items():
        rows = []
        for i in range(len(future)):
            rows.append({
                "id": future[i]["id"],
                "timestamp": np.asarray(future[i]["timestamp"]),
                "predictions": np.asarray(per_item[i], dtype=float).tolist(),
            })
        out[target] = Dataset.from_list(rows)
    return out


def run_task(entry: dict, lookback: int, alpha: float) -> dict:
    """Fit and score all three baselines on one Dev task, over its locked origins."""
    task = build_locked_task(entry)
    targets = list(task.target_columns)
    H = int(task.horizon)
    m = int(task.seasonality)

    record = {
        "task_id": entry["task_id"],
        "dataset_config": entry["dataset_config"],
        "family": entry["family"],
        "domain": entry["domain"],
        "horizon": H,
        "seasonality": m,
        "num_windows": len(entry["window_indices"]),
        "window_indices": entry["window_indices"],
        "n_targets": len(targets),
        "n_items": None,
        "models": {},
    }

    preds_per_model: dict[str, list] = {name: [] for name in MODEL_NAMES}
    per_window_metrics: dict[str, list] = {name: [] for name in MODEL_NAMES}
    fit_times: dict[str, list] = {name: [] for name in MODEL_NAMES}
    pred_times: dict[str, list] = {name: [] for name in MODEL_NAMES}
    not_computable: dict[str, int] = {name: 0 for name in MODEL_NAMES}
    lookbacks: dict[str, set] = {name: set() for name in MODEL_NAMES}
    n_items_seen = 0

    for w_pos, window in enumerate(task.iter_windows(num_proc=1)):
        past, _ = window.get_input_data()
        n_items_seen = max(n_items_seen, len(past))

        raw_preds: dict[str, DatasetDict] = {}
        for name in MODEL_NAMES:
            model = build_baselines(lookback=lookback, alpha=alpha)[name]
            per_target: dict[str, list[np.ndarray]] = {}
            for target in targets:
                if target not in past.column_names:
                    continue
                series_list = item_series(past[target])
                preds = []
                for series in series_list:
                    t0 = time.perf_counter()
                    try:
                        hist = clean_history(series)
                        y = model.fit_predict(hist, H, m)
                    except InsufficientHistoryError:
                        not_computable[name] += 1
                        t1 = time.perf_counter()
                        fit_times[name].append(t1 - t0)
                        y = None
                    else:
                        t1 = time.perf_counter()
                        fit_times[name].append(t1 - t0)
                        if getattr(model, "L_used", None) is not None:
                            lookbacks[name].add(int(model.L_used))
                    if y is None:
                        preds.append(np.full(H, np.nan))
                    else:
                        y = np.asarray(y, dtype=float).ravel()[:H]
                        if y.size < H:
                            y = np.concatenate([y, np.full(H - y.size, np.nan)])
                        preds.append(y)
                per_target[target] = preds
            t0 = time.perf_counter()
            payload = make_predictions(window, per_target)
            raw_preds[name] = payload
            pred_times[name].append(time.perf_counter() - t0)

            cleaned = task.clean_and_validate_predictions(payload)
            metrics = window.compute_metrics(
                cleaned, metrics=[fev.metrics.MASE()],
                seasonality=m, quantile_levels=[])
            per_window_metrics[name].append(float(metrics["MASE"]))

        for name in MODEL_NAMES:
            preds_per_model[name].append(raw_preds[name])

    record["n_items"] = n_items_seen

    for name in MODEL_NAMES:
        summary = task.evaluation_summary(preds_per_model[name], model_name=name)
        ft = np.asarray(fit_times[name], dtype=float)
        pt = np.asarray(pred_times[name], dtype=float)
        record["models"][name] = {
            "task_mase": float(summary["test_error"]),
            "per_window_mase": per_window_metrics[name],
            "not_computable_series": int(not_computable[name]),
            "lookbacks_used": sorted(lookbacks[name]),
            "fit_seconds": {
                "n_series_fits": int(ft.size),
                "total": float(ft.sum()),
                "list": [round(float(v), 6) for v in ft],
            },
            "predict_seconds": {
                "total": float(pt.sum()),
                "per_window": [round(float(v), 6) for v in pt],
            },
        }
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--tasks", nargs="*", default=None)
    ap.add_argument("--lookback", type=int, default=DEFAULT_LOOKBACK)
    ap.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    a = ap.parse_args()

    out_path = Path(a.out)
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = man["dev_tasks"]
    bad = [e["task_id"] for e in entries if not e["task_id"].startswith("dev_")]
    if bad:
        raise SystemExit(f"refusing to run: non-Dev task ids in dev_tasks: {bad}")
    if a.tasks:
        wanted = set(a.tasks)
        entries = [e for e in entries if e["task_id"] in wanted]
        missing = wanted - {e["task_id"] for e in entries}
        if missing:
            raise SystemExit(f"unknown task ids: {sorted(missing)}")

    done: dict[str, dict] = {}
    if a.resume and out_path.exists():
        prev = json.loads(out_path.read_text(encoding="utf-8"))
        done = {t["task_id"]: t for t in prev.get("tasks", [])}
        print(f"resume: {len(done)} tasks already in {out_path.name}", flush=True)

    artifact = {
        "protocol": "fev-v2-generalization",
        "phase": "1b",
        "layer": "dev",
        "manifest_sha256": man["manifest_sha256"],
        "model_spec": {
            "SeasonalNaive": {"definition": "y[T+h] = y[T+h-m], m = task seasonality"},
            "NLinear": {"definition": "instance-normalised single linear layer (Zeng et al. 2023, 4.2)",
                        "lookback": a.lookback, "estimator": "closed-form ridge", "alpha": a.alpha},
            "DLinear": {"definition": "moving-average decomposition + joint two-layer linear map (Zeng et al. 2023, 4.1)",
                        "lookback": a.lookback, "kernel_size": DEFAULT_KERNEL,
                        "estimator": "closed-form ridge, joint solve", "alpha": a.alpha},
            "metric": "fev.metrics.MASE via EvaluationWindow.compute_metrics / Task.evaluation_summary",
            "windows": "manifest window_indices (last 3 origins per task)",
            "fit_protocol": "per-origin, history strictly before the origin",
        },
        "tasks": [],
    }

    t_start = time.time()
    for i, entry in enumerate(entries, start=1):
        if entry["task_id"] in done:
            artifact["tasks"].append(done[entry["task_id"]])
            continue
        t0 = time.time()
        try:
            rec = run_task(entry, a.lookback, a.alpha)
        except Exception as err:  # a load failure is data, not a crash
            rec = {
                "task_id": entry["task_id"],
                "dataset_config": entry["dataset_config"],
                "error": f"{type(err).__name__}: {err}",
            }
            print(f"[{i:2d}/{len(entries)}] {entry['task_id']:32s} ERROR {rec['error']}", flush=True)
        else:
            print(f"[{i:2d}/{len(entries)}] {entry['task_id']:32s} "
                  f"items={rec['n_items']:5d} "
                  + " ".join(f"{n}={rec['models'][n]['task_mase']:.4f}" for n in MODEL_NAMES)
                  + f"  ({time.time() - t0:6.1f}s)", flush=True)
        artifact["tasks"].append(rec)
        artifact["elapsed_seconds"] = round(time.time() - t_start, 1)
        out_path.write_text(json.dumps(artifact, indent=1), encoding="utf-8")

    print(f"\nwrote {out_path} ({len(artifact['tasks'])} tasks, {time.time() - t_start:.1f}s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
