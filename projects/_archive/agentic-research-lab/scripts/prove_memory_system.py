#!/usr/bin/env python3
"""Run reproducible acceptance proofs for the workspace-memory foundation.

The proof uses temporary authoritative stores and checks observable contracts. It
never mutates the repository's corpus, frontier, session, or projection files.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "knowledge" / "graph"
if str(GRAPH) not in sys.path:
    sys.path.insert(0, str(GRAPH))

import context_gateway as gateway  # noqa: E402
from context_gateway import context_packet  # noqa: E402
from mcp_server import handle_request  # noqa: E402
from session_graph import project  # noqa: E402
from session_store import (  # noqa: E402
    RETENTION_DELETE_CONFIRMATION,
    append_event,
    execute_retention_cleanup,
    record_artifact,
    start_session,
    timeline,
    verify_chain,
)
from frontier_state import build_manifest, load_ledger, validate_ledger, replay  # noqa: E402


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rpc(method: str, params: dict, request_id: int) -> dict:
    response = handle_request(json.dumps({"jsonrpc": "2.0", "id": request_id,
                                          "method": method, "params": params}))
    check(response is not None, f"no MCP response for {method}")
    value = json.loads(response)
    check(value.get("jsonrpc") == "2.0" and value.get("id") == request_id,
          f"invalid MCP envelope for {method}")
    return value


def main() -> int:
    proofs: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="memory-proof-") as raw:
        root = Path(raw)
        source = root / "sessions.db"
        projection = root / "session_graph.db"
        frontier = root / "frontier"
        frontier.mkdir()
        memory = root / "memory.md"

        sid_one = start_session("proof-one", path=source, session_id="proof-s1")
        sid_two = start_session("proof-two", path=source, session_id="proof-s2")
        event_id = append_event(sid_one, "note", {"message": "retrieval proof", "api_key": "hidden"}, path=source)
        append_event(sid_one, "followup", {"message": "chain proof"}, path=source)
        artifact_one = record_artifact(sid_one, "tmp/proof.log", db_path=source)
        artifact_two = record_artifact(sid_two, "tmp/other.log", db_path=source)

        event_payload = timeline(sid_one, path=source)[0]["payload"]
        check("hidden" not in event_payload and "REDACTED" in event_payload, "secret redaction failed")
        proofs.append({"id": "privacy-redaction", "status": "pass", "evidence": "secret value absent from authoritative event payload"})
        chain_ok, chain_message = verify_chain(sid_one, path=source)
        check(chain_ok and chain_message == "ok", "session hash chain verification failed")
        proofs.append({"id": "session-hash-chain", "status": "pass", "evidence": chain_message})

        try:
            record_artifact(sid_one, "config/.env", db_path=source)
        except ValueError:
            proofs.append({"id": "sensitive-path-rejection", "status": "pass", "evidence": "sensitive artifact rejected before persistence"})
        else:
            raise AssertionError("sensitive artifact path was accepted")

        projected = project(source, projection)
        check(projected["counts"]["sessions"] == 2 and projected["counts"]["events"] == 2,
              "projection counts do not match source")
        first_fingerprint = projected["source_fingerprint"]
        projection.unlink()
        projected_again = project(source, projection)
        check(projected_again["source_fingerprint"] == first_fingerprint and projected_again["counts"] == projected["counts"],
              "projection rebuild was not deterministic")
        proofs.append({"id": "projection-rebuild", "status": "pass", "evidence": json.dumps(projected["counts"], sort_keys=True)})

        packet = context_packet("proof log", mode="fast", workspace="proof-one",
                               session_graph_path=projection, frontier_dir=root / "missing-frontier",
                               memory_path=root / "missing-memory.md")
        artifact_ids = {item["id"] for item in packet["items"] if item["kind"] == "artifact"}
        check(artifact_one in artifact_ids and artifact_two not in artifact_ids, "workspace isolation failed")
        check(packet["estimated_tokens"] <= packet["token_budget"], "context budget exceeded")
        proofs.append({"id": "workspace-and-budget", "status": "pass",
                       "evidence": f"selected={sorted(artifact_ids)} estimated={packet['estimated_tokens']} budget={packet['token_budget']}"})

        denied = False
        try:
            execute_retention_cleanup(older_than_days=0, db_path=source)
        except PermissionError:
            denied = True
        check(denied, "cleanup was not authorization gated")
        deleted = execute_retention_cleanup(
            older_than_days=0, tier="ephemeral", workspace="proof-one",
            confirmation=RETENTION_DELETE_CONFIRMATION, db_path=source,
        )
        check(deleted == [artifact_one], "authorized cleanup deleted the wrong artifacts")
        remaining_events = timeline(sid_one, path=source)
        check(len(remaining_events) == 2 and remaining_events[0]["event_id"] == event_id,
              "cleanup deleted session events")
        proofs.append({"id": "retention-authorization", "status": "pass", "evidence": f"deleted={deleted}"})

        ledger = b""
        (frontier / "ledger.jsonl").write_bytes(ledger)
        manifest = build_manifest([], ledger, 200)
        (frontier / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        memory.write_text("### proof-rule — accepted\n\nUse bounded proof evidence.\n", encoding="utf-8")
        valid_packet = context_packet("proof evidence", mode="deep", frontier_dir=frontier, memory_path=memory,
                                      session_graph_path=root / "missing-session-graph")
        frontier_items = [item for item in valid_packet["items"] if item["kind"] == "frontier"]
        check(frontier_items and frontier_items[0]["integrity"] == "valid", "valid frontier was not admitted")
        check(any(item["kind"] == "lesson" for item in valid_packet["items"]), "accepted lesson was not retrieved")
        proofs.append({"id": "frontier-integrity-and-lesson", "status": "pass", "evidence": "valid frontier and accepted lesson admitted"})

        malformed = b'{"record_type":"turn"}\n'
        (frontier / "ledger.jsonl").write_bytes(malformed)
        (frontier / "manifest.json").write_text(json.dumps({"ledger_sha256": hashlib.sha256(malformed).hexdigest(),
                                                              "ledger_line_count": 1}), encoding="utf-8")
        original_query, original_search = gateway.query, gateway.search_events
        gateway.query = lambda *_args, **_kwargs: []
        gateway.search_events = lambda *_args, **_kwargs: []
        try:
            blocked = context_packet("frontier", mode="fast", frontier_dir=frontier,
                                    memory_path=root / "missing-memory.md",
                                    session_graph_path=root / "missing-session-graph")
        finally:
            gateway.query, gateway.search_events = original_query, original_search
        check(any(item["kind"] == "frontier_integrity" for item in blocked["items"]),
              "invalid frontier was not fail-closed")
        check(not any(item["kind"] == "frontier" and item.get("integrity") != "valid" for item in blocked["items"]),
              "invalid frontier record entered normal context")
        proofs.append({"id": "frontier-fail-closed", "status": "pass", "evidence": "invalid frontier withheld and diagnostic returned"})

        try:
            records, raw, _ = load_ledger(frontier)
            canonical_errors = validate_ledger(records, raw)
        except Exception as error:
            canonical_errors = [str(error)]
        check(canonical_errors, "malformed frontier unexpectedly passed canonical validation")
        check(replay([])["open_turn_ids"] == [], "frontier replay empty-state proof failed")

    listed = rpc("tools/list", {}, 1)
    tool_names = {tool["name"] for tool in listed["result"]["tools"]}
    check("get_context_packet" in tool_names, "MCP context tool missing")
    initialized = rpc("initialize", {}, 2)
    check(initialized["result"]["protocolVersion"] == "2024-11-05", "MCP initialize contract failed")
    called = rpc("tools/call", {"name": "get_context_packet",
                                 "arguments": {"question": "retrieval", "mode": "fast", "limit": 1}}, 3)
    content = called.get("result", {}).get("content", [])
    check(content and content[0].get("type") == "text", "MCP context call returned no text content")
    packet = json.loads(content[0]["text"])
    check(packet["estimated_tokens"] <= packet["token_budget"], "MCP context call exceeded its budget")
    proofs.append({"id": "mcp-protocol", "status": "pass", "evidence": "initialize, tools/list, and get_context_packet JSON-RPC contracts passed"})

    print(json.dumps({"proof_suite": "workspace-memory-foundation", "status": "pass", "proofs": proofs}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
