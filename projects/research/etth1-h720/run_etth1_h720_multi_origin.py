"""ETTh1 H720 multi-origin test (different starting points) — S49 protocol.

Genuine ETTh1 (OT column; zhouhaoyi/ETDataset ETT-small; n=17420 hourly,
2016-07-01..2018-06-30). Leakage-safe expanding-window protocol:
    for origin o:  train = s[max(0, o-CAP):o]   (fit here only)
                  pred  = model.predict(context s[:o], H=720)
                  score on s[o:o+720]
Origins: disjoint 30-day windows, o = 4320 + k*720  (18 origins).
Metrics: MAE/MSE raw, MAE normalized by train-std, 120h horizon-bin MAE profile.
Incumbent reference: S44 H720 MAE 1.9781 (raw scale, see H720 lineage).
Outputs: results/etth1_h720_multi_origin.{json,md}, plots/etth1_h720_multi_origin.png
"""
import json, time, pathlib, sys
import numpy as np
import pandas as pd

import _workspace_paths
from _workspace_paths import ROOT, RESULTS_DIR, data_csv
from members.amr_fbs import AMRFBSForecaster
from members.knn_feature_forecaster import KNNFeatureForecaster
from members.big_dict_elm import BigDictELM
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft, fit_theta, pred_theta
from members.sab_l import SABLForecaster

H, CAP, O0 = 720, 8640, 4320

def load_data():
    df = pd.read_csv(data_csv())
    s = pd.to_numeric(df["OT"], errors="coerce").dropna().to_numpy(float)
    dates = [str(x)[:10] for x in df["date"]]
    return s, dates

def drift_pred(ctx, H):
    w = ctx[-720:]
    t = np.arange(720)
    m, b = np.polyfit(t, w, 1)
    return b + m * np.arange(1, H + 1)

def nlinear_fit(train, H, L=96, alpha=10.0):
    ends = np.arange(L, train.shape[0] - H + 1)
    SW = np.stack([train[i - L:i] for i in ends])
    X = SW - SW[:, -1:]
    Y = np.stack([train[e:e + H] - train[e - 1] for e in ends])
    A = X.T @ X + alpha * np.eye(L)
    return np.linalg.solve(A, X.T @ Y)

def make_methods(sabl_alpha=10.0, sabl_profile="auto"):
    def nl(tr, ctx, H_):
        W = nlinear_fit(tr, H_)
        w = ctx[-96:]; a = w[-1]
        return (w - a) @ W + a
    def dlin(tr, ctx, H_):
        return pred_dlinear(fit_dlinear(tr, H_), ctx)
    def fft(tr, ctx, H_):
        return pred_fft(fit_fft(tr, H_), ctx)
    def theta(tr, ctx, H_):
        return pred_theta(fit_theta(tr, H_), ctx)
    def amr(tr, ctx, H_):
        return AMRFBSForecaster(lookback=96, seed=42).fit(tr, H_).predict_hist(ctx)
    def knn(tr, ctx, H_):
        return KNNFeatureForecaster(input_length=96).fit(tr, H_).predict_hist(ctx)
    def bigd(tr, ctx, H_):
        return BigDictELM(input_length=96).fit(tr, horizon=H_).predict_hist(ctx)
    def sabl(tr, ctx, H_):
        return SABLForecaster(alpha=sabl_alpha, profile=sabl_profile).fit(tr, H_).predict_hist(ctx)[:H_]
    return [
        ("persistence", lambda tr, ctx, H_: np.full(H_, ctx[-1])),
        ("drift_linear", lambda tr, ctx, H_: drift_pred(ctx, H_)),
        ("nlinear_L96", nl),
        ("dlinear", dlin),
        ("spectral_fft", fft),
        ("theta", theta),
        ("amr_fbs", amr),
        ("knn_96_k24", knn),
        ("bigdict_elm", bigd),
        ("sab_l", sabl),
    ]

def main():
    s, dates = load_data()
    N = len(s)
    sliding = "--sliding" in sys.argv
    sabl_alpha = 10.0
    sabl_profile = "auto"
    if "--sabl-alpha" in sys.argv:
        sabl_alpha = float(sys.argv[sys.argv.index("--sabl-alpha") + 1])
    if "--sabl-profile" in sys.argv:
        sabl_profile = sys.argv[sys.argv.index("--sabl-profile") + 1]
    custom_tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else ""
    o0 = CAP if sliding else O0
    origins = [o0 + k * H for k in range((N - o0 - H) // H + 1)]
    tag = ("_sliding360d" if sliding else "") + custom_tag
    methods = make_methods(sabl_alpha=sabl_alpha, sabl_profile=sabl_profile)
    per_origin = []
    t0 = time.time()
    for oi, o in enumerate(origins):
        train = s[max(0, o - CAP):o]
        std_tr = float(train.std())
        actual = s[o:o + H]
        row = {"origin_index": oi, "origin": int(o), "date": dates[o],
               "train_len": int(len(train)), "train_std": std_tr, "methods": {}}
        for name, fn in methods:
            tm = time.time()
            try:
                pred = np.asarray(fn(train, s[:o], H), dtype=float)[:H]
                err = pred - actual
                bins = [float(np.mean(np.abs(err[b * 120:(b + 1) * 120]))) for b in range(6)]
                row["methods"][name] = {
                    "mae_raw": round(float(np.mean(np.abs(err))), 4),
                    "mse_raw": round(float(np.mean(err ** 2)), 4),
                    "mae_norm": round(float(np.mean(np.abs(err))) / std_tr, 4),
                    "bin_mae": [round(x, 4) for x in bins],
                    "wall_s": round(time.time() - tm, 1),
                }
            except Exception as e:
                row["methods"][name] = {"error": f"{type(e).__name__}: {str(e)[:120]}"}
            print(f"  o{oi:02d} {dates[o]} {name:14s} "
                  f"{row['methods'][name].get('mae_raw', row['methods'][name].get('error', '')[:40])} ({row['methods'][name].get('wall_s','')}s)")
        per_origin.append(row)

    # aggregates
    names = [m[0] for m in methods]
    agg = {}
    for name in names:
        rows_m = [r["methods"][name] for r in per_origin if "mae_raw" in r["methods"][name]]
        maes = [x["mae_raw"] for x in rows_m]
        norms = [x["mae_norm"] for x in rows_m]
        bins = ([round(float(np.mean([x["bin_mae"][b] for x in rows_m])), 4) for b in range(6)]
                if rows_m else [None] * 6)
        agg[name] = {"mae_raw_mean": round(float(np.mean(maes)), 4) if maes else None,
                     "mae_raw_std": round(float(np.std(maes)), 4) if maes else None,
                     "mae_norm_mean": round(float(np.mean(norms)), 4) if norms else None,
                     "horizon_bin_mae": bins,
                     "below_incumbent_1_9781_origins": int(sum(1 for m in maes if m < 1.9781)),
                     "n_origins": len(rows_m)}
    # win-rate matrix (A better than B on how many origins)
    wr = {}
    for a in names:
        wr[a] = {}
        for b in names:
            if a == b:
                continue
            wa = sum(1 for r in per_origin
                     if a in r["methods"] and b in r["methods"]
                     and "mae_raw" in r["methods"][a] and "mae_raw" in r["methods"][b]
                     and r["methods"][a]["mae_raw"] < r["methods"][b]["mae_raw"])
            wr[a][b] = wa
    res = {
        "protocol": {"H": H, "train_cap_days": CAP // 24, "mode": "sliding_fixed_360d" if sliding else "expanding",
                     "origins": [o for o in origins],
                     "fit": "expanding window, leakage-safe (fit on s[:o] only)", "context": "full history s[:o], model slices its own L",
                     "seeds": "frozen seed 42 for all randomized components",
                     "incumbent_ref": "S44 H720 MAE 1.9781 (raw scale)"},
        "data": {"file": "data/ETTh1_h1.csv", "source": "zhouhaoyi/ETDataset ETT-small ETTh1.csv (HF mirror ETDataset/ett)",
                  "n": int(N), "col": "OT", "mean": round(float(s.mean()), 3), "std": round(float(s.std()), 3),
                  "range": [str(dates[0]), str(dates[-1])]},
        "per_origin": per_origin, "aggregate": agg, "win_rate": wr, "wall_total_s": round(time.time() - t0, 1),
    }
    RESULTS_DIR.mkdir(exist_ok=True)
    json.dump(res, open(RESULTS_DIR / ("etth1_h720_multi_origin" + tag + ".json"), "w"), indent=1)

    # summary md
    lines = ["# ETTh1 H720 multi-origin (different starting points) test",
             f"\nData: {res['data']['source']}  n={N}  {res['data']['range'][0]}..{res['data']['range'][1]}  OT mean={res['data']['mean']} std={res['data']['std']}",
             f"\nProtocol: {len(origins)} disjoint 30-day origins, {'fixed 360d sliding train window' if sliding else 'expanding train window (cap 360d)'}, leakage-safe, frozen seeds.",
             "\n## Aggregate (mean over origins, raw MAE)",
             "\n| method | MAE raw | std | MAE norm | bins[0..5] (120h each) | <1.9781 |",
             "|---|---|---|---|---|---|"]
    for name in sorted([n for n in names if agg[n]["mae_raw_mean"] is not None],
                      key=lambda n: agg[n]["mae_raw_mean"]):
        a = agg[name]
        lines.append(f"| {name} | {a['mae_raw_mean']} | {a['mae_raw_std']} | {a['mae_norm_mean']} | {a['horizon_bin_mae']} | {a['below_incumbent_1_9781_origins']}/{a['n_origins']} |")
    lines.append(f"\n## Incumbent S44 H720: 1.9781 raw MAE. Best-novel check: see table.")
    open(RESULTS_DIR / ("etth1_h720_multi_origin" + tag + ".md"), "w").write("\n".join(lines))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
        ok = {n: agg[n] for n in names if agg[n]["n_origins"] > 0}
        order = sorted(ok, key=lambda n: ok[n]["mae_raw_mean"])
        ax1.bar(range(len(order)), [ok[n]["mae_raw_mean"] for n in order], align="center")
        ax1.set_xticks(range(len(order)), order, rotation=40, ha="right", fontsize=8)
        ax1.axhline(1.9781, color="r", ls="--", lw=1, label="S44 incumbent 1.9781")
        ax1.set_ylabel("MAE (raw) mean over 18 origins"); ax1.set_title("ETTh1 H720 multi-origin"); ax1.legend(fontsize=8)
        for n in ok:
            ax2.plot([120, 240, 360, 480, 600, 720], ok[n]["horizon_bin_mae"],
                     marker="o", ms=3, lw=0.8, label=n)
        ax2.set_xlabel("horizon (hours)"); ax2.set_ylabel("bin MAE (raw)"); ax2.set_title("error growth over horizon")
        ax2.legend(fontsize=7, ncols=3); ax2.grid(alpha=0.3)
        (ROOT / "plots").mkdir(exist_ok=True)
        fig.tight_layout(); fig.savefig(ROOT / "plots" / ("etth1_h720_multi_origin" + tag + ".png"), dpi=130)
        print("plot saved")
    except Exception as e:
        print("plot skipped:", repr(e)[:100])
    print(f"\nDONE in {res['wall_total_s']}s")

if __name__ == "__main__":
    main()
