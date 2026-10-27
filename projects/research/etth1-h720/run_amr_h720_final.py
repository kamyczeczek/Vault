"""AMR-24/168 locked H720 evaluation on the canonical 12-origin sliding suite.

Frozen configuration: the level-anchor rule selected by `diag_amr_early_dev.py`
on the four early dev origins (8640, 9360, 10080, 10800).  This script does not
re-tune anything; it fits the frozen AMR-24/168 on the fixed 360-day training
slice, scores the 12 later 720-hour blocks once, and evaluates the pre-
registered gates:

  G1  mean rolling raw MAE at H720 < 1.9781 (incumbent S44)
  G2  beat DLinear and SpectralFFT at H720 (per-origin majority)
  G3  no-regression at H96/H336 (within +5% of the member's S47-pool best)
  G4  mean rank <= 2 across {members + SOTA baselines} over 5 seeds

Artifacts: results/etth1_h720_amr24168_<anchor>.{json,md},
results/etth1_h720_amr24168_g4.json, results/etth1_h720_amr24168_g3.json.

Run the expensive gates explicitly:
    python run_amr_h720_final.py            # locked H720 pass (seed 42)
    python run_amr_h720_final.py --g4       # + 5-seed mean-rank sweep
    python run_amr_h720_final.py --g3       # + H96/H336 regression
"""
from __future__ import annotations

import json
import os
import pathlib
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

import _workspace_paths
from _workspace_paths import ROOT, data_csv
from members.amr_24_168 import AMR24168Forecaster
from members.knn_feature_forecaster import KNNFeatureForecaster
from members.big_dict_elm import BigDictELM
from members.amr_fbs import AMRFBSForecaster
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft, fit_theta, pred_theta

H, CAP = 720, 8640
SEEDS = [42, 43, 44, 45, 46]
# G3 reference: AMR-24/168's S47-pool best is the amr_fbs singleton.
#   H96  <- results_s47.json  per_task.etth1_H96.singleton.amr_fbs.mean
#   H336 <- results_multi_horizon.json Electricity_Transformer_Load.336.AMR-FBS.mae
#          (S47 has no ETTh1 H336 entry; multi_horizon is the lineage reference.)
G3_REF = {96: 3.2641274145778896, 336: 6.7378}


def load():
    return pd.read_csv(data_csv())["OT"].to_numpy(float)


def load_selected_anchor() -> str:
    sel = ROOT / "results" / "amr_early_dev_selection.json"
    if sel.is_file():
        try:
            chosen = json.loads(sel.read_text(encoding="utf-8")).get("selected")
            if chosen:
                return chosen.replace("amr_", "")
        except Exception:
            pass
    return "weekly"  # design-intent default


def amr_factory(anchor: str, seed: int):
    return lambda: AMR24168Forecaster(lookback=336, hdict=256, seed=seed, anchor_rule=anchor)


def deterministic_methods():
    def persistence(tr, ctx, h):
        return np.full(h, ctx[-1])
    def drift(tr, ctx, h):
        w = ctx[-720:]
        m, b = np.polyfit(np.arange(len(w)), w, 1)
        return b + m * np.arange(1, h + 1)
    def nlinear(tr, ctx, h):
        L, alpha = 96, 10.0
        ends = np.arange(L, len(tr) - h + 1)
        X = np.stack([tr[i - L:i] for i in ends])
        X = X - X[:, -1:]
        Y = np.stack([tr[i:i + h] - tr[i - 1] for i in ends])
        W = np.linalg.solve(X.T @ X + alpha * np.eye(L), X.T @ Y)
        w = ctx[-L:]
        return (w - w[-1]) @ W + w[-1]
    return [
        ("persistence", persistence), ("drift_linear", drift), ("nlinear_L96", nlinear),
        ("dlinear", lambda tr, ctx, h: pred_dlinear(fit_dlinear(tr, h), ctx)),
        ("spectral_fft", lambda tr, ctx, h: pred_fft(fit_fft(tr, h), ctx)),
        ("theta", lambda tr, ctx, h: pred_theta(fit_theta(tr, h), ctx)),
    ]


def seed_methods(anchor: str, seed: int):
    return [
        ("amr_fbs", lambda tr, ctx, h: AMRFBSForecaster(lookback=96, seed=seed).fit(tr, h).predict_hist(ctx)),
        ("knn_96_k24", lambda tr, ctx, h: KNNFeatureForecaster(input_length=96, k_neighbors=24).fit(tr, h).predict_hist(ctx)),
        ("bigdict_elm", lambda tr, ctx, h: BigDictELM(input_length=96, seed=seed).fit(tr, horizon=h).predict_hist(ctx)),
        ("amr_24_168", lambda tr, ctx, h: amr_factory(anchor, seed)().fit(tr, h).predict_hist(ctx)),
    ]


def all_methods(anchor: str, seed: int):
    return deterministic_methods() + seed_methods(anchor, seed)


def _maes(fn, s, o, h):
    train, ctx, actual = s[o - CAP:o], s[:o], s[o:o + h]
    p = np.asarray(fn(train, ctx, h), dtype=float)[:h]
    e = p - actual
    return {"mae_raw": round(float(np.mean(np.abs(e))), 4),
            "mae_norm": round(float(np.mean(np.abs(e))) / float(train.std()), 4)}


def run_locked(anchor: str) -> dict:
    s = load()
    origins = [CAP + k * H for k in range((len(s) - CAP - H) // H + 1)]
    specs = all_methods(anchor, 42)
    t0 = time.time()
    per_origin = []
    for oi, o in enumerate(origins):
        row = {"origin_index": oi, "origin": o, "train_len": CAP, "methods": {}}
        for name, fn in specs:
            started = time.time()
            try:
                m = _maes(fn, s, o, H)
                m["wall_s"] = round(time.time() - started, 2)
                row["methods"][name] = m
            except Exception as exc:
                row["methods"][name] = {"error": f"{type(exc).__name__}: {str(exc)[:160]}"}
            print(oi, o, name, row["methods"][name].get("mae_raw", row["methods"][name].get("error")), flush=True)
        per_origin.append(row)

    agg = {}
    for name, _ in specs:
        vals = [r["methods"][name] for r in per_origin if "mae_raw" in r["methods"][name]]
        maes = [v["mae_raw"] for v in vals]
        agg[name] = {
            "mae_raw_mean": round(float(np.mean(maes)), 4) if maes else None,
            "mae_raw_std": round(float(np.std(maes)), 4) if maes else None,
            "mae_norm_mean": round(float(np.mean([v["mae_norm"] for v in vals])), 4) if vals else None,
            "below_incumbent_1_9781": sum(m < 1.9781 for m in maes),
            "n_origins": len(vals),
        }
    amr = {n: a for n, a in agg.items() if "amr_24_168" in n}
    amr_mean = next(iter(amr.values()))["mae_raw_mean"]
    dl = agg.get("dlinear", {}).get("mae_raw_mean")
    ff = agg.get("spectral_fft", {}).get("mae_raw_mean")
    g1 = (amr_mean is not None and amr_mean < 1.9781)
    # G2: per-origin majority win vs each baseline
    def wins(name, ref):
        c = 0
        for r in per_origin:
            a, b = r["methods"].get(name, {}), r["methods"].get(ref, {})
            if "mae_raw" in a and "mae_raw" in b:
                c += a["mae_raw"] < b["mae_raw"]
        return c
    g2 = (wins("amr_24_168", "dlinear") >= 6) and (wins("amr_24_168", "spectral_fft") >= 6)
    result = {
        "protocol": {"H": H, "train_cap_hours": CAP, "mode": "sliding_fixed_360d",
                     "origins": origins, "fit": "fit on s[o-CAP:o] only", "context": "full s[:o]",
                     "amr_selection": f"anchor_rule={anchor} selected on early dev origins",
                     "seed": 42, "incumbent_ref": "S44 H720 MAE 1.9781 raw"},
        "data": {"file": "ETTh1_h1.csv", "n": len(s)},
        "per_origin": per_origin, "aggregate": agg,
        "gates": {
            "G1_below_incumbent": g1, "G1_amr_mean": amr_mean,
            "G2_beat_dlinear_origins": wins("amr_24_168", "dlinear"),
            "G2_beat_spectralfft_origins": wins("amr_24_168", "spectral_fft"),
            "G2_pass": g2,
            "G1_amr_mean_vs_dlinear": dl, "G1_amr_mean_vs_spectral": ff,
        },
        "wall_total_s": round(time.time() - t0, 2),
    }
    out = ROOT / "results" / f"etth1_h720_amr24168_{anchor}.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    _write_md(result, anchor)
    print(json.dumps(result["gates"], indent=2))
    print("DONE", out, result["wall_total_s"])
    return result


def _write_md(result, anchor):
    lines = [f"# ETTh1 H720 locked AMR-24/168 evaluation (anchor={anchor})", "",
             f"Protocol: genuine ETTh1 OT, fixed 360-day sliding window, {result['aggregate']['persistence']['n_origins']} later origins; "
             f"AMR-24/168 lookback=336, hdict=256, seed=42, anchor_rule={anchor} (selected on early dev origins).", "",
             "| method | MAE raw | std | MAE norm | <1.9781 |", "|---|---:|---:|---:|---:|"]
    for name, a in sorted(result["aggregate"].items(),
                          key=lambda kv: kv[1]["mae_raw_mean"] if kv[1]["mae_raw_mean"] is not None else 1e9):
        if a["mae_raw_mean"] is not None:
            lines.append(f"| {name} | {a['mae_raw_mean']} | {a['mae_raw_std']} | {a['mae_norm_mean']} | "
                         f"{a['below_incumbent_1_9781']}/{a['n_origins']} |")
    g = result["gates"]
    lines += ["", "## Gates (H720)",
              f"- G1 (mean raw MAE < 1.9781): amr={g['G1_amr_mean']} -> {'PASS' if g['G1_below_incumbent'] else 'FAIL'}",
              f"- G2 (beat DLinear on {g['G2_beat_dlinear_origins']}/12 and SpectralFFT on {g['G2_beat_spectralfft_origins']}/12): "
              f"{'PASS' if g['G2_pass'] else 'FAIL'}"]
    (ROOT / "results" / f"etth1_h720_amr24168_{anchor}.md").write_text("\n".join(lines), encoding="utf-8")


def run_g4(anchor: str) -> dict:
    s = load()
    origins = [CAP + k * H for k in range((len(s) - CAP - H) // H + 1)]
    cache_path = ROOT / "results" / "amr_g4_cells.json"
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.is_file() else {}
    except (OSError, json.JSONDecodeError):
        cache = {}
    cache = cache if cache.get("anchor") == anchor else {"anchor": anchor, "cells": {}}
    cells = cache.setdefault("cells", {})
    jobs = [(anchor, int(seed), int(origin), s) for seed in SEEDS for origin in origins
            if f"{seed}:{origin}" not in cells]
    workers = max(1, min(len(jobs), (os.cpu_count() or 2) - 1))
    if jobs:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for seed, origin, cell in pool.map(_g4_cell, jobs):
                cells[f"{seed}:{origin}"] = cell
                cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
                print("G4 cached", seed, origin, flush=True)

    per_seed = {}
    for seed in SEEDS:
        row = {}
        for origin in origins:
            cell = cells[f"{seed}:{origin}"]
            amr = cell.get("amr_24_168")
            ranked = [v for v in cell.values() if v is not None]
            row[origin] = (1 + sum(1 for v in ranked if v < amr)) if amr is not None else None
        ranks = [v for v in row.values() if v is not None]
        per_seed[seed] = {"ranks": row, "mean_rank": round(float(np.mean(ranks)), 4) if ranks else None}
        print("G4 seed", seed, "mean_rank", per_seed[seed]["mean_rank"], flush=True)
    mr = [per_seed[sd]["mean_rank"] for sd in SEEDS if per_seed[sd]["mean_rank"] is not None]
    mean_rank = float(np.mean(mr)) if mr else None
    result = {"gate": "G4_mean_rank_across_5_seeds", "anchor": anchor, "seeds": SEEDS,
              "per_seed": per_seed, "mean_rank": round(mean_rank, 4) if mean_rank else None,
              "pass": (mean_rank is not None and mean_rank <= 2.0)}
    out = ROOT / "results" / f"etth1_h720_amr24168_g4.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


def _g4_cell(args):
    """Evaluate one independent (seed, origin) cell for ProcessPoolExecutor."""
    anchor, seed, origin, series = args

    def safe(fn):
        try:
            return _maes(fn, series, origin, H)["mae_raw"]
        except Exception:
            return None

    cell = {name: safe(fn) for name, fn in deterministic_methods()}
    cell.update({name: safe(fn) for name, fn in seed_methods(anchor, seed)})
    return seed, origin, cell


def run_g3(anchor: str) -> dict:
    s = load()
    out_rows = {}
    for Hs in (96, 336):
        origins = [CAP + k * Hs for k in range((len(s) - CAP - Hs) // Hs + 1)][:4]
        factory = lambda tr, ctx, h: amr_factory(anchor, 42)().fit(tr, h).predict_hist(ctx)
        maes = [_maes(factory, s, o, Hs)["mae_raw"] for o in origins]
        ref = G3_REF[Hs]
        out_rows[str(Hs)] = {"origins": origins, "amr_mae_mean": round(float(np.mean(maes)), 4),
                             "s47_ref": ref, "plus5pct": round(1.05 * ref, 4),
                             "pass": float(np.mean(maes)) <= 1.05 * ref}
    result = {"gate": "G3_no_regression_H96_H336", "anchor": anchor,
              "ref_source": "results_s47.json etth1_H96 amr_fbs singleton; results_multi_horizon.json H336 amr_fbs",
              "runs": out_rows, "pass": all(v["pass"] for v in out_rows.values())}
    out = ROOT / "results" / "etth1_h720_amr24168_g3.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


def main():
    anchor = load_selected_anchor()
    print(f"AMR-24/168 locked H720 run, anchor_rule={anchor}", flush=True)
    run_locked(anchor)
    if "--g4" in __import__("sys").argv:
        run_g4(anchor)
    if "--g3" in __import__("sys").argv:
        run_g3(anchor)


if __name__ == "__main__":
    main()
