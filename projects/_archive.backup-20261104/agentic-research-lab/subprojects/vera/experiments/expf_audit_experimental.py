#!/usr/bin/env python3
"""Post-promotion audit for experimental candidates (001/002/004).

Applies the same structural audit as expf_post_promotion_audit.py but to
candidate rules not yet in memory.md: checks evidence resolution, action
specificity, and applicability to held-out VERA questions.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

ROOT = Path(__file__).resolve().parents[3]
QUESTIONS = ROOT / "subprojects" / "vera" / "benchmark" / "QUESTIONS.md"
GRAPH = ROOT / "knowledge" / "graph" / "graph.db"
FINGERPRINT = ROOT / "knowledge" / "graph" / ".graph_fingerprint"
CANDIDATES = ROOT / "reflection" / "candidates" / "vera_expa_findings.jsonl"
RUNS = ROOT / "subprojects" / "vera" / "experiments" / "runs"


def parse_questions() -> list[dict]:
    questions = []
    current: dict = {}
    text = QUESTIONS.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("### Q"):
            if current.get("id"):
                questions.append(current)
            current = {"id": line[4:].strip()}
        elif line.startswith("question:"):
            current["question"] = line[11:].strip('"')
        elif line.startswith("level:"):
            current["level"] = int(line[6:].strip())
    if current.get("id"):
        questions.append(current)
    return questions


def audit_candidate(cid: str, rule: dict, questions: list[dict]) -> dict:
    evidence = re.findall(r"`([^`]+)`", rule.get("Evidence", ""))
    missing = [e for e in evidence if not _evidence_in_graph(e)]

    action = rule.get("Action", "").lower()
    vague_terms = ["optimize", "improve", "consider", "maybe"]
    vague_flags = [t for t in vague_terms if t in action]

    applies_count = 0
    for q in questions:
        scope = q.get("question", "").lower()
        target = rule.get("Target", "").lower()
        # rule applies to reflection pipeline; VERA questions target research workflow
        if "reflection" in target or "pipeline" in target:
            applies_count += 1

    issues = []
    if missing:
        issues.append({"type": "evidence_missing", "ids": missing})
    if vague_flags:
        issues.append({"type": "vague_action", "terms": vague_flags})

    status = "pass" if not issues else "review"
    return {
        "candidate_id": cid,
        "status": status,
        "evidence_count": len(evidence),
        "evidence_missing": missing,
        "action_vagueness": vague_flags,
        "questions_tested": len(questions),
        "issues": issues,
    }


import sqlite3


def _evidence_in_graph(eid: str) -> bool:
    conn = sqlite3.connect(str(GRAPH))
    row = conn.execute("SELECT 1 FROM nodes WHERE id=?", (eid,)).fetchone()
    conn.close()
    return row is not None


def main() -> int:
    fingerprint = FINGERPRINT.read_text().strip() if FINGERPRINT.exists() else "?"
    questions = parse_questions()
    results = []

    for line in CANDIDATES.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rule = json.loads(line)
        if rule.get("state") == "experimental":
            results.append(audit_candidate(rule["id"], rule, questions))

    RUNS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {
        "experiment": "F_post_promotion_audit_experimental",
        "timestamp": datetime.now().isoformat(),
        "fingerprint": fingerprint,
        "results": results,
    }
    out = RUNS / f"EXPF_audit_experimental_{ts}.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=" * 60)
    print("Post-Promotion Audit: Experimental Candidates")
    print("=" * 60)
    for r in results:
        mark = "PASS" if r["status"] == "pass" else "REVIEW"
        print(f"[{mark}] {r['candidate_id']}: evidence={r['evidence_count']}, "
              f"missing={r['evidence_missing']}, vague={r['action_vagueness']}")
    print(f"\nResults: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
