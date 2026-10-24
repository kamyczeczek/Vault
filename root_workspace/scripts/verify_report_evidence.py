#!/usr/bin/env python3
"""Forcing function against S59: every number claimed in a report must point
at a tool call.

Expected format in the report:
    ## Tool calls
    | Wartosc | Komenda | Surowy output (fragment) |
    |---------|---------|--------------------------|
    | 0.376 | `python scripts/_scratch/run_rerank.py` | `MRR@5=0.376` |

Usage:
    python scripts/verify_report_evidence.py [--report-only] [--enforce-after YYYY-MM-DD] <report.md>

Exit 0 + ALL_NUMBERS_HAVE_TOOLCALLS when every claimed number appears in
the Wartosc column; exit 1 with the missing list otherwise.
--report-only prints the missing list but exits 0 (for report authors).
--enforce-after skips reports whose filename date is older than the cutoff:
prints SKIPPED_PRE_STANDARD and exits 0 (the ## Tool calls standard was
introduced 2026-10-13; earlier reports cannot be retrofitted honestly).
Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DECIMAL_RX = re.compile(r"(?<!\d)(\d+\.\d+)(?!\d)")
PERCENT_RX = re.compile(r"(?<!\d)(\d+(?:\.\d+)?%)(?!\d)")
FRACTION_RX = re.compile(r"(?<!\d)(\d+/\d+)(?!\d)")
BIGNUM_RX = re.compile(r"(?<!\d)(\d{3,})(?!\d)")

# Things that look like numbers but are not claims: dates, versions, line refs.
SKIP_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{2}:\d{2}(:\d{2})?$|^v?\d+\.\d+(\.\d+)+$")


def claimed_numbers(text: str) -> list[str]:
    """All claim-like numbers in the report body (outside ## Tool calls).

    Fenced code blocks are raw evidence, not claims — excluded. Date
    fragments (2026-10-13) are excluded via the dash-adjacency rule.
    """
    body = re.split(r"^## Tool calls", text, flags=re.M)[0]
    body = re.sub(r"```.*?```", "", body, flags=re.S)  # raw output, not claims
    body = re.sub(r"`[^`]*`", "", body)  # inline code (commands, ids)
    found: list[str] = []
    for rx, adj in ((FRACTION_RX, False), (PERCENT_RX, False),
                    (DECIMAL_RX, True), (BIGNUM_RX, True)):
        for m in rx.finditer(body):
            n = m.group(1)
            if adj:  # skip date fragments like 2026 in 2026-10-13
                before = body[m.start() - 1] if m.start() > 0 else ""
                after = body[m.end()] if m.end() < len(body) else ""
                if before == "-" or after == "-":
                    continue
            if SKIP_RX.match(n):
                continue
            found.append(n)
    out: list[str] = []
    for n in found:
        if SKIP_RX.match(n):
            continue
        if n not in out:
            out.append(n)
    return out


def toolcall_values(text: str) -> tuple[bool, list[str]]:
    """(has_section, values listed in the Wartosc column)."""
    m = re.search(r"^## Tool calls(.*)$", text, flags=re.M | re.S)
    if not m:
        return False, []
    section = m.group(1)
    # stop at the next ## heading
    nxt = re.search(r"^## ", section, flags=re.M)
    if nxt:
        section = section[:nxt.start()]
    values: list[str] = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in line.strip("|").split("|")]
        if len(cells) < 1 or not cells[0]:
            continue
        if re.match(r"^-+$", cells[0]) or cells[0].lower().startswith("wartos"):
            continue
        values.append(cells[0])
    return True, values


def main() -> int:
    ap = argparse.ArgumentParser(prog="verify_report_evidence.py")
    ap.add_argument("report", help="path to the report markdown file")
    ap.add_argument("--report-only", action="store_true",
                    help="list gaps but exit 0")
    ap.add_argument("--enforce-after", default=None, metavar="YYYY-MM-DD",
                    help="skip reports with a filename date older than this")
    a = ap.parse_args()
    if a.enforce_after:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", Path(a.report).name)
        if m and m.group(1) < a.enforce_after:
            print(f"SKIPPED_PRE_STANDARD: raport z {m.group(1)} "
                  f"sprzed {a.enforce_after}, sekcja ## Tool calls nie wymagana")
            return 0
    text = Path(a.report).read_text(encoding="utf-8")
    claimed = claimed_numbers(text)
    has_section, values = toolcall_values(text)
    print(f"CLAIMED_NUMBERS={len(claimed)} TOOLCALL_ROWS={len(values)} "
          f"HAS_TOOLCALLS_SECTION={has_section}")
    if not has_section:
        print("MISSING_TOOLCALLS_SECTION: raport nie ma sekcji ## Tool calls")
        for n in claimed:
            print(f"MISSING: {n}")
        return 0 if a.report_only else 1
    missing = [n for n in claimed
               if not any(n in v or v in n for v in values)]
    if missing:
        for n in missing:
            print(f"MISSING: {n}")
        return 0 if a.report_only else 1
    print("ALL_NUMBERS_HAVE_TOOLCALLS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
