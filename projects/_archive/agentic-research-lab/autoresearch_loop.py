#!/usr/bin/env python3
"""
autoresearch_loop.py — Autonomous research loop with knowledge-gap detection,
intelligent retrieval, and human escalation when materials are inaccessible.

Modes:
    --mode task      (default) Run gap detection before starting a task
    --mode periodic  Scan all topics in knowledge/topics.md
    --mode escalate  Jump straight to escalation (for re-running after user reply)

Usage:
    python autoresearch_loop.py                          # task mode, default question from frontier
    python autoresearch_loop.py --question "self-evolving agents"
    python autoresearch_loop.py --mode periodic
    python autoresearch_loop.py --mode escalate          # re-check pending requests
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
INBOX = ROOT / "INBOX"
SCRIPTS = ROOT / "scripts"
FRONTIER = ROOT / "frontier"
MANIFEST = FRONTIER / "manifest.json"

# Import our new modules
sys.path.insert(0, str(SCRIPTS))
try:
    from knowledge_gap_detector import detect_gap, GapRecord  # noqa: E402
    from autonomous_retriever import retrieve, RetrieverResult   # noqa: E402
    from material_request import build_request, save_request       # noqa: E402
    from evidence_graph import gate as evidence_gate             # noqa: E402
    from repair_ledger import gate as repair_ledger_gate          # noqa: E402
except ImportError as e:
    print(f"[autoresearch_loop] Import error: {e}", file=sys.stderr)
    sys.exit(2)


def run_cmd(cmd: list[str], cwd: Optional[Path] = None) -> bool:
    print(f"[*] Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd or ROOT))
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print(res.stderr, file=sys.stderr)
    return res.returncode == 0


def run_git_health() -> bool:
    print("[git] Checking working tree cleanliness...")
    if not run_cmd([sys.executable, str(SCRIPTS / "git_worktree.py"), "list"]):
        print("[-] git_worktree list failed.", file=sys.stderr)
        return False
    print("[git] Worktree health OK")
    return True


def get_default_question() -> str:
    """Extract the most recent open-turn question from the frontier manifest."""
    if not MANIFEST.exists():
        return "autonomous agent research loops with knowledge-gap detection"
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        turns = data.get("turns", {})
        open_ids = data.get("open_turn_ids", [])
        for tid in reversed(open_ids[-3:]):
            turn = turns.get(tid, {})
            for key in ("next_action", "question", "issue"):
                val = turn.get(key, "")
                if val and len(val) > 10:
                    return val.strip()
    except Exception:
        pass
    return "autonomous agent research loops with knowledge-gap detection"


def run_gap_detection(question: str) -> tuple[GapRecord, bool]:
    """Run gap detection; returns (record, needs_escalation)."""
    record = detect_gap(question)
    print(f"\n[Gap Detection] Question: {record.question}")
    print(f"  Coverage: {record.coverage_score:.0%} | Severity: {record.severity}")
    print(f"  Deep chunks: {record.deep_chunk_count}/{record.top_chunks_returned}")
    needs_esc = record.severity in ("high", "medium")
    return record, needs_esc


def run_retrieval(question: str, coverage: float) -> RetrieverResult:
    """Attempt autonomous retrieval. Skip if coverage already high."""
    if coverage >= 0.6:
        print("[Retrieval] Coverage sufficient — skipping.")
        return RetrieverResult(
            question=question, sub_queries=[], papers=[],
            coverage_estimate=coverage, no_adequate_sources=False,
        )
    print(f"[Retrieval] Attempting retrieval (coverage={coverage:.0%})...")
    result = retrieve(question)
    print(f"  Papers found: {len(result.papers)} | Coverage estimate: {result.coverage_estimate:.0%}")
    for i, p in enumerate(result.papers[:5], 1):
        print(f"    [{i}] ({p['source_type']}) {p['title'][:80]}")
    return result


def escalate(record: GapRecord, result: RetrieverResult) -> Path:
    """Generate and save a human-readable escalation request."""
    req = build_request(
        record.question,
        coverage_score=record.coverage_score,
        papers_found=[p["title"] for p in result.papers],
        sub_queries=result.sub_queries,
    )
    path = save_request(req)
    print(f"\n{'='*60}", file=sys.stderr)
    print("ESCALATION — human input required:", file=sys.stderr)
    print(f"  Saved to: {path}", file=sys.stderr)
    print(f"  Request ID: {req.request_id}", file=sys.stderr)
    print(f"  Reply with a URL, arXiv ID, or local file path.", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    return path


def ingest_pending_materials() -> int:
    """Check INBOX for newly delivered material and auto-ingest it."""
    pending = sorted(INBOX.glob("_pending_request_*.md"))
    delivered = sorted(INBOX.glob("*_delivered.md"))
    ingested = 0
    for d in delivered:
        slug = d.stem.replace("_delivered", "")
        target = INBOX / f"{slug}.md"
        if not target.exists():
            print(f"[Ingest] Moving {d.name} → {target.name}")
            d.rename(target)
            ingested += 1
    if ingested:
        print(f"[Ingest] {ingested} new file(s) detected. Running quality check + ingestion...", file=sys.stderr)
        run_cmd([sys.executable, str(SCRIPTS / "check_research_quality.py")])
        run_cmd([sys.executable, str(SCRIPTS / "ingest.py")])
        run_cmd([sys.executable, str(ROOT / "knowledge" / "graph" / "build_graph.py")])
    return ingested


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous research loop with gap detection")
    parser.add_argument("--mode", choices=["task", "periodic", "escalate"], default="task")
    parser.add_argument("--question", default=None, help="Override default question")
    parser.add_argument("--threshold", type=float, default=0.6, help="Coverage threshold for escalation")
    args = parser.parse_args()

    print(f"=== AUTONOMOUS RESEARCH LOOP [{args.mode.upper()}] ===")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print()

    # Always try to ingest any newly delivered materials first
    ingest_pending_materials()

    if args.mode == "periodic":
        # Scan all topics as potential gap questions
        topics_file = ROOT / "knowledge" / "topics.md"
        if not topics_file.exists():
            print("[-] knowledge/topics.md not found. Run in --mode task instead.", file=sys.stderr)
            return 1
        topics = [l.strip() for l in topics_file.read_text().splitlines()
                  if l.strip() and not l.startswith("-") and not l.startswith("#")]
        for topic in topics:
            q = f"{topic} autonomous research methodology"
            record, needs_esc = run_gap_detection(q)
            if needs_esc:
                result = run_retrieval(q, record.coverage_score)
                if result.no_adequate_sources:
                    escalate(record, result)
        return 0

    question = args.question or get_default_question()
    print(f"Target question: {question}\n")

    # Phase 1: Gap Detection
    record, needs_esc = run_gap_detection(question)

    if record.severity == "low":
        print("\n[Loop] Knowledge coverage is adequate — proceeding to normal pipeline.\n")
        # Continue with standard pipeline
        if not run_git_health():
            return 1
        if not run_cmd([sys.executable, str(SCRIPTS / "check_manifest.py")]):
            return 1
        if not run_cmd([sys.executable, str(ROOT / "knowledge" / "graph" / "build_graph.py")]):
            return 1
        return 0

    # Phase 2: Autonomous Retrieval
    result = run_retrieval(question, record.coverage_score)

    # Phase 3: Escalate if still inadequate
    if result.no_adequate_sources:
        escalate(record, result)
        print("\n[Loop] Paused — awaiting human-provided material.", file=sys.stderr)
        return 2  # Non-zero exit signals that human intervention was triggered

    # Phase 4: Evidence/workflow graph gate before ingestion
    graph_ok, graph_report = evidence_gate(repair=True)
    ledger_ok, ledger_report = repair_ledger_gate()
    print(f"[Evidence Graph] status={graph_report['status']} issues={len(graph_report['issues'])}")
    print(f"[Repair Ledger] status={ledger_report['status']} events={ledger_report['ledger_events']}")
    if not graph_ok or not ledger_ok:
        print("[Loop] Self-healing gate blocked acceptance; repair state is quarantined.", file=sys.stderr)
        return 4

    # Phase 5: Quality-check retrieved material before ingesting
    print("\n[Loop] Checking research quality on retrieved material...", file=sys.stderr)
    qc = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_research_quality.py")],
        capture_output=True, text=True, cwd=str(ROOT), timeout=120
    )
    has_hard_errors = "FAIL — hard errors" in qc.stdout or qc.returncode != 0
    if has_hard_errors:
        print("[Loop] Quality check found hard errors — material deposited to INBOX for enrichment.\n"
              "Run `python scripts/check_research_quality.py` to see what needs fixing.\n"
              "After enriching, re-run this loop to ingest.", file=sys.stderr)
        print(qc.stdout)
        return 3  # Signal: materials need human/enrichment attention
    # All quality checks passed — safe to ingest
    run_cmd([sys.executable, str(SCRIPTS / "ingest.py")])
    run_cmd([sys.executable, str(ROOT / "knowledge" / "graph" / "build_graph.py")])
    print("\n=== AUTONOMOUS RESEARCH LOOP COMPLETED ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
