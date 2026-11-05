#!/usr/bin/env python3
"""
material_request.py — Generates structured human-readable requests when
the autonomous retriever cannot find adequate sources.

Template-based escalation that tells the user exactly what is needed and why.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "INBOX"


@dataclass
class MaterialRequest:
    timestamp: str
    question: str
    justification: str
    what_we_need: str
    suggested_queries: list[str]
    suggested_sources: list[str]
    impact_if_missing: str
    request_id: str


TEMPLATE = """\
## Research Gap Escalation — {request_id}

**Detected at:** {timestamp}

---

### Question Under Investigation
{question}

### Why This Matters
{justification}

### What We Need
{what_we_need}

### Suggested Search Queries
{queries_bullets}

### Where to Look
{suggestions_bullets}

### Impact If Missing
{impact}

---
*Generated autonomously by the Agentic Research Lab. Reply with a URL, arXiv ID, or file path and the loop will resume automatically.*
"""


def render_request(req: MaterialRequest) -> str:
    queries_bullets = "\n".join(f"- `{q}`" for q in req.suggested_queries) or "- *(none)*"
    suggestions_bullets = "\n".join(f"- {s}" for s in req.suggested_sources) or "- *(none)*"
    return TEMPLATE.format(
        request_id=req.request_id,
        timestamp=req.timestamp,
        question=req.question,
        justification=req.justification,
        what_we_need=req.what_we_need,
        queries_bullets=queries_bullets,
        suggestions_bullets=suggestions_bullets,
        impact=req.impact_if_missing,
    )


def build_request(
    question: str,
    *,
    coverage_score: float,
    papers_found: list[str] | None = None,
    sub_queries: list[str] | None = None,
    justification: str | None = None,
) -> MaterialRequest:
    papers_str = "\n".join(f"  - {p}" for p in (papers_found or [])) or "  *(none retrieved)*"
    queries_str = "\n".join(f"  - `{q}`" for q in (sub_queries or [question])) or "  - `" + question + "`"

    return MaterialRequest(
        timestamp=datetime.utcnow().isoformat() + "Z",
        question=question,
        justification=justification or (
            f"Corpus coverage for '{question}' is only {coverage_score:.0%}. "
            "Without additional sources the analysis risk hallucination and shallow synthesis."
        ),
        what_we_need=f"Primary-source material (paper, preprint, or documentation) addressing: {question}\n\nPapers already attempted:\n{papers_str}",
        suggested_queries=[question] + (sub_queries or []),
        suggested_sources=[
            "arXiv: https://arxiv.org/search/?query=" + question.replace(" ", "+"),
            "Semantic Scholar: https://www.semanticscholar.org/search?q=" + question.replace(" ", "+"),
            "OpenAlex: https://openalex.org/?q=" + question.replace(" ", "+"),
        ],
        impact_if_missing=(
            f"Continuing without this evidence risks producing analysis grounded in speculation rather than empirical findings. "
            "The resulting report would be flagged as low-confidence by `check_research_quality.py`."
        ),
        request_id=f"REQ-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
    )


def save_request(req: MaterialRequest) -> Path:
    INBOX.mkdir(parents=True, exist_ok=True)
    path = INBOX / f"_pending_request_{req.request_id}.md"
    path.write_text(render_request(req), encoding="utf-8")
    # Also append a JSON log for machine-readable tracking
    log_path = INBOX / "_escalation_log.jsonl"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(req)) + "\n")
    return path


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("question", help="The research question that hit a gap")
    parser.add_argument("--coverage", type=float, required=True, help="Coverage score from detector (0–1)")
    parser.add_argument("--papers-found", nargs="*", default=[], help="Titles of papers already tried")
    parser.add_argument("--sub-queries", nargs="*", default=[], help="Sub-queries that were tried")
    parser.add_argument("--justification", default=None, help="Override auto-generated justification")
    parser.add_argument("--output", default=None, help="Custom output path")
    args = parser.parse_args()

    req = build_request(
        args.question,
        coverage_score=args.coverage,
        papers_found=args.papers_found,
        sub_queries=args.sub_queries,
        justification=args.justification,
    )

    out_path = Path(args.output) if args.output else save_request(req)
    print(render_request(req))
    print(f"\n[Saved to {out_path}]", file=sys.stderr)

    # Exit 1 signals that human input is required
    return 1


if __name__ == "__main__":
    sys.exit(main())
