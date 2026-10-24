#!/usr/bin/env python3
"""Session Memory MCP server — stdio JSON-RPC (protocol 2024-11-05).

Thin MCP wrapper over `memory_index.py`: reuses `query_memory`, `open_db`,
`log_usage` directly — no duplicated retrieval logic. Read-only: query / get /
stats. No ingest (write path stays on the CLI by design).

Stdlib only. Run with the Windows interpreter (`python.exe`), not WSL
`python3` — the index DB resolves under the Windows home (CONTEXT.md).

Usage:
  python.exe scripts/memory_mcp.py          # stdio server (MCP handshake)
  python.exe scripts/mcp_call.py python.exe scripts/memory_mcp.py memory_query '{"query":"cache hit ratio","limit":5}'

Tools:
  memory_query  — survey search, one line per hit (cheap default)
  memory_get    — one chunk in full by chunk_id (drill-down)
  memory_stats  — index health summary (+ usage telemetry with usage=true)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from memory_index import (  # noqa: E402
    log_usage,
    open_db,
    query_memory,
)

PROTOCOL_VERSION = "2025-06-18"
SERVER_NAME = "session-memory"
SERVER_VERSION = "0.1.0"

TOOLS = [
    {
        "name": "memory_query",
        "description": (
            "Search past agent sessions (701 sessions, FTS5). "
            "Survey first: one line per hit. Then memory_get for the one hit worth reading. "
            "Use 2-3 transcript tokens (e.g. '--check', 'CRLF', 'bm25'), not full sentences; "
            "more words = narrower (AND, OR fallback). "
            "Use type='error' for failures, type='decision' for past choices."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "2-3 keyword tokens from the transcript"},
                "limit": {"type": "integer", "default": 8, "description": "Max results (default 8)"},
                "agent": {"type": "string", "description": "Filter by agent (e.g. goose, pi, opencode)"},
                "type": {
                    "type": "string",
                    "enum": ["error", "decision", "tool", "content", "curated"],
                    "description": "Filter by chunk type",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "memory_get",
        "description": (
            "Drill down: print one chunk in full by chunk_id "
            "(e.g. 'pi::01a0f438-65c::202'). Use after memory_query."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "chunk_id": {"type": "string", "description": "Chunk id from a memory_query hit"},
            },
            "required": ["chunk_id"],
        },
    },
    {
        "name": "memory_stats",
        "description": "Index health: session/chunk counts, date range, per-agent and per-type breakdown.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "usage": {"type": "boolean", "default": False, "description": "Include query/get usage telemetry"},
            },
        },
    },
]


def _text(content: str, is_error: bool = False) -> dict:
    return {
        "jsonrpc": "2.0",
        "content": [{"type": "text", "text": content}],
        "isError": is_error,
    }


def tool_memory_query(args: dict) -> dict:
    q = (args.get("query") or "").strip()
    if not q:
        return _text("error: 'query' is required (2-3 keyword tokens)", True)
    limit = int(args.get("limit") or 8)
    con = open_db()
    try:
        results = query_memory(
            con, q, limit=limit,
            agent_filter=args.get("agent"),
            chunk_type_filter=args.get("type"),
        )
    finally:
        con.close()
    log_usage({"cmd": "query", "query": q, "limit": limit,
               "agent": args.get("agent"), "type": args.get("type"),
               "hits": len(results), "via": "mcp"})
    lines = [f"{r['chunk_id']}  score={r['score']:.3f}  {r['heading'][:80]}" for r in results]
    return _text("\n".join(lines) if lines else "(no hits — narrow to 2-3 transcript tokens)")


def tool_memory_get(args: dict) -> dict:
    chunk_id = args.get("chunk_id") or ""
    if not chunk_id:
        return _text("error: 'chunk_id' is required", True)
    con = open_db()
    try:
        row = con.execute(
            "SELECT chunk_id, agent, session_id, session_title, session_date,"
            " raw_path, chunk_type, heading, body FROM memory_fts WHERE chunk_id=?",
            (chunk_id,),
        ).fetchone()
    finally:
        con.close()
    if not row:
        log_usage({"cmd": "get", "chunk_id": chunk_id, "found": False, "via": "mcp"})
        return _text(f"Chunk not found: {chunk_id}", True)
    log_usage({"cmd": "get", "chunk_id": chunk_id, "found": True, "via": "mcp"})
    body = (
        f"chunk_id: {row[0]}\nagent: {row[1]}\nsession_id: {row[2]}\n"
        f"session_title: {row[3]}\nsession_date: {row[4]}\nraw_path: {row[5]}\n"
        f"chunk_type: {row[6]}\nheading: {row[7]}\n\n{row[8]}"
    )
    return _text(body)


def tool_memory_stats(args: dict) -> dict:
    show_usage = bool(args.get("usage"))
    con = open_db()
    try:
        n_sessions = con.execute("SELECT COUNT(*) FROM sessions_meta").fetchone()[0]
        n_chunks = con.execute("SELECT COUNT(*) FROM memory_fts").fetchone()[0]
        row = con.execute("SELECT MIN(session_date), MAX(session_date) FROM sessions_meta").fetchone()
        agents = con.execute(
            "SELECT agent, COUNT(*) FROM sessions_meta GROUP BY agent ORDER BY COUNT(*) DESC").fetchall()
        types = con.execute(
            "SELECT chunk_type, COUNT(*) FROM memory_fts GROUP BY chunk_type ORDER BY COUNT(*) DESC").fetchall()
    finally:
        con.close()
    lines = [
        f"sessions: {n_sessions}",
        f"chunks: {n_chunks}",
        f"date range: {row[0]} -> {row[1]}",
        "by agent: " + ", ".join(f"{a}={c}" for a, c in agents),
        "by type: " + ", ".join(f"{t}={c}" for t, c in types),
    ]
    if show_usage:
        from memory_index import TELEMETRY_PATH
        import collections
        if TELEMETRY_PATH.exists():
            cmds: collections.Counter = collections.Counter()
            with TELEMETRY_PATH.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        cmds[json.loads(line).get("cmd", "?")] += 1
                    except Exception:
                        continue
            lines.append("usage: " + ", ".join(f"{k}={v}" for k, v in cmds.most_common()))
        else:
            lines.append("usage: (no telemetry file)")
    return _text("\n".join(lines))


HANDLERS = {
    "memory_query": tool_memory_query,
    "memory_get": tool_memory_get,
    "memory_stats": tool_memory_stats,
}


def handle(msg: dict):
    mid = msg.get("id")
    method = msg.get("method", "")
    params = msg.get("params") or {}

    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        }}
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        name = params.get("name", "")
        fn = HANDLERS.get(name)
        if fn is None:
            return {"jsonrpc": "2.0", "id": mid, "result": _text(f"unknown tool: {name}", True)}
        try:
            result = fn(params.get("arguments") or {})
        except Exception as exc:  # noqa: BLE001 — MCP must return errors, not crash stdio
            return {"jsonrpc": "2.0", "id": mid, "result": _text(f"error: {exc}", True)}
        return {"jsonrpc": "2.0", "id": mid, "result": result}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    return {"jsonrpc": "2.0", "id": mid,
            "error": {"code": -32601, "message": f"unknown method: {method}"}}


def main() -> int:
    stdin = sys.stdin
    stdout = sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(msg)
        if resp is not None:
            stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
