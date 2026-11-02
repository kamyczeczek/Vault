"""Manifest and dataset split definitions for benchmark-core v2.

Normative reference: benchmark-core/PROTOCOL.md
Tasks originate from fev 0.10.0 and the fev-bench publication (arXiv:2509.26468).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Set

MANIFEST_VERSION = "2.0.0"

# The 7 normative FEV domains (Appendix E, Table 15 & Appendix A, Tables 6-12)
FEV_DOMAINS = [
    "cloud",
    "energy",
    "healthcare",
    "nature",
    "retail",
    "econ",
    "mobility",
]

# The 15 families in Dev (fev-bench-mini) and their domain mapping
DEV_FAMILY_TO_DOMAIN: Dict[str, str] = {
    "boomlet": "cloud",
    "bizitobs": "cloud",
    "epf": "energy",
    "ETT": "energy",
    "proenfo_gfc": "energy",
    "solar": "energy",
    "hospital_admissions": "healthcare",
    "uk_covid": "healthcare",
    "jena_weather": "nature",
    "uci_air_quality": "nature",
    "rohlik": "retail",
    "rossmann": "retail",
    "us_consumption": "econ",
    "world_co2_emissions": "econ",
    "M_DENSE": "mobility",
}

# Prefix patterns to map dataset_config to family
DEV_FAMILY_PATTERNS: Dict[str, str] = {
    "boomlet": "boomlet_",
    "bizitobs": "bizitobs_",
    "epf": "epf_",
    "ETT": "ETT_",
    "proenfo_gfc": "proenfo_gfc",
    "solar": "solar_",
    "hospital_admissions": "hospital_admissions_",
    "uk_covid": "uk_covid_",
    "jena_weather": "jena_weather_",
    "uci_air_quality": "uci_air_quality_",
    "rohlik": "rohlik_",
    "rossmann": "rossmann_",
    "us_consumption": "us_consumption_",
    "world_co2_emissions": "world_co2_emissions",
    "M_DENSE": "M_DENSE_",
}

# Lockbox families domain mapping
LOCKBOX_FAMILY_TO_DOMAIN: Dict[str, str] = {
    "entsoe": "energy",
    "ercot": "energy",
    "redset": "energy",
    "kdd_cup_2022": "energy",
    "restaurant": "retail",
    "hermes": "retail",
    "walmart": "retail",
    "m5": "retail",
    "hierarchical_sales": "retail",
    "favorita_stores": "retail",
    "favorita_transactions": "retail",
    "hospital": "healthcare",
    "ecdc_ili": "healthcare",
    "LOOP_SEATTLE": "mobility",
    "SZ_TAXI": "mobility",
    "australian_tourism": "econ",
    "world_tourism": "econ",
    "world_life_expectancy": "econ",
    "fred_md": "econ",
    "fred_qd": "econ",
    "gvar": "econ",
}


def classify_family(config_name: str) -> str:
    """Map a dataset_config string to its root dataset family."""
    for fam, prefix in DEV_FAMILY_PATTERNS.items():
        if config_name.startswith(prefix) or config_name == prefix:
            return fam

    # Lockbox family matching
    lockbox_prefixes = [
        ("LOOP_SEATTLE", "LOOP_SEATTLE_"),
        ("SZ_TAXI", "SZ_TAXI_"),
        ("entsoe", "entsoe_"),
        ("ercot", "ercot_"),
        ("favorita_stores", "favorita_stores_"),
        ("favorita_transactions", "favorita_transactions_"),
        ("fred_md", "fred_md_"),
        ("fred_qd", "fred_qd_"),
        ("kdd_cup_2022", "kdd_cup_2022_"),
        ("m5", "m5_"),
        ("redset", "redset_"),
        ("hierarchical_sales", "hierarchical_sales_"),
    ]
    for fam, prefix in lockbox_prefixes:
        if config_name.startswith(prefix):
            return fam

    exact_matches = {
        "restaurant": "restaurant",
        "hermes": "hermes",
        "walmart": "walmart",
        "hospital": "hospital",
        "australian_tourism": "australian_tourism",
        "world_tourism": "world_tourism",
        "world_life_expectancy": "world_life_expectancy",
        "ecdc_ili": "ecdc_ili",
        "gvar": "gvar",
    }
    if config_name in exact_matches:
        return exact_matches[config_name]

    return config_name


def classify_domain(family: str) -> str:
    """Map a family to its primary domain."""
    if family in DEV_FAMILY_TO_DOMAIN:
        return DEV_FAMILY_TO_DOMAIN[family]
    if family in LOCKBOX_FAMILY_TO_DOMAIN:
        return LOCKBOX_FAMILY_TO_DOMAIN[family]
    return "unknown"


def select_window_indices(num_windows: int, window_budget: int = 3) -> List[int]:
    """Select exactly the last window_budget evaluation windows (index rule [-3:])."""
    if num_windows <= window_budget:
        return list(range(num_windows))
    return list(range(num_windows - window_budget, num_windows))


def _task_kwargs(t: Dict[str, Any]) -> Dict[str, Any]:
    """Exact kwargs to reconstruct this task with fev.Task.

    Metric is forced to MASE (PROTOCOL.md §3) and quantile levels dropped, so
    the runner produces point forecasts only. The raw YAML dict is kept under
    `source_yaml` for provenance.
    """
    kwargs = dict(t)
    kwargs["eval_metric"] = "MASE"
    kwargs["extra_metrics"] = []
    kwargs["quantile_levels"] = []
    kwargs.pop("dataset_config", None)
    kwargs["dataset_config"] = t.get("dataset_config")
    return kwargs


def build_manifest(mini_tasks: List[Dict[str, Any]], full_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build the complete, normative manifest from raw task definitions."""
    dev_configs = set(t["dataset_config"] for t in mini_tasks)

    # 1. Dev tasks (20 tasks, fev-bench-mini)
    dev_tasks = []
    for idx, t in enumerate(mini_tasks):
        cfg = t["dataset_config"]
        fam = classify_family(cfg)
        domain = classify_domain(fam)
        num_w = int(t.get("num_windows", 1))
        windows = select_window_indices(num_w, 3)

        dev_tasks.append({
            "task_id": f"dev_{idx:02d}_{cfg}",
            "dataset_config": cfg,
            "dataset_path": t.get("dataset_path", "autogluon/fev_datasets"),
            "family": fam,
            "domain": domain,
            "horizon": int(t["horizon"]),
            "seasonality": int(t["seasonality"]),
            "num_windows": num_w,
            "window_indices": windows,
            "target": t.get("target"),
            "eval_metric": "MASE",
            "task_kwargs": _task_kwargs(t),
        })

    dev_families = set(t["family"] for t in dev_tasks)

    # 2. Sibling quarantine & Lockbox tasks from full_tasks
    quarantine_tasks = []
    lockbox_tasks = []

    # Identify which full tasks match dev tasks exactly. The signature must be
    # the full task identity (config, target, horizon, windows, seasonality):
    # a 3-field signature collides on uk_covid_nation_1D, which appears twice in
    # the full list with the same target+horizon but different seasonality, and
    # would silently swallow a sibling into the dev set.
    dev_signatures = set(
        (t["dataset_config"], str(t.get("target")), int(t["horizon"]),
         int(t.get("num_windows", 1)), int(t["seasonality"]))
        for t in mini_tasks
    )

    for idx, t in enumerate(full_tasks):
        cfg = t["dataset_config"]
        fam = classify_family(cfg)
        domain = classify_domain(fam)
        num_w = int(t.get("num_windows", 1))
        windows = select_window_indices(num_w, 3)

        sig = (cfg, str(t.get("target")), int(t["horizon"]),
               int(t.get("num_windows", 1)), int(t["seasonality"]))
        is_dev = sig in dev_signatures

        task_entry = {
            "task_id": f"task_{idx:02d}_{cfg}",
            "dataset_config": cfg,
            "dataset_path": t.get("dataset_path", "autogluon/fev_datasets"),
            "family": fam,
            "domain": domain,
            "horizon": int(t["horizon"]),
            "seasonality": int(t["seasonality"]),
            "num_windows": num_w,
            "window_indices": windows,
            "target": t.get("target"),
            "eval_metric": "MASE",
            "task_kwargs": _task_kwargs(t),
        }

        if is_dev:
            continue
        elif fam in dev_families:
            task_entry["quarantine_reason"] = f"Sibling of dev family '{fam}'"
            quarantine_tasks.append(task_entry)
        else:
            lockbox_tasks.append(task_entry)

    manifest = {
        "version": MANIFEST_VERSION,
        "protocol": "fev-v2-generalization",
        "counts": {
            "dev_tasks": len(dev_tasks),
            "dev_families": len(dev_families),
            "quarantine_tasks": len(quarantine_tasks),
            "lockbox_tasks": len(lockbox_tasks),
            "lockbox_families": len(set(t["family"] for t in lockbox_tasks)),
        },
        "domains": FEV_DOMAINS,
        "dev_tasks": dev_tasks,
        "unused_sibling_quarantine": quarantine_tasks,
        "lockbox_tasks": lockbox_tasks,
    }

    # Verify integrity before returning
    verify_manifest(manifest)
    return manifest


def verify_manifest(manifest: Dict[str, Any]) -> None:
    """Assert all normative invariants on the manifest."""
    dev_tasks = manifest["dev_tasks"]
    lockbox_tasks = manifest["lockbox_tasks"]
    quarantine = manifest["unused_sibling_quarantine"]

    assert len(dev_tasks) == 20, f"Dev tasks must be exactly 20, got {len(dev_tasks)}"

    dev_families = set(t["family"] for t in dev_tasks)
    lockbox_families = set(t["family"] for t in lockbox_tasks)

    assert len(dev_families) == 15, f"Dev families must be exactly 15, got {len(dev_families)}"

    # Hard disjointness gate
    overlap = dev_families.intersection(lockbox_families)
    assert not overlap, f"Dev and Lockbox families must not overlap! Found: {overlap}"

    # ETT must not be in Lockbox
    assert "ETT" not in lockbox_families, "ETT is strictly forbidden in Lockbox"

    # All Dev tasks must have an assigned domain from the 7 domains
    for t in dev_tasks:
        assert t["domain"] in FEV_DOMAINS, f"Invalid domain '{t['domain']}' for dev task {t['task_id']}"
        assert len(t["window_indices"]) == min(3, t["num_windows"]), (
            f"Window indices must be last 3 (or all if <3), got {t['window_indices']}"
        )

    # All quarantine tasks must belong to dev families
    for q in quarantine:
        assert q["family"] in dev_families, (
            f"Quarantine task {q['task_id']} family '{q['family']}' not in dev families"
        )


def compute_manifest_sha256(manifest: Dict[str, Any]) -> str:
    """Compute deterministic SHA-256 hash of canonical manifest JSON."""
    raw = json.dumps(manifest, sort_keys=True, indent=None, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
