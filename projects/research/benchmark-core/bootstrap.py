"""Normative bootstrap confidence interval engine for benchmark-core v2.

Compliant with PROTOCOL.md:
- Cluster bootstrap over dataset families (resampling whole families with replacement).
- Unstratified cluster bootstrap (normative decision gate).
- Stratified cluster bootstrap & i.i.d. task bootstrap (reported as sensitivity).
- B = 10,000 resamples.
- Dev Promotion (Gate 2): 1-sided 95% CI (alpha = 0.05).
- Lockbox Evaluation (Gate 3): 1-sided 98.33% CI (Bonferroni alpha = 0.05 / 3 = 0.01667).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from metrics import clip_relative_error, compute_geometric_mean, compute_skill_score


def cluster_bootstrap_families(
    task_ratios: Dict[str, float],
    task_families: Dict[str, str],
    n_resamples: int = 10000,
    alpha: float = 0.05,
    seed: int = 42,
) -> Dict[str, Any]:
    """Unstratified cluster bootstrap over dataset families.

    Resamples families with replacement; all tasks within a sampled family enter together.

    Parameters
    ----------
    task_ratios : Dict[str, float]
        Clipped relative errors r_t = MASE_candidate / MASE_reference per task.
    task_families : Dict[str, str]
        Mapping from task_id to dataset family name.
    n_resamples : int
        Number of bootstrap iterations (default 10,000 per protocol).
    alpha : float
        Significance level for 1-sided lower bound (default 0.05 for Dev, 0.01667 for Lockbox).
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    Dict[str, Any]
        Dictionary with point_estimate, lower_ci, upper_ci, and bootstrap statistics.
    """
    # Group tasks by family
    family_to_tasks: Dict[str, List[str]] = {}
    for task_id in task_ratios:
        fam = task_families[task_id]
        family_to_tasks.setdefault(fam, []).append(task_id)

    unique_families = sorted(list(family_to_tasks.keys()))
    n_families = len(unique_families)
    if n_families == 0:
        raise ValueError("Cannot bootstrap over 0 families")

    # Point estimate on actual sample
    all_r = [task_ratios[t] for t in task_ratios]
    point_skill = compute_skill_score(all_r)

    rng = np.random.default_rng(seed)
    sampled_skills = np.empty(n_resamples, dtype=np.float64)

    for b in range(n_resamples):
        # Sample families with replacement
        sampled_fam_indices = rng.integers(0, n_families, size=n_families)

        # Collect all tasks from sampled families
        bootstrap_r = []
        for idx in sampled_fam_indices:
            fam = unique_families[idx]
            tasks = family_to_tasks[fam]
            bootstrap_r.extend(task_ratios[t] for t in tasks)

        # Compute skill score on this resampled dataset
        gmean = compute_geometric_mean(bootstrap_r)
        sampled_skills[b] = 1.0 - gmean

    # 1-sided (1 - alpha) CI corresponds to quantile alpha for the lower bound
    lower_bound = float(np.percentile(sampled_skills, 100.0 * alpha))
    # 2-sided (1 - 2*alpha) CI for completeness
    two_sided_lower = float(np.percentile(sampled_skills, 100.0 * (alpha / 2.0)))
    two_sided_upper = float(np.percentile(sampled_skills, 100.0 * (1.0 - alpha / 2.0)))

    return {
        "method": "unstratified_cluster_bootstrap",
        "n_resamples": n_resamples,
        "n_families": n_families,
        "n_tasks": len(task_ratios),
        "alpha": alpha,
        "point_estimate": point_skill,
        "one_sided_lower_ci": lower_bound,
        "passes_gate": lower_bound > 0.0,
        "two_sided_ci": (two_sided_lower, two_sided_upper),
        "bootstrap_mean": float(np.mean(sampled_skills)),
        "bootstrap_std": float(np.std(sampled_skills)),
    }


def iid_task_bootstrap(
    task_ratios: Dict[str, float],
    n_resamples: int = 10000,
    alpha: float = 0.05,
    seed: int = 42,
) -> Dict[str, Any]:
    """Standard i.i.d. task bootstrap (sensitivity analysis only)."""
    tasks = list(task_ratios.keys())
    n_tasks = len(tasks)
    r_arr = np.array([task_ratios[t] for t in tasks], dtype=np.float64)

    point_skill = 1.0 - compute_geometric_mean(r_arr.tolist())

    rng = np.random.default_rng(seed)
    sampled_skills = np.empty(n_resamples, dtype=np.float64)

    for b in range(n_resamples):
        sample_indices = rng.integers(0, n_tasks, size=n_tasks)
        sub_r = r_arr[sample_indices]
        gmean = math.exp(np.mean(np.log(sub_r)))
        sampled_skills[b] = 1.0 - gmean

    lower_bound = float(np.percentile(sampled_skills, 100.0 * alpha))
    return {
        "method": "iid_task_bootstrap",
        "n_resamples": n_resamples,
        "alpha": alpha,
        "point_estimate": point_skill,
        "one_sided_lower_ci": lower_bound,
        "passes_gate": lower_bound > 0.0,
        "bootstrap_std": float(np.std(sampled_skills)),
    }


def stratified_domain_cluster_bootstrap(
    task_ratios: Dict[str, float],
    task_families: Dict[str, str],
    task_domains: Dict[str, str],
    n_resamples: int = 10000,
    alpha: float = 0.05,
    seed: int = 42,
) -> Dict[str, Any]:
    """Stratified cluster bootstrap by domain (sensitivity analysis only).

    Resamples families within each domain with replacement.
    """
    domain_to_families: Dict[str, Set[str]] = {}
    family_to_tasks: Dict[str, List[str]] = {}
    for task_id in task_ratios:
        fam = task_families[task_id]
        dom = task_domains.get(task_id, "unknown")
        domain_to_families.setdefault(dom, set()).add(fam)
        family_to_tasks.setdefault(fam, []).append(task_id)

    dom_fams = {d: sorted(list(fams)) for d, fams in domain_to_families.items()}
    rng = np.random.default_rng(seed)
    sampled_skills = np.empty(n_resamples, dtype=np.float64)

    point_skill = compute_skill_score(list(task_ratios.values()))

    for b in range(n_resamples):
        bootstrap_r = []
        for dom, fams in dom_fams.items():
            k = len(fams)
            sampled_idx = rng.integers(0, k, size=k)
            for idx in sampled_idx:
                fam = fams[idx]
                for t in family_to_tasks[fam]:
                    bootstrap_r.append(task_ratios[t])

        gmean = compute_geometric_mean(bootstrap_r)
        sampled_skills[b] = 1.0 - gmean

    lower_bound = float(np.percentile(sampled_skills, 100.0 * alpha))
    return {
        "method": "stratified_domain_cluster_bootstrap",
        "n_resamples": n_resamples,
        "alpha": alpha,
        "point_estimate": point_skill,
        "one_sided_lower_ci": lower_bound,
        "passes_gate": lower_bound > 0.0,
        "bootstrap_std": float(np.std(sampled_skills)),
    }
