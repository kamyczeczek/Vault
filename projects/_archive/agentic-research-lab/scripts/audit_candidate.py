#!/usr/bin/env python3
"""audit_candidate.py — Independent content auditor for reflection candidates (W-AUDIT).

Validates that a reflection candidate is not just structurally sound (resolving IDs),
but that its cited evidence chunks actually contain textual backing for the claim.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "reflection" / "candidates"
DB = ROOT / "knowledge" / "graph" / "graph.db"


def find_candidate(cid: str) -> tuple[Path | None, dict | None]:
    for jl in CANDIDATES.glob("*.jsonl"):
        for line in jl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                if obj.get("id") == cid:
                    return jl, obj
            except Exception:
                continue
    return None, None

_STOPWORDS = {
    "would", "could", "should", "these", "their", "there", "which", "while",
    "because", "however", "provide", "process", "system", "result", "other",
    "about", "into", "over", "under", "also", "more", "than", "then",
    "when", "this", "that", "with", "from", "have", "been", "being", "both",
    "each", "some", "many", "such", "only", "used", "using", "uses", "make",
}


def _suggest_chunk_terms(text: str, limit: int = 8) -> list[str]:
    from collections import Counter

    freq = Counter(w for w in re.findall(r"[a-z]{5,}", (text or "").lower()) if w not in _STOPWORDS)
    return [w for w, _ in freq.most_common(limit)]


def audit_claim_grounding(claim: str, evidence_ids: list[str]) -> tuple[bool, list[str]]:
    """Check that evidence chunks exist and contain relevant keywords from the claim."""
    if not DB.exists():
        return False, ["graph.db missing"]

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    issues = []

    words = [w.lower() for w in claim.replace("/", " ").replace("-", " ").split() if len(w) > 3]
    if not words:
        words = [claim.lower()]

    for eid in evidence_ids:
        row = conn.execute("SELECT id, title, body FROM nodes WHERE id = ?", (eid,)).fetchone()
        if not row:
            issues.append(f"Evidence ID `{eid}` not found in graph.db")
            continue

        body = (row["body"] or "").lower()
        title = (row["title"] or "").lower()
        full_text = f"{title}\n{body}"

        # Count keyword overlap between claim and evidence chunk
        matches = [w for w in words if w in full_text]
        if not matches:
            suggestions = _suggest_chunk_terms(full_text)
            hint = f" — suggest weaving in chunk terms: {', '.join(suggestions)}" if suggestions else ""
            issues.append(f"Chunk `{eid}` shares zero meaningful keywords with claim: '{claim[:60]}...'{hint}")

    conn.close()
    return len(issues) == 0, issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("candidate_id", help="Candidate slug to audit")
    args = ap.parse_args()

    jl, obj = find_candidate(args.candidate_id)
    if obj is None:
        print(f"FAIL: Candidate `{args.candidate_id}` not found", file=sys.stderr)
        return 1

    claim = obj.get("Rule") or obj.get("claim") or ""
    evidence = obj.get("Evidence") or obj.get("evidence") or []
    if isinstance(evidence, str):
        found = re.findall(r"`([^`]+)`", evidence)
        evidence = found or [evidence]

    if not evidence:
        print(f"FAIL: Candidate `{args.candidate_id}` carries no evidence IDs", file=sys.stderr)
        return 1

    passed, issues = audit_claim_grounding(claim, evidence)
    if not passed:
        print(f"AUDITOR REJECT: Candidate `{args.candidate_id}` failed content audit:", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        return 1

    print(f"AUDITOR PASS: Candidate `{args.candidate_id}` content-grounded across {len(evidence)} chunk(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
