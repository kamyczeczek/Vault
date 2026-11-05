import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
GRAPH_DIR = ROOT / "knowledge" / "graph"
if str(GRAPH_DIR) not in sys.path:
    sys.path.insert(0, str(GRAPH_DIR))

import ask  # noqa: E402
import mcp_server  # noqa: E402


class GraphRetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db = Path(self.tempdir.name) / "graph.db"
        conn = sqlite3.connect(self.db)
        conn.executescript(
            """
            CREATE TABLE nodes(
                id TEXT PRIMARY KEY, title TEXT, path TEXT, tags TEXT,
                headings TEXT, body TEXT, node_type TEXT, source_family TEXT,
                source TEXT, trust_tier INTEGER, semantic_edges TEXT
            );
            CREATE TABLE edges(src TEXT, dst TEXT, kind TEXT, conf REAL, tag TEXT);
            CREATE TABLE node_tags(
                node_id TEXT NOT NULL, tag TEXT NOT NULL,
                PRIMARY KEY(node_id, tag)
            );
            CREATE INDEX node_tags_tag_node ON node_tags(tag, node_id);
            CREATE VIRTUAL TABLE fts USING fts5(id, title, body, source_family);
            """
        )
        nodes = [
            (
                "n1", "Session Memory", "knowledge/corpus/n1.md", '["memory", "graph"]',
                '["Overview", "Retrieval"]',
                "# Overview\n\nSession memory is stored as an append-only graph event.\n\n"
                "# Retrieval\n\nUse bounded evidence spans to reduce token usage.",
                "corpus", "session_memory", "", 1, "{}",
            ),
            (
                "n2", "Unrelated", "knowledge/corpus/n2.md", '["other"]', '[]',
                "An unrelated paragraph.", "corpus", "other", "", 1, "{}",
            ),
        ]
        conn.executemany("INSERT INTO nodes VALUES(?,?,?,?,?,?,?,?,?,?,?)", nodes)
        conn.executemany("INSERT INTO fts VALUES(?,?,?,?)", [(n[0], n[1], n[5], n[7]) for n in nodes])
        conn.executemany("INSERT INTO node_tags VALUES(?, ?)", [("n1", "memory"), ("n1", "graph"), ("n2", "other"), ("n2", "nonexistentword")])
        conn.commit()
        conn.close()
        self.db_patch = patch.object(ask, "DB", self.db)
        self.db_patch.start()

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.tempdir.cleanup()

    def test_tag_query_uses_normalized_tags(self) -> None:
        rows = ask.query("", limit=5, tags=["memory"])
        self.assertEqual([row["id"] for row in rows], ["n1"])

    def test_evidence_spans_are_bounded_and_section_aware(self) -> None:
        spans = ask.evidence_spans("n1", "session retrieval", limit=2, max_chars=80)
        self.assertEqual(len(spans), 2)
        self.assertTrue(all(len(span["text"]) <= 80 for span in spans))
        self.assertTrue(any(span["section"] == "Retrieval" for span in spans))

    def test_missing_node_returns_no_spans(self) -> None:
        self.assertEqual(ask.evidence_spans("missing", "memory"), [])

    def test_mcp_exposes_evidence_tool(self) -> None:
        response = json.loads(mcp_server.handle_request(json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}
        })))
        tools = response["result"]["tools"]
        self.assertIn("get_evidence_spans", {tool["name"] for tool in tools})

    def test_multi_word_query_reaches_chunk_via_fts_match(self) -> None:
        # Regression: _fts_rows previously bound the space-joined phrase into the
        # FTS MATCH placeholder (FTS5 implicit-AND) instead of the OR/AND-joined
        # expression, so queries whose words do not co-occur in one chunk returned
        # no rows on the read path. "memory" (n1) and "unrelated" (n2) never
        # co-occur, so only the OR-joined recall path resolves both.
        rows = ask.query("memory unrelated", limit=5)
        self.assertEqual({row["id"] for row in rows}, {"n1", "n2"})

    def test_fts_or_recall_bind_order(self) -> None:
        # Direct pin of the FTS bind position: OR-recall over two words that exist
        # only in separate chunks must reach both; phrase-binding (implicit AND)
        # returns [] because no single row contains both words.
        conn = sqlite3.connect(self.db)
        conn.row_factory = sqlite3.Row
        rows = ask._fts_rows(conn, ["memory", "unrelated"], "", [], 10, False)
        conn.close()
        self.assertEqual({row["id"] for row in rows}, {"n1", "n2"})

    def test_tags_do_not_create_fts_hits(self) -> None:
        # Regression (C-3): the FTS table used to index the `tags` column, so a
        # curated label produced matches for text the chunk never contained. On
        # the live corpus, "leak" appears in zero titles and zero body tokens,
        # yet "leakage" matched 7,824 rows through the `anti-leakage` tag.
        #
        # n2 carries the tag "nonexistentword" in its frontmatter. That string
        # appears in no indexed column — not body, title, or source_family — so
        # a tag-indexed FTS would return n2 here and a prose-only FTS must not.
        conn = sqlite3.connect(self.db)
        conn.row_factory = sqlite3.Row
        tag_only = ask._fts_rows(conn, ["nonexistentword"], "", [], 10, False)
        prose_hit = ask._fts_rows(conn, ["unrelated"], "", [], 10, False)
        conn.close()
        self.assertEqual([r["id"] for r in tag_only], [],
                         "a tag word absent from all indexed prose must not match")
        self.assertEqual([r["id"] for r in prose_hit], ["n2"],
                         "prose that really contains the word must still match")

    def test_family_aggregation_does_not_let_volume_beat_relevance(self) -> None:
        # Regression (C-3): _aggregate_families sorted by `count * 0.25`, so the
        # family contributing the most chunks won even when its best chunk was a
        # worse match than a lone chunk from another family. The lone exact match
        # sits at rank 3 here, so the two orderings genuinely disagree.
        def row(ident, family):
            return {"id": ident, "source_family": family, "title": ident,
                    "snippet": "", "body": "", "path": "", "tags": "[]",
                    "source": "", "trust_tier": 1}
        rows = [row("weak_1", "F1"), row("weak_2", "F1"),
                row("weak_3", "F1"), row("exact", "F2")]
        ranked = ask._aggregate_families(rows, 5)
        self.assertEqual(ranked[0]["id"], "weak_1",
                         "rank order must be preserved across families")
        self.assertEqual(ranked[1]["id"], "exact")
        # And the crowded family must not be able to displace a better match:
        # with the exact match first, volume must not promote F1 above it.
        self.assertEqual(
            [r["id"] for r in ask._aggregate_families(
                [row("exact", "F2"), row("weak_1", "F1"), row("weak_2", "F1")], 5)],
            ["exact", "weak_1"])


class CriticGateTests(unittest.TestCase):
    """The cheap gate before neighbor expansion: expand thin or concentrated
    hit sets, skip the neighbor queries when the base already covers."""

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db = Path(self.tempdir.name) / "graph.db"
        conn = sqlite3.connect(self.db)
        conn.executescript(
            """
            CREATE TABLE nodes(
                id TEXT PRIMARY KEY, title TEXT, path TEXT, tags TEXT,
                headings TEXT, body TEXT, node_type TEXT, source_family TEXT,
                source TEXT, trust_tier INTEGER, semantic_edges TEXT
            );
            CREATE TABLE edges(src TEXT, dst TEXT, kind TEXT, conf REAL, tag TEXT);
            CREATE TABLE node_tags(
                node_id TEXT NOT NULL, tag TEXT NOT NULL,
                PRIMARY KEY(node_id, tag)
            );
            CREATE VIRTUAL TABLE fts USING fts5(id, title, body, source_family);
            """
        )
        nodes = [
            (
                "n1", "Session Memory", "knowledge/corpus/n1.md", '["memory", "graph"]',
                '["Overview", "Retrieval"]',
                "# Overview\n\nSession memory is stored as an append-only graph event.\n\n"
                "# Retrieval\n\nUse bounded evidence spans to reduce token usage.",
                "corpus", "session_memory", "", 1, "{}",
            ),
            (
                "n2", "Unrelated", "knowledge/corpus/n2.md", '["other"]', '[]',
                "An unrelated paragraph.", "corpus", "other", "", 1, "{}",
            ),
        ]
        conn.executemany("INSERT INTO nodes VALUES(?,?,?,?,?,?,?,?,?,?,?)", nodes)
        conn.executemany("INSERT INTO fts VALUES(?,?,?,?)", [(n[0], n[1], n[5], n[7]) for n in nodes])
        conn.executemany("INSERT INTO node_tags VALUES(?, ?)", [("n1", "memory"), ("n1", "graph"), ("n2", "other")])
        conn.commit()
        conn.close()
        self.db_patch = patch.object(ask, "DB", self.db)
        self.db_patch.start()

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.tempdir.cleanup()

    @staticmethod
    def row(ident: str, family: str) -> dict:
        return {"id": ident, "source_family": family, "title": ident,
                "snippet": "", "body": "", "path": "", "tags": "[]",
                "source": "", "trust_tier": 1}

    def test_empty_base_has_nothing_to_expand(self) -> None:
        self.assertEqual(ask.critic_verdict([], 5)[0], "empty")

    def test_thin_base_expands(self) -> None:
        verdict, _ = ask.critic_verdict([self.row("a", "F1")], 5)
        self.assertEqual(verdict, "expand")

    def test_concentrated_full_base_expands(self) -> None:
        verdict, reason = ask.critic_verdict(
            [self.row("a", "F1"), self.row("b", "F1")], 2)
        self.assertEqual(verdict, "expand")
        self.assertIn("concentration", reason)

    def test_diverse_full_base_is_sufficient(self) -> None:
        verdict, _ = ask.critic_verdict(
            [self.row("a", "F1"), self.row("b", "F2")], 2)
        self.assertEqual(verdict, "sufficient")

    def test_sufficient_base_skips_neighbor_queries(self) -> None:
        holder: list[dict] = []
        with patch.object(ask, "get_neighbors",
                          side_effect=AssertionError("must not expand")):
            rows = ask.query("memory unrelated", limit=2, expand=True,
                             verdict_out=holder)
        self.assertEqual({r["id"] for r in rows}, {"n1", "n2"})
        self.assertEqual(holder[0]["verdict"], "sufficient")

    def test_thin_base_still_expands_through_the_gate(self) -> None:
        conn = sqlite3.connect(self.db)
        conn.execute("INSERT INTO edges VALUES('n1', 'n2', 'SEQUENCE', 1.0, '')")
        conn.commit()
        conn.close()
        holder: list[dict] = []
        rows = ask.query("memory", limit=5, expand=True, verdict_out=holder)
        self.assertEqual(holder[0]["verdict"], "expand")
        self.assertIn("n2", {r["id"] for r in rows})


if __name__ == "__main__":
    unittest.main()
