#!/usr/bin/env python3
"""Build a deterministic graph projection from the append-only session store.

The session store remains authoritative. This derived database is disposable and
optimized for graph-oriented retrieval, so rebuilding it never changes graph.db.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DB = Path(__file__).with_name("sessions.db")
PROJECTION_DB = Path(__file__).with_name("session_graph.db")
SCHEMA_VERSION = 1


def search_events(text: str, limit: int = 10, *, path: Path = PROJECTION_DB,
                  workspace: str | None = None) -> list[dict[str, Any]]:
    """Search projected redacted events with optional workspace scoping."""
    if not path.exists() or not text.strip() or limit < 1:
        return []
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    sql = ("SELECT e.*, s.workspace FROM event_fts f "
           "JOIN events e ON e.event_id=f.event_id "
           "JOIN sessions s ON s.session_id=e.session_id "
           "WHERE event_fts MATCH ?")
    params: list[Any] = [text]
    if workspace is not None:
        sql += " AND s.workspace=?"
        params.append(workspace)
    sql += " ORDER BY e.occurred_at DESC, e.sequence DESC LIMIT ?"
    params.append(limit)
    rows = [dict(row) for row in conn.execute(sql, params).fetchall()]
    conn.close()
    return rows


def neighbors(node_id: str, limit: int = 10, *, path: Path = PROJECTION_DB) -> list[dict[str, Any]]:
    """Return bounded typed neighbors for a session or event node."""
    if not path.exists() or limit < 1:
        return []
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT src_id, dst_id, edge_kind, evidence_ref FROM edges "
        "WHERE src_id=? OR dst_id=? ORDER BY edge_kind, src_id, dst_id LIMIT ?",
        (node_id, node_id, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def _source_fingerprint(conn: sqlite3.Connection) -> str:
    digest = hashlib.sha256()
    for table, order in (("sessions", "session_id"), ("events", "event_id"),
                         ("artifacts", "artifact_id"), ("session_edges", "src_id, dst_id, edge_kind"),
                         ("lesson_links", "lesson_id, source_event_id, verification_event_id")):
        try:
            rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order}").fetchall()
        except sqlite3.OperationalError:
            rows = []
        for row in rows:
            digest.update(json.dumps(tuple(row), ensure_ascii=False, sort_keys=True, default=str).encode())
            digest.update(b"\n")
    return digest.hexdigest()[:16]


def _schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE projection_meta(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE sessions(
            session_id TEXT PRIMARY KEY,
            parent_session_id TEXT,
            workspace TEXT NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            status TEXT NOT NULL,
            agent_kind TEXT NOT NULL,
            model TEXT,
            provider TEXT
        );
        CREATE TABLE events(
            event_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            parent_event_id TEXT,
            sequence INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            payload TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            verification_status TEXT NOT NULL,
            UNIQUE(session_id, sequence)
        );
        CREATE TABLE artifacts(
            artifact_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            event_id TEXT,
            path TEXT NOT NULL,
            content_hash TEXT,
            artifact_type TEXT,
            payload_ref TEXT
        );
        CREATE TABLE edges(
            src_id TEXT NOT NULL,
            dst_id TEXT NOT NULL,
            edge_kind TEXT NOT NULL,
            evidence_ref TEXT,
            PRIMARY KEY(src_id, dst_id, edge_kind)
        );
        CREATE TABLE lesson_links(
            lesson_id TEXT NOT NULL,
            source_event_id TEXT NOT NULL,
            verification_event_id TEXT NOT NULL,
            status TEXT NOT NULL,
            last_validated_at TEXT NOT NULL,
            PRIMARY KEY(lesson_id, source_event_id, verification_event_id)
        );
        CREATE VIRTUAL TABLE event_fts USING fts5(
            event_id UNINDEXED, session_id UNINDEXED, event_type, payload
        );
        CREATE INDEX events_session_sequence ON events(session_id, sequence);
        CREATE INDEX events_type ON events(event_type);
        CREATE INDEX edges_src_kind ON edges(src_id, edge_kind);
        CREATE INDEX edges_dst_kind ON edges(dst_id, edge_kind);
        CREATE INDEX sessions_workspace_status ON sessions(workspace, status);
        """
    )


def project(source: Path = SOURCE_DB, destination: Path = PROJECTION_DB) -> dict[str, Any]:
    if not source.exists():
        raise FileNotFoundError(f"session source does not exist: {source}")
    src = sqlite3.connect(source)
    src.row_factory = sqlite3.Row
    fingerprint = _source_fingerprint(src)
    tmp = destination.with_suffix(destination.suffix + ".new")
    tmp.unlink(missing_ok=True)
    out = sqlite3.connect(tmp)
    _schema(out)

    for row in src.execute("SELECT session_id,parent_session_id,workspace,started_at,ended_at,status,agent_kind,model,provider FROM sessions ORDER BY session_id"):
        out.execute("INSERT INTO sessions VALUES(?,?,?,?,?,?,?,?,?)", tuple(row))
    for row in src.execute("SELECT event_id,session_id,parent_event_id,sequence,event_type,actor_id,occurred_at,payload,payload_hash,verification_status FROM events ORDER BY session_id,sequence"):
        values = tuple(row)
        out.execute("INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?)", values)
        out.execute("INSERT INTO event_fts VALUES(?,?,?,?)", (row[0], row[1], row[4], row[7]))
    for table, columns in (("artifacts", "artifact_id,session_id,event_id,path,content_hash,artifact_type,payload_ref"),
                           ("session_edges", "src_id,dst_id,edge_kind,evidence_ref"),
                           ("lesson_links", "lesson_id,source_event_id,verification_event_id,status,last_validated_at")):
        for row in src.execute(f"SELECT {columns} FROM {table} ORDER BY 1,2,3"):
            target = "edges" if table == "session_edges" else table
            out.execute(f"INSERT INTO {target} VALUES({','.join('?' for _ in row)})", tuple(row))

    counts = {}
    for table in ("sessions", "events", "artifacts", "edges", "lesson_links"):
        counts[table] = out.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    out.executemany("INSERT INTO projection_meta VALUES(?,?)", [
        ("schema_version", str(SCHEMA_VERSION)),
        ("source_fingerprint", fingerprint),
        ("source_path", str(source)),
    ])
    out.commit()
    out.close()
    src.close()
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp.replace(destination)
    return {"schema_version": SCHEMA_VERSION, "source_fingerprint": fingerprint, "counts": counts}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE_DB)
    parser.add_argument("--destination", type=Path, default=PROJECTION_DB)
    args = parser.parse_args()
    print(json.dumps(project(args.source, args.destination), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
