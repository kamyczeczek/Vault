#!/usr/bin/env python3
"""audit_prose_numbers.py — every number in a report's prose is gated, not trusted.

    python scripts/audit_prose_numbers.py --list   REPORT.html   # what is unclassified
    python scripts/audit_prose_numbers.py --check  REPORT.html   # exit 1 if unclassified

Why this exists: `audit_agents_md.py --report-check` diffs the generated block
against the live output, and that is the whole of its reach. A report's prose
lives outside the block, so prose can quote a figure the block does not emit and
the gate stays green. That is not hypothetical — v7 says "AGENTS.md is 137 lines"
in four places while the block's complement moves to `:106-:140` the moment
AGENTS.md grows by three lines, and `--report-check` reports nothing. A gate
that guards the generated paragraph and ignores the hand-typed ones is a gate on
half the document.

The previous fix for that was a throwaway probe in %TEMP%: it found the live 137
and the ":1-:54, :106-:137" complement, and then nothing re-ran it. A finding whose
detector cannot be re-derived decays exactly like the figure it found — that was
F1 again, one level down. So the detector is this file, committed, tested, and
called by the root gate.

The rule, in one line: every numeric token in the prose is either

  1. emitted by `audit_agents_md.report_block()` — re-derived on every run, or
  2. matched by a mechanical class below (a date, a `:113-137` line reference, a
     `v7` version tag, an ordered-item marker), or
  3. listed in EXEMPT with a class and a reason.

Anything else fails. The check is also bidirectional: a listed exemption that no
longer appears in the prose fails too, so the list cannot quietly accumulate
entries for numbers that were since deleted — a whitelist that only grows is a
second copy of the prose, drifting.

The judgement calls live in EXEMPT and nowhere else. They are the part a human
owns, and they are in a diffable table rather than in a report's paragraph, which
is the product.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_agents_md as audit  # noqa: E402

# Regions that are not prose and not claims: the generated block (audit's own
# numbers, checked by --report-check), <script>/<style> bodies (Tailwind's CDN
# tag and the stylesheet), and HTML tags themselves (`colspan="2"`, `w-44`,
# `text-red-700` — scaffolding digits, not statements about the workspace).
SCRIPT_OR_STYLE = re.compile(r"<(script|style)\b.*?</\1\s*>", re.IGNORECASE | re.DOTALL)
TAG = re.compile(r"<[^>]*>")
BLOCK_REGION = re.compile(
    re.escape(audit.BLOCK_BEGIN) + r".*?" + re.escape(audit.BLOCK_END), re.DOTALL
)

# Mechanical classes. Each is a shape, not a topic: a shape is checkable by a
# human reading one regex, a topic ("figures about other files") is a judgement
# that has to be listed per number in EXEMPT.
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
VERSION = re.compile(r"(?<![A-Za-z0-9])[vV]\d+(?![0-9])")
DECISION_ID = re.compile(r"(?<![A-Za-z0-9])D\d{1,2}(?![0-9])")
# A colon-anchored pointer: `scripts/x.py:76-98`, `:113-137`, `:1-:54`. The
# colon makes it a reference, but not every reference is current: `:61-:111`
# survived a 3-line span shift while this class waved it through, because the
# shape alone was the whole check. So a bare ref counts as a pointer only if
# every figure in it is a line number the block itself emits — the same bar
# `WORD_LINE_REF` already clears — and anything else needs a human's class in
# EXEMPT. Two carve-outs, both for refs that point outside the audited file:
# a ref glued to another file's name (`scripts/build_handoff.py:76-98`), and
# a bare ref on a line that names exactly one other file (`:150-151` in a
# `<li>` about `build_handoff.py`). AGENTS.md itself is neither: a line that
# mentions it is making a claim about the audited file, and history quotes
# (`v4 claimed … :106-137`) are claims too — stale ones, which is the point.
# Glued-ness is same-token adjacency and the single-file scan is line-scoped,
# neither a neighbourhood window — see `overlaps` for why that matters. Two
# files on one line is ambiguous and fails closed to validation.
LINE_REF = re.compile(r":\s*\d+(?:\s*[-–]\s*:?\s*\d+)?")
FILENAME = re.compile(
    r"(?=[A-Za-z0-9_.\-+/\\]*[A-Za-z])"  # a bare version ("11.7") is not a name
    r"[A-Za-z0-9_][A-Za-z0-9_.\-+/\\]*\.[A-Za-z0-9]{2,5}"
)
FOREIGN_GLUED = re.compile(
    r"(?=[A-Za-z0-9_.\-+/\\]*[A-Za-z])"
    r"[A-Za-z0-9_][A-Za-z0-9_.\-+/\\]*\.[A-Za-z0-9]{2,5}\s*$"
)
# A word-anchored range: "lines 1–54", "lines 20-25". NOT a shape on its own —
# "lines 1–54 are not audited" is a claim about the file, and it was exactly the
# claim that drifted while the gate stayed green. It counts as a pointer only if
# every figure in it is a line number the block itself emits; otherwise it needs
# a class like any other claim.
WORD_LINE_REF = re.compile(r"\blines?\s+(\d+(?:\s*[-–]\s*\d+)?)", re.IGNORECASE)
# A badge: an element whose entire text content is the number, e.g.
# `<span class="text-cyan-700">4</span>`. The report enumerates candidates and
# badges each one; the digit names which row this is, it is not a measurement.
BADGE = re.compile(
    r"<(?:span|td|th|div|b|i|code)[^>]*>\s*" + r"(?P<n>\d+(?:\.\d+)?)\s*</"
)
# A named item: "Candidate 4", "Step 3's", "candidates 1–4". The report's own
# vocabulary for the rows it walks through. A digit that names a row is a pointer
# to prose, not a figure about the workspace.
ITEM_NOUN = re.compile(
    r"\b(?:candidates?|steps?|phases?|options?|findings?|flags?|rules?|items?|"
    r"actions?|candidates?-?list|phase)\b\s*:?\s*(?:\d+\s*[-–]\s*)?$",
    re.IGNORECASE,
)
# A slug fragment: `phase-5`, `step-2`, `v7-2`. The digit is part of a name, so it
# cannot be read as a quantity. The character before the dash must be a letter or
# an underscore: allowing a digit there made `1-2` and `16-17` slugs, which is how
# a report's claim about which lines are not audited passed as an identifier.
SLUG = re.compile(r"[A-Za-z_]-\d+(?:\.\d+)?(?![0-9])")
# An identifier that begins with a digit: `4-steps-1`, `2-of-4`. `SLUG` cannot
LEADING_ID = re.compile(r"\b\d+(?:-[A-Za-z][A-Za-z0-9]*)+")
# A rewrite arrow: `2 → 3`, `+20→+50`, `≈neutral→~610`. A before-and-after, which
# is two figures the report is deliberately pairing. Deliberately NOT a bare
# hyphenated range: "lines 16-17 are not audited" is a claim about the file, and
# letting `\d+-\d+` through here waved the G1 complement straight past the gate.
RANGE = re.compile(r"\d+\s*→\s*~?\d+")
# A single-token `<code>` span holding a name: `plain_language_meter_d003.md`,
# `a15ebf4`, `CONTEXT.md`. Digits inside one are part of the name. Two conditions,
# each closing a hole: the span must have no whitespace, or `<code>AGENTS.md is 137
# lines</code>` counts as prose; and it must contain a letter, or `<code>137</code>`
# — a bare figure in a code span, which is the exact shape the defect takes — would
# be exempt as an identifier. Checked after the specific shapes so a line reference
# is named `line-ref` rather than borrowing this class's name.
CODE_SPAN = re.compile(r"<code[^>]*>([^<]+)</code>")

# A section or label number: `<h2>4 · A gate requires…`, `<b>3 · No hook…`.
# The digit indexes the item, so it names a row rather than measuring anything.
HEADING_NUM = re.compile(r"<(?:h[1-6]|b|strong)[^>]*>\s*(?P<n>\d+)\s*[·.]\s")
# A rule or node id: `R13`, `R3`, `A3["…"]` — the gate's own identifier, which
# `check_workspace_integrity.py` owns.
RULE_ID = re.compile(r"(?<![A-Za-z0-9])[RA]\d{1,2}(?![0-9])")
# An action id: "4 step 1", "4 step 3". The report's own identifier for a step of
# a candidate, in prose and in tables alike.
ACTION_ID = re.compile(r"\b\d+\s+step\s+\d+\b", re.IGNORECASE)

# A number, with thousands separators kept inside the token: `28,926` is one
# figure, not the two that `\d+` alone reports. The separator is stripped for
# comparison, so a table's "4,816" and a sentence's "4816" are one entry rather
# than two — otherwise every regrouped figure silently needs its own exemption.
NUMBER = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")

# Classes an entry may declare. A value can carry more than one, and that is not
# a loophole: "50" is `35 + 15 = 50` (arithmetic on two withdrawn figures) at
# :106 and `51 − 1 = 50` (a mutation row on the gate's own baseline) at :329.
# Forcing one class on it would be a false claim in the table, which is the
# defect this workstream exists to remove — the table would then assert
# something untrue about the report it guards.
#
#   other-file          a figure about a file other than AGENTS.md — the block
#                       emits nothing about these, so they cannot be checked
#                       against it. Dated, because the file may vanish (see
#                       `dead-file`).
#   dead-file           a figure about a file that no longer exists.
#   withdrawn           a figure an earlier revision stated and this one retracts.
#   derived-from-gate   arithmetic on figures the block does emit (51 − 1 = 50).
#   cost-estimate       a candidate's projected effect, not a measurement.
#   commit-hash         digits inside a git hash — `a15ebf4`, `931aac5`.
#   ordinal             a count of things the report names in words ("the same 7
#                       rules", "6 project repos", "invariant 7").
#   diagram-label       a figure inside a mermaid label, duplicating prose.
#   zero                a literal 0 in an inequality or an expectation.
#   quoted-ags-evidence  a figure quoted out of AGENTS.md's own evidence bullet.
#                       Named honestly: `audit_agents_md.py --check` catches that
#                       line being deleted, not its figures being edited, so a
#                       quote of it rots until someone re-reads AGENTS.md. The
#                       gate cannot close that, and this entry says so instead of
#                       implying the number is verified.
EXEMPT: dict[str, tuple[tuple[str, ...], str]] = {
    "0": (("zero",), "'cost 0', '> 0 always' in the withdrawn step-3 arithmetic."),
    "12": (("withdrawn",), "the contrast figure in 'the gap is 182 lines, not 12' (:690) — v4's own number, restated to reject it."),
    "3": (("ordinal",), "'4 superseded pairs', '1, 2 and 3 all add or tighten gates' — counts the report names in words."),
    "0.0": (("other-file",), "re-read delta quoted from TOKEN-EFFICIENCY.md (measured 2026-10-03)."),
    "1.17": (("other-file",), "the re-read ratio quoted from TOKEN-EFFICIENCY.md (measured 2026-10-03)."),
    "4.0": (("quoted-ags-evidence",), "AGENTS.md's own evidence bullet ('4.0M at 0.0%'); --check catches the line, not a figure edited inside it."),
    "11.7": (("quoted-ags-evidence",), "AGENTS.md's own evidence bullet ('tool output 11.7x'); see the 4.0 entry for what this does not catch."),
    "4": (("commit-hash", "ordinal", "diagram-label"), "digits of the hash a15ebf4; '4 superseded pairs' in a diagram; an ordinal count in prose."),
    "6": (("ordinal",), "'6 project repos', 'invariant 6' — counts the report names, not measurements."),
    "7": (("ordinal",), "'the same 7 rules', 'invariant 7' — counts the report names."),
    "10": (("withdrawn",), "v4's evidence-row figure of 10, retracted at :141 and :857."),
    "11": (("cost-estimate",), "11K tokens re-paid per turn, an estimate at the cache ratio TOKEN-EFFICIENCY.md records."),
    "13": (("other-file",), "case count of scripts/test_build_handoff.py, re-derivable by pytest --collect-only (2026-10-03)."),
    "14": (("derived-from-gate",), "51 − 37 = 14 — arithmetic on figures the block emits (:303, :836)."),
    "15": (("withdrawn",), "the '15' of the withdrawn '35 + 15 = 50' arithmetic at :106."),
    "16": (("derived-from-gate",), "17 − 1 = 16 in a mutation row (:329)."),
    "18": (("derived-from-gate", "withdrawn"), "17 + 1 = 18 in a mutation row (:328); v6's withdrawn live total (:201)."),
    "20": (("withdrawn",), "the '+20 gate lines' figure v7 retracts; also the 'Q0–Q20' gate-list bounds."),
    "22": (("withdrawn", "other-file"), "v5's hand-split '22 evidence', which the gate contradicts with 24; and scratch/flag counts, none of them AGENTS.md's."),
    "25": (("other-file",), "count of handoff/flags/*.md — the report's own flags, not AGENTS.md's figures."),
    "27": (("other-file",), "MB and file counts of the untracked scripts/_scratch dump (measured 2026-10-03)."),
    "29": (("other-file",), "count of skill directories at the workspace root; re-derivable by skills/verify_catalog.py, measured 2026-10-03."),
    "35": (("withdrawn", "cost-estimate"), "the ~35-line figure v7 retracts in favour of the counted 17; also a candidate-1 cost estimate."),
    "38": (("withdrawn",), "v4's evidence-row count, corrected at :812."),
    "41": (("withdrawn",), "the size of v4's audit table — a figure this revision retracts (:136, :850)."),
    "43": (("other-file",), "KB of the generated HANDOFF.md (measured 2026-10-03)."),
    "50": (("withdrawn", "derived-from-gate"), "35 + 15 = 50 on withdrawn figures (:106); 51 − 1 = 50 in a mutation row (:329)."),
    "52": (("derived-from-gate",), "51 + 1 = 52 in a mutation row (:328)."),
    "110": (("withdrawn", "cost-estimate"), "how much v4 flattered candidate 1 by, and the delta it reports."),
    "141": (("dead-file",), "lines of scripts/migrate_handoff_to_flags.py, which no longer exists — labelled in the report at :200."),
    "150": (("withdrawn", "other-file"), "v4's line count for migrate_handoff_to_flags.py; the file is gone (:109). Also build_handoff.py's render ref (:710 :150-151, other-file)."),
    "180": (("other-file",), "the 180-line deep-note ceiling the report proposes, not one it measured (:726)."),
    "182": (("other-file",), "lines held in handoff/deep notes (measured 2026-10-03); not AGENTS.md's figures."),
    "287": (("other-file",), "flag-body lines in a diagram, whole files rather than the generated view."),
    "359": (("other-file",), "lines of the untracked HANDOFF.pre-migration.md, on disk 2026-10-03."),
    "460": (("withdrawn",), "v4's byte-derived line figure, retracted at :110."),
    "498": (("other-file",), "lines of the generated HANDOFF.md view (measured 2026-10-03)."),
    "500": (("cost-estimate",), "candidate C's claimed reduction — an estimate on the author's arithmetic, and a dead-matter total."),
    "560": (("cost-estimate",), "candidate 1's net reduction, an estimate (:110)."),
    "610": (("withdrawn", "cost-estimate"), "the '~610 lines (bytes, not lines)' figure v7 lists as withdrawn; also a candidate's size."),
    "812": (("other-file",), "re-read ratio quoted from TOKEN-EFFICIENCY.md (measured 2026-10-03)."),
    "931": (("commit-hash",), "digits of the commit hash 931aac5 (:347)."),
    "28926": (("other-file",), "bytes of HANDOFF.pre-migration.md (measured 2026-10-03)."),
    "4816": (("dead-file",), "bytes of the deleted migrate_handoff_to_flags.py."),
    "36.5": (("other-file",), "a token count for the deep notes, from TOKEN-EFFICIENCY.md."),
    "5.4": (("other-file",), "MB of one file in the untracked scratch dump (measured 2026-10-03)."),
    "8.0": (("other-file",), "MB of one file in the untracked scratch dump (measured 2026-10-03)."),
    "12.0": (("other-file",), "MB of one file in the untracked scratch dump (measured 2026-10-03)."),
    "80.6": (("other-file",), "28926/359 — a ratio between two other-file figures, both dated 2026-10-03."),
    "69.5": (("quoted-ags-evidence",), "AGENTS.md's own evidence bullet ('69.5M tokens/29 sessions')."),
    "95": (("other-file",), "lines of handoff/deep/deep-research-kg-icm.md, read 2026-10-03."),
    "502": (("quoted-ags-evidence",), "AGENTS.md's own evidence bullet ('23x/502K')."),
    "34.2": (("dead-file",), "4816/141 — a ratio on a file that no longer exists."),
    "106": (("withdrawn",), "v4's stale AGENTS.md span quote (:106-137 at :136, :849); the span moved +3 in d98d284, see 137."),
    "137": (("withdrawn",), "the other endpoint of v4's stale span quote (:136, :849); see 106."),
    "55": (("other-file",), "audit_agents_md.py's own rule table (:287 :55, :289 :55-:105) — the audit script's lines, not AGENTS.md's."),
    "63": (("other-file",), "v4's assumed bytes/line ratio, retracted at :120 and :478; a historical assumption about HANDOFF.pre-migration.md, not AGENTS.md's lines."),
    "101": (("other-file",), "check_wiring.py retired-names range :101-107 (:896); the audit script's file, not AGENTS.md's."),
    "105": (("other-file",), "the audit-script span in the rule table (:289 :55-:105); see 55."),
    "123": (("other-file",), "build_handoff.py's --check contract (:578 :123-124); the paragraph states the contract without naming the file."),
    "124": (("other-file",), "the same contract (:578); see 123."),
    "155": (("other-file",), "the same contract (:578 :155-156); see 123."),
    "156": (("other-file",), "the same contract (:578); :570's occurrence inherits mechanically from its build_handoff.py label."),
    "125": (("other-file",), "a cross-file bare ref: build_handoff.py's sort key (:582); :400, :908 and :927 inherit mechanically from their file labels."),
    "151": (("other-file",), "build_handoff.py's render ref (:710 :150-151, no filename on the line); :696 inherits mechanically."),
    "2": (("withdrawn", "ordinal", "diagram-label"), "withdrawn duplicate arithmetic (17+2, 2 duplicate evidence :282,:284,:794,:823,:829,:863,:951,:1151); the report's own identifiers and small counts it names (Block 2 :103, Tier 2 :709, candidate 2 :906,:1101,:1138, '2 one-shot scripts' :472, '2 required names' :977); mermaid node ids (G2/F2/OK2/A2 :536,:988-:994)."),
    "17": (("withdrawn",), "v7's counted routing lines (candidate 4's denominator, quoted --check output in mutation rows :313-314); the 2026-10-04 deletion moved the live count to 8."),
    "19": (("withdrawn", "other-file"), "candidate 4's removal figure (17+2, implemented 2026-10-04); skill-catalog entry counts in other files and mermaid (:888,:913,:965,:974); router-catalog contrast kept as stated 2026-10-03 (:69,:196)."),
    "24": (("withdrawn", "other-file"), "v7's evidence count (candidate 4's table :282,:284,:823,:830); per-file catalog lines at :879 (audit_agents_md.py, measured 2026-10-03)."),
    "51": (("withdrawn",), "v7's section total (:289, quoted --check in mutation rows :313-314); the deletion moved the live total to 37."),
    "96": (("withdrawn",), "pre-deletion range :96-102 (:793); the duplicate-block endpoint moved with the deletion."),
    "98": (("withdrawn",), "pre-deletion duplicate-block refs (:881,:932,:1128); the block was removed 2026-10-04."),
    "104": (("withdrawn",), "pre-deletion duplicate-evidence ref (:794) and action refs (:870); the section now ends at :98."),
    "107": (("other-file",), "retired-names range :101-107 (:895)."),
    "108": (("withdrawn",), "pre-deletion duplicate-block refs (:821,:881,:1128); the section now ends at :98."),
    "109": (("withdrawn",), "pre-deletion blank-separator ref (:825)."),
    "111": (("withdrawn",), "pre-deletion blank-separator ref (:825)."),
    "113": (("withdrawn",), "v5's section-end line (:841); the complement moved to :99-:130."),
    "144": (("withdrawn",), "v7's AGENTS.md line total (:841, re-verified in v5); the deletion moved the live total to 130."),
}



SCRIPT_OR_STYLE = re.compile(r"<(script|style)\b.*?</\1\s*>", re.IGNORECASE | re.DOTALL)
TAG = re.compile(r"<[^>]*>")

def mask(raw: str) -> tuple[str, str]:
    """A line with its tags blanked to equal-length spaces: (plain, text).

    Width-preserving on purpose: the offsets in `prose_numbers` are measured
    against this text, so re-deriving it with a plain `sub(" ", ...)` in a second
    place shifts every offset after the first tag and the classifier starts
    labelling the wrong digit. Two different tag-strippings in one tool is how a
    gate ends up confidently wrong.

    `plain` keeps the tags' slots as spaces and is what structural patterns match
    against — a badge is `<span ...>4</span>`, and the digits inside it survive
    the blanking while the surrounding markup does not. `text` is the readable
    form for context windows. `html.unescape` can change a line's length, so it is
    applied only to the copy used for reading, never to the one holding offsets.
    """
    plain = TAG.sub(lambda m: " " * len(m.group(0)), raw)
    return plain, html.unescape(plain)


def prose_numbers(text: str) -> list[tuple[int, str, str, int]]:
    """(line_number, value, raw_line, offset) per numeric token outside the block.

    The raw line, not the stripped one: whether a digit is a badge or a
    measurement is visible in the markup around it, and stripping the tags first
    would throw away the evidence the classifier needs. The offset is carried
    rather than re-found — a line holding "v4 claimed ... 4 ... 4" has three 4s,
    and `line.find(value)` labels all three with the first one's context. That
    mislabelling is how a gate ends up confidently exempting the wrong digit, so
    the position travels with the value.

    `value` has thousands separators stripped; the token in the document keeps
    them. Callers that need the token's width re-match `NUMBER` at `offset`.
    """
    found: list[tuple[int, str, str, int]] = []
    for lineno, raw in enumerate(masked_lines_keep_tags(text), start=1):
        for match in NUMBER.finditer(mask(raw)[1]):
            found.append((lineno, match.group(0).replace(",", ""), raw, match.start()))
    return found


def block_line_numbers() -> set[str]:
    """The line numbers the block itself emits: span, complement, duplicates.

    A prose "lines 1-54" is a pointer only if it names one of these. Keeping the
    set to line numbers — rather than every digit in the block — stops a
    coincidental match from excusing an unrelated claim, which is how the first
    draft of this script reported full coverage while the live 137 sat unexamined
    four lines from a passing gate.
    """
    if not audit.AGENTS.is_file():
        raise SystemExit(f"audit_prose_numbers: {audit.AGENTS} not found")
    lines = audit.AGENTS.read_text(encoding="utf-8").splitlines()
    lo, hi = audit.section_span(lines)
    rows = audit.classify(lines, lo, hi)
    block = audit.report_block(rows, lo, hi, audit.tally(rows), len(lines))
    refs = " ".join([m.group(0) for m in LINE_REF.finditer(block)] + audit.duplicates(rows))
    return {m.group(0).replace(",", "") for m in NUMBER.finditer(refs)}


def overlaps(text: str, pattern: re.Pattern[str], start: int, end: int) -> bool:
    """True if any match of `pattern` covers part of [start, end).

    Overlap, not "appears in the neighbourhood". A ±32-character window made
    "v4 claimed 4242 lines" exempt the 4242 as a version tag, because the shape
    sat twenty characters away — a gate that covers the wrong number on the same
    line is worse than no gate, because it is believed.
    """
    return any(
        m.start() < end and m.end() > start for m in pattern.finditer(text)
    )


def line_ref_or_none(text: str, match: re.Match[str], block_lines: set[str]) -> str | None:
    """A colon-anchored ref is `line-ref`, or None if it needs a human's class.

    Fail closed on purpose: a stale ref must land in EXEMPT with a reason, not
    fall through to a later shape (`item-noun` would happily relabel
    "finding :61-111"), which would reopen through another class the hole this
    closes. The foreign-file carve-outs are the only way out without validation.
    """
    name = FOREIGN_GLUED.search(text[: match.start()])
    if name and not name.group(0).strip().endswith("AGENTS.md"):
        return "line-ref"
    files = [m.group(0) for m in FILENAME.finditer(text)]
    if not any(f.endswith("AGENTS.md") for f in files):
        others = {f for f in files if not f.endswith("AGENTS.md")}
        if len(others) == 1:
            return "line-ref"
    numbers = [n.replace(",", "") for n in NUMBER.findall(match.group(0))]
    if numbers and all(n in block_lines for n in numbers):
        return "line-ref"
    return None


def mechanical_class(raw: str, value: str, offset: int, block_lines: set[str]) -> str | None:
    """Classify by shape, or None if this number needs a human's judgement."""
    plain, text = mask(raw)
    start = max(0, min(offset, len(text) - len(value)))
    token = NUMBER.match(text, start)
    end = token.end() if token else start + len(value)

    # Every badge on the line, not the first: a findings row carries its number
    # in a span and its prose figures in the same <li>, and `BADGE.search` alone
    # would exempt whichever badge came first and leave the real figure to the
    # table — or the reverse.
    if any(
        m.start("n") == start and m.group("n") == value for m in BADGE.finditer(raw)
    ):
        return "badge"
    if any(
        m.start("n") == start and m.group("n") == value
        for m in HEADING_NUM.finditer(raw)
    ):
        return "section-number"
    for pattern, name in (
        (DATE, "date"),
        (VERSION, "version"),
        (DECISION_ID, "decision-id"),
        (RULE_ID, "rule-id"),
        (ACTION_ID, "action-id"),
        (SLUG, "slug"),
        (LEADING_ID, "leading-id"),
    ):
        if overlaps(text, pattern, start, end):
            return name
    for match in LINE_REF.finditer(text):
        if match.start() < end and match.end() > start:
            return line_ref_or_none(text, match, block_lines)
    if any(
        m.start(1) < end
        and m.end(1) > start
        and " " not in m.group(1).strip()
        and re.search(r"[A-Za-z]", m.group(1))
        for m in CODE_SPAN.finditer(raw)
    ):
        return "code-token"
    word = WORD_LINE_REF.search(text)
    if (
        word
        and word.start() < end
        and word.end() > start
        and all(n.strip() in block_lines for n in NUMBER.findall(word.group(1)))
    ):
        return "line-ref"
    if ITEM_NOUN.search(text[max(0, start - 24) : start]):
        return "item-noun"
    if overlaps(text, RANGE, start, end):
        return "rewrite"
    return None


def emitted_numbers() -> set[str]:
    """The figures a report may state as quantities, re-derived from AGENTS.md.

    Narrow on purpose. Scraping every digit out of the whole block would also
    pick up the line numbers in its duplicate list, and then a prose figure that
    merely coincides with one of them looks covered — the block's `:15` would
    excuse an unrelated claim of "15". That is the same defect this script
    exists to catch, one level in: a gate that believes itself covered because a
    number matched. Line numbers stay covered, but by `line-ref` in the prose,
    where the colon is visible.
    """
    if not audit.AGENTS.is_file():
        raise SystemExit(f"audit_prose_numbers: {audit.AGENTS} not found")
    lines = audit.AGENTS.read_text(encoding="utf-8").splitlines()
    lo, hi = audit.section_span(lines)
    rows = audit.classify(lines, lo, hi)
    counts = audit.tally(rows)
    dups = audit.duplicates(rows)
    figures = list(audit.derived_sums(counts, dups, lo, hi, len(lines)))
    figures += list(audit.COUNT_KEYS)
    figures.append(str(counts["routing"] + len(dups)))
    return {m.group(0).replace(",", "") for line in figures for m in NUMBER.finditer(line)}


def masked_lines_keep_tags(text: str) -> list[str]:
    """The report's lines with the block, <script> and <style> bodies blanked.

    Blanking rather than deleting keeps the line numbers in the report's own
    coordinates, so a finding says "REPORT.html:98" and not "line 3 of the
    residue". Tags are left in place — see `prose_numbers`.
    """
    text = BLOCK_REGION.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = SCRIPT_OR_STYLE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return text.split("\n")


def residue(path: Path) -> tuple[list[dict], list[dict]]:
    """Split the prose into (unclassified, exempt) — both fully accounted for."""
    text = path.read_text(encoding="utf-8")
    audit.extract_block(text)  # raises if the report has no single block
    emitted = emitted_numbers()
    block_lines = block_line_numbers()
    unclassified: dict[tuple[str, int], dict] = {}
    exempt: dict[tuple[str, int], dict] = {}
    for lineno, value, raw, offset in prose_numbers(text):
        if value in emitted:
            continue
        entry = {"line": lineno, "value": value, "context": html.unescape(raw.strip())}
        cls = mechanical_class(raw, value, offset, block_lines)
        if cls is None and value in EXEMPT:
            cls = EXEMPT[value][0][0]
        if cls is None and value in EXEMPT:
            cls = EXEMPT[value][0]
        if cls is None:
            unclassified[(value, lineno)] = entry
        else:
            entry["class"] = cls
            exempt[(value, lineno)] = entry
    return list(unclassified.values()), list(exempt.values())


def report(path: Path, rc: int) -> None:
    if rc:
        print(f"\nFAIL — {path} states figures nothing re-derives:", file=sys.stderr)
    else:
        print(f"OK — {path}: every prose number is emitted, mechanical, or listed.")
    print(
        f"  block-emitted figures come from audit_agents_md.report_block(); the\n"
        f"  {len(EXEMPT)} entries in EXEMPT carry a class and a reason.",
        file=sys.stderr if rc else sys.stdout,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("report", metavar="REPORT", help="a report in docs/reviews/")
    ap.add_argument(
        "--list",
        action="store_true",
        help="print the residue with line context and exit 0 — the diagnostic form",
    )
    ap.add_argument(
        "--by-value",
        action="store_true",
        help="group the residue by value — the form used to write EXEMPT entries",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if the prose states a figure nothing re-derives (gate form)",
    )
    args = ap.parse_args(argv)
    if not (args.list or args.by_value or args.check):
        ap.error("pick one of --list, --by-value or --check")

    path = Path(args.report)
    if not path.is_file():
        print(f"audit_prose_numbers: {path} not found", file=sys.stderr)
        return 1

    unclassified, exempt = residue(path)
    if args.list:
        print(f"{len(exempt)} mechanically/listed, {len(unclassified)} unclassified\n")
        for entry in unclassified:
            print(f"  {path.name}:{entry['line']}  {entry['value']:>6}  {entry['context'][:88]}")
        return 0

    if args.by_value:
        grouped: dict[str, list[dict]] = {}
        for entry in unclassified:
            grouped.setdefault(entry["value"], []).append(entry)
        print(f"{len(grouped)} distinct values need a class\n")
        for value, entries in sorted(grouped.items(), key=lambda kv: -len(kv[1])):
            lines = ",".join(str(e["line"]) for e in entries)
            print(f"  {value:>6} x{len(entries):<3} :{lines}")
            print(f"          {entries[0]['context'][:86]}")
        return 0

    by_class: dict[str, int] = {}
    for entry in exempt:
        by_class[entry["class"]] = by_class.get(entry["class"], 0) + 1

    stale = sorted(
        value for value in EXEMPT if not any(e["value"] == value for e in exempt)
    )
    rc = 1 if (unclassified or stale) else 0
    for entry in unclassified:
        print(
            f"  {path.name}:{entry['line']}  {entry['value']:>6}  {entry['context'][:88]}",
            file=sys.stderr,
        )
    for value in stale:
        print(
            f"  EXEMPT lists {value} ({EXEMPT[value][0]}) but the prose no longer "
            f"states it — delete the entry",
            file=sys.stderr,
        )
    report(path, rc)
    if not rc:
        print("  classes: " + ", ".join(f"{k} {v}" for k, v in sorted(by_class.items())))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
