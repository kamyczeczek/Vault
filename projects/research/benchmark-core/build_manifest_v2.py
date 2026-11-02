"""Phase 1b — build and freeze the v2 manifest.

Fetches the canonical task definitions (fev-bench-mini 20 tasks, fev-bench 100
tasks), builds the normative manifest via `manifest.py`, and writes it to
`results/manifest.json`.

The raw task lists are cached under `results/` so a rebuild is reproducible
without network access. The manifest's SHA-256 is printed for the ledger's
Genesis block.

Usage:
    python build_manifest_v2.py            # fetch or use cache, then build
    python build_manifest_v2.py --offline  # cache only, never touch network
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
MINI_CACHE = RESULTS / "fev_tasks_mini.json"
FULL_CACHE = RESULTS / "fev_tasks_full.json"
MANIFEST_OUT = RESULTS / "manifest.json"

MINI_URL = "https://raw.githubusercontent.com/autogluon/fev/main/benchmarks/fev_bench/tasks_mini.yaml"
FULL_URL = "https://raw.githubusercontent.com/autogluon/fev/main/benchmarks/fev_bench/tasks.yaml"

sys.path.insert(0, str(ROOT))
import manifest as manifest_mod  # noqa: E402


def _fetch(url: str) -> list[dict]:
    import requests
    import yaml

    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return yaml.safe_load(resp.text)["tasks"]


def load_tasks(url: str, cache: Path, offline: bool) -> list[dict]:
    if cache.is_file():
        tasks = json.loads(cache.read_text(encoding="utf-8"))
        print(f"  cache hit: {cache.name} ({len(tasks)} tasks)")
        return tasks
    if offline:
        raise SystemExit(f"--offline but no cache at {cache}")
    print(f"  fetching {url}")
    tasks = _fetch(url)
    RESULTS.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
    print(f"  cached {len(tasks)} tasks -> {cache.name}")
    return tasks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="use cached task lists only; fail if absent")
    a = ap.parse_args()

    print("loading task definitions")
    mini = load_tasks(MINI_URL, MINI_CACHE, a.offline)
    full = load_tasks(FULL_URL, FULL_CACHE, a.offline)

    print("building manifest")
    man = manifest_mod.build_manifest(mini, full)

    sha = manifest_mod.compute_manifest_sha256(man)
    man["manifest_sha256"] = sha

    RESULTS.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUT.write_text(json.dumps(man, indent=2, sort_keys=True), encoding="utf-8")

    c = man["counts"]
    print(f"wrote {MANIFEST_OUT}")
    print(f"  dev_tasks        = {c['dev_tasks']}")
    print(f"  dev_families     = {c['dev_families']}")
    print(f"  quarantine_tasks = {c['quarantine_tasks']}")
    print(f"  lockbox_tasks    = {c['lockbox_tasks']}")
    print(f"  lockbox_families = {c['lockbox_families']}")
    print(f"  manifest_sha256  = {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
