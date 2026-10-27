"""PROCESS/run_gates.py — design-phase gate checks for sub-experiments.

Usage:
    python PROCESS/run_gates.py --all
    python PROCESS/run_gates.py --experiment s41
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

H720_ROOT = Path(__file__).resolve().parent.parent
SUB_DIR = H720_ROOT / "sub_experiments"
CONTEXT = H720_ROOT / "CONTEXT.md"


def check_s41_design() -> dict:
    """Gate checks for S-41 RFF-MoE design."""
    exp_dir = SUB_DIR / "rff_ensemble_s41"
    design = exp_dir / "S41_DESIGN.md"
    rolling = exp_dir / "rolling_arm.py"
    results = exp_dir / "results_s41.json"

    status = {
        "experiment": "S-41",
        "directory_exists": exp_dir.is_dir(),
        "design_exists": design.exists(),
        "rolling_arm_exists": rolling.exists(),
        "results_exists": results.exists(),
    }

    if design.exists():
        text = design.read_text(encoding="utf-8")
        required_sections = [
            "## 1. Expert Pool",
            "## 2. Feature Encoder Spec",
            "## 3. Router Design",
            "## 4. Stack Head (optional)",
            "## 6. Acceptance Criteria",
        ]
        status["design_sections"] = {s: s in text for s in required_sections}
        status["design_complete"] = all(status["design_sections"].values())
    else:
        status["design_sections"] = {}
        status["design_complete"] = False

    if rolling.exists():
        try:
            source = rolling.read_text(encoding="utf-8")
            ast.parse(source)
            status["rolling_arm_valid_python"] = True
        except SyntaxError as e:
            status["rolling_arm_valid_python"] = False
            status["rolling_arm_error"] = str(e)
    else:
        status["rolling_arm_valid_python"] = False

    if CONTEXT.exists():
        text = CONTEXT.read_text(encoding="utf-8")
        status["context_has_s41"] = "## Sub-Experiment: RFF-MoE Ensemble (S-41)" in text
    else:
        status["context_has_s41"] = False

    status["pass"] = (
        status["directory_exists"]
        and status["design_exists"]
        and status.get("design_complete", False)
        and status.get("rolling_arm_valid_python", False)
        and status["context_has_s41"]
    )

    return status


def check_s44_design() -> dict:
    """Gate checks for S-44 blend-promotion re-registration (PROMOTED)."""
    exp_dir = SUB_DIR / "blend_promotion_s44"
    design = exp_dir / "S44_DESIGN.md"
    rolling = exp_dir / "rolling_arm.py"
    results = exp_dir / "results_s44.json"

    status = {
        "experiment": "S-44",
        "directory_exists": exp_dir.is_dir(),
        "design_exists": design.exists(),
        "rolling_arm_exists": rolling.exists(),
        "results_exists": results.exists(),
    }

    if design.exists():
        text = design.read_text(encoding="utf-8")
        required_sections = [
            "## 2. Gate-semantics declaration",
            "### D2 — Binding gate is blend-based",
            "## 4. Acceptance & close conditions",
            "## 5. Parity requirements",
        ]
        status["design_sections"] = {s: s in text for s in required_sections}
        status["design_complete"] = all(status["design_sections"].values())
    else:
        status["design_sections"] = {}
        status["design_complete"] = False

    if rolling.exists():
        try:
            source = rolling.read_text(encoding="utf-8")
            ast.parse(source)
            status["rolling_arm_valid_python"] = True
        except SyntaxError as e:
            status["rolling_arm_valid_python"] = False
            status["rolling_arm_error"] = str(e)
    else:
        status["rolling_arm_valid_python"] = False

    if results.exists():
        try:
            data = json.loads(results.read_text(encoding="utf-8"))
            parity = data.get("parity") or {}
            gate = data.get("binding_gate") or {}
            status["results_verdict"] = data.get("verdict")
            status["results_parity_all_pass"] = bool(parity.get("all_pass"))
            status["results_binding_all_pass"] = bool(gate.get("all_binding_pass"))
            checks = parity.get("checks")
            if isinstance(checks, list):
                status["results_parity_checks"] = len(checks)
        except Exception as e:
            status["results_parse_error"] = str(e)

    if CONTEXT.exists():
        text = CONTEXT.read_text(encoding="utf-8")
        status["context_has_s44"] = "## Sub-Experiment: Blend-Promotion Re-registration (S-44)" in text
    else:
        status["context_has_s44"] = False

    status["pass"] = (
        status["directory_exists"]
        and status["design_exists"]
        and status.get("design_complete", False)
        and status.get("rolling_arm_valid_python", False)
        and status["results_exists"]
        and status.get("results_verdict") == "PROMOTED"
        and status.get("results_parity_all_pass", False)
        and status.get("results_binding_all_pass", False)
        and status["context_has_s44"]
    )

    return status


def check_s40_design() -> dict:
    """Gate checks for S-40 (completed reference)."""
    exp_dir = SUB_DIR / "calendar_aware_linear_s40"
    design = exp_dir / "S40_DESIGN.md"
    rolling = exp_dir / "rolling_arm.py"
    results = exp_dir / "results_s40.json"

    status = {
        "experiment": "S-40",
        "directory_exists": exp_dir.is_dir(),
        "design_exists": design.exists(),
        "rolling_arm_exists": rolling.exists(),
        "results_exists": results.exists(),
    }

    if results.exists():
        try:
            data = json.loads(results.read_text(encoding="utf-8"))
            status["test_mae"] = data.get("test_mae") or data.get("full_mae")
            status["disjoint_4"] = data.get("disjoint_4")
        except Exception:
            pass

    status["pass"] = status["directory_exists"] and status["results_exists"]
    return status


def check_s39_design() -> dict:
    """Gate checks for S-39 (completed reference)."""
    exp_dir = SUB_DIR / "ztl_moe_s39"
    design = exp_dir / "DESIGN.md"
    results = exp_dir / "results_s39.json"

    status = {
        "experiment": "S-39",
        "directory_exists": exp_dir.is_dir(),
        "design_exists": design.exists(),
        "results_exists": results.exists(),
    }

    if results.exists():
        try:
            data = json.loads(results.read_text(encoding="utf-8"))
            status["test_mae"] = data.get("test_mae") or data.get("full_mae")
        except Exception:
            pass

    status["pass"] = status["directory_exists"] and status["results_exists"]
    return status


def check_tsfm_phase2() -> dict:
    """Gate checks for Omega-gated TSFM ensemble Phase 2."""
    exp_dir = SUB_DIR / "spectral_omega_gate"
    adapter = exp_dir / "tsfm_adapter.py"
    rolling = exp_dir / "rolling_arm_phase2.py"
    results = exp_dir / "results_tsfm_phase2.json"
    phase1 = exp_dir / "results_omega.json"

    status = {
        "experiment": "TSFM-Phase2",
        "adapter_exists": adapter.exists(),
        "rolling_arm_exists": rolling.exists(),
        "results_exists": results.exists(),
        "phase1_results_exists": phase1.exists(),
    }

    for py_file in [adapter, rolling]:
        key = py_file.name
        if py_file.exists():
            try:
                source = py_file.read_text(encoding="utf-8")
                ast.parse(source)
                status[f"{key}_valid_python"] = True
            except SyntaxError as e:
                status[f"{key}_valid_python"] = False
                status[f"{key}_error"] = str(e)
        else:
            status[f"{key}_valid_python"] = False

    if results.exists():
        try:
            data = json.loads(results.read_text(encoding="utf-8"))
            status["call_rate"] = data.get("gate", {}).get("call_rate")
        except Exception as e:
            status["results_parse_error"] = str(e)

    status["pass"] = (
        status.get("adapter_exists", False)
        and status.get("rolling_arm_exists", False)
        and status.get(f"{adapter.name}_valid_python", False)
        and status.get(f"{rolling.name}_valid_python", False)
        and status.get("phase1_results_exists", False)
    )
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description="Run design gates for sub-experiments")
    parser.add_argument("--all", action="store_true", help="Run all gate checks")
    parser.add_argument(
        "--experiment",
        choices=["s44", "s41", "s40", "s39", "tsfm_phase2"],
        help="Run specific experiment gate",
    )
    args = parser.parse_args()

    if args.all:
        experiments = ["s44", "s41", "s40", "s39", "tsfm_phase2"]
    elif args.experiment:
        experiments = [args.experiment]
    else:
        parser.print_help()
        return 1

    results = {}
    for exp in experiments:
        if exp == "s44":
            results["S-44"] = check_s44_design()
        elif exp == "s41":
            results["S-41"] = check_s41_design()
        elif exp == "s40":
            results["S-40"] = check_s40_design()
        elif exp == "s39":
            results["S-39"] = check_s39_design()
        elif exp == "tsfm_phase2":
            results["TSFM-Phase2"] = check_tsfm_phase2()

    print(json.dumps(results, indent=2))

    all_pass = all(v.get("pass", False) for v in results.values())
    if not all_pass:
        print("\nFAIL: one or more gates failed")
        return 1
    print("\nPASS: all gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
