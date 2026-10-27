#!/usr/bin/env python3
"""Budget-aware unified retrieval for corpus and projected session memory."""
from __future__ import annotations

from pathlib import Path
import json
import re
import sys
from typing import Any

from ask import query, evidence_spans
from session_graph import PROJECTION_DB, search_events

BUDGETS = {"fast": 800, "default": 1600, "deep": 3200}
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FRONTIER = ROOT / "frontier"
DEFAULT_MEMORY = ROOT / "reflection" / "memory.md"
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from frontier_state import (DEFAULT_FRONTIER, FrontierError, inspect_frontier, ledger_path,  # noqa: E402
                            manifest_path)


def _estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


def _frontier_integrity(frontier_dir: Path) -> tuple[str, list[str]]:
    """Label frontier records valid/partial/invalid using the canonical validators.

    Fail-closed: anything the canonical inspection cannot prove valid is
    withheld unless the caller explicitly asks for forensic access.
    """
    if not ledger_path(frontier_dir).exists() and not manifest_path(frontier_dir).exists():
        return "missing", []
    try:
        view = inspect_frontier(frontier_dir)
    except (FrontierError, OSError, UnicodeDecodeError, UnicodeError, json.JSONDecodeError,
            TypeError, ValueError) as error:
        return "partial", [str(error)]
    if not view["present"]:
        return "missing", []
    return ("invalid" if view["errors"] else "valid"), view["errors"]


def _frontier_item(question: str, frontier_dir: Path, *, include_invalid: bool = False) -> dict[str, Any] | None:
    manifest = frontier_dir / "manifest.json"
    if not manifest.exists():
        return None
    try:
        state = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    active = state.get("open_turn_ids", [])
    turns = state.get("turns", {})
    actions = [turns.get(turn_id, {}).get("next_action", "") for turn_id in active]
    text = "frontier status: " + ("; ".join(action for action in actions if action) or "no active next action")
    text += f"; open turns={len(active)}; bound ok={state.get('bound_ok', True)}"
    integrity, errors = _frontier_integrity(frontier_dir)
    if integrity != "valid" and not include_invalid:
        return {"kind": "frontier_integrity", "id": "frontier:integrity", "path": str(frontier_dir),
                "integrity": integrity, "integrity_errors": errors,
                "text": f"frontier integrity is {integrity}; authoritative frontier context withheld"}
    return {"kind": "frontier", "id": "frontier:manifest", "path": str(manifest),
            "integrity": integrity, "integrity_errors": errors, "text": text}


def _frontier_items(question: str, frontier_dir: Path, limit: int, *, include_invalid: bool = False) -> list[dict[str, Any]]:
    ledger = frontier_dir / "ledger.jsonl"
    if not ledger.exists():
        return []
    terms = {word.lower() for word in re.findall(r"\w+", question) if len(word) > 2}
    matches: list[tuple[int, int, dict[str, Any]]] = []
    integrity, errors = _frontier_integrity(frontier_dir)
    if integrity != "valid" and not include_invalid:
        return []
    try:
        lines = ledger.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for index, line in enumerate(lines):
        try:
            record = json.loads(line)
        except (TypeError, ValueError):
            continue
        if not isinstance(record, dict):
            continue
        text = " ".join(str(record.get(key, "")) for key in
                        ("turn_id", "turn_type", "session_id", "next_action", "status", "issue_ids"))
        score = sum(1 for term in terms if term in text.lower())
        if score:
            record_id = str(record.get("turn_id") or record.get("record_type") or index)
            matches.append((score, index, {"kind": "frontier", "id": f"frontier:{record_id}",
                                           "path": str(ledger), "integrity": integrity,
                                           "integrity_errors": errors, "text": text}))
    matches.sort(key=lambda match: (-match[0], -match[1]))
    return [item for _, _, item in matches[:limit]]


def _lesson_items(question: str, memory_path: Path, limit: int) -> list[dict[str, Any]]:
    if not memory_path.exists():
        return []
    try:
        content = memory_path.read_text(encoding="utf-8")
    except OSError:
        return []
    terms = {word.lower() for word in re.findall(r"\w+", question) if len(word) > 2}
    items = []
    for block in re.split(r"\n(?=###\s+)", content):
        header = block.strip().splitlines()[0] if block.strip() else ""
        if not re.match(r"###\s+.+\s+—\s+accepted\s*$", header, re.I):
            continue
        score = sum(1 for term in terms if term in block.lower())
        if score:
            items.append((score, {"kind": "lesson", "id": header[4:].strip(),
                                  "path": str(memory_path), "text": block.strip()}))
    items.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    return [item for _, item in items[:limit]]


def _artifact_items(question: str, path: Path, workspace: str | None, limit: int) -> list[dict[str, Any]]:
    import sqlite3
    if not path.exists():
        return []
    terms = {word.lower() for word in re.findall(r"\w+", question) if len(word) > 2}
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    sql = ("SELECT a.artifact_id,a.session_id,a.path,a.artifact_type,s.workspace "
           "FROM artifacts a JOIN sessions s ON s.session_id=a.session_id")
    params: list[Any] = []
    if workspace is not None:
        sql += " WHERE s.workspace=?"
        params.append(workspace)
    sql += " ORDER BY a.artifact_id LIMIT ?"
    params.append(max(limit * 5, limit))
    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.DatabaseError:
        conn.close()
        return []
    conn.close()
    scored = []
    for row in rows:
        item = dict(row)
        haystack = f"{item['path']} {item['artifact_type'] or ''}".lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            scored.append((score, {"kind": "artifact", "id": item["artifact_id"],
                                   "session_id": item["session_id"], "workspace": item["workspace"],
                                   "path": item["path"],
                                   "text": f"{item['artifact_type'] or 'artifact'}: {item['path']}"}))
    scored.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    return [item for _, item in scored[:limit]]


def context_packet(question: str, *, mode: str = "default", limit: int = 5,
                   workspace: str | None = None,
                   session_graph_path: Path | None = None,
                   frontier_dir: Path | None = None,
                   memory_path: Path | None = None,
                   include_invalid_frontier: bool = False) -> dict[str, Any]:
    """Return bounded, provenance-rich context without full corpus bodies."""
    if mode not in BUDGETS:
        raise ValueError(f"unknown mode: {mode}")
    budget = BUDGETS[mode]
    if not question.strip() or limit < 1:
        return {"mode": mode, "token_budget": budget, "estimated_tokens": 0,
                "items": [], "truncated": False}

    items: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    corpus_rows = query(question, limit=max(limit, 3))
    for row in corpus_rows:
        key = ("corpus", row["id"])
        if key in seen:
            continue
        spans = evidence_spans(row["id"], question, limit=2, max_chars=1100)
        text = "\n".join(span["text"] for span in spans)
        if not text:
            text = row.get("snippet", "")
        items.append({"kind": "corpus", "id": row["id"],
                      "source_family": row.get("source_family", ""),
                      "path": row.get("path", ""), "text": text})
        seen.add(key)

    session_path = session_graph_path or PROJECTION_DB
    try:
        session_rows = search_events(question, limit=max(limit, 3),
                                     workspace=workspace, path=session_path)
    except (FileNotFoundError, OSError):
        session_rows = []
    for row in session_rows:
        key = ("session", row["event_id"])
        if key in seen:
            continue
        items.append({"kind": "session", "id": row["event_id"],
                      "session_id": row["session_id"],
                      "workspace": row.get("workspace", ""),
                      "event_type": row["event_type"], "text": row["payload"]})
        seen.add(key)

    frontier_path = frontier_dir or DEFAULT_FRONTIER
    frontier = _frontier_item(question, frontier_path, include_invalid=include_invalid_frontier)
    if frontier:
        items.append(frontier)
        seen.add(("frontier", frontier["id"]))
    for item in _frontier_items(question, frontier_path, limit, include_invalid=include_invalid_frontier):
        key = ("frontier", item["id"])
        if key not in seen:
            items.append(item)
            seen.add(key)
    for item in _artifact_items(question, session_path, workspace, limit):
        key = ("artifact", item["id"])
        if key not in seen:
            items.append(item)
            seen.add(key)
    for item in _lesson_items(question, memory_path or DEFAULT_MEMORY, limit):
        key = ("lesson", item["id"])
        if key not in seen:
            items.append(item)
            seen.add(key)

    selected: list[dict[str, Any]] = []
    used = 0
    omitted = False
    # DB-1 fix (VERA runs/DB1_arms.md, DB1-F2): reserve per-kind slots so
    # lesson/frontier items cannot crowd out corpus evidence rows.
    per_kind_reserved = {"corpus": 3}
    reserved_counts = {k: 0 for k in per_kind_reserved}
    for item in items:
        kind = item["kind"]
        if kind in per_kind_reserved and reserved_counts[kind] < per_kind_reserved[kind]:
            cost = _estimate_tokens(item["text"])
            if not selected and cost > budget:
                item["text"] = item["text"][: budget * 4]
                cost = _estimate_tokens(item["text"])
            elif selected and used + cost > budget:
                room = max(0, (budget - used) * 4)
                item["text"] = item["text"][:room]
                cost = _estimate_tokens(item["text"])
            reserved_counts[kind] += 1
            item["estimated_tokens"] = cost
            selected.append(item)
            used += cost
            continue
    for item in items:
        if any(item is s for s in selected):
            continue
        cost = _estimate_tokens(item["text"])
        if not selected and cost > budget:
            item["text"] = item["text"][: budget * 4]
            cost = _estimate_tokens(item["text"])
        elif selected and used + cost > budget:
            omitted = True
            continue
        item["estimated_tokens"] = cost
        selected.append(item)
        used += cost

    return {"mode": mode, "token_budget": budget, "estimated_tokens": used,
            "items": selected, "truncated": omitted or len(selected) < len(items)}
