#!/usr/bin/env python3
"""check_research_quality.py — quality gate for new research artifacts in INBOX/.

Checks:
- W-DEEP depth: corpus chunks contain algorithms/data structures/threat models/limitations
- Source quality: stable identifier present (DOI/arXiv URL)
- Deduplication: no duplicate titles/IDs against existing corpus
- Primary-source requirement: URLs match trusted academic domains
- Anti-slop: minimum length, no marketing-ese markers

Exit 0 = all checks pass. Exit 1 = hard failure. Exit 2 = warning-only (soft fail).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "INBOX"
IDEAS = INBOX / "ideas"
CORPUS = ROOT / "knowledge" / "corpus"
RAW = ROOT / "knowledge" / "raw"

# Minimum body length (after frontmatter) for a meaningful corpus chunk
MIN_BODY_CHARS = 1200

# Marketing/aggregator phrases to down-weight
MARKETING_ESSE = (
    "game-changer", "revolutionary", "groundbreaking", "must-read",
    "you won't believe", "shocking", "secret", "unlock", "hack",
)


class CheckResult(NamedTuple):
    file: str
    check: str
    passed: bool
    severity: str  # "error" | "warning" | "info"
    detail: str


def parse_frontmatter_and_body(text: str) -> tuple[dict[str, str], str]:
    """Split YAML-ish frontmatter from markdown body."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            fm = text[3:end]
            body = text[end + 3:].lstrip("\n")
            meta: dict[str, str] = {}
            for line in fm.splitlines():
                if ":" in line and not line.startswith("-"):
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            return meta, body
    return {}, text


def extract_ids_from_frontmatter(meta: dict[str, str]) -> list[str]:
    """Extract candidate identifiers from frontmatter."""
    ids: list[str] = []
    for key in ("id", "source", "title"):
        val = meta.get(key, "")
        if val:
            ids.append(val.lower())
    return ids


def check_source_identifier(text: str) -> CheckResult:
    """Check that frontmatter has a stable source identifier."""
    meta, _ = parse_frontmatter_and_body(text)
    source = meta.get("source", "")
    if not source:
        return CheckResult("<frontmatter>", "source_identifier", False, "error",
                           "Missing 'source:' field in frontmatter")
    # Must contain a stable identifier pattern
    if not re.search(r'(arxiv\.org|doi\.org|github\.com|gitlab\.com|openreview\.net|acm\.org|ieee\.org|springer\.com|nature\.com|science\.org)', source, re.I):
        return CheckResult(source, "source_identifier", False, "warning",
                           f"Source '{source}' lacks a stable academic/publisher URL")
    return CheckResult(source, "source_identifier", True, "info",
                       "Source identifier present")


def check_primary_source_requirement(text: str) -> CheckResult:
    """Check that the source looks like a primary source, not a blog/tweet summary."""
    meta, _ = parse_frontmatter_and_body(text)
    source = meta.get("source", "")
    if not source:
        return CheckResult("<none>", "primary_source", False, "error",
                           "No source to evaluate")
    # Reject obvious secondary/marketing sources
    if re.search(r'(medium\.com|substack\.com|twitter\.com|x\.com|reddit\.com|youtube\.com|youtu\.be|blog|newsletter)', source, re.I):
        return CheckResult(source, "primary_source", False, "warning",
                           "Source appears to be secondary (blog, social media, video)")
    # Accept arxiv, DOI, publisher domains
    if re.search(r'(arxiv\.org|doi\.org|openreview\.net|acm\.org|ieee\.org|springer\.com|nature\.com|science\.org|paperswithcode\.com)', source, re.I):
        return CheckResult(source, "primary_source", True, "info",
                           "Source is primary academic")
    return CheckResult(source, "primary_source", True, "info",
                       "Source accepted as primary-ish")


def _count_hits(body_lower: str, keywords: list[str]) -> tuple[int, list[str]]:
    hits = [kw for kw in keywords if kw in body_lower]
    return len(hits), hits


def check_wdeep_depth(text: str) -> CheckResult:
    """Check W-DEEP technical depth: presence of algorithms, data structures, threat models, limitations.

    Each pillar is scored independently; the file passes when at least two
    pillars surface evidence (per `research-depth-skeletal-triples`). Soft
    warnings flag pillars that are entirely absent so the enricher can fill
    them later rather than blocking ingestion on a single shallow abstract.
    """
    _, body = parse_frontmatter_and_body(text)
    body_lower = body.lower()

    markers = {
        "algorithm": ["algorithm", "procedure", "method", "approach", "technique",
                       "protocol", "pipeline", "process", "steps", "workflow"],
        "data_structure": ["data structure", "graph", "tree", "queue", "stack", "hash",
                           "dictionary", "array", "list", "set", "map", "database",
                           "table", "index", "schema", "format", "representation"],
        "threat_model": ["threat model", "attack", "vulnerability", "exploit", "risk",
                         "security", "adversarial", "robustness", "failure mode",
                         "limitation", "constraint", "assumption", "boundary", "caveat",
                         "drawback", "issue", "problem", "danger", "harm"],
        "limitations": ["limitation", "drawback", "constraint", "assumption", "boundary",
                        "caveat", "future work", "open question", "unknown", "risk",
                        "tradeoff", "compromise"],
    }

    found = {}
    empty = []
    for category, keywords in markers.items():
        count, hits = _count_hits(body_lower, keywords)
        found[category] = hits
        if count == 0:
            empty.append(category)

    # Require at least 2 out of 4 pillars so a single-topic abstract doesn't block ingestion
    passed_pillars = sum(1 for v in found.values() if v)
    if passed_pillars < 2:
        return CheckResult("<body>", "wdeep_depth", False, "error",
                           f"Insufficient W-DEEP evidence ({passed_pillars}/4 pillars); missing: {', '.join(empty)}; found: {found}")

    # Soft-warning if any pillar is completely absent (enrichment target)
    if empty:
        return CheckResult("<body>", "wdeep_depth", True, "warning",
                           f"W-DEEP depth partially satisfied ({passed_pillars}/4); missing: {', '.join(empty)}; found: {found}")

    return CheckResult("<body>", "wdeep_depth", True, "info",
                       "W-DEEP depth markers present")


def check_minimum_length(text: str) -> CheckResult:
    """Check that the body has substantive content."""
    _, body = parse_frontmatter_and_body(text)
    body_len = len(body.strip())
    if body_len < MIN_BODY_CHARS:
        return CheckResult("<body>", "minimum_length", False, "error",
                           f"Body too short ({body_len} chars, minimum {MIN_BODY_CHARS})")
    return CheckResult("<body>", "minimum_length", True, "info",
                       f"Body length OK ({body_len} chars)")


def check_marketing_ese(text: str) -> CheckResult:
    """Flag marketing/aggregator language."""
    _, body = parse_frontmatter_and_body(text)
    body_lower = body.lower()
    hits = [phrase for phrase in MARKETING_ESSE if phrase in body_lower]
    if hits:
        return CheckResult("<body>", "marketing_ese", False, "warning",
                           f"Marketing language detected: {hits}")
    return CheckResult("<body>", "marketing_ese", True, "info",
                       "No marketing language")


def normalize_for_dedup(value: str) -> str:
    """Normalize titles/IDs for dedup comparison."""
    v = value.lower().strip()
    # Strip chunk numbering prefix: "00_", "01_", ..., "99_"
    v = re.sub(r'^\d{1,2}_', '', v)
    # Strip part suffixes: " (part 1/118)", " (part 12/118)", "(part 1/2)"
    v = re.sub(r'\s*\(part\s+\d+/\d+\)', '', v)
    # Strip file extension
    v = re.sub(r'\.(md|txt|pdf)$', '', v)
    return v.strip()


def check_duplicate(text: str, existing_ids: set[str], current_path: Path) -> CheckResult:
    """Check for duplicate title/ID against existing corpus."""
    meta, _ = parse_frontmatter_and_body(text)
    title = normalize_for_dedup(meta.get("title", ""))
    source = normalize_for_dedup(meta.get("source", ""))
    paper_id = normalize_for_dedup(meta.get("id", ""))

    current_norm = {
        normalize_for_dedup(current_path.stem),
        normalize_for_dedup(current_path.name),
    }
    # Exact-match normalized values against existing corpus
    duplicates = set()
    for val in (title, source, paper_id):
        if val and val in existing_ids and val not in current_norm:
            duplicates.add(val)

    if duplicates:
        return CheckResult("<frontmatter>", "duplicate", False, "error",
                           f"Duplicate detected against existing corpus: {duplicates}")
    return CheckResult("<frontmatter>", "duplicate", True, "info",
                       "No duplicate detected")


def load_existing_corpus_ids() -> set[str]:
    """Load all titles/sources/ids from existing corpus for dedup."""
    ids: set[str] = set()
    if not CORPUS.exists():
        return ids
    for f in CORPUS.glob("*.md"):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
            meta, _ = parse_frontmatter_and_body(text)
            for val in (meta.get("id", ""), meta.get("source", ""), meta.get("title", "")):
                if val:
                    ids.add(normalize_for_dedup(val))
        except Exception:
            continue
    return ids


def check_file(path: Path, existing_ids: set[str]) -> list[CheckResult]:
    """Run all checks on a single file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [CheckResult(str(path), "read", False, "error", f"Read error: {e}")]

    results = [
        check_source_identifier(text),
        check_primary_source_requirement(text),
        check_wdeep_depth(text),
        check_minimum_length(text),
        check_marketing_ese(text),
        check_duplicate(text, existing_ids, path),
    ]
    return results


def is_idea_file(path: Path) -> bool:
    """True for discussion files under INBOX/ideas/, which Q12 ignores."""
    try:
        return path.resolve().is_relative_to(IDEAS.resolve())
    except OSError:
        return False


def main() -> int:
    targets: list[Path] = []
    if INBOX.exists():
        for p in sorted(INBOX.glob("*.md")):
            # Skip escalation/pending request files and log files
            if "pending" in p.name.lower() or "request" in p.name.lower():
                continue
            # INBOX/ideas/ is arguments, not research. Q12 grades intake
            # quality; a discussion file is not intake (scripts/discuss.py).
            if is_idea_file(p):
                continue
            if not p.name.startswith("_"):
                targets.append(p)

    if not targets:
        print("No research files found in INBOX/")
        return 0

    existing_ids = load_existing_corpus_ids()
    results: list[CheckResult] = []

    for path in targets:
        results.extend(check_file(path, existing_ids))

    errors = [r for r in results if r.passed is False and r.severity == "error"]
    warnings = [r for r in results if r.passed is False and r.severity == "warning"]
    infos = [r for r in results if r.passed is True]

    print(f"\nChecked {len(targets)} file(s), {len(results)} check(s)")
    print(f"  errors:   {len(errors)}")
    print(f"  warnings: {len(warnings)}")
    print(f"  passed:   {len(infos)}")

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        tag = {"error": "[ERROR]", "warning": "[WARN]", "info": "[OK]"}[r.severity]
        print(f"  {tag} {status} | {r.file} | {r.check}: {r.detail}")

    if errors:
        print("\nRESULT: FAIL — hard errors must be fixed before ingestion")
        return 1
    elif warnings:
        print("\nRESULT: WARN — warnings should be reviewed")
        return 2
    else:
        print("\nRESULT: PASS")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())