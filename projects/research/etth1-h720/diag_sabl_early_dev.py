"""Independent early-origin development selection for SAB-L.

The four origins are disjoint from the final late-origin evaluation blocks in
the canonical H720 run.  Only the compact SAB-L architecture and a small,
pre-declared ridge grid are compared.  This is development selection, not a
public benchmark result; the final result must be the full locked suite.
"""
from __future__ import annotations
import json, pathlib, sys, time
import numpy as np
import pandas as pd
import _workspace_paths
from _workspace_paths import ROOT, data_csv
from members.big_dict_elm import BigDictELM
from members.sab_l import SABLForecaster

H, CAP = 720, 8640
ORIGINS = (CAP, CAP + H, CAP + 2 * H, CAP + 3 * H)
DATA = data_csv()
SPECS = [
    ("bigdict_L96", lambda: BigDictELM(input_length=96)),
    ("sabl_compact_a10", lambda: SABLForecaster(input_length=336, profile="compact", alpha=10.0, dict_dim=256)),
    ("sabl_compact_a30", lambda: SABLForecaster(input_length=336, profile="compact", alpha=30.0, dict_dim=256)),
    ("sabl_compact_a100", lambda: SABLForecaster(input_length=336, profile="compact", alpha=100.0, dict_dim=256)),
    ("sabl_compact_a300", lambda: SABLForecaster(input_length=336, profile="compact", alpha=300.0, dict_dim=256)),
    ("sabl_compact_a1000", lambda: SABLForecaster(input_length=336, profile="compact", alpha=1000.0, dict_dim=256)),
]

def run_one(s, o, factory):
    train, actual = s[o - CAP:o], s[o:o + H]
    t0 = time.time()
    model = factory()
    if isinstance(model, BigDictELM):
        model.fit(train, horizon=H)
    else:
        model.fit(train, H)
    pred = np.asarray(model.predict_hist(s[:o]), float)[:H]
    if not np.isfinite(pred).all():
        raise RuntimeError("non-finite prediction")
    err = pred - actual
    return {"mae": round(float(np.mean(np.abs(err))), 6), "mse": round(float(np.mean(err ** 2)), 6), "fit_s": round(time.time() - t0, 2)}

def main():
    s = pd.to_numeric(pd.read_csv(DATA)["OT"], errors="coerce").dropna().to_numpy(float)
    result = {"purpose": "independent early-origin development selection", "origins": list(ORIGINS), "runs": []}
    out = ROOT / "results" / "sabl_early_dev_selection.json"
    for o in ORIGINS:
        row = {"origin": int(o), "date": str(pd.to_datetime(o, unit="h", origin="2016-07-01 00:00:00"))[:10], "methods": {}}
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
    result["selected"] = min((k for k, v in means.items() if k.startswith("sabl_") and v is not None), key=means.get)
    out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1), flush=True)

if __name__ == "__main__":
    main()
