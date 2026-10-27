"""BigDictELM component ablation study."""
from __future__ import annotations
import json
import time
import numpy as np
from pathlib import Path

# Reuse bench helpers
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from members.big_dict_elm import BigDictELM
from bench import gen_multiscale, gen_thomas, get_sunspot, gen_seasonal

TASKS = {
    "multiscale_H48": (gen_multiscale, 48),
    "thomas_H24": (gen_thomas, 24),
    "seasonal_H48": (gen_seasonal, 48),
}

# Filter groups to test individually (by index into _filter_bank_one output)
# Index map: 0=identity, 1-4=MA3/6/12/24, 5-6=EMA0.3/0.7, 7=diff1, 8=diff2,
#            9=HP12, 10=HP24, 11-18=wavelet approx/detail (db4+s4m4 × levels2)
FILTER_GROUPS = [
    ("identity",       [0]),
    ("ma3",            [1]),
    ("ma6",            [2]),
    ("ma12",           [3]),
    ("ma24",           [4]),
    ("ema0.3",         [5]),
    ("ema0.7",         [6]),
    ("diff1",          [7]),
    ("diff2",          [8]),
    ("hp12",           [9]),
    ("hp24",           [10]),
    ("wavelets",       list(range(11, 19))),
    # Key combos
    ("ma12+hp12",      [3, 9]),
    ("ma24+hp24",      [4, 10]),
    ("ma_shorts",      [1, 2]),
    ("ma_longs",       [3, 4]),
    ("all_linear",     list(range(0, 11))),  # everything except wavelets
]

ACT_TYPES = ["cos", "rbf", "hybrid"]


def run_task(task_name, series_fn, H):
    """Run full bench on one task. Returns dict: model_key -> MAE."""
    series = series_fn()
    train = series[:2000]
    test = series[2000:]

    results = {}
    t0 = time.time()

    # Baselines from harness.log (re-run for comparison)
    # --- individual filters ---
    for fname, idx in FILTER_GROUPS:
        m = BigDictELM(input_length=96, hidden=384, act_type="cos", alpha=100, seed=42,
                       wavelet_bank=("db4",), levels=1, use_packet=False)
        # Monkey-patch _bank to only return selected groups
        orig_bank = m._bank
        def sel_bank(xa):
            feats = orig_bank(xa)
            return [feats[i] for i in idx]
        m._bank = sel_bank
        try:
            m.fit(train, horizon=H)
            pred = m.predict_hist(series[2000-H:2000])
            mae = float(np.mean(np.abs(pred - test[:len(pred)])))
            results[f"filter:{fname}"] = round(mae, 4)
        except Exception as e:
            results[f"filter:{fname}"] = f"ERR:{e}"

    # Activation type ablation (full filter bank)
    for act in ACT_TYPES:
        m = BigDictELM(input_length=96, hidden=384, act_type=act, alpha=100, seed=42)
        try:
            m.fit(train, horizon=H)
            pred = m.predict_hist(series[2000-H:2000])
            mae = float(np.mean(np.abs(pred - test[:len(pred)])))
            results[f"act:{act}"] = round(mae, 4)
        except Exception as e:
            results[f"act:{act}"] = f"ERR:{e}"

    # Full BigDict (reference)
    m_full = BigDictELM(input_length=96, hidden=384, act_type="hybrid", alpha=100, seed=42)
    m_full.fit(train, horizon=H)
    pred_full = m_full.predict_hist(series[2000-H:2000])
    results["FULL"] = round(float(np.mean(np.abs(pred_full - test[:len(pred_full)]))), 4)

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"{task_name} ({H})  [{elapsed:.1f}s]")
    print(f"{'='*60}")
    for k, v in sorted(results.items(), key=lambda x: (x[1] if isinstance(x[1], float) else 999)):
        tag = " ***" if isinstance(v, float) and v == min(r for r in results.values() if isinstance(r, float)) else ""
        print(f"  {k:25s}  MAE={v}{tag}")
    return results, elapsed


def main():
    all_results = {}
    total_time = 0
    for name, (fn, H) in TASKS.items():
        res, t = run_task(name, fn, H)
        all_results[name] = {"results": res, "time_s": round(t, 1)}
        total_time += t
    all_results["_meta"] = {"total_time_s": round(total_time, 1), "tasks": list(TASKS.keys())}

    out = Path("results_bigdict_ablation.json")
    out.write_text(json.dumps(all_results, indent=2))
    print(f"\nResults saved to {out}")
    print(f"Total wall time: {total_time:.1f}s")


if __name__ == "__main__":
    main()
