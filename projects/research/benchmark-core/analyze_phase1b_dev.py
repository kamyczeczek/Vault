"""Phase 1b Dev analysis script compliant with Krok 5 instructions.

- Czas per dopasowanie per model (mediana i p95)
- Łączny czas per model vs budżet 20 min (1200 s)
- Szum między originami (zmienność inter-window r_t)
- MDE (Cluster Bootstrap B=10,000, 15 rodzin, alpha=0.05)
- Weryfikacja zadań z MASE > 3 w results/denominator_anomaly_scan.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
DRYRUN_FILE = RESULTS / "phase1b_dev_dryrun.json"
DENOM_FILE = RESULTS / "denominator_anomaly_scan.json"
OUT_FILE = RESULTS / "phase1b_dev_analysis.json"

sys.path.insert(0, str(ROOT))
from metrics import clip_relative_error
from bootstrap import cluster_bootstrap_families

def main():
    if not DRYRUN_FILE.exists():
        print(f"Brak pliku {DRYRUN_FILE}")
        return 1

    data = json.loads(DRYRUN_FILE.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    print(f"Wczytano {len(tasks)} zadań Dev z {DRYRUN_FILE.name}")

    model_names = ["SeasonalNaive", "NLinear", "DLinear"]

    # Collect per-fit times and wall times per model
    fit_times = {m: [] for m in model_names}
    task_wall_times = {m: [] for m in model_names}
    task_mases = {m: {} for m in model_names}
    task_families = {}
    task_domains = {}

    for t in tasks:
        tid = t["task_id"]
        task_families[tid] = t["family"]
        task_domains[tid] = t["domain"]
        for m in model_names:
            m_info = t["models"][m]
            task_mases[m][tid] = m_info["task_mase"]
            fits = m_info["fit_seconds"]["list"]
            fit_times[m].extend(fits)
            task_wall_times[m].append(m_info["fit_seconds"]["total"] + m_info["predict_seconds"]["total"])

    # 1. Timing analysis
    print("\n--- 1. CZAS EWALUACJI I DOPASOWAŃ PER MODEL ---")
    timing_summary = {}
    for m in model_names:
        fits_arr = np.array(fit_times[m])
        t_wall_arr = np.array(task_wall_times[m])
        sum_wall = float(np.sum(t_wall_arr))
        fit_med = float(np.median(fits_arr) * 1000)
        fit_p95 = float(np.percentile(fits_arr, 95) * 1000)
        print(f"Model {m:15s}:")
        print(f"  Średni czas dopasowania per seria: mediana = {fit_med:.3f} ms, p95 = {fit_p95:.3f} ms, max = {np.max(fits_arr)*1000:.3f} ms")
        print(f"  Czas per zadanie (wall):          mediana = {np.median(t_wall_arr):.2f} s,  p95 = {np.percentile(t_wall_arr, 95):.2f} s,  max = {np.max(t_wall_arr):.2f} s")
        print(f"  Łączny czas dla modelu:           {sum_wall:.1f} s ({sum_wall/60:.2f} min) vs budżet 20 min (1200 s) -> {'OK' if sum_wall <= 1200 else 'PRZEKROCZONY'}")

        timing_summary[m] = {
            "fit_median_ms": fit_med,
            "fit_p95_ms": fit_p95,
            "total_wall_seconds": sum_wall,
            "within_20min_budget": sum_wall <= 1200.0,
        }

    # 2. Relative Ratios & Skill Scores
    print("\n--- 2. SKILL SCORE I RELATYWNE ILORAZY vs SEASONAL NAIVE ---")
    sn_mases = task_mases["SeasonalNaive"]
    rel_ratios = {}
    task_ids = list(sn_mases.keys())
    for m in ["NLinear", "DLinear"]:
        rel_ratios[m] = {tid: clip_relative_error(task_mases[m][tid] / sn_mases[tid]) for tid in task_ids}
        r_vals = list(rel_ratios[m].values())
        gmean_r = math.exp(np.mean(np.log(r_vals)))
        skill = 1.0 - gmean_r
        print(f"Model {m:10s} vs SNaive: gmean_r = {gmean_r:.4f}, skill_score = {skill:+.4f} ({skill*100:+.2f}%)")

    # 3. Inter-window variability (natural noise between origins)
    print("\n--- 3. ZMIENNOŚĆ NATURALNA ZADAŃ MIĘDZY OKNAMI ---")
    window_variability = {}
    for m in ["NLinear", "DLinear"]:
        std_rs = []
        max_devs = []
        for t in tasks:
            tid = t["task_id"]
            sn_w = t["models"]["SeasonalNaive"]["per_window_mase"]
            m_w = t["models"][m]["per_window_mase"]
            r_windows = [clip_relative_error(mw / snw) for mw, snw in zip(m_w, sn_w)]
            std_r = float(np.std(r_windows))
            mean_r = float(np.mean(r_windows))
            std_rs.append(std_r)
            max_devs.append(max(abs(rw - mean_r) for rw in r_windows))
        print(f"Model {m:10s} szum m-oknami r_t: mediana std = {np.median(std_rs):.4f}, p95 std = {np.percentile(std_rs, 95):.4f}, max odchylenie = {np.max(max_devs):.4f}")
        window_variability[m] = {
            "median_std_across_windows": float(np.median(std_rs)),
            "p95_std_across_windows": float(np.percentile(std_rs, 95)),
            "max_single_window_deviation": float(np.max(max_devs)),
        }

    # 4. Cluster Bootstrap & MDE Analysis (B=10,000, 15 families, alpha=0.05)
    print("\n--- 4. MDE I ANALIZA BOOTSTRAP KLASTROWY (B=10,000, 15 RODZIN, alpha=0.05) ---")
    boot_nl = cluster_bootstrap_families(rel_ratios["NLinear"], task_families, n_resamples=10000, alpha=0.05, seed=42)
    boot_dl = cluster_bootstrap_families(rel_ratios["DLinear"], task_families, n_resamples=10000, alpha=0.05, seed=42)

    # Relative ratio DLinear vs NLinear
    rel_d_vs_n = {tid: clip_relative_error(task_mases["DLinear"][tid] / task_mases["NLinear"][tid]) for tid in task_ids}
    boot_d_vs_n = cluster_bootstrap_families(rel_d_vs_n, task_families, n_resamples=10000, alpha=0.05, seed=42)

    for name, boot in [("NLinear_vs_SNaive", boot_nl), ("DLinear_vs_SNaive", boot_dl), ("DLinear_vs_NLinear", boot_d_vs_n)]:
        ci_half = boot['point_estimate'] - boot['one_sided_lower_ci']
        mde80 = 2.80 * boot['bootstrap_std']
        boot['ci_halfwidth'] = ci_half
        boot['mde_80_power'] = mde80
        print(f"{name:20s}: Skill = {boot['point_estimate']:+.4f} | 95% Lower CI = {boot['one_sided_lower_ci']:+.4f} | Boot std = {boot['bootstrap_std']:.4f} | CI halfwidth = {ci_half:.4f} | MDE (80% power) = {mde80:.4f}")

    # 5. High MASE (> 3.0) Tasks Verification
    print("\n--- 5. WERYFIKACJA ZADAŃ Z MASE > 3 W DENOMINATOR ANOMALY SCAN ---")
    denom_data = json.loads(DENOM_FILE.read_text(encoding="utf-8")) if DENOM_FILE.exists() else {"tasks": []}
    denom_map = {t["task_id"]: t for t in denom_data.get("tasks", [])}

    high_mase_report = []
    for tid in task_ids:
        high_m = {m: task_mases[m][tid] for m in model_names if task_mases[m][tid] > 3.0}
        if high_m:
            denom_info = denom_map.get(tid, {})
            zero_items = sum(t_info.get("zero_error_items_any_window", 0) for t_info in denom_info.get("targets", {}).values())
            nan_items = sum(t_info.get("nan_error_items_any_window", 0) for t_info in denom_info.get("targets", {}).values())
            status = "ANOMALIA MIANOWNIKA (zero_err > 0)" if zero_items > 0 else "PRZWDIWY SYGNAŁ DANYCH (zero_err == 0)"
            print(f"  {tid:30s}: SNaive={task_mases['SeasonalNaive'][tid]:.2f}, NLinear={task_mases['NLinear'][tid]:.2f}, DLinear={task_mases['DLinear'][tid]:.2f}")
            print(f"    Skan mianownika: zero_err_items={zero_items}, nan_err_items={nan_items} -> {status}")

            high_mase_report.append({
                "task_id": tid,
                "mase_values": {m: task_mases[m][tid] for m in model_names},
                "zero_error_items_in_scan": zero_items,
                "nan_error_items_in_scan": nan_items,
                "verdict": status,
            })

    output_payload = {
        "timing_summary": timing_summary,
        "skill_scores": {
            "NLinear_vs_SNaive": boot_nl["point_estimate"],
            "DLinear_vs_SNaive": boot_dl["point_estimate"],
            "DLinear_vs_NLinear": boot_d_vs_n["point_estimate"],
        },
        "bootstrap_mde": {
            "NLinear_vs_SNaive": boot_nl,
            "DLinear_vs_SNaive": boot_dl,
            "DLinear_vs_NLinear": boot_d_vs_n,
        },
        "inter_window_variability": window_variability,
        "high_mase_tasks_verification": high_mase_report,
    }

    OUT_FILE.write_text(json.dumps(output_payload, indent=2), encoding="utf-8")
    sha256 = import_sha256(OUT_FILE)
    print(f"\nZapisano raport analizy: {OUT_FILE} (sha256: {sha256})")

def import_sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()

if __name__ == "__main__":
    main()
