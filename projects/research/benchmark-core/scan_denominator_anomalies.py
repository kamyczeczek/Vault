"""Phase 1b — scan the MASE denominator for zero seasonal error.

PROTOCOL.md §3: series whose in-sample seasonal error is zero (giving inf/nan
MASE) are identified once, in Phase 1b, from a Seasonal Naive evaluation and
frozen in the manifest. No model run in Phase 3 may be failed by a property of
the data's denominator.

The scan walks every Dev task over its locked last-3 windows and every target
column, computing fev's per-item in-sample seasonal error. Results are written
incrementally so an interrupted run keeps its progress.

Usage:
    python scan_denominator_anomalies.py                 # scan Dev
    python scan_denominator_anomalies.py --layer lockbox # scan Lockbox (audit)
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
MANIFEST = RESULTS / "manifest.json"
OUT = RESULTS / "denominator_anomaly_scan.json"

# fev's own DEFAULT_NUM_PROC spawns worker pools; on Windows a script without a
# __main__ guard deadlocks. Single-process keeps the scan deterministic too.
import fev  # noqa: E402
import fev.constants  # noqa: E402

fev.constants.DEFAULT_NUM_PROC = 1

import numpy as np  # noqa: E402


def seasonal_error_per_item(items: list[np.ndarray], m: int) -> list[float]:
    """fev's per-item in-sample seasonal error: mean |y[t] - y[t-m]|.

    Mirrors `fev.metrics._seasonal_error_per_item` exactly: an item whose
    history is not longer than `seasonality` contributes no diffs and therefore
    yields NaN (fev then excludes it from the MASE aggregate via `_safemean`),
    not 0.0. An item with all-NaN diffs also yields NaN. Only a genuine 0.0
    (perfectly periodic history) makes the MASE denominator vanish.
    """
    out = []
    for y in items:
        if len(y) <= m:
            out.append(float("nan"))
            continue
        diff = np.abs(y[m:] - y[:-m])
        valid = diff[~np.isnan(diff)]
        out.append(float(np.mean(valid)) if valid.size else float("nan"))
    return out


def as_item_arrays(values) -> list[np.ndarray]:
    """Unwrap a fev target column into a list of 1-D float arrays (one per item).

    `datasets.Dataset[col]` returns a `datasets.Column`, which is neither a
    list nor an ndarray. Handing it straight to `np.asarray` silently
    concatenates every item into one vector when the items share a length
    (rossmann: 1115 items x 798 -> one 885,570-long array) and raises on ragged
    columns. Iterating the Column yields one array per item, which is what
    fev's [N, D] seasonal error expects.
    """
    if isinstance(values, np.ndarray) and values.ndim <= 1:
        seq = [values]
    else:
        seq = list(values)
    arrs = []
    for v in seq:
        a = np.asarray(v, dtype=float)
        arrs.append(np.ravel(a) if a.ndim > 1 else a)
    return arrs


def scan_task(entry: dict) -> dict:
    kwargs = dict(entry["task_kwargs"])
    task = fev.Task(**kwargs)
    m = int(entry["seasonality"])
    targets = kwargs.get("target") or ["target"]
    if isinstance(targets, str):
        targets = [targets]

    record = {
        "task_id": entry["task_id"],
        "dataset_config": entry["dataset_config"],
        "family": entry["family"],
        "domain": entry["domain"],
        "seasonality": m,
        "windows": [],
        "targets": {},
    }

    for w_idx in entry["window_indices"]:
        window = task.get_window(w_idx)
        past, _ = window.get_input_data()
        w_rec = {"window_index": w_idx, "n_rows": len(past), "targets": {}}
        for col in targets:
            if col not in past.column_names:
                continue
            items = as_item_arrays(past[col])
            errs = seasonal_error_per_item(items, m)
            # A zero denominator makes MASE inf/nan and MUST be excluded before
            # any model runs; a NaN denominator is already excluded by fev's
            # own _safemean and is recorded only for transparency.
            zero_idx = [i for i, e in enumerate(errs) if not math.isnan(e) and e <= 0.0]
            nan_idx = [i for i, e in enumerate(errs) if math.isnan(e)]
            finite = [e for e in errs if not math.isnan(e)]
            w_rec["targets"][col] = {
                "n_items": len(items),
                "zero_error_items": len(zero_idx),
                "nan_error_items": len(nan_idx),
                "zero_item_indices": zero_idx[:50],
                "nan_item_indices": nan_idx[:50],
                "min_seasonal_error": (min(finite) if finite else None),
                "max_seasonal_error": (max(finite) if finite else None),
            }
        record["windows"].append(w_rec)

    # union across windows: an item is anomalous in this task if it is anomalous
    # in any locked window
    for col in targets:
        union_zero: set[int] = set()
        union_nan: set[int] = set()
        n_items = 0
        for w in record["windows"]:
            t = w["targets"].get(col)
            if not t:
                continue
            n_items = max(n_items, t["n_items"])
            union_zero.update(t["zero_item_indices"])
            union_nan.update(t["nan_item_indices"])
        record["targets"][col] = {
            "n_items": n_items,
            "zero_error_items_any_window": len(union_zero),
            "nan_error_items_any_window": len(union_nan),
            "zero_item_indices_union": sorted(union_zero)[:50],
            "nan_item_indices_union": sorted(union_nan)[:50],
        }
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", choices=["dev", "lockbox"], default="dev")
    a = ap.parse_args()

    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = man["dev_tasks"] if a.layer == "dev" else man["lockbox_tasks"]

    print(f"scanning {len(entries)} {a.layer} tasks for zero seasonal error", flush=True)
    records = []
    t0 = time.time()
    for i, entry in enumerate(entries, start=1):
        ts = time.time()
        try:
            rec = scan_task(entry)
        except Exception as err:  # a load failure is data, not a crash
            rec = {"task_id": entry["task_id"], "dataset_config": entry["dataset_config"],
                   "error": f"{type(err).__name__}: {err}"}
        records.append(rec)
        zero = sum(t["zero_error_items_any_window"] for t in rec.get("targets", {}).values())
        nan = sum(t["nan_error_items_any_window"] for t in rec.get("targets", {}).values())
        print(f"[{i:2d}/{len(entries)}] {entry['dataset_config']:28s} "
              f"zero_err={zero:4d} nan_err={nan:4d}  ({time.time() - ts:5.1f}s, "
              f"total {time.time() - t0:6.1f}s)", flush=True)
        OUT.write_text(json.dumps({"layer": a.layer, "tasks": records}, indent=2),
                       encoding="utf-8")

    n_bad_tasks = sum(1 for r in records
                      if any(t["zero_error_items_any_window"] > 0
                             for t in r.get("targets", {}).values()))
    n_nan_tasks = sum(1 for r in records
                      if any(t["nan_error_items_any_window"] > 0
                             for t in r.get("targets", {}).values()))
    print(f"\ndone: {len(records)} tasks scanned, {n_bad_tasks} with >=1 zero-denominator item, "
          f"{n_nan_tasks} with >=1 NaN-denominator item "
          f"({time.time() - t0:.1f}s) -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
