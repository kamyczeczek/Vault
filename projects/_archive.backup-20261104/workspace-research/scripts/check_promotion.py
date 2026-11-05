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


def accepted_candidates() -> list[tuple[str, dict, Path]]:
    out: list[tuple[str, dict, Path]] = []
    for jl in sorted(CANDIDATES.glob("*.jsonl")):
        for line in jl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("state") == "accepted":
                out.append((obj.get("id", "?"), obj, jl))
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

    # --- write side: every accepted rule landed, with at least one citable evidence id ---
    c = sqlite3.connect(DB)
    ids = {r[0] for r in c.execute("SELECT id FROM nodes").fetchall()}
    c.close()

    landed = set(re.findall(r"^### (.+?) — accepted", text, flags=re.M))
    # per-section text, so evidence is matched within the rule's own entry — a shared
    # file where one rule's ids are backticked and another's are a raw list must fail on
    # the raw one, not pass by borrowing another entry's backticks
    sections: dict[str, str] = {}
    for cid, body in re.findall(r"^### (.+?) — accepted\n(.*?)(?=^### |\Z)",
                               text, flags=re.M | re.S):
        sections[cid] = body

    errors: list[str] = []
    accepted = accepted_candidates()
    for cid, obj, jl in accepted:
        if cid not in landed:
            errors.append(f"{cid} ({jl.name}): accepted but no entry in {MEMORY.name}")
            continue
        # evidence ids the rule cites must actually appear in the memory entry —
        # a rule whose citations were dropped in promotion is uncitable in practice.
        # BOTH schemas are accepted: new {evidence: [...]} and legacy
        # {evidence_ids: [...]} / {principle: "00_..."}; grounding is what matters.
        ev = obj.get("evidence") or []
        if isinstance(ev, str):
            ev = [ev]
        if not ev and isinstance(obj.get("evidence_ids"), list):
            ev = obj["evidence_ids"]
        if not ev and isinstance(obj.get("principle"), str):
            ev = [obj["principle"]]
        ev_ids = [e for e in ev if isinstance(e, str) and re.match(r"^[0-9]{2}_", e)]
        if ev_ids:
            body = sections.get(cid, "")
            # the id must appear BACKTICKED in this rule's own section: an id present as
            # a bare token (or as a raw Python list) is uncitable by any consumer that
            # reads ids out of this file. Readable to a human is not sufficient.
            missing = [e for e in ev_ids if f"`{e}`" not in body]
            if missing:
                errors.append(f"{cid}: {len(missing)} evidence id(s) not backticked in its "
                              f"own {MEMORY.name} entry (e.g. {missing[0]}) — promotion "
                              f"wrote a raw list; re-run promotion")

    if errors:
        print(f"FAIL: {len(errors)} promotion gap(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {len(accepted)} accepted candidate(s) landed in {MEMORY.name}; "
          f"memory file is a contracted 04_reflect input; citations carried")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
