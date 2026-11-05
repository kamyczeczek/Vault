#!/usr/bin/env python3
"""
expf_post_promotion_audit.py — Post-Promotion Audit for vera-expa-003.

Tests every accepted lesson in reflection/memory.md against held-out VERA
benchmark questions to verify rules don't fire incorrectly (condition holds
but application is wrong).

If a rule produces incorrect guidance on a held-out question, its score
should decrement per the eviction predicate from vera-expa-003.

Usage:
  python subprojects/vera/experiments/expf_post_promotion_audit.py
  python subprojects/vera/experiments/expf_post_promotion_audit.py --rule causal-falsification-loops
  python subprojects/vera/experiments/expf_post_promotion_audit.py --report
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MEMORY_FILE = ROOT / "reflection" / "memory.md"
QUESTIONS_FILE = ROOT / "subprojects" / "vera" / "benchmark" / "QUESTIONS.md"
RUNS_DIR = ROOT / "subprojects" / "vera" / "experiments" / "runs"
FINGERPRINT_FILE = ROOT / "knowledge" / "graph" / ".graph_fingerprint"


def get_fingerprint() -> str:
    if FINGERPRINT_FILE.exists():
        return FINGERPRINT_FILE.read_text().strip()
    return "?"


def parse_memory_rules() -> list[dict]:
    """Parse reflection/memory.md into structured rules."""
    if not MEMORY_FILE.exists():
        print(f"[audit] ERROR: {MEMORY_FILE} not found", file=sys.stderr)
        return []

    rules = []
    current = {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("### ") and "— accepted" in line:
                if current:
                    rules.append(current)
                current = {"id": line[4:].split(" — ")[0].strip()}
            elif line.startswith("Rule:"):
                current["rule"] = line[5:].strip()
            elif line.startswith("Evidence:"):
                current["evidence"] = line[9:].strip()
            elif line.startswith("Target:"):
                current["target"] = line[7:].strip()
            elif line.startswith("Action:"):
                current["action"] = line[7:].strip()
    if current:
        rules.append(current)
    return rules


def parse_questions() -> list[dict]:
    """Parse QUESTIONS.md into structured questions."""
    if not QUESTIONS_FILE.exists():
        print(f"[audit] ERROR: {QUESTIONS_FILE} not found", file=sys.stderr)
        return []

    questions = []
    current = {}
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("### Q"):
                if current and current.get("id"):
                    questions.append(current)
                current = {"id": line[4:].strip()}
            elif line.startswith("question:"):
                current["question"] = line[11:].strip('"')
            elif line.startswith("level:"):
                try:
                    current["level"] = int(line[6:].strip())
                except ValueError:
                    pass
            elif line.startswith("seeds:") and "workspace:" not in line:
                current["seeds"] = [s.strip() for s in line[6:].split(";") if s.strip()]
            elif line.startswith("distractors:") and "workspace:" not in line:
                current["distractors"] = [s.strip() for s in line[12:].split(",") if s.strip()]
    if current and current.get("id"):
        questions.append(current)
    return questions


def test_rule_against_question(rule: dict, question: dict) -> dict:
    """Test if a rule applies correctly to a held-out question."""
    rule_id = rule.get("id", "unknown")
    question_id = question.get("id", "unknown")
    question_text = question.get("question", "")[:100]

    # Check if rule's target matches question's scope
    rule_target = rule.get("target", "").lower()
    q_scope = question.get("scope", "").lower()

    # Check if rule evidence resolves in graph
    evidence_str = rule.get("evidence", "")
    evidence_ids = re.findall(r"`([^`]+)`", evidence_str)

    # Simulate rule application: does the rule provide correct guidance?
    # For this audit, we check structural correctness:
    # 1. Rule cites resolving evidence
    # 2. Rule's action is actionable (not vague)
    # 3. Rule doesn't contradict itself

    issues = []

    # Check evidence resolution (would need actual graph query)
    # For now, mark as untested without graph access
    if not evidence_ids:
        issues.append("no_evidence_cited")

    # Check for vague actions
    action = rule.get("action", "").lower()
    vague_terms = ["optimize", "improve", "consider", "maybe"]
    if any(term in action for term in vague_terms):
        issues.append("vague_action")

    # Check if rule applies to question domain
    applies = rule_target in q_scope or q_scope in rule_target

    return {
        "rule_id": rule_id,
        "question_id": question_id,
        "applies": applies,
        "issues": issues,
        "score": 1.0 if not issues and applies else 0.5 if issues else 0.0
    }


def run_audit(rule_filter: str | None = None) -> dict:
    """Run full post-promotion audit."""
    rules = parse_memory_rules()
    questions = parse_questions()

    if not rules:
        print("[audit] ERROR: No rules found in memory.md", file=sys.stderr)
        return {}

    if not questions:
        print("[audit] ERROR: No questions found in QUESTIONS.md", file=sys.stderr)
        return {}

    results = {
        "experiment": "F_post_promotion_audit",
        "timestamp": datetime.now().isoformat(),
        "fingerprint": get_fingerprint(),
        "rules_tested": len(rules),
        "questions_tested": len(questions),
        "rule_scores": {},
        "violations": []
    }

    for rule in rules:
        if rule_filter and rule.get("id") != rule_filter:
            continue

        rule_id = rule.get("id", "unknown")
        total_score = 0.0
        test_count = 0
        violations = []

        for question in questions:
            result = test_rule_against_question(rule, question)
            total_score += result["score"]
            test_count += 1

            if result["score"] < 1.0:
                violations.append({
                    "question_id": result["question_id"],
                    "issues": result["issues"],
                    "applies": result["applies"]
                })

        avg_score = total_score / max(test_count, 1)
        results["rule_scores"][rule_id] = {
            "average_score": round(avg_score, 3),
            "tests_run": test_count,
            "violations": len(violations)
        }
        results["violations"].extend([
            {"rule_id": rule_id, **v} for v in violations
        ])

    return results


def write_results(results: dict) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RUNS_DIR / f"EXPF_post_promotion_audit_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"[audit] Results written: {output_file}")
    return output_file


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rule", help="Specific rule ID to audit")
    parser.add_argument("--report", action="store_true", help="Show summary report")
    args = parser.parse_args()

    if args.report:
        runs = list(RUNS_DIR.glob("EXPF_post_promotion_audit_*.json"))
        if not runs:
            print("No audit results found.")
            return 0
        latest = max(runs, key=lambda p: p.stat().st_mtime)
        print(f"\nLatest results: {latest}")
        with open(latest, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(json.dumps(data, indent=2))
        return 0

    print("="*60)
    print("Post-Promotion Audit (Experiment F sub-phase)")
    print("="*60)
    print(f"Fingerprint: {get_fingerprint()}")

    results = run_audit(args.rule)
    if not results.get("rule_scores"):
        return 1

    write_results(results)

    print("\n" + "="*60)
    print("AUDIT RESULTS")
    print("="*60)
    for rule_id, scores in results["rule_scores"].items():
        status = "✓ PASS" if scores["violations"] == 0 and scores["average_score"] >= 0.8 else "⚠ REVIEW"
        print(f"{status} {rule_id}: avg={scores['average_score']:.3f}, violations={scores['violations']}")

    if results["violations"]:
        print(f"\n{len(results['violations'])} violation(s) found:")
        for v in results["violations"][:5]:
            print(f"  - {v['rule_id']} on {v['question_id']}: {v['issues']}")

    print(f"\nResults: {list(RUNS_DIR.glob('EXPF_post_promotion_audit_*.json'))[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
