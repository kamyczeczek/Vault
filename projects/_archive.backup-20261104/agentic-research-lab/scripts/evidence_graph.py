#!/usr/bin/env python3
"""Versioned evidence/workflow graph and repair gate.

The corpus remains canonical. This file records a compact, append-only graph
snapshot describing evidence and workflow candidates above that corpus.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from repair_ledger import append as ledger_append, gate as ledger_gate

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "knowledge" / "corpus"
INBOX = ROOT / "INBOX"
CANDIDATES = ROOT / "reflection" / "candidates"
STATE = ROOT / "reflection" / "evidence_graph.jsonl"


def _ids() -> set[str]:
    return {p.stem for p in CORPUS.glob("*.md")}


def _fingerprint() -> str:
    h = hashlib.sha256()
    for p in sorted(CORPUS.glob("*.md")):
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def _evidence_ids() -> set[str]:
    ids = set()
    for p in CORPUS.glob("*.md"):
        ids.add(p.stem)
        ids.add(re.sub(r"^\d+_", "", p.stem))
    graph_db = ROOT / "knowledge" / "graph" / "graph.db"
    if graph_db.exists():
        import sqlite3
        try:
            with sqlite3.connect(graph_db) as conn:
                ids.update(row[0] for row in conn.execute("SELECT id FROM nodes"))
        except sqlite3.Error:
            pass
    for p in CANDIDATES.glob("*.jsonl"):
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("id"):
                ids.add(str(obj["id"]))
    return ids


def _evidence(value) -> list[str]:
    if isinstance(value, list):
        raw = value
    else:
        raw = re.findall(r"`([^`]+)`", str(value or "")) or [str(value or "")]
    return [x.strip() for x in raw if isinstance(x, str) and x.strip()]


def inspect(repair: bool = False) -> dict:
    """Inspect pending findings and workflow candidates.

    Repair is conservative: malformed/unsupported candidate records are marked
    rejected in the graph snapshot, never silently rewritten in source files.
    """
    corpus_ids = _evidence_ids()
    nodes, edges, issues = [], [], []
    for p in sorted(INBOX.glob("*.md")):
        if p.name.startswith("_") or "request" in p.name.lower():
            continue
        nid = f"inbox:{p.stem}"
        nodes.append({"id": nid, "type": "finding", "path": str(p.relative_to(ROOT))})
        text = p.read_text(encoding="utf-8", errors="replace")
        if len(text.strip()) < 1200:
            issues.append({"node": nid, "kind": "insufficient_finding", "repair": "hold"})
    for p in sorted(CANDIDATES.glob("*.jsonl")):
        for line_no, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                issues.append({"node": f"candidate:{p.stem}:{line_no}", "kind": "malformed_json", "repair": "reject"})
                continue
            cid = str(obj.get("id", f"{p.stem}:{line_no}"))
            state = obj.get("state", "proposed")
            nodes.append({"id": f"candidate:{cid}", "type": "workflow", "path": str(p.relative_to(ROOT)), "state": state})
            ev = _evidence(obj.get("Evidence", obj.get("evidence", [])))
            if not ev:
                issues.append({"node": f"candidate:{cid}", "kind": "missing_evidence", "repair": "quarantine"})
            for eid in ev:
                edges.append({"src": f"candidate:{cid}", "dst": eid, "kind": "SUPPORTED_BY"})
                if eid not in corpus_ids:
                    issues.append({"node": f"candidate:{cid}", "kind": "missing_evidence_ref", "target": eid, "repair": "quarantine"})
    status = "repair_required" if issues else "ready"
    ledger_ok, ledger_report = ledger_gate()
    if issues:
        ledger_append("FailureEvent", {"category": "evidence_graph", "issue_count": len(issues), "issues": issues, "layer": "graph", "validation_boundary": "evidence_graph gate"}, state="quarantined")
        ledger_append("Defect", {"depends_on": [], "issue_count": len(issues), "evidence_ids": [i.get("target", i.get("node", "")) for i in issues], "layer": "graph", "validation_boundary": "evidence_graph gate"}, state="quarantined")
    if not ledger_ok:
        issues.append({"node": "repair_ledger", "kind": "invalid_ledger", "repair": "hold", "details": ledger_report["issues"]})
    if repair and issues:
        for issue in issues:
            if issue["repair"] == "reject":
                issue["repaired"] = True
        if all(i.get("repair") == "reject" for i in issues):
            status = "repaired_rejected"
    return {"version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
            "corpus_fingerprint": _fingerprint(), "status": status,
            "nodes": nodes, "edges": edges, "issues": issues}


def record(snapshot: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    with STATE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(snapshot, sort_keys=True) + "\n")


def gate(repair: bool = False) -> tuple[bool, dict]:
    snapshot = inspect(repair=repair)
    record(snapshot)
    blocking = [i for i in snapshot["issues"] if i["repair"] != "reject"]
    return not blocking and snapshot["status"] in ("ready", "repaired_rejected"), snapshot


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--repair", action="store_true")
    args = ap.parse_args()
    ok, report = gate(args.repair)
    print(json.dumps({"ok": ok, "status": report["status"], "issues": report["issues"]}, indent=2))
    raise SystemExit(0 if ok else 1)
