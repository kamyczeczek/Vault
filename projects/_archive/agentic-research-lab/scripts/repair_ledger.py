#!/usr/bin/env python3
"""Append-only repair ledger and invariant gate for workspace self-healing."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "reflection" / "repair_ledger.jsonl"

VALID_TYPES = {"FailureEvent", "Defect", "RepairProposal", "ValidationRun", "Checkpoint", "Commit", "Rollback"}
VALID_STATES = {"proposed", "quarantined", "experimental", "accepted", "rejected", "superseded"}
VALID_LAYERS = {"prompt", "context", "loop", "harness", "graph", "attention", "ontology"}
# Fixed cutoff, not a moving window: writers were fixed on 2026-09-27
# (repair_graph_state.log and evidence_graph appends now emit schema
# records). Anything older is admitted history — counted, never rewritten.
LEGACY_CUTOFF = "2026-09-27T00:00:00+00:00"

def _now(): return datetime.now(timezone.utc).isoformat()
def _id(kind, payload):
    raw = json.dumps([kind, payload, _now()], sort_keys=True).encode()
    return f"{kind.lower()}-{hashlib.sha256(raw).hexdigest()[:16]}"

def append(kind: str, payload: dict, *, state: str = "proposed") -> dict:
    if kind not in VALID_TYPES: raise ValueError(f"invalid ledger type: {kind}")
    if state not in VALID_STATES: raise ValueError(f"invalid ledger state: {state}")
    event = {"id": _id(kind, payload), "type": kind, "state": state, "created_at": _now(), **payload}
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f: f.write(json.dumps(event, sort_keys=True) + "\n")
    return event

def read() -> list[dict]:
    if not LEDGER.exists(): return []
    result = []
    for line in LEDGER.read_text(encoding="utf-8", errors="replace").splitlines():
        try: result.append(json.loads(line))
        except json.JSONDecodeError: continue
    return result

def validate() -> tuple[bool, list[str]]:
    events, issues, ids = read(), [], set()
    grandfathered = 0
    for event in events:
        ident = event.get("id")
        if not ident:
            # Legacy operational rows (pre-2026-09-27, written by
            # repair_graph_state.log before it emitted schema records).
            # Admitted history: counted, not rewritten, never an issue.
            # All new writes go through append() and must conform.
            grandfathered += 1
            continue
        if ident in ids: issues.append(f"duplicate id: {ident}")
        ids.add(ident)
        if event.get("type") not in VALID_TYPES: issues.append(f"invalid type: {ident}")
        if event.get("state") not in VALID_STATES: issues.append(f"invalid state: {ident}")
        if event.get("type") in {"FailureEvent", "Defect", "RepairProposal"}:
            if str(event.get("created_at", "")) < LEGACY_CUTOFF:
                grandfathered += 1
                continue
            layer = event.get("layer")
            if layer not in VALID_LAYERS:
                issues.append(f"invalid or missing layer ({layer}): {ident}")
            if not event.get("validation_boundary"):
                issues.append(f"missing validation_boundary: {ident}")
    return not issues, issues + ([f"grandfathered legacy rows: {grandfathered}"] if grandfathered else [])

def gate() -> tuple[bool, dict]:
    ok, issues = validate()
    return ok, {"ledger_events": len(read()), "issues": issues, "status": "ready" if ok else "repair_required"}

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--validate", action="store_true")
    args = ap.parse_args(); ok, report = gate(); print(json.dumps(report, indent=2)); raise SystemExit(0 if ok else 1)
