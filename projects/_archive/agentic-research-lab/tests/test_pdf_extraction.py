"""Regression tests for PDF extraction fidelity (C-6).

The corpus-wide "lost whitespace" defect was never in the source PDFs. pypdf's
default extraction mode discards glyph positioning and emits run-together words
("ofthecausalinferenceengine"); `extraction_mode="layout"` reconstructs the
spacing from the text matrix. Measured on the two INBOX PDFs: 31 glue runs under
the default mode across seven sampled pages, 0 under layout mode.

These tests pin both halves of the fix, because either alone is a regression:
extracting well and then mangling it during normalization.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ingest  # noqa: E402
from check_corpus_health import suspicious_runs  # noqa: E402


GLUED = "ofthe“causalinferenceengine”describedintheIntroduction."


class FakePage:
    """Minimal pypdf page stand-in: one mode returns glue, the other is clean."""

    def __init__(self, layout: str, default: str) -> None:
        self._by_mode = {("extraction_mode", "layout"): layout, ("plain", None): default}

    def extract_text(self, **kwargs):
        if kwargs.get("extraction_mode") == "layout":
            return self._by_mode[("extraction_mode", "layout")]
        return self._by_mode[("plain", None)]


class RaisingPage(FakePage):
    def extract_text(self, **kwargs):
        if kwargs.get("extraction_mode") == "layout":
            raise ValueError("no layout pass in this PDF")
        return self._by_mode[("plain", None)]


class EmptyPage(FakePage):
    def extract_text(self, **kwargs):
        raise ValueError("cannot extract")


class PageExtractionTests(unittest.TestCase):
    def test_prefers_layout_mode_when_default_glues_words(self) -> None:
        page = FakePage(layout="of the causal inference engine", default=GLUED)
        self.assertEqual(ingest._pdf_page_text(page), "of the causal inference engine")

    def test_falls_back_to_default_when_layout_is_worse(self) -> None:
        # A PDF whose layout pass is garbage must still yield its text.
        page = FakePage(layout="a" * 40, default="ordinary readable text")
        self.assertEqual(ingest._pdf_page_text(page), "ordinary readable text")

    def test_survives_a_mode_that_raises(self) -> None:
        page = RaisingPage(layout="", default="recovered text")
        self.assertEqual(ingest._pdf_page_text(page), "recovered text")

    def test_survives_a_page_that_cannot_extract(self) -> None:
        self.assertEqual(ingest._pdf_page_text(EmptyPage(layout="", default="")), "")


class LayoutNormalizationTests(unittest.TestCase):
    def test_dehyphenates_across_line_break(self) -> None:
        self.assertEqual(ingest._normalize_layout("Sys-\ntem/360"), "System/360")

    def test_collapses_layout_padding(self) -> None:
        self.assertEqual(ingest._normalize_layout("a     b\t\tc"), "a b c")

    def test_strips_hanging_indentation(self) -> None:
        self.assertEqual(ingest._normalize_layout("   body text"), "body text")

    def test_removes_soft_hyphen(self) -> None:
        self.assertEqual(ingest._normalize_layout("man\u00admonth"), "manmonth")

    def test_normalization_does_not_mask_glue(self) -> None:
        # Normalizing must not hide the defect the extractor exists to fix: this
        # is a real glue run, and collapsing whitespace cannot repair it.
        glued = "ofthecausalinferenceengine" + "des" * 20
        self.assertEqual(len(suspicious_runs(ingest._normalize_layout(glued))), 1)

    def test_detector_sees_glue_running_into_a_capitalised_word(self) -> None:
        # \b alone cannot end a lowercase run at a capital; 71 such cases exist
        # in the live corpus and were unreported until the lookahead was added.
        glued = "ofthecausalinferenceenginedescribedin" + "the" * 10 + "Introduction"
        self.assertEqual(len(suspicious_runs(glued)), 1)

    def test_end_to_end_page_text_is_clean(self) -> None:
        # The failure this guards: normalize applied after the glue measurement,
        # so the extractor reports clean and stores padding runs.
        page = FakePage(layout="The  Book  ofWhy          27", default=GLUED)
        text = ingest._pdf_page_text(page)
        self.assertEqual(text, "The Book ofWhy 27")
        self.assertEqual(suspicious_runs(text), [])
        self.assertNotIn("  ", text)


class EvictionTests(unittest.TestCase):
    CHUNK = "---\nid: {cid}\ntitle: \"t\"\nsource: \"{source}\"\ntrust_tier: 1\n---\n\nbody\n"

    def test_finds_chunks_by_source_substring(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text(
                self.CHUNK.format(cid="a", source="The Book of Why (2020).pdf"), encoding="utf-8")
            (root / "b.md").write_text(
                self.CHUNK.format(cid="b", source="Unrelated Book.pdf"), encoding="utf-8")
            original = ingest.CORPUS
            ingest.CORPUS = root
            try:
                hits = ingest.find_family_chunks("book of why")
            finally:
                ingest.CORPUS = original
        self.assertEqual([p.stem for p in hits], ["a"])

    def test_dry_run_evicts_nothing(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text(
                self.CHUNK.format(cid="a", source="Mythical Man-month.pdf"), encoding="utf-8")
            original = ingest.CORPUS
            ingest.CORPUS = root
            try:
                removed = ingest.evict_family("mythical", dry=True)
                still_there = (root / "a.md").exists()
            finally:
                ingest.CORPUS = original
        self.assertEqual(removed, ["a"])
        self.assertTrue(still_there, "--dry must not delete corpus files")

    def test_evict_removes_matched_chunks_only(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text(
                self.CHUNK.format(cid="a", source="Mythical Man-month.pdf"), encoding="utf-8")
            (root / "b.md").write_text(
                self.CHUNK.format(cid="b", source="Other.pdf"), encoding="utf-8")
            original = ingest.CORPUS
            ingest.CORPUS = root
            try:
                ingest.evict_family("mythical")
                left = sorted(p.name for p in root.glob("*.md"))
            finally:
                ingest.CORPUS = original
        self.assertEqual(left, ["b.md"])


if __name__ == "__main__":
    unittest.main()
