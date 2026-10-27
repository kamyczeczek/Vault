#!/usr/bin/env python3
"""check_promotion.py — closed-loop gate (phase 5 sub-gate).

THE DEFECT THIS GATE CLOSES

`scripts/promote_candidate.py` validates a candidate's evidence ids resolve in
graph.db before promotion, and can append an accepted rule to a memory file. But
nothing verified that the memory file is on a path the read side actually reads.
The project shipped exactly that hole: on 2026-09-16, 30 candidates were already
`accepted`, `reflection/memory.md` existed nowhere on disk, and the string
"memory.md" appeared in exactly one place — the promote_candidate.py docstring.
Injection was one-directional: rules were promoted into a file nothing consumed,
which is a write-only loop, i.e. not a loop. The reflections were inert by
construction, not by intent.

This gate asserts the loop is closed end to end:

  exit 0  every accepted candidate has a landed, non-empty, citation-bearing
          entry in the memory file, AND that file is listed as an input in the
          04_reflect stage contract (so a spawned reflection can read it)
  exit 1  a promoted rule never landed, or landed with no evidence id — a
          rule a working agent cannot cite is a rule that does not constrain it
  exit 2  prerequisite missing (memory file, candidate files, or graph.db)

The write side and the read side are both checked. A memory file that exists but
is not contracted as a 04_reflect input is a silent promotion — the defect above,
reproduced — so that is a failure too, exit 1.

Corpus grounding:
- `00_08_lesson_persistence_eviction_requirement` — a stored lesson is only
  trustworthy if eviction maintains it. Reachability is the same requirement on
  the intake end: a lesson no agent can reach is not stored knowledge.
- `00_reflection_closed_vocabulary_before_content` — "questions silently go
  unanswered." Promotion that lands off the read path is the same silence.
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "reflection" / "candidates"
CONTRACT = ROOT / "stages" / "04_reflect" / "CONTEXT.md"
DB = ROOT / "knowledge" / "graph" / "graph.db"

# the memory file promote_candidate.py writes to; it must be a contracted read input
MEMORY = ROOT / "reflection" / "memory.md"
CANONICAL_FIELDS = ("Rule", "Evidence", "Target", "Action")


def _field(body: str, name: str) -> str | None:
    match = re.search(rf"^{re.escape(name)}:\s*(.+)$", body, re.MULTILINE)
    return match.group(1).strip() if match else None


def _legacy_section(body: str) -> bool:
    return bool(
        re.search(
            r"^\s*-\s*(?:claim|evidence)\s*:",
            body,
            flags=re.MULTILINE | re.IGNORECASE,
        )
    )


def _canonical_memory_sections(text: str) -> tuple[set[str], dict[str, dict[str, str]], list[str]]:
    landed: set[str] = set()
    sections: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    header_re = re.compile(r"^###\s+(?P<id>.+?)\s+—\s+(?P<state>accepted|proposed)\s*$", re.M)
    matches = list(header_re.finditer(text))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end].strip()
        rule_id = match.group("id")
        if _legacy_section(body):
            errors.append(f"{rule_id}: legacy '- claim: / - evidence:' representation is forbidden")
            continue
        if match.group("state") != "accepted":
            why = _field(body, "Why")
            if not why:
                errors.append(f"{rule_id}: proposed memory section has no non-empty Why field")
            continue
        landed.add(rule_id)
        values = {name: _field(body, name) for name in CANONICAL_FIELDS}
        missing = [name for name, value in values.items() if not value]
        if missing:
            errors.append(
                f"{rule_id}: accepted memory section has missing or blank canonical field(s): "
                f"{', '.join(missing)}"
            )
            continue
        sections[rule_id] = {name: value.strip() for name, value in values.items()}
    return landed, sections, errors


def _candidate_id(obj: dict) -> str:
    return str(obj.get("id") or obj.get("candidate_id") or "?")


def _candidate_evidence(obj: dict) -> list[str]:
    value = obj.get("Evidence")
    if isinstance(value, str):
        return re.findall(r"`([^`]+)`", value)
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def accepted_candidates() -> list[tuple[str, dict, Path]]:
    out: list[tuple[str, dict, Path]] = []
    for jl in sorted(CANDIDATES.glob("*.jsonl")):
        for line in jl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{jl.name}: invalid JSON: {exc}") from exc
            if obj.get("state") == "accepted":
                out.append((_candidate_id(obj), obj, jl))
    return out



def contract_lists_memory() -> bool:
    """The 04_reflect contract's Inputs table must name the memory file, or a
    spawned agent cannot read what promotion wrote."""
    if not CONTRACT.exists():
        return False
    return "reflection/memory.md" in CONTRACT.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    if not DB.exists():
        print("FAIL: graph.db missing — run build_graph.py first", file=sys.stderr)
        return 2
    if not MEMORY.exists():
        # the file is created on first promotion; missing + zero accepted = nothing to check
        accepted = accepted_candidates()
        if not accepted:
            print("OK: no accepted candidates and no memory file — nothing promoted yet")
            return 0
        print(f"FAIL: {len(accepted)} accepted candidate(s) but {MEMORY.name} does not "
              f"exist — promoted rules landed nowhere (write-only loop)",
              file=sys.stderr)
        for cid, _, jl in accepted[:8]:
            print(f"  - {cid} ({jl.name})", file=sys.stderr)
        if len(accepted) > 8:
            print(f"  ... {len(accepted) - 8} more", file=sys.stderr)
        return 1

    # --- read side: the memory file is contracted as an input ---
    if not contract_lists_memory():
        print(f"FAIL: {MEMORY.name} exists but stages/04_reflect/CONTEXT.md does not list "
              f"it as an input — promoted rules are not on the read path (silent promotion)",
              file=sys.stderr)
        return 1

    text = MEMORY.read_text(encoding="utf-8")
    if not text.strip():
        print(f"FAIL: {MEMORY.name} is empty — accepted rules have no content", file=sys.stderr)
        return 1

    landed, memory_sections, memory_errors = _canonical_memory_sections(text)
    errors = list(memory_errors)

    # --- write side: accepted candidates and memory entries must be canonical ---
    c = sqlite3.connect(DB)
    ids = {r[0] for r in c.execute("SELECT id FROM nodes").fetchall()}
    c.close()

    try:
        accepted = accepted_candidates()
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    for cid, obj, jl in accepted:
        missing = [
            name
            for name in CANONICAL_FIELDS
            if not isinstance(obj.get(name), str) or not obj[name].strip()
        ]
        if missing:
            errors.append(
                f"{cid} ({jl.name}): accepted candidate has missing or blank canonical "
                f"field(s): {', '.join(missing)}"
            )
            continue
        legacy_keys = [key for key in ("claim", "evidence", "evidence_ids", "principle") if key in obj]
        if legacy_keys:
            errors.append(
                f"{cid} ({jl.name}): accepted candidate still carries legacy field(s): "
                f"{', '.join(legacy_keys)}"
            )
        if cid not in landed:
            errors.append(f"{cid} ({jl.name}): accepted but no entry in {MEMORY.name}")
            continue
        body = memory_sections.get(cid)
        if body is None:
            continue
        for name in CANONICAL_FIELDS:
            if " ".join(str(obj[name]).split()) != " ".join(body[name].split()):
                errors.append(f"{cid}: candidate {name} does not match its accepted memory section")
        ev_ids = _candidate_evidence(obj)
        memory_ev_ids = re.findall(r"`([^`]+)`", body["Evidence"])
        if not memory_ev_ids:
            errors.append(f"{cid}: accepted memory Evidence has no backticked citation ids")
            continue
        missing_evidence = [e for e in ev_ids if e not in memory_ev_ids]
        if missing_evidence:
            errors.append(
                f"{cid}: {len(missing_evidence)} evidence id(s) not backticked in its own "
                f"{MEMORY.name} entry (e.g. {missing_evidence[0]})"
            )

    if errors:
        print(f"FAIL: {len(errors)} promotion gap(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {len(accepted)} accepted candidate(s) landed in {MEMORY.name}; "
          f"memory file is a contracted 04_reflect input; canonical fields and citations carried")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
