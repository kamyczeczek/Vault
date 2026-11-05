#!/usr/bin/env python3
"""Validate typed agent trace referential integrity against the active graph."""
from __future__ import annotations
import json, sqlite3, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "reflection" / "trace" / "events.jsonl"
DB = ROOT / "knowledge" / "graph" / "graph.db"
GEN = ROOT / "knowledge" / "graph" / "generation.json"

def main() -> int:
    if not TRACE.exists():
        print("OK: no agent trace records")
        return 0
    try:
        active = json.loads(GEN.read_text(encoding="utf-8"))["generation_id"]
        conn = sqlite3.connect(DB)
        ids = {row[0] for row in conn.execute("SELECT id FROM nodes")}
        conn.close()
    except (OSError, ValueError, KeyError, sqlite3.Error) as exc:
        print(f"FAIL: trace validation setup: {exc}", file=sys.stderr)
        return 2
    seen = set(); errors = []; runs = set(); events = {}
    records = []
    for lineno, line in enumerate(TRACE.read_text(encoding="utf-8").splitlines(), 1):
        try:
            obj = json.loads(line)
        except ValueError as exc:
            errors.append(f"line {lineno}: invalid JSON ({exc})"); continue
        required = {"event_id", "kind", "timestamp", "graph_generation"}
        missing = required - obj.keys()
        if missing: errors.append(f"line {lineno}: missing {sorted(missing)}")
        eid = obj.get("event_id")
        if eid in seen: errors.append(f"line {lineno}: duplicate event_id {eid}")
        seen.add(eid)
        events[eid] = obj
        records.append((lineno, obj))
        if obj.get("graph_generation") and obj["graph_generation"] != active:
            errors.append(f"line {lineno}: stale graph generation {obj['graph_generation']}")
        run_id = obj.get("run_id")
        if run_id:
            runs.add(run_id)
        for artifact in obj.get("artifacts", []) if isinstance(obj.get("artifacts"), list) else ([obj["artifact"]] if obj.get("artifact") else []):
            if not (ROOT / artifact).exists():
                errors.append(f"line {lineno}: missing artifact {artifact}")
        if obj.get("kind") in {"artifact", "validation"} and not run_id:
            errors.append(f"line {lineno}: {obj['kind']} event has no run_id")
        for retrieval_id in obj.get("retrieval_event_ids", []):
            retrieval = events.get(retrieval_id)
            if not retrieval:
                errors.append(f"line {lineno}: unknown retrieval event {retrieval_id}")
            elif retrieval.get("kind") != "retrieval":
                errors.append(f"line {lineno}: {retrieval_id} is not a retrieval event")
            elif retrieval.get("run_id") != run_id:
                errors.append(f"line {lineno}: retrieval {retrieval_id} belongs to another run")
        if obj.get("kind") == "retrieval":
            returned = obj.get("returned_ids", [])
            missing_ids = sorted(set(returned) - ids)
            if missing_ids: errors.append(f"line {lineno}: unknown returned_ids {missing_ids[:3]}")
    if errors:
        print("\n".join("FAIL: " + e for e in errors), file=sys.stderr); return 1
    print(f"OK: validated {len(seen)} typed trace event(s), generation={active}")
    return 0
if __name__ == "__main__": raise SystemExit(main())
