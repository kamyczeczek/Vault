"""Phase 1b — independent procedural audit of the benchmark-core v2 artifacts.

Implements the rubric in PROTOCOL.md §9. Designed to run in a fresh session
with no memory of how the artifacts were produced: every input is a frozen
file on disk (`ledger.jsonl`, `results/manifest.json`, source files).

Rubric
------
1. Ledger hash chain (`prev_sha256`) and Genesis binding to the manifest.
2. Chronology: a `cycle_card` must precede its `run_result`.
3. Gate/budget compliance recorded in `run_result` entries.
4. No Lockbox or quarantine task references in the Dev runtime path.

The auditor reports evidentiary findings; it does not issue discretionary
verdicts (PROTOCOL.md §9). Exit code 0 means "no hard findings".

Usage:
    python audit_v2.py
    python audit_v2.py --json     # machine-readable report
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "results" / "manifest.json"
LEDGER = ROOT / "ledger.jsonl"

sys.path.insert(0, str(ROOT))
import ledger as ledger_mod  # noqa: E402

# Files that legitimately name Lockbox/quarantine tasks: the one-time manifest
# builder, the Phase 1b denominator scanner, the ledger initializer, the audit
# itself, and tests. Everything else is "runtime" and must stay Lockbox-blind.
EXEMPT_FILES = {
    "manifest.py",            # classifies families, incl. Lockbox families
    "build_manifest_v2.py",   # loads the full fev task list (one-time)
    "scan_denominator_anomalies.py",  # can scan --layer lockbox (definitions only)
    "init_ledger_v2.py",      # records counts + amendments
    "audit_v2.py",            # this file
}

WALL_BUDGET_S = 1200.0
MAX_FAILURE_RATE = 0.02
MAX_LOCKBOX_EVALS = 3
LOCKBOX_ALPHA = 0.05 / 3


class Report:
    def __init__(self) -> None:
        self.hard: list[str] = []
        self.info: list[str] = []
        self.checks: list[dict[str, Any]] = []

    def check(self, name: str, ok: bool, detail: str) -> None:
        self.checks.append({"check": name, "ok": ok, "detail": detail})
        if not ok:
            self.hard.append(f"{name}: {detail}")

    def note(self, msg: str) -> None:
        self.info.append(msg)

    def as_dict(self) -> dict[str, Any]:
        return {
            "checks": self.checks,
            "hard_findings": self.hard,
            "informational": self.info,
            "verdict": "CLEAN" if not self.hard else "FINDINGS",
        }


def canonical_sha256(obj: dict) -> str:
    raw = json.dumps(obj, sort_keys=True, indent=None,
                     separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# --------------------------------------------------------------- 1. manifest
def audit_manifest(rep: Report) -> dict:
    if not MANIFEST.is_file():
        rep.check("manifest.present", False, f"missing {MANIFEST}")
        return {}

    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    stored = man.get("manifest_sha256", "")
    body = {k: v for k, v in man.items() if k != "manifest_sha256"}
    rep.check("manifest.sha256", canonical_sha256(body) == stored,
              f"stored {stored[:16]}… vs recomputed {canonical_sha256(body)[:16]}…")

    counts = man.get("counts", {})
    dev = man.get("dev_tasks", [])
    quar = man.get("unused_sibling_quarantine", [])
    lb = man.get("lockbox_tasks", [])

    rep.check("manifest.counts.dev", len(dev) == counts.get("dev_tasks") == 20,
              f"len={len(dev)} declared={counts.get('dev_tasks')}")
    rep.check("manifest.counts.quarantine",
              len(quar) == counts.get("quarantine_tasks") == 38,
              f"len={len(quar)} declared={counts.get('quarantine_tasks')}")
    rep.check("manifest.counts.lockbox", len(lb) == counts.get("lockbox_tasks") == 42,
              f"len={len(lb)} declared={counts.get('lockbox_tasks')}")
    rep.check("manifest.partition", len(dev) + len(quar) + len(lb) == 100,
              f"20 + 38 + 42 = {len(dev) + len(quar) + len(lb)}")

    dev_fams = {t["family"] for t in dev}
    lb_fams = {t["family"] for t in lb}
    rep.check("manifest.dev_families", len(dev_fams) == 15,
              f"families={sorted(dev_fams)}")
    rep.check("manifest.lockbox_families", len(lb_fams) == counts.get("lockbox_families") == 21,
              f"families={len(lb_fams)} declared={counts.get('lockbox_families')}")
    rep.check("manifest.disjoint", not (dev_fams & lb_fams),
              f"overlap={sorted(dev_fams & lb_fams)}")
    rep.check("manifest.ett_not_in_lockbox", "ETT" not in lb_fams,
              "ETT must never appear in Lockbox")

    # Every quarantine task must belong to a dev family.
    bad_q = [t["task_id"] for t in quar if t["family"] not in dev_fams]
    rep.check("manifest.quarantine_in_dev_families", not bad_q,
              f"offending={bad_q[:5]}")

    # Every dev task must carry reconstructible kwargs with MASE and no quantiles.
    bad_kw = []
    for t in dev:
        kw = t.get("task_kwargs") or {}
        if kw.get("eval_metric") != "MASE" or kw.get("quantile_levels") != [] \
                or kw.get("extra_metrics") != []:
            bad_kw.append(t["task_id"])
    rep.check("manifest.task_kwargs", not bad_kw, f"offending={bad_kw[:5]}")

    return man


# ----------------------------------------------------------------- 2. ledger
def audit_ledger(rep: Report, manifest_sha: str) -> list[dict]:
    if not LEDGER.is_file():
        rep.check("ledger.present", False, f"missing {LEDGER}")
        return []

    try:
        led = ledger_mod.Ledger(LEDGER)
        led.verify_integrity(expected_manifest_sha256=manifest_sha)
        entries = led.read_entries()
        rep.check("ledger.chain", True, f"{len(entries)} entries, chain intact")
    except Exception as err:  # any failure is a hard finding
        rep.check("ledger.chain", False, f"{type(err).__name__}: {err}")
        return []

    genesis = entries[0]
    rep.check("ledger.genesis.type", genesis.get("type") == "genesis",
              f"type={genesis.get('type')}")
    rep.check("ledger.genesis.prev_null", genesis.get("prev_sha256") is None,
              f"prev_sha256={genesis.get('prev_sha256')}")
    rep.check("ledger.genesis.binds_manifest",
              genesis.get("manifest_sha256") == manifest_sha,
              f"genesis={str(genesis.get('manifest_sha256'))[:16]}…")
    return entries


# ------------------------------------------------------------- 3. chronology
def audit_chronology(rep: Report, entries: list[dict]) -> None:
    cards: dict[str, int] = {}
    orphans: list[str] = []

    for i, e in enumerate(entries):
        if e.get("type") == "cycle_card":
            key = str(e.get("cycle_id") or e.get("candidate_name") or e.get("candidate"))
            cards.setdefault(key, i)
        elif e.get("type") == "run_result":
            key = str(e.get("cycle_id") or e.get("candidate_name") or e.get("candidate"))
            if key not in cards:
                orphans.append(f"entry {i} ({key})")
            elif cards[key] >= i:
                orphans.append(f"entry {i} ({key}) card at {cards[key]}")

    rep.check("ledger.chronology.card_before_result", not orphans,
              f"orphaned results={orphans[:5]}")

    # Monotonic timestamps, when present.
    stamps = [e["timestamp"] for e in entries if isinstance(e.get("timestamp"), str)]
    rep.check("ledger.chronology.timestamps_monotonic",
              stamps == sorted(stamps),
              f"{len(stamps)} timestamped entries")


# --------------------------------------------------------- 4. gates / budget
def audit_gates(rep: Report, entries: list[dict]) -> None:
    results = [e for e in entries if e.get("type") == "run_result"]
    if not results:
        rep.note("no run_result entries yet; gate checks are vacuous")
        return

    for i, e in enumerate(results):
        cid = e.get("cycle_id") or e.get("candidate") or f"result[{i}]"
        failed = e.get("failed_fits")
        total = e.get("total_fits")
        if isinstance(failed, int) and isinstance(total, int) and total > 0:
            rate = failed / total
            rep.check(f"gate.failure_rate.{cid}", rate <= MAX_FAILURE_RATE,
                      f"{failed}/{total} = {rate:.2%} (max {MAX_FAILURE_RATE:.0%})")
        else:
            rep.note(f"{cid}: failed_fits/total_fits not recorded; cannot check 2% rule")

        wall = e.get("wall_elapsed_s")
        if isinstance(wall, (int, float)):
            rep.check(f"gate.wall_budget.{cid}", wall <= WALL_BUDGET_S,
                      f"{wall:.0f}s (max {WALL_BUDGET_S:.0f}s)")
        else:
            rep.note(f"{cid}: wall_elapsed_s not recorded; cannot check 20-min budget")

        verdict = e.get("verdict")
        if verdict == "fail":
            rep.note(f"{cid}: verdict=fail recorded (Gate 1 rejection is legitimate)")

    lockbox_runs = [e for e in entries if e.get("type") == "lockbox_result"]
    rep.check("gate.lockbox_uses", len(lockbox_runs) <= MAX_LOCKBOX_EVALS,
              f"{len(lockbox_runs)} of max {MAX_LOCKBOX_EVALS}")
    bad_alpha = [e for e in lockbox_runs
                 if abs(float(e.get("alpha", -1)) - LOCKBOX_ALPHA) > 1e-9]
    rep.check("gate.lockbox_alpha", not bad_alpha,
              f"{len(bad_alpha)} entries with alpha != {LOCKBOX_ALPHA:.5f}")


# ------------------------------------------------------ 5. Lockbox isolation
def audit_isolation(rep: Report, man: dict) -> None:
    if not man:
        rep.check("isolation.scan", False, "no manifest to derive task names from")
        return

    forbidden = {t["dataset_config"] for t in man.get("lockbox_tasks", [])}
    forbidden |= {t["dataset_config"] for t in man.get("unused_sibling_quarantine", [])}
    # Word-boundary match, not substring: "hospital" (a Lockbox config) must not
    # match the dev name "hospital_admissions_1D", and "_" is a word character
    # so the boundary holds there.
    patterns = {name: re.compile(r"\b" + re.escape(name) + r"\b") for name in forbidden}

    runtime_files = []
    for p in sorted(ROOT.glob("*.py")):
        if p.name in EXEMPT_FILES or p.name.startswith("test_"):
            continue
        runtime_files.append(p)

    hits: list[str] = []
    for p in runtime_files:
        text = p.read_text(encoding="utf-8", errors="replace")
        for name, pat in patterns.items():
            if pat.search(text):
                hits.append(f"{p.name}: '{name}'")
        if re.search(r"lockbox", text, re.IGNORECASE):
            rep.note(f"{p.name}: mentions 'lockbox' (review manually)")
        if "tasks.yaml" in text or "mini=False" in text:
            rep.note(f"{p.name}: can load the full fev task list (procedural risk)")

    rep.check("isolation.no_lockbox_configs_in_runtime", not hits,
              f"hits={hits[:8]}")
    rep.note(f"scanned {len(runtime_files)} runtime .py files in {ROOT.name}")


# ---------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    a = ap.parse_args()

    rep = Report()
    man = audit_manifest(rep)
    sha = man.get("manifest_sha256", "")
    entries = audit_ledger(rep, sha)
    audit_chronology(rep, entries)
    audit_gates(rep, entries)
    audit_isolation(rep, man)

    payload = rep.as_dict()
    if a.json:
        print(json.dumps(payload, indent=2))
    else:
        print("benchmark-core v2 — procedural audit")
        print(f"  ledger:   {LEDGER}")
        print(f"  manifest: {MANIFEST}")
        print()
        for c in payload["checks"]:
            mark = "PASS" if c["ok"] else "FAIL"
            print(f"  [{mark}] {c['check']}: {c['detail']}")
        print()
        if payload["informational"]:
            print("  informational:")
            for msg in payload["informational"]:
                print(f"    - {msg}")
            print()
        print(f"  verdict: {payload['verdict']} "
              f"({len(payload['hard_findings'])} hard findings)")

    return 0 if not payload["hard_findings"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
