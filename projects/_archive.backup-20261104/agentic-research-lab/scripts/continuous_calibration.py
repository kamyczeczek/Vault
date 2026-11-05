#!/usr/init/env python3
"""
continuous_calibration.py — Autonomous continuous calibration daemon for workspace memory (reflection/memory.md).

Audits accepted rules against graph.db evidence resolution and candidate eviction predicates.
Fails loud or prunes rules whose cited evidence no longer resolves, closing the ExpeL
eviction loop on workspace memory.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
MEMORY_MD = ROOT / "reflection" / "memory.md"
DB = ROOT / "knowledge" / "graph" / "graph.db"
LOG_FILE = ROOT / "reflection" / "calibration_log.jsonl"
CANDIDATES_DIR = ROOT / "reflection" / "candidates"

def existing_ids() -> set[str]:
    if not DB.exists():
        return set()
    conn = sqlite3.connect(DB)
    try:
        return {r[0] for r in conn.execute("SELECT id FROM nodes").fetchall()}
    finally:
        conn.close()

def parse_memory() -> list[dict]:
    if not MEMORY_MD.exists():
        return []
    content = MEMORY_MD.read_text(encoding="utf-8")
    rules = []
    blocks = content.split("### ")
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        header = lines[0]
        rule_id = header.split(" — ")[0].strip()
        rule_text = ""
        evidence_ids = []
        for line in lines[1:]:
            if line.startswith("Rule:"):
                rule_text = line.split("Rule:", 1)[1].strip()
            elif line.startswith("Evidence:"):
                ev_part = line.split("Evidence:", 1)[1].strip()
                evidence_ids = re.findall(r"`([^`]+)`", ev_part)
        rules.append({
            "id": rule_id,
            "rule": rule_text,
            "evidence": evidence_ids
        })
    return rules

def main() -> int:
    ap = argparse.ArgumentParser(description="Continuous Calibration Daemon")
    ap.add_argument("--dry-run", action="store_true", help="Report calibration without modifying memory")
    args = ap.parse_args()

    print("=== VERA Continuous Memory Calibration ===")
    print(f"Timestamp: {datetime.now().isoformat()}")

    if not DB.exists():
        print("FAIL: graph.db missing — run build_graph.py first", file=sys.stderr)
        return 2

    ids = existing_ids()
    rules = parse_memory()
    print(f"Loaded {len(rules)} accepted rules from reflection/memory.md")

    calibrations = []
    stale_count = 0

    sys.path.insert(0, str(ROOT / "scripts"))
    import memory_scores
    scores = memory_scores.load_scores()

    for r in rules:
        rule_id = r["id"]
        evidence = r["evidence"]
        unresolved = [e for e in evidence if e not in ids]
        status = "valid"
        if unresolved:
            status = "stale_ungrounded"
            stale_count += 1
            print(f"[{rule_id}] STALE: evidence IDs {unresolved} no longer resolve in graph.db")
        else:
            print(f"[{rule_id}] VALID: all {len(evidence)} evidence chunks resolve")
        # vera-expa-002/003 loop closure: the memory_scores sidecar carries the
        # machine-readable score + eviction predicate. A rule whose score has
        # dropped below the threshold is stale even if its evidence still
        # resolves — the audit verdict, not just the chunk, is the predicate.
        rule_score = scores.get(rule_id, {}).get("score")
        if rule_score is not None and rule_score < memory_scores.EVICT_THRESHOLD:
            status = "below_eviction_threshold"
            stale_count += 1
            print(f"[{rule_id}] EVICT-CANDIDATE: score {rule_score} < {memory_scores.EVICT_THRESHOLD}")
        elif rule_score is not None and rule_score < 1.0:
            print(f"[{rule_id}] DECORLATED: score {rule_score} (audit decrements)")

        calibrations.append({
            "timestamp": datetime.now().isoformat(),
            "rule_id": rule_id,
            "status": status,
            "unresolved_evidence": unresolved,
            "score": rule_score,
        })

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        for entry in calibrations:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"\nCalibration complete: {len(rules)} checked, {stale_count} stale rules detected.")
    print(f"Log written to: {LOG_FILE.relative_to(ROOT)}")

    if stale_count > 0 and not args.dry_run:
        print("WARNING: Stale ungrounded rules detected in memory.md. Run eviction protocol.", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
