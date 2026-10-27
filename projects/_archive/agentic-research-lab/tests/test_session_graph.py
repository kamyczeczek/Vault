import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys

from knowledge.graph import session_graph

GRAPH_DIR = Path(__file__).resolve().parents[1] / "knowledge" / "graph"
if str(GRAPH_DIR) not in sys.path:
    sys.path.insert(0, str(GRAPH_DIR))
import mcp_server  # noqa: E402


class SessionGraphProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.source = root / "sessions.db"
        self.destination = root / "session_graph.db"
        conn = sqlite3.connect(self.source)
        conn.executescript(
            """
            CREATE TABLE sessions(session_id TEXT PRIMARY KEY, parent_session_id TEXT,
                workspace TEXT NOT NULL, started_at TEXT NOT NULL, ended_at TEXT,
                status TEXT NOT NULL, agent_kind TEXT NOT NULL, model TEXT, provider TEXT);
            CREATE TABLE events(event_id TEXT PRIMARY KEY, session_id TEXT NOT NULL,
                parent_event_id TEXT, sequence INTEGER NOT NULL, event_type TEXT NOT NULL,
                actor_id TEXT NOT NULL, occurred_at TEXT NOT NULL, payload TEXT NOT NULL,
                payload_hash TEXT NOT NULL, verification_status TEXT NOT NULL);
            CREATE TABLE artifacts(artifact_id TEXT PRIMARY KEY, session_id TEXT NOT NULL,
                event_id TEXT, path TEXT NOT NULL, content_hash TEXT, artifact_type TEXT, payload_ref TEXT);
            CREATE TABLE session_edges(src_id TEXT, dst_id TEXT, edge_kind TEXT, evidence_ref TEXT);
            CREATE TABLE lesson_links(lesson_id TEXT, source_event_id TEXT,
                verification_event_id TEXT, status TEXT, last_validated_at TEXT);
            """
        )
        conn.execute("INSERT INTO sessions VALUES(?,?,?,?,?,?,?,?,?)",
                     ("s1", None, "workspace", "2026-01-01T00:00:00Z", None,
                      "active", "agent", "model", "provider"))
        conn.execute("INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?)",
                     ("e1", "s1", None, 0, "tool_result", "agent",
                      "2026-01-01T00:00:01Z", '{"result":"redacted"}', "hash", "verified"))
        conn.execute("INSERT INTO session_edges VALUES(?,?,?,?)", ("s1", "e1", "CONTAINS", "e1"))
        conn.commit()
        conn.close()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_projection_is_rebuildable_and_counts_match(self) -> None:
        first = session_graph.project(self.source, self.destination)
        first_bytes = self.destination.read_bytes()
        second = session_graph.project(self.source, self.destination)
        second_bytes = self.destination.read_bytes()
        self.assertEqual(first["counts"], {"sessions": 1, "events": 1, "artifacts": 0, "edges": 1, "lesson_links": 0})
        self.assertEqual(first["source_fingerprint"], second["source_fingerprint"])
        self.assertEqual(first_bytes, second_bytes)

    def test_projection_preserves_redacted_payload_and_relationship(self) -> None:
        session_graph.project(self.source, self.destination)
        conn = sqlite3.connect(self.destination)
        self.assertEqual(conn.execute("SELECT payload FROM events WHERE event_id='e1'").fetchone()[0], '{"result":"redacted"}')
        self.assertEqual(conn.execute("SELECT edge_kind FROM edges WHERE src_id='s1'").fetchone()[0], "CONTAINS")
        self.assertEqual(conn.execute("SELECT event_id FROM event_fts").fetchone()[0], "e1")
        conn.close()

    def test_search_and_neighbors_are_workspace_scoped(self) -> None:
        session_graph.project(self.source, self.destination)
        rows = session_graph.search_events("redacted", path=self.destination, workspace="workspace")
        self.assertEqual([row["event_id"] for row in rows], ["e1"])
        self.assertEqual(session_graph.search_events("redacted", path=self.destination, workspace="other"), [])
        self.assertEqual(session_graph.neighbors("s1", path=self.destination)[0]["edge_kind"], "CONTAINS")

    def test_mcp_lists_projected_session_tools(self) -> None:
        response = json.loads(mcp_server.handle_request(json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}
        })))
        names = {tool["name"] for tool in response["result"]["tools"]}
        self.assertIn("query_session_graph", names)
        self.assertIn("get_session_graph_neighbors", names)


if __name__ == "__main__":
    unittest.main()
