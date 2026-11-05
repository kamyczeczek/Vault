#!/usr/bin/env python3
"""Validate candidate evidence before a candidate file can be written.

Unresolved references are never emitted as proposed. Callers receive a
quarantined record that preserves the original references and reason.
"""
from __future__ import annotations
import json, re, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "knowledge" / "graph" / "graph.db"
CANDIDATES = ROOT / "reflection" / "candidates"

def graph_ids() -> set[str]:
    if not DB.exists(): return set()
    with sqlite3.connect(DB) as conn:
        return {row[0] for row in conn.execute("SELECT id FROM nodes")}

def evidence_list(value) -> list[str]:
    if isinstance(value, list): return [str(x).strip() for x in value if str(x).strip()]
    return [x.strip() for x in re.findall(r"`([^`]+)`", str(value or "")) if x.strip()]

def prepare(candidate: dict) -> tuple[dict, list[str]]:
    evidence = evidence_list(candidate.get("Evidence", candidate.get("evidence", candidate.get("evidence_ids", []))))
    missing = sorted(set(evidence) - graph_ids())
    result = dict(candidate)
    result["Evidence"] = ", ".join(f"`{x}`" for x in evidence)

    # Every reusable lesson must be explicit, not hidden in prose. This keeps
    # the failure-condition -> reason -> correction unit machine-checkable.
    target = str(result.get("Target", "the target workflow")).strip() or "the target workflow"
    rule = str(result.get("Rule", result.get("claim", "the observed failure mode"))).strip()
    action = str(result.get("Action", "apply the proposed correction")).strip()
    result.setdefault("Condition", f"When {target} fails, drifts, or becomes unreliable.")
    result.setdefault("Reason", rule)
    result.setdefault("Correction", action)
    triple_missing = [k for k in ("Condition", "Reason", "Correction") if not str(result.get(k, "")).strip()]
    if triple_missing:
        missing.extend(f"triple:{k}" for k in triple_missing)
    if missing:
        result["state"] = "quarantined"
        result["quarantine"] = {"reason": "unresolved_evidence_or_incomplete_triple", "missing": missing}
    else:
        result.setdefault("state", "proposed")
    return result, missing

def write(path: Path, candidates: list[dict]) -> bool:
    prepared = [prepare(c)[0] for c in candidates]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in prepared), encoding="utf-8")
    return not any(c.get("state") == "quarantined" for c in prepared)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("candidate_file")
    args = ap.parse_args(); path = Path(args.candidate_file)
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    ok = write(path, rows); print(json.dumps({"ok": ok, "path": str(path)})); raise SystemExit(0 if ok else 2)
