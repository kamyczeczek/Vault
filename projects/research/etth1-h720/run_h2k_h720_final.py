"""H2K final locked evaluation on the canonical 12-origin sliding suite.

The implementation/configuration was selected only on early origins
8640, 9360, 10080, 10800.  This script does not choose hyperparameters.  It
fits each model on the fixed 360-day training slice and scores the 12 later
720-hour blocks.  Existing SAB-L artifacts are not overwritten.
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
from members.amr_fbs import AMRFBSForecaster
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft, fit_theta, pred_theta

H, CAP = 720, 8640


def load():
    return pd.read_csv(data_csv())["OT"].to_numpy(float)

def methods():
    def persistence(tr, ctx, h):
        return np.full(h, ctx[-1])
    def drift(tr, ctx, h):
        w = ctx[-720:]
        m, b = np.polyfit(np.arange(len(w)), w, 1)
        return b + m * np.arange(1, h + 1)
    def nlinear(tr, ctx, h):
        L, alpha = 96, 10.0
        ends = np.arange(L, len(tr) - h + 1)
        X = np.stack([tr[i-L:i] for i in ends])
        X = X - X[:, -1:]
        Y = np.stack([tr[i:i+h] - tr[i-1] for i in ends])
        W = np.linalg.solve(X.T @ X + alpha * np.eye(L), X.T @ Y)
        w = ctx[-L:]
        return (w - w[-1]) @ W + w[-1]
    def dlinear(tr, ctx, h):
        return pred_dlinear(fit_dlinear(tr, h), ctx)
    def fft(tr, ctx, h):
        return pred_fft(fit_fft(tr, h), ctx)
    def theta(tr, ctx, h):
        return pred_theta(fit_theta(tr, h), ctx)
    def amr(tr, ctx, h):
        return AMRFBSForecaster(lookback=96, seed=42).fit(tr, h).predict_hist(ctx)
    def knn(tr, ctx, h):
        return KNNFeatureForecaster(input_length=96, k_neighbors=24).fit(tr, h).predict_hist(ctx)
    def bigdict(tr, ctx, h):
        return BigDictELM(input_length=96).fit(tr, horizon=h).predict_hist(ctx)
    def h2k(tr, ctx, h):
        return H2KForecaster(input_length=168, k_neighbors=48, drift_damping=0.0).fit(tr, h).predict_hist(ctx)
    return [
        ("persistence", persistence), ("drift_linear", drift), ("nlinear_L96", nlinear),
        ("dlinear", dlinear), ("spectral_fft", fft), ("theta", theta), ("amr_fbs", amr),
        ("knn_96_k24", knn), ("bigdict_elm", bigdict), ("h2k", h2k),
    ]


def main():
    s = load()
    origins = [CAP + k * H for k in range((len(s) - CAP - H) // H + 1)]
    specs = methods()
    per_origin = []
    t0 = time.time()
    for oi, origin in enumerate(origins):
        train, ctx, actual = s[origin-CAP:origin], s[:origin], s[origin:origin+H]
        row = {"origin_index": oi, "origin": origin, "train_len": len(train),
               "train_std": float(train.std()), "methods": {}}
        for name, fn in specs:
            started = time.time()
            try:
                p = np.asarray(fn(train, ctx, H), dtype=float)[:H]
                e = p - actual
                row["methods"][name] = {
                    "mae_raw": round(float(np.mean(np.abs(e))), 4),
                    "mse_raw": round(float(np.mean(e*e)), 4),
                    "mae_norm": round(float(np.mean(np.abs(e))) / float(train.std()), 4),
                    "bin_mae": [round(float(np.mean(np.abs(e[i:i+120]))), 4) for i in range(0, H, 120)],
                    "wall_s": round(time.time()-started, 2),
                }
            except Exception as exc:
                row["methods"][name] = {"error": f"{type(exc).__name__}: {str(exc)[:160]}"}
            print(oi, name, row["methods"][name].get("mae_raw", row["methods"][name].get("error")), flush=True)
        per_origin.append(row)
    agg = {}
    for name, _ in specs:
        vals = [r["methods"][name] for r in per_origin if "mae_raw" in r["methods"][name]]
        maes = [v["mae_raw"] for v in vals]
        norms = [v["mae_norm"] for v in vals]
        agg[name] = {
            "mae_raw_mean": round(float(np.mean(maes)), 4) if maes else None,
            "mae_raw_std": round(float(np.std(maes)), 4) if maes else None,
            "mae_norm_mean": round(float(np.mean(norms)), 4) if norms else None,
            "horizon_bin_mae": [round(float(np.mean([v["bin_mae"][b] for v in vals])), 4) for b in range(6)] if vals else [None]*6,
            "below_incumbent_1_9781_origins": sum(m < 1.9781 for m in maes),
            "n_origins": len(vals),
        }
    win = {a: {b: sum(1 for r in per_origin if "mae_raw" in r["methods"].get(a, {}) and "mae_raw" in r["methods"].get(b, {}) and r["methods"][a]["mae_raw"] < r["methods"][b]["mae_raw"]) for b, _ in specs if a != b} for a, _ in specs}
    result = {
        "protocol": {"H": H, "train_cap_hours": CAP, "train_cap_days": CAP//24,
                     "mode": "sliding_fixed_360d", "origins": origins,
                     "fit": "fit on s[o-CAP:o] only", "context": "full s[:o]",
                     "h2k_selection": "L168_k48_d0.0 selected on early origins 8640,9360,10080,10800",
                     "incumbent_ref": "S44 H720 MAE 1.9781 raw"},
        "data": {"file": "data/ETTh1_h1.csv", "n": len(s)},
        "per_origin": per_origin, "aggregate": agg, "win_rate": win,
        "wall_total_s": round(time.time()-t0, 2),
    }
    out = ROOT / "results" / "etth1_h720_multi_origin_sliding360d_h2k_l168_k48.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# ETTh1 H720 locked H2K evaluation", "", "Protocol: genuine ETTh1 OT, fixed 360-day sliding window, 12 later origins; H2K L=168, k=48, damping=0 selected on early origins only.", "", "| method | MAE raw | std | MAE norm | bins | <1.9781 |", "|---|---:|---:|---:|---|---:|"]
    for name, a in sorted(agg.items(), key=lambda kv: kv[1]["mae_raw_mean"] if kv[1]["mae_raw_mean"] is not None else 1e9):
        if a["mae_raw_mean"] is not None:
            lines.append(f"| {name} | {a['mae_raw_mean']} | {a['mae_raw_std']} | {a['mae_norm_mean']} | {a['horizon_bin_mae']} | {a['below_incumbent_1_9781_origins']}/{a['n_origins']} |")
    (ROOT / "results" / "etth1_h720_multi_origin_sliding360d_h2k_l168_k48.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(agg, indent=2)); print("DONE", out, result["wall_total_s"])


if __name__ == "__main__":
    main()
