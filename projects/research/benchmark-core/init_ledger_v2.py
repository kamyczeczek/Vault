"""Phase 1b — initialize the append-only ledger with the Genesis block.

Binds the frozen `results/manifest.json` (by SHA-256) into block 0 and records
the four protocol amendments (A1-A4) that were made while measuring the
manifest, so the audit trail starts at block 0 rather than mid-history.

Refuses to run if the ledger already exists: the ledger is append-only, and a
second Genesis would silently invalidate every later `prev_sha256`.

Usage:
    python init_ledger_v2.py            # create ledger.jsonl
    python init_ledger_v2.py --check    # verify an existing ledger only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "results" / "manifest.json"
LEDGER = ROOT / "ledger.jsonl"

sys.path.insert(0, str(ROOT))
import ledger as ledger_mod  # noqa: E402

PROTOCOL_VERSION = "2.0.0"
AMENDMENT_DATE = "2026-11-01"


def load_manifest_sha256() -> tuple[dict, str]:
    """Load the manifest and re-derive its hash from canonical JSON.

    The stored `manifest_sha256` field is stripped before hashing, because
    `compute_manifest_sha256` was called on the manifest *before* the field was
    added (see build_manifest_v2.py).
    """
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    stored = man.get("manifest_sha256")
    if not stored:
        raise SystemExit(f"{MANIFEST} has no manifest_sha256 field")

    body = {k: v for k, v in man.items() if k != "manifest_sha256"}
    raw = json.dumps(body, sort_keys=True, indent=None,
                     separators=(",", ":")).encode("utf-8")
    recomputed = hashlib.sha256(raw).hexdigest()
    if recomputed != stored:
        raise SystemExit(
            f"manifest_sha256 mismatch: stored {stored}, recomputed {recomputed}"
        )
    return man, stored


def amendments(manifest_sha256: str) -> list[dict]:
    """The four Phase 1b amendments, in the order they were decided."""
    common = {
        "type": "amendment",
        "protocol_version": PROTOCOL_VERSION,
        "date": AMENDMENT_DATE,
        "manifest_sha256": manifest_sha256,
    }
    return [
        dict(common, **{
            "amendment_id": "A1",
            "sections": ["§2", "§4", "§6", "§8"],
            "summary": (
                "Lockbox 46 -> 42 tasks; sibling quarantine 30 -> 38 tasks; "
                "Lockbox families 24 -> 21."
            ),
            "evidence": (
                "results/manifest.json counts: 20 Dev + 38 quarantine + "
                "42 Lockbox = 100. The original figures predated the manifest "
                "build and were estimates."
            ),
        }),
        dict(common, **{
            "amendment_id": "A2",
            "sections": ["§6"],
            "summary": (
                "'20 tasks x 3 windows = 741 fits' -> '247 target columns x "
                "3 windows = 741 units'; item scale disclosed (2,767 series; "
                "8,301 item x window evaluations)."
            ),
            "evidence": (
                "20 x 3 = 60, so the original equation was arithmetically "
                "wrong. 741 was re-verified column by column against the "
                "manifest; item totals from results/denominator_anomaly_scan.json."
            ),
        }),
        dict(common, **{
            "amendment_id": "A3",
            "sections": ["§2"],
            "summary": (
                "Lockbox domain coverage disclosed: 5 of 7 domains (no cloud, "
                "no nature)."
            ),
            "evidence": (
                "Manifest measurement: retail 14 tasks / 7 families, energy "
                "13/4, econ 8/6, mobility 5/2, healthcare 2/2. Hard sibling "
                "cut removed every cloud and nature family from Lockbox."
            ),
        }),
        dict(common, **{
            "amendment_id": "A4",
            "sections": ["§3"],
            "summary": (
                "Phase 1b MASE-denominator resolution: 0 items with zero "
                "seasonal error and 0 items with NaN, across all 20 Dev tasks; "
                "no exclusions are written to the manifest."
            ),
            "evidence": (
                "results/denominator_anomaly_scan.json: 20/20 tasks scanned "
                "per item, matching fev.metrics._seasonal_error_per_item. The "
                "first scanner version failed to iterate datasets.Column (it "
                "treated a whole column as one item); it was fixed before the "
                "freeze and the corrected scan is binding."
            ),
        }),
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify the existing ledger instead of creating it")
    a = ap.parse_args()

    man, sha = load_manifest_sha256()
    counts = man["counts"]
    print(f"manifest: {MANIFEST.name}  sha256={sha}")
    print(f"  dev={counts['dev_tasks']}  quarantine={counts['quarantine_tasks']}  "
          f"lockbox={counts['lockbox_tasks']}  lockbox_families={counts['lockbox_families']}")

    if a.check:
        led = ledger_mod.Ledger(LEDGER)
        led.verify_integrity(expected_manifest_sha256=sha)
        entries = led.read_entries()
        print(f"ledger OK: {len(entries)} entries, chain intact, genesis bound to manifest")
        return 0

    if LEDGER.exists():
        raise SystemExit(
            f"{LEDGER} already exists; the ledger is append-only. "
            f"Run with --check to verify it."
        )

    led = ledger_mod.Ledger.initialize_genesis(
        LEDGER,
        manifest_sha256=sha,
        protocol_version=PROTOCOL_VERSION,
        metadata={
            "project": "benchmark-core",
            "phase": "1b",
            "fev_version": "0.10.0",
            "dev_tasks": counts["dev_tasks"],
            "dev_families": counts["dev_families"],
            "quarantine_tasks": counts["quarantine_tasks"],
            "lockbox_tasks": counts["lockbox_tasks"],
            "lockbox_families": counts["lockbox_families"],
        },
    )
    print("genesis written")

    for entry in amendments(sha):
        h = led.append_entry(entry)
        print(f"  amendment {entry['amendment_id']}: {h[:16]}…")

    led.verify_integrity(expected_manifest_sha256=sha)
    print(f"ledger verified: {len(led.read_entries())} entries -> {LEDGER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
