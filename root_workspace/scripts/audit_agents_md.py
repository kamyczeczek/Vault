#!/usr/bin/env python3
"""audit_agents_md.py — classify AGENTS.md's token-efficiency section, repeatably.

Why this exists: the architecture review's own numbers were prose, so every
revision re-counted them by hand and got a different answer. Prose has no gate.
This module is the gate's artifact: it derives every count from the file, prints
the classification so a human can audit the classifier, and `--check` fails when
the picture drifts.

    python scripts/audit_agents_md.py            # classify + print counts
    python scripts/audit_agents_md.py --check    # exit 1 if the counts moved
    python scripts/audit_agents_md.py --report-check REVIEW.html
    python scripts/audit_agents_md.py --write-block REVIEW.html

`--check` guards AGENTS.md against the recorded baseline. It cannot see a report
that misquotes those counts, which is where the errors actually lived: a review
carried "18" three times with no arithmetic path yielding 18. So a report embeds
this script's output between `<!-- audit:begin -->` and `<!-- audit:end -->`, and
`--report-check` recomputes the block and diffs it against the document. The same
`report_block()` produces the text and compares it, so the report cannot quote a
number this script would not emit. `--write-block` regenerates the block in place
after a deliberate baseline change.

Classification is rule-based, not line-number-based, so editing AGENTS.md moves
the answer instead of breaking the script. Rules, in order:

  blank            the line is empty or whitespace
  routing-heading  a `##` heading whose text mentions "skill" and which heads a
                   block containing a routing anchor
  routing          a routing anchor (an "Integrate `skills/...`" instruction),
                   plus every `- ` bullet continuing that block
  heading          any other `##` heading
  evidence         everything else — measured discipline, pointers, catalogs

"Redundant" is deliberately NOT a category here. Whether a line duplicates
another is reported separately as a mechanical finding (exact or substring), so
the count cannot depend on a human judgement call about near-duplicates.

Stdlib only. See handoff/CONTEXT.md for who writes what.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"

# Baseline recorded 2026-10-03 by reading all 137 lines; re-recorded 2026-10-04
# after implementing candidate 4's recommendation (duplicate token-efficiency
# block deleted, AGENTS.md now 130 lines, span 62-98). `--check` compares
# against these, so a change to AGENTS.md that is not reflected in the report
# fails here instead of surviving until a reader notices.
EXPECTED = {"routing": 8, "evidence": 23, "heading": 1, "blank": 5, "total": 37}

SECTION_HEADING = re.compile(r"^##\s+(.*)$")
ROUTING_ANCHOR = re.compile(r"Integrate\s+`skills/")
BULLET = re.compile(r"^\s*-\s")


def section_span(lines: list[str]) -> tuple[int, int]:
    """1-based inclusive span of the token-efficiency section.

    Starts at the first heading naming token efficiency and runs to the next
    heading that is NOT part of it. A heading belongs to the section when it
    names token efficiency or a skill — `## Token efficiency skill` is the
    second routing block, not the end of the span. Stopping at the first
    heading of any kind truncated the audit at :91 and silently dropped 14 of
    the 51 lines.

    Derived, never hardcoded, so inserting a section above does not move the
    audited range without the counts changing.
    """
    start = None
    for i, line in enumerate(lines):
        m = SECTION_HEADING.match(line)
        if m and "token efficiency" in m.group(1).lower():
            start = i
            break
    if start is None:
        raise SystemExit("audit_agents_md: no '## Token efficiency' heading found")
    for j in range(start + 1, len(lines)):
        m = SECTION_HEADING.match(lines[j])
        if not m:
            continue
        title = m.group(1).lower()
        if "token efficiency" in title or "skill" in title:
            continue
        return start + 1, j
    return start + 1, len(lines)


def classify(lines: list[str], lo: int, hi: int) -> list[tuple[int, str, str]]:
    """Return (line_no, category, text) for every line in the audited span."""
    out: list[tuple[int, str, str]] = []
    in_block = False
    for n in range(lo, hi + 1):
        raw = lines[n - 1]
        text = raw.strip()

        if not text:
            # A blank does NOT end a routing block. Block 1 puts its anchor and
            # its bullets on consecutive lines (:57-:64); block 2 separates them
            # with a blank (:94 anchor, :95 blank, :96-:102 bullets). Terminating
            # on the blank classified 7 of the 17 routing lines as evidence.
            category = "blank"
        elif ROUTING_ANCHOR.search(text):
            category = "routing"
            in_block = True
        elif in_block and BULLET.match(raw):
            category = "routing"
        elif SECTION_HEADING.match(raw):
            # A heading heads the block it introduces. Look ahead past blanks for
            # the first non-blank line; if that is a routing anchor, this
            # heading belongs to the routing prose, not to the surrounding prose.
            nxt = n + 1
            while nxt <= hi and not lines[nxt - 1].strip():
                nxt += 1
            ahead = lines[nxt - 1].strip() if nxt <= hi else ""
            category = (
                "routing"
                if "skill" in SECTION_HEADING.match(raw).group(1).lower()
                and ROUTING_ANCHOR.search(ahead)
                else "heading"
            )
            in_block = False
        else:
            category = "evidence"
            in_block = False
        out.append((n, category, text))
    return out


def duplicates(rows: list[tuple[int, str, str]]) -> list[str]:
    """Lines that repeat another line in the span. Mechanical, not a judgement.

    Compared on bullet-stripped text: `:85` is "- Re-measure after changes: ..."
    while `:66` is "Evidence: ... Re-measure after changes: ..." — the same
    sentence wearing different markdown, which a raw string compare misses.
    """
    def norm(text: str) -> str:
        return BULLET.sub("", text).strip()

    evidence = [(n, norm(t)) for n, c, t in rows if c == "evidence"]
    found = []
    for n, t in evidence:
        for m, u in evidence:
            # Report each pair once, from the later line's point of view: the
            # later occurrence is the redundant one.
            if n <= m or not t or not u:
                continue
            if t == u or t in u:
                kind = "an exact" if t == u else "a substring"
                found.append(f"  :{n} is {kind} repeat of :{m}  ({t[:64]})")
                break
    return sorted(set(found))


def render(rows: list[tuple[int, str, str]], lo: int, hi: int) -> str:
    marks = {"routing": "R", "evidence": "E", "heading": "H", "blank": "."}
    lines_out = [f"audited span: AGENTS.md:{lo}-{hi} ({hi - lo + 1} lines)", ""]
    for n, cat, text in rows:
        shown = (text[:58] + "...") if len(text) > 58 else text
        # rstrip: a blank line's category marker would otherwise leave two
        # trailing spaces, and this output is pasted verbatim into a committed
        # file — where `git diff --check` reads them as whitespace errors. The
        # gate's own output must not need a whitespace exemption.
        lines_out.append(f"  {marks[cat]} :{n:<4} {shown}".rstrip())
    return "\n".join(lines_out)


def tally(rows: list[tuple[int, str, str]]) -> dict[str, int]:
    counts = {k: 0 for k in EXPECTED if k != "total"}
    for _, cat, _ in rows:
        counts[cat] += 1
    counts["total"] = len(rows)
    return counts


# --- report citation ---------------------------------------------------------
#
# `--check` guards AGENTS.md against the baseline. It does nothing about a
# *report* that quotes the numbers: the architecture review carried "18" three
# times with no arithmetic path yielding 18, and "35" before it — both invisible
# to `--check`, because the error lived in the document, not in the file. So the
# report embeds this script's output verbatim between two markers, and
# `--report-check` recomputes it and diffs.
#
# One function produces the block and the same function compares it. That is the
# whole design: a report cannot quote a number this script would not emit.

BLOCK_BEGIN = "<!-- audit:begin -->"
BLOCK_END = "<!-- audit:end -->"
COUNT_KEYS = ("routing", "evidence", "heading", "blank", "total")


def derived_sums(
    counts: dict[str, int], dups: list[str], lo: int, hi: int, total: int
) -> list[str]:
    """Figures a report quotes in prose, derived here rather than by hand.

    v7 of the architecture review was caught quoting numbers the block did not
    contain: "19 lines a router could retire" (routing + 2 duplicates), and
    "AGENTS.md is 137 lines / lines 1–54 and 106–137 are not audited". The block
    was gated, the prose was not, so the document could pass the gate and still be
    wrong — the same defect one level down. The fix is not a narrower claim but
    these lines: anything a report may state as a figure has to be emitted here,
    by the same run that emits the categories.

    The span's complement is included because "lines 1–54 are not audited" is a
    claim about the file, and it moves whenever the file does.

    These are sums and spans, not classifications. "Retireable" is the review's
    policy claim (a router retires routing prose; a separate dedup pass retires
    the duplicate lines) — the arithmetic is gated, the policy is not.
    """
    outside = []
    if lo > 1:
        outside.append(f":1-:{lo - 1}")
    if hi < total:
        outside.append(f":{hi + 1}-:{total}")
    rows = [
        ("derived sums (not classifications; policy stays the reader's):", ""),
        (
            f"  retireable if both actions happen (routing {counts['routing']}"
            f" + {len(dups)} duplicate evidence)",
            str(counts["routing"] + len(dups)),
        ),
        (
            "  coverage sum (routing + evidence + heading + blank)",
            f"{counts['routing']} + {counts['evidence']} + {counts['heading']}"
            f" + {counts['blank']} = {counts['total']}",
        ),
        ("  AGENTS.md lines in total", str(total)),
        ("  outside the audited span (nothing is claimed about these)", ", ".join(outside) or "none"),
    ]
    return [f"{label:<62} {value}".rstrip() for label, value in rows]


def report_block(
    rows: list[tuple[int, str, str]],
    lo: int,
    hi: int,
    counts: dict[str, int],
    total: int,
) -> str:
    """The canonical text a report must carry between the markers.

    Also what a bare run prints, so the block and the terminal output cannot
    disagree by construction.
    """
    out = [render(rows, lo, hi), ""]
    out += [f"  {key:<9} {counts[key]:>3}" for key in COUNT_KEYS]
    dups = duplicates(rows)
    if dups:
        out += ["", "  duplicate evidence lines (not a category — a separate finding):"]
        out += dups
    out += [""] + derived_sums(counts, dups, lo, hi, total)
    return "\n".join(out)


def normalize_block(text: str) -> str:
    """Compare text by content, not by the editor that touched it.

    CRLF vs LF, trailing spaces and surrounding blank lines are transport, not
    claims. Everything else is a claim and must match byte for byte.
    """
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def extract_block(text: str) -> str:
    """Return the text between the markers, or exit 1 if it is not well-formed.

    Zero markers, two blocks, or reversed markers are all errors: each means the
    document no longer declares which numbers are generated, and silently
    skipping the check would restore exactly the prose-drift this exists to stop.
    """
    begins = text.count(BLOCK_BEGIN)
    ends = text.count(BLOCK_END)
    if begins != 1 or ends != 1:
        raise SystemExit(
            f"audit_agents_md: report must carry exactly one {BLOCK_BEGIN}…{BLOCK_END} "
            f"block (found {begins} begin, {ends} end)"
        )
    start = text.index(BLOCK_BEGIN) + len(BLOCK_BEGIN)
    end = text.index(BLOCK_END)
    if end < start:
        raise SystemExit("audit_agents_md: report audit block is inverted")
    return text[start:end]


def replace_block(text: str, block: str) -> str:
    """Rewrite the block in place — one writer, so the numbers are generated."""
    start = text.index(BLOCK_BEGIN) + len(BLOCK_BEGIN)
    end = text.index(BLOCK_END)
    return text[:start] + "\n" + block + "\n" + text[end:]


def block_diff(want: str, got: str) -> str:
    """Line-by-line diff, so a mismatch names the wrong number instead of
    reporting that two strings differ."""
    return "\n".join(
        difflib.unified_diff(
            want.split("\n"),
            got.split("\n"),
            fromfile="report",
            tofile="script",
            lineterm="",
            n=1,
        )
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if the classification differs from the recorded baseline",
    )
    ap.add_argument(
        "--report-check",
        metavar="REPORT",
        help="exit 1 if REPORT's audit block differs from this script's live output",
    )
    ap.add_argument(
        "--write-block",
        metavar="REPORT",
        help="rewrite REPORT's audit block from live output (the one writer)",
    )
    args = ap.parse_args(argv)

    if not AGENTS.is_file():
        print(f"audit_agents_md: {AGENTS} not found", file=sys.stderr)
        return 1
    lines = AGENTS.read_text(encoding="utf-8").splitlines()
    lo, hi = section_span(lines)
    rows = classify(lines, lo, hi)
    counts = tally(rows)
    block = report_block(rows, lo, hi, counts, len(lines))

    if args.write_block:
        path = Path(args.write_block)
        if not path.is_file():
            print(f"audit_agents_md: {path} not found", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        # newline="\n": .gitattributes is `* text=auto eol=lf`, and write_text on
        # Windows would otherwise rewrite the whole file as CRLF — the report
        # would show as modified after every regeneration for a reason that is
        # not an edit.
        path.write_text(replace_block(text, block), encoding="utf-8", newline="\n")
        print(f"OK — wrote audit block into {path}")
        return 0

    print(block)

    drift = [
        f"{k}: expected {EXPECTED[k]}, got {counts[k]}"
        for k in EXPECTED
        if counts[k] != EXPECTED[k]
    ]
    if args.report_check:
        path = Path(args.report_check)
        if not path.is_file():
            print(f"audit_agents_md: {path} not found", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        want = normalize_block(extract_block(text))
        got = normalize_block(block)
        rc = 0
        if want != got:
            print(f"\nFAIL — {path} quotes numbers this script does not emit:", file=sys.stderr)
            print(block_diff(want, got), file=sys.stderr)
            print(
                "  regenerate the block: python scripts/audit_agents_md.py "
                f"--write-block {path}",
                file=sys.stderr,
            )
            rc = 1
        if drift:
            print(
                f"\nFAIL — AGENTS.md no longer matches the recorded baseline:\n"
                + "\n".join(f"  {d}" for d in drift),
                file=sys.stderr,
            )
            print(
                "  the architecture review cites these counts; update it or the\n"
                "  baseline in this script, deliberately.",
                file=sys.stderr,
            )
            rc = 1
        if rc:
            return 1
        print(f"\nOK — {path} quotes exactly what this script emits.")
        return 0

    if not args.check:
        print("\n  R=routing  E=evidence  H=heading  .=blank")
        return 0

    print()
    if drift:
        print("FAIL — AGENTS.md no longer matches the recorded baseline:", file=sys.stderr)
        for d in drift:
            print(f"  {d}", file=sys.stderr)
        print(
            "  the architecture review cites these counts; update it or the\n"
            "  baseline in this script, deliberately.",
            file=sys.stderr,
        )
        return 1
    print("OK — classification matches the recorded baseline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())