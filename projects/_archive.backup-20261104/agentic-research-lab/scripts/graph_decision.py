#!/usr/bin/env python3
"""Decide whether an agent task should consult the knowledge graph.

This is advisory by default: it makes graph use discoverable and records the decision,
without forcing irrelevant retrieval. High-risk knowledge claims are fail-closed.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "knowledge" / "graph" / "generation.json"
TOPICS = ROOT / "knowledge" / "topics.md"
try:
    from agent_trace import emit
except ImportError:
    emit = None

HIGH = ("research", "reflect", "reflection", "knowledge", "evidence", "memory", "graph", "workflow", "architecture", "design", "why", "how")
LOW = ("format", "rename", "status", "compile", "syntax", "typo")

def controlled_topics() -> set[str]:
    if not TOPICS.exists():
        return set()
    return {line[2:].strip().lower() for line in TOPICS.read_text(encoding="utf-8").splitlines() if line.startswith("- ")}


def decide(task: str, task_class: str = "") -> dict:
    text = f"{task_class} {task}".lower()
    topics = controlled_topics()
    topic_hits = sorted(topic for topic in topics if topic and topic in text)
    high = [w for w in HIGH if re.search(rf"\b{re.escape(w)}\b", text)]
    low = [w for w in LOW if re.search(rf"\b{re.escape(w)}\b", text)]
    required = task_class in {"research", "reflection", "repair"} or len(high) >= 2 or len(topic_hits) >= 2
    recommended = required or (bool(high) and not low) or bool(topic_hits)
    reason = "knowledge-bearing task" if required else ("controlled topic match" if topic_hits else ("possible workspace knowledge dependency" if recommended else "local mechanical task"))
    generation = ""
    try:
        generation = json.loads(GEN.read_text(encoding="utf-8"))["generation_id"]
    except (OSError, ValueError, KeyError):
        pass
    result = {"use_graph": recommended, "required": required, "reason": reason,
              "signals": sorted(set(high)), "topic_matches": topic_hits, "graph_generation": generation,
              "next": "query knowledge/graph/ask.py before acting" if recommended else "proceed, but record validation"}
    if emit:
        emit("graph_decision", task_class=task_class, task_summary=task[:300], decision=result)
    return result

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--class", dest="task_class", default="")
    args = ap.parse_args()
    print(json.dumps(decide(args.task, args.task_class), indent=2))
    return 0
if __name__ == "__main__": raise SystemExit(main())
