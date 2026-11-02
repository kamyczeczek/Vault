"""Normative metrics and evaluation engine for benchmark-core v2.

Compliant with fev 0.10.0:
- MASE scaling with task seasonality m
- Relative error r_t = MASE_model / MASE_SNaive
- Clipping to [0.01, 100.0]
- Skill score = 1 - gmean(r_t)
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


FEV_CLIP_MIN = 0.01
FEV_CLIP_MAX = 100.0


def compute_in_sample_seasonal_error(y_past: np.ndarray, seasonality: int) -> float:
    """Compute the in-sample mean absolute seasonal difference for a series.

    y_past: 1D array of historical target observations.
    seasonality: period m.
    """
    if len(y_past) <= seasonality:
        return 0.0
    diff = np.abs(y_past[seasonality:] - y_past[:-seasonality])
    valid = diff[~np.isnan(diff)]
    if len(valid) == 0:
        return 0.0
    return float(np.mean(valid))


def compute_mase(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    seasonal_error: float,
    epsilon: float = 1e-8,
) -> float:
    """Compute Mean Absolute Scaled Error (MASE) given ground truth, forecast, and seasonal error.

    If seasonal_error <= epsilon, raises ZeroDivisionError or returns nan depending on policy.
    """
    if seasonal_error <= epsilon:
        raise ZeroDivisionError(f"Seasonal error {seasonal_error} is <= epsilon {epsilon}")

    mae = float(np.mean(np.abs(y_true - y_pred)))
    return mae / seasonal_error


def clip_relative_error(r: float, min_val: float = FEV_CLIP_MIN, max_val: float = FEV_CLIP_MAX) -> float:
    """Clip relative error r to FEV normative range [0.01, 100.0]."""
    if math.isnan(r) or r <= 0:
        return max_val
    return max(min_val, min(max_val, r))


def compute_geometric_mean(values: List[float]) -> float:
    """Compute geometric mean of positive values stably via log-sum."""
    if not values:
        return float("nan")
    log_sum = sum(math.log(v) for v in values)
    return math.exp(log_sum / len(values))


def compute_skill_score(rel_errors: List[float]) -> float:
    """Skill score = 1 - geometric_mean(clipped_relative_errors)."""
    clipped = [clip_relative_error(r) for r in rel_errors]
    gmean = compute_geometric_mean(clipped)
    return 1.0 - gmean


def evaluate_task_ratios(
    model_mases: Dict[str, float],
    baseline_mases: Dict[str, float],
) -> Dict[str, float]:
    """Compute clipped relative errors r_t = model_mase / baseline_mase for each task."""
    ratios = {}
    for task_id, m_val in model_mases.items():
        b_val = baseline_mases.get(task_id)
        if b_val is None or b_val <= 0:
            raise ValueError(f"Baseline MASE for task '{task_id}' missing or non-positive: {b_val}")
        r = m_val / b_val
        ratios[task_id] = clip_relative_error(r)
    return ratios


def aggregate_benchmark_summary(
    task_ratios: Dict[str, float],
    task_domains: Dict[str, str],
) -> Dict[str, Any]:
    """Produce comprehensive summary metrics across tasks and domains.

    Computes:
    - skill_score
    - geometric_mean_r
    - median_r
    - win_rate (proportion with r < 1.0)
    - domain_geometric_means
    - worst_domain (highest gmean r)
    - worst_task (highest r)
    """
    tasks = list(task_ratios.keys())
    if not tasks:
        raise ValueError("Cannot summarize empty task ratios")

    r_vals = [task_ratios[t] for t in tasks]
    gmean_r = compute_geometric_mean(r_vals)
    skill = 1.0 - gmean_r
    median_r = float(np.median(r_vals))
    win_rate = float(np.mean([1.0 if r < 1.0 else 0.0 for r in r_vals]))

    # Domain aggregations
    domain_to_r: Dict[str, List[float]] = {}
    for t, r in task_ratios.items():
        dom = task_domains.get(t, "unknown")
        domain_to_r.setdefault(dom, []).append(r)

    domain_gmeans = {dom: compute_geometric_mean(vals) for dom, vals in domain_to_r.items()}

    # Find worst domain and worst task
    worst_dom = max(domain_gmeans.items(), key=lambda kv: kv[1])[0]
    worst_task = max(task_ratios.items(), key=lambda kv: kv[1])[0]

    return {
        "skill_score": skill,
        "geometric_mean_r": gmean_r,
        "median_r": median_r,
        "win_rate": win_rate,
        "domain_gmeans": domain_gmeans,
        "worst_domain": worst_dom,
        "worst_domain_gmean": domain_gmeans[worst_dom],
        "worst_task": worst_task,
        "worst_task_r": task_ratios[worst_task],
        "total_tasks": len(tasks),
    }
