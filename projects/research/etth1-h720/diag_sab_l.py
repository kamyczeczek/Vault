"""Focused, logged SAB-L dev diagnostic.

This is a development diagnostic, not a second public test suite.  It uses
origins already present in the canonical H720 run; any subsequent choice must
still be reported on that complete suite.  The goal is to isolate concrete
implementation differences rather than perform a broad hyperparameter sweep.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
import traceback

import numpy as np
import pandas as pd

import _workspace_paths
from _workspace_paths import ROOT, data_csv
from members.big_dict_elm import BigDictELM
from members.sab_l import SABLForecaster

H = 720
CAP = 8640
ORIGINS = (8640 + 5 * H, 8640 + 11 * H)  # 2017-11-23, 2018-05-22
DATA = data_csv()


def evaluate(s, origin, make_model):
    train = s[origin - CAP:origin]
    actual = s[origin:origin + H]
    start = time.time()
    if isinstance(model := make_model(), BigDictELM):
        model.fit(train, horizon=H)
    else:
        model.fit(train, H)
    pred = np.asarray(model.predict_hist(s[:origin]), dtype=float)[:H]
    err = pred - actual
    if not np.isfinite(pred).all():
        raise RuntimeError("non-finite prediction")
    return {
        "mae": round(float(np.mean(np.abs(err))), 6),
        "mse": round(float(np.mean(err ** 2)), 6),
        "prediction_range": [round(float(pred.min()), 5), round(float(pred.max()), 5)],
        "fit_s": round(time.time() - start, 2),
        "alpha_chosen": getattr(model, "alpha_chosen_", None),
        "profile": getattr(model, "profile_", getattr(model, "profile", None)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Only run baseline plus fixed SAB-L.")
    args = parser.parse_args()

    s = pd.to_numeric(pd.read_csv(DATA)["OT"], errors="coerce").dropna().to_numpy(float)
    specs = [
        ("bigdict_L96", lambda: BigDictELM(input_length=96)),
        ("sabl_fixed_L336_a100", lambda: SABLForecaster(input_length=336, dict_dim=256, alpha=100.0, profile="compact")),
        ("sabl_fixed_L336_a1000", lambda: SABLForecaster(input_length=336, dict_dim=256, alpha=1000.0, profile="compact")),
        ("sabl_scaled_a100", lambda: SABLForecaster(input_length=336, dict_dim=256, alpha=100.0, profile="compact", feature_scaling=True)),
        ("sabl_scaled_a1000", lambda: SABLForecaster(input_length=336, dict_dim=256, alpha=1000.0, profile="compact", feature_scaling=True)),
        ("sabl_scaled_valalpha", lambda: SABLForecaster(input_length=336, dict_dim=256, alpha=100.0, profile="compact", feature_scaling=True, alpha_grid=(30, 100, 300, 1000, 3000))),
    ]
    if not args.quick:
        specs.extend([
            ("sabl_scaled_L96_a1000", lambda: SABLForecaster(input_length=96, dict_dim=256, alpha=1000.0, profile="compact", feature_scaling=True)),
            ("sabl_scaled_approx_a1000", lambda: SABLForecaster(input_length=336, dict_dim=256, alpha=1000.0, profile="approx", feature_scaling=True)),
        ])

    results = {"purpose": "development diagnostic; not an independent evaluation set", "origins": list(ORIGINS), "runs": []}
    out_path = ROOT / "results" / "sabl_dev_diagnostic.json"
    log_path = ROOT / "results" / "sabl_dev_diagnostic.log"
    out_path.parent.mkdir(exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        for origin in ORIGINS:
            results["runs"].append({"origin": origin, "date": str(pd.to_datetime(origin, unit="h", origin="2016-07-01 00:00:00"))[:10], "methods": {}})
            print(f"\n=== origin {origin} ({results['runs'][-1]['date']}) ===", flush=True)
            log.write(f"\n=== origin {origin} ({results['runs'][-1]['date']}) ===\n")
            log.flush()
            for name, factory in specs:
                print(f"  fitting {name} ...", end=" ", flush=True)
                try:
                    row = evaluate(s, origin, factory)
                    results["runs"][-1]["methods"][name] = row
                    line = f"MAE={row['mae']:.4f} range={row['prediction_range']} fit={row['fit_s']}s"
                except Exception as exc:
                    results["runs"][-1]["methods"][name] = {"error": f"{type(exc).__name__}: {exc}"}
                    line = results["runs"][-1]["methods"][name]["error"]
                    traceback.print_exc(file=log)
                print(line, flush=True)
                log.write(f"  {name:27s} {line}\n")
                log.flush()
                out_path.write_text(json.dumps(results, indent=1), encoding="utf-8")

    summary = {}
    for name, _ in specs:
        vals = [r["methods"].get(name, {}).get("mae") for r in results["runs"]]
        summary[name] = round(float(np.mean(vals)), 6) if all(v is not None for v in vals) else None
    results["mean_mae_two_origins"] = summary
    out_path.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print("\nMean MAE (two development origins):", json.dumps(summary, indent=1), flush=True)


if __name__ == "__main__":
    main()
