#!/usr/bin/env python3
"""Print the frozen v2 manifest's split keys, declared counts and per-domain totals.

Why this exists: the Phase 1b freeze flag claims "20 Dev / 38 quarantine /
42 Lockbox = 100 tasks". This script reads the manifest that is actually on
disk and prints the keys, the declared `counts` block and the recomputed
per-layer totals, so the claim can be verified rather than repeated.
Read-only; writes nothing.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "results" / "manifest.json"

LAYER_KEYS = {
    "dev_tasks": "dev",
    "unused_sibling_quarantine": "quarantine",
    "lockbox_tasks": "lockbox",
}


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(f"protocol: {data.get('protocol')}  version: {data.get('version')}")
    print(f"manifest_sha256: {data.get('manifest_sha256')}")
    print(f"declared counts: {json.dumps(data.get('counts'), sort_keys=True)}")
    print(f"declared domains: {json.dumps(data.get('domains'), sort_keys=True)}")

    recomputed = {}
    for key, layer in LAYER_KEYS.items():
        tasks = data.get(key, [])
        domains = {}
        for task in tasks:
            domains[task.get("domain")] = domains.get(task.get("domain"), 0) + 1
        recomputed[layer] = len(tasks)
        print(f"{layer:11s}: n={len(tasks):3d}  domains={json.dumps(domains, sort_keys=True)}")

    total = sum(recomputed.values())
    print(f"recomputed total: {total} (dev+quarantine+lockbox)")

    declared = data.get("counts", {}) if isinstance(data.get("counts"), dict) else {}
    mismatches = []
    for key, layer in LAYER_KEYS.items():
        value = declared.get(layer, declared.get(key))
        if value is not None and int(value) != recomputed[layer]:
            mismatches.append(f"{layer}: declared {value} != actual {recomputed[layer]}")
    if declared.get("total") is not None and int(declared["total"]) != total:
        mismatches.append(f"total: declared {declared['total']} != actual {total}")
    print("verdict:", "MISMATCH " + "; ".join(mismatches) if mismatches else "matches the declared counts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
