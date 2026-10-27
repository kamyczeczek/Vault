#!/usr/bin/env python3
"""Model Context Protocol (MCP) server for the agentic-research-lab knowledge graph.

Exposes local SQLite FTS5 knowledge graph queries over stdio JSON-RPC so any
MCP-compatible client (Claude Desktop, Cursor, etc.) can query the 2,830+ node
research corpus directly.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "knowledge" / "graph"))

from ask import query, get_neighbors, evidence_spans, DB
from session_store import search as search_sessions, timeline as session_timeline, verify_chain
from session_graph import search_events as search_session_graph, neighbors as session_neighbors, PROJECTION_DB
from context_gateway import context_packet


def handle_request(line: str) -> str | None:
    try:
        req = json.loads(line)
    except json.JSONDecodeError:
        return None

    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "agentic-research-lab-mcp", "version": "1.0.0"}
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": [
                    {
                        "name": "query_knowledge",
                        "description": "Query the agentic research knowledge graph using full-text search (FTS5) and RRF ranking.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string", "description": "Search query or research question"},
                                "limit": {"type": "integer", "description": "Max results to return (default 5)", "default": 5},
                                "tags": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Optional tag filters"
                                }
                            },
                            "required": ["question"]
                        }
                    },
                    {
                        "name": "get_neighbors",
                        "description": "Retrieve connected graph chunks for a given node ID, ordered by edge confidence.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "node_id": {"type": "string", "description": "Corpus chunk ID (e.g. 00_mcp_second_brains)"},
                                "limit": {"type": "integer", "description": "Max neighbors to return (default 5)", "default": 5}
                            },
                            "required": ["node_id"]
                        }
                    },
                    {
                        "name": "get_evidence_spans",
                        "description": "Fetch small section-aware evidence spans for one corpus node without loading its full body.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "node_id": {"type": "string"},
                                "question": {"type": "string"},
                                "limit": {"type": "integer", "default": 2},
                                "max_chars": {"type": "integer", "default": 1400}
                            },
                            "required": ["node_id", "question"]
                        }
                    },
                    {
                        "name": "query_sessions",
                        "description": "Search redacted, append-only agent session events without loading full transcripts.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "limit": {"type": "integer", "default": 10}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "get_session_timeline",
                        "description": "Retrieve the ordered event timeline for one session.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"session_id": {"type": "string"}},
                            "required": ["session_id"]
                        }
                    },
                    {
                        "name": "verify_session_chain",
                        "description": "Verify event ordering and hash-chain integrity for one session.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"session_id": {"type": "string"}},
                            "required": ["session_id"]
                        }
                    },
                    {
                        "name": "query_session_graph",
                        "description": "Search the rebuildable session graph with optional workspace scope.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "workspace": {"type": "string"},
                                "limit": {"type": "integer", "default": 10}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "get_session_graph_neighbors",
                        "description": "Retrieve bounded typed relationships from the projected session graph.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "node_id": {"type": "string"},
                                "limit": {"type": "integer", "default": 10}
                            },
                            "required": ["node_id"]
                        }
                    },
                    {
                        "name": "get_context_packet",
                        "description": "Retrieve bounded corpus and session evidence under a fixed token budget.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string"},
                                "mode": {"type": "string", "enum": ["fast", "default", "deep"], "default": "default"},
                                "limit": {"type": "integer", "default": 5},
                                "workspace": {"type": "string"}
                            },
                            "required": ["question"]
                        }
                    }
                ]
            }
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "query_knowledge":
            question = arguments.get("question", "")
            limit = int(arguments.get("limit", 5))
            tags = arguments.get("tags")
            results = query(question, limit=limit, tags=tags)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(results, indent=2)}]
                }
            })

        if tool_name == "get_neighbors":
            node_id = arguments.get("node_id", "")
            limit = int(arguments.get("limit", 5))
            nbrs = get_neighbors(node_id, limit=limit)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(nbrs, indent=2)}]
                }
            })

        if tool_name == "get_evidence_spans":
            spans = evidence_spans(
                arguments.get("node_id", ""),
                arguments.get("question", ""),
                limit=int(arguments.get("limit", 2)),
                max_chars=int(arguments.get("max_chars", 1400)),
            )
            return json.dumps({"jsonrpc": "2.0", "id": msg_id,
                               "result": {"content": [{"type": "text", "text": json.dumps(spans, indent=2)}]}})

        if tool_name == "query_sessions":
            results = search_sessions(arguments.get("query", ""), limit=int(arguments.get("limit", 10)))
            return json.dumps({"jsonrpc": "2.0", "id": msg_id,
                               "result": {"content": [{"type": "text", "text": json.dumps(results, indent=2)}]}})

        if tool_name == "get_session_timeline":
            results = session_timeline(arguments.get("session_id", ""))
            return json.dumps({"jsonrpc": "2.0", "id": msg_id,
                               "result": {"content": [{"type": "text", "text": json.dumps(results, indent=2)}]}})

        if tool_name == "verify_session_chain":
            ok, message = verify_chain(arguments.get("session_id", ""))
            return json.dumps({"jsonrpc": "2.0", "id": msg_id,
                               "result": {"content": [{"type": "text", "text": json.dumps({"ok": ok, "message": message})}]}})

        if tool_name == "query_session_graph":
            results = search_session_graph(
                arguments.get("query", ""),
                limit=int(arguments.get("limit", 10)),
                workspace=arguments.get("workspace"),
                path=PROJECTION_DB,
            )
            return json.dumps({"jsonrpc": "2.0", "id": msg_id,
                               "result": {"content": [{"type": "text", "text": json.dumps(results, indent=2)}]}})

        if tool_name == "get_session_graph_neighbors":
            results = session_neighbors(
                arguments.get("node_id", ""),
                limit=int(arguments.get("limit", 10)),
                path=PROJECTION_DB,
            )
            return json.dumps({"jsonrpc": "2.0", "id": msg_id,
                               "result": {"content": [{"type": "text", "text": json.dumps(results, indent=2)}]}})

        if tool_name == "get_context_packet":
            result = context_packet(
                arguments.get("question", ""),
                mode=arguments.get("mode", "default"),
                limit=int(arguments.get("limit", 5)),
                workspace=arguments.get("workspace"),
                session_graph_path=PROJECTION_DB,
            )
            return json.dumps({"jsonrpc": "2.0", "id": msg_id,
                               "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}})

        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
        })

    return None


def main() -> int:
    if not DB.exists():
        print("Error: graph.db missing — run build_graph.py first", file=sys.stderr)
        return 1

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        res = handle_request(line)
        if res:
            print(res)
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
