#!/usr/bin/env python3
"""
check_problems.py — MONITORING/KNOWLEDGE/problems integrity + no-circles gate.

Implements PROCESS/PROBLEM_ROUTING.md §7. Guarantees the two user-mandated
properties are machine-checked:
  1. every problem is caught/monitored/solved-for-good (open problems are
     visible in PROGRESS.md; terminal problems carry verification + a
     routed prevention invariant; recurrences are reopenings, not dupes)
  2. no going in circles (the `check` subcommand is the recurrence /
     prior-knowledge lookup that plans and fixes MUST run and cite).

Full-mode checks (exit 1 on any violation):
  H1 shape     — every problem file has a parseable Status + (v2 files)
                 a Fingerprint; recovered/systematic_fix_applied files
                 carry a non-empty Verification section + Owning doc
  H2 terminal  — systematic_fix_applied files also carry a
                 Prevention Invariant section + Recurrences field
  H3 progress  — PROGRESS.md has an '## Open Problems' section; every
                 open problem is listed there and every listed ID cites
                 an existing problem file
  H4 unique    — no two files share the same Fingerprint (recurrence =
                 reopen the existing file, never a duplicate)

Subcommand:
  check "<fingerprint tokens>"  — print files whose Fingerprint shares >=1
      token with the query (recurrence / no-circles lookup).
      exit 0 = hits, exit 2 = no hits, exit 1 = usage error.

Legacy (pre-2026-09-04) files: status synonyms resolved/fixed accepted as
terminal; Fingerprint/Verification fields not required (see PROBLEM_ROUTING.md §8).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBLEMS = ROOT / "MONITORING" / "KNOWLEDGE" / "problems"
PROGRESS = ROOT / "PROGRESS.md"
V2_CUTOVER = "2026-09-04"
V2_STATUS = {"open", "recovered", "systematic_fix_applied"}
LEGACY_STATUS = {"resolved", "fixed"}
TERMINAL = V2_STATUS | LEGACY_STATUS
NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_[A-Za-z0-9][\w-]*\.md$")
PLACEHOLDER_RE = re.compile(r"^<.*>$")


def tokens(s: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[a-z0-9]{3,}", s.lower())}


def field(text: str, name: str):
    """Inline field value in any of the shapes '**Name:** v',
    '**Name**: v', 'Name: v' (colon/bold in either order), OR a
    '## Name' header with the value on the next non-empty line
    (legacy header style)."""
    m = re.search(rf"\*{{0,2}}{re.escape(name)}\s*:?\s*\*{{0,2}}\s*:?\s*([^\n]*)",
                  text)
    if m and m.group(1).strip():
        return m.group(1).strip()
    m = re.search(rf"^## {re.escape(name)}\s*$\s*\n([^\n]+)", text, re.M)
    return m.group(1).strip() if m else None


def parse_problem(p: Path) -> dict:
    text = p.read_text(encoding="utf-8", errors="replace")
    m = NAME_RE.match(p.name)
    date = m.group(1) if m else "0000-00-00"
    is_v2 = date >= V2_CUTOVER

    status = field(text, "Status")
    status = status.lower().split()[0].strip("._-") if status else None

    fingerprint = field(text, "Fingerprint")

    rec_m = re.search(r"\*{0,2}Recurrences\s*:?\s*\*{0,2}\s*:?\s*(\d+)",
                      text)
    recurrences = int(rec_m.group(1)) if rec_m else None

    owning_doc = field(text, "Owning doc")

    def section(name: str) -> str:
        m = re.search(rf"^## {re.escape(name)}\s*$(.*?)(?=^## |\Z)",
                      text, re.M | re.S)
        if not m:
            return ""
        body = "\n".join(ln for ln in m.group(1).splitlines()
                         if ln.strip())
        return body

    return {
        "path": p, "name": p.name, "date": date, "is_v2": is_v2,
        "status": status, "fingerprint": fingerprint,
        "recurrences": recurrences, "owning_doc": owning_doc,
        "verification": section("Verification"),
        "prevention": section("Prevention Invariant"),
    }


def non_empty(body: str) -> bool:
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    return bool(lines) and not all(PLACEHOLDER_RE.match(ln) for ln in lines)


def full_check() -> int:
    errors: list[str] = []
    if not PROBLEMS.is_dir():
        print("FAIL: MONITORING/KNOWLEDGE/problems/ missing", file=sys.stderr)
        return 1
    files = [p for p in sorted(PROBLEMS.glob("*.md"))
             if not p.name.startswith("_") and NAME_RE.match(p.name)]
    parsed = [parse_problem(p) for p in files]

    # H1 shape
    for pr in parsed:
        nm = pr["name"]
        if pr["status"] not in TERMINAL:
            errors.append(f"{nm}: unparseable/unknown Status "
                          f"{pr['status']!r}")
            continue
        if pr["is_v2"] and pr["status"] not in V2_STATUS:
            errors.append(f"{nm}: pre-v2 status synonym used on a "
                          f"post-cutover file")
        if pr["is_v2"] and not pr["fingerprint"]:
            errors.append(f"{nm}: missing Fingerprint")
        if pr["is_v2"] and pr["status"] in ("recovered",
                                            "systematic_fix_applied"):
            if not non_empty(pr["verification"]):
                errors.append(f"{nm}: {pr['status']} without a "
                              f"non-empty Verification section")
            if not pr["owning_doc"] or PLACEHOLDER_RE.match(pr["owning_doc"]):
                errors.append(f"{nm}: {pr['status']} without an Owning doc")
        # H2 terminal
        if pr["is_v2"] and pr["status"] == "systematic_fix_applied":
            if not non_empty(pr["prevention"]):
                errors.append(f"{nm}: systematic_fix_applied without a "
                              f"Prevention Invariant section")
            if pr["recurrences"] is None:
                errors.append(f"{nm}: systematic_fix_applied without "
                              f"Recurrences field")

    # H3 PROGRESS cross-check
    if not PROGRESS.exists():
        errors.append("PROGRESS.md missing")
    else:
        prog = PROGRESS.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^## Open Problems\s*$(.*?)(?=^## |\Z)", prog,
                      re.M | re.S)
        if not m:
            errors.append("PROGRESS.md has no '## Open Problems' section")
        else:
            bullets = [ln for ln in m.group(1).splitlines()
                       if ln.strip().startswith("-")
                       and not ln.strip().lower().startswith("- (none)")]
            stems = {p.stem for p in files}
            open_stems = {pr["name"][:-3] for pr in parsed
                          if pr["status"] == "open"}
            for b in bullets:
                if not any(stem in b for stem in stems):
                    errors.append(f"PROGRESS.md Open Problems line cites no "
                                  f"existing problem file: {b.strip()[:70]}")
            for stem in open_stems:
                if not any(stem in b for b in bullets):
                    errors.append(f"{stem}.md: open problem not listed in "
                                  f"PROGRESS.md '## Open Problems'")

    # H4 fingerprint uniqueness
    seen: dict[frozenset, str] = {}
    for pr in parsed:
        if not pr["fingerprint"]:
            continue
        key = frozenset(tokens(pr["fingerprint"]))
        if key in seen:
            errors.append(f"{pr['name']}: Fingerprint duplicates "
                          f"{seen[key]} (recurrence = reopen, not a new "
                          f"file)")
        else:
            seen[key] = pr["name"]

    if errors:
        print("FAIL: problem lifecycle (PROBLEM_ROUTING.md §7):",
              file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    quiet = "--quiet" in sys.argv
    n_open = sum(1 for pr in parsed if pr["status"] == "open")
    if not quiet:
        print(f"[check_problems] OK — {len(parsed)} problem file(s): "
              f"{n_open} open, {len(parsed) - n_open} recovered/closed; "
              f"PROGRESS.md cross-check clean; fingerprints unique.")
    return 0


def check_query(query: str) -> int:
    qtok = tokens(query)
    if not qtok:
        print("FAIL: no matchable tokens in query", file=sys.stderr)
        return 1
    if not PROBLEMS.is_dir():
        print("FAIL: MONITORING/KNOWLEDGE/problems/ missing", file=sys.stderr)
        return 1
    hits = 0
    for p in sorted(PROBLEMS.glob("*.md")):
        if p.name.startswith("_") or not NAME_RE.match(p.name):
            continue
        pr = parse_problem(p)
        if not pr["fingerprint"]:
            continue
        shared = qtok & tokens(pr["fingerprint"])
        if shared:
            hits += 1
            print(f"{p.stem}  [status={pr['status']}]  shared: "
                  f"{', '.join(sorted(shared))}")
    if hits == 0:
        print(f"NO-HIT: no problem Fingerprint shares a token with "
              f"{query!r} — this is a NEW surface.", file=sys.stderr)
        return 2
    print(f"{hits} problem file(s) match — consult before planning/fixing "
          f"(PROBLEM_ROUTING.md §4/§5).", file=sys.stderr)
    return 0


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "check":
        if len(args) != 2:
            print("usage: check_problems.py check \"<fingerprint tokens>\"",
                  file=sys.stderr)
            return 1
        return check_query(args[1])
    return full_check()


if __name__ == "__main__":
    sys.exit(main())
