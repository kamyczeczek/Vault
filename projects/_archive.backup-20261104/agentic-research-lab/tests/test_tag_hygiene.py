"""Regression tests for corpus tag hygiene (C-3).

Tag pollution was invisible to every existing quality gate: the graph looked
richly connected while 99% of its edges were whole-book cliques built from OCR
debris, and the FTS index answered questions from curation labels rather than
from text the chunks actually contained.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "knowledge" / "graph"))

import build_graph  # noqa: E402

class KeepTagTests(unittest.TestCase):
    """`_keep_tag` only rejects by shape. Book-scoped debris like "Msqrt" is
    shaped like a word and is removed by `_drop_book_wide_tags` instead."""

    def test_rejects_junk_by_shape(self) -> None:
        for junk in ("x83db59", "o377", "bll001", "HGBN85421", "1", "42",
                     "b", "l", "o", "c", "P-", "2A"):
            self.assertFalse(build_graph._keep_tag(junk), f"{junk!r} should be rejected")

    def test_book_scoped_debris_survives_shape_filter(self) -> None:
        # Documents the split: letter-only debris ("Msqrt", "bllllllll",
        # "SeismicEvents") is shaped like a word, so only the second layer —
        # single-source confinement — removes it. Both layers are required.
        for tag in ("Msqrt", "bllllllll", "SeismicEvents", "LoginID"):
            self.assertTrue(build_graph._keep_tag(tag), f"{tag!r} passes the shape filter")

    def test_endif_is_removed_by_the_book_wide_layer(self) -> None:
        # A C preprocessor keyword: shaped like a word, confined to one book.
        self.assertTrue(build_graph._keep_tag("endif"))
        nodes = [{"id": "c0", "source": "book_a.pdf", "tags": ["endif", "memory"]}]
        build_graph._drop_book_wide_tags(nodes)
        self.assertEqual(nodes[0]["tags"], ["memory"])

    def test_keeps_real_topic_vocabulary(self) -> None:
        for tag in ("memory", "agents", "context-engineering", "anti-leakage",
                    "multi-agent", "knowledge-graph", "icm", "retrieval"):
            self.assertTrue(build_graph._keep_tag(tag), f"{tag!r} should be kept")

    def test_rejects_malformed_shapes(self) -> None:
        for junk in ("", "-leading", "trailing-", "has_underscore", "has space", "Ünicode"):
            self.assertFalse(build_graph._keep_tag(junk), f"{junk!r} should be rejected")


class BookWideTagTests(unittest.TestCase):
    @staticmethod
    def _nodes(spec):
        return [{"id": f"c{i}", "source": src, "tags": list(tags)}
                for i, (src, tags) in enumerate(spec)]

    def test_drops_tag_confined_to_one_source(self) -> None:
        # Every chunk of one book carried that book's margin debris.
        nodes = self._nodes([
            ("book_a.pdf", ("Msqrt", "memory")),
            ("book_a.pdf", ("Msqrt", "memory")),
            ("book_b.pdf", ("memory",)),
        ])
        stats = build_graph._drop_book_wide_tags(nodes)
        self.assertIn("Msqrt", stats["dropped_tag_types_sample"])
        self.assertEqual({t for n in nodes for t in n["tags"]}, {"memory"})

    def test_keeps_tag_spanning_multiple_sources(self) -> None:
        nodes = self._nodes([
            ("book_a.pdf", ("memory",)), ("book_b.pdf", ("memory",)),
            ("book_c.pdf", ("memory",)),
        ])
        build_graph._drop_book_wide_tags(nodes)
        self.assertEqual({t for n in nodes for t in n["tags"]}, {"memory"})

    def test_registered_topic_survives_single_source(self) -> None:
        # `multi-agent` lives in one book but is controlled vocabulary; the first
        # cut of this filter dropped it and silently unregistered 8 topics.
        registered = build_graph._registered_topics()
        if "multi-agent" not in registered:
            self.skipTest("topics.md no longer registers multi-agent")
        nodes = self._nodes([("book_a.pdf", ("multi-agent", "Msqrt"))])
        build_graph._drop_book_wide_tags(nodes)
        self.assertIn("multi-agent", nodes[0]["tags"])
        self.assertNotIn("Msqrt", nodes[0]["tags"])

    def test_parse_chunk_applies_the_shape_filter(self) -> None:
        # Integration pin: the shape filter must be wired into the real parse
        # path, not merely correct in isolation. Deleting the call from
        # `parse_chunk` leaves every unit test green and lets debris back in.
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp, patch.object(build_graph, "ROOT", Path(tmp)):
            chunk = Path(tmp) / "sample_chunk.md"
            chunk.write_text(
                "---\n"
                "id: sample_chunk\n"
                'title: "Sample"\n'
                'source: "book_a.pdf"\n'
                "tags: [memory, x83db59, 1, b, Msqrt]\n"
                "trust_tier: 1\n"
                "---\n"
                "# Section\n\nProse body.\n",
                encoding="utf-8",
            )
            parsed = build_graph.parse_chunk(chunk)
        # Shape rejects x83db59 (alphanumeric debris), 1 and b (too short).
        self.assertNotIn("x83db59", parsed["tags"])
        self.assertNotIn("1", parsed["tags"])
        self.assertNotIn("b", parsed["tags"])
        # Msqrt is word-shaped: the book-wide layer, not this one, removes it.
        self.assertIn("Msqrt", parsed["tags"])
        self.assertIn("memory", parsed["tags"])

    def test_registered_topics_parses_only_unreserved_section(self) -> None:
        registered = build_graph._registered_topics()
        self.assertIn("memory", registered)
        # Planned topics are reserved for future coverage, not yet routable.
        self.assertNotIn("interpretable-context", registered)


class FtsSchemaTests(unittest.TestCase):
    def test_fts_table_has_no_tags_column(self) -> None:
        # The tags column let curation labels answer content queries.
        self.assertNotIn("tags", build_graph.FTS_COLUMNS)
        self.assertEqual(build_graph.FTS_COLUMNS, ("id", "title", "body", "source_family"))


if __name__ == "__main__":
    unittest.main()
