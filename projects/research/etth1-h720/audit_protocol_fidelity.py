#!/usr/bin/env python3
"""Protocol fidelity audit for S49 ETTh1 H720 line.

Computes actual values from artifacts and verifies ADR matches them.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def extract_declared_origins(text: str) -> int:
    """Extract W=20 from pre-registration design doc."""
    m = re.search(r"W\s*=\s*(\d+)\s*locked eval origins", text, re.IGNORECASE)
    if not m:
        m = re.search(r"W=(\d+)\s*locked eval", text, re.IGNORECASE)
    if not m:
        m = re.search(r"(\d+)\s*locked eval origins", text, re.IGNORECASE)
    if not m:
        raise ValueError("Could not extract declared origins count from DESIGN.md")
    return int(m.group(1))


def extract_declared_seeds(text: str) -> int:
    """Extract 5 seeds from pre-registration design doc."""
    m = re.search(r"(\d+)\s*seeds", text, re.IGNORECASE)
    if not m:
        raise ValueError("Could not extract declared seeds count from DESIGN.md")
    return int(m.group(1))


def extract_executed_origins(json_path: Path) -> int:
    """Count origins in the locked evaluation JSON (per_origin array)."""
    d = json.loads(read_text(json_path))
    return len(d["per_origin"])


def extract_main_table_seed(json_path: Path) -> int:
    """Extract the single seed used in main evaluation tables (protocol.seed)."""
    d = json.loads(read_text(json_path))
    return d["protocol"]["seed"]


def extract_g4_seeds(json_path: Path) -> list[int]:
    """Extract the list of seeds used in G4 diagnostic."""
    d = json.loads(read_text(json_path))
    return d["seeds"]


def extract_s44_origins() -> int:
    """Extract S44 origins count from archived S44 design."""
    s44_design = Path("projects/_archive/ts-ml-experiments/h720/sub_experiments/blend_promotion_s44/S44_DESIGN.md")
    if s44_design.is_file():
        text = read_text(s44_design)
        m = re.search(r"MAE_full\((\d+)\)", text)
        if m:
            return int(m.group(1))
    # Fallback to measured gate semantics doc
    measured = Path("projects/_archive/agentic-research-lab/knowledge/raw/measured_gate_semantics_s43.md")
    if measured.is_file():
        text = read_text(measured)
        m = re.search(r"(\d+)-origin mean", text)
        if m:
            return int(m.group(1))
    raise ValueError("Could not extract S44 origins count")


def check_adr_contains_values(adr_path: Path, values: dict) -> dict:
    """Verify ADR contains all required computed values."""
    text = read_text(adr_path)
    missing = []
    for key, val in values.items():
        if str(val) not in text:
            missing.append(f"{key}={val}")
    return {"ok": len(missing) == 0, "missing": missing}


def main() -> int:
    design = ROOT / "LONGTERM_ETTH1_H720_DESIGN.md"
    amr_json = ROOT / "results" / "etth1_h720_amr24168_weekly.json"
    g4_json = ROOT / "results" / "etth1_h720_amr24168_g4.json"
    adr = ROOT / "docs" / "adr" / "0001-s49-closeout-and-protocol-discrepancies.md"

    # Compute from artifacts
    declared_origins = extract_declared_origins(read_text(design))
    declared_seeds = extract_declared_seeds(read_text(design))
    executed_origins = extract_executed_origins(amr_json)
    main_seed = extract_main_table_seed(amr_json)
    g4_seeds = extract_g4_seeds(g4_json)
    s44_origins = extract_s44_origins()

    print(f"Declared origins (pre-reg): {declared_origins}")
    print(f"Declared seeds (pre-reg):   {declared_seeds}")
    print(f"Executed origins (JSON):    {executed_origins}")
    print(f"Main table seed:            {main_seed}")
    print(f"G4 diagnostic seeds:        {g4_seeds}")
    print(f"S44 origins (blend):        {s44_origins}")

    # Values ADR must contain
    required_in_adr = {
        "declared_origins": declared_origins,
        "executed_origins": executed_origins,
        "declared_seeds": declared_seeds,
        "main_seed": main_seed,
        "g4_seed_count": len(g4_seeds),
        "s44_origins": s44_origins,
    }

    adr_check = check_adr_contains_values(adr, required_in_adr)

    if not adr_check["ok"]:
        print("ADR MISSING VALUES:")
        for m in adr_check["missing"]:
            print(f"  - {m}")
        return 1

    print("PROTOCOL_AUDIT_OK")
    return 0


if __name__ == "__main__":
    exit(main())