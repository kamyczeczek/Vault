#!/usr/bin/env python3
"""Append-only session event store and causal graph projection.

The corpus graph remains derived from Markdown. Session execution data lives in a
separate SQLite database so runtime events cannot invalidate the corpus graph's
fingerprint or node-count gates.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
DB = Path(__file__).with_name("sessions.db")
_SECRET_KEY = re.compile(r"(?i)(api[_-]?key|token|password|secret|private[_-]?key)")
_SECRET_VALUE = re.compile(r"(?i)(api[_-]?key|token|password|secret|private[_-]?key)\s*[:=]\s*([^,\s]+)")
DEFAULT_SENSITIVE_PATH_PATTERNS = (
    ".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "*credentials*",
    "*secret*", "*token*", "*password*", ".git/*", ".ssh/*",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): "[REDACTED]" if _SECRET_KEY.search(str(k)) else redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return _SECRET_VALUE.sub(lambda m: f"{m.group(1)}=[REDACTED]", value)
    return value


def payload_json(payload: Any) -> str:
    return json.dumps(redact(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _normalized_path(path: str) -> str:
    return path.replace("\\", "/").strip().lstrip("./").lower()


def is_sensitive_path(path: str, patterns: Iterable[str] = DEFAULT_SENSITIVE_PATH_PATTERNS) -> bool:
    """Return whether an artifact path should never enter the session index."""
    normalized = _normalized_path(path)
    parts = normalized.split("/")
    return any(
        fnmatch.fnmatch(normalized, pattern.lower()) or
        fnmatch.fnmatch(parts[-1], pattern.lower())
        for pattern in patterns
    )


def retention_tier(path: str, artifact_type: str | None = None) -> str:
    """Classify metadata retention without retaining artifact contents."""
    normalized = _normalized_path(path)
    kind = (artifact_type or "").lower()
    if kind in {"log", "transcript", "tool_output", "temporary"} or "/tmp/" in f"/{normalized}/":
        return "ephemeral"
    if kind in {"lesson", "decision", "verification"} or normalized.startswith(("reflection/", "knowledge/")):
        return "durable"
    return "warm"


def record_artifact(session_id: str, path: str, *, event_id: str | None = None,
                    content_hash: str | None = None, artifact_type: str | None = None,
                    payload_ref: str | None = None, db_path: Path = DB,
                    sensitive_patterns: Iterable[str] = DEFAULT_SENSITIVE_PATH_PATTERNS) -> str:
    """Record safe artifact metadata; reject sensitive paths before persistence."""
    if not path or is_sensitive_path(path, sensitive_patterns):
        raise ValueError(f"sensitive artifact path is not indexable: {path!r}")
    artifact_id = str(uuid.uuid4())
    conn = connect(db_path)
    if not conn.execute("SELECT 1 FROM sessions WHERE session_id=?", (session_id,)).fetchone():
        conn.close()
        raise ValueError(f"unknown session: {session_id}")
    metadata_type = artifact_type or retention_tier(path)
    conn.execute(
        "INSERT INTO artifacts(artifact_id,session_id,event_id,path,content_hash,artifact_type,payload_ref) VALUES(?,?,?,?,?,?,?)",
        (artifact_id, session_id, event_id, path, content_hash, metadata_type, payload_ref),
    )
    conn.commit()
    conn.close()
    return artifact_id


RETENTION_DAYS = {"ephemeral": 7, "warm": 90, "durable": None}


RETENTION_DELETE_CONFIRMATION = "DELETE_RETENTION_ARTIFACTS"


def retention_plan(*, older_than_days: int | None = None, tier: str | None = None,
                   workspace: str | None = None, db_path: Path = DB,
                   now_value: datetime | None = None) -> list[dict[str, Any]]:
    """Return an auditable deletion plan; never deletes rows."""
    if older_than_days is not None and older_than_days < 0:
        raise ValueError("older_than_days must be non-negative")
    if tier is not None and tier not in RETENTION_DAYS:
        raise ValueError(f"unknown retention tier: {tier}")
    cutoff = None
    if older_than_days is not None:
        current = now_value or datetime.now(timezone.utc)
        cutoff = current.timestamp() - older_than_days * 86400
    conn = connect(db_path)
    query = (
        "SELECT a.artifact_id,a.session_id,a.event_id,a.path,a.content_hash,a.artifact_type,"
        "s.started_at,s.status FROM artifacts a JOIN sessions s ON s.session_id=a.session_id "
    )
    params: tuple[Any, ...] = ()
    if workspace is not None:
        query += "WHERE s.workspace=? "
        params = (workspace,)
    query += "ORDER BY a.artifact_id"
    rows = conn.execute(query, params).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["retention_tier"] = retention_tier(item["path"], item["artifact_type"])
        item["eligible"] = False
        item["reason"] = "durable_or_not_old_enough"
        if tier is not None and item["retention_tier"] != tier:
            result.append(item)
            continue
        if item["retention_tier"] == "durable":
            result.append(item)
            continue
        if cutoff is not None:
            try:
                started = datetime.fromisoformat(item["started_at"].replace("Z", "+00:00")).timestamp()
            except (AttributeError, ValueError):
                started = None
            if started is not None and started <= cutoff:
                item["eligible"] = True
                item["reason"] = "retention_cutoff"
        result.append(item)
    conn.close()
    return result


def execute_retention_cleanup(*, older_than_days: int, tier: str | None = None,
                              workspace: str | None = None,
                              confirmation: str = "", db_path: Path = DB,
                              now_value: datetime | None = None) -> list[str]:
    """Delete only eligible artifact metadata after explicit authorization.

    Session events and source files are never deleted by this operation. Callers
    should persist the returned IDs as an audit record before proceeding.
    """
    if confirmation != RETENTION_DELETE_CONFIRMATION:
        raise PermissionError("explicit retention deletion confirmation is required")
    plan = retention_plan(older_than_days=older_than_days, tier=tier, workspace=workspace,
                          db_path=db_path, now_value=now_value)
    ids = [item["artifact_id"] for item in plan if item["eligible"]]
    if not ids:
        return []
    conn = connect(db_path)
    conn.executemany("DELETE FROM artifacts WHERE artifact_id=?", ((artifact_id,) for artifact_id in ids))
    conn.commit()
    conn.close()
    return ids


def connect(path: Path = DB) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions(
            session_id TEXT PRIMARY KEY,
            parent_session_id TEXT REFERENCES sessions(session_id),
            workspace TEXT NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            status TEXT NOT NULL,
            agent_kind TEXT NOT NULL,
            model TEXT,
            provider TEXT,
            schema_version INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS events(
            event_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES sessions(session_id),
            parent_event_id TEXT REFERENCES events(event_id),
            sequence INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            payload TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            previous_hash TEXT,
            verification_status TEXT NOT NULL DEFAULT 'unverified',
            UNIQUE(session_id, sequence)
        );
        CREATE INDEX IF NOT EXISTS events_session_sequence ON events(session_id, sequence);
        CREATE INDEX IF NOT EXISTS events_type ON events(event_type);
        CREATE TABLE IF NOT EXISTS artifacts(
            artifact_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES sessions(session_id),
            event_id TEXT REFERENCES events(event_id),
            path TEXT NOT NULL,
            content_hash TEXT,
            artifact_type TEXT,
            payload_ref TEXT
        );
        CREATE TABLE IF NOT EXISTS session_edges(
            src_id TEXT NOT NULL,
            dst_id TEXT NOT NULL,
            edge_kind TEXT NOT NULL,
            evidence_ref TEXT,
            PRIMARY KEY(src_id, dst_id, edge_kind)
        );
        CREATE TABLE IF NOT EXISTS lesson_links(
            lesson_id TEXT NOT NULL,
            source_event_id TEXT NOT NULL REFERENCES events(event_id),
            verification_event_id TEXT NOT NULL REFERENCES events(event_id),
            status TEXT NOT NULL CHECK(status IN ('proposed','verified','rejected')),
            last_validated_at TEXT NOT NULL,
            PRIMARY KEY(lesson_id, source_event_id, verification_event_id)
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS event_fts USING fts5(
            event_id UNINDEXED, session_id UNINDEXED, event_type, payload
        );
        """
    )
    return conn


def _last_hash(conn: sqlite3.Connection, session_id: str) -> str | None:
    row = conn.execute(
        "SELECT payload_hash FROM events WHERE session_id=? ORDER BY sequence DESC LIMIT 1",
        (session_id,),
    ).fetchone()
    return row[0] if row else None


def start_session(workspace: str, *, agent_kind: str = "hermes", model: str = "", provider: str = "",
                  parent_session_id: str | None = None, session_id: str | None = None,
                  path: Path = DB) -> str:
    sid = session_id or str(uuid.uuid4())
    conn = connect(path)
    conn.execute(
        "INSERT INTO sessions(session_id,parent_session_id,workspace,started_at,status,agent_kind,model,provider) VALUES(?,?,?,?,?,?,?,?)",
        (sid, parent_session_id, workspace, now(), "active", agent_kind, model, provider),
    )
    if parent_session_id:
        conn.execute("INSERT OR IGNORE INTO session_edges VALUES(?,?,?,?)",
                     (parent_session_id, sid, "SPAWNED_SESSION", None))
    conn.commit()
    conn.close()
    return sid


def append_event(session_id: str, event_type: str, payload: Any, *, actor_id: str = "agent",
                 parent_event_id: str | None = None, verification_status: str = "unverified",
                 event_id: str | None = None, path: Path = DB) -> str:
    conn = connect(path)
    session = conn.execute("SELECT session_id FROM sessions WHERE session_id=?", (session_id,)).fetchone()
    if not session:
        conn.close()
        raise ValueError(f"unknown session: {session_id}")
    row = conn.execute("SELECT COALESCE(MAX(sequence), -1) + 1 FROM events WHERE session_id=?", (session_id,)).fetchone()
    sequence = int(row[0])
    body = payload_json(payload)
    previous_hash = _last_hash(conn, session_id)
    digest = hashlib.sha256(f"{previous_hash or ''}\0{event_type}\0{body}".encode()).hexdigest()
    eid = event_id or str(uuid.uuid4())
    conn.execute(
        "INSERT INTO events(event_id,session_id,parent_event_id,sequence,event_type,actor_id,occurred_at,payload,payload_hash,previous_hash,verification_status) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (eid, session_id, parent_event_id, sequence, event_type, actor_id, now(), body, digest, previous_hash, verification_status),
    )
    conn.execute("INSERT INTO event_fts VALUES(?,?,?,?)", (eid, session_id, event_type, body))
    conn.commit()
    conn.close()
    return eid


def finish_session(session_id: str, status: str = "completed", *, path: Path = DB) -> None:
    if status not in {"completed", "failed", "aborted", "branched"}:
        raise ValueError(f"invalid terminal status: {status}")
    conn = connect(path)
    changed = conn.execute("UPDATE sessions SET status=?, ended_at=? WHERE session_id=?", (status, now(), session_id)).rowcount
    if not changed:
        conn.close()
        raise ValueError(f"unknown session: {session_id}")
    conn.commit()
    conn.close()


def link_lesson(lesson_id: str, source_event_id: str, verification_event_id: str,
                status: str = "verified", *, path: Path = DB) -> None:
    if status not in {"proposed", "verified", "rejected"}:
        raise ValueError(f"invalid lesson status: {status}")
    conn = connect(path)
    rows = conn.execute("SELECT event_id FROM events WHERE event_id IN (?,?)", (source_event_id, verification_event_id)).fetchall()
    if len(rows) != 2:
        conn.close()
        raise ValueError("source and verification events must both exist")
    conn.execute("INSERT OR REPLACE INTO lesson_links VALUES(?,?,?,?,?)",
                 (lesson_id, source_event_id, verification_event_id, status, now()))
    conn.execute("INSERT OR IGNORE INTO session_edges VALUES(?,?,?,?)",
                 (source_event_id, verification_event_id, "VERIFIED_BY", lesson_id))
    conn.commit()
    conn.close()


def search(text: str, limit: int = 10, *, path: Path = DB) -> list[dict[str, Any]]:
    conn = connect(path)
    rows = conn.execute(
        "SELECT e.* FROM event_fts f JOIN events e ON e.event_id=f.event_id WHERE event_fts MATCH ? ORDER BY e.sequence LIMIT ?",
        (text, limit),
    ).fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result


def timeline(session_id: str, *, path: Path = DB) -> list[dict[str, Any]]:
    conn = connect(path)
    rows = conn.execute("SELECT * FROM events WHERE session_id=? ORDER BY sequence", (session_id,)).fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result

def session_exists(session_id: str, *, path: Path = DB) -> bool:
    """Whether `session_id` names an open or closed session in this store."""
    conn = connect(path)
    row = conn.execute(
        "SELECT 1 FROM sessions WHERE session_id=?", (session_id,)
    ).fetchone()
    conn.close()
    return row is not None


def verify_chain(session_id: str, *, path: Path = DB) -> tuple[bool, str]:
    # An unknown id yields an empty timeline, and an empty timeline is
    # trivially well-formed — so without this check the function certifies a
    # session that was never opened. "Verified" must mean "this exists and its
    # history is intact", not "I found nothing wrong with nothing".
    if not session_exists(session_id, path=path):
        return False, f"unknown session {session_id}"
    events = timeline(session_id, path=path)
    previous: str | None = None
    for expected, event in enumerate(events):
        if event["sequence"] != expected or event["previous_hash"] != previous:
            return False, f"sequence/hash link broken at event {event['event_id']}"
        digest = hashlib.sha256(f"{previous or ''}\0{event['event_type']}\0{event['payload']}".encode()).hexdigest()
        if digest != event["payload_hash"]:
            return False, f"payload hash mismatch at event {event['event_id']}"
        previous = digest
    return True, "ok"


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start"); start.add_argument("workspace"); start.add_argument("--agent-kind", default="hermes"); start.add_argument("--model", default=""); start.add_argument("--provider", default="")
    event = sub.add_parser("event"); event.add_argument("session_id"); event.add_argument("event_type"); event.add_argument("payload"); event.add_argument("--actor", default="agent"); event.add_argument("--verified", action="store_true")
    finish = sub.add_parser("finish"); finish.add_argument("session_id"); finish.add_argument("--status", default="completed")
    verify = sub.add_parser("verify"); verify.add_argument("session_id")
    search_cmd = sub.add_parser("search"); search_cmd.add_argument("query"); search_cmd.add_argument("--limit", type=int, default=10)
    timeline_cmd = sub.add_parser("timeline"); timeline_cmd.add_argument("session_id")
    args = parser.parse_args()
    try:
        if args.command == "start": print(start_session(args.workspace, agent_kind=args.agent_kind, model=args.model, provider=args.provider))
        elif args.command == "event": print(append_event(args.session_id, args.event_type, json.loads(args.payload), actor_id=args.actor, verification_status="verified" if args.verified else "unverified"))
        elif args.command == "finish": finish_session(args.session_id, args.status)
        elif args.command == "verify":
            ok, message = verify_chain(args.session_id); print(message); return 0 if ok else 1
        elif args.command == "search": print(json.dumps(search(args.query, args.limit), indent=2, ensure_ascii=False))
        elif args.command == "timeline": print(json.dumps(timeline(args.session_id), indent=2, ensure_ascii=False))
    except (ValueError, json.JSONDecodeError, sqlite3.Error) as exc:
        print(f"error: {exc}", file=sys.stderr); return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
