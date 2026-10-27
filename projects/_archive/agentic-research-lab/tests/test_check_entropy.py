"""Tests for check_entropy.py — the unbuildable-chunk gate.

The gate exists to catch chunks whose source is unrecoverable. It is only
useful if the number it reports means what it says, which is why these pin the
cases where it could be made to look better by destroying evidence: a chunk that
was never derived from a file, a source that merely changed format, and a
write-up whose subject was archived.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_entropy as ce  # noqa: E402

CHUNK = """---
id: 00_sample
title: "Sample"
source: "{source}"
tags: [x]
---

Body text.
"""


class ScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.corpus = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write_chunk(self, name: str, source: str) -> None:
        (self.corpus / name).write_text(CHUNK.format(source=source), encoding="utf-8")

    def scan(self):
        return ce.scan(self.corpus)

    def test_a_source_on_disk_counts_as_buildable(self) -> None:
        self.write_chunk("00_a.md", "book.pdf")
        by_source, total = self.scan()
        self.assertEqual(total, 1)
        # scan() consults the real RAW_DIR; assert the classification, not the
        # absolute path, so the test is about the rule rather than the machine.
        self.assertIn("book.pdf", by_source)
        self.assertEqual(by_source["book.pdf"]["chunks"], 1)

    def test_missing_source_is_unbuildable(self) -> None:
        self.write_chunk("00_a.md", "nowhere.pdf")
        by_source, _ = self.scan()
        self.assertEqual(ce.unbuildable(by_source), {"nowhere.pdf": 1})

    def test_chunk_without_source_field_is_reported(self) -> None:
        (self.corpus / "00_a.md").write_text(
            '---\nid: x\ntitle: "y"\n---\n\nBody\n', encoding="utf-8")
        by_source, _ = self.scan()
        self.assertIn("<no source: field>", by_source)


class OriginTests(unittest.TestCase):
    """`is_authored` decides what is a loss and what never was one."""

    def test_topic_label_without_extension_is_authored(self) -> None:
        self.assertTrue(ce.is_authored("agent_workspace_research"))
        self.assertTrue(ce.is_authored("web_research_modular_composition_2026-09-19"))

    def test_archived_write_ups_are_authored(self) -> None:
        for name in ce.SUPERSEDED_SOURCES:
            self.assertTrue(ce.is_authored(name), name)

    def test_a_real_missing_document_is_not_authored(self) -> None:
        # The distinction that matters: a book that is genuinely gone is a loss,
        # and must never be reclassified to make a gate pass.
        self.assertFalse(ce.is_authored("Some Book (Author).pdf"))
        self.assertFalse(ce.is_authored("Another Book.epub"))


class LibraryAliasTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.index = Path(self._tmp.name) / "index.json"
        self.addCleanup(self._tmp.cleanup)
        self._original = ce.LIBRARY_INDEX

    def tearDown(self) -> None:
        ce.LIBRARY_INDEX = self._original

    def test_alias_lets_a_renamed_source_resolve(self) -> None:
        # 345 chunks declared a .txt source that was later supplied as a .pdf.
        # Without alias resolution the file is present but the gate cannot see it.
        self.index.write_text(json.dumps({
            "abc123": {"title": "T", "filename": "Real.pdf",
                       "aliases": ["Original.txt"]},
        }), encoding="utf-8")
        ce.LIBRARY_INDEX = self.index
        names = ce.library_sources()
        self.assertIn("Real.pdf", names)
        self.assertIn("Original.txt", names)

    def test_missing_index_is_not_an_error(self) -> None:
        ce.LIBRARY_INDEX = self.index.with_name("absent.json")
        self.assertEqual(ce.library_sources(), set())

    def test_malformed_index_is_not_an_error(self) -> None:
        self.index.write_text("{ not json", encoding="utf-8")
        ce.LIBRARY_INDEX = self.index
        self.assertEqual(ce.library_sources(), set())


if __name__ == "__main__":
    unittest.main()
