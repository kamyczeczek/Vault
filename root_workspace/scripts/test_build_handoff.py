#!/usr/bin/env python3
"""Hermetic tests for scripts/build_handoff.py (tmpdir, no real DB, no repo)."""
from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_handoff as bh  # noqa: E402

FLAG_A = """---
flag: alpha_done
since: 2026-10-03
owner: agent-a
agent: agent-a
model: opencode/some-model
---

`alpha_done` — 2026-10-03: shipped the thing. Next: nothing.
"""

FLAG_B = """---
flag: beta_open
since: 2026-10-01
owner: agent-b
agent: agent-b
model: other/model
---

`beta_open` — 2026-10-01: waiting on a human call. Next: decide.
"""

DEEP_NOTE = "# Gotchas\n\n- one scar worth 60 seconds\n"


class BuildHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(__import__("tempfile").TemporaryDirectory()))
        self.flags = self.tmp / "handoff" / "flags"
        self.deep = self.tmp / "handoff" / "deep"
        self.flags.mkdir(parents=True)
        self.deep.mkdir(parents=True)
        (self.flags / "alpha_done.md").write_text(FLAG_A, encoding="utf-8")
        (self.flags / "beta_open.md").write_text(FLAG_B, encoding="utf-8")
        (self.deep / "gotchas.md").write_text(DEEP_NOTE, encoding="utf-8")

    def collect(self):
        return bh.collect(self.flags, self.deep)

    def test_parse_reads_frontmatter_and_body(self):
        f = bh.parse_flag(self.flags / "alpha_done.md")
        self.assertEqual(f["flag"], "alpha_done")
        self.assertEqual(f["since"], "2026-10-03")
        self.assertEqual(f["owner"], "agent-a")
        self.assertNotIn("---", f["body"])

    def test_summary_strips_flag_prefix(self):
        f = bh.parse_flag(self.flags / "alpha_done.md")
        self.assertEqual(f["summary"], "shipped the thing. Next: nothing.")

    def test_summary_is_clipped_at_word_boundary(self):
        long = "x" * 10 + " " + "word " * 200
        s = bh.summarize(long)
        self.assertLessEqual(len(s), bh.SUMMARY_CHARS + 1)
        self.assertTrue(s.endswith("…"))
        self.assertNotIn("  ", s)

    def test_summary_handles_empty_body(self):
        self.assertEqual(bh.summarize(""), "(empty)")

    def test_flags_sorted_newest_first(self):
        flags, problems, _ = self.collect()
        self.assertEqual([f["flag"] for f in flags], ["alpha_done", "beta_open"])
        self.assertEqual(problems, [])

    def test_filename_flag_mismatch_is_reported_not_crashed(self):
        (self.flags / "gamma.md").write_text(
            "---\nflag: other_name\nsince: 2026-10-03\n---\n\nbody\n", encoding="utf-8")
        flags, problems, _ = self.collect()
        self.assertTrue(any("!= filename" in p for p in problems))

    def test_missing_since_is_reported(self):
        (self.flags / "delta.md").write_text("---\nflag: delta\n---\n\nbody\n", encoding="utf-8")
        _, problems, _ = self.collect()
        self.assertTrue(any("missing `since`" in p for p in problems))

    def test_render_contains_every_flag_and_the_deep_note(self):
        flags, problems, deep = self.collect()
        text = bh.render(flags, deep, problems)
        for f in ("alpha_done", "beta_open"):
            self.assertIn(f, text)
        self.assertIn("## Gotchas", text)
        self.assertIn("GENEROWANE", text)

    def test_render_carries_provenance_comment_per_flag(self):
        flags, problems, deep = self.collect()
        text = bh.render(flags, deep, problems)
        self.assertIn("owner: agent-a", text)
        self.assertIn("model: opencode/some-model", text)

    def test_render_lists_problems_in_the_view(self):
        (self.flags / "gamma.md").write_text(
            "---\nflag: other_name\nsince: 2026-10-03\n---\n\nbody\n", encoding="utf-8")
        flags, problems, deep = self.collect()
        self.assertIn("Problemy", bh.render(flags, deep, problems))

    def test_render_is_idempotent(self):
        flags, problems, deep = self.collect()
        self.assertEqual(bh.render(flags, deep, problems), bh.render(flags, deep, problems))

    def test_is_stale_detects_missing_and_changed(self):
        out = self.tmp / "HANDOFF.md"
        text = "x\n"
        self.assertTrue(bh.is_stale(out, text))
        out.write_text(text, encoding="utf-8")
        self.assertFalse(bh.is_stale(out, text))
        out.write_text("y\n", encoding="utf-8")
        self.assertTrue(bh.is_stale(out, text))

    def test_missing_dirs_yield_empty_view_not_crash(self):
        empty = self.tmp / "nope"
        flags, problems, deep = bh.collect(empty / "flags", empty / "deep")
        self.assertEqual((flags, problems, deep), ([], [], []))

    # --- S81: the inline window must be deterministic, not wall-clock -------
    def test_split_flags_defaults_to_newest_since_not_today(self):
        # Midline bug (S81): anchoring on date.today() let a close that crossed
        # midnight build the view at 10-17 in the hook and rebuild it at 10-18
        # in `integrity`, so --check saw a spurious STALE. Anchor on content.
        flags, _, _ = self.collect()  # newest since = 2026-10-03
        self.assertEqual(bh.newest_since(flags), date(2026, 10, 3))
        fresh, archived = bh.split_flags(flags)
        self.assertEqual([f["flag"] for f in fresh], ["alpha_done", "beta_open"])
        self.assertEqual(archived, [])

    def test_split_flags_same_as_of_is_identical(self):
        flags, _, _ = self.collect()
        self.assertEqual(bh.split_flags(flags, "2026-10-05"),
                         bh.split_flags(flags, "2026-10-05"))

    def test_split_flags_window_moves_only_boundary_flags(self):
        # M1 (S56/S62): changing as_of relocates exactly the flags whose `since`
        # sits between the two cutoffs (10-14 vs 10-15), nothing else.
        flags = [{"flag": "old", "since": "2026-10-01"},
                 {"flag": "edge", "since": "2026-10-14"},
                 {"flag": "new", "since": "2026-10-18"}]
        f17, a17 = bh.split_flags(flags, "2026-10-17")  # cutoff 2026-10-14
        f18, a18 = bh.split_flags(flags, "2026-10-18")  # cutoff 2026-10-15
        self.assertEqual([f["flag"] for f in f17], ["edge", "new"])
        self.assertEqual([f["flag"] for f in a17], ["old"])
        self.assertEqual([f["flag"] for f in f18], ["new"])
        self.assertEqual([f["flag"] for f in a18], ["old", "edge"])

    def test_split_flags_keeps_missing_since_fresh(self):
        flags = [{"flag": "nosince"}, {"flag": "old", "since": "2020-01-01"}]
        fresh, archived = bh.split_flags(flags, "2026-10-18")
        self.assertEqual([f["flag"] for f in fresh], ["nosince"])
        self.assertEqual([f["flag"] for f in archived], ["old"])


if __name__ == "__main__":
    unittest.main(verbosity=2)