"""Append amendment A7 (lockbox remedy) to benchmark-core/ledger.jsonl.

A7 records the owner decision on the §8 Lockbox remedy opened by the A6
contamination disclosure. It re-designates the 42-task legacy Lockbox as
post-hoc diagnostics (variant b, now) and defers a fresh blind Lockbox built
outside fev-bench-100 (variant c) to just before any final champion
promotion. The manifest and its SHA-256 are unchanged; A7 is a remedy choice,
not a manifest change, so it appends after the A6 disclosure entries.

Kept in projects/_archive/ (mirroring benchmark-core-apply-a6.py): a one-time
ledger tooling file that names Lockbox scope, so it must not sit in the
benchmark-core runtime tree scanned by audit_v2's isolation gate.

Run from repo root:
    python.exe projects/_archive/benchmark-core-apply-a7.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BC = HERE / ".." / "research" / "benchmark-core"
sys.path.insert(0, str(BC.resolve()))

from ledger import Ledger  # noqa: E402

MANIFEST = BC.resolve() / "results" / "manifest.json"
MANIFEST_SHA = "34b35abc12652a43306b9c976d007a6fa70762c13ec32e039b933180936b42da"

SUMMARY = (
    "A7 (owner decision, 2026-11-07): §8 Lockbox remedy chosen as variant (b) now "
    "+ variant (c) before final promotion. The 42-task legacy Lockbox (36/42 "
    "contaminated by the aborted 2026-10-30 legacy --fev-full run, per A6) is "
    "re-designated post-hoc diagnostics and carries NO confirmatory claim under §8. "
    "A new blind Lockbox will be built from fresh data outside fev-bench-100 before "
    "any final champion promotion. Dev incumbent for Phase 2 is NLinear "
    "(vs SNaive +14.88%, lower 98.33% CI +3.75%, passes); DLinear (+12.08%, lower "
    "CI -0.63%) is the comparator and does not pass. No generalization claims are "
    "made. Phase 2 (starting population N<=8, Champion=NLinear, 20-min/method "
    "Dev budget, dashboard) is unblocked on Dev. GIFT-Eval overlap with fev-bench "
    "is unverified and must be confirmed before any (c) data selection."
)

EVIDENCE = (
    "Phase 1b Dev analysis: results/phase1b_dev_analysis.json (commit cd087c3) "
    "NLinear_vs_SNaive skill 0.1488 (lower CI +3.75%, passes the >0 gate), "
    "DLinear_vs_SNaive 0.1208 (lower CI -0.63%, fails), MDE 0.178, 20/20 tasks "
    "in 1359s, all within the 20-min budget. Contamination scope and the "
    "clean-task list (task_id 76,92,93,94,95,99; families ecdc_ili, fred_md, "
    "fred_qd, gvar; domains econ, healthcare) come from the A6 ledger entry and "
    "results/manifest.json (lockbox_tasks=42, lockbox_families=21). Decision "
    "registered in handoff/decisions/benchmark-core-a7-lockbox.md and row A7 "
    "added to PROTOCOL.md §15. Manifest SHA-256 unchanged."
)

entry = {
    "type": "amendment",
    "amendment_id": "A7",
    "date": "2026-11-07",
    "protocol_version": "2.0.0",
    "manifest_sha256": MANIFEST_SHA,
    "sections": ["§8", "§15"],
    "summary": SUMMARY,
    "evidence": EVIDENCE,
    "remedy_variants": {
        "now": "b - 42-task legacy Lockbox kept as post-hoc diagnostics, no confirmatory claim",
        "before_final_promotion": "c - new blind Lockbox built from fresh data outside fev-bench-100",
    },
    "dev_incumbent": "NLinear",
    "dev_comparator": "DLinear",
}


def rederive_manifest_sha() -> str:
    """Re-derive the manifest SHA-256 (stripping the stored field) and assert
    it matches the A6/A7 constant, so a silent manifest drift is caught."""
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    body = {k: v for k, v in man.items() if k != "manifest_sha256"}
    raw = json.dumps(body, sort_keys=True, indent=None,
                     separators=(",", ":")).encode("utf-8")
    recomputed = hashlib.sha256(raw).hexdigest()
    if recomputed != MANIFEST_SHA:
        raise SystemExit(
            f"manifest drift: recomputed {recomputed} != expected {MANIFEST_SHA}; "
            "refusing to append A7 against an unbound manifest"
        )
    return recomputed


def main() -> int:
    sha = rederive_manifest_sha()
    ledger = Ledger(BC.resolve() / "ledger.jsonl")
    existing = ledger.read_entries()
    if any(e.get("amendment_id") == "A7" for e in existing):
        raise SystemExit("A7 already present — refusing to append a duplicate")

    h = ledger.append_entry(entry)
    ledger.verify_integrity(expected_manifest_sha256=sha)
    print(f"A7 appended, row_sha256 = {h}")
    print(f"entries now: {len(ledger.read_entries())} | chain verified against "
          f"manifest sha {sha[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
