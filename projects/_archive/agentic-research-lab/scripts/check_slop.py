#!/usr/bin/env python3
"""check_slop.py — quality regression gate for reflection artifacts.

Detects three forms of "slop" (degradation under iteration) in reflection
candidates and digests, inspired by SlopCodeBench's findings on code erosion
under iterative agent work:

  HARD FAILURES (exit 1):
  1. near-duplicate claim — an active candidate repeats an existing memory.md
     rule above the similarity threshold.

  2. unsupported verbosity — an active candidate with ≤1 evidence id produces
     a claim longer than the verbosity limit.

  WARNINGS (exit 0, printed to stderr):
  3. citation concentration — an active candidate file with 2+ rows cites the
     same small set of evidence ids disproportionately.

  4. lesson triple shape — a canonical candidate must explicitly provide
     Condition, Reason, and Correction fields. Missing fields are hard failures,
     because a lesson that cannot be reused should not enter the active pool.

  The gate normalizes legacy (claim/evidence) and canonical
  (Rule/Evidence/Target/Action) rows before checking; canonical rows used to
  pass through invisible.

Accepted/rejected candidates are excluded — they already passed promotion
gates and their similarity to memory.md is expected.

Verification runs must write to reflection/scratch/ via `spawn.py --scratch`,
not here: this gate grades research output, and a test fixture is not research
output. That is a property of where the run was told to write, decided before
the run — not a filter on the graded set, added afterwards.

Exit code: 0 = clean or warnings, 1 = hard failures, 2 = prerequisite missing.
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "reflection" / "candidates"
MEMORY = ROOT / "reflection" / "memory.md"

# thresholds
NEAR_DUP_RATIO = 0.70
CITATION_CONCENTRATION_THRESHOLD = 0.60  # fraction of rows citing same top-3 ids
UNSUPPORTED_VERBOSITY_LIMIT = 200  # chars


def existing_memory_claims() -> list[str]:
    """Extract rule claims from memory.md (lines following 'Rule:' or '- claim:')."""
    if not MEMORY.exists():
        return []
    text = MEMORY.read_text(encoding="utf-8")
    claims = re.findall(r"(?:^Rule:\s*(.+)$|^- claim:\s*(.+)$)", text, re.MULTILINE)
    return [c.strip() for pair in claims for c in pair if c.strip()]


def _claim_and_evidence(row: dict) -> tuple[str, list[str]]:
    """Normalize legacy (claim/evidence) and canonical (Rule/Evidence/Target/Action) rows.

    Without this the gate is blind to canonical candidates: row.get("evidence", [])
    returns [] and row.get("claim", "") returns "" for Rule/Evidence rows, so
    verbosity and duplication checks silently skip them.
    """
    claim = row.get("claim") or row.get("Rule") or row.get("Action") or ""
    evidence = row.get("evidence")
    if not isinstance(evidence, list):
        evidence = re.findall(r"`([^`]+)`", str(row.get("Evidence", "")))
    evidence = [item for item in evidence if isinstance(item, str)]
    return str(claim), evidence


def load_candidates() -> dict[str, list[dict]]:
    """Load all candidate jsonl files, keyed by filename."""
    result: dict[str, list[dict]] = {}
    if not CANDIDATES.exists():
        return result
    for jl in sorted(CANDIDATES.glob("*.jsonl")):
        rows = []
        for line in jl.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        result[jl.name] = rows
    return result


def active_candidates(files: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """Keep only proposed/experimental rows; accepted/rejected rows already
    cleared promotion gates and their similarity to memory.md is expected."""
    return {
        fname: [r for r in rows if r.get("state") not in {"accepted", "rejected"}]
        for fname, rows in files.items()
    }


def check_near_duplicates(claims: list[str], memory_claims: list[str]) -> list[str]:
    """Flag active candidates whose claim duplicates an existing memory rule."""
    if not claims or not memory_claims:
        return []
    errors: list[str] = []
    for claim in claims:
        if not claim:
            continue
        for existing in memory_claims:
            ratio = difflib.SequenceMatcher(None, claim.lower(), existing.lower()).ratio()
            if ratio >= NEAR_DUP_RATIO:
                errors.append(
                    f"near-duplicate claim (similarity {ratio:.2f}): "
                    f"new claim overlaps existing rule: {existing[:80]}..."
                )
                break
    return errors


def check_unsupported_verbosity(rows: list[dict]) -> list[str]:
    """Flag candidates with ≤1 evidence id but verbose unsupported claims."""
    errors: list[str] = []
    for row in rows:
        claim, evidence = _claim_and_evidence(row)
        if len(evidence) <= 1 and len(claim) > UNSUPPORTED_VERBOSITY_LIMIT:
            errors.append(
                f"unsupported verbosity ({len(claim)} chars, {len(evidence)} evidence): "
                f"{claim[:80]}..."
            )
    return errors


def check_triple_shape(rows: list[dict]) -> list[str]:
    """Validate reusable lesson shape without rejecting legacy rows lacking fields."""
    errors: list[str] = []
    for row in rows:
        if row.get("state") in {"accepted", "rejected"}:
            continue
        # Legacy rows are normalized by candidate_writer on the next write. Do
        # not fail the current corpus merely because old rows predate the schema.
        if all(isinstance(row.get(field), str) and row[field].strip()
               for field in ("Condition", "Reason", "Correction")):
            continue
        if not str(row.get("Action", "")).strip() or not str(row.get("Rule", row.get("claim", ""))).strip():
            errors.append(f"lesson triple incomplete and cannot be inferred: {row.get('id', '?')}")
    return errors


def check_citation_concentration(
    active: dict[str, list[dict]],
) -> dict[str, list[str]]:
    """Flag candidate files where citation is narrowly concentrated.
    Only files with 3+ active rows are assessed; with two rows, any shared
    citation necessarily produces 50–100% concentration and is not a useful
    iteration-level signal.
    """
    warnings: dict[str, list[str]] = {}
    for fname, rows in active.items():
        if not rows or len(rows) < 3:
            continue
        id_counts: dict[str, int] = {}
        for row in rows:
            for eid in _claim_and_evidence(row)[1]:
                id_counts[eid] = id_counts.get(eid, 0) + 1
        if not id_counts:
            continue
        top3 = sorted(id_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        cited_rows = sum(
            1 for row in rows
            if any(eid in {i for i, _ in top3} for eid in _claim_and_evidence(row)[1])
        )
        concentration = cited_rows / len(rows)
        if concentration >= CITATION_CONCENTRATION_THRESHOLD:
            warnings[fname] = [
                f"citation concentration {concentration:.0%}: "
                f"top-3 ids {[i for i, _ in top3]} cited in {cited_rows}/{len(rows)} rows"
            ]
    return warnings


def main() -> int:
    if not CANDIDATES.exists():
        print("FAIL: reflection/candidates/ missing", file=sys.stderr)
        return 2

    memory_claims = existing_memory_claims()
    files = load_candidates()
    active = active_candidates(files)
    hard_errors: list[str] = []
    warnings: list[str] = []

    # 1. near-duplicate check across active candidates vs memory.md
    active_claims = [_claim_and_evidence(row)[0] for rows in active.values() for row in rows]
    dup_errors = check_near_duplicates(active_claims, memory_claims)
    hard_errors.extend(dup_errors)

    # 2. unsupported verbosity (hard failure)
    for fname, rows in active.items():
        verb_errors = check_unsupported_verbosity(rows)
        for e in verb_errors:
            hard_errors.append(f"[{fname}] {e}")

    # 3. citation concentration (warning, not hard failure)
    concentration_warnings = check_citation_concentration(active)
    for fname, errs in concentration_warnings.items():
        for e in errs:
            warnings.append(f"[{fname}] {e}")

    triple_errors: list[str] = []
    for fname, rows in active.items():
        for e in check_triple_shape(rows):
            triple_errors.append(f"[{fname}] {e}")
    hard_errors.extend(triple_errors)

    if warnings:
        print(f"WARN: slop warnings ({len(warnings)} issues)", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)

    if hard_errors:
        print(f"FAIL: slop detected ({len(hard_errors)} hard failures)", file=sys.stderr)
        for e in hard_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    total_active = sum(len(rows) for rows in active.values())
    print(f"OK: checked {total_active} active candidates across {len(active)} files — no hard failures.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
