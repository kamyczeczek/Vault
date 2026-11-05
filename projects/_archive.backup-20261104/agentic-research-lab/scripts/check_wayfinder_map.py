#!/usr/bin/env python3
"""check_wayfinder_map.py — structural validator for a wayfinder map file.

Stdlib only. Checks the invariants wayfinder states but never mechanises, so a
map cannot quietly stop being a map:

  G1  exactly one `## Destination` (a map with two is a workspace where a cold
      agent cannot tell which plan it is following)
  G2  every frontier ticket poses a question, not a build step
  G3  the section set is complete and the fog section holds fog only
  G4  every relative link in the file resolves on disk
  G5  `Out of scope` is present and non-empty
  G6  a charting-pass map is visibly provisional

The G2 check counts question-shaped tickets rather than reading intent. That is
a real limit and is stated in the map's own ledger: intent is reviewed by a
human. The check catches deletion and renumbering, which are the failures that
happen by accident.

Usage:
    python scripts/check_wayfinder_map.py <map.md> [--gate G1|G2|G3|G4|G5|G6|all]
Exit codes: 0 all selected gates met, 1 a gate failed, 2 the map is unusable
(which is a structural error, not a failed gate — never reported as success).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SECTIONS = ("## Destination", "## Notes", "## Decisions so far",
            "## Frontier tickets", "## Not yet specified", "## Out of scope")
TICKET_RE = re.compile(r"^###\s+(?P<id>T\d+|[A-Z]-\d+)\s+—\s+(?P<title>.+)$", re.MULTILINE)
QUESTION_RE = re.compile(r"^\s*[-*]?\s*\*\*Question:\*\*\s*\S", re.MULTILINE)
# A ticket whose "question" is an instruction is a build step wearing a
# question's label. Match the imperative, not the label, and match it anywhere
# the label appears: the first version required the whole line to be exactly
# `- **Question:** <imperative>`, and the negative control's mutation — which
# produces exactly that shape — slipped through as undetected. The real map
# wraps the question across continuation lines, so a line-anchored test is
# measuring the label rather than the content.
BUILD_STEP_RE = re.compile(
    r"\*\*Question:\*\*[^\n]{0,200}?\b(?:implement|build|write|add|create|remove|"
    r"delete|wire|ship|merge|refactor)\b",
    re.IGNORECASE | re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]*\]\((?!https?:)([^)#]+)(?:#[^)]*)?\)")
GATES = ("G1", "G2", "G3", "G4", "G5", "G6")


def read_sections(text: str) -> dict[str, list[str]]:
    """Split on `## ` headings; return heading -> body lines."""
    out: dict[str, list[str]] = {}
    current = ""
    for line in text.splitlines():
        if line.startswith("## "):
            current = line.strip()
            out.setdefault(current, [])
        elif current:
            out[current].append(line)
    return out


def check_g1(text: str) -> tuple[bool, str]:
    count = text.count("\n## Destination\n") + (1 if text.startswith("## Destination\n") else 0)
    return count == 1, f"found {count} `## Destination` headings, expected exactly 1"


def check_g2(text: str) -> tuple[bool, str]:
    tickets = list(TICKET_RE.finditer(text))
    if not tickets:
        return False, "no frontier tickets found (`### T1 — title` shape)"
    questions = len(QUESTION_RE.findall(text))
    build_steps = BUILD_STEP_RE.findall(text)
    if build_steps:
        return False, f"{len(build_steps)} ticket(s) state a build step where a question belongs"
    if questions < len(tickets):
        return False, f"{len(tickets)} tickets but only {questions} `**Question:**` lines"
    return True, f"{len(tickets)} tickets, all question-shaped"


def check_g3(text: str) -> tuple[bool, str]:
    sections = read_sections(text)
    missing = [s for s in SECTIONS if s not in sections]
    if missing:
        return False, f"missing sections: {', '.join(missing)}"
    fog = "\n".join(sections["## Not yet specified"]).strip()
    if not fog:
        return False, "`## Not yet specified` is empty — delete the section or fill it"
    # Fog must not restate a live ticket as a decision. A live ticket id
    # appearing in Decisions-so-far is the shape this catches.
    live = {m.group("id") for m in TICKET_RE.finditer(text)}
    decided = "\n".join(sections["## Decisions so far"])
    for ticket_id in sorted(live):
        # A Decisions entry can name its ticket inline as `- **[T1 — title]**`
        # or as a bare `- T1:` bullet, so match the id inside the list marker
        # rather than only at the start of the line. The negative control
        # mutation for this gate writes the bracketed form, and the first
        # version of this check only matched the bare form — the mutation
        # reported NOT DETECTED against a gate that was simply not looking.
        if re.search(rf"^\s*[-*]\s*(?:\[\*\*|\*\*\[|\*\*)?{re.escape(ticket_id)}\b",
                     decided, re.MULTILINE):
            return False, f"live ticket `{ticket_id}` is also listed under Decisions so far"
    return True, f"{len(SECTIONS)} sections present; {len(live)} live tickets not double-listed"


def check_g4(path: Path, text: str) -> tuple[bool, str]:
    base = path.parent
    broken: list[str] = []
    seen: set[str] = set()
    for target in LINK_RE.findall(text):
        target = target.strip()
        if not target or target in seen:
            continue
        seen.add(target)
        resolved = (base / target).resolve()
        if not resolved.exists():
            broken.append(target)
    if broken:
        return False, f"{len(broken)} unresolved link(s): {', '.join(sorted(broken)[:5])}"
    return True, f"{len(seen)} relative link(s) resolve"


def check_g5(text: str) -> tuple[bool, str]:
    sections = read_sections(text)
    body = "\n".join(sections.get("## Out of scope", [])).strip()
    if not body:
        return False, "`## Out of scope` is empty"
    bullets = [ln for ln in body.splitlines() if ln.strip().startswith(("- ", "* "))]
    if not bullets:
        return False, "`## Out of scope` has no entries"
    return True, f"{len(bullets)} out-of-scope entries recorded"


def check_g6(text: str) -> tuple[bool, str]:
    # A map must declare its own status, and the declared status must be a real
    # one. The first version only required the words PROPOSED or provisional, so
    # when a human confirmed the destination (2026-10-01) the gate started
    # failing on a correctly-updated map: it had encoded "charting precedes
    # confirmation" as "this text is permanent". Two states are legal, and a
    # confirmed map must carry a date, because an undated confirmation is
    # indistinguishable from a proposal nobody read.
    confirmed = re.search(r"\*\*CONFIRMED\s+(\d{4}-\d{2}-\d{2})", text)
    if confirmed:
        return True, f"map is confirmed ({confirmed.group(1)}) — destination accepted by a human"
    if "PROPOSED" in text or "provisional" in text.lower():
        return True, "map is marked provisional — charting pass precedes human confirmation"
    return False, ("map declares no status: it must be marked PROPOSED, or CONFIRMED "
                   "with an ISO date, so a reader can tell a proposal from a decision")


CHECKS = {"G1": check_g1, "G2": check_g2, "G3": check_g3, "G5": check_g5, "G6": check_g6}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("map", type=Path)
    ap.add_argument("--gate", default="all", help=f"gate id or 'all' ({'/'.join(GATES)})")
    args = ap.parse_args()

    if not args.map.is_file():
        print(f"MAP_MISSING: {args.map}", file=sys.stderr)
        return 2
    text = args.map.read_text(encoding="utf-8", errors="ignore")

    selected = GATES if args.gate == "all" else (args.gate,)
    unknown = [g for g in selected if g not in GATES]
    if unknown:
        print(f"BAD_GATE: unknown gate(s) {', '.join(unknown)}; expected {', '.join(GATES)} or 'all'",
              file=sys.stderr)
        return 2

    failed = 0
    for gate in selected:
        if gate == "G4":
            ok, detail = check_g4(args.map, text)
        else:
            ok, detail = CHECKS[gate](text)
        if ok:
            print(f"{gate}_OK: {detail}")
        else:
            failed += 1
            print(f"{gate}_FAIL: {detail}")
    if failed:
        print(f"MAP_CHECK_FAILED: {failed}/{len(selected)} gate(s) failed")
        return 1
    print("MAP_STRUCTURE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())