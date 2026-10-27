"""Independent early-origin development selection for AMR-24/168.

Mirrors the SAB-L / H2K early-dev recipe: four development origins
(8640, 9360, 10080, 10800) -- disjoint from the later locked blocks in the
canonical H720 run -- are used to choose the level-anchor rule and the envelope
weights before a single frozen pass over the 12 locked origins.  BigDictELM is
kept as an external reference only; the selection among AMR-24/168 variants is
what gets frozen.  This is development selection, not a public benchmark
result; the final number must come from the locked suite.
"""
from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd

import _workspace_paths
from _workspace_paths import ROOT, data_csv
from members.big_dict_elm import BigDictELM
from members.amr_24_168 import AMR24168Forecaster

H, CAP = 720, 8640
ORIGINS = (CAP, CAP + H, CAP + 2 * H, CAP + 3 * H)
DATA = data_csv()

SPECS = [
    ("amr_last",   lambda: AMR24168Forecaster(lookback=336, hdict=256, seed=42, anchor_rule="last")),
    ("amr_weekly", lambda: AMR24168Forecaster(lookback=336, hdict=256, seed=42, anchor_rule="weekly")),
    ("amr_blend",  lambda: AMR24168Forecaster(lookback=336, hdict=256, seed=42, anchor_rule="blend")),
    ("bigdict_L96", lambda: BigDictELM(input_length=96)),
]


def run_one(s, o, factory):
    train, actual = s[o - CAP:o], s[o:o + H]
    t0 = time.time()
    model = factory()
    model.fit(train, horizon=H)
    pred = np.asarray(model.predict_hist(s[:o]), float)[:H]
    if not np.isfinite(pred).all():
        raise RuntimeError("non-finite prediction")
    err = pred - actual
    return {
        "mae": round(float(np.mean(np.abs(err))), 6),
        "mse": round(float(np.mean(err ** 2)), 6),
        "mae_norm": round(float(np.mean(np.abs(err))) / float(train.std()), 6),
        "fit_s": round(time.time() - t0, 2),
    }


def main():
    s = pd.to_numeric(pd.read_csv(DATA)["OT"], errors="coerce").dropna().to_numpy(float)
    result = {"purpose": "independent early-origin development selection (AMR-24/168)",
              "origins": list(ORIGINS), "runs": []}
    out = ROOT / "results" / "amr_early_dev_selection.json"
    for o in ORIGINS:
        row = {"origin": int(o),
               "date": str(pd.to_datetime(o, unit="h", origin="2016-07-01 00:00:00"))[:10],
               "methods": {}}
        result["runs"].append(row)
        print("ORIGIN", o, row["date"], flush=True)
        for name, factory in SPECS:
            try:
                row["methods"][name] = run_one(s, o, factory)
                print(name, row["methods"][name], flush=True)
            except Exception as exc:
                row["methods"][name] = {"error": f"{type(exc).__name__}: {exc}"}
                print(name, row["methods"][name], flush=True)
            out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    means = {}
    for name, _ in SPECS:
        vals = [r["methods"].get(name, {}).get("mae") for r in result["runs"]]
        means[name] = round(float(np.mean(vals)), 6) if all(v is not None for v in vals) else None
    result["mean_mae"] = means
    amr = {k: v for k, v in means.items() if k.startswith("amr_") and v is not None}
    result["selected"] = min(amr, key=amr.get) if amr else None
    out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1), flush=True)


if __name__ == "__main__":
    main()
