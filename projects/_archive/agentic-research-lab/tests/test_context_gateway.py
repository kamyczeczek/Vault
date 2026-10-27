import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

GRAPH_DIR = Path(__file__).resolve().parents[1] / "knowledge" / "graph"
if str(GRAPH_DIR) not in sys.path:
    sys.path.insert(0, str(GRAPH_DIR))

import context_gateway  # noqa: E402


class ContextGatewayTests(unittest.TestCase):
    def test_empty_question_is_empty(self) -> None:
        result = context_gateway.context_packet("")
        self.assertEqual(result["items"], [])
        self.assertEqual(result["estimated_tokens"], 0)

    def test_mode_budget_is_enforced(self) -> None:
        corpus = [{"id": "c1", "source_family": "family", "path": "p", "snippet": "", "body": ""}]
        with patch.object(context_gateway, "query", return_value=corpus), \
             patch.object(context_gateway, "evidence_spans", return_value=[{"text": "x" * 5000}]), \
             patch.object(context_gateway, "search_events", return_value=[]):
            result = context_gateway.context_packet("question", mode="fast")
        self.assertLessEqual(result["estimated_tokens"], 800)
        self.assertTrue(result["truncated"] or result["items"])

    def test_budget_clips_oversized_middle_item_and_keeps_later_items(self) -> None:
        corpus = [{"id": "c1", "snippet": "small"}, {"id": "c2", "snippet": "large"},
                  {"id": "c3", "snippet": "later"}]
        spans = {"c1": "a" * 100, "c2": "b" * 5000, "c3": "c" * 100}
        with patch.object(context_gateway, "query", return_value=corpus), \
             patch.object(context_gateway, "evidence_spans", side_effect=lambda node, *_args, **_kw: [{"text": spans[node]}]), \
             patch.object(context_gateway, "search_events", return_value=[]):
            result = context_gateway.context_packet("question", mode="fast",
                                                    frontier_dir=Path("missing-frontier"),
                                                    memory_path=Path("missing-memory.md"))
        # DB-1: reserved corpus slots are clipped to fit the budget, never skipped.
        self.assertEqual([item["id"] for item in result["items"]], ["c1", "c2", "c3"])
        by_id = {item["id"]: item for item in result["items"]}
        self.assertEqual(len(by_id["c1"]["text"]), 100)          # small item untouched
        self.assertLess(len(by_id["c2"]["text"]), 5000)          # oversized item clipped
        self.assertLess(len(by_id["c3"]["text"]), 100)          # later item kept, clipped to remaining room

    def test_malformed_artifact_store_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "not-sqlite.db"
            db.write_text("not a database", encoding="utf-8")
            with patch.object(context_gateway, "query", return_value=[]), \
                 patch.object(context_gateway, "search_events", return_value=[]):
                result = context_gateway.context_packet(
                    "artifact", mode="fast", session_graph_path=db,
                    frontier_dir=Path(tmp) / "missing", memory_path=Path(tmp) / "missing.md",
                )
        self.assertEqual(result["items"], [])

    def test_default_session_graph_path_does_not_raise_when_missing(self) -> None:
        with patch.object(context_gateway, "query", return_value=[]), \
             patch.object(context_gateway, "evidence_spans", return_value=[]):
            result = context_gateway.context_packet(
                "session memory", mode="fast",
                frontier_dir=Path("missing-frontier"), memory_path=Path("missing-memory.md"),
            )
        self.assertEqual(result["items"], [])

    def test_invalid_mode_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            context_gateway.context_packet("question", mode="unknown")

    def test_frontier_and_promoted_lesson_are_included(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontier = root / "frontier"
            frontier.mkdir()
            (frontier / "manifest.json").write_text(json.dumps({
                "open_turn_ids": ["t1"], "turns": {"t1": {"next_action": "verify retrieval"}},
                "bound_ok": True,
            }), encoding="utf-8")
            (frontier / "ledger.jsonl").write_text(
                "not-json\n" + json.dumps({"record_type": "turn", "turn_id": "t1",
                    "turn_type": "research", "session_id": "s1",
                    "next_action": "verify retrieval quality", "status": "open"}) + "\n",
                encoding="utf-8")
            memory = root / "memory.md"
            memory.write_text("### retrieval-policy — accepted\n\nUse bounded retrieval evidence.\n", encoding="utf-8")
            with patch.object(context_gateway, "query", return_value=[]), \
                 patch.object(context_gateway, "search_events", return_value=[]):
                result = context_gateway.context_packet(
                    "retrieval evidence", mode="deep", frontier_dir=frontier, memory_path=memory,
                )
            kinds = {item["kind"] for item in result["items"]}
            self.assertIn("frontier_integrity", kinds)
            self.assertIn("lesson", kinds)
            self.assertFalse(any(item["id"] == "frontier:t1" for item in result["items"]))
            self.assertTrue(any(item["kind"] == "frontier_integrity" for item in result["items"]))
            with patch.object(context_gateway, "query", return_value=[]), \
                 patch.object(context_gateway, "search_events", return_value=[]):
                forensic = context_gateway.context_packet(
                    "retrieval evidence", mode="deep", frontier_dir=frontier,
                    memory_path=memory, include_invalid_frontier=True,
                )
            self.assertTrue(any(item["id"] == "frontier:t1" for item in forensic["items"]))

    def test_partial_frontier_is_labeled_without_being_treated_as_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            frontier = Path(tmp) / "frontier"
            frontier.mkdir()
            (frontier / "manifest.json").write_text("{}", encoding="utf-8")
            with patch.object(context_gateway, "query", return_value=[]), \
                 patch.object(context_gateway, "search_events", return_value=[]):
                result = context_gateway.context_packet(
                    "frontier", mode="fast", frontier_dir=frontier,
                    memory_path=Path(tmp) / "missing.md",
                )
        item = next(item for item in result["items"] if item["kind"] == "frontier_integrity")
        self.assertEqual(item["kind"], "frontier_integrity")
        self.assertEqual(item["integrity"], "partial")

    def test_artifacts_are_workspace_scoped(self) -> None:
        import sqlite3
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "session_graph.db"
            conn = sqlite3.connect(db)
            conn.executescript("""
                CREATE TABLE sessions(session_id TEXT, workspace TEXT);
                CREATE TABLE artifacts(artifact_id TEXT, session_id TEXT, path TEXT, artifact_type TEXT);
            """)
            conn.executemany("INSERT INTO sessions VALUES(?,?)", [("s1", "one"), ("s2", "two")])
            conn.executemany("INSERT INTO artifacts VALUES(?,?,?,?)", [
                ("a1", "s1", "tmp/one.log", "log"), ("a2", "s2", "tmp/two.log", "log")])
            conn.commit()
            conn.close()
            with patch.object(context_gateway, "query", return_value=[]), \
                 patch.object(context_gateway, "search_events", return_value=[]):
                result = context_gateway.context_packet(
                    "one log", mode="deep", workspace="one", session_graph_path=db,
                    frontier_dir=Path(tmp) / "missing", memory_path=Path(tmp) / "missing.md",
                )
        self.assertEqual([item["id"] for item in result["items"] if item["kind"] == "artifact"], ["a1"])


if __name__ == "__main__":
    unittest.main()
