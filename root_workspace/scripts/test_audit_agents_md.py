#!/usr/bin/env python3
"""Hermetic tests for scripts/audit_agents_md.py (tmpdir fixture, no repo read).

The real script hardcodes `AGENTS` and `EXPECTED` at module scope so a bare run
audits the repo. The tests rebind both onto a tmpdir fixture — the same reason
build_handoff's tests write into a TemporaryDirectory rather than reading
`handoff/flags/`. A test that read the real AGENTS.md would pass for the wrong
reason: it would exercise the live baseline, not the drift detection.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_agents_md as audit  # noqa: E402

# Fixture shape mirrors the real file's three hazards: a routing block whose
# anchor is followed immediately by bullets, a routing block split by a blank,
# and a `## ... skill` heading that is a second block, not the span's end.
FIXTURE = """# AGENTS

## Rules

- something else entirely

## Token efficiency (D13, D15)

- **Integrate `skills/token-hygiene/SKILL.md` on every session start.** It enforces:
- Anti-SubRetrv: check context before re-reading
- Bash output caps

Evidence: `TOKEN-EFFICIENCY.md`. Re-measure after changes: `python3 scripts/pi_cache_forensics.py --since 7d`.

Context is re-paid every turn. Measured: 78.0% cache hit, 69.5M tokens/29 sessions.

## Token efficiency skill

Integrate `skills/token-efficiency/SKILL.md` on every session start. It enforces:

- Anti-SubRetrv: check context before re-reading
- Scope elion: no blind whole-file reads

Evidence: `TOKEN-EFFICIENCY.md`. Re-measure after changes: `python3 scripts/pi_cache_forensics.py --since 7d`.

## Where to go

- routing table entries live here
"""


def counts_for(text: str) -> dict[str, int]:
    lines = text.splitlines()
    lo, hi = audit.section_span(lines)
    return audit.tally(audit.classify(lines, lo, hi))


# FIXTURE's own classification, read off the script's printed output rather than
# counted by hand: R:7 E:3 H:1 .:8 = 19.
BASE = {"routing": 7, "evidence": 3, "heading": 1, "blank": 8, "total": 19}


class SectionSpanTests(unittest.TestCase):
    def test_span_skips_the_skill_heading(self):
        lines = FIXTURE.splitlines()
        lo, hi = audit.section_span(lines)
        # The span must run past `## Token efficiency skill` (:17 here) — that
        # heading introduces the second routing block, it does not end the
        # section. Stopping at the first heading after the start truncated the
        # real audit at :91 and dropped 14 of 51 lines; that bug shipped once.
        self.assertEqual(lines[lo - 1].strip(), "## Token efficiency (D13, D15)")
        self.assertEqual(lines[hi].strip(), "## Where to go")
        self.assertEqual(lines[hi - 1].strip(), "")

    def test_missing_section_raises(self):
        with self.assertRaises(SystemExit):
            audit.section_span(["# AGENTS", "", "no such heading"])


class ClassifyTests(unittest.TestCase):
    def test_counts_derive_from_the_fixture(self):
        # Derived, not hand-counted: the probe of this fixture printed
        # R:7 (:9-:11, :17, :19, :21-:22) E:3 H:1 .:8 -> total 19.
        self.assertEqual(
            counts_for(FIXTURE),
            {"routing": 7, "evidence": 3, "heading": 1, "blank": 8, "total": 19},
        )

    def test_blank_does_not_end_a_routing_block(self):
        # Block 2 puts its anchor and bullets on opposite sides of a blank
        # (:19 anchor, :20 blank, :21-:22 bullets). Terminating on the blank
        # reclassified 7 of 17 real routing lines as evidence.
        self.assertEqual(counts_for(FIXTURE)["routing"], 7)

    def test_heading_outside_the_section_is_not_audited(self):
        lines = FIXTURE.splitlines()
        lo, hi = audit.section_span(lines)
        rows = audit.classify(lines, lo, hi)
        self.assertNotIn("routing table entries live here", [t for _, _, t in rows])
        self.assertEqual(len(rows), 19)


class DuplicateTests(unittest.TestCase):
    def test_exact_repeat_is_reported_once_from_the_later_line(self):
        lines = FIXTURE.splitlines()
        lo, hi = audit.section_span(lines)
        found = audit.duplicates(audit.classify(lines, lo, hi))
        self.assertEqual(len(found), 1)
        self.assertIn("is an exact repeat of", found[0])

    def test_bullet_marker_is_stripped_before_comparing(self):
        # An evidence bullet "- Re-measure ..." inside an evidence run is a
        # substring of "Evidence: ... Re-measure ...". A raw string compare
        # misses it; a compare that keeps the bullet marker reports a false
        # "no duplicates". Both directions were wrong in the first draft.
        text = FIXTURE.replace(
            "## Where to go",
            "- Re-measure after changes: `python3 scripts/pi_cache_forensics.py --since 7d`.\n"
            "\n## Where to go",
        )
        lines = text.splitlines()
        lo, hi = audit.section_span(lines)
        found = audit.duplicates(audit.classify(lines, lo, hi))
        self.assertEqual(len(found), 2)
        self.assertTrue(any("is a substring repeat of" in f for f in found))


class CheckTests(unittest.TestCase):
    """`--check` must fail for the right reason, not merely be capable of failing."""

    BASE = BASE

    def run_check(self, text: str, expected: dict[str, int]):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "AGENTS.md"
            path.write_text(text, encoding="utf-8")
            old_agents, old_expected = audit.AGENTS, audit.EXPECTED
            audit.AGENTS, audit.EXPECTED = path, expected
            try:
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    rc = audit.main(["--check"])
                return rc, out.getvalue(), err.getvalue()
            finally:
                audit.AGENTS, audit.EXPECTED = old_agents, old_expected

    def test_matching_baseline_passes(self):
        rc, out, _ = self.run_check(FIXTURE, self.BASE)
        self.assertEqual(rc, 0, out)

    def test_wrong_baseline_fails_even_when_the_file_is_fine(self):
        baseline = dict(self.BASE, heading=0)
        rc, _, err = self.run_check(FIXTURE, baseline)
        self.assertEqual(rc, 1)
        self.assertIn("heading: expected 0, got 1", err)

    def test_one_added_routing_line_fails(self):
        text = FIXTURE.replace("- Bash output caps", "- Bash output caps\n- New rule")
        rc, _, err = self.run_check(text, self.BASE)
        self.assertEqual(rc, 1)
        self.assertIn("routing: expected 7, got 8", err)
        self.assertIn("total: expected 19, got 20", err)

    def test_one_removed_bullet_fails(self):
        text = FIXTURE.replace("- Scope elion: no blind whole-file reads\n", "")
        rc, _, err = self.run_check(text, self.BASE)
        self.assertEqual(rc, 1)
        self.assertIn("routing: expected 7, got 6", err)

    def test_drift_message_names_the_baseline_edit_as_deliberate(self):
        rc, _, err = self.run_check(FIXTURE, dict(self.BASE, routing=99))
        self.assertEqual(rc, 1)
        self.assertIn("routing: expected 99, got 7", err)
        self.assertIn("deliberately", err)


class LiveRepoTests(unittest.TestCase):
    """The recorded baseline must describe the real file, not a fixture."""

    def test_live_agents_md_matches_recorded_baseline(self):
        rc, out, _ = self.run_live()
        self.assertEqual(rc, 0, f"baseline drift against the real AGENTS.md:\n{out}")

    def run_live(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = audit.main(["--check"])
        return rc, out.getvalue(), err.getvalue()


REPORT_TEMPLATE = """<html><body><h1>Audit</h1>
<p>The token-efficiency section is routing 7 / evidence 3.</p>
<pre>{BEGIN}
PLACEHOLDER
{END}</pre>
</body></html>
"""


class NormalizeTests(unittest.TestCase):
    """`normalize_block` ignores transport, ignores nothing else."""

    def test_crlf_and_trailing_space_are_transport(self):
        self.assertEqual(
            audit.normalize_block("  routing  \r\n  evidence 24  \r\n"),
            "  routing\n  evidence 24",
        )

    def test_surrounding_blank_lines_are_transport(self):
        self.assertEqual(audit.normalize_block("\n\n  routing      7\n\n\n"), "  routing      7")

    def test_a_different_number_is_not_transport(self):
        self.assertNotEqual(
            audit.normalize_block("  routing      7"),
            audit.normalize_block("  routing      8"),
        )


class ReportBlockTests(unittest.TestCase):
    """The report's numbers must be generated, not retyped."""

    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.old_agents, self.old_expected = audit.AGENTS, audit.EXPECTED
        ag = self.tmp / "AGENTS.md"
        ag.write_text(FIXTURE, encoding="utf-8")
        audit.AGENTS, audit.EXPECTED = ag, dict(BASE)
        self.addCleanup(setattr, audit, "AGENTS", self.old_agents)
        self.addCleanup(setattr, audit, "EXPECTED", self.old_expected)

    def block(self) -> str:
        lines = FIXTURE.splitlines()
        lo, hi = audit.section_span(lines)
        rows = audit.classify(lines, lo, hi)
        return audit.report_block(rows, lo, hi, audit.tally(rows), len(lines))

    def write_report(self, body: str) -> Path:
        # bytes, not text: write_text would translate the "\n" this fixture is
        # built from, which is exactly the transport the test must not inject
        # twice.
        path = self.tmp / "REVIEW.html"
        path.write_bytes(
            body.replace("{BEGIN}", audit.BLOCK_BEGIN)
            .replace("{END}", audit.BLOCK_END)
            .encode("utf-8")
        )
        return path

    def run_mode(self, path: Path, mode: str):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = audit.main([mode, str(path)])
        return rc, out.getvalue(), err.getvalue()

    def test_bare_run_prints_the_block_it_expects_a_report_to_carry(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = audit.main(["--check"])
        self.assertEqual(rc, 0)
        self.assertIn(self.block(), out.getvalue())

    def test_derived_sums_are_derived_not_hand_written(self):
        # Fixture: routing 7, evidence 3, heading 1, blank 8, one duplicate found.
        # Compared on words, not on hand-typed padding: re-typing a column width
        # in a test is the same hand-count this workstream exists to remove.
        sums = audit.derived_sums(BASE, ["  :24 is an exact repeat of :13"], 7, 25, 33)
        retireable = next(line for line in sums if line.strip().startswith("retireable"))
        self.assertIn("(routing 7 + 1 duplicate evidence)", retireable)
        self.assertTrue(retireable.endswith(" 8"), retireable)
        coverage = next(line for line in sums if line.strip().startswith("coverage sum"))
        self.assertTrue(coverage.endswith("7 + 3 + 1 + 8 = 19"), coverage)
        # The span's complement is a claim about the file too: "lines 1-54 and
        # 106-137 are not audited" moves whenever the file does.
        self.assertIn(":1-:6, :26-:33", next(l for l in sums if "outside" in l))
        self.assertIn("33", next(l for l in sums if "lines in total" in l))

    def test_span_complement_is_empty_when_the_section_is_the_whole_file(self):
        sums = audit.derived_sums(BASE, [], 1, 19, 19)
        self.assertIn("none", next(l for l in sums if "outside" in l))

    def test_a_total_a_report_quotes_is_inside_the_block(self):
        # The v7 defect: the block was gated, "19 lines a router could retire"
        # was prose, and prose survives a drift. Any total the report states has
        # to be emitted by the run that emits the categories.
        block = self.block()
        self.assertIn("retireable", block)
        self.assertIn(str(BASE["routing"] + 1), block)
        self.assertIn(f"= {BASE['total']}", block)

    def test_report_check_passes_when_the_block_is_current(self):
        path = self.write_report(REPORT_TEMPLATE.replace("PLACEHOLDER", self.block()))
        rc, out, err = self.run_mode(path, "--report-check")
        self.assertEqual(rc, 0, err)
        self.assertIn("quotes exactly what this script emits", out)

    def test_report_check_fails_on_a_miscount(self):
        # "18" is the exact defect from the review: three times in prose, no
        # arithmetic path to it. Here one digit, caught by the artifact.
        wrong = f"  {'routing':<9} {18:>3}"
        path = self.write_report(REPORT_TEMPLATE.replace("PLACEHOLDER", self.block()))
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                f"  {'routing':<9} {7:>3}", wrong
            ),
            encoding="utf-8",
        )
        rc, _, err = self.run_mode(path, "--report-check")
        self.assertEqual(rc, 1)
        # `fromfile` is the report and `tofile` is the script, so the report's
        # miscount is the `-` line and the script's true figure the `+` line.
        # These labels were swapped until `block_diff` was fixed; a test that
        # pins the wrong side is what let the swap survive.
        self.assertIn(f"-{wrong}", err)
        self.assertIn(f"+  {'routing':<9} {7:>3}", err)

    def test_report_check_fails_on_a_wrong_span(self):
        # The span header is part of the claim: "(19 lines)" is the count the
        # review quotes in prose, and it moves whenever AGENTS.md does.
        path = self.write_report(REPORT_TEMPLATE.replace("PLACEHOLDER", self.block()))
        path.write_text(
            path.read_text(encoding="utf-8").replace("(19 lines)", "(18 lines)"),
            encoding="utf-8",
        )
        rc, _, err = self.run_mode(path, "--report-check")
        self.assertEqual(rc, 1)
        self.assertIn("(18 lines)", err)
        self.assertIn("--write-block", err)

    def test_report_check_tolerates_transport_differences(self):
        # Trailing spaces and a stray blank line are transport, not claims: a
        # report authored in an editor must not fail a check about numbers.
        # CRLF is covered by NormalizeTests — read_text() universal-newlines it
        # away before the comparison ever sees it.
        spaced = "\n".join(line + "   " for line in self.block().split("\n"))
        path = self.write_report(REPORT_TEMPLATE.replace("PLACEHOLDER", spaced + "\n\n\n"))
        rc, _, err = self.run_mode(path, "--report-check")
        self.assertEqual(rc, 0, err)

    def test_missing_markers_are_an_error_not_a_skip(self):
        path = self.write_report("<html><p>routing 7, evidence 3</p></html>")
        with self.assertRaises(SystemExit) as ctx:
            self.run_mode(path, "--report-check")
        self.assertIn("exactly one", str(ctx.exception))

    def test_two_blocks_are_an_error(self):
        body = REPORT_TEMPLATE.replace("PLACEHOLDER", self.block())
        body = body + REPORT_TEMPLATE.replace("{BEGIN}", audit.BLOCK_BEGIN).replace(
            "{END}", audit.BLOCK_END
        ).replace("PLACEHOLDER", self.block())
        path = self.write_report(body)
        with self.assertRaises(SystemExit):
            self.run_mode(path, "--report-check")

    def test_baseline_drift_fails_the_report_check_too(self):
        path = self.write_report(REPORT_TEMPLATE.replace("PLACEHOLDER", self.block()))
        audit.EXPECTED = dict(BASE, routing=99)
        rc, _, err = self.run_mode(path, "--report-check")
        self.assertEqual(rc, 1)
        self.assertIn("routing: expected 99, got 7", err)

    def test_write_block_then_check(self):
        stale = self.block().replace("(19 lines)", "(18 lines)")
        path = self.write_report(REPORT_TEMPLATE.replace("PLACEHOLDER", stale))
        rc, _, err = self.run_mode(path, "--report-check")
        self.assertEqual(rc, 1)
        rc, _, err = self.run_mode(path, "--write-block")
        self.assertEqual(rc, 0, err)
        rc, out, err = self.run_mode(path, "--report-check")
        self.assertEqual(rc, 0, err)
        self.assertIn("(19 lines)", path.read_text(encoding="utf-8"))
        self.assertNotIn("(18 lines)", path.read_text(encoding="utf-8"))

    def test_write_block_leaves_the_rest_of_the_report_alone(self):
        path = self.write_report(REPORT_TEMPLATE.replace("PLACEHOLDER", "stale"))
        before = path.read_text(encoding="utf-8").splitlines()
        self.run_mode(path, "--write-block")
        after = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(before[:2], after[:2])
        self.assertEqual(before[-2:], after[-2:])
        joined = "\n".join(after)
        self.assertEqual(joined.count(audit.BLOCK_BEGIN), 1)
        self.assertEqual(joined.count(audit.BLOCK_END), 1)


if __name__ == "__main__":
    unittest.main()