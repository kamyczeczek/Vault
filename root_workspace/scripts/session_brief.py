#!/usr/bin/env python3
"""Compact, deterministic brief of the N latest sessions.

Selection reuses the L1 cards from `session_digest.py` (commits, flags, tests,
micro) and the `did` event stream from `extract_did.py` (user/assistant text,
mutating tools). Nothing is summarized by a model: every line is either a
mechanical fact, a quoted line, or a truncated tool excerpt.

Usage:
    python.exe scripts/session_brief.py --last 20 --valuable
    python.exe scripts/session_brief.py --last 20 --valuable -o out.md
    python.exe scripts/session_brief.py --last 10 --agent opencode

Exit 0 = written, 1 = no valuable sessions / argument error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import extract_did as did  # noqa: E402
import memory_index as memory  # noqa: E402
import session_digest as digest  # noqa: E402

DEFAULT_OUT = SCRIPTS / "_scratch" / "sessions" / "02_products" / "session_brief.md"
DEFAULT_TOOL_CALLS = SCRIPTS / "_scratch" / "sessions" / "02_products" / "tool_calls.jsonl"

READ_ONLY_BASH = re.compile(
    r"^\s*(?:ls|dir|cat|type|head|tail|Get-Content|grep|rg|find|where|"
    r"Select-String|Get-ChildItem|Get-Item|Get-Command|Test-Path|foreach|cd|"
    r"Set-Location|Write-Output|echo|gh\s+auth\s+status|gh\s+--version|"
    r"git\s+(?:status|diff|log|show|branch|remote|config|rev-parse|ls-files))\b",
    re.IGNORECASE,
)
READ_ONLY_BASH_VAR = re.compile(r"^\s*\$", re.IGNORECASE)
READ_ONLY_ARGS = re.compile(r"(?:^|\s)(?:--help|--version|-h)(?=\s|$|[;,|)])", re.IGNORECASE)
NULL_REDIRECT = re.compile(r"(?:\d|\*)?>\s*\$null\b|(?:\d|\*)?>&\s*\d", re.IGNORECASE)
QUOTED_SPAN = re.compile(r"\"[^\"]*\"|'[^']*'", re.DOTALL)
MUTATING_BASH = re.compile(
    r"(?:>>?|(?<![\w-])(?:rm|mv|cp)\b|Set-Content|Add-Content|Out-File|New-Item|"
    r"Remove-Item|Move-Item|Copy-Item|git\s+(?:add|commit|rm|mv|reset|restore|"
    r"checkout|switch|stash|apply|am|rebase|merge|push)|python(?:\.exe)?\b|"
    r"pytest|npm|npx|make|cargo|go\s+test|dotnet|uv\b|pip\b)",
    re.IGNORECASE,
)
FLAG_ID_RX = re.compile(r"\d{4}-\d{2}-\d{2}")


def _blen(text: str) -> int:
    return len(text.encode("utf-8"))


def truncate(text: str, limit: int, tail: bool = False) -> str:
    text = str(text or "").strip()
    if limit <= 0:
        return ""
    if len(text) <= limit:
        return text
    removed = len(text) - limit
    if tail:
        return f"...[{removed} chars]... " + text[-limit:]
    return text[:limit] + f" ...[{removed} chars]"


def _one_line(text: str) -> str:
    return " ".join(str(text or "").split())


def is_noise_path(path: str) -> bool:
    value = str(path or "").replace("/", "\\").lower()
    return (
        "\\appdata\\local\\temp\\" in value
        or value.startswith("\\tmp\\")
        or value.startswith("temp\\")
    )


def hard_truncate(text: str, limit: int) -> str:
    text = str(text or "")
    if limit <= 0:
        return ""
    if _blen(text) <= limit:
        return text
    marker = "\n...[truncated]\n"
    budget = max(0, limit - _blen(marker))
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if _blen(text[:mid]) <= budget:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo] + marker if budget > 0 else marker[:limit]


def _code(text: str) -> str:
    text = _one_line(text)
    if "`" in text:
        return "``" + text + "``"
    return "`" + text + "`"


def _json_obj(value: str):
    if isinstance(value, dict):
        return value
    try:
        obj = json.loads(value or "{}")
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def _first_str(obj, keys) -> str:
    if not isinstance(obj, dict):
        return ""
    for key in keys:
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _bash_command(event: dict) -> str:
    obj = _json_obj(event.get("input") or "")
    if not isinstance(obj, dict):
        return ""
    return _first_str(obj, ("command", "cmd", "script"))


def bash_is_noise(event: dict) -> bool:
    command = _bash_command(event)
    if not command:
        return False
    if READ_ONLY_ARGS.search(command):
        return True
    command = NULL_REDIRECT.sub(" ", command)
    if MUTATING_BASH.search(QUOTED_SPAN.sub(" ", command)):
        return False
    first = command.splitlines()[0].strip()
    return bool(READ_ONLY_BASH.match(first) or READ_ONLY_BASH_VAR.match(first))


def tool_is_mutating(event: dict) -> bool:
    if event.get("kind") != "tool":
        return False
    name = str(event.get("name") or "").lower()
    if name in ("bash", "shell"):
        return not bash_is_noise(event)
    if name == "skill":
        return False
    if name in ("write", "edit", "apply_patch", "patch", "multiedit"):
        obj = _json_obj(event.get("input") or "")
        path = _first_str(obj, ("filePath", "path", "file_path", "filename"))
        if path and is_noise_path(path):
            return False
    return name in did.MUTATING


def _category(event: dict) -> str:
    name = str(event.get("name") or "").lower()
    if name in ("write", "edit", "apply_patch", "patch", "multiedit"):
        return "edit"
    if name in ("bash", "shell"):
        return "bash"
    if name in ("question", "ask"):
        return "ask"
    return "other"


def select_actions(events: list[dict], max_actions: int = 8) -> list[dict]:
    buckets: dict[str, list[tuple[int, dict]]] = {"edit": [], "bash": [], "ask": [], "other": []}
    for idx, event in enumerate(events):
        if tool_is_mutating(event):
            buckets[_category(event)].append((idx, event))
    caps = {"edit": 3, "bash": 3, "ask": 2, "other": 2}
    chosen: list[tuple[int, dict]] = []
    for name in ("edit", "bash", "ask", "other"):
        chosen.extend(buckets[name][: caps[name]])
    chosen.sort(key=lambda pair: pair[0])
    return [event for _, event in chosen[: max(0, max_actions)]]


def _role_texts(events: list[dict], role: str) -> list[str]:
    out = []
    for event in events:
        if event.get("kind") == "text" and event.get("role") == role:
            text = str(event.get("text") or "").strip()
            if text:
                out.append(text)
    return out


def meaningful(text: str, min_len: int = 3) -> bool:
    value = _one_line(text)
    if len(value) < min_len:
        return False
    if not re.search(r"[A-Za-z0-9]", value):
        return False
    if value.lower().strip(" .:;") in ("not checked", "none", "todo", "done"):
        return False
    return True


def goal_text(card: dict, events: list[dict]) -> str:
    goal = card.get("goal") or {}
    text = str(goal.get("text") or "").strip()
    if meaningful(text):
        return text
    users = _role_texts(events, "user")
    return users[0] if users else text


def ending_text(card: dict, events: list[dict]) -> str:
    ending = card.get("ending") or {}
    candidate = ""
    if ending.get("kind") == "quote":
        candidate = str(ending.get("text") or "").strip()
    elif ending.get("kind") == "marker":
        candidate = str(ending.get("raw_line") or "").strip()
    if meaningful(candidate, 12):
        return candidate
    for text in reversed(_role_texts(events, "assistant")):
        if meaningful(text, 12):
            return text
    return candidate if meaningful(candidate) else ""


def value_reason(card: dict, events: list[dict]) -> tuple[bool, str]:
    session_id = str(card.get("session_id") or "")
    if session_id and memory.is_excluded(session_id):
        return False, "meta"
    if not events and not goal_text(card, events) and not (card.get("commits") or card.get("flags")):
        return False, "empty"
    signals = bool(card.get("commits") or card.get("flags") or card.get("tests"))
    has_mutation = any(tool_is_mutating(event) for event in events)
    if card.get("micro") and not signals and not has_mutation:
        return False, "micro"
    if not signals and not has_mutation:
        return False, "no_delta"
    return True, "ok"


def _join_code(items, limit: int = 5) -> str:
    values = [str(item) for item in (items or []) if str(item).strip()]
    shown = ", ".join(_code(value) for value in values[:limit])
    if len(values) > limit:
        shown += f" (+{len(values) - limit})"
    return shown


def delta_text(card: dict) -> str:
    files = [path for path in (card.get("files") or []) if not is_noise_path(path)]
    flags = [flag for flag in (card.get("flags") or []) if FLAG_ID_RX.search(str(flag))]
    absent_ids = {str(flag) for flag in (card.get("flags_missing") or [])}
    flags_present = [flag for flag in flags if str(flag) not in absent_ids]
    flags_absent = [flag for flag in flags if str(flag) in absent_ids]
    parts = []
    if card.get("commits"):
        parts.append("commits: " + _join_code(card["commits"]))
    if files:
        parts.append("files: " + _join_code(files))
    if flags_present:
        parts.append("flags: " + _join_code(flags_present))
    if flags_absent:
        parts.append("flags absent now: " + _join_code(flags_absent, 3))
    if card.get("tests"):
        parts.append("tests: " + _join_code(card["tests"], 3))
    return "; ".join(parts) if parts else "-"


def _content_excerpt(obj) -> str:
    if not isinstance(obj, dict):
        return ""
    content = _first_str(obj, ("content", "newString", "new_string", "new", "patch", "diff"))
    return truncate(content, 180)


def render_action(event: dict) -> str:
    name = str(event.get("name") or "").lower()
    obj = _json_obj(event.get("input") or "")
    output = truncate(event.get("output") or "", 500, tail=True)
    out = f" — {_code(output)}" if output else " — (no output)"
    if name in ("write", "edit", "apply_patch", "patch", "multiedit"):
        path = _first_str(obj, ("filePath", "path", "file_path", "filename"))
        detail = ""
        if name == "edit" and isinstance(obj, dict):
            old = _first_str(obj, ("oldString", "old_string", "old"))
            new = _first_str(obj, ("newString", "new_string", "new"))
            if old or new:
                detail = f" {_code(truncate(old, 120))} -> {_code(truncate(new, 120))}"
        else:
            excerpt = _content_excerpt(obj)
            if excerpt:
                detail = f" {_code(excerpt)}"
        return f"- **{name}** {_code(path or '?')}{detail}{out}"
    if name in ("bash", "shell"):
        command = _bash_command(event)
        return f"- **bash** {_code(truncate(command, 300) or '?')}{out}"
    if name in ("question", "ask"):
        question = _first_str(obj, ("question", "prompt", "text"))
        if not question and isinstance(obj, dict):
            questions = obj.get("questions")
            if isinstance(questions, list) and questions and isinstance(questions[0], dict):
                question = (
                    _first_str(questions[0], ("question", "header"))
                    or str(questions[0].get("question") or "")
                )
        question = question or str(event.get("input") or "")
        return f"- **{name}** {_code(truncate(question, 300))}{out}"
    if name == "skill":
        skill = _first_str(obj, ("skill", "name")) or str(event.get("input") or "")
        return f"- **skill** {_code(truncate(skill, 160))}{out}"
    return f"- **{name or 'tool'}**{out}"


def render_session(rank: int, session, card: dict, events: list[dict],
                   session_kb: int, max_actions: int) -> str:
    title = _one_line(session.title or session.id or "session")
    agent = session.agent or "-"
    model = card.get("model") or session.model or "-"
    stamp = card.get("date") or session.updated_at or session.created_at or "-"
    duration = card.get("duration") or "-"
    goal = truncate(_one_line(goal_text(card, events)), 600)
    ending = truncate(_one_line(ending_text(card, events)), 700)
    goal = goal if meaningful(goal) else "-"
    ending = ending if meaningful(ending) else "-"
    delta = delta_text(card)
    key = card.get("stable_key") or f"{agent}:{session.id}"

    head = [
        f"## {rank}. {truncate(title, 120)}",
        "",
        f"- **Agent / model**: {agent} / {model}",
        f"- **Date / duration**: {stamp} / {duration}",
        f"- **Stable key**: {_code(key)}",
        f"- **Goal**: {goal}",
        f"- **Delta**: {delta}",
    ]
    tail = [
        "",
        f"- **Ending**: {ending}",
        f"- **Full body**: {_code(f'python.exe scripts/agent_sessions.py export {agent} {session.id}')}",
        "",
    ]

    actions = select_actions(events, max_actions)
    action_lines = ["- **Actions**:"] if actions else ["- **Actions**: -"]
    limit = session_kb * 1024
    for event in actions:
        line = "  " + render_action(event)
        candidate = "\n".join(head + [""] + action_lines + [line] + tail)
        if _blen(candidate) > limit:
            action_lines.append("  - (more actions omitted: session budget)")
            break
        action_lines.append(line)

    text = "\n".join(head + [""] + action_lines + tail)
    return hard_truncate(text, limit)


def build(args) -> int:
    as_mod = digest.load_agent_sessions()
    digest.merged._AGENT_SESSIONS = as_mod
    sessions = as_mod.get_all_sessions(
        args.agent, limit_per_agent=max(args.last * 3, 60), days=None
    )
    main, _children, available = digest.select_sessions(sessions, args.last, args.days, args.until)
    if not main:
        sys.exit("No main sessions for the given filters")

    tool_calls = Path(args.tool_calls) if args.tool_calls else None
    sidecar = digest.load_tool_calls(tool_calls if tool_calls and tool_calls.is_file() else None)
    sidecar_data, sidecar_meta = sidecar if sidecar else (None, None)
    flags_dir = ROOT / "handoff" / "flags"

    rows = []
    skipped: Counter[str] = Counter()
    for session in main:
        body = as_mod.render_session_body(session, include_reasoning=False).strip()
        card = digest.card_from_actions(session, body, sidecar_data, sidecar_meta, flags_dir)
        stats: Counter = Counter()
        events = did._events_for(session, as_mod, stats)
        ok, reason = value_reason(card, events)
        if args.valuable and not ok:
            skipped[reason] += 1
            continue
        rows.append((session, card, events))

    if not rows:
        print("BRIEF_WRITTEN selected=0", file=sys.stderr)
        for reason, count in sorted(skipped.items()):
            print(f"  skipped_{reason}={count}", file=sys.stderr)
        return 1

    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = [
        f"# Brief - last {args.last} sessions",
        "",
        f"- **Generated**: {generated}",
        f"- **Requested / selected**: {args.last} / {len(rows)}",
        f"- **Agent**: {args.agent}",
        f"- **Filter**: {'valuable' if args.valuable else 'all'}",
        f"- **Budget**: session={args.session_kb} KB, total={args.total_kb} KB",
        "",
        "Selection is mechanical: L1 cards (commits, files, flags, tests, micro) "
        "plus mutating `did` events. No model summary.",
        "",
    ]
    body_parts = []
    omitted = []
    total_limit = args.total_kb * 1024
    header_len = _blen("\n".join(header))
    for rank, (session, card, events) in enumerate(rows, 1):
        section = render_session(rank, session, card, events, args.session_kb, args.max_actions)
        if body_parts and header_len + _blen("\n".join(body_parts + [section])) > total_limit:
            omitted = [r[1].get("stable_key") or "" for r in rows[rank - 1:]]
            break
        if not body_parts and header_len + _blen(section) > total_limit:
            section = hard_truncate(section, max(512, total_limit - header_len - 200)) + "\n"
        body_parts.append(section)

    footer = []
    if omitted:
        footer = ["## Omitted by total budget", ""]
        footer.extend(f"- {_code(key)}" for key in omitted if key)
        footer.append("")
    out_text = "\n".join(header + body_parts + footer)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(out_text, encoding="utf-8", newline="\n")

    print(f"BRIEF_WRITTEN selected={len(body_parts)} requested={args.last} "
          f"skipped={sum(skipped.values())} available={available}")
    print(f"  path={out} size={_blen(out_text)} bytes")
    for reason, count in sorted(skipped.items()):
        print(f"  skipped_{reason}={count}")
    if omitted:
        print(f"  omitted_by_total_budget={len(omitted)}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Compact, deterministic session brief")
    parser.add_argument("--last", type=int, default=10, help="number of latest main sessions")
    parser.add_argument("--valuable", action="store_true", help="drop micro/read-only/no-delta sessions")
    parser.add_argument("--agent", default="all", help="agent filter")
    parser.add_argument("--days", type=int, default=None, help="alternative window in days")
    parser.add_argument("--until", default=None, help="freeze window: YYYY-MM-DD HH:MM:SS")
    parser.add_argument("-o", "--out", default=str(DEFAULT_OUT), help="output markdown")
    parser.add_argument("--tool-calls", default=str(DEFAULT_TOOL_CALLS), help="tool_calls.jsonl sidecar")
    parser.add_argument("--session-kb", type=int, default=8, help="per-session budget")
    parser.add_argument("--total-kb", type=int, default=120, help="total budget")
    parser.add_argument("--max-actions", type=int, default=8, help="max actions per session")
    args = parser.parse_args(argv)
    args.last = max(1, args.last)
    args.session_kb = max(1, args.session_kb)
    args.total_kb = max(1, args.total_kb)
    return build(args)


if __name__ == "__main__":
    raise SystemExit(main())
