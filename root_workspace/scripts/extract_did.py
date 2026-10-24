#!/usr/bin/env python3
"""Extract what the agent actually produced in the N latest sessions.

Keeps only structural evidence:
- user text (the commands)
- assistant text (the answers)
- mutating tool calls: write, edit, bash/shell, question/ask, skill
  with their full input and output

Drops:
- reasoning/thinking (the "road", not the result)
- read-only exploration: read, grep, glob, list, webfetch, codesearch
- step markers and harness events

No session file path is written to the output.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sqlite3
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_SESSIONS = ROOT / "scripts" / "agent_sessions.py"
OC_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"

MUTATING = {
    "write", "edit", "bash", "shell", "question", "ask", "skill",
    "apply_patch", "patch", "multiedit",
}
READ_ONLY = {
    "read", "grep", "glob", "list", "webfetch", "codesearch",
    "todoread", "todo",
}
HARNESS = {"idle", "model-switched", "compaction", "system", "synthetic", "developer"}


def _load_agent_sessions():
    spec = importlib.util.spec_from_file_location("agent_sessions", AGENT_SESSIONS)
    if spec is None or spec.loader is None:
        sys.exit(f"Nie znaleziono {AGENT_SESSIONS}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["agent_sessions"] = module
    spec.loader.exec_module(module)
    return module


def _fence(text: str, lang: str = "") -> str:
    text = str(text)
    runs = re.findall(r"`+", text)
    width = max([3] + [len(r) + 1 for r in runs])
    fence = "`" * width
    return f"{fence}{lang}\n{text}\n{fence}"


def _as_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            else:
                parts.append(str(item))
        return "\n".join(p for p in parts if p)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def _tool_output(state: dict, part: dict) -> str:
    for key in ("output", "content"):
        if key in state and state.get(key) not in (None, "", []):
            return _as_text(state.get(key))
    return _as_text(part.get("output"))


def _tool_input(state: dict, part: dict) -> str:
    value = state.get("input")
    if value in (None, "", {}):
        value = part.get("input")
    if value in (None, "", {}):
        return "{}"
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            return value
    return json.dumps(value, ensure_ascii=False, indent=2)


def _event_text(role: str, text: str) -> dict:
    return {"kind": "text", "role": role, "text": text}


def _event_tool(name: str, status: str, inp: str, out: str) -> dict:
    return {"kind": "tool", "name": name, "status": status, "input": inp, "output": out}


def _opencode_events(sid: str, stats: Counter) -> list[dict]:
    if not OC_DB.is_file():
        return []
    conn = sqlite3.connect(str(OC_DB))
    conn.row_factory = sqlite3.Row
    try:
        tables = {r[0] for r in conn.execute("select name from sqlite_master where type='table'")}
        has_v2 = "session_message" in tables and conn.execute(
            "select 1 from session_message where session_id=? limit 1", (sid,)
        ).fetchone() is not None
        if has_v2:
            rows = conn.execute(
                "select type, data from session_message where session_id=? order by seq, time_created, id",
                (sid,),
            ).fetchall()
            return _opencode_v2(rows, stats)
        return _opencode_legacy(conn, sid, stats)
    finally:
        conn.close()


def _opencode_v2(rows, stats: Counter) -> list[dict]:
    events: list[dict] = []
    for row in rows:
        role = row["type"] or "user"
        if role in HARNESS:
            continue
        try:
            data = json.loads(row["data"]) if row["data"] else {}
        except Exception:
            data = {}
        if not isinstance(data, dict):
            data = {}
        if role == "user":
            text = (data.get("text") or "").strip()
            if text:
                events.append(_event_text("user", text))
            continue
        for block in data.get("content") or []:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                text = (block.get("text") or "").strip()
                if text:
                    events.append(_event_text(role, text))
            elif btype == "reasoning":
                stats["reasoning"] += 1
            elif btype == "tool":
                name = block.get("name") or block.get("tool") or "?"
                if name in MUTATING:
                    state = block.get("state") or {}
                    events.append(_event_tool(
                        name,
                        str(state.get("status") or block.get("status") or "?"),
                        _tool_input(state, block),
                        _tool_output(state, block),
                    ))
                elif name in READ_ONLY:
                    stats["read_only"] += 1
                else:
                    stats["other"] += 1
            elif btype in ("step-start", "step-finish"):
                continue
    return events


def _opencode_legacy(conn: sqlite3.Connection, sid: str, stats: Counter) -> list[dict]:
    events: list[dict] = []
    messages = conn.execute(
        "select id, data from message where session_id=? order by time_created, id", (sid,)
    ).fetchall()
    for message in messages:
        try:
            mdata = json.loads(message["data"]) if message["data"] else {}
        except Exception:
            mdata = {}
        role = mdata.get("role", "user")
        if role in HARNESS:
            continue
        parts = conn.execute(
            "select data from part where message_id=? order by time_created, id", (message["id"],)
        ).fetchall()
        for part_row in parts:
            try:
                part = json.loads(part_row["data"]) if part_row["data"] else {}
            except Exception:
                part = {}
            ptype = part.get("type")
            if ptype == "text":
                text = (part.get("text") or "").strip()
                if text and role in ("user", "assistant"):
                    events.append(_event_text(role, text))
            elif ptype == "reasoning":
                stats["reasoning"] += 1
            elif ptype == "tool":
                name = part.get("tool") or part.get("name") or "?"
                if name in MUTATING:
                    state = part.get("state") or {}
                    events.append(_event_tool(
                        name,
                        str(state.get("status") or part.get("status") or "?"),
                        _tool_input(state, part),
                        _tool_output(state, part),
                    ))
                elif name in READ_ONLY:
                    stats["read_only"] += 1
                else:
                    stats["other"] += 1
            elif ptype in ("step-start", "step-finish"):
                continue
    return events


def _pi_style_events(path: Path, stats: Counter) -> list[dict]:
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    results: dict[str, tuple[str, str]] = {}
    parsed = []
    for line in lines:
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        parsed.append(obj)
        if obj.get("type") != "message":
            continue
        msg = obj.get("message") or {}
        if msg.get("role") != "toolResult":
            continue
        content = _as_text(msg.get("content"))
        results[str(msg.get("toolCallId") or msg.get("tool_call_id") or "")] = (
            str(msg.get("toolName") or msg.get("tool_name") or "?"),
            ("ERROR\n" if msg.get("isError") else "") + content,
        )

    events: list[dict] = []
    for obj in parsed:
        if obj.get("type") != "message":
            continue
        msg = obj.get("message") or {}
        role = msg.get("role") or ""
        if role in HARNESS or role == "toolResult":
            continue
        content = msg.get("content")
        if role == "user":
            text = _as_text(content).strip()
            if text:
                events.append(_event_text("user", text))
            continue
        if role != "assistant":
            continue
        if isinstance(content, str):
            text = content.strip()
            if text:
                events.append(_event_text("assistant", text))
            continue
        for block in content or []:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                text = (block.get("text") or "").strip()
                if text:
                    events.append(_event_text("assistant", text))
            elif btype in ("toolCall", "tool_call", "toolUse", "tool_use", "tool"):
                name = block.get("name") or block.get("tool") or "?"
                if name in MUTATING:
                    args = block.get("arguments") or block.get("args") or block.get("input") or {}
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            pass
                    tid = str(block.get("id") or block.get("toolCallId") or "")
                    _, output = results.get(tid, ("", ""))
                    events.append(_event_tool(
                        name,
                        "error" if output.startswith("ERROR\n") else "completed",
                        json.dumps(args, ensure_ascii=False, indent=2) if not isinstance(args, str) else args,
                        output[6:] if output.startswith("ERROR\n") else output,
                    ))
                elif name in READ_ONLY:
                    stats["read_only"] += 1
                else:
                    stats["other"] += 1
            elif btype in ("reasoning", "thinking"):
                stats["reasoning"] += 1
            elif btype in ("step-start", "step-finish"):
                continue
    return events


def _generic_events(session, agent_sessions, stats: Counter) -> list[dict]:
    """Best-effort fallback for agents without a structural reader.

    Keeps user/assistant prose and only mutating tool blocks from the rendered
    body. Tool payloads may already be truncated by the source loader.
    """
    body = agent_sessions.render_session_body(session, include_reasoning=False)
    events: list[dict] = []
    role = ""
    tool_lines: list[str] | None = None
    tool_name = ""
    text_lines: list[str] = []

    def flush_text() -> None:
        nonlocal text_lines
        text = "\n".join(text_lines).strip()
        if text and role in ("user", "assistant"):
            events.append(_event_text(role, text))
        text_lines = []

    def flush_tool() -> None:
        nonlocal tool_lines, tool_name
        if tool_lines is not None and tool_name in MUTATING:
            events.append(_event_tool(tool_name, "?", "", "\n".join(tool_lines)))
        tool_lines = None
        tool_name = ""

    for line in body.splitlines():
        heading = re.match(r"^## \[([^\]]+)\]$", line.strip())
        if heading:
            flush_text()
            flush_tool()
            role = heading.group(1)
            continue
        tool_header = re.match(
            r"^> \*\*(?:tool|tool request|tool call|tool result)\*\*\s+`?([^`·\s]+)`?", line.strip()
        )
        if tool_header:
            flush_text()
            flush_tool()
            tool_name = tool_header.group(1)
            if tool_name in MUTATING:
                tool_lines = [line]
            elif tool_name in READ_ONLY:
                stats["read_only"] += 1
            else:
                stats["other"] += 1
            continue
        if tool_lines is not None:
            tool_lines.append(line)
            continue
        if role in ("user", "assistant"):
            if line.strip():
                text_lines.append(line)
            elif text_lines:
                flush_text()
    flush_text()
    flush_tool()
    return events


def _events_for(session, agent_sessions, stats: Counter) -> list[dict]:
    agent = str(session.agent or "").lower()
    if agent == "opencode":
        events = _opencode_events(session.id, stats)
        if events or session.message_count:
            return events
        return []
    if agent in ("pi", "omp"):
        return _pi_style_events(Path(session.raw_path), stats)
    return _generic_events(session, agent_sessions, stats)


def _write_session(f, idx: int, total: int, session, events: list[dict], stats: Counter) -> None:
    title = (session.title or session.id or "session").replace("\n", " ")
    f.write(f"## Sesja {idx}/{total} — {title}\n\n")
    f.write(f"- **Agent**: {session.agent or '-'}\n")
    f.write(f"- **Model**: {session.model or '-'}\n")
    f.write(f"- **Czas**: {session.created_at or '-'} → {session.updated_at or '-'}\n")
    f.write(f"- **Wiadomości**: {session.message_count}\n")
    verdict = []
    if stats.get("reasoning"):
        verdict.append(f"reasoning×{stats['reasoning']}")
    if stats.get("read_only"):
        verdict.append(f"read-only×{stats['read_only']}")
    if stats.get("other"):
        verdict.append(f"inne×{stats['other']}")
    f.write("- **Pominięto**: " + (", ".join(verdict) if verdict else "brak") + "\n\n")

    if not events:
        f.write("*Brak wyprodukowanej treści poza reasoningiem i eksploracją.*\n\n---\n\n")
        return

    for event in events:
        if event["kind"] == "text":
            f.write(f"### [{event['role']}]\n\n{event['text']}\n\n")
        else:
            f.write(f"#### [tool: {event['name']} · {event['status']}]\n\n")
            f.write("input:\n\n")
            f.write(_fence(event["input"], "json") + "\n\n")
            f.write("output:\n\n")
            output = event["output"]
            f.write(_fence(output if output else "(brak outputu)") + "\n\n")
    f.write("---\n\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exact description of what the agent produced in the N latest sessions."
    )
    parser.add_argument("count", nargs="?", type=int, default=None, help="N (default: 10)")
    parser.add_argument("--count", "-n", dest="count_opt", type=int, default=None,
                        help="N (default: 10)")
    parser.add_argument("-o", "--out", type=Path,
                        default=ROOT / "scripts" / "_scratch" / "sessions"
                        / "02_products" / "did_sessions.md")
    parser.add_argument("--agent", default="all", help="all (default) or one agent name")
    args = parser.parse_args()

    n = max(1, args.count_opt or args.count or 10)
    agent_sessions = _load_agent_sessions()
    sessions = agent_sessions.get_all_sessions(args.agent, limit_per_agent=max(n, 10), days=None)
    if not sessions:
        print("Brak sesji.", file=sys.stderr)
        return 1
    targets = sessions[:n]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Co agent zrobił — ostatnie {len(targets)} sesji\n\n")
        f.write(f"- **Wygenerowano**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Sesje**: {len(targets)} (agent: {args.agent})\n")
        f.write("- **Zostawiono**: tekst użytkownika, tekst asystenta, mutujące narzędzia "
                "(write, edit, bash/shell, question/ask, skill) z pełnym inputem i outputem.\n")
        f.write("- **Pominięto**: reasoning/thinking, read-only (read, grep, glob, list, "
                "webfetch, codesearch), znaczniki kroków i zdarzenia harnessu.\n\n")
        for idx, session in enumerate(targets, 1):
            stats: Counter = Counter()
            events = _events_for(session, agent_sessions, stats)
            _write_session(f, idx, len(targets), session, events, stats)

    size_kb = args.out.stat().st_size // 1024
    print(f"Zapisano: {args.out}")
    print(f"Sesji: {len(targets)}  |  {size_kb} KB")
    for idx, session in enumerate(targets, 1):
        print(f"  {idx:02d}. [{session.agent}] {session.updated_at or session.created_at}  {session.title[:60]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
