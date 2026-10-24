#!/usr/bin/env python3
"""Unified Multi-Agent Session Browser & Exporter.

Supports reading, listing, rendering, exporting, and copying sessions across:
- opencode (SQLite: %USERPROFILE%/.local/share/opencode/opencode.db — 2.x `session_v2`/`session_message`, legacy `session`/`message`/`part`)
- goose (SQLite: %APPDATA%/Block/goose/data/sessions/sessions.db)
- hermes (SQLite: %LOCALAPPDATA%/hermes/state.db)
- pi (JSONL: %USERPROFILE%/.pi/agent/sessions/*/*.jsonl)
- omp / oh-my-pi (JSONL: %USERPROFILE%/.omp/agent/sessions/*/*.jsonl — fork pi-coding-agent)
- jcode (JSON: %USERPROFILE%/.jcode/sessions/session_*.json)
- antigravity (JSONL: %USERPROFILE%/.gemini/antigravity-ide/brain/*/logs/transcript*.jsonl)
- cursor (SQLite: %APPDATA%/Cursor/User/globalStorage/state.vscdb — composerHeaders + cursorDiskKV)
- droid (JSONL: %USERPROFILE%/.factory/sessions/**/*.jsonl — Factory AI agent)
- cline (JSON: %USERPROFILE%/.cline/data/sessions/*/*.messages.json + <id>.json meta)

Usage:
  python scripts/agent_sessions.py list [--agent AGENT] [--limit N] [--query SEARCH]
  python scripts/agent_sessions.py browse [--out FILE] [--limit N] [--agent AGENT]
  python scripts/agent_sessions.py export <agent> <session_id> [-o FILE] [--format md|raw]
"""
from __future__ import annotations

import argparse
import html as _html
import json
import os
import re
import shutil
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "scripts" / "_scratch" / "sessions" / "02_products"

# Standard paths
OPENCODE_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
GOOSE_DB = Path.home() / "AppData" / "Roaming" / "Block" / "goose" / "data" / "sessions" / "sessions.db"
HERMES_DB = Path.home() / "AppData" / "Local" / "hermes" / "state.db"
PI_DIR = Path.home() / ".pi" / "agent" / "sessions"
OMP_DIR = Path.home() / ".omp" / "agent" / "sessions"
JCODE_DIR = Path.home() / ".jcode" / "sessions"
ANTIGRAVITY_BRAIN = Path.home() / ".gemini" / "antigravity-ide" / "brain"
CURSOR_STATE_DB = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "globalStorage" / "state.vscdb"
DROID_SESSIONS_DIR = Path.home() / ".factory" / "sessions"
DEEPSEEK_SESSIONS_DIR = Path.home() / ".deepseek-harness" / "sessions"
DSH_SESSIONS_DIR = Path.home() / ".dsh" / "sessions"
CLINE_SESSIONS_DIR = Path.home() / ".cline" / "data" / "sessions"

SUPPORTED_AGENTS = ["opencode", "goose", "hermes", "pi", "omp", "jcode", "antigravity", "cursor", "droid", "deepseek", "cline"]

# Message/event types that the harness writes next to the conversation. They are
# audit events, not turns: rendering them as `## [type]` blocks turns a transcript
# into a log of model switches and idle ticks, and inflates the message count.
HARNESS_MESSAGE_TYPES = frozenset({
    "idle", "model-switched", "compaction", "system", "synthetic", "developer",
})

# Harness events that carry text worth keeping (operational notices, synthetic
# prompts). They are collapsed into one section, never rendered as turns.
TEXT_HARNESS_MESSAGE_TYPES = frozenset({"system", "synthetic", "developer"})

# Every role the loaders emit as a `## [role]` boundary. Used to recognise a
# real message start when an unclosed `<details>` reasoning block has no
# `</details>` to end on (see `strip_reasoning_blocks`). `message` is the
# default several loaders use when the store omits a role.
MESSAGE_BOUNDARY_ROLES = frozenset({
    "user", "assistant", "tool", "message", "reasoning", "prompt", "toolResult",
}) | HARNESS_MESSAGE_TYPES


@dataclass
class SessionItem:
    agent: str
    id: str
    title: str
    directory: str
    created_at: str
    updated_at: str
    message_count: int
    model: str
    raw_path: str
    text_markdown: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)
    # Set only where the store records it (opencode `session_v2.parent_id`).
    # Empty means "not a child / unknown", both rendered honestly, never as a
    # fabricated link — 44 subagent sessions must not look independent.
    parent: str = ""


def fmt_ts(val: Any) -> str:
    if not val:
        return ""
    try:
        if isinstance(val, (int, float)):
            # check if seconds or ms
            if val > 1e11:
                val = val / 1000.0
            return datetime.fromtimestamp(val).strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(val, str):
            # check iso format
            val_clean = val.replace("Z", "+00:00")
            if "T" in val_clean:
                dt = datetime.fromisoformat(val_clean)
                # A Z-suffixed (UTC) value parses to a tz-aware datetime. Convert
                # to local wall time before formatting, so jcode sessions (stored
                # in UTC) line up with the naive-local times every other agent
                # reports. Naive datetimes are untouched (their tzinfo is None).
                if dt.tzinfo is not None:
                    dt = dt.astimezone()
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            return val[:19]
    except Exception:
        pass
    return str(val)[:19]


def fmt_utc_wall(val: Any) -> str:
    """Render a UTC wall-clock value as local wall time.

    Goose stores `created_at`/`updated_at` as naive UTC
    (`YYYY-MM-DD HH:MM:SS`, no offset marker), so printing them raw shows
    Warsaw sessions 2h behind (CEST). Assume UTC when no offset is present
    and convert to local time; aware values are just converted.
    """
    if not val:
        return ""
    s = str(val).strip()
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        if "T" in s:
            dt = datetime.fromisoformat(s)
        else:
            dt = datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return s[:19]


def _iso_key(val: Any) -> float:
    """Sortable numeric key for a jcode ISO timestamp (Z-suffixed, mixed
    fractional precision). Parsing to an aware datetime makes the ordering
    exact, unlike a raw string compare, which mis-orders values that fall in
    the same second but carry different fractional-digit counts (jcode mixes
    0/6/9-digit fractions in practice). Returns -inf when unparseable so such
    values sort first rather than crashing the pick."""
    if not isinstance(val, str) or "T" not in val:
        return float("-inf")
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00")).timestamp()
    except Exception:
        return float("-inf")


# -------------------------------------------------------------
# 1. opencode
# -------------------------------------------------------------
def _opencode_tables(c: sqlite3.Connection) -> set:
    return {r[0] for r in c.execute("select name from sqlite_master where type='table'")}


def _format_model(value: Any) -> str:
    """Turn a stored model value into `provider/id` instead of a raw JSON blob.

    opencode 2.x keeps `{"id": ..., "providerID": ...}` in the model column; the
    exporter used to stringify the dict, so every header showed JSON.
    """
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""
        try:
            value = json.loads(text)
        except Exception:
            return text
    if isinstance(value, dict):
        model_id = str(value.get("id") or value.get("name") or "")
        provider = str(value.get("providerID") or value.get("provider") or "")
        if provider and model_id:
            return f"{provider}/{model_id}"
        return model_id or json.dumps(value, ensure_ascii=False)
    return str(value or "")


# Emitted by `_truncate_mid`; the merged builder detects it to mark a session
# as truncated and to keep truncated outputs out of dedup (equal head+tail does
# not imply equal content).
TRUNC_MARKER_RE = re.compile(r"…\[\+\d+ zn\.\]…")


def _truncate_mid(text: Any, cap: int) -> str:
    """Keep both ends of an over-budget tool payload and state what was cut.

    `text[:cap]` loses the tail — for `git log`/`git show` that is the newest,
    most relevant lines — and never says how much was dropped. Head + tail
    keeps the same budget while showing what the command was and how it ended,
    plus a gap marker the reader can account for. Never applied to prompts or
    assistant prose, only to tool in/out payloads.
    """
    s = str(text)
    if len(s) <= cap:
        return s
    half = cap // 2
    omitted = len(s) - 2 * half
    return f"{s[:half]} …[+{omitted} zn.]… {s[-half:]}"


def _append_harness_summary(lines: List[str], counts: Dict[str, int],
                            texts: Optional[Dict[str, List[str]]] = None) -> None:
    """Collapse non-conversational rows into one auditable section.

    Counts are always reported. Text-bearing events (`system`, `synthetic`) are
    kept inside a collapsed `<details>` block instead of being silently lost.
    """
    if not counts or not lines:
        return
    summary = ", ".join(f"{k}×{v}" for k, v in sorted(counts.items()))
    kept = {k: v for k, v in (texts or {}).items() if v}
    if kept:
        lines.append(f"<details><summary>Zdarzenia harnessu ({summary})</summary>")
        lines.append("")
        for role in sorted(kept):
            for txt in kept[role]:
                lines.append(f"**{role}**: {txt[:2000]}")
                lines.append("")
        lines.append("</details>")
    else:
        lines.append(f"> **Pominiete zdarzenia harnessu**: {summary}")
    lines.append("")


def _render_opencode_legacy(c: sqlite3.Connection, sid: str) -> "tuple[List[str], int]":
    """Pre-2.0 layout: `message` rows, each with `part` rows."""
    msgs = c.execute("select id from message where session_id=? order by time_created, id", (sid,)).fetchall()
    lines: List[str] = []
    harness: Dict[str, int] = {}
    harness_texts: Dict[str, List[str]] = {}
    rendered = 0
    for m in msgs:
        mrow = c.execute("select data from message where id=?", (m["id"],)).fetchone()
        try: mdata = json.loads(mrow["data"])
        except Exception: mdata = {}
        role = mdata.get("role", "user")
        is_harness = role in HARNESS_MESSAGE_TYPES
        if is_harness:
            harness[role] = harness.get(role, 0) + 1
        else:
            rendered += 1
            lines.append(f"## [{role}]")
        for prow in c.execute("select data from part where message_id=? order by time_created, id", (m["id"],)).fetchall():
            try: p = json.loads(prow["data"])
            except Exception: continue
            t = p.get("type")
            if is_harness:
                if (t == "text" and p.get("text")
                        and role in TEXT_HARNESS_MESSAGE_TYPES):
                    harness_texts.setdefault(role, []).append(p.get("text", ""))
                continue
            if t == "text":
                lines.append(p.get("text", ""))
            elif t == "tool":
                st = p.get("state") or {}
                name = p.get("tool", "?")
                lines.append(f"> **tool** `{name}` · {st.get('status','?')}")
                inp = st.get("input") or p.get("input") or {}
                outp = st.get("output") or p.get("output") or ""
                if inp:
                    istr = json.dumps(inp, ensure_ascii=False)
                    lines.append(f"> in: `{_truncate_mid(istr, 4000)}`")
                if outp:
                    lines.append(f"> out: `{_truncate_mid(outp, 4000)}`")
            elif t == "reasoning":
                txt = p.get("text", "")
                if txt:
                    lines.append(f"<details><summary>reasoning</summary>\n\n{txt[:2500]}\n\n</details>")
        if not is_harness:
            lines.append("")
    _append_harness_summary(lines, harness, harness_texts)
    return lines, rendered


def _render_opencode_v2(c: sqlite3.Connection, sid: str) -> "tuple[List[str], int]":
    """opencode 2.x layout: `session_message` rows; assistant `data.content` blocks."""
    msgs = c.execute(
        "select type, data from session_message where session_id=? order by seq, time_created, id",
        (sid,)).fetchall()
    lines: List[str] = []
    harness: Dict[str, int] = {}
    harness_texts: Dict[str, List[str]] = {}
    rendered = 0
    for m in msgs:
        try: data = json.loads(m["data"]) if m["data"] else {}
        except Exception: data = {}
        if not isinstance(data, dict):
            data = {}
        role = m["type"] or "user"
        # Harness events are counted, not rendered as turns. Text-bearing ones
        # (system/synthetic) are kept in the collapsed summary so audit survives.
        if role in HARNESS_MESSAGE_TYPES:
            harness[role] = harness.get(role, 0) + 1
            if data.get("text") and role in TEXT_HARNESS_MESSAGE_TYPES:
                harness_texts.setdefault(role, []).append(str(data["text"]))
            continue
        rendered += 1
        lines.append(f"## [{role}]")
        if role == "user":
            txt = data.get("text", "")
            if txt:
                lines.append(txt)
        else:
            for b in data.get("content") or []:
                t = b.get("type")
                if t == "text":
                    lines.append(b.get("text", ""))
                elif t == "reasoning":
                    txt = b.get("text", "")
                    if txt:
                        lines.append(f"<details><summary>reasoning</summary>\n\n{txt[:2500]}\n\n</details>")
                elif t == "tool":
                    st = b.get("state") or {}
                    name = b.get("name") or b.get("tool") or "?"
                    lines.append(f"> **tool** `{name}` · {st.get('status','?')}")
                    inp = st.get("input")
                    if inp:
                        lines.append(f"> in: `{_truncate_mid(json.dumps(inp, ensure_ascii=False), 4000)}`")
                    outp = st.get("content")
                    if isinstance(outp, list):
                        outp = " ".join(x.get("text", "") for x in outp if isinstance(x, dict))
                    if outp:
                        lines.append(f"> out: `{_truncate_mid(outp, 4000)}`")
        lines.append("")
    _append_harness_summary(lines, harness, harness_texts)
    return lines, rendered


def load_opencode_sessions(limit: int = 50) -> List[SessionItem]:
    if not OPENCODE_DB.exists():
        return []
    items = []
    try:
        c = sqlite3.connect(str(OPENCODE_DB))
        c.row_factory = sqlite3.Row
        tables = _opencode_tables(c)
        # Union of legacy `session` and `session_v2`, merged by id. The
        # 2026-10-16 assumption that v2 is a strict superset no longer
        # holds: today's live opencode writes main sessions that exist
        # ONLY in the legacy table, while v2 still carries child sessions
        # that legacy lacks (145 ids were v2-only). Reading either table
        # alone silently drops sessions of the other kind — same silent
        # loss class as S68. Keep the row with the later time_updated.
        union_rows: dict = {}
        for t in [t for t in ("session", "session_v2") if t in tables]:
            for s in c.execute(f"select * from {t}"):
                sid = s["id"]
                cur = union_rows.get(sid)
                if cur is None or (s["time_updated"] or 0) > (cur["time_updated"] or 0):
                    union_rows[sid] = s
        ordered = sorted(
            union_rows.values(), key=lambda s: s["time_updated"] or 0, reverse=True
        )
        for s in ordered[:limit]:
            sid = s["id"]
            # A 2.0 session has no legacy `message` rows; only then render from
            # `session_message`, so pre-2.0 sessions keep their existing rendering.
            has_legacy = "message" in tables and c.execute(
                "select 1 from message where session_id=? limit 1", (sid,)).fetchone() is not None
            body, count = (_render_opencode_legacy(c, sid) if has_legacy
                           else _render_opencode_v2(c, sid))
            lines = [
                f"# [opencode] {s['title'] or sid}",
                "",
                f"- **Agent**: `opencode`",
                f"- **ID**: `{sid}`",
                f"- **Katalog**: `{s['directory']}`",
                f"- **Model**: `{_format_model(s['model']) or '?'}`",
                f"- **Utworzona**: {fmt_ts(s['time_created'])} | **Zaktualizowana**: {fmt_ts(s['time_updated'])}",
                f"- **Wiadomości**: {count}",
                "",
            ]
            lines.extend(body)

            items.append(SessionItem(
                agent="opencode",
                id=sid,
                title=s["title"] or sid,
                directory=s["directory"] or "",
                created_at=fmt_ts(s["time_created"]),
                updated_at=fmt_ts(s["time_updated"]),
                message_count=count,
                model=_format_model(s["model"]),
                raw_path=str(OPENCODE_DB),
                text_markdown="\n".join(lines),
                parent=str(s["parent_id"] or "") if "parent_id" in s.keys() else "",
            ))
        c.close()
    except Exception as e:
        print(f"Error reading opencode sessions: {e}", file=sys.stderr)
    return items


# -------------------------------------------------------------
# 2. goose
# -------------------------------------------------------------
def _render_goose_block(block: dict) -> List[str]:
    """Render one goose content_json block.

    The live schema is camelCase (`toolRequest`/`toolResponse`/`thinking`);
    an older draft of this loader matched snake_case names that never occur,
    silently dropping every tool call, tool result and reasoning block — only
    bare user texts survived. Unknown shapes are dumped as JSON, never
    dropped: a noisy line beats a hole in the log.
    """
    out: List[str] = []
    b_type = block.get("type")
    if b_type == "text":
        out.append(block.get("text", ""))
    elif b_type == "thinking":
        txt = block.get("thinking", "")
        if txt:
            out.append(f"<details><summary>thinking</summary>\n\n{txt[:2500]}\n\n</details>")
    elif b_type in ("toolRequest", "tool_request"):
        call = block.get("toolCall") or block.get("tool_call") or {}
        val = call.get("value", {}) if isinstance(call, dict) else {}
        name = val.get("name", "?") if isinstance(val, dict) else "?"
        args = val.get("arguments", {}) if isinstance(val, dict) else {}
        status = call.get("status", "?") if isinstance(call, dict) else "?"
        out.append(f"> **tool request** `{name}` · {status} · id `{block.get('id', '?')}`")
        if args:
            out.append(f"> in: `{_truncate_mid(json.dumps(args, ensure_ascii=False), 1200)}`")
    elif b_type in ("toolResponse", "tool_response"):
        res = block.get("toolResult") or block.get("tool_response") or {}
        val = res.get("value") if isinstance(res, dict) else res
        status = res.get("status", "?") if isinstance(res, dict) else "?"
        out.append(f"> **tool response** `{block.get('id', '?')}` · {status}")
        out.append(f"> out: `{_truncate_mid(_goose_result_text(val), 1200)}`")
    else:
        out.append(f"> `[{b_type}]` `{_truncate_mid(json.dumps(block, ensure_ascii=False), 1200)}`")
    return out


def _goose_result_text(val: Any) -> str:
    """Flatten a goose toolResult value (nested content list or plain)."""
    if isinstance(val, dict) and isinstance(val.get("content"), list):
        parts = []
        for item in val["content"]:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            else:
                parts.append(json.dumps(item, ensure_ascii=False))
        return "\n".join(parts)
    return str(val)


def load_goose_sessions(limit: int = 50) -> List[SessionItem]:
    if not GOOSE_DB.exists():
        return []
    items = []
    try:
        c = sqlite3.connect(str(GOOSE_DB))
        c.row_factory = sqlite3.Row
        q = "select * from sessions order by updated_at desc limit ?"
        for s in c.execute(q, (limit,)):
            sid = s["id"]
            msg_rows = c.execute("select * from messages where session_id=? order by created_timestamp, id", (sid,)).fetchall()

            lines = [
                f"# [goose] {s['name'] or sid}",
                "",
                f"- **Agent**: `goose`",
                f"- **ID**: `{sid}`",
                f"- **Katalog**: `{s['working_dir']}`",
                f"- **Model**: `{s['provider_name'] or '?'}`",
                f"- **Utworzona**: {fmt_utc_wall(s['created_at'])} | **Zaktualizowana**: {fmt_utc_wall(s['updated_at'])}",
                f"- **Wiadomości**: {len(msg_rows)}",
                "",
            ]
            for m in msg_rows:
                lines.append(f"## [{m['role']}]")
                try:
                    c_json = json.loads(m["content_json"])
                    for block in c_json:
                        lines.extend(_render_goose_block(block))
                except Exception:
                    lines.append(m["content_json"] or "")
                lines.append("")

            title = s["name"] or s["description"] or sid
            items.append(SessionItem(
                agent="goose",
                id=sid,
                title=title,
                directory=s["working_dir"] or "",
                created_at=fmt_utc_wall(s["created_at"]),
                updated_at=fmt_utc_wall(s["updated_at"]),
                message_count=len(msg_rows),
                model=str(s["provider_name"] or ""),
                raw_path=str(GOOSE_DB),
                text_markdown="\n".join(lines)
            ))
        c.close()
    except Exception as e:
        print(f"Error reading goose sessions: {e}", file=sys.stderr)
    return items


# -------------------------------------------------------------
# 3. hermes
# -------------------------------------------------------------
def load_hermes_sessions(limit: int = 50) -> List[SessionItem]:
    if not HERMES_DB.exists():
        return []
    items = []
    try:
        c = sqlite3.connect(str(HERMES_DB))
        c.row_factory = sqlite3.Row
        q = "select * from sessions order by started_at desc limit ?"
        for s in c.execute(q, (limit,)):
            sid = s["id"]
            msg_rows = c.execute("select * from messages where session_id=? order by timestamp, id", (sid,)).fetchall()

            lines = [
                f"# [hermes] {s['title'] or sid}",
                "",
                f"- **Agent**: `hermes`",
                f"- **ID**: `{sid}`",
                f"- **Katalog**: `{s['cwd']}`",
                f"- **Model**: `{s['model'] or '?'}`",
                f"- **Rozpoczęta**: {s['started_at']} | **Zakończona**: {s['ended_at'] or '-'}",
                f"- **Wiadomości**: {len(msg_rows)}",
                "",
            ]
            for m in msg_rows:
                lines.append(f"## [{m['role']}]")
                content = m["content"] or ""
                if content:
                    lines.append(content)
                if m["tool_calls"]:
                    lines.append(f"> **tool calls**: `{_truncate_mid(m['tool_calls'], 4000)}`")
                if m["reasoning"] or m["reasoning_content"]:
                    r_text = m["reasoning"] or m["reasoning_content"]
                    lines.append(f"<details><summary>reasoning</summary>\n\n{r_text[:2500]}\n\n</details>")
                lines.append("")

            items.append(SessionItem(
                agent="hermes",
                id=sid,
                title=s["title"] or sid,
                directory=s["cwd"] or "",
                created_at=fmt_ts(s["started_at"]),
                updated_at=fmt_ts(s["last_activity_at"] or s["started_at"]),
                message_count=len(msg_rows),
                model=str(s["model"] or ""),
                raw_path=str(HERMES_DB),
                text_markdown="\n".join(lines)
            ))
        c.close()
    except Exception as e:
        print(f"Error reading hermes sessions: {e}", file=sys.stderr)
    return items


# -------------------------------------------------------------
# 4. pi
# -------------------------------------------------------------
def _load_pi_style_sessions(source_dir: Path, agent_name: str, limit: int = 50) -> List[SessionItem]:
    if not source_dir.exists():
        return []
    items = []
    try:
        files = sorted(source_dir.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
        for f in files:
            msgs = []
            session_info = {}
            lines = []
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                        t = obj.get("type")
                        if t == "session":
                            session_info = obj
                        elif t == "message":
                            msgs.append(obj.get("message") or {})
                        elif t in ("user", "assistant", "system", "tool_result"):
                            msgs.append(obj)
                    except Exception:
                        pass

            sid = session_info.get("id", f.stem)
            cwd = session_info.get("cwd", f.parent.name.replace("--", "/"))

            lines.append(f"# [{agent_name}] {sid}")
            lines.append("")
            lines.append(f"- **Agent**: `{agent_name}`")
            lines.append(f"- **ID**: `{sid}`")
            lines.append(f"- **Plik**: `{f}`")
            lines.append(f"- **Katalog**: `{cwd}`")
            lines.append(f"- **Czas**: {fmt_ts(f.stat().st_mtime)}")
            lines.append(f"- **Wiadomości**: {len(msgs)}")
            lines.append("")

            first_user_prompt = ""
            session_model = ""
            for m in msgs:
                role = m.get("role") or m.get("type", "message")
                if m.get("model"):
                    prov = str(m.get("provider") or "")
                    mid = str(m["model"])
                    session_model = f"{prov}/{mid}" if prov else mid
                lines.append(f"## [{role}]")
                content = m.get("content") or ""
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("type") == "text":
                                txt = item.get("text", "")
                                lines.append(txt)
                                if not first_user_prompt and role == "user":
                                    first_user_prompt = txt[:60]
                            elif item.get("type") == "tool_use":
                                lines.append(f"> **tool call** `{item.get('name')}`: `{_truncate_mid(json.dumps(item.get('input',{})), 4000)}`")
                            elif item.get("type") == "tool_result":
                                lines.append(f"> **tool result**: `{_truncate_mid(item.get('content'), 4000)}`")
                        else:
                            lines.append(str(item))
                elif isinstance(content, str):
                    lines.append(content)
                    if not first_user_prompt and role == "user":
                        first_user_prompt = content[:60]
                lines.append("")

            display_title = (first_user_prompt.strip() or sid).replace("\n", " ")
            # omp prefixes the first prompt with an `<attachment>` block, so a
            # dozen sessions all titled `<attachment>` are told apart only by the
            # text after it. Strip the marker before deriving the title.
            display_title = re.sub(
                r"^\s*(?:<attachment[^>]*>\s*)+", "", display_title).strip()

            items.append(SessionItem(
                agent=agent_name,
                id=sid,
                title=display_title[:80] or sid,
                directory=str(cwd),
                created_at=fmt_ts(session_info.get("timestamp") or f.stat().st_ctime),
                updated_at=fmt_ts(f.stat().st_mtime),
                message_count=len(msgs),
                model=session_model,
                raw_path=str(f),
                text_markdown="\n".join(lines),
                parent=str(session_info.get("parentID")
                           or session_info.get("parentId")
                           or session_info.get("parent") or ""),
            ))
    except Exception as e:
        print(f"Error reading {agent_name} sessions: {e}", file=sys.stderr)
    return items


def load_pi_sessions(limit: int = 50) -> List[SessionItem]:
    return _load_pi_style_sessions(PI_DIR, "pi", limit)


def load_omp_sessions(limit: int = 50) -> List[SessionItem]:
    """oh-my-pi (omp) — fork pi-coding-agent, ten sam format JSONL, wlasny katalog."""
    return _load_pi_style_sessions(OMP_DIR, "omp", limit)


# -------------------------------------------------------------
# 5. jcode
# -------------------------------------------------------------
def _jcode_activity_mtime(p) -> float:
    """Last-activity mtime for a jcode session file.

    The recency pre-filter below must not rank on the .json checkpoint
    mtime alone: a live session keeps appending to its sibling
    .journal.jsonl, which does NOT refresh the checkpoint. Ranking on
    max(checkpoint, journal) mtime keeps an actively-written session
    inside the top-`limit` window even when its last checkpoint flush is
    stale (R5 red test: an active session was dropped by the old key).
    """
    try:
        t = p.stat().st_mtime
    except OSError:
        return 0.0
    jp = p.parent / (p.stem + ".journal.jsonl")
    try:
        if jp.exists():
            t = max(t, jp.stat().st_mtime)
    except OSError:
        pass
    return t


def load_jcode_sessions(limit: int = 50) -> List[SessionItem]:
    if not JCODE_DIR.exists():
        return []
    items = []
    try:
        files = sorted(JCODE_DIR.glob("*.json"), key=_jcode_activity_mtime, reverse=True)[:limit]
        for f in files:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                data = json.load(fh)

            sid = str(data.get("id") or f.stem)
            raw_title = data.get("title")
            title = str(raw_title) if raw_title else sid
            cwd = str(data.get("working_dir") or "")
            msgs = data.get("messages") or []

            # jcode checkpoints the transcript into this .json file, but a session
            # that is still live keeps appending to a sibling .journal.jsonl
            # (lines of shape {"meta": {...}, "append_messages": [...]}, whose
            # messages are not yet in the snapshot). Without merging them, the
            # export truncates the session by however much time has passed since
            # the last snapshot flush. Merge (dedup by message id) and take the
            # journal's newest meta.updated_at as the true last-activity time.
            journal_path = f.parent / (f.stem + ".journal.jsonl")
            journal_ts: Optional[str] = None
            if journal_path.exists():
                seen = {m.get("id") for m in msgs if isinstance(m, dict) and m.get("id")}
                extra_msgs: List[Dict[str, Any]] = []
                try:
                    for raw in journal_path.read_text(encoding="utf-8", errors="replace").splitlines():
                        if not raw.strip():
                            continue
                        try:
                            entry = json.loads(raw)
                        except Exception:
                            continue
                        meta_ts = (entry.get("meta") or {}).get("updated_at")
                        if meta_ts:
                            journal_ts = str(meta_ts)  # entries appended in order; last non-null wins
                        for m in entry.get("append_messages") or []:
                            if not isinstance(m, dict):
                                continue
                            mid = m.get("id")
                            if mid:
                                if mid in seen:
                                    continue
                                seen.add(mid)
                            extra_msgs.append(m)
                except Exception:
                    extra_msgs = []
                msgs = msgs + extra_msgs
            updated_at_raw = data.get("updated_at")
            if journal_ts and _iso_key(journal_ts) > _iso_key(updated_at_raw or ""):
                updated_at_raw = journal_ts

            lines = [
                f"# [jcode] {title}",
                "",
                f"- **Agent**: `jcode`",
                f"- **ID**: `{sid}`",
                f"- **Plik**: `{f}`",
                f"- **Katalog**: `{cwd}`",
                f"- **Model**: `{data.get('model', '?')}`",
                f"- **Utworzona**: {fmt_ts(data.get('created_at'))} | **Zaktualizowana**: {fmt_ts(updated_at_raw)}",
                f"- **Wiadomości**: {len(msgs)}",
                "",
            ]
            for m in msgs:
                if not isinstance(m, dict):
                    continue
                role = m.get("role", "message")
                lines.append(f"## [{role}]")
                content = m.get("content") or ""
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict):
                            if part.get("type") == "text":
                                lines.append(part.get("text", ""))
                            elif part.get("type") == "tool_use":
                                lines.append(f"> **tool** `{part.get('name')}`: `{_truncate_mid(json.dumps(part.get('input',{})), 4000)}`")
                            elif part.get("type") == "tool_result":
                                lines.append(f"> **tool_result**: `{_truncate_mid(part.get('content'), 800)}`")
                        else:
                            lines.append(str(part))
                else:
                    lines.append(str(content))
                lines.append("")

            items.append(SessionItem(
                agent="jcode",
                id=sid,
                title=title[:80],
                directory=cwd,
                created_at=fmt_ts(data.get("created_at") or f.stat().st_ctime),
                updated_at=fmt_ts(updated_at_raw or f.stat().st_mtime),
                message_count=len(msgs),
                model=str(data.get("model", "")),
                raw_path=str(f),
                text_markdown="\n".join(lines)
            ))
    except Exception as e:
        print(f"Error reading jcode sessions: {e}", file=sys.stderr)
    return items


# -------------------------------------------------------------
# 6. antigravity
# -------------------------------------------------------------
def load_antigravity_sessions(limit: int = 50) -> List[SessionItem]:
    if not ANTIGRAVITY_BRAIN.exists():
        return []
    items = []
    try:
        conv_dirs = [d for d in ANTIGRAVITY_BRAIN.iterdir() if d.is_dir()]
        conv_dirs = sorted(conv_dirs, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]

        for c_dir in conv_dirs:
            t_file = c_dir / ".system_generated" / "logs" / "transcript.jsonl"
            if not t_file.exists():
                t_file = c_dir / ".system_generated" / "logs" / "transcript_full.jsonl"
            if not t_file.exists():
                continue

            sid = c_dir.name
            first_user_req = ""
            steps = []
            with open(t_file, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if not line.strip():
                        continue
                    try:
                        step = json.loads(line)
                        steps.append(step)
                        if not first_user_req and step.get("type") == "USER_INPUT":
                            first_user_req = (step.get("content") or "").replace("<USER_REQUEST>", "").replace("</USER_REQUEST>", "").strip()[:80]
                    except Exception:
                        pass

            display_title = (first_user_req or sid).replace("\n", " ")

            lines = [
                f"# [antigravity] {display_title}",
                "",
                f"- **Agent**: `antigravity`",
                f"- **ID**: `{sid}`",
                f"- **Katalog Brain**: `{c_dir}`",
                f"- **Log**: `{t_file}`",
                f"- **Czas**: {fmt_ts(c_dir.stat().st_mtime)}",
                f"- **Kroki / wpisy**: {len(steps)}",
                "",
            ]

            for s in steps:
                s_type = s.get("type", "step")
                src = s.get("source", "")
                lines.append(f"## [{src} · {s_type}]")
                content = s.get("content") or ""
                if content:
                    lines.append(content)
                tool_calls = s.get("tool_calls") or []
                for tc in tool_calls:
                    lines.append(f"> **tool call** `{tc.get('toolName')}`: `{_truncate_mid(json.dumps(tc.get('args',{})), 4000)}`")
                lines.append("")

            items.append(SessionItem(
                agent="antigravity",
                id=sid,
                title=display_title[:80],
                directory=str(c_dir),
                created_at=fmt_ts(c_dir.stat().st_ctime),
                updated_at=fmt_ts(c_dir.stat().st_mtime),
                message_count=len(steps),
                model="",
                raw_path=str(t_file),
                text_markdown="\n".join(lines)
            ))
    except Exception as e:
        print(f"Error reading antigravity sessions: {e}", file=sys.stderr)
    return items


# -------------------------------------------------------------
# 7. cursor
# -------------------------------------------------------------
def load_cursor_sessions(limit: int = 50) -> List[SessionItem]:
    """Read Cursor composer sessions from state.vscdb.

    composerHeaders table holds metadata (composerId, workspaceId, timestamps).
    cursorDiskKV holds content under keys like 'composer.content.<hash>' and
    'composerData:<uuid>'.
    """
    if not CURSOR_STATE_DB.exists():
        return []
    items = []
    try:
        c = sqlite3.connect(str(CURSOR_STATE_DB))
        c.row_factory = sqlite3.Row

        # Build a map of composerId -> composer data blob from cursorDiskKV
        composer_data_map: Dict[str, Any] = {}
        try:
            for row in c.execute("SELECT key, value FROM cursorDiskKV WHERE key LIKE 'composerData:%'"):
                cid = row["key"].split(":", 1)[1] if ":" in row["key"] else row["key"]
                val = row["value"]
                if isinstance(val, bytes):
                    val = val.decode("utf-8", errors="replace")
                try:
                    composer_data_map[cid] = json.loads(val)
                except Exception:
                    composer_data_map[cid] = {"raw": str(val)[:500]}
        except Exception:
            pass

        rows = c.execute(
            "SELECT composerId, workspaceId, createdAt, lastUpdatedAt, isArchived, subagentTypeName, value "
            "FROM composerHeaders ORDER BY lastUpdatedAt DESC LIMIT ?",
            (limit,)
        ).fetchall()

        for row in rows:
            cid = row["composerId"]
            created_ts = row["createdAt"]
            updated_ts = row["lastUpdatedAt"]
            workspace_id = row["workspaceId"] or ""
            is_archived = bool(row["isArchived"])
            subagent = row["subagentTypeName"] or ""

            # Parse the value JSON for title / model info
            title = ""
            model = ""
            msg_count = 0
            raw_value = row["value"]
            if raw_value:
                if isinstance(raw_value, bytes):
                    raw_value = raw_value.decode("utf-8", errors="replace")
                try:
                    vdata = json.loads(raw_value)
                    title = vdata.get("name") or vdata.get("title") or ""
                    model = vdata.get("model") or ""
                    msgs = vdata.get("conversation") or vdata.get("messages") or []
                    msg_count = len(msgs) if isinstance(msgs, list) else 0
                except Exception:
                    pass

            # Also check composer_data_map for richer data
            cdata = composer_data_map.get(cid, {})
            if not title:
                title = cdata.get("name") or cdata.get("title") or ""
            if not model:
                model = cdata.get("model") or ""
            if not msg_count:
                conversation = cdata.get("conversation") or cdata.get("messages") or []
                msg_count = len(conversation) if isinstance(conversation, list) else 0

            # Render first few messages as markdown preview
            lines = [
                f"# [cursor] {title or cid}",
                "",
                f"- **Agent**: `cursor`",
                f"- **ID**: `{cid}`",
                f"- **Workspace**: `{workspace_id}`",
                f"- **Model**: `{model or '?'}`",
                f"- **Archived**: {is_archived}",
                f"- **Subagent**: `{subagent}`" if subagent else "",
                f"- **Utworzona**: {fmt_ts(created_ts)} | **Zaktualizowana**: {fmt_ts(updated_ts)}",
                f"- **Wiadomości**: {msg_count}",
                "",
            ]

            conversation = cdata.get("conversation") or cdata.get("messages") or []
            if isinstance(conversation, list):
                for m in conversation[:30]:  # cap at 30 messages for rendering
                    if not isinstance(m, dict):
                        continue
                    role = m.get("role") or m.get("type") or "message"
                    lines.append(f"## [{role}]")
                    # text content
                    text = m.get("text") or m.get("content") or ""
                    if isinstance(text, list):
                        for part in text:
                            if isinstance(part, dict) and part.get("type") == "text":
                                lines.append(part.get("text", ""))
                            elif isinstance(part, str):
                                lines.append(part)
                    elif text:
                        lines.append(str(text))
                    # tool calls
                    tool_calls = m.get("toolCalls") or m.get("tool_calls") or []
                    for tc in tool_calls:
                        if isinstance(tc, dict):
                            tc_name = tc.get("name") or tc.get("toolName") or "?"
                            tc_args = tc.get("args") or tc.get("input") or {}
                            lines.append(f"> **tool** `{tc_name}`: `{_truncate_mid(json.dumps(tc_args, ensure_ascii=False), 4000)}`")
                    lines.append("")

            display_title = (title or cid).replace("\n", " ")

            items.append(SessionItem(
                agent="cursor",
                id=cid,
                title=display_title[:80],
                directory=workspace_id,
                created_at=fmt_ts(created_ts),
                updated_at=fmt_ts(updated_ts),
                message_count=msg_count,
                model=model,
                raw_path=str(CURSOR_STATE_DB),
                text_markdown="\n".join(l for l in lines if l is not None)
            ))

        c.close()
    except Exception as e:
        print(f"Error reading cursor sessions: {e}", file=sys.stderr)
    return items


# -------------------------------------------------------------
# 8. droid (Factory AI)
# -------------------------------------------------------------
def load_droid_sessions(limit: int = 50) -> List[SessionItem]:
    """Read Factory Droid sessions from ~/.factory/sessions/**/*.jsonl.

    Each workspace has its own folder (encoded path), containing:
    - <uuid>.jsonl — sequence of JSON objects (type: message, agent_turn_outcome, etc.)
    - <uuid>.settings.json — optional session metadata
    """
    if not DROID_SESSIONS_DIR.exists():
        return []
    items = []
    try:
        # Find all .jsonl files, sort by mtime
        jsonl_files = sorted(
            DROID_SESSIONS_DIR.rglob("*.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]

        for f in jsonl_files:
            # Decode workspace path from parent dir name
            workspace_encoded = f.parent.name  # e.g. "-C-Users-Mateusz-Desktop-root_worksapce"
            workspace_path = workspace_encoded.replace("-", "\\", 1).replace("-", "/")
            # Better: just use the encoded name as-is but replace leading - and dashes
            workspace_display = workspace_encoded.lstrip("-").replace("-", "/")

            sid = f.stem  # UUID

            # Load optional .settings.json
            settings_file = f.with_suffix(".settings.json")
            session_meta: Dict[str, Any] = {}
            if settings_file.exists():
                try:
                    with open(settings_file, "r", encoding="utf-8", errors="replace") as sf:
                        session_meta = json.load(sf)
                except Exception:
                    pass

            # Parse JSONL events
            events: List[Dict[str, Any]] = []
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if not line.strip():
                        continue
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        pass

            # Reconstruct conversation from message events
            messages = [e for e in events if e.get("type") == "message"]
            model = ""
            first_user_text = ""

            lines = [
                f"# [droid] {sid}",
                "",
                f"- **Agent**: `droid`",
                f"- **ID**: `{sid}`",
                f"- **Workspace**: `{workspace_display}`",
                f"- **Plik**: `{f}`",
                f"- **Zdarzenia**: {len(events)}",
                f"- **Czas**: {fmt_ts(f.stat().st_mtime)}",
                "",
            ]

            for ev in events:
                ev_type = ev.get("type", "")
                if ev_type == "message":
                    msg = ev.get("message", {})
                    role = msg.get("role", "message")
                    lines.append(f"## [{role}]")
                    content = msg.get("content") or []
                    if isinstance(content, list):
                        for part in content:
                            if isinstance(part, dict):
                                if part.get("type") == "text":
                                    txt = part.get("text", "")
                                    lines.append(txt)
                                    if not first_user_text and role == "user":
                                        first_user_text = txt[:60]
                                elif part.get("type") == "tool_use":
                                    lines.append(f"> **tool** `{part.get('name')}`: `{_truncate_mid(json.dumps(part.get('input', {})), 800)}`")
                                elif part.get("type") == "tool_result":
                                    lines.append(f"> **tool_result**: `{_truncate_mid(part.get('content', ''), 4000)}`")
                            elif isinstance(part, str):
                                lines.append(part)
                    elif isinstance(content, str):
                        lines.append(content)
                        if not first_user_text and role == "user":
                            first_user_text = content[:60]
                    lines.append("")
                elif ev_type == "agent_turn_outcome":
                    reason = ev.get("reason", "")
                    result = ev.get("resultKind", "")
                    lines.append(f"> *turn outcome*: `{reason}` / `{result}`")
                    lines.append("")

            display_title = (first_user_text.strip() or sid).replace("\n", " ")

            items.append(SessionItem(
                agent="droid",
                id=sid,
                title=display_title[:80],
                directory=workspace_display,
                created_at=fmt_ts(f.stat().st_ctime),
                updated_at=fmt_ts(f.stat().st_mtime),
                message_count=len(messages),
                model=model,
                raw_path=str(f),
                text_markdown="\n".join(lines)
            ))
    except Exception as e:
        print(f"Error reading droid sessions: {e}", file=sys.stderr)
    return items


def load_deepseek_sessions(limit: int = 50) -> List[SessionItem]:
    """Read both standalone harness JSONL store and DSH runtime zstd/jsonl sessions (v4 format supported), filtered to current workspace."""
    items = []
    session_paths = []
    current_workspace = ROOT.name.lower()

    if DEEPSEEK_SESSIONS_DIR.exists():
        session_paths.extend(DEEPSEEK_SESSIONS_DIR.glob("*.jsonl"))

    if DSH_SESSIONS_DIR.exists():
        for p in DSH_SESSIONS_DIR.glob("**/*.jsonl"):
            if current_workspace in str(p).lower():
                session_paths.append(p)
        try:
            import zstandard as zstd
            for p in DSH_SESSIONS_DIR.glob("**/*.zstd"):
                if current_workspace in str(p).lower():
                    session_paths.append(p)
        except ImportError:
            pass

    session_paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    for path in session_paths[:limit]:
        events = []
        sid = path.stem
        model_name = ""
        provider_name = ""
        timestamps = []

        try:
            if path.name.endswith(".zstd"):
                import zstandard as zstd
                dctx = zstd.ZstdDecompressor()
                with open(path, "rb") as f:
                    with dctx.stream_reader(f) as reader:
                        decompressed = reader.read()
                lines = decompressed.decode("utf-8", errors="ignore").splitlines()
            else:
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

            for raw in lines:
                try:
                    obj = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if not isinstance(obj, dict):
                    continue

                t = obj.get("type", "")
                data = obj.get("data", {})
                time_val = obj.get("time")
                if time_val:
                    timestamps.append(time_val)

                if t == "session":
                    sid = obj.get("id", sid)
                elif t in ("request/header", "request/context"):
                    cfg = data.get("header", {}).get("config", {}) or data.get("config", {}) or data
                    if isinstance(cfg, dict):
                        if cfg.get("provider") and not provider_name:
                            provider_name = cfg.get("provider")
                        if cfg.get("model") and not model_name:
                            model_name = cfg.get("model")
                elif t == "user/message":
                    content_blocks = data.get("content", [])
                    text_parts = [b.get("text", "") for b in content_blocks if isinstance(b, dict) and b.get("type") == "text"]
                    text = "\n".join(filter(None, text_parts))
                    boilerplate_markers = (
                        "<system-reminder>",
                        "Current runtime context",
                        "Instructions from: AGENTS.md",
                        "Instructions from: CLAUDE.md",
                        "<available_skills>",
                    )
                    if text and not any(marker in text for marker in boilerplate_markers):
                        events.append({"role": "user", "content": text, "timestamp": time_val})
                elif t in ("tool/call", "tool/result", "assistant/reasoning", "reasoning"):
                    payload = data if isinstance(data, dict) else {}
                    text = payload.get("text") or payload.get("content") or payload.get("output") or payload.get("name")
                    if isinstance(text, (dict, list)):
                        text = json.dumps(text, ensure_ascii=False)
                    if text:
                        events.append({"role": "tool" if "tool/" in t else "reasoning", "content": str(text), "timestamp": time_val})
                elif t in ("assistant/message", "system/message"):
                    msg = data.get("message", {})
                    role = msg.get("role", t.split("/")[0])
                    if not model_name and msg.get("model"):
                        model_name = msg.get("model")
                    if not provider_name and msg.get("provider"):
                        provider_name = msg.get("provider")
                    content_blocks = msg.get("content", [])
                    if isinstance(content_blocks, str):
                        text = content_blocks
                    elif isinstance(content_blocks, list):
                        text_parts = []
                        for b in content_blocks:
                            if isinstance(b, dict):
                                if b.get("type") == "text":
                                    text_parts.append(b.get("text", ""))
                                elif "text" in b:
                                    text_parts.append(str(b.get("text", "")))
                            elif isinstance(b, str):
                                text_parts.append(b)
                        text = "\n".join(filter(None, text_parts))
                    else:
                        text = str(content_blocks)
                    if text:
                        events.append({"role": role, "content": text, "timestamp": time_val})
                elif "role" in obj and "content" in obj:
                    events.append(obj)
        except Exception:
            continue

        if not events:
            continue

        first_prompt = next((str(e.get("content", "")) for e in events if e.get("role") in {"user", "prompt"}), sid)

        lines_md = [
            f"# [deepseek] {first_prompt[:80]}",
            "",
            "- **Agent**: `deepseek`",
            f"- **ID**: `{sid}`",
            f"- **Model**: `{provider_name}/{model_name}`" if (model_name or provider_name) else "- **Model**: `?`",
            f"- **Wiadomości**: {len(events)}",
            ""
        ]
        for event in events:
            lines_md.extend([f"## [{event.get('role', '?')}]", str(event.get("content", "")), ""])

        t_list = [e.get("timestamp") for e in events if e.get("timestamp")]
        if not t_list and timestamps:
            t_list = timestamps

        created = fmt_ts(t_list[0] / 1000.0) if t_list and isinstance(t_list[0], (int, float)) else fmt_ts(path.stat().st_ctime)
        updated = fmt_ts(t_list[-1] / 1000.0) if t_list and isinstance(t_list[-1], (int, float)) else fmt_ts(path.stat().st_mtime)

        items.append(SessionItem(
            agent="deepseek",
            id=sid,
            title=first_prompt[:80].replace("\n", " "),
            directory=str(path.parent),
            created_at=created,
            updated_at=updated,
            message_count=len(events),
            model=model_name,
            raw_path=str(path),
            text_markdown="\n".join(lines_md),
            extra={"provider": provider_name}
        ))
    return items


# -------------------------------------------------------------
# 9. cline (desktop app / CLI — ~/.cline/data/sessions/*/*.messages.json)
# -------------------------------------------------------------
def _cline_clean(text: str) -> str:
    """Strip Cline's <user_input mode=...> wrapper from user prompts."""
    if not isinstance(text, str):
        return str(text)
    text = re.sub(r"</?user_input[^>]*>", "", text).strip()
    return text


def _cline_result_text(content: Any) -> str:
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            else:
                parts.append(json.dumps(item, ensure_ascii=False))
        return "\n".join(parts)
    return str(content)


def load_cline_sessions(limit: int = 50) -> List[SessionItem]:
    """Read Cline app/CLI sessions from ~/.cline/data/sessions/<id>/.

    Each session dir holds <id>.messages.json
    ({sessionId, updated_at, messages: [{id, role, content, ts(ms)}]})
    plus an <id>.json sidecar with run metadata
    (source desktop/cli, provider, model, cwd, started_at, status).
    """
    if not CLINE_SESSIONS_DIR.exists():
        return []
    items = []
    try:
        dirs = sorted(
            [d for d in CLINE_SESSIONS_DIR.iterdir() if d.is_dir()],
            key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
        for d in dirs:
            msg_files = sorted(d.glob("*.messages.json"),
                               key=lambda p: p.stat().st_mtime, reverse=True)
            if not msg_files:
                continue
            mf = msg_files[0]
            try:
                data = json.loads(mf.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            sid = str(data.get("sessionId") or d.name)
            meta: Dict[str, Any] = {}
            meta_file = d / mf.name.replace(".messages.json", ".json")
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8", errors="replace"))
                except Exception:
                    meta = {}
            msgs = data.get("messages") or []
            provider = str(meta.get("provider") or "")
            model = str(meta.get("model") or "")
            cwd = str(meta.get("cwd") or meta.get("workspace_root") or "")

            first_user = ""
            lines = [
                f"# [cline] {sid}",
                "",
                f"- **Agent**: `cline`",
                f"- **ID**: `{sid}`",
                f"- **Katalog**: `{cwd}`",
                f"- **Model**: `{provider + '/' if provider else ''}{model or '?'}`",
                f"- **Źródło**: `{meta.get('source') or '?'}` · **Status**: `{meta.get('status') or '?'}`",
                f"- **Utworzona**: {fmt_ts(meta.get('started_at'))} | **Zaktualizowana**: {fmt_ts(data.get('updated_at') or mf.stat().st_mtime)}",
                f"- **Wiadomości**: {len(msgs)}",
                "",
            ]
            for m in msgs:
                if not isinstance(m, dict):
                    continue
                role = m.get("role", "message")
                lines.append(f"## [{role}]")
                content = m.get("content")
                if isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            lines.append(str(block))
                            continue
                        b_type = block.get("type")
                        if b_type == "text":
                            txt = _cline_clean(block.get("text", ""))
                            lines.append(txt)
                            if not first_user and role == "user" and txt:
                                first_user = txt[:60]
                        elif b_type == "thinking":
                            txt = block.get("thinking", "")
                            if txt:
                                lines.append(f"<details><summary>thinking</summary>\n\n{txt[:2500]}\n\n</details>")
                        elif b_type == "tool_use":
                            lines.append(f"> **tool** `{block.get('name', '?')}`: `{_truncate_mid(json.dumps(block.get('input', {}), ensure_ascii=False), 4000)}`")
                        elif b_type == "tool_result":
                            lines.append(f"> **tool_result**: `{_truncate_mid(_cline_result_text(block.get('content', '')), 4000)}`")
                        elif b_type == "image":
                            lines.append(f"> [image `{block.get('mediaType', '?')}`]")
                        else:
                            lines.append(f"> `[{b_type}]` `{_truncate_mid(json.dumps(block, ensure_ascii=False), 800)}`")
                elif isinstance(content, str):
                    txt = _cline_clean(content)
                    lines.append(txt)
                    if not first_user and role == "user" and txt:
                        first_user = txt[:60]
                lines.append("")

            display_title = (first_user.strip() or sid).replace("\n", " ")
            items.append(SessionItem(
                agent="cline",
                id=sid,
                title=display_title[:80],
                directory=cwd,
                created_at=fmt_ts(meta.get("started_at") or mf.stat().st_ctime),
                updated_at=fmt_ts(data.get("updated_at") or mf.stat().st_mtime),
                message_count=len(msgs),
                model=f"{provider}/{model}" if provider and model else model,
                raw_path=str(mf),
                text_markdown="\n".join(lines)
            ))
    except Exception as e:
        print(f"Error reading cline sessions: {e}", file=sys.stderr)
    return items


def get_all_sessions(agent_filter: Optional[str] = None, limit_per_agent: int = 50, days: Optional[int] = None) -> List[SessionItem]:
    all_sessions: List[SessionItem] = []

    ag = agent_filter.lower() if agent_filter else "all"

    if ag in ("all", "opencode"):
        all_sessions.extend(load_opencode_sessions(limit_per_agent))
    if ag in ("all", "goose"):
        all_sessions.extend(load_goose_sessions(limit_per_agent))
    if ag in ("all", "hermes"):
        all_sessions.extend(load_hermes_sessions(limit_per_agent))
    if ag in ("all", "pi"):
        all_sessions.extend(load_pi_sessions(limit_per_agent))
    if ag in ("all", "omp", "oh-my-pi", "ohmy-pi", "oh_my_pi"):
        all_sessions.extend(load_omp_sessions(limit_per_agent))
    if ag in ("all", "jcode"):
        all_sessions.extend(load_jcode_sessions(limit_per_agent))
    if ag in ("all", "antigravity"):
        all_sessions.extend(load_antigravity_sessions(limit_per_agent))
    if ag in ("all", "cursor"):
        all_sessions.extend(load_cursor_sessions(limit_per_agent))
    if ag in ("all", "droid"):
        all_sessions.extend(load_droid_sessions(limit_per_agent))
    if ag in ("all", "deepseek"):
        all_sessions.extend(load_deepseek_sessions(limit_per_agent))
    if ag in ("all", "cline"):
        all_sessions.extend(load_cline_sessions(limit_per_agent))

    if days is not None and days > 0:
        cutoff = datetime.now() - timedelta(days=days)
        filtered = []
        for s in all_sessions:
            ts_str = s.updated_at or s.created_at
            if ts_str:
                try:
                    dt = datetime.strptime(ts_str[:19], "%Y-%m-%d %H:%M:%S")
                    if dt >= cutoff:
                        filtered.append(s)
                except Exception:
                    pass  # skip sessions with unparseable dates when filtering
            # sessions with no date at all are excluded when days filter is active
        all_sessions = filtered

    # sort newest first
    all_sessions.sort(key=lambda x: x.updated_at or x.created_at, reverse=True)
    return all_sessions


_UNSAFE_FS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _safe_name(s: SessionItem) -> str:
    """Windows-safe, sortable fragment for an export filename.

    Titles come from user prompts and agent output, so they carry slashes,
    colons and newlines that Windows will not accept in a filename. Keep the
    head of the title (it identifies the session better than the id) and fall
    back to the id when sanitising leaves nothing.
    """
    raw = s.title or s.id
    cleaned = _UNSAFE_FS_CHARS.sub("_", raw).strip().rstrip(".")
    cleaned = re.sub(r"\s+", "_", cleaned)
    if len(cleaned) > 60:
        cleaned = cleaned[:60].rstrip("_")
    if not cleaned:
        cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", s.id)[:60] or "session"
    return cleaned


def _empty_dir(out_dir: Path) -> None:
    """Recreate out_dir as an empty folder.

    A whole-tree rmtree fails on Windows when another process holds the
    directory itself open (WinError 32: Explorer on the folder, indexer,
    AV scan). Emptying the contents in place survives that, so try rmtree
    first for a truly clean slate and fall back to per-entry deletion.
    Entries that stay locked are reported, not fatal: the export continues
    and the stale file is named in the warning.
    """
    try:
        if out_dir.exists():
            # This folder is a derived mirror, rebuilt from scratch every run.
            # Removing the whole dir (not just its contents) also drops
            # whatever name this session happened to invent.
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True)
        return
    except OSError:
        pass
    out_dir.mkdir(parents=True, exist_ok=True)
    for child in sorted(out_dir.iterdir()):
        try:
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
        except OSError as e:
            print(f"Ostrzezenie: pomijam zablokowany plik {child.name}: {e}", file=sys.stderr)


def _session_header(s: SessionItem, idx: int = 1, total: int = 1,
                    sha256: Optional[str] = None,
                    message_count: Optional[int] = None,
                    blocks: Optional[int] = None,
                    turns: Optional[int] = None,
                    truncated: Optional[bool] = None,
                    parent: Optional[str] = None,
                    losses: Optional[str] = None,
                    flag: Optional[str] = None,
                    duration: Optional[str] = None,
                    last_line: Optional[str] = None,
                    source_ref: Optional[str] = None,
                    exit_info: Optional[str] = None,
                    artifact_info: Optional[str] = None) -> str:
    """Provenance header prepended to an exported session (a bare transcript
    with no agent/id/date is not self-describing once it sits in a folder).

    `blocks`/`turns`/`truncated`/`parent`/`losses`/`flag`/`duration`/
    `last_line`/`source_ref`/`exit_info`/`artifact_info` are optional audit
    fields: they are only emitted when explicitly supplied, so single-file
    exports (`agent_sessions.py last`) keep the exact legacy header, and only
    the merged artifact pays for the extra honesty.
    """
    source_line = f"- **Plik zrodlowy**: {s.raw_path}"
    if source_ref:
        source_line += f"  ({source_ref})"
    lines = [
        f"# Sesja {idx}/{total}: {s.title}",
        f"",
        f"- **Agent**: {s.agent}",
        f"- **ID**: `{s.id}`",
        f"- **Zaktualizowano**: {s.updated_at or s.created_at}",
        f"- **Model**: {s.model or '-'}",
        f"- **Katalog**: {s.directory}",
        f"- **Wiadomosci**: {s.message_count if message_count is None else message_count}",
        source_line,
    ]
    if blocks is not None:
        lines.append(f"- **Bloki**: {blocks}")
    if turns is not None:
        lines.append(f"- **Tury**: {turns}")
    if truncated is not None:
        lines.append(f"- **Uciete**: {'tak' if truncated else 'nie'}")
    if parent:
        lines.append(f"- **Parent**: `{parent}`")
    if duration:
        lines.append(f"- **Czas**: {duration}")
    if losses:
        lines.append(f"- **Straty**: {losses}")
    if exit_info:
        lines.append(f"- **Exit**: {exit_info}")
    if artifact_info:
        lines.append(f"- **Artefakty**: {artifact_info}")
    if flag:
        lines.append(f"- **Flaga (wzmianka)**: `{flag}`")
    if last_line:
        lines.append(f"- **Ostatnia linia**: {last_line}")
    if sha256:
        lines.append(f"- **SHA256**: `{sha256}`")
    lines += ["", "---", ""]
    return "\n".join(lines)


def strip_native_header(md: str) -> str:
    """Remove the header a loader already embeds in `text_markdown`.

    Every loader starts its markdown with `# [agent] title`, a blank line, a
    metadata bullet list and a blank line. Callers that prepend their own
    provenance header must strip it, or every session carries two copies.
    Unknown shapes are returned unchanged.
    """
    lines = md.splitlines()
    if not lines or not lines[0].startswith("# ["):
        return md
    i = 1
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == "" or stripped == "---" or stripped.startswith("- **"):
            i += 1
            continue
        break
    return "\n".join(lines[i:]).lstrip("\n")


def strip_harness_blocks(md: str) -> str:
    """Collapse `## [idle]`-style sections instead of rendering them as turns.

    Text-bearing events (`system`, `synthetic`, `developer`) are kept in one
    collapsed `<details>` block: dropping them silently loses audit context,
    rendering them as turns turns the transcript into a harness log.
    """
    out: List[str] = []
    kept: Dict[str, List[str]] = {}
    role: Optional[str] = None
    buf: List[str] = []

    def flush() -> None:
        nonlocal role, buf
        if role is None:
            out.extend(buf)
        elif role in HARNESS_MESSAGE_TYPES:
            text = "\n".join(buf).strip()
            if role in TEXT_HARNESS_MESSAGE_TYPES and text:
                kept.setdefault(role, []).append(text)
        else:
            out.append(f"## [{role}]")
            out.extend(buf)
        role, buf = None, []

    # A `## [x]` line inside a `<details>` block is quoted text, not a turn
    # heading. Tracking depth keeps reasoning/system content from being split.
    details_depth = 0
    for line in md.splitlines():
        m = None if details_depth > 0 else re.match(r"^## \[([^\]]+)\]$", line)
        if m:
            flush()
            role = m.group(1)
        else:
            buf.append(line)
            details_depth += line.count("<details") - line.count("</details>")
            if details_depth < 0:
                details_depth = 0
    flush()

    if kept:
        summary = ", ".join(f"{k}×{len(v)}" for k, v in sorted(kept.items()))
        out.append(f"<details><summary>Zdarzenia harnessu ({summary})</summary>")
        out.append("")
        for name in sorted(kept):
            for text in kept[name]:
                out.append(f"**{name}**: {text[:2000]}")
                out.append("")
        out.append("</details>")
        out.append("")
    return "\n".join(out)


def strip_reasoning_blocks(md: str) -> str:
    """Drop `<details>` reasoning/thinking blocks (their text was capped anyway).

    Parsed line-by-line, not with a non-greedy regex: a reasoning trace may
    itself contain a `## [foo]` line (quoted output, a code block), which a
    lookahead would treat as the end of the block and cut the trace short.

    `<details>` depth is counted so a nested block ends at *its* closing tag.
    The source data sometimes contains an unclosed `<details>` (the harness cut
    the part mid-stream). In that case the block ends at the next `## [role]`
    heading, not at `</details>` — otherwise a single malformed part would leak
    the entire reasoning trace into the export.
    """
    opener = re.compile(r"<details><summary>(?:reasoning|thinking)</summary>", re.I)
    # An unclosed reasoning block ends at the next *message* heading. A quoted
    # `## [not-a-turn]` inside a trace is not enough evidence, so only headings
    # that name a role the renderers actually emit terminate the block.
    terminator = re.compile(
        r"^## \[(?:"
        + "|".join(sorted(re.escape(t) for t in MESSAGE_BOUNDARY_ROLES))
        + r")\]$")
    out: List[str] = []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not opener.search(line):
            out.append(line)
            i += 1
            continue
        depth = line.count("<details") - line.count("</details>")
        i += 1
        while i < len(lines) and depth > 0:
            if terminator.match(lines[i]):
                break
            depth += lines[i].count("<details") - lines[i].count("</details>")
            i += 1
    return "\n".join(out)


def render_session_body(s: SessionItem, *, include_reasoning: bool = True) -> str:
    """Canonical session body: one header (the caller's), no harness events."""
    body = strip_native_header(s.text_markdown)
    if not include_reasoning:
        # Strip reasoning before harness filtering: a reasoning trace can quote
        # `## [system]`-like lines, which the harness parser would otherwise
        # mistake for real harness events.
        body = strip_reasoning_blocks(body)
    body = strip_harness_blocks(body)
    body = body.strip()
    return body + "\n" if body else ""


BROWSE_HTML_TEMPLATE = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__PAGE_TITLE__</title>
<style>
:root {
  --bg: #0f172a;
  --bg-card: #1e293b;
  --bg-panel: #0b1120;
  --text: #f1f5f9;
  --text-muted: #94a3b8;
  --border: #334155;
  --accent: #38bdf8;
  --accent-hover: #0284c7;
  --badge-opencode: #60a5fa;
  --badge-goose: #34d399;
  --badge-hermes: #fbbf24;
  --badge-pi: #f472b6;
  --badge-omp: #e879a8;
  --badge-jcode: #a78bfa;
  --badge-antigravity: #4ade80;
  --badge-cursor: #818cf8;
  --badge-droid: #fb923c;
}
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  margin: 0;
  color: var(--text);
  background: var(--bg);
  line-height: 1.5;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.header {
  padding: 0.75rem 1.25rem;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}
.header h1 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.filters {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.search-box {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.85rem;
  outline: none;
  min-width: 180px;
}
.search-box:focus {
  border-color: var(--accent);
}
.agent-filter-btn {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-muted);
  padding: 0.35rem 0.7rem;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s ease;
}
.agent-filter-btn:hover {
  background: #273549;
  color: var(--text);
}
.agent-filter-btn.active {
  background: var(--accent);
  color: #0f172a;
  font-weight: 600;
  border-color: var(--accent);
}
.days-control {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  font-size: 0.8rem;
  color: var(--text-muted);
}
.days-control label {
  font-size: 0.78rem;
}
.days-select {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.8rem;
  outline: none;
  cursor: pointer;
}
.days-select:focus {
  border-color: var(--accent);
}
.days-input {
  width: 50px;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.8rem;
  outline: none;
  text-align: center;
}
.days-input:focus {
  border-color: var(--accent);
}
.wrap {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.sidebar {
  width: 380px;
  min-width: 320px;
  border-right: 1px solid var(--border);
  background: var(--bg-panel);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.session-item {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  border-bottom: 1px solid #1e293b;
  padding: 0.75rem 1rem;
  cursor: pointer;
  color: var(--text);
  transition: background 0.15s;
}
.session-item:hover {
  background: #1e293b;
}
.session-item.active {
  background: #24344d;
  border-left: 3px solid var(--accent);
}
.item-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
  gap: 0.5rem;
}
.badge {
  font-size: 0.7rem;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: bold;
  letter-spacing: 0.05em;
  background: #334155;
  color: #fff;
}
.badge-opencode { background: #1d4ed8; color: #bfdbfe; }
.badge-goose { background: #065f46; color: #a7f3d0; }
.badge-hermes { background: #854d0e; color: #fde68a; }
.badge-pi { background: #831843; color: #fbcfe8; }
.badge-omp { background: #701a3a; color: #fecdd3; }
.badge-jcode { background: #581c87; color: #e9d5ff; }
.badge-antigravity { background: #14532d; color: #bbf7d0; }
.badge-cursor { background: #3730a3; color: #c7d2fe; }
.badge-droid { background: #7c2d12; color: #fed7aa; }
.badge-cline { background: #0e7490; color: #cffafe; }

.item-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}
.item-title {
  font-size: 0.88rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  word-break: break-word;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.item-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.main-view {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}
.view-header {
  border-bottom: 1px solid var(--border);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}
.view-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.5rem;
}
.view-title {
  margin: 0;
  font-size: 1.35rem;
  word-break: break-word;
}
.btn-bar {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.action-btn {
  background: var(--accent);
  color: #0f172a;
  border: none;
  padding: 0.45rem 0.9rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.82rem;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  transition: background 0.15s;
}
.action-btn:hover {
  background: var(--accent-hover);
}
.action-btn.secondary {
  background: var(--bg-card);
  color: var(--text);
  border: 1px solid var(--border);
}
.action-btn.secondary:hover {
  background: #334155;
}
.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
  background: var(--bg-panel);
  padding: 0.75rem 1rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  font-size: 0.8rem;
  color: var(--text-muted);
}
.meta-grid span strong {
  color: var(--text);
}
.content-area {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.25rem;
  overflow-x: auto;
}
pre.md {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 0.875rem;
  line-height: 1.6;
}
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: #10b981;
  color: #fff;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  font-weight: 600;
  font-size: 0.85rem;
  display: none;
  animation: fadeIn 0.2s;
  z-index: 999;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
</head>
<body>

<header class="header">
  <h1><span>⚡</span> Multi-Agent Unified Sessions</h1>
  <div class="filters">
    <input type="text" id="search" class="search-box" placeholder="Szukaj sesji / promptu...">
    <div class="days-control">
      <label for="daysSelect">📅 Dni wstecz:</label>
      <select id="daysSelect" class="days-select">
        <option value="1">1 dzień</option>
        <option value="3" selected>3 dni</option>
        <option value="7">7 dni</option>
        <option value="14">14 dni</option>
        <option value="30">30 dni</option>
        <option value="all">Wszystkie</option>
        <option value="custom">Inne...</option>
      </select>
      <input type="number" id="daysCustom" class="days-input" style="display:none;" min="1" max="999" value="7">
    </div>
    <button class="agent-filter-btn active" data-agent="all">Wszystkie</button>
    <button class="agent-filter-btn" data-agent="opencode">opencode</button>
    <button class="agent-filter-btn" data-agent="goose">goose</button>
    <button class="agent-filter-btn" data-agent="hermes">hermes</button>
    <button class="agent-filter-btn" data-agent="pi">pi</button>
    <button class="agent-filter-btn" data-agent="omp">omp</button>
    <button class="agent-filter-btn" data-agent="jcode">jcode</button>
    <button class="agent-filter-btn" data-agent="antigravity">antigravity</button>
    <button class="agent-filter-btn" data-agent="cursor">cursor</button>
    <button class="agent-filter-btn" data-agent="droid">droid</button>
    <button class="agent-filter-btn" data-agent="cline">cline</button>
  </div>
</header>

<div class="wrap">
  <nav id="sidebar" class="sidebar"></nav>
  <main id="view" class="main-view">
    <div style="color: var(--text-muted); text-align: center; margin-top: 5rem;">
      Wybierz sesję z listy po lewej stronie.
    </div>
  </main>
</div>

<div id="toast" class="toast">Skopiowano do schowka!</div>

<script id="data" type="application/json">
__DATA_JSON__
</script>

<script>
(function() {
  const store = JSON.parse(document.getElementById('data').textContent);
  let activeSessions = store.sessions.slice();
  let currentFilter = 'all';
  let searchQuery = '';
  let selectedIndex = 0;

  const sidebar = document.getElementById('sidebar');
  const view = document.getElementById('view');
  const searchInput = document.getElementById('search');
  const filterBtns = document.querySelectorAll('.agent-filter-btn');
  const daysSelect = document.getElementById('daysSelect');
  const daysCustom = document.getElementById('daysCustom');
  const toast = document.getElementById('toast');

  let currentDays = 7;

  function showToast(msg) {
    toast.textContent = msg || 'Skopiowano!';
    toast.style.display = 'block';
    setTimeout(() => { toast.style.display = 'none'; }, 2000);
  }

  function copyText(text, successMsg) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => showToast(successMsg));
    } else {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      showToast(successMsg);
    }
  }

  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s || '';
    return d.innerHTML;
  }

  function parseDate(dateStr) {
    if (!dateStr) return null;
    const clean = dateStr.replace(' ', 'T');
    const d = new Date(clean);
    return isNaN(d.getTime()) ? null : d;
  }

  function filterSessions() {
    const now = new Date();
    const cutoff = (currentDays !== null && currentDays > 0)
      ? new Date(now.getTime() - (currentDays * 24 * 60 * 60 * 1000))
      : null;

    activeSessions = store.sessions.filter(s => {
      const matchAgent = (currentFilter === 'all' || s.agent === currentFilter);
      const query = searchQuery.toLowerCase();
      const matchSearch = !query ||
        (s.title && s.title.toLowerCase().includes(query)) ||
        (s.id && s.id.toLowerCase().includes(query)) ||
        (s.directory && s.directory.toLowerCase().includes(query)) ||
        (s.text && s.text.toLowerCase().includes(query));

      let matchDate = true;
      if (cutoff) {
        const sDate = parseDate(s.updated_at || s.created_at);
        if (sDate && sDate < cutoff) {
          matchDate = false;
        }
      }

      return matchAgent && matchSearch && matchDate;
    });
    renderList();
    if (activeSessions.length > 0) {
      showSession(0);
    } else {
      view.innerHTML = '<div style="color: var(--text-muted); text-align: center; margin-top: 5rem;">Brak sesji dla wybranych kryteriów (spróbuj zwiększyć liczbę dni lub zmienić filtr).</div>';
    }
  }

  function renderList() {
    sidebar.innerHTML = '';
    activeSessions.forEach((s, idx) => {
      const btn = document.createElement('button');
      btn.className = 'session-item' + (idx === selectedIndex ? ' active' : '');
      btn.innerHTML = `
        <div class="item-head">
          <span class="badge badge-${s.agent}">${esc(s.agent)}</span>
          <span class="item-date">${esc(s.updated_at || s.created_at)}</span>
        </div>
        <div class="item-title" title="${esc(s.title || s.id)}">${esc(s.title || s.id)}</div>
        <div class="item-sub">${esc(s.directory || s.id)} · ${s.message_count} msg</div>
      `;
      btn.onclick = () => showSession(idx);
      sidebar.appendChild(btn);
    });
  }

  function showSession(idx) {
    selectedIndex = idx;
    const s = activeSessions[idx];
    if (!s) return;

    document.querySelectorAll('.session-item').forEach((el, j) => {
      el.classList.toggle('active', idx === j);
    });

    view.innerHTML = `
      <div class="view-header">
        <div class="view-title-row">
          <h2 class="view-title">${esc(s.title || s.id)}</h2>
          <div class="btn-bar">
            <button id="btnCopyMd" class="action-btn">📋 Kopiuj sesję (Markdown)</button>
            <button id="btnCopyPath" class="action-btn secondary">📂 Kopiuj ścieżkę pliku</button>
            <button id="btnCopyId" class="action-btn secondary">🔑 Kopiuj ID</button>
          </div>
        </div>
        <div class="meta-grid">
          <span><strong>Agent:</strong> <span class="badge badge-${s.agent}">${esc(s.agent)}</span></span>
          <span><strong>ID:</strong> ${esc(s.id)}</span>
          <span><strong>Katalog:</strong> ${esc(s.directory || '-')}</span>
          <span><strong>Wiadomości:</strong> ${s.message_count}</span>
          <span><strong>Data:</strong> ${esc(s.created_at)} (akt: ${esc(s.updated_at)})</span>
          <span><strong>Ścieżka na dysku:</strong> ${esc(s.raw_path || '-')}</span>
        </div>
      </div>
      <div class="content-area">
        <pre class="md">${esc(s.text)}</pre>
      </div>
    `;

    document.getElementById('btnCopyMd').onclick = () => copyText(s.text, 'Skopiowano treść sesji do schowka!');
    document.getElementById('btnCopyPath').onclick = () => copyText(s.raw_path, 'Skopiowano ścieżkę pliku do schowka!');
    document.getElementById('btnCopyId').onclick = () => copyText(s.id, 'Skopiowano ID sesji!');
  }

  filterBtns.forEach(btn => {
    btn.onclick = () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.getAttribute('data-agent');
      filterSessions();
    };
  });

  daysSelect.onchange = (e) => {
    const val = e.target.value;
    if (val === 'all') {
      currentDays = null;
      daysCustom.style.display = 'none';
    } else if (val === 'custom') {
      daysCustom.style.display = 'inline-block';
      currentDays = parseInt(daysCustom.value, 10) || 7;
    } else {
      currentDays = parseInt(val, 10) || 7;
      daysCustom.style.display = 'none';
    }
    filterSessions();
  };

  daysCustom.oninput = (e) => {
    const val = parseInt(e.target.value, 10);
    if (!isNaN(val) && val > 0) {
      currentDays = val;
      filterSessions();
    }
  };

  searchInput.oninput = (e) => {
    searchQuery = e.target.value;
    filterSessions();
  };

  filterSessions();
})();
</script>
</body>
</html>
"""


def build_browse_html(sessions: List[SessionItem], title: str = "Multi-Agent Unified Sessions") -> str:
    serialized = []
    for s in sessions:
        serialized.append({
            "agent": s.agent,
            "id": s.id,
            "title": s.title,
            "directory": s.directory,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
            "message_count": s.message_count,
            "model": s.model,
            "raw_path": s.raw_path,
            "text": s.text_markdown,
        })
    payload = json.dumps({"title": title, "sessions": serialized}, ensure_ascii=False)
    payload = payload.replace("</", "<\\/")
    doc = BROWSE_HTML_TEMPLATE.replace("__PAGE_TITLE__", _html.escape(title))
    doc = doc.replace("__DATA_JSON__", payload)
    return doc


def main():
    ap = argparse.ArgumentParser(prog="agent_sessions.py", description="Multi-Agent Unified Session Tool")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # 1. list
    p_list = sub.add_parser("list", help="List sessions across agents")
    p_list.add_argument("--agent", choices=["all"] + SUPPORTED_AGENTS, default="all")
    p_list.add_argument("--days", type=int, default=None, help="Filter sessions from last N days")
    p_list.add_argument("--limit", type=int, default=30)
    p_list.add_argument("--query", type=str, default="")

    # 2. browse
    p_browse = sub.add_parser("browse", help="Generate single-file HTML viewer with live search and copy")
    p_browse.add_argument("--agent", choices=["all"] + SUPPORTED_AGENTS, default="all")
    p_browse.add_argument("--days", type=int, default=None, help="Limit embedded sessions to last N days (default: all embedded, 7 days filtered by default in UI)")
    p_browse.add_argument("--limit", type=int, default=100)
    p_browse.add_argument("-o", "--out", type=Path, default=OUTDIR / "browse_all.html")

    # 3. markdown — big combined dump
    p_md = sub.add_parser("markdown", help="Dump all sessions into one big .md file")
    p_md.add_argument("--agent", choices=["all"] + SUPPORTED_AGENTS, default="all")
    p_md.add_argument("--days", type=int, default=7, help="Filter sessions from last N days (default: 7)")
    p_md.add_argument("--limit", type=int, default=500)
    p_md.add_argument("-o", "--out", type=Path, default=OUTDIR / "sessions_dump.txt")

    # 4. last — export the N most recent sessions
    p_last = sub.add_parser("last", help="Export the most recent session (or the N most recent, with --count)")
    p_last.add_argument("--agent", choices=["all"] + SUPPORTED_AGENTS, default="all")
    p_last.add_argument("--count", "-n", type=int, default=1,
                        help="How many of the newest sessions to export (default: 1, the single latest)")
    p_last.add_argument("--out-dir", type=Path, default=None,
                        help="Clean this folder, then write one .md per session into it "
                             "(forces the folder layout; --out is ignored)")
    p_last.add_argument("-o", "--out", type=Path, default=OUTDIR / "last_session.txt",
                        help="Single-file target, used when --out-dir is not given")
    p_last.add_argument("--no-clean", action="store_true",
                        help="Do not empty the target folder first (off by default: the folder IS cleaned)")

    # 5. export
    p_exp = sub.add_parser("export", help="Export a specific session to markdown or file")
    p_exp.add_argument("agent", choices=SUPPORTED_AGENTS)
    p_exp.add_argument("session_id")
    p_exp.add_argument("-o", "--out", type=Path)

    args = ap.parse_args()

    if args.cmd == "list":
        sessions = get_all_sessions(args.agent, limit_per_agent=args.limit, days=args.days)
        if args.query:
            q = args.query.lower()
            sessions = [s for s in sessions if q in s.title.lower() or q in s.id.lower() or q in s.directory.lower()]

        print(f"{'AGENT':<12} {'DATE':<19} {'MSGS':<5} {'ID / TITLE'}")
        print("-" * 80)
        for s in sessions[:args.limit]:
            title_disp = s.title if s.title != s.id else s.id
            print(f"{s.agent:<12} {s.updated_at or s.created_at:<19} {s.message_count:<5} {title_disp[:50]}")
            if s.directory:
                print(f"  └─ dir: {s.directory}")

    elif args.cmd == "browse":
        sessions = get_all_sessions(args.agent, limit_per_agent=args.limit, days=args.days)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        html_doc = build_browse_html(sessions)
        args.out.write_text(html_doc, encoding="utf-8")
        print(f"Wrote unified viewer to: {args.out}")
        print(f"Total sessions indexed: {len(sessions)}")

    elif args.cmd == "markdown":
        sessions = get_all_sessions(args.agent, limit_per_agent=args.limit, days=args.days)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chunks = [
            f"# Multi-Agent Sessions Dump",
            f"",
            f"- **Wygenerowano**: {generated_at}",
            f"- **Filtr**: ostatnie {args.days} dni",
            f"- **Agenci**: {args.agent}",
            f"- **Liczba sesji**: {len(sessions)}",
            f"",
            f"---",
            f"",
            f"## Spis sesji",
            f"",
        ]
        for i, s in enumerate(sessions, 1):
            anchor = f"session-{i}"
            ts = s.updated_at or s.created_at or ""
            chunks.append(f"{i}. [{s.agent}] **{s.title}** — {ts}")
        chunks.append("")
        chunks.append("---")
        chunks.append("")
        for i, s in enumerate(sessions, 1):
            chunks.append(f"<!-- session-{i} -->")
            chunks.append(s.text_markdown)
            chunks.append("")
            chunks.append("---")
            chunks.append("")
        out_text = "\n".join(chunks)
        args.out.write_text(out_text, encoding="utf-8")
        size_kb = args.out.stat().st_size // 1024
        print(f"Wrote markdown dump to: {args.out}")
        print(f"Total sessions: {len(sessions)}  |  File size: {size_kb} KB")

    elif args.cmd == "last":
        n = max(1, args.count)
        # Recency is absolute: every agent store is scanned (--agent all, the
        # default), then the merged list is sorted newest-first across agents.
        # limit_per_agent only bounds how deep each store is read; it must be at
        # least n, otherwise an agent holding n of the newest sessions could
        # push one of them past the cut.
        sessions = get_all_sessions(args.agent, limit_per_agent=max(n, 10), days=None)
        if not sessions:
            sys.exit("Brak sesji do wyeksportowania.")
        targets = sessions[:n]

        if args.out_dir:
            out_dir = args.out_dir
            if args.no_clean:
                out_dir.mkdir(parents=True, exist_ok=True)
            else:
                _empty_dir(out_dir)

            used_names: Dict[str, int] = {}
            written = []
            for idx, s in enumerate(targets, 1):
                name = f"{idx:02d}_{s.agent}_{_safe_name(s)}.md"
                # Two sessions can render to the same filename (same agent, same
                # title); suffix rather than overwrite so no export is lost.
                if name in used_names:
                    used_names[name] += 1
                    stem, ext = name.rsplit(".", 1)
                    name = f"{stem}_{used_names[name]}.{ext}"
                else:
                    used_names[name] = 1
                path = out_dir / name
                path.write_text(_session_header(s, idx, len(targets)) + render_session_body(s),
                                encoding="utf-8")
                written.append((path, s))

            print(f"Katalog wyczyszczony i zapisany: {out_dir}")
            for path, s in written:
                size_kb = path.stat().st_size // 1024
                print(f"  {path.name}  [{s.agent}]  {s.updated_at or s.created_at}  ({size_kb} KB)")
            print(f"Zapisano sesji: {len(written)} (z {len(sessions)} dostepnych)")
        else:
            target = targets[0]  # get_all_sessions sorts newest-first
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(_session_header(target, 1, 1) + render_session_body(target),
                                encoding="utf-8")
            size_kb = args.out.stat().st_size // 1024
            print(f"Agent   : {target.agent}")
            print(f"Tytuł   : {target.title}")
            print(f"Data    : {target.updated_at or target.created_at}")
            print(f"Zapisano: {args.out}  ({size_kb} KB)")
            if n > 1:
                print(f"Uwaga: --count {n} bez --out-dir — zapisano tylko najnowsza sesje. "
                      f"Uzyj --out-dir, aby dostac {n} plikow.")

    elif args.cmd == "export":

        sessions = get_all_sessions(args.agent, limit_per_agent=100)
        matched = [s for s in sessions if s.id == args.session_id or args.session_id in s.id]
        if not matched:
            sys.exit(f"Session '{args.session_id}' not found for agent '{args.agent}'")
        target = matched[0]
        out_path = args.out or (OUTDIR / f"{target.agent}_{target.id[:12]}.md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(target.text_markdown, encoding="utf-8")
        print(f"Exported {target.agent} session {target.id} to: {out_path}")


if __name__ == "__main__":
    main()
