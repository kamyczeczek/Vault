#!/usr/bin/env python3
"""Deterministic, append-only live-frontier ledger.

The JSONL file is the source of truth.  ``manifest.json`` is the only compacted
mutable index and is rebuilt from physical ledger order after every mutation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FRONTIER = ROOT / "frontier"
DEFAULT_OPEN_TURN_BOUND = 200
SCHEMA_VERSION = 1
COMMIT_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")
VALID_RECORD_TYPES = {"turn", "close", "compaction", "rollback"}
VALID_STATUSES = {"open", "closed", "rolled_back"}
REQUIRED_FIELDS = {
    "record_type", "session_id", "turn_id", "timestamp", "parent_turn_id",
    "parent_session_id", "turn_type", "model", "subagent_of", "issue_ids",
    "depends_on", "verifier", "next_action", "status",
}


class FrontierError(Exception):
    """Raised for an invalid frontier operation or invariant."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_bytes(value: Any) -> bytes:
    return (canonical_json(value) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_timestamp(value: str | None) -> str:
    value = value or utc_now()
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as error:
        raise FrontierError(f"invalid timestamp {value!r}") from error
    if parsed.tzinfo is None:
        raise FrontierError("timestamp must include a timezone")
    return parsed.isoformat()


def nonempty(value: Any, field: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise FrontierError(f"{field} must be a non-empty string")
    return value


def string_list(value: Iterable[str] | None, field: str) -> list[str]:
    if value is None:
        return []
    result = [nonempty(item, field) or "" for item in value]
    if len(result) != len(set(result)):
        raise FrontierError(f"{field} contains duplicate values")
    return result


def parse_id_list(value: str | None) -> list[str]:
    if not value:
        return []
    return string_list((part.strip() for part in value.split(",") if part.strip()), "id list")


def parse_json(value: str | None, field: str) -> Any:
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as error:
        raise FrontierError(f"invalid JSON for {field}: {error.msg}") from error


def verifier(value: Any) -> dict[str, Any]:
    """Return the canonical verifier object, rejecting any other shape."""
    if value is None:
        value = {"name": "", "exit": None, "fingerprint": ""}
    if not isinstance(value, dict) or set(value) != {"name", "exit", "fingerprint"}:
        raise FrontierError("verifier must contain exactly name, exit, and fingerprint")
    if not isinstance(value["name"], str) or not isinstance(value["fingerprint"], str):
        raise FrontierError("verifier name and fingerprint must be strings")
    exit_code = value["exit"]
    if exit_code is not None and (isinstance(exit_code, bool) or not isinstance(exit_code, int)):
        raise FrontierError("verifier exit must be an integer or null")
    return {"name": value["name"], "exit": exit_code, "fingerprint": value["fingerprint"]}


def turn_record(
    *,
    session_id: str,
    turn_id: str,
    timestamp: str | None,
    parent_turn_id: str | None,
    parent_session_id: str | None,
    turn_type: str,
    model: str,
    subagent_of: str | None,
    issue_ids: Iterable[str],
    depends_on: Iterable[str],
    verifier_value: Any,
    next_action: str,
    status: str = "open",
) -> dict[str, Any]:
    if status not in VALID_STATUSES:
        raise FrontierError(f"invalid status: {status}")
    return {
        "record_type": "turn",
        "session_id": nonempty(session_id, "session_id") or "",
        "turn_id": nonempty(turn_id, "turn_id") or "",
        "timestamp": parse_timestamp(timestamp),
        "parent_turn_id": nonempty(parent_turn_id, "parent_turn_id", optional=True),
        "parent_session_id": nonempty(parent_session_id, "parent_session_id", optional=True),
        "turn_type": nonempty(turn_type, "turn_type") or "",
        "model": model if isinstance(model, str) else str(model),
        "subagent_of": nonempty(subagent_of, "subagent_of", optional=True),
        "issue_ids": string_list(issue_ids, "issue_ids"),
        "depends_on": string_list(depends_on, "depends_on"),
        "verifier": verifier(verifier_value),
        "next_action": next_action if isinstance(next_action, str) else str(next_action),
        "status": status,
    }


def control_record(
    *,
    record_type: str,
    records: list[dict[str, Any]],
    timestamp: str | None,
    session_id: str,
    turn_id: str | None,
    parent_turn_id: str | None,
    parent_session_id: str | None,
    turn_type: str,
    model: str,
    subagent_of: str | None,
    issue_ids: Iterable[str],
    depends_on: Iterable[str],
    verifier_value: Any,
    next_action: str,
    status: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    if record_type not in {"close", "compaction", "rollback"}:
        raise FrontierError(f"invalid control record type: {record_type}")
    event_id = metadata.pop("event_id", _next_event_id(record_type, records))
    record = turn_record(
        session_id=session_id,
        turn_id=turn_id or event_id,
        timestamp=timestamp,
        parent_turn_id=parent_turn_id,
        parent_session_id=parent_session_id,
        turn_type=turn_type,
        model=model,
        subagent_of=subagent_of,
        issue_ids=issue_ids,
        depends_on=depends_on,
        verifier_value=verifier_value,
        next_action=next_action,
        status=status,
    )
    record["record_type"] = record_type
    record["event_id"] = event_id
    record.update(metadata)
    return record


def ledger_path(frontier_dir: Path = DEFAULT_FRONTIER) -> Path:
    return frontier_dir / "ledger.jsonl"


def manifest_path(frontier_dir: Path = DEFAULT_FRONTIER) -> Path:
    return frontier_dir / "manifest.json"


def load_ledger(frontier_dir: Path = DEFAULT_FRONTIER) -> tuple[list[dict[str, Any]], bytes, list[str]]:
    path = ledger_path(frontier_dir)
    if not path.exists():
        return [], b"", []
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise FrontierError(f"ledger is not UTF-8: {error}") from error
    if raw and (not raw.endswith(b"\n") or any(b"\r" in line for line in raw.splitlines())):
        raise FrontierError("ledger must use UTF-8 LF-terminated lines")
    lines = text.splitlines()
    records: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            raise FrontierError(f"blank ledger line {number}")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise FrontierError(f"invalid JSON on ledger line {number}: {error.msg}") from error
        if not isinstance(value, dict):
            raise FrontierError(f"ledger line {number} is not an object")
        records.append(value)
    return records, raw, lines


def read_ledger(frontier_dir: Path = DEFAULT_FRONTIER) -> list[dict[str, Any]]:
    return load_ledger(frontier_dir)[0]


def read_manifest(frontier_dir: Path = DEFAULT_FRONTIER) -> dict[str, Any] | None:
    path = manifest_path(frontier_dir)
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FrontierError(f"cannot read manifest: {error}") from error
    if not isinstance(value, dict):
        raise FrontierError("manifest root must be an object")
    return value


def ledger_bytes(frontier_dir: Path = DEFAULT_FRONTIER) -> bytes:
    path = ledger_path(frontier_dir)
    return path.read_bytes() if path.exists() else b""


def replay(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Replay the physical event stream into the current frontier."""
    turns: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    close_events: list[dict[str, Any]] = []
    rollback_events: list[dict[str, Any]] = []
    compaction_events: list[dict[str, Any]] = []
    for record in records:
        kind = record.get("record_type")
        if kind == "turn":
            turn_id = record.get("turn_id")
            if turn_id in turns:
                raise FrontierError(f"duplicate turn_id: {turn_id}")
            turns[turn_id] = dict(record)
            order.append(turn_id)
        elif kind == "close":
            close_events.append(dict(record))
            target = record.get("turn_id")
            if target not in turns:
                raise FrontierError(f"close references unknown turn: {target}")
            turns[target].update(
                status="closed",
                next_action=record.get("next_action", turns[target].get("next_action", "")),
            )
            turns[target]["verifier"] = verifier(record.get("verifier", turns[target].get("verifier")))
        elif kind == "rollback":
            rollback_events.append(dict(record))
            target = record.get("reverted_to_turn")
            if target not in turns:
                raise FrontierError(f"rollback references unknown turn: {target}")
            start = order.index(target)
            for turn_id in order[start + 1:]:
                turns[turn_id]["status"] = "rolled_back"
            turns[target].update(
                status="open",
                next_action=record.get("next_action", turns[target].get("next_action", "")),
            )
        elif kind == "compaction":
            compaction_events.append(dict(record))
        else:
            raise FrontierError(f"unknown record_type: {kind!r}")

    open_ids = [turn_id for turn_id in order if turns[turn_id].get("status") == "open"]
    closed_ids = [turn_id for turn_id in order if turns[turn_id].get("status") == "closed"]
    rolled_back_ids = [turn_id for turn_id in order if turns[turn_id].get("status") == "rolled_back"]
    return {
        "turns": turns,
        "order": order,
        "open_turn_ids": open_ids,
        "closed_turn_ids": closed_ids,
        "rolled_back_turn_ids": rolled_back_ids,
        "active_turn_ids": open_ids,
        "verifier_state": {turn_id: turns[turn_id]["verifier"] for turn_id in order},
        "close_events": close_events,
        "rollback_events": rollback_events,
        "compaction_events": compaction_events,
    }


def build_manifest(records: list[dict[str, Any]], raw: bytes, bound: int) -> dict[str, Any]:
    if bound < 1:
        raise FrontierError("open_turn_bound must be at least 1")
    state = replay(records)
    return {
        "schema_version": SCHEMA_VERSION,
        "open_turn_bound": bound,
        "ledger_sha256": sha256_bytes(raw),
        "ledger_line_count": len(records),
        "latest_sequence": len(records),
        "turns": state["turns"],
        "order": state["order"],
        "active_turn_ids": state["active_turn_ids"],
        "open_turn_ids": state["open_turn_ids"],
        "closed_turn_ids": state["closed_turn_ids"],
        "rolled_back_turn_ids": state["rolled_back_turn_ids"],
        "verifier_state": state["verifier_state"],
        "close_events": state["close_events"],
        "rollback_events": state["rollback_events"],
        "compaction_events": state["compaction_events"],
        "open_turn_count": len(state["open_turn_ids"]),
        "bound_ok": len(state["open_turn_ids"]) <= bound,
    }


def validate_ledger(records: list[dict[str, Any]], raw: bytes | None = None) -> list[str]:
    """Validate physical encoding, schema, and cross-record invariants."""
    errors: list[str] = []
    if raw is not None:
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as error:
            errors.append(f"ledger is not UTF-8: {error}")
        if raw and (not raw.endswith(b"\n") or any(b"\r" in line for line in raw.splitlines())):
            errors.append("ledger must use UTF-8 LF-terminated lines")
        physical = raw.decode("utf-8", errors="replace").splitlines() if raw else []
        if len(physical) != len(records):
            errors.append("ledger physical line count does not match parsed records")

    seen: dict[str, dict[str, Any]] = {}
    current_status: dict[str, str] = {}
    order: list[str] = []
    event_ids: set[str] = set()
    for index, record in enumerate(records, 1):
        if not isinstance(record, dict):
            errors.append(f"line {index}: record is not an object")
            continue
        missing = REQUIRED_FIELDS - set(record)
        if missing:
            errors.append(f"line {index}: missing fields {sorted(missing)}")
            continue
        kind = record.get("record_type")
        if kind not in VALID_RECORD_TYPES:
            errors.append(f"line {index}: invalid record_type {kind!r}")
            continue
        try:
            parse_timestamp(record.get("timestamp"))
            verifier(record.get("verifier"))
        except FrontierError as error:
            errors.append(f"line {index}: {error}")
        for field in ("session_id", "turn_id", "turn_type"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                errors.append(f"line {index}: {field} must be non-empty")
        if not isinstance(record.get("model"), str) or not isinstance(record.get("next_action"), str):
            errors.append(f"line {index}: model and next_action must be strings")
        if record.get("status") not in VALID_STATUSES:
            errors.append(f"line {index}: invalid status")
        for field in ("parent_turn_id", "parent_session_id", "subagent_of"):
            if record.get(field) is not None and (not isinstance(record[field], str) or not record[field].strip()):
                errors.append(f"line {index}: {field} must be null or non-empty")
        for field in ("issue_ids", "depends_on"):
            value = record.get(field)
            if (not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value)
                    or len(value) != len(set(value))):
                errors.append(f"line {index}: {field} must be unique non-empty strings")

        turn_id = record.get("turn_id")
        if kind == "turn":
            if turn_id in seen:
                errors.append(f"line {index}: duplicate turn_id {turn_id!r}")
            seen[turn_id] = record
            current_status[turn_id] = record.get("status", "open")
            order.append(turn_id)
        else:
            event_id = record.get("event_id")
            if (not isinstance(event_id, str) or not event_id
                    or event_id in event_ids or not event_id.startswith(f"{kind}-")):
                errors.append(f"line {index}: invalid or duplicate event_id")
            else:
                event_ids.add(event_id)

        parent = record.get("parent_turn_id")
        if parent is not None:
            if parent not in seen or (record.get("parent_session_id") is not None
                                      and record["parent_session_id"] != seen[parent].get("session_id")):
                errors.append(f"line {index}: invalid parent reference")
        elif record.get("parent_session_id") is not None:
            errors.append(f"line {index}: parent_session_id requires parent_turn_id")

        if kind == "close":
            if turn_id not in seen or current_status.get(turn_id) != "open":
                errors.append(f"line {index}: close target is not open")
            else:
                current_status[turn_id] = "closed"
        elif kind == "rollback":
            target = record.get("reverted_to_turn")
            commit = record.get("git_commit")
            if target not in seen:
                errors.append(f"line {index}: rollback target is unknown")
            elif current_status.get(target) != "open":
                errors.append(f"line {index}: rollback target is not open")
            else:
                start = order.index(target)
                for later in order[start + 1:]:
                    current_status[later] = "rolled_back"
                current_status[target] = "open"
            if commit is not None and (not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit)):
                errors.append(f"line {index}: invalid git_commit")
        elif kind == "compaction":
            compacted = record.get("compacted_turn_ids")
            if (not isinstance(compacted, list)
                    or any(item not in seen
                           or current_status.get(item) not in {"closed", "rolled_back"}
                           for item in compacted)):
                errors.append(f"line {index}: invalid compacted_turn_ids")
    return errors


def validate_manifest(records: list[dict[str, Any]], raw: bytes, manifest: dict[str, Any], bound: int) -> list[str]:
    try:
        expected = build_manifest(records, raw, bound)
    except FrontierError as error:
        return [str(error)]
    return [f"manifest {field} does not match replay" for field in expected if manifest.get(field) != expected[field]]


def inspect_frontier(frontier_dir: Path = DEFAULT_FRONTIER,
                     open_turn_bound: int = DEFAULT_OPEN_TURN_BOUND) -> dict[str, Any]:
    """Load, validate, and read the manifest through one canonical path.

    Every reader (status, rebuild_manifest, check_frontier, recover, the
    gateway) must go through this so the two artifacts' consistency rules and
    the canonical validators cannot drift apart.  Raises FrontierError on
    inconsistent artifacts or invalid records; a missing-but-consistent pair
    is reported with ``present=False`` rather than as an error.
    """
    ledger_exists, manifest_exists = _artifact_state(frontier_dir)
    if not ledger_exists and not manifest_exists:
        return {"present": False, "records": [], "raw": b"", "manifest": None, "errors": []}
    if ledger_exists != manifest_exists:
        raise FrontierError("frontier has only one of ledger.jsonl and manifest.json")
    records, raw, _ = load_ledger(frontier_dir)
    errors = validate_ledger(records, raw)
    manifest = read_manifest(frontier_dir)
    if manifest is None:
        errors.append("manifest is missing")
    else:
        errors.extend(validate_manifest(records, raw, manifest, open_turn_bound))
    return {"present": True, "records": records, "raw": raw, "manifest": manifest, "errors": errors}

def ensure_frontier(frontier_dir: Path) -> None:
    frontier_dir.mkdir(parents=True, exist_ok=True)
    (ROOT / ".unlazy" / "backups").mkdir(parents=True, exist_ok=True)


def backup_file(path: Path) -> None:
    if path.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        shutil.copy2(path, ROOT / ".unlazy" / "backups" / f"{stamp}_{path.name}")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _next_event_id(kind: str, records: list[dict[str, Any]]) -> str:
    return f"{kind}-{len(records) + 1:06d}"


def append_record(record: dict[str, Any], frontier_dir: Path = DEFAULT_FRONTIER) -> dict[str, Any]:
    ensure_frontier(frontier_dir)
    path = ledger_path(frontier_dir)
    records, raw, _ = load_ledger(frontier_dir)
    candidate_raw = raw + canonical_bytes(record)
    errors = validate_ledger(records + [record], candidate_raw)
    if errors:
        raise FrontierError("; ".join(errors))
    backup_file(path)
    with path.open("ab") as stream:
        stream.write(canonical_bytes(record))
        stream.flush()
        os.fsync(stream.fileno())
    return record


def rebuild_manifest(frontier_dir: Path = DEFAULT_FRONTIER, bound: int = DEFAULT_OPEN_TURN_BOUND) -> dict[str, Any]:
    records, raw, _ = load_ledger(frontier_dir)
    errors = validate_ledger(records, raw)
    if errors:
        raise FrontierError("; ".join(errors))
    manifest = build_manifest(records, raw, bound)
    backup_file(manifest_path(frontier_dir))
    atomic_write(manifest_path(frontier_dir), canonical_bytes(manifest))
    return manifest


def _artifact_state(frontier_dir: Path) -> tuple[bool, bool]:
    return ledger_path(frontier_dir).exists(), manifest_path(frontier_dir).exists()


def initialize(frontier_dir: Path = DEFAULT_FRONTIER) -> None:
    ledger_exists, manifest_exists = _artifact_state(frontier_dir)
    if not ledger_exists and not manifest_exists:
        ensure_frontier(frontier_dir)
        atomic_write(ledger_path(frontier_dir), b"")
        rebuild_manifest(frontier_dir)
    elif ledger_exists != manifest_exists:
        raise FrontierError("frontier has only one of ledger.jsonl and manifest.json")


def empty_status(bound: int = DEFAULT_OPEN_TURN_BOUND) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "open_turn_bound": bound,
        "open_turn_count": 0,
        "bound_ok": True,
        "active_turn_ids": [],
        "verifier_state": {},
        "close_events": [],
        "rollback_events": [],
        "compaction_events": [],
        "ledger_line_count": 0,
    }


def status(frontier_dir: Path = DEFAULT_FRONTIER, open_turn_bound: int = DEFAULT_OPEN_TURN_BOUND) -> dict[str, Any]:
    view = inspect_frontier(frontier_dir, open_turn_bound)
    if not view["present"]:
        return empty_status(open_turn_bound)
    if view["errors"]:
        raise FrontierError("; ".join(view["errors"]))
    records = view["records"]
    state = replay(records)
    return {
        "schema_version": SCHEMA_VERSION,
        "open_turn_bound": open_turn_bound,
        "open_turn_count": len(state["open_turn_ids"]),
        "bound_ok": len(state["open_turn_ids"]) <= open_turn_bound,
        "active_turn_ids": state["active_turn_ids"],
        "verifier_state": state["verifier_state"],
        "close_events": state["close_events"],
        "rollback_events": state["rollback_events"],
        "compaction_events": state["compaction_events"],
        "ledger_line_count": len(records),
    }


def open_turn(
    *, session_id: str, turn_id: str, timestamp: str | None = None,
    parent_turn_id: str | None = None, parent_session_id: str | None = None,
    turn_type: str = "agent", model: str = "", subagent_of: str | None = None,
    issue_ids: Iterable[str] = (), depends_on: Iterable[str] = (),
    verifier_value: Any = None, next_action: str = "",
    frontier_dir: Path = DEFAULT_FRONTIER, open_turn_bound: int = DEFAULT_OPEN_TURN_BOUND,
) -> dict[str, Any]:
    initialize(frontier_dir)
    records = read_ledger(frontier_dir)
    state = replay(records)
    if turn_id in state["turns"]:
        raise FrontierError(f"turn_id already exists: {turn_id}")
    if len(state["open_turn_ids"]) >= open_turn_bound:
        raise FrontierError(f"open-turn bound reached ({open_turn_bound})")
    record = turn_record(session_id=session_id, turn_id=turn_id, timestamp=timestamp,
                         parent_turn_id=parent_turn_id, parent_session_id=parent_session_id,
                         turn_type=turn_type, model=model, subagent_of=subagent_of,
                         issue_ids=issue_ids, depends_on=depends_on, verifier_value=verifier_value,
                         next_action=next_action, status="open")
    append_record(record, frontier_dir)
    rebuild_manifest(frontier_dir, open_turn_bound)
    return record


def close_turn(
    *, turn_id: str, timestamp: str | None = None, session_id: str | None = None,
    parent_turn_id: str | None = None, parent_session_id: str | None = None,
    turn_type: str = "close", model: str = "", subagent_of: str | None = None,
    issue_ids: Iterable[str] = (), depends_on: Iterable[str] = (),
    verifier_value: Any = None, next_action: str = "",
    frontier_dir: Path = DEFAULT_FRONTIER, open_turn_bound: int = DEFAULT_OPEN_TURN_BOUND,
) -> dict[str, Any]:
    initialize(frontier_dir)
    records = read_ledger(frontier_dir)
    state = replay(records)
    if turn_id not in state["turns"] or state["turns"][turn_id].get("status") != "open":
        raise FrontierError(f"turn is not open: {turn_id}")
    record = control_record(record_type="close", records=records, timestamp=timestamp,
                            session_id=session_id or state["turns"][turn_id]["session_id"],
                            turn_id=turn_id, parent_turn_id=parent_turn_id,
                            parent_session_id=parent_session_id, turn_type=turn_type,
                            model=model, subagent_of=subagent_of, issue_ids=issue_ids,
                            depends_on=depends_on, verifier_value=verifier_value,
                            next_action=next_action, status="closed",
                            metadata={"event_id": _next_event_id("close", records)})
    append_record(record, frontier_dir)
    rebuild_manifest(frontier_dir, open_turn_bound)
    return record


def compact(
    *, timestamp: str | None = None, reason: str = "",
    frontier_dir: Path = DEFAULT_FRONTIER, open_turn_bound: int = DEFAULT_OPEN_TURN_BOUND,
) -> dict[str, Any]:
    initialize(frontier_dir)
    records = read_ledger(frontier_dir)
    state = replay(records)
    record = control_record(record_type="compaction", records=records, timestamp=timestamp,
                            session_id="frontier", turn_id=None, parent_turn_id=None,
                            parent_session_id=None, turn_type="compaction", model="",
                            subagent_of=None, issue_ids=(), depends_on=(), verifier_value=None,
                            next_action="continue from active frontier", status="closed",
                            metadata={"event_id": _next_event_id("compaction", records),
                                      "reason": reason,
                                      "compacted_turn_ids": state["closed_turn_ids"] + state["rolled_back_turn_ids"],
                                      "ledger_sha256_before": sha256_bytes(ledger_bytes(frontier_dir)),
                                      "open_turn_ids": list(state["open_turn_ids"])})
    append_record(record, frontier_dir)
    rebuild_manifest(frontier_dir, open_turn_bound)
    return record


def rollback(
    *, reverted_to_turn: str, timestamp: str | None = None, git_commit: str | None = None,
    reason: str = "", session_id: str = "frontier", parent_turn_id: str | None = None,
    parent_session_id: str | None = None, turn_type: str = "rollback", model: str = "",
    subagent_of: str | None = None, issue_ids: Iterable[str] = (), depends_on: Iterable[str] = (),
    verifier_value: Any = None, next_action: str = "",
    frontier_dir: Path = DEFAULT_FRONTIER, open_turn_bound: int = DEFAULT_OPEN_TURN_BOUND,
) -> dict[str, Any]:
    initialize(frontier_dir)
    records = read_ledger(frontier_dir)
    state = replay(records)
    if reverted_to_turn not in state["turns"]:
        raise FrontierError(f"unknown reverted_to_turn: {reverted_to_turn}")
    if git_commit is not None and not COMMIT_RE.fullmatch(git_commit):
        raise FrontierError("git_commit must be a git-like hex id")
    record = control_record(record_type="rollback", records=records, timestamp=timestamp,
                            session_id=session_id, turn_id=None,
                            parent_turn_id=parent_turn_id,
                            parent_session_id=parent_session_id, turn_type=turn_type,
                            model=model, subagent_of=subagent_of, issue_ids=issue_ids,
                            depends_on=depends_on, verifier_value=verifier_value,
                            next_action=next_action, status="rolled_back",
                            metadata={"event_id": _next_event_id("rollback", records),
                                      "reverted_to_turn": reverted_to_turn,
                                      "git_commit": git_commit, "reason": reason})
    append_record(record, frontier_dir)
    rebuild_manifest(frontier_dir, open_turn_bound)
    return record


def recover(*, write: bool = False, frontier_dir: Path = DEFAULT_FRONTIER,
            open_turn_bound: int = DEFAULT_OPEN_TURN_BOUND) -> dict[str, Any]:
    view = inspect_frontier(frontier_dir, open_turn_bound)
    if not view["present"]:
        if write:
            initialize(frontier_dir)
        return empty_status(open_turn_bound)
    if view["errors"] and not write:
        raise FrontierError("; ".join(view["errors"]))
    if write:
        rebuild_manifest(frontier_dir, open_turn_bound)
    return status(frontier_dir, open_turn_bound)


def _record_from_args(args: argparse.Namespace, *, control: str | None = None) -> dict[str, Any]:
    return turn_record(session_id=args.session_id, turn_id=args.turn_id, timestamp=args.timestamp,
                       parent_turn_id=args.parent_turn_id, parent_session_id=args.parent_session_id,
                       turn_type=args.turn_type, model=args.model, subagent_of=args.subagent_of,
                       issue_ids=parse_id_list(args.issue_ids), depends_on=parse_id_list(args.depends_on),
                       verifier_value=parse_json(args.verifier, "verifier"), next_action=args.next_action)


def _add_record_options(parser: argparse.ArgumentParser, *, include_session: bool) -> None:
    if include_session:
        parser.add_argument("--session-id", required=True)
    else:
        parser.add_argument("--session-id", default=None)
    parser.add_argument("--timestamp", default=None)
    parser.add_argument("--parent-turn-id", default=None)
    parser.add_argument("--parent-session-id", default=None)
    parser.add_argument("--turn-type", default=None)
    parser.add_argument("--model", default="")
    parser.add_argument("--subagent-of", default=None)
    parser.add_argument("--issue-ids", default="")
    parser.add_argument("--depends-on", default="")
    parser.add_argument("--verifier", "--verifier-json", dest="verifier", default=None)
    parser.add_argument("--next-action", default="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier-dir", type=Path, default=DEFAULT_FRONTIER)
    parser.add_argument("--open-turn-bound", type=int, default=DEFAULT_OPEN_TURN_BOUND)
    sub = parser.add_subparsers(dest="command", required=True)

    open_parser = sub.add_parser("open", help="append an open turn")
    open_parser.add_argument("--turn-id", required=True)
    _add_record_options(open_parser, include_session=True)

    close_parser = sub.add_parser("close", help="append a close event")
    close_parser.add_argument("--turn-id", required=True)
    _add_record_options(close_parser, include_session=False)

    compact_parser = sub.add_parser("compact", help="append a compaction event")
    compact_parser.add_argument("--timestamp", default=None)
    compact_parser.add_argument("--reason", default="")

    rollback_parser = sub.add_parser("rollback", help="append a rollback event")
    rollback_parser.add_argument("--reverted-to-turn", required=True)
    _add_record_options(rollback_parser, include_session=False)
    rollback_parser.add_argument("--git-commit", default=None)

    sub.add_parser("status", help="show reconstructed frontier state")
    recover_parser = sub.add_parser("recover", help="verify or rebuild the manifest")
    recover_parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "open":
            result = open_turn(session_id=args.session_id, turn_id=args.turn_id,
                               timestamp=args.timestamp, parent_turn_id=args.parent_turn_id,
                               parent_session_id=args.parent_session_id, turn_type=args.turn_type,
                               model=args.model, subagent_of=args.subagent_of,
                               issue_ids=parse_id_list(args.issue_ids), depends_on=parse_id_list(args.depends_on),
                               verifier_value=parse_json(args.verifier, "verifier"), next_action=args.next_action,
                               frontier_dir=args.frontier_dir, open_turn_bound=args.open_turn_bound)
        elif args.command == "close":
            result = close_turn(turn_id=args.turn_id, timestamp=args.timestamp,
                                session_id=args.session_id, parent_turn_id=args.parent_turn_id,
                                parent_session_id=args.parent_session_id, turn_type=args.turn_type,
                                model=args.model, subagent_of=args.subagent_of,
                                issue_ids=parse_id_list(args.issue_ids), depends_on=parse_id_list(args.depends_on),
                                verifier_value=parse_json(args.verifier, "verifier"), next_action=args.next_action,
                                frontier_dir=args.frontier_dir, open_turn_bound=args.open_turn_bound)
        elif args.command == "compact":
            result = compact(timestamp=args.timestamp, reason=args.reason, frontier_dir=args.frontier_dir,
                             open_turn_bound=args.open_turn_bound)
        elif args.command == "rollback":
            result = rollback(reverted_to_turn=args.reverted_to_turn, timestamp=args.timestamp,
                              git_commit=args.git_commit, reason=args.reason, session_id=args.session_id,
                              parent_turn_id=args.parent_turn_id, parent_session_id=args.parent_session_id,
                              turn_type=args.turn_type, model=args.model, subagent_of=args.subagent_of,
                              issue_ids=parse_id_list(args.issue_ids), depends_on=parse_id_list(args.depends_on),
                              verifier_value=parse_json(args.verifier, "verifier"), next_action=args.next_action,
                              frontier_dir=args.frontier_dir, open_turn_bound=args.open_turn_bound)
        elif args.command == "status":
            result = status(args.frontier_dir, args.open_turn_bound)
        else:
            result = recover(write=args.write, frontier_dir=args.frontier_dir,
                             open_turn_bound=args.open_turn_bound)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (FrontierError, OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
