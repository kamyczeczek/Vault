"""H2K focused early-dev ablation after the level-relative correction.

This is still development-only (origins 8640..10800).  It tests the two
remaining design choices independently: retrieval neighborhood size and
how much of the retrieved motif should be trusted when the query is not a
close match.  No late-origin result is consulted.
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

OUT = ROOT / "results" / "h2k_early_dev_ablation.json"
LOG = ROOT / "results" / "h2k_early_dev_ablation.log"
H, CAP = 720, 8640
ORIGINS = (CAP, CAP + H, CAP + 2 * H, CAP + 3 * H)

SPECS = []
for length in (168, 336, 672):
    for k in (5, 12, 24, 48):
        for damping in (0.0, 0.25):
            SPECS.append((f"L{length}_k{k}_d{damping}", dict(
                input_length=length, k_neighbors=k, drift_damping=damping)))


    s = pd.read_csv(data_csv())["OT"].to_numpy(float)
    scores = {}
    started = time.time()
    with LOG.open("w", encoding="utf-8") as log:
        for oi, origin in enumerate(ORIGINS):
            train, ctx, actual = s[origin - CAP:origin], s[:origin], s[origin:origin + H]
            log.write(f"origin={origin}\n")
            for name, kwargs in SPECS:
                t0 = time.time()
                try:
                    p = H2KForecaster(**kwargs).fit(train, H).predict_hist(ctx)
                    mae = float(np.mean(np.abs(p - actual)))
                    scores.setdefault(name, []).append(mae)
                    log.write(f"  {name}: {mae:.6f} ({time.time()-t0:.2f}s)\n")
                except Exception as exc:
                    log.write(f"  {name}: ERROR {type(exc).__name__}: {exc}\n")
            print(f"origin {oi+1}/{len(ORIGINS)}", flush=True)
    means = {k: float(np.mean(v)) for k, v in scores.items() if v}
    selected = min(means, key=means.get)
    result = {
        "purpose": "H2K early-dev ablation; no locked late-origin evaluation",
        "origins": list(ORIGINS), "H": H, "cap": CAP,
        "specs": {name: kwargs for name, kwargs in SPECS},
        "per_origin_mae": scores, "mean_mae": means,
        "selected": selected, "wall_s": round(time.time()-started, 2),
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("SELECTED", selected, "MAE", means[selected])
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
