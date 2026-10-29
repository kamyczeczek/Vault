#!/usr/bin/env python3
"""Deterministic checks for the unlazy GATES.md ledger (P0/P1 closure leaves).

Each --gate <id> prints exactly one line: "<id> PASS" on success, or
"<id> FAIL: <reason>" on failure, and exits 0/1 accordingly. One gate per
process keeps the oracle decisive: a gate can only pass when every assertion
in it holds, and the failure reason names the first broken assertion.

Usage:
    python scripts/gate_checks.py --gate g1-amr-g4
    python scripts/gate_checks.py --list
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AMR_DOC = ROOT / "projects" / "research" / "etth1-h720" / "AMR_24_168_H720_RESULT.md"
FEV_FLAG = ROOT / "handoff" / "flags" / "benchmark-core-fev-multivariate-2026-10-27.md"
FEV_PROTOCOL = ROOT / "projects" / "research" / "benchmark-core" / "FEV_PROTOCOL.md"
BENCH_PY = ROOT / "projects" / "research" / "benchmark-core" / "bench.py"
G4_ARTIFACT = ROOT / "projects" / "research" / "etth1-h720" / "results" / "etth1_h720_amr24168_g4.json"
OKF_NOTES = [
    "DECISION-minimalny-przeplyw-wiedzy.md",
    "DECISION-kontrakt-odpowiedzi-retrieval.md",
    "EXPERIMENT-benchmark-scope-2026-10-25.md",
    "EXPERIMENT-retrieval-benchmark-20-2026-10-25.md",
    "EXPERIMENT-retrieval-answer-contract-2026-10-25.md",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def gate_g1_amr_g4() -> str | None:
    """The AMR result document must not contradict the committed G4 artifact."""
    if not G4_ARTIFACT.is_file():
        return f"missing artifact {G4_ARTIFACT.name} — gate cannot assert the run happened"
    doc = _read(AMR_DOC)
    if "5-seed sweep was not run to completion" in doc:
        return "AMR_24_168_H720_RESULT.md still claims the 5-seed sweep did not finish"
    if "mean_rank 6.1" not in doc:
        return "AMR_24_168_H720_RESULT.md does not report mean_rank 6.1"
    if "pass: false" not in doc and "pass=false" not in doc:
        return "AMR_24_168_H720_RESULT.md does not report pass: false"
    if "etth1_h720_amr24168_g4.json" not in doc:
        return "AMR_24_168_H720_RESULT.md does not name the G4 artifact"
    return None


def gate_g2_fev_flag() -> str | None:
    """Flag, protocol and code must agree about per-origin fit."""
    bench = _read(BENCH_PY)
    has_loop = "for w in windows:" in bench and "train_cols_w" in bench
    if not has_loop:
        return "bench.py has no per-origin fit loop (for w in windows: + train_cols_w)"
    flag = _read(FEV_FLAG)
    not_checked_lines = [line for line in flag.splitlines() if line.startswith("not checked:")]
    if any("per-origin fit" in line.lower() for line in not_checked_lines):
        return "flag's `not checked:` line still claims per-origin fit is unverified"
    protocol = _read(FEV_PROTOCOL)
    if "per-origin" not in protocol.lower():
        return "FEV_PROTOCOL.md does not mention per-origin fit at all"
    return None


def gate_g6_did_sessions() -> str | None:
    """The committed default must be COUNT=5, not the session-1 value of 1."""
    try:
        head = subprocess.run(
            ["git", "show", "HEAD:scripts/did_sessions.bat"],
            capture_output=True, text=True, cwd=str(ROOT), check=True,
        ).stdout
    except subprocess.CalledProcessError as exc:  # pragma: no cover - git failure
        return f"git show HEAD:scripts/did_sessions.bat failed: {exc.stderr.strip()[:120]}"
    if not re.search(r'if "%COUNT%"==""\s+set COUNT=5', head):
        return "committed did_sessions.bat does not default to COUNT=5"
    return None


def gate_g7_okf_sources() -> str | None:
    """Five OKF-rag notes must carry structured sources with line ranges."""
    migrated = 0
    for name in OKF_NOTES:
        text = _read(ROOT / "kb" / "Notes" / "OKF-rag" / name)
        block = re.search(r"^sources:\s*\n((?:[ \t]+.*\n)+)", text, re.M)
        if not block:
            continue
        if re.search(r"^\s*-\s*\{\s*file\s*:", block.group(1), re.M) and "lines:" in block.group(1):
            migrated += 1
    if migrated != len(OKF_NOTES):
        return f"{migrated}/{len(OKF_NOTES)} OKF-rag notes migrated to [{{file, lines}}]"
    return None


def gate_g10_no_strays() -> str | None:
    """No close scratch files in handoff/root or lock dirs left in the tree."""
    strays = [
        p for p in ROOT.rglob("close_body.txt")
        if ".git" not in p.parts and "scripts" not in p.parts and "_scratch" not in p.parts
    ]
    if strays:
        return f"stray close_body.txt: {strays[0].relative_to(ROOT)}"
    tracked = subprocess.run(
        ["git", "ls-files", "--", "*close_body*", "*correct_body*"],
        capture_output=True, text=True, cwd=str(ROOT),
    ).stdout.splitlines()
    if tracked:
        return f"tracked close body in git index: {tracked[0]}"
    locks = ROOT / ".unlazy"
    if locks.is_dir():
        return ".unlazy/ exists — it deadlocks python.exe on Windows"
    return None


GATES = {
    "g1-amr-g4": gate_g1_amr_g4,
    "g2-fev-flag": gate_g2_fev_flag,
    "g6-did-sessions": gate_g6_did_sessions,
    "g7-okf-sources": gate_g7_okf_sources,
    "g10-no-strays": gate_g10_no_strays,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gate", choices=sorted(GATES))
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        for name in sorted(GATES):
            print(name)
        return 0
    if not args.gate:
        ap.error("one of --gate or --list is required")

    reason = GATES[args.gate]()
    if reason is None:
        print(f"{args.gate} PASS")
        return 0
    print(f"{args.gate} FAIL: {reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
