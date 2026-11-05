#!/usr/bin/env python3
"""memory_scores.py — W7 structured score sidecar for reflection/memory.md.

Implements the vera-expa-002/003 pattern: every accepted lesson carries a
machine-readable score and eviction predicate, not just free-text.

Format: one JSON object per line in reflection/memory_scores.jsonl
{
  "rule_id": "vera-expa-001",
  "score": 1.0,
  "last_audit_ts": "2026-09-25T20:30:00",
  "last_audit_verdict": "pass",
  "predicate": "decrement 0.2 when any accepted lesson's evidence chunk is evicted or fails held-out post-promotion audit; evict at score < 0.4",
  "audit_history": [
    {"ts": "...", "verdict": "pass", "f1_status": "partial", "delta": 0.0}
  ]
}

Functions:
- ensure_scores(): seed sidecar rows for all memory.md rules missing an entry
- record_audit(rule_id, verdict, details): append audit event, apply predicate
- active_rules(): return rule_ids with score >= EVICT_THRESHOLD
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMORY = ROOT / "reflection" / "memory.md"
SIDECAR = ROOT / "reflection" / "memory_scores.jsonl"

EVICT_THRESHOLD = 0.4
DECREMENT = 0.2
SEED_SCORE = 1.0


def _parse_rule_ids() -> list[str]:
    if not MEMORY.exists():
        return []
    text = MEMORY.read_text(encoding="utf-8")
    return re.findall(r"^### (\S+) — accepted", text, re.MULTILINE)


def load_scores() -> dict[str, dict]:
    if not SIDECAR.exists():
        return {}
    out: dict[str, dict] = {}
    for line in SIDECAR.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        out[obj["rule_id"]] = obj
    return out


def ensure_scores() -> int:
    """Seed missing rules with seed score. Returns number seeded."""
    scores = load_scores()
    seeded = 0
    for rule_id in _parse_rule_ids():
        if rule_id not in scores:
            scores[rule_id] = {
                "rule_id": rule_id,
                "score": SEED_SCORE,
                "last_audit_ts": datetime.now().isoformat(),
                "last_audit_verdict": "seeded",
                "predicate": ("decrement 0.2 on failed held-out post-promotion audit "
                              "or evicted evidence chunk; evict at score < 0.4"),
                "audit_history": [],
            }
            seeded += 1
    if seeded:
        with open(SIDECAR, "w", encoding="utf-8") as f:
            for rid in scores:
                f.write(json.dumps(scores[rid], ensure_ascii=False) + "\n")
    return seeded


def record_audit(rule_id: str, verdict: str, details: dict | None = None) -> dict:
    """Apply the eviction predicate: pass = no delta, fail = decrement 0.2."""
    ensure_scores()
    scores = load_scores()
    if rule_id not in scores:
        scores[rule_id] = {
            "rule_id": rule_id, "score": SEED_SCORE,
            "last_audit_ts": datetime.now().isoformat(),
            "last_audit_verdict": "seeded",
            "predicate": "decrement 0.2 on failed audit; evict at score < 0.4",
            "audit_history": [],
        }
    entry = scores[rule_id]
    delta = 0.0 if verdict == "pass" else -DECREMENT
    entry["score"] = round(max(entry.get("score", SEED_SCORE) + delta, 0.0), 3)
    entry["last_audit_ts"] = datetime.now().isoformat()
    entry["last_audit_verdict"] = verdict
    event = {"ts": entry["last_audit_ts"], "verdict": verdict, "delta": delta}
    if details:
        event.update(details)
    entry.setdefault("audit_history", []).append(event)

    with open(SIDECAR, "w", encoding="utf-8") as f:
        for rid in scores:
            f.write(json.dumps(scores[rid], ensure_ascii=False) + "\n")

    return entry


def active_rules() -> list[str]:
    """Rule ids still above the eviction threshold (eligible for stage use)."""
    ensure_scores()
    return [r for r, s in load_scores().items() if s.get("score", 0) >= EVICT_THRESHOLD]


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == "audit":
        rule, verdict = sys.argv[2].split(":", 1)
        print(json.dumps(record_audit(rule, verdict), indent=2))
    elif len(sys.argv) == 2 and sys.argv[1] == "active":
        print(json.dumps(active_rules(), indent=2))
    else:
        ensure_scores()
        print(json.dumps(load_scores(), indent=2))
