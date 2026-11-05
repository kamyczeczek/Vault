#!/usr/bin/env python3
"""
check_workflow.py — PROCESS/WORKFLOW.md routing-table integrity gate.

Validates the deterministic knowledge-routing table (section 5) in
PROCESS/WORKFLOW.md against the LIVE brains, so a routing row that has
drifted (corpus change broke its query, min-score unmet, malformed row,
scenario coverage hole, or a documented skill that no longer exists)
blocks the commit instead of silently mis-routing future tasks.

Checks (fail-loud, exit 1 on any violation):
  1. rows parse     — every "| K-NN | ..." line has exactly 6 fields,
                      brain tag in {skill, scar}, numeric min-score,
                      no pipe inside the query field
  2. ids            — unique and contiguous K-01..K-NN (no gaps/dupes)
  3. queries live   — each row's query run against the corresponding
  4. coverage       - each stage 01_align..07_reflect appears in at least one row
                      skills/<name>/SKILL.md folder

Usage:
    python PROCESS/check_workflow.py            # full report
    python PROCESS/check_workflow.py --quiet    # silent on pass
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "PROCESS" / "WORKFLOW.md"
SKILL_ASK = ROOT / "brain" / "ask.py"
SCAR_ASK = ROOT / "brain" / "ask.py"
SKILLS_DIR = ROOT / "skills"
SCENARIOS = ("01_align", "02_research", "03_plan", "04_implement", "05_verify", "06_modify", "07_reflect")
ROW_RE = re.compile(r"^\|\s*(K-\d+)\s*\|")
TOP_SCORE_RE = re.compile(r"^\[(\d+)\]")
SKILL_NAME_RE = re.compile(r"(?<![\w/])/([a-z0-9][a-z0-9-]*)")


def parse_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        if not ROW_RE.match(line.strip()):
            continue
        fields = [f.strip() for f in line.strip().strip("|").split("|")]
        rows.append(fields)
    return rows


def live_top_score(brain: str, query: str) -> tuple[int, int]:
    """Return (exit_code, top_score) for a query against the brain."""
    ask = SKILL_ASK if brain == "skill" else SCAR_ASK
    command = [sys.executable, "-X", "utf8", str(ask)]
    if brain == "scar" and query == "rejected":
        r = subprocess.run(command + ["rejected"], capture_output=True,
                           text=True, cwd=ROOT)
        return r.returncode, 1 if "Negative Memory Buffer" in r.stdout else 0
    r = subprocess.run(command + [query, "--limit", "1"],
                       capture_output=True, text=True, cwd=ROOT)
    score = 0
    for ln in r.stdout.splitlines():
        m = TOP_SCORE_RE.match(ln.strip())
        if m:
            score = max(score, int(m.group(1)))
            break
    return r.returncode, score


def main() -> int:
    quiet = "--quiet" in sys.argv
    if not WORKFLOW.exists():
        print("FAIL: PROCESS/WORKFLOW.md missing", file=sys.stderr)
        return 1
    rows = parse_rows(WORKFLOW.read_text(encoding="utf-8"))
    if not rows:
        print("FAIL: no routing rows found in PROCESS/WORKFLOW.md",
              file=sys.stderr)
        return 1

    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_scen: set[str] = set()

    # 1 + 2: field shape, brain tag, min-score, id uniqueness/contiguity
    for f in rows:
        rid = f[0]
        if len(f) != 6:
            errors.append(f"{rid}: expected 6 fields, got {len(f)}: {f}")
            continue
        if f[2] not in ("skill", "scar"):
            errors.append(f"{rid}: brain tag {f[2]!r} not in skill/scar")
        if not f[4].isdigit():
            errors.append(f"{rid}: min-score {f[4]!r} is not numeric")
        if rid in seen_ids:
            errors.append(f"{rid}: duplicate id")
        seen_ids.add(rid)
        for s in SCENARIOS:
            if re.search(rf"\b{s}\b", f[1]):
                seen_scen.add(s)

    nums = sorted(int(rid.split("-")[1]) for rid in seen_ids)
    if nums != list(range(1, len(nums) + 1)):
        missing = [n for n in range(1, len(nums) + 1) if n not in nums]
        errors.append(f"ids not contiguous (missing: "
                      f"{', '.join('K-%02d' % n for n in missing)})")

    # 3 + 5: queries live; documented skill targets exist
    for f in rows:
        rid = f[0]
        if len(f) != 6:
            continue
        brain, query, min_score, expected = f[2], f[3], int(f[4]), f[5]
        if brain in ("skill", "scar"):
            rc, score = live_top_score(brain, query)
            if rc != 0:
                errors.append(f"{rid}: query misses ({brain}): {query!r}")
            elif score < min_score:
                errors.append(f"{rid}: top score {score} < min-score "
                              f"{min_score}: {query!r}")
        if brain == "skill":
            for name in SKILL_NAME_RE.findall(expected):
                if not (SKILLS_DIR / name / "SKILL.md").is_file():
                    errors.append(f"{rid}: documented skill "
                                  f"{name!r} has no SKILL.md on disk")

    # 4: scenario coverage
    for s in SCENARIOS:
        if s not in seen_scen:
            errors.append(f"scenario {s} has no routing row (coverage hole)")

    if errors:
        print("FAIL: PROCESS/WORKFLOW.md routing table:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print(f"{len(errors)} violation(s). Fix the rows (probe live first) "
              f"or the corpus, then re-run.", file=sys.stderr)
        return 1
    if not quiet:
        live = sum(1 for f in rows if len(f) == 6)
        print(f"[check_workflow] OK — {live} routing row(s) parsed, "
              f"all queries live at min-score, scenarios "
              f"{'/'.join(SCENARIOS)} covered, documented skills exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
