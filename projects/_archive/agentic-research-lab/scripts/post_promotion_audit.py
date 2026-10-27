#!/usr/bin/env python3
"""post_promotion_audit.py — held-out audit of an accepted rule (vera-expa-002/003).

Runs the post-promotion audit loop: evidence resolution, action specificity,
reachability of seeded questions, and (when the VERA benchmark is present)
held-out question applicability. Records the verdict in the memory_scores
sidecar so the eviction predicate can mechanically decrement stale rules.

Exit codes: 0 = pass, 1 = review (decrement applied), 2 = prerequisite missing.
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "knowledge" / "graph" / "graph.db"
MEMORY = ROOT / "reflection" / "memory.md"
SEEDS = ROOT / "reflection" / "reachability-seed.jsonl"
QUESTIONS = ROOT / "subprojects" / "vera" / "benchmark" / "QUESTIONS.md"
CANDIDATES_DIR = ROOT / "reflection" / "candidates"

sys.path.insert(0, str(ROOT / "scripts"))

VAGUE_TERMS = ["optimize", "improve", "consider", "maybe", "promote when externally verified"]


def _parse_rule(rule_id: str) -> dict | None:
    """Locate a rule id in memory.md or candidate jsonl files."""
    if MEMORY.exists():
        text = MEMORY.read_text(encoding="utf-8")
        m = re.search(rf"^### {re.escape(rule_id)} — accepted\n(.*?)(?=^### |\Z)", text, re.MULTILINE | re.DOTALL)
        if m:
            body = m.group(1)
            fields = {}
            for line in body.splitlines():
                mm = re.match(r"^(Rule|Evidence|Target|Action):\s*(.*)", line.strip())
                if mm:
                    fields[mm.group(1)] = mm.group(2).strip()
            if fields.get("Rule"):
                return {"id": rule_id, **fields}
    for jl in sorted(CANDIDATES_DIR.glob("*.jsonl")):
        for line in jl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            if obj.get("id") == rule_id or obj.get("candidate_id") == rule_id:
                return {"id": rule_id, **{k: obj[k] for k in ("Rule", "Evidence", "Target", "Action") if k in obj}}
    return None


def _evidence_in_graph(eid: str, ids: set[str]) -> bool:
    return eid in ids


def audit(rule_id: str) -> dict:
    rule = _parse_rule(rule_id)
    if rule is None:
        return {"rule_id": rule_id, "status": "fail", "issues": [{"type": "rule_not_found"}]}

    conn = sqlite3.connect(str(GRAPH))
    ids = {r[0] for r in conn.execute("SELECT id FROM nodes")}
    conn.close()

    evidence = re.findall(r"`([^`]+)`", rule.get("Evidence", ""))
    missing = [e for e in evidence if not _evidence_in_graph(e, ids)]

    action = rule.get("Action", "").lower()
    vague = [t for t in VAGUE_TERMS if t in action]

    issues: list[dict] = []
    if missing:
        issues.append({"type": "evidence_missing", "ids": missing})
    if vague:
        issues.append({"type": "vague_action", "terms": vague})

    # Reachability seeds (standing held-out probe): every seed question must still
    # resolve at least one chunk in the live graph.
    seed_failures: list[str] = []
    if SEEDS.exists():
        import subprocess
        ok = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_reachability.py")],
                            capture_output=True, text=True)
        if ok.returncode != 0:
            seed_failures = [l for l in ok.stdout.splitlines() if "UNREACHABLE" in l]
            issues.append({"type": "reachability_regression", "count": len(seed_failures)})

    held_out = 0
    if QUESTIONS.exists():
        q_text = QUESTIONS.read_text(encoding="utf-8")
        held_out = len(re.findall(r"^\s*question:", q_text, re.MULTILINE))
        target = rule.get("Target", "").lower()
        if not target:
            issues.append({"type": "missing_target", "detail": "cannot judge held-out applicability"})

    status = "pass" if not issues else "fail"
    return {
        "rule_id": rule_id,
        "status": status,
        "evidence_count": len(evidence),
        "evidence_missing": missing,
        "action_vagueness": vague,
        "reachability_failures": seed_failures,
        "held_out_questions": held_out,
        "issues": issues,
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rule_id", nargs="?", help="rule/candidate id to audit")
    ap.add_argument("--all", action="store_true", help="audit every accepted rule in memory.md")
    ap.add_argument("--record", action="store_true", help="record verdict in memory_scores.jsonl")
    args = ap.parse_args()

    import memory_scores

    rule_ids: list[str] = []
    if args.all:
        rule_ids = memory_scores._parse_rule_ids()
    elif args.rule_id:
        rule_ids = [args.rule_id]
    else:
        ap.print_help()
        return 2

    results = []
    for rid in rule_ids:
        res = audit(rid)
        results.append(res)
        print(f"[{rid}] {res['status'].upper()}: evidence={res['evidence_count']} "
              f"missing={len(res['evidence_missing'])} vague={res['action_vagueness']}")
        for issue in res["issues"]:
            print(f"   issue: {issue}")
        if args.record:
            entry = memory_scores.record_audit(rid, res["status"], {
                "f1_status": res["status"],
                "issues": [i.get("type") for i in res["issues"]],
            })
            print(f"   score now: {entry['score']}")

    bad = sum(1 for r in results if r["status"] != "pass")
    print(f"[post_promotion_audit] {len(results)} audited, {bad} failing")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
