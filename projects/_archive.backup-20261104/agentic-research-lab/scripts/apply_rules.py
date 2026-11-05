#!/usr/bin/env python3
"""apply_rules.py — Heuristic invocation and rule binding engine.

Bridges the gap between stored metacognitive knowledge (reflection/memory.md)
and actual agent execution. Dynamically binds accepted rules and specialized
skills to tasks, stages, or execution contexts, and logs invocation telemetry.

Usage:
    python scripts/apply_rules.py --task "research new papers on agentic memory"
    python scripts/apply_rules.py --stage 01_inbox
    python scripts/apply_rules.py --skill research
    python scripts/apply_rules.py --format json --task "refactor codebase"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from memory_rules import parse_accepted_rules
ROOT = Path(__file__).resolve().parents[1]
MEMORY_FILE = ROOT / "reflection" / "memory.md"
EVENTS_LOG = ROOT / "reflection" / "events.jsonl"
# Skills are workspace-shared and live at the root. This project holds no copy:
# a skill has one home, and a project that forked one would drift from it.
SKILLS_DIR = ROOT.parents[1] / "skills"
# Target alias and keyword mappings for dynamic semantic resolution
TARGET_KEYWORDS = {
    "inbox": ["inbox", "ingest", "intake", "raw", "source", "download", "paper", "arxiv"],
    "expand": ["expand", "search", "literature", "find", "explore", "tree-search", "mcts", "reasoning"],
    "corpus": ["corpus", "chunk", "markdown", "provenance", "manifest"],
    "graph": ["graph", "db", "sqlite", "fts5", "digest", "fingerprint", "sandbox", "isolation"],
    "reflect": ["reflect", "digest", "candidate", "peer-review", "rubric", "review", "synthesize"],
    "self-evolution": ["evolution", "self-evolve", "meta", "upgrade", "contract", "prompt", "gate"],
    "multi-agent": ["multi-agent", "escalation", "handoff", "subagent", "delegate", "coordination"],
    "general": ["plan", "design", "module", "code", "architecture", "refactor", "bug", "fix"],
}


def parse_memory_rules() -> list[dict]:
    """Parse only explicit canonical accepted rules from reflection/memory.md."""
    rules = parse_accepted_rules(MEMORY_FILE, on_rejection=lambda r: print(r.message()))
    return [rule.as_dict() for rule in rules]


def match_rules(rules: list[dict], query: str, stage: str | None = None, skill: str | None = None) -> list[dict]:
    """Score and match rules against task query, stage, or skill."""
    matched = []
    q_lower = (query or "").lower()
    stage_lower = (stage or "").lower()
    skill_lower = (skill or "").lower()

    for r in rules:
        score = 0
        tgt = r["target"].lower()

        # Direct target matching
        if stage_lower and (tgt in stage_lower or any(k in stage_lower for k in TARGET_KEYWORDS.get(tgt, []))):
            score += 10
        if skill_lower and (tgt in skill_lower or any(k in skill_lower for k in TARGET_KEYWORDS.get(tgt, []))):
            score += 8

        # Keyword matching against task query
        if q_lower:
            # Check target keywords
            for kw in TARGET_KEYWORDS.get(tgt, []):
                if kw in q_lower:
                    score += 5

            # Check rule text overlap
            rule_text = f"{r['id']} {r['name']} {r['claim']} {r['action']}".lower()
            words = [w for w in re.findall(r"\w+", q_lower) if len(w) > 3]
            for w in words:
                if w in rule_text:
                    score += 2

        # General rules always apply with base score if no specific rules match
        if tgt == "general":
            score += 1

        if score > 0:
            matched.append((score, r))

    matched.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in matched]


def log_invocation(context: dict) -> None:
    """Log heuristic invocation event to reflection/events.jsonl."""
    event = {
        "timestamp": time.time(),
        "event": "heuristic_invocation",
        "task": context.get("task"),
        "stage": context.get("stage"),
        "skill": context.get("skill"),
        "applied_rules": [r["id"] for r in context.get("rules", [])],
        "count": len(context.get("rules", [])),
    }
    try:
        EVENTS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with EVENTS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except OSError:
        pass


def format_rules_markdown(matched: list[dict], query_context: str) -> str:
    """Format matched rules as actionable instructions for an agent prompt."""
    if not matched:
        return f"<!-- No specific memory rules found for context: {query_context} -->"

    out = [
        f"### Applied Heuristics & Rules (Context: {query_context})",
        "> In compliance with Interpretable Context Methodology (ICM) and `reflection/memory.md`:",
        ""
    ]
    for r in matched:
        out.append(f"- **[{r['id']}] {r['name']}** (Target: `{r['target']}`)")
        if r['action']:
            out.append(f"  - **Action Requirement**: {r['action']}")
        if r['evidence']:
            out.append(f"  - *Grounded in*: `{'`, `'.join(r['evidence'])}`")
    out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bind and apply workspace memory heuristics to execution context.")
    parser.add_argument("--task", help="Natural language task or command intent")
    parser.add_argument("--stage", help="Stage name (e.g. 01_inbox, 04_reflect)")
    parser.add_argument("--skill", help="Skill name (e.g. research, implement)")
    parser.add_argument("--format", choices=["markdown", "prompt", "json", "ids"], default="markdown", help="Output format")
    parser.add_argument("--log", action="store_true", default=True, help="Record telemetry event (default True)")
    parser.add_argument("--no-log", dest="log", action="store_false", help="Disable telemetry logging")
    args = parser.parse_args()

    rules = parse_memory_rules()
    if not rules:
        if args.format == "json":
            print(json.dumps({"rules": [], "count": 0}))
        else:
            print("No active accepted rules found in reflection/memory.md.")
        return 0

    query_str = args.task or ""
    matched = match_rules(rules, query=query_str, stage=args.stage, skill=args.skill)

    if args.log and matched:
        log_invocation({
            "task": args.task,
            "stage": args.stage,
            "skill": args.skill,
            "rules": matched,
        })

    if args.format == "json":
        print(json.dumps({"matched_rules": matched, "count": len(matched)}, indent=2))
    elif args.format == "ids":
        print(" ".join(r["id"] for r in matched))
    else:
        ctx_desc = args.task or args.stage or args.skill or "General Workspace"
        print(format_rules_markdown(matched, ctx_desc))

    return 0


if __name__ == "__main__":
    sys.exit(main())
