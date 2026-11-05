#!/usr/bin/env python3
"""Automatic task gateway: decide graph use and produce agent context."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
try:
    from agent_trace import emit
except ImportError:
    emit = None

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--class", dest="task_class", default="")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--context-file", type=Path)
    args = ap.parse_args()
    decision_cmd = [sys.executable, str(ROOT / "scripts" / "graph_decision.py"), args.task, "--class", args.task_class]
    decision = json.loads(subprocess.check_output(decision_cmd, cwd=ROOT, text=True))
    context = {"task": args.task, "task_class": args.task_class, "decision": decision, "results": []}
    if decision["use_graph"]:
        query = subprocess.run([sys.executable, str(ROOT / "knowledge" / "graph" / "ask.py"), args.task, "--limit", str(args.limit)], cwd=ROOT, capture_output=True, text=True)
        if query.returncode and decision["required"]:
            print(query.stderr, file=sys.stderr)
            return query.returncode
        context["results_text"] = query.stdout
        context["query_status"] = query.returncode
        warn = subprocess.run([sys.executable, str(ROOT / "scripts" / "warn.py"), args.task, "--limit", "3"], cwd=ROOT, capture_output=True, text=True)
        context["warnings"] = json.loads(warn.stdout) if warn.returncode == 0 else []
        if emit:
            emit("retrieval", task_class=args.task_class, task_summary=args.task[:300],
                 query=args.task, limit=args.limit,
                 status="ok" if not query.returncode else "failed")
    else:
        context["results_text"] = ""
        context["query_status"] = None
        context["warnings"] = []
    text = json.dumps(context, indent=2, ensure_ascii=False)
    if args.context_file:
        args.context_file.write_text(text + "\n", encoding="utf-8")
        if emit:
            emit("artifact", task_class=args.task_class, task_summary=args.task[:300],
                 artifact=str(args.context_file), status="observed")
    print(text)
    return 0
if __name__ == "__main__": raise SystemExit(main())
