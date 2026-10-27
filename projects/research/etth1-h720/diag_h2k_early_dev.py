"""H2K development-only selection on early ETTh1 origins.

This script is intentionally separate from the locked late-origin suite.  The
four origins below were also used for the SAB-L early-dev selection; H2K is a
new candidate, so no late-origin result is inspected while selecting it.
"""
from __future__ import annotations

import json
import pathlib
import time
import numpy as np
import pandas as pd

import _workspace_paths
from _workspace_paths import ROOT, data_csv
from members.h2k import H2KForecaster
from members.knn_feature_forecaster import KNNFeatureForecaster
from members.big_dict_elm import BigDictELM

OUT = ROOT / "results" / "h2k_early_dev_selection.json"
LOG = ROOT / "results" / "h2k_early_dev_selection.log"
H = 720
CAP = 8640
ORIGINS = (CAP, CAP + H, CAP + 2 * H, CAP + 3 * H)

# Deliberately small, preregistered H2K grid.  The final configuration is
# selected by mean MAE on ORIGINS only; late origins remain locked.
SPECS = [
    ("h2k_L96_k5", dict(input_length=96, k_neighbors=5)),
    ("h2k_L96_k12", dict(input_length=96, k_neighbors=12)),
    ("h2k_L96_k24", dict(input_length=96, k_neighbors=24)),
    ("h2k_L96_k48", dict(input_length=96, k_neighbors=48)),
    ("h2k_L168_k12", dict(input_length=168, k_neighbors=12)),
    ("h2k_L168_k24", dict(input_length=168, k_neighbors=24)),
    ("h2k_L336_k12", dict(input_length=336, k_neighbors=12)),
    ("h2k_L336_k24", dict(input_length=336, k_neighbors=24)),
    ("h2k_L672_k12", dict(input_length=672, k_neighbors=12)),
    ("h2k_L672_k24", dict(input_length=672, k_neighbors=24)),
]


def load():
    df = pd.read_csv(data_csv())
    return pd.to_numeric(df["OT"], errors="coerce").dropna().to_numpy(float)


def main():
    series = load()
    rows = {name: [] for name, _ in SPECS}
    baselines = {"bigdict_L96": [], "knn_L96_k24": []}
    started = time.time()
    with LOG.open("w", encoding="utf-8") as log:
        log.write("H2K early development selection (no late-origin evaluation)\n")
        log.write(f"origins={ORIGINS}\n")
        for origin in ORIGINS:
            train = series[max(0, origin - CAP):origin]
            context = series[:origin]
            actual = series[origin:origin + H]
            log.write(f"origin={origin}\n")
            for name, kwargs in SPECS:
                t0 = time.time()
                try:
                    pred = H2KForecaster(**kwargs).fit(train, H).predict_hist(context)
                    mae = float(np.mean(np.abs(pred - actual)))
                    rows[name].append(mae)
                    log.write(f"  {name}: {mae:.6f} ({time.time()-t0:.2f}s)\n")
                except Exception as exc:
                    log.write(f"  {name}: ERROR {type(exc).__name__}: {exc}\n")
            for name in baselines:
                t0 = time.time()
                try:
                    if name.startswith("bigdict"):
                        model = BigDictELM(input_length=96).fit(train, horizon=H)
                    else:
                        model = KNNFeatureForecaster(input_length=96, k_neighbors=24).fit(train, H)
                    pred = model.predict_hist(context)
                    mae = float(np.mean(np.abs(pred - actual)))
                    baselines[name].append(mae)
                    log.write(f"  {name}: {mae:.6f} ({time.time()-t0:.2f}s)\n")
                except Exception as exc:
                    log.write(f"  {name}: ERROR {type(exc).__name__}: {exc}\n")
            print(f"origin {origin} done", flush=True)

    means = {name: (float(np.mean(values)) if values else None)
             for name, values in rows.items()}
    valid = [(name, means[name]) for name in means if means[name] is not None]
    selected = min(valid, key=lambda pair: pair[1])[0] if valid else None
    result = {
        "purpose": "independent early-origin H2K development selection",
        "protocol": "genuine ETTh1 OT; fixed 360-day train cap; origins are disjoint 720h blocks",
        "H": H, "cap": CAP, "origins": list(ORIGINS),
        "specs": dict(SPECS),
        "mean_mae": means,
        "per_origin_mae": rows,
        "baselines_mean_mae": {k: (float(np.mean(v)) if v else None) for k, v in baselines.items()},
        "baselines_per_origin_mae": baselines,
        "selected": selected,
        "wall_s": round(time.time() - started, 2),
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"WROTE {OUT} and {LOG}")


if __name__ == "__main__":
    main()
