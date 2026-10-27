"""Tests for word_count.count_words — whitespace-separated token counting.

The contract: tokens are maximal runs of non-whitespace characters, and
runs of any whitespace (spaces, tabs, newlines) separate them. This pins
the degenerate cases that a naive ``text.split(" ")`` would get wrong:
the empty string, whitespace-only strings, leading/trailing space, and
mixed/extra internal separators.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import word_count  # noqa: E402


class TestCountWords(unittest.TestCase):
    def test_empty_string_is_zero(self) -> None:
        self.assertEqual(word_count.count_words(""), 0)

    def test_whitespace_only_is_zero(self) -> None:
        self.assertEqual(word_count.count_words("   "), 0)
        self.assertEqual(word_count.count_words("\t\n  \n\t"), 0)

    def test_single_word(self) -> None:
        self.assertEqual(word_count.count_words("hello"), 1)

    def test_simple_spaces(self) -> None:
        self.assertEqual(word_count.count_words("the quick brown fox"), 4)

    def test_newlines_and_tabs_separate(self) -> None:
        self.assertEqual(word_count.count_words("one\ntwo\nthree"), 3)
        self.assertEqual(word_count.count_words("a\tb\tc"), 3)

    def test_repeated_internal_separators_count_once(self) -> None:
        self.assertEqual(word_count.count_words("a  b   c\t\t d"), 4)

    def test_leading_and_trailing_whitespace_ignored(self) -> None:
        self.assertEqual(word_count.count_words("  x y  "), 2)


if __name__ == "__main__":
    unittest.main()
