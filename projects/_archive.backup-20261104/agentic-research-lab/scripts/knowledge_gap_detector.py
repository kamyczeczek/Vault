#!/usr/bin/env python3
"""
knowledge_gap_detector.py — Detects knowledge gaps by querying the corpus
and scoring coverage against a target question.

Output: GapRecord (JSON) written to INBOX/_gap_<timestamp>.jsonl
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "INBOX"


@dataclass
class GapRecord:
    question: str
    coverage_score: float      # 0.0 – 1.0
    top_chunks_returned: int
    deep_chunk_count: int      # chunks with technical signal
    missing_evidence: list[str]
    tags: list[str]
    severity: str              # "high" | "medium" | "low"
    top_hits_preview: list[str]


def run_ask(query: str, limit: int = 10) -> tuple[list[dict], int]:
    """Run ask.py and return (rows, exit_code)."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "knowledge" / "graph" / "ask.py"),
         query, "--limit", str(limit)],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    rows: list[dict] = []
    try:
        data = json.loads(result.stdout)
        rows = data.get("items", []) if isinstance(data, dict) else []
    except json.JSONDecodeError:
        pass
    # Also parse markdown table output as fallback
    if not rows:
        for line in result.stdout.splitlines():
            if line.startswith("| #") or line.strip().startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 3 and re.match(r"^\d+$", parts[0]):
                rows.append({"id": parts[1], "path": parts[2], "snippet": parts[3] if len(parts) > 3 else ""})
    return rows, result.returncode


def has_deep_signal(text: str) -> bool:
    """Heuristic: does this chunk contain technical depth?"""
    tech_signals = [
        r"\b(algorithm|architecture|framework|pipeline|protocol)\b",
        r"\b(methodology|empirical|experimental|evaluation)\b",
        r"\b(loss|gradient|optimization|training)\b",
        r"\b(agent|retrieval|memory|planning|reflection)\b",
        r"\b(security|threat|adversarial|sanitiz)\b",
        r"\b(hard[- ]gate|soft[- ]guidance|constraint)\b",
        r"\b(MCTS|tree.search|reinforcement)\b",
        r"\b(arxiv|doi|peer.?review|publication)\b",
        r"\b(\d{4}[\.\-]\d{4,7}|arXiv)\b",
        r"\b(token|embedding|vector|neural)\b",
    ]
    text_lower = text.lower()
    return sum(1 for pat in tech_signals if re.search(pat, text_lower)) >= 2


def detect_gap(
    question: str,
    *,
    threshold: float = 0.6,
    limit: int = 10,
    tags: Optional[list[str]] = None,
) -> GapRecord:
    rows, rc = run_ask(question, limit=limit)
    total = len(rows)
    deep_chunks = [r for r in rows if has_deep_signal(r.get("snippet", "") + " " + r.get("text", ""))]
    deep_count = len(deep_chunks)
    # Coverage: weight deep chunks more heavily
    coverage = min(1.0, (deep_count * 1.5 + (total - deep_count)) / max(limit, 1))
    coverage = round(coverage, 2)

    missing = [r["id"] for r in rows if not has_deep_signal(r.get("snippet", "") + " " + r.get("text", ""))]

    if coverage < 0.3:
        severity = "high"
    elif coverage < threshold:
        severity = "medium"
    else:
        severity = "low"

    preview = [f"{r.get('id','?')}: {r.get('snippet', r.get('text',''))[:120]}" for r in rows[:5]]

    return GapRecord(
        question=question,
        coverage_score=coverage,
        top_chunks_returned=total,
        deep_chunk_count=deep_count,
        missing_evidence=missing[:10],
        tags=tags or [],
        severity=severity,
        top_hits_preview=preview,
    )


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("question", help="Research question to evaluate")
    parser.add_argument("--tags", default="", help="Comma-separated topic tags")
    parser.add_argument("--threshold", type=float, default=0.6)
    parser.add_argument("--output", help="Output path (default: INBOX/_gap_<ts>.jsonl)")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    record = detect_gap(args.question, threshold=args.threshold, tags=tags)
    print(json.dumps(asdict(record), indent=2))

    out_path = Path(args.output) if args.output else INBOX / f"_gap_{int(datetime.now().timestamp())}.jsonl"
    INBOX.mkdir(parents=True, exist_ok=True)
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record)) + "\n")
    print(f"\n[Gap detector] Score={record.coverage_score}, Severity={record.severity}", file=sys.stderr)
    print(f"[Gap detector] Saved to {out_path}", file=sys.stderr)
    return 0 if record.severity == "low" else 1


if __name__ == "__main__":
    sys.exit(main())
