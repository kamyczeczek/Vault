#!/usr/bin/env python3
"""Test to prevent quiet tooling regressions in scripts/did_sessions.bat."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DidSessionsBatTests(unittest.TestCase):
    def test_default_count_is_5(self):
        text = (ROOT / "scripts" / "did_sessions.bat").read_text(encoding="utf-8")
        self.assertRegex(text, r'if "%COUNT%"=="" set COUNT=5')


if __name__ == "__main__":
    unittest.main()
