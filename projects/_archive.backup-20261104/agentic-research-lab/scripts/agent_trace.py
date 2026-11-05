"""Typed execution trace records for agent work.

The trace is operational evidence, separate from the durable knowledge graph. Records
use stable IDs and graph-generation references so retrievals and artifacts can be
replayed without promoting runtime noise into corpus knowledge.
"""
from __future__ import annotations
import hashlib, json, os, time, uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = ROOT / "reflection" / "trace"
TRACE_FILE = TRACE_DIR / "events.jsonl"
SESSIONS_FILE = TRACE_DIR / "sessions.jsonl"
CONTEXT_FILE = TRACE_DIR / "current_run.json"
GENERATION = ROOT / "knowledge" / "graph" / "generation.json"


def generation_id() -> str:
    try:
        return str(json.loads(GENERATION.read_text(encoding="utf-8"))["generation_id"])
    except (OSError, ValueError, KeyError):
        return ""


def new_run_id(prefix: str = "run") -> str:
    run_id = f"{prefix}-{uuid.uuid4().hex[:16]}"
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    CONTEXT_FILE.write_text(json.dumps({"run_id": run_id, "graph_generation": generation_id()}), encoding="utf-8")
    return run_id


def event_id(kind: str, payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode()
    return f"{kind}-{hashlib.sha256(body).hexdigest()[:16]}"


def emit(kind: str, *, run_id: str | None = None, parent_id: str | None = None,
         status: str = "observed",
         model_id: str | None = None,
         input_tokens: int | None = None, output_tokens: int | None = None,
         cached_tokens: int | None = None,
         started_at: float | None = None, ended_at: float | None = None,
         path: str | None = None,
         **fields: Any) -> str:
    """Append a typed trace event. Cost/instrumentation fields are all
    nullable and dropped when None: absent means unlogged, never zero.
    `path` tags eval runs as success_path vs exploration (direct/loaded
    split); omit it everywhere else.
    """
    run_id = run_id or os.environ.get("AGENT_TRACE_RUN_ID", "")
    if not run_id and CONTEXT_FILE.exists():
        try:
            run_id = json.loads(CONTEXT_FILE.read_text(encoding="utf-8")).get("run_id", "")
        except (OSError, ValueError):
            run_id = ""
    payload = {"kind": kind, "run_id": run_id,
               "parent_id": parent_id, "status": status, "graph_generation": generation_id(),
               "timestamp": time.time(),
               "model_id": model_id, "input_tokens": input_tokens,
               "output_tokens": output_tokens, "cached_tokens": cached_tokens,
               "started_at": started_at, "ended_at": ended_at, "path": path,
               **fields}
    payload = {k: v for k, v in payload.items() if v is not None}
    payload["event_id"] = event_id(kind, payload)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    with TRACE_FILE.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
    return payload["event_id"]


def session_open(session_id: str, model_id: str | None = None) -> str:
    """Open a session record. All cost fields nullable; absent means unlogged."""
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    row = {"session_id": session_id, "model_id": model_id,
           "started_at": time.time(), "graph_generation": generation_id()}
    row = {k: v for k, v in row.items() if v is not None}
    with SESSIONS_FILE.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return session_id


def session_close(session_id: str, total_tokens: int | None = None,
                  wall_clock_minutes: float | None = None) -> None:
    """Close a session record. Never coalesce to zero."""
    row = {"session_id": session_id, "total_tokens": total_tokens,
           "wall_clock_minutes": wall_clock_minutes, "closed_at": time.time()}
    row = {k: v for k, v in row.items() if v is not None}
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    with SESSIONS_FILE.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
