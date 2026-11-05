#!/usr/bin/env python3
"""root_cause_attribution.py — AgentDebug-style error classification for reflection candidates (vera-expa-004).

detect -> attribute -> correct. Classifies each FAILED candidate (quarantined by
candidate_writer, or vague/ungrounded) into exactly one root-cause category and
emits a structured JSON diagnostic. Downstream correction targets the attributed
root cause, not the symptom.

Error categories (AgentDebug taxonomy adapted to this workspace):
  retrieval_miss        — cited evidence chunk does not resolve in graph.db
  grounding_gap         — action/claim shares no meaningful keyword with its cited evidence
  logical_inconsistency — the failure-condition triple (Condition/Reason/Correction) is incomplete
  tool_misuse           — the run that produced the candidate failed in the tool/agent layer
                         (process non-zero, timeout, or an escalation record for this topic)

Output: one JSON object per failed candidate, appended to reflection/diagnostics/.
A passed/proposed candidate is NOT diagnosed — only failures get an attribution.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_DIR = ROOT / "reflection" / "candidates"
DIAG_DIR = ROOT / "reflection" / "diagnostics"
ESCALATIONS = ROOT / "reflection" / "escalations.jsonl"
GRAPH = ROOT / "knowledge" / "graph" / "graph.db"

sys.path.insert(0, str(ROOT / "scripts"))
import sqlite3

# Vague-action terms: a claim that only says "do better" has a grounding gap.
VAGUE_TERMS = ["optimize", "improve", "consider", "maybe", "promote when externally verified",
               "do better", "handle it", "address"]


def _graph_ids() -> set[str]:
    if not GRAPH.exists():
        return set()
    conn = sqlite3.connect(str(GRAPH))
    try:
        return {r[0] for r in conn.execute("SELECT id FROM nodes")}
    finally:
        conn.close()


def _evidence_ids(cand: dict) -> list[str]:
    raw = cand.get("Evidence") or cand.get("evidence") or cand.get("evidence_ids") or []
    if isinstance(raw, str):
        return [x.strip() for x in re.findall(r"`([^`]+)`", raw) if x.strip()]
    return [str(x).strip() for x in raw if str(x).strip()]


def _is_vague(cand: dict, ids: set[str]) -> bool:
    """True when the action is vague OR none of the cited evidence shares a keyword with the action."""
    action = str(cand.get("Action", "")).lower()
    if not action:
        return False
    if any(t in action for t in VAGUE_TERMS):
        return True
    # keyword overlap check against the cited chunks' bodies
    ev = _evidence_ids(cand)
    if not ev:
        return True
    if GRAPH.exists():
        conn = sqlite3.connect(str(GRAPH))
        try:
            placeholders = ",".join("?" * len(ev))
            rows = conn.execute(
                f"SELECT body FROM nodes WHERE id IN ({placeholders})", ev).fetchall()
        finally:
            conn.close()
    else:
        rows = []
    blob = " ".join(r[0] or "" for r in rows).lower()
    action_words = {w for w in re.findall(r"[a-z]{5,}", action) if w not in VAGUE_TERMS}
    return not (action_words & set(re.findall(r"[a-z]{5,}", blob)))


def classify(candidate: dict, ids: set[str], topic: str | None = None) -> dict | None:
    """Return a diagnostic dict for a failed candidate, else None.

    `topic` is the candidate file stem (the reflect topic). It selects the
    tool_misuse class: a failed candidate whose topic has an escalation record
    failed in the tool/agent layer, not in the lesson's logic.
    """
    state = candidate.get("state")
    cid = candidate.get("id") or candidate.get("candidate_id")
    if state in ("accepted",):
        return None  # accepted rules are not 'failed candidates'
    quarantine = candidate.get("quarantine") or {}
    missing = quarantine.get("missing", []) if isinstance(quarantine, dict) else []

    unres = [m for m in missing if not m.startswith("triple:")]
    incomplete = [m for m in missing if m.startswith("triple:")]

    # Attribute in strict priority order; the FIRST matching root cause is emitted.
    causes: list[str] = []
    if unres:
        causes.append("retrieval_miss")
    if incomplete:
        causes.append("logical_inconsistency")
    if not causes:
        if _is_vague(candidate, ids):
            causes.append("grounding_gap")

    # tool_misuse: a candidate that is logically healthy (or only grounding-gap)
    # whose topic has an escalation record failed in the tool/agent layer.
    escalated = topic in tool_misuse_topics()
    if escalated and "retrieval_miss" not in causes:
        causes.append("tool_misuse")

    if not causes:
        return None  # a healthy proposed candidate — nothing to attribute

    return {
        "candidate_id": cid,
        "state": state,
        "error_class": causes[0],
        "all_causes": causes,
        "topic": topic,
        "detail": {
            "unresolved_evidence": unres,
            "incomplete_triple_fields": [m.split(":", 1)[1] for m in incomplete],
            "vague": _is_vague(candidate, ids),
            "escalated_topic": escalated,
        },
        "correction": _correction(causes[0], unres, incomplete),
    }


def _correction(cause: str, unres: list[str], incomplete: list[str]) -> str:
    if cause == "retrieval_miss":
        return f"re-retrieve or add a resolving evidence chunk for {unres}; never cite an id that graph.db lacks"
    if cause == "logical_inconsistency":
        return f"complete the failure triple — fill {incomplete} (Condition/Reason/Correction)"
    if cause == "grounding_gap":
        return "rewrite the Action with concrete, keyword-specific terms that appear in the cited chunk bodies; drop vague verbs"
    return "inspect the tool/agent run that produced this candidate before retrying"


def diagnose_candidate_file(path: Path, ids: set[str] | None = None, topic: str | None = None) -> list[dict]:
    ids = ids or _graph_ids()
    topic = topic if topic is not None else path.stem
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            cand = json.loads(line)
        except json.JSONDecodeError:
            continue
        diag = classify(cand, ids, topic)
        if diag is not None:
            out.append(diag)
    return out


def tool_misuse_topics() -> set[str]:
    """Topics that have an escalation record => their failures are tool_misuse, not logic."""
    if not ESCALATIONS.exists():
        return set()
    topics: set[str] = set()
    for line in ESCALATIONS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("event") == "ESCALATE" and obj.get("topic"):
            topics.add(obj["topic"])
    return topics


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("candidate_file", nargs="?", help="path to a candidate jsonl (default: all)")
    ap.add_argument("--out", help="write diagnostics here (default: reflection/diagnostics/<topic>_root_cause.jsonl)")
    args = ap.parse_args()

    ids = _graph_ids()
    if args.candidate_file:
        target = CANDIDATES_DIR / args.candidate_file if not Path(args.candidate_file).is_absolute() else Path(args.candidate_file)
        diags = diagnose_candidate_file(target, ids)
        out = Path(args.out) if args.out else DIAG_DIR / f"{target.stem}_root_cause.jsonl"
    else:
        diags = []
        out = None
        for target in sorted(CANDIDATES_DIR.glob("*.jsonl")):
            d = diagnose_candidate_file(target, ids)
            if d:
                out = DIAG_DIR / f"{target.stem}_root_cause.jsonl"
                out.parent.mkdir(parents=True, exist_ok=True)
                with out.open("w", encoding="utf-8") as f:
                    for dd in d:
                        f.write(json.dumps(dd, ensure_ascii=False) + "\n")
                diags.extend(d)
                print(f"[root_cause] {target.name}: {len(d)} attributed -> {out.relative_to(ROOT)}")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for d in diags:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"[root_cause] {out.name}: {len(diags)} failures attributed")
    for d in diags:
        print(f"  {d['candidate_id']}: {d['error_class']} — {d['correction'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
