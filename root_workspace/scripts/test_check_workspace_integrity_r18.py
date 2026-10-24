#!/usr/bin/env python3
"""Hermetic tests for _r18_pending_decisions (S84a → S85)."""
from __future__ import annotations
import datetime
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_workspace_integrity import _r18_pending_decisions  # noqa: E402

TODAY = datetime.date(2026, 10, 18)

# Adversarial cases written BEFORE the run (S56/S62):
# M1 control, below threshold -> 0 FAIL 0 WARN
# M2 shift, above FAIL threshold -> 1 entry, age 17d
# M3 false positive: WYKONANE + closing prose mentioning the word -> []
# M4 mixed: only the real pending is returned, D-04 is not flagged


def _entry(fid: str, status: str, zapisano: str = "2026-10-01") -> str:
    return (f"- id: {fid}\n  temat: x\n  zapisano: {zapisano}\n"
            f"  wykonawca: x\n  status: {status}")


CLOSING = ("\n\n`session-decision` — closing prose mentioning "
           "PENDING_IMPLEMENTATION here.\n")


class R18PendingTests(unittest.TestCase):
    def test_m1_control_pending_below_threshold(self):
        text = _entry("D-2026-10-18-01", "PENDING_IMPLEMENTATION",
                      "2026-10-18") + "\n"
        got = _r18_pending_decisions(text, TODAY)
        self.assertEqual(len(got), 1)
        fid, age, _entry_text, reason, raw = got[0]
        self.assertEqual(fid, "D-2026-10-18-01")
        self.assertEqual(age, 0)
        self.assertIsNone(reason)
        self.assertEqual(raw, "2026-10-18")

    def test_m2_shift_pending_above_threshold(self):
        text = _entry("D-2026-10-01-01", "PENDING_IMPLEMENTATION",
                      "2026-10-01") + "\n"
        got = _r18_pending_decisions(text, TODAY)
        self.assertEqual(len(got), 1)
        fid, age, _entry_text, reason, raw = got[0]
        self.assertEqual(fid, "D-2026-10-01-01")
        self.assertEqual(age, 17)  # 17d > 14 -> FAIL path in check_r18
        self.assertIsNone(reason)
        self.assertEqual(raw, "2026-10-01")

    def test_m3_false_positive_wykonane_with_closing_prose(self):
        text = _entry("D-2026-10-11-04", "WYKONANE", "2026-10-11") + CLOSING
        self.assertEqual(_r18_pending_decisions(text, TODAY), [])

    def test_m4_mixed_one_pending_one_done(self):
        text = (_entry("D-2026-10-08-01", "PENDING_IMPLEMENTATION",
                       "2026-10-08")
                + "\n\n"
                + _entry("D-2026-10-11-04", "WYKONANE", "2026-10-11")
                + CLOSING)
        got = _r18_pending_decisions(text, TODAY)
        self.assertEqual([t[0] for t in got], ["D-2026-10-08-01"])
        self.assertEqual(got[0][1], 10)  # 10d > 3 -> WARN path, not FAIL
        self.assertEqual(got[0][3], None)

    def test_m5_no_date_reason(self):
        text = "- id: D-99\n  status: PENDING_IMPLEMENTATION\n\n"
        got = _r18_pending_decisions(text, TODAY)
        self.assertEqual(got[0][3], "no_date")
        self.assertIsNone(got[0][4])

    def test_m5b_bad_date_reason(self):
        text = ("- id: D-98\n  zapisano: 2026-13-99\n"
                "  status: PENDING_IMPLEMENTATION\n\n")
        got = _r18_pending_decisions(text, TODAY)
        self.assertEqual(got[0][3], "bad_date")
        self.assertEqual(got[0][4], "2026-13-99")


if __name__ == "__main__":
    unittest.main()
