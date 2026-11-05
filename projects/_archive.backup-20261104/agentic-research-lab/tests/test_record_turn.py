"""Tests for record_turn.py — the write seam for conversation turns.

The recorder's job is not to store text; `session_store` already does that. Its
job is to refuse. A ledger whose vocabulary drifts fragments the FTS index into
whatever each caller happened to type, and an empty or misattributed turn is
worse than no turn at all, so the refusals are what these pin.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "record_turn.py"


def run(*args: str, stdin: str | None = None, db: Path) -> subprocess.CompletedProcess[str]:
    """Invoke the recorder as a subprocess against a throwaway ledger."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--db", str(db)],
        input=stdin, capture_output=True, text=True, cwd=ROOT,
    )


def payloads(db: Path, session: str) -> list[dict]:
    conn = sqlite3.connect(db)
    rows = conn.execute(
        "SELECT payload FROM events WHERE session_id=? ORDER BY sequence", (session,)
    ).fetchall()
    conn.close()
    return [json.loads(row[0]) for row in rows]


def status_of(db: Path, session: str) -> str:
    conn = sqlite3.connect(db)
    value = conn.execute(
        "SELECT status FROM sessions WHERE session_id=?", (session,)
    ).fetchone()[0]
    conn.close()
    return value


class TurnRecorderCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.db = Path(self._tmp.name) / "sessions.db"
        self.addCleanup(self._tmp.cleanup)

    def start(self, workspace: str = "grill") -> str:
        proc = run("start", workspace, "--session-id", "s1", db=self.db)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout.strip()

    # --- the happy path, end to end -------------------------------------

    def test_full_conversation_is_recorded_and_verifies(self) -> None:
        self.start()
        turns = [
            ("question", "agent", "Q1 - ledger home?", None),
            ("answer", "user", "Extend in place, no new project", "Q1"),
            ("decision", "agent", "Extend session_store in place", None),
        ]
        for event_type, actor, text, question_id in turns:
            extra = ["--question-id", question_id] if question_id else []
            proc = run("turn", "s1", event_type, "--actor", actor, "--text", text,
                       *extra, db=self.db)
            self.assertEqual(proc.returncode, 0, proc.stderr)

        closed = run("close", "s1", db=self.db)
        self.assertEqual(closed.returncode, 0, closed.stderr)
        self.assertIn("chain: ok", closed.stdout)
        self.assertIn("completed", closed.stdout)

    def test_question_id_and_round_survive_into_the_payload(self) -> None:
        self.start()
        run("turn", "s1", "answer", "--actor", "user", "--text", "yes",
            "--round", "2", "--question-id", "Q4", db=self.db)
        payload = payloads(self.db, "s1")[0]
        self.assertEqual(payload["round"], 2)
        self.assertEqual(payload["question_id"], "Q4")
        self.assertEqual(payload["answer"], "yes")

    def test_long_turn_with_quotes_arrives_intact(self) -> None:
        self.start()
        text = 'He said "no" about {"key": "value"} and \'single quotes\' — twice.'
        run("turn", "s1", "user_message", "--actor", "user", "--text", text, db=self.db)
        self.assertEqual(payloads(self.db, "s1")[0]["text"], text)

    def test_text_can_come_from_stdin(self) -> None:
        self.start()
        proc = run("turn", "s1", "insight", "--actor", "agent", stdin="a piped insight", db=self.db)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(payloads(self.db, "s1")[0]["insight"], "a piped insight")

    def test_text_file_source(self) -> None:
        self.start()
        body = Path(self._tmp.name) / "turn.md"
        body.write_text("from a file\n", encoding="utf-8")
        proc = run("turn", "s1", "term", "--actor", "agent",
                   "--text-file", str(body), db=self.db)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(payloads(self.db, "s1")[0]["term"], "from a file")

    def test_secrets_are_redacted_before_they_are_stored(self) -> None:
        self.start()
        run("turn", "s1", "user_message", "--actor", "user",
            "--text", "my api_key=sk-live-should-not-persist", db=self.db)
        stored = payloads(self.db, "s1")[0]["text"]
        self.assertNotIn("sk-live-should-not-persist", stored)
        self.assertIn("REDACTED", stored)

    # --- the refusals, which are the real contract ----------------------

    def test_unknown_event_type_is_refused(self) -> None:
        self.start()
        proc = run("turn", "s1", "chit_chat", "--actor", "user", "--text", "hi", db=self.db)
        self.assertEqual(proc.returncode, 2)  # argparse rejects a closed choice list
        self.assertEqual(payloads(self.db, "s1"), [])

    def test_agent_may_not_impersonate_the_user(self) -> None:
        self.start()
        proc = run("turn", "s1", "user_message", "--actor", "agent", "--text", "I agree", db=self.db)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("written by the user", proc.stderr)
        self.assertEqual(payloads(self.db, "s1"), [])

    def test_user_may_not_write_an_agent_decision(self) -> None:
        self.start()
        proc = run("turn", "s1", "decision", "--actor", "user", "--text", "decided", db=self.db)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("written by the agent", proc.stderr)
        self.assertEqual(payloads(self.db, "s1"), [])

    def test_empty_turn_is_refused(self) -> None:
        self.start()
        proc = run("turn", "s1", "user_message", "--actor", "user", "--text", "   ", db=self.db)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("empty", proc.stderr)
        self.assertEqual(payloads(self.db, "s1"), [])

    def test_missing_body_is_refused(self) -> None:
        # A closed pipe is not a tty, so this covers "stdin was piped but empty".
        # The tty branch is unreachable from a test; a caller who supplies no
        # body at all gets the same non-zero exit either way.
        self.start()
        proc = run("turn", "s1", "user_message", "--actor", "user", stdin="", db=self.db)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("no turn body", proc.stderr)
        self.assertEqual(payloads(self.db, "s1"), [])

    def test_unreadable_text_file_is_refused_as_missing_not_empty(self) -> None:
        self.start()
        proc = run("turn", "s1", "user_message", "--actor", "user",
                   "--text-file", str(Path(self._tmp.name) / "absent.md"), db=self.db)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("no turn body", proc.stderr)
        self.assertEqual(payloads(self.db, "s1"), [])

    def test_close_refuses_to_seal_a_tampered_session(self) -> None:
        self.start()
        run("turn", "s1", "user_message", "--actor", "user", "--text", "truth", db=self.db)
        conn = sqlite3.connect(self.db)
        conn.execute("UPDATE events SET payload='{\"text\":\"edited\"}'")
        conn.commit()
        conn.close()

        proc = run("close", "s1", db=self.db)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("hash mismatch", proc.stdout)
        self.assertNotIn("completed", proc.stdout)
        self.assertEqual(
            status_of(self.db, "s1"), "active",
            "a broken chain must stay unsealed, not finished as completed",
        )

    def test_close_refuses_an_unknown_session(self) -> None:
        # An empty timeline is trivially well-formed, so without an existence
        # check this seals a typo'd id as a completed conversation.
        self.start()
        proc = run("close", "no-such-session", db=self.db)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("unknown session", proc.stdout)

    def test_start_prints_a_bare_lf_terminated_id(self) -> None:
        # A session id is the one value a caller captures in a shell. Python
        # writes \r\n on Windows and MSYS $(...) strips only the \n, so a
        # captured id kept a trailing \r and every later lookup missed.
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "start", "grill",
             "--session-id", "crlf-probe", "--db", str(self.db)],
            capture_output=True, cwd=ROOT,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        self.assertNotIn(b"\r", proc.stdout, "captured session ids must not carry a CR")
        self.assertEqual(proc.stdout.decode().strip(), "crlf-probe")


if __name__ == "__main__":
    unittest.main()
