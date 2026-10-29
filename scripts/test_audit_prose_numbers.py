#!/usr/bin/env python3
"""Hermetic tests for scripts/audit_prose_numbers.py (tmpdir fixture, no repo read).

The real gate reads the live AGENTS.md and the live report; these tests rebind
both onto a tmpdir fixture, for the reason test_audit_agents_md.py does: a test
that read the real files would exercise the baseline instead of the drift
detection, and would keep passing after the classifier had stopped working.
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
import audit_prose_numbers as prose  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
V7 = REPO / "docs" / "reviews" / "architecture-review-20261003-v7.html"

# A miniature AGENTS.md: the same three hazards the real file has (a routing
# anchor followed by bullets, a second skill heading, a following section), so
# the block this fixture produces has counts, a span and a complement.
FIXTURE = """# AGENTS

## Rules

- something else entirely

## Token efficiency (D13, D15)

- **Integrate `skills/token-hygiene/SKILL.md` on every session start.** It enforces:
- Anti-SubRetrv: check context before re-reading
- Scope elision: no blind whole-file reads

Evidence: `TOKEN-EFFICIENCY.md`.

## Token efficiency skill

- Integrate `skills/token-efficiency/SKILL.md` on every session start.

## Where to go

- routing table entries live here
"""


def fixture_block() -> tuple[str, int]:
    lines = FIXTURE.splitlines()
    lo, hi = audit.section_span(lines)
    rows = audit.classify(lines, lo, hi)
    return (
        audit.report_block(rows, lo, hi, audit.tally(rows), len(lines)),
        len(lines),
    )


def report(body: str, block: str) -> str:
    return (
        f"<html><body>\n{body}\n<pre>{audit.BLOCK_BEGIN}\n{block}\n{audit.BLOCK_END}</pre>\n"
        "</body></html>\n"
    )


def unexempted_above(total: int) -> int:
    """A figure the block does not emit and no EXEMPT entry happens to cover."""
    value = total + 1
    while str(value) in prose.EXEMPT:
        value += 1
    return value


def stale_pair_above(total: int) -> tuple[int, int]:
    """Two adjacent figures the fixture block neither emits nor lists.

    EXEMPT is cleared in these tests, so only the block's own figures matter —
    a pair the block cannot produce, for the ref the gate must refuse.
    """
    known = prose.block_line_numbers() | prose.emitted_numbers()
    n = total + 1
    while str(n) in known or str(n + 1) in known:
        n += 1
    return n, n + 1


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.old_agents = audit.AGENTS
        ag = self.tmp / "AGENTS.md"
        ag.write_text(FIXTURE, encoding="utf-8")
        audit.AGENTS = ag
        self.addCleanup(setattr, audit, "AGENTS", self.old_agents)
        # The live table is cleared: these tests are about the classifier, and a
        # fixture report is not the report the 57 live entries describe. Leaving
        # it in place made every one of them fail on "delete the entry" — the
        # stale check working correctly on the wrong document. The live table is
        # exercised on its own, against the real report.
        self.old_exempt = dict(prose.EXEMPT)
        prose.EXEMPT.clear()
        self.addCleanup(lambda: (prose.EXEMPT.clear(), prose.EXEMPT.update(self.old_exempt)))
        self.block, self.total = fixture_block()

    def run_mode(self, body: str, mode: str):
        path = self.tmp / "REVIEW.html"
        path.write_text(report(body, self.block), encoding="utf-8", newline="\n")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = prose.main([mode, str(path)])
        return rc, out.getvalue(), err.getvalue()

    def check(self, body: str):
        return self.run_mode(body, "--check")


class DriftTests(Base):
    """The defect this script exists for: prose that outgrows the block."""

    def test_prose_total_that_contradicts_the_block_fails(self):
        # The v7 defect, reproduced: the block is current, the gate on the block
        # is happy, and the prose states a total nothing emits. Before this
        # script, `--report-check` returned 0 on exactly this document.
        bogus = unexempted_above(self.total)
        rc, _, err = self.check(f"<p>AGENTS.md is {bogus} lines.</p>")
        self.assertEqual(rc, 1)
        self.assertIn(f"states figures nothing re-derives", err)
        self.assertIn(str(bogus), err)

    def test_prose_matching_the_block_passes(self):
        rc, out, err = self.check(f"<p>AGENTS.md is {self.total} lines.</p>")
        self.assertEqual(rc, 0, err)
        self.assertIn("every prose number", out)

    def complement(self) -> str:
        """The block's own emitted complement, read off it rather than retyped."""
        line = next(l for l in self.block.splitlines() if "outside the audited span" in l)
        return line.rsplit("  ", 1)[-1].strip()

    def test_a_complement_the_block_emits_passes(self):
        rc, _, err = self.check(f"<p>Lines {self.complement()} are not audited.</p>")
        self.assertEqual(rc, 0, err)

    def test_a_complement_that_disagrees_with_the_block_fails(self):
        # The G1 scenario in its other dress: the prose states which lines are
        # not audited, and names a figure the block does not emit. A gate that
        # read "lines 1-2" as a mere pointer would wave this through.
        rc, _, err = self.check("<p>Lines 1-2 and 16-17 are not audited.</p>")
        self.assertEqual(rc, 1)
        self.assertIn("states figures nothing re-derives", err)

    def test_the_failure_names_the_line_it_is_on(self):
        body = "<p>padding</p>\n<p>padding</p>\n<p>AGENTS.md is 4242 lines.</p>"
        rc, _, err = self.check(body)
        self.assertEqual(rc, 1)
        self.assertIn(":4", err)


class ShapeTests(Base):
    """A shape is checkable by reading one regex; these are the shapes."""

    def test_badge_is_a_label_not_a_measurement(self):
        rc, _, err = self.check(
            '<li><span class="text-cyan-700 font-bold">14</span>'
            "<div>the finding</div></li>"
        )
        self.assertEqual(rc, 0, err)

    def test_a_figure_next_to_a_badge_on_the_same_line_is_still_checked(self):
        # The first draft used `BADGE.search`, which finds one badge and then
        # exempts whichever number it happened to sit next to. Two numbers on
        # one line is the case that breaks it.
        rc, _, err = self.check(
            '<li><span class="text-cyan-700 font-bold">14</span>'
            "<div>it costs 4242 lines</div></li>"
        )
        self.assertEqual(rc, 1)
        self.assertIn("4242", err)

    def test_line_reference_is_a_pointer(self):
        rc, _, err = self.check("<p>see <code>scripts/build_handoff.py:76-98</code></p>")
        self.assertEqual(rc, 0, err)

    def test_a_bare_ref_the_block_emits_is_a_pointer(self):
        block_lines = sorted(prose.block_line_numbers(), key=int)
        lo, hi = block_lines[0], block_lines[-1]
        rc, _, err = self.check(f"<p>exactly <code>:{lo}-:{hi}</code>.</p>")
        self.assertEqual(rc, 0, err)

    def test_a_stale_bare_ref_is_not_a_pointer(self):
        # The R13 blind spot: `:61-:111` survived a span shift because the
        # colon alone was the whole check. A bare ref nothing emits is residue.
        lo, hi = stale_pair_above(self.total)
        rc, _, err = self.check(f"<p>exactly <code>:{lo}-:{hi}</code>.</p>")
        self.assertEqual(rc, 1)
        self.assertIn(str(lo), err)

    def test_a_bare_ref_inheriting_a_foreign_label_is_a_pointer(self):
        lo, _ = stale_pair_above(self.total)
        rc, _, err = self.check(
            f"<p><code>scripts/other.py:1-2</code> does it at <code>:{lo}</code></p>"
        )
        self.assertEqual(rc, 0, err)

    def test_two_file_labels_are_ambiguous_and_fail_closed(self):
        lo, _ = stale_pair_above(self.total)
        rc, _, err = self.check(
            f"<p><code>scripts/a.py:1-2</code> and <code>scripts/b.py:3-4</code>"
            f" meet at <code>:{lo}</code></p>"
        )
        self.assertEqual(rc, 1)
        self.assertIn(str(lo), err)

    def test_an_agents_md_mention_forces_validation(self):
        # A history quote names the audited file, so it is a claim about it —
        # stale ones fail until a human lists them in EXEMPT as withdrawn.
        lo, hi = stale_pair_above(self.total)
        rc, _, err = self.check(
            f"<p>v4 claimed all of <code>AGENTS.md</code> outside "
            f"<code>:{lo}-{hi}</code>.</p>"
        )
        self.assertEqual(rc, 1)
        self.assertIn(str(lo), err)

    def test_an_agents_md_glued_ref_is_checked_not_carved_out(self):
        lo, hi = stale_pair_above(self.total)
        rc, _, err = self.check(f"<p>see <code>AGENTS.md:{lo}-{hi}</code></p>")
        self.assertEqual(rc, 1)
        self.assertIn(str(lo), err)

    def test_a_total_written_after_the_word_lines_is_not_a_pointer(self):
        # "AGENTS.md is 137 lines" must not read as a `:137` reference. Anchoring
        # the pointer on the colon, not the word, is the whole difference.
        rc, _, err = self.check("<p>AGENTS.md is 4242 lines in total.</p>")
        self.assertEqual(rc, 1)
        self.assertIn("4242", err)

    def test_version_and_date_are_shapes(self):
        rc, _, err = self.check("<p>v7 supersedes v6, dated 2026-10-03.</p>")
        self.assertEqual(rc, 0, err)

    def test_rule_id_and_action_id_are_identifiers(self):
        rc, _, err = self.check("<p>R13 guards it; candidate 4 step 2 does the rest.</p>")
        self.assertEqual(rc, 0, err)

    def test_a_version_does_not_exempt_a_later_figure_on_the_same_line(self):
        # `line.find(value)` labelled every "4" on the line with the context of
        # the first one, so "v4 claimed 4242" exempted the 4242 too.
        rc, _, err = self.check("<p>v4 claimed 4242 lines.</p>")
        self.assertEqual(rc, 1)
        self.assertIn("4242", err)

    def test_a_slug_is_an_identifier(self):
        rc, _, err = self.check("<p>the phase-5 list, per 4-steps-1.</p>")
        self.assertEqual(rc, 0, err)

    def test_style_and_script_bodies_are_not_prose(self):
        body = (
            "<style>.x{color:#1a2b3c;margin:0 4px}</style>"
            '<script src="https://cdn.tailwindcss.com"></script>'
            "<p>and the prose says nothing numeric</p>"
        )
        rc, _, err = self.check(body)
        self.assertEqual(rc, 0, err)

    def test_inside_the_block_is_not_residue(self):
        # The block is checked by --report-check; counting its digits twice would
        # report the gate's own output as the gate's residue.
        unclassified, _ = prose.residue(self.write_and_return("<p>no figures</p>"))
        self.assertEqual(unclassified, [])

    def write_and_return(self, body: str) -> Path:
        path = self.tmp / "REVIEW.html"
        path.write_text(report(body, self.block), encoding="utf-8", newline="\n")
        return path


class EmittedTests(Base):
    """`emitted_numbers` must be the figures, not every digit in the block."""

    def test_a_duplicate_line_number_does_not_excuse_an_unrelated_figure(self):
        emitted = prose.emitted_numbers()
        for row in audit.duplicates(audit.classify(FIXTURE.splitlines(), 5, 9)):
            for token in row.split():
                if token.strip(":").isdigit():
                    self.assertNotIn(
                        token.strip(":"),
                        emitted,
                        "a duplicate's line number leaked into the emitted figures",
                    )

    def test_the_totals_the_block_reports_are_emitted(self):
        emitted = prose.emitted_numbers()
        self.assertIn(str(self.total), emitted)
        self.assertIn(str(audit.tally(audit.classify(FIXTURE.splitlines(), 5, 9))["routing"]), emitted)


class ExemptTests(Base):
    """The table is the human's half, and it is held to both directions."""

    def test_a_listed_figure_is_accepted(self):
        prose.EXEMPT["4242"] = (("other-file",), "a figure about another file, dated.")
        rc, _, err = self.check("<p>the other file has 4242 lines.</p>")
        self.assertEqual(rc, 0, err)

    def test_an_entry_the_prose_no_longer_states_fails(self):
        # A whitelist that only grows is a second copy of the prose, drifting.
        prose.EXEMPT["4242"] = (("other-file",), "dated.")
        rc, _, err = self.check("<p>no figures at all here</p>")
        self.assertEqual(rc, 1)
        self.assertIn("delete the entry", err)

    def test_the_live_table_has_no_stale_entries(self):
        prose.EXEMPT.update(self.old_exempt)
        rc, _, err = self.check("<p>the live table, checked against this body</p>")
        self.assertEqual(rc, 1)
        self.assertIn("delete the entry", err)
        self.assertEqual(len(prose.EXEMPT), len(self.old_exempt))

    def test_every_live_entry_names_a_class_and_a_reason(self):
        for value, (classes, reason) in self.old_exempt.items():
            with self.subTest(value=value):
                self.assertTrue(classes, f"{value} has no class")
                self.assertTrue(reason.strip(), f"{value} has no reason")


class DiagnosticTests(Base):
    def test_list_mode_prints_the_residue_and_exits_zero(self):
        rc, out, _ = self.run_mode("<p>AGENTS.md is 4242 lines.</p>", "--list")
        self.assertEqual(rc, 0)
        self.assertIn("4242", out)
        self.assertIn("unclassified", out)

    def test_by_value_groups_for_writing_entries(self):
        rc, out, _ = self.run_mode("<p>4242 and 4243 lines.</p>", "--by-value")
        self.assertEqual(rc, 0)
        self.assertIn("4242", out)
        self.assertIn("2 distinct values", out)

    def test_no_mode_is_an_error(self):
        with self.assertRaises(SystemExit):
            self.run_mode("<p>x</p>", "--nonsense")

    def test_a_report_without_a_block_is_an_error_not_a_skip(self):
        path = self.tmp / "NOBLOCK.html"
        path.write_text("<p>AGENTS.md is 4242 lines.</p>", encoding="utf-8")
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(io.StringIO()):
                prose.main(["--check", str(path)])


class DriftProofTests(unittest.TestCase):
    """The v7 scenario, run against the real report: growth in AGENTS.md.

    This is the pair of verdicts the workstream exists to change. Before this
    script, growing AGENTS.md moved the block's complement to `:106-:140`, left
    v7's prose saying 137 in four places, and `--report-check` returned 0. So the
    test asserts both halves: the block gate really does stay green (otherwise
    this proves nothing about the prose gate), and the prose gate really does go
    red on the same document.
    """

    def test_regenerating_the_block_does_not_launder_the_prose(self):
        if not V7.is_file() or not audit.AGENTS.is_file():
            self.skipTest("live report or AGENTS.md not available")
        with tempfile.TemporaryDirectory() as tmp:
            grown = Path(tmp) / "AGENTS.md"
            grown.write_text(
                audit.AGENTS.read_text(encoding="utf-8") + "\n- one more rule\n" * 3,
                encoding="utf-8",
            )
            # A copy, because step 2 rewrites the block in place and v7 is not
            # this test's to mutate.
            report_copy = Path(tmp) / "v7.html"
            report_copy.write_text(V7.read_text(encoding="utf-8"), encoding="utf-8")

            old = audit.AGENTS
            audit.AGENTS = grown
            sink = io.StringIO()
            try:
                with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                    stale_rc = audit.main(["--report-check", str(report_copy)])
                    write_rc = audit.main(["--write-block", str(report_copy)])
                    fresh_rc = audit.main(["--report-check", str(report_copy)])
                    prose_rc = prose.main(["--check", str(report_copy)])
                prose_err = sink.getvalue()
            finally:
                audit.AGENTS = old

        self.assertNotEqual(stale_rc, 0, "the block did not move, so nothing is proved")
        self.assertEqual(write_rc, 0, "--write-block should absorb the new figures")
        self.assertEqual(
            fresh_rc, 0, "after regenerating, the block gate must be green again"
        )
        self.assertEqual(
            prose_rc, 1, f"prose survived a regenerated block:\n{prose_err}"
        )
        self.assertIn("137", prose_err)
    """The committed report and the live table must agree, or the gate is a lie."""

    def test_v7_prose_is_fully_classified(self):
        if not V7.is_file():
            self.skipTest("v7 report not available")
        if not prose.audit.AGENTS.is_file():
            self.skipTest("live AGENTS.md not available")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = prose.main(["--check", str(V7)])
        self.assertEqual(rc, 0, f"v7 prose has unclassified figures:\n{err.getvalue()}")

    def test_the_live_table_carries_no_stale_entry(self):
        if not V7.is_file():
            self.skipTest("v7 report not available")
        residue = prose.residue(V7)
        covered = {e["value"] for e in residue[1]}
        stale = [v for v in prose.EXEMPT if v not in covered]
        self.assertEqual(stale, [], f"EXEMPT entries the report no longer needs: {stale}")


if __name__ == "__main__":
    unittest.main()
