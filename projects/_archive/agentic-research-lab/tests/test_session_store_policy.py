import sqlite3
import tempfile
import unittest
from pathlib import Path

from knowledge.graph import session_store


class SessionStorePolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db = Path(self.tempdir.name) / "sessions.db"
        self.session_id = session_store.start_session("workspace", path=self.db, session_id="s1")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_secret_payload_is_redacted(self) -> None:
        event_id = session_store.append_event(
            self.session_id, "tool_result",
            {"api_key": "dont-store", "message": "token=also-secret"},
            path=self.db, event_id="e1",
        )
        self.assertEqual(event_id, "e1")
        event = session_store.timeline(self.session_id, path=self.db)[0]
        self.assertNotIn("dont-store", event["payload"])
        self.assertNotIn("also-secret", event["payload"])
        self.assertIn("REDACTED", event["payload"])

    def test_sensitive_artifact_is_rejected_before_db_write(self) -> None:
        with self.assertRaises(ValueError):
            session_store.record_artifact(self.session_id, "config/.env", db_path=self.db)
        conn = sqlite3.connect(self.db)
        self.assertEqual(conn.execute("SELECT count(*) FROM artifacts").fetchone()[0], 0)
        conn.close()

    def test_safe_artifact_gets_retention_classification(self) -> None:
        artifact_id = session_store.record_artifact(
            self.session_id, "reflection/decision.md", db_path=self.db,
        )
        conn = sqlite3.connect(self.db)
        row = conn.execute("SELECT artifact_id, artifact_type FROM artifacts").fetchone()
        conn.close()
        self.assertEqual(row[0], artifact_id)
        self.assertEqual(row[1], "durable")

    def test_retention_plan_is_dry_run_and_preserves_rows(self) -> None:
        artifact_id = session_store.record_artifact(
            self.session_id, "tmp/run.log", artifact_type="log", db_path=self.db,
        )
        plan = session_store.retention_plan(
            older_than_days=0,
            tier="ephemeral",
            db_path=self.db,
            now_value=session_store.datetime.now(session_store.timezone.utc),
        )
        selected = [item for item in plan if item["artifact_id"] == artifact_id]
        self.assertEqual(len(selected), 1)
        self.assertTrue(selected[0]["eligible"])
        conn = sqlite3.connect(self.db)
        self.assertEqual(conn.execute("SELECT count(*) FROM artifacts").fetchone()[0], 1)
        conn.close()

    def test_durable_artifacts_are_never_retention_eligible(self) -> None:
        artifact_id = session_store.record_artifact(
            self.session_id, "knowledge/rule.md", db_path=self.db,
        )
        plan = session_store.retention_plan(older_than_days=0, db_path=self.db)
        row = next(item for item in plan if item["artifact_id"] == artifact_id)
        self.assertFalse(row["eligible"])

    def test_retention_tiers_are_deterministic(self) -> None:
        self.assertEqual(session_store.retention_tier("tmp/run.log"), "ephemeral")
        self.assertEqual(session_store.retention_tier("src/module.py"), "warm")
        self.assertEqual(session_store.retention_tier("knowledge/rule.md"), "durable")

    def test_retention_plan_is_workspace_scoped(self) -> None:
        other = session_store.start_session("other-workspace", path=self.db, session_id="s2")
        own_id = session_store.record_artifact(self.session_id, "tmp/own.log", db_path=self.db)
        other_id = session_store.record_artifact(other, "tmp/other.log", db_path=self.db)
        plan = session_store.retention_plan(older_than_days=0, workspace="workspace", db_path=self.db,
                                            now_value=session_store.datetime.now(session_store.timezone.utc))
        ids = {item["artifact_id"] for item in plan}
        self.assertEqual(ids, {own_id})
        self.assertNotIn(other_id, ids)

    def test_cleanup_requires_confirmation_and_preserves_events(self) -> None:
        event_id = session_store.append_event(self.session_id, "note", {"ok": True}, path=self.db)
        artifact_id = session_store.record_artifact(self.session_id, "tmp/run.log", db_path=self.db)
        with self.assertRaises(PermissionError):
            session_store.execute_retention_cleanup(older_than_days=0, db_path=self.db)
        deleted = session_store.execute_retention_cleanup(
            older_than_days=0,
            tier="ephemeral",
            workspace="workspace",
            confirmation=session_store.RETENTION_DELETE_CONFIRMATION,
            db_path=self.db,
            now_value=session_store.datetime.now(session_store.timezone.utc),
        )
        self.assertEqual(deleted, [artifact_id])
        self.assertEqual(len(session_store.timeline(self.session_id, path=self.db)), 1)
        self.assertEqual(session_store.timeline(self.session_id, path=self.db)[0]["event_id"], event_id)


if __name__ == "__main__":
    unittest.main()
