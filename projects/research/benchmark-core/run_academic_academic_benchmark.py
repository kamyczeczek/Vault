from __future__ import annotations
import numpy as np
import json
import time
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

from members.state_space_hybrid import StateSpaceDictionaryHybrid
from members.big_dict_elm import BigDictELM
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.knn_feature_forecaster import KNNFeatureForecaster
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft, fit_theta, pred_theta, fit_arima, pred_arima, fit_ets, pred_ets

# Import task generators from bench.py or define them
from bench import TASKS, get_series

def run_academic_benchmark():
    print("=== Running Ultimate Academic SOTA Benchmarking Suite ===")

    # Select key representative scientific benchmark tasks
    selected_tasks = ["thomas_H24", "sunspot_H24", "etth1_H96", "multiscale_H96", "seasonal_H48"]

    models_def = {
        "BigDictELM": (lambda tr, h: BigDictELM(input_length=96).fit(tr, h), lambda m, h, hist: m.predict(hist)[:h]),
        "AMR-FBS": (lambda tr, h: fit_amr_fbs(tr, h), lambda m, h, hist: pred_amr_fbs(m, h)[:h]),
        "StateSpaceHybrid": (lambda tr, h: StateSpaceDictionaryHybrid(input_length=96).fit(tr, h), lambda m, h, hist: m.predict(hist, h)),
        "KNNForecaster": (lambda tr, h: KNNFeatureForecaster(input_length=96).fit(tr, h), lambda m, h, hist: m.predict_hist(hist)[:h]),
        "DLinear": (lambda tr, h: fit_dlinear(tr, h), lambda m, h, hist: pred_dlinear(m, hist)[:h]),
        "SpectralFFT": (lambda tr, h: fit_fft(tr, h), lambda m, h, hist: pred_fft(m, hist)[:h]),
        "Theta": (lambda tr, h: fit_theta(tr, h), lambda m, h, hist: pred_theta(m, hist)[:h]),
        "ARIMA": (lambda tr, h: fit_arima(tr, h), lambda m, h, hist: pred_arima(m, hist)[:h]),
        "ETS": (lambda tr, h: fit_ets(tr, h), lambda m, h, hist: pred_ets(m, hist)[:h]),
    }

    results = {}

    for task_name, H, domain in TASKS:
        if task_name not in selected_tasks:
            continue

        print(f"\n--- Benchmark Task: {task_name} (H={H}, Domain={domain}) ---")
        series = get_series(task_name)
        train = series[:-H]
        test = series[-H:]

        task_res = {}
        for name, (fit_fn, pred_fn) in models_def.items():
            t0 = time.time()
            try:
                model = fit_fn(train, H)
                pred = pred_fn(model, H, train[-96:])
                pred = np.asarray(pred, dtype=float).ravel()[:H]
                mae = float(np.mean(np.abs(pred - test)))
                dt = time.time() - t0
                task_res[name] = {"MAE": mae, "time": dt}
                print(f"  {name:18s} : MAE {mae:.4f} ({dt:.2f}s)")
            except Exception as e:
                print(f"  {name:18s} : ERROR ({e})")
                task_res[name] = {"MAE": None, "error": str(e)}

        results[task_name] = {"H": H, "domain": domain, "models": task_res}

    with open("results_academic_sota.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved academic SOTA benchmark results to results_academic_sota.json")

    # Ingest into knowledge graph corpus
    corpus_path = pathlib.Path("../agentic-research-lab/knowledge/corpus/1001_academic_sota_benchmark_results.md")
    corpus_path.parent.mkdir(parents=True, exist_ok=True)

    md = f"""---
id: 1001_academic_sota_benchmark_results
title: "Academic SOTA Benchmarking Suite vs. Invented Models"
tags: [ts-diverse, academic-sota, benchmarking, models, results]
---

# Academic SOTA Benchmarking Results

Generated on: 2026-09-21
Framework: `benchmark-core`

## Comparative Performance Summary
"""
    for task, info in results.items():
        md += f"\n### Task: `{task}` (H={info['H']}, Domain={info['domain']})\n"
        models_sorted = sorted([(m, d['MAE']) for m, d in info['models'].items() if d['MAE'] is not None], key=lambda x: x[1])
        for m, mae in models_sorted:
            md += f"- `{m}`: MAE **{mae:.4f}**\n"

    corpus_path.write_text(md, encoding="utf-8")
    print(f"Successfully wrote academic benchmark results to corpus: {corpus_path}")

if __name__ == "__main__":
    run_academic_benchmark()
