"""SAB-L architecture isolation: BigDict bank vs SAB-L head/readout design."""
from __future__ import annotations
import json, pathlib, sys, time
import numpy as np
import pandas as pd
import _workspace_paths
from _workspace_paths import ROOT, data_csv
from members.big_dict_elm import BigDictELM
from members.sab_l import SABLForecaster

H, CAP = 720, 8640
ORIGINS = (8640 + 5 * H, 8640 + 11 * H)
DATA = data_csv()

SPECS = [
    ("bigdict_L96", lambda: BigDictELM(input_length=96)),
    ("bigdict_L336", lambda: BigDictELM(input_length=336)),
    ("sabl_cos_grouped", lambda: SABLForecaster(input_length=336, profile="compact", alpha=100, dict_dim=256)),
    ("sabl_cos_approx_grouped", lambda: SABLForecaster(input_length=336, profile="approx", alpha=100, dict_dim=256)),
    ("sabl_cos_approx_direct", lambda: SABLForecaster(input_length=336, profile="approx", alpha=100, dict_dim=256, heads=(720,))),
    ("sabl_cos_approx_direct_a300", lambda: SABLForecaster(input_length=336, profile="approx", alpha=300, dict_dim=256, heads=(720,))),
]

def fit_predict(s, o, factory):
    tr = s[o-CAP:o]
    t0 = time.time()
    m = factory()
    if isinstance(m, BigDictELM):
        m.fit(tr, horizon=H)
    else:
        m.fit(tr, H)
    p = np.asarray(m.predict_hist(s[:o]), float)[:H]
    y = s[o:o+H]
    return {"mae": float(np.mean(np.abs(p-y))), "mse": float(np.mean((p-y)**2)), "fit_s": time.time()-t0, "alpha": getattr(m, "alpha_chosen_", None)}

def main():
    s = pd.to_numeric(pd.read_csv(DATA)["OT"], errors="coerce").dropna().to_numpy(float)
    result = {"origins": list(ORIGINS), "specs": [x[0] for x in SPECS], "runs": []}
    path = ROOT / "results" / "sabl_architecture_diagnostic.json"
    for o in ORIGINS:
        row = {"origin": int(o), "methods": {}}
        result["runs"].append(row)
        print("ORIGIN", o, flush=True)
        for name, factory in SPECS:
            try:
                v = fit_predict(s, o, factory)
                row["methods"][name] = v
                print(name, json.dumps(v), flush=True)
            except Exception as e:
                row["methods"][name] = {"error": f"{type(e).__name__}: {e}"}
                print(name, row["methods"][name], flush=True)
            path.write_text(json.dumps(result, indent=1), encoding="utf-8")
    result["mean_mae"] = {}
    for name, _ in SPECS:
        vals = [r["methods"].get(name, {}).get("mae") for r in result["runs"]]
        result["mean_mae"][name] = float(np.mean(vals)) if all(v is not None for v in vals) else None
    path.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result["mean_mae"], indent=1), flush=True)

if __name__ == "__main__":
    main()
