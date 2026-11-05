"""Append amendment A6 (disclosure) to benchmark-core/ledger.jsonl.

A6 corrects A5's "cannot be determined" claim about the aborted 2026-10-30
legacy --fev-full run, and records why the requested mechanical re-partition of
the Lockbox is not implementable under PROTOCOL.md §2.

Run from repo root: python.exe projects/research/benchmark-core/apply_a6.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ledger import Ledger  # noqa: E402

MANIFEST_SHA = "34b35abc12652a43306b9c976d007a6fa70762c13ec32e039b933180936b42da"

CONTAMINATED_IDX = [7, 8, 9, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                    30, 35, 36, 37, 40, 41, 42, 45, 46, 47, 48, 49, 56, 62, 63,
                    65, 66, 67, 68, 69]
CLEAN_IDX = [76, 92, 93, 94, 95, 99]

SUMMARY = (
    "A5 correction + Lockbox contamination disclosure. The aborted 2026-10-30 legacy "
    "`bench.py --fev-full` run (pre-protocol) reached full-set position 74, i.e. it "
    "computed MASE-inputs for 73 tasks completely and task 74 partially. By manifest "
    "task_id index (build_manifest enumerates the full list, so index == position - 1) "
    "that is 36 of the 42 Lockbox tasks, across 17 of 21 Lockbox families and all 5 "
    "Lockbox domains. Only 6 Lockbox tasks were never computed: task_id indices "
    "76, 92, 93, 94, 95, 99 (families ecdc_ili, fred_md, fred_qd, gvar; domains econ, "
    "healthcare). Consequence: those 36 tasks cannot carry a confirmatory Lockbox "
    "claim under §8. The mechanical re-partition requested to restore blindness is NOT "
    "implementable under §2 and was therefore not applied: sibling quarantine may hold "
    "only Dev-family siblings and Lockbox only non-Dev families (verify_manifest "
    "asserts both, plus the ETT ban), so a contaminated Lockbox task cannot be moved "
    "into quarantine and no clean pool exists to refill the Lockbox from. Manifest and "
    "its SHA-256 are unchanged; the §8 remedy (accept 6-task Lockbox, brand the 42 as "
    "post-hoc diagnostics, or add fresh blind data outside fev-bench-100) is an owner "
    "decision and will be recorded as a separate amendment."
)

EVIDENCE = (
    "Recovered console log: %TEMP%/fev-full.log, 959 lines, written 2026-10-30 "
    "00:26-01:50, containing `-- task N/100 <dataset>` headers through task 74 and two "
    "model lines for task 74 before the process exited. No artifact was written to the "
    "repo (`results/bench_fev_full.json` absent), which is why A5 recorded 'cannot be "
    "determined'; the position evidence survives in the console log and in this "
    "session's transcript. index->task_id mapping taken from results/manifest.json "
    "(`task_%02d_<config>`). Invariants checked in manifest.py verify_manifest: "
    "quarantine family must be in Dev families; Dev and Lockbox families must be "
    "disjoint; ETT forbidden in Lockbox. Legacy protocol caveat: the 2026-10-30 run "
    "used raw MAE, 5 rolling origins and the pre-v2 model set (nlinear_a1/a10, rff_h64, "
    "subband_cA1/d1, knn_forecaster, wavelet_pooled, pools A/B/C/I), not v2 MASE with "
    "the last 3 windows; the leak is therefore coarse relative ranking, not a v2 "
    "measurement — but §8 is precautionary and treats it as contamination."
)

entry = {
    "type": "amendment",
    "amendment_id": "A6",
    "date": "2026-11-02",
    "protocol_version": "2.0.0",
    "manifest_sha256": MANIFEST_SHA,
    "sections": ["§2", "§8", "§15"],
    "summary": SUMMARY,
    "evidence": EVIDENCE,
    "contaminated_lockbox_task_index": CONTAMINATED_IDX,
    "clean_lockbox_task_index": CLEAN_IDX,
}

ledger = Ledger(HERE / "ledger.jsonl")
existing = ledger.read_entries()
if any(e.get("amendment_id") == "A6" for e in existing):
    raise SystemExit("A6 already present — refusing to append a duplicate")

h = ledger.append_entry(entry)
ledger.verify_integrity(expected_manifest_sha256=MANIFEST_SHA)
print("A6 appended, row_sha256 =", h)
print("entries now:", len(ledger.read_entries()), "| chain verified against manifest sha")
