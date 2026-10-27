#!/usr/bin/env python3
"""Export a pi session JSONL to a bounded markdown reflection file.

Purpose: the durable reflection layer is .md, not opaque KV. This exporter
turns one session transcript into a small, git-trackable, FTS5-indexable
markdown file under reflection/sessions/ that the ICM reflection pass
(candidates -> digests -> memory.md) can distill over.

Design constraints (knowledge/corpus/00_reflection_reorientation_cost.md):
  - BOUNDED: hard line caps; a full session transcript is never dumped.
  - QUERYABLE: output is plain markdown -> indexed by the knowledge graph;
    recovery is a query, not a re-read.
  - Scars are failure triples (failed state / cause / fix) per
    knowledge/corpus/reflection_rule_of_scars.md.

Usage:
  python scripts/export_session_reflection.py [session.jsonl]
  (default: $PI_SESSION_FILE)

Stdlib only. Idempotent: one file per session id; re-export overwrites it.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

CAP_INTENT = 200
CAP_ERROR = 150
CAP_FILE = 120
TOP_TOOLS = 6
TOP_FILES = 10
TOP_ERRORS = 8
MAX_OUT_LINES = 90  # hard bound on the whole document


def parse_session(path: str) -> dict:
    """Extract bounded signals from a pi session JSONL. stdlib only."""
    session_id = ""
    started_at = ""
    cwd = ""
    models = []
    user_texts: list[str] = []
    tools: Counter[str] = Counter()
    files: set[str] = set()
    errors: list[tuple[str, str]] = []  # (tool, one-line error)

    pending_calls: dict[str, str] = {}  # toolCallId -> tool name

    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = e.get("type")
            if t == "session":
                session_id = str(e.get("id", ""))
                started_at = str(e.get("timestamp", ""))
                cwd = str(e.get("cwd", ""))
            elif t == "model_change":
                m = f"{e.get('provider')}:{e.get('modelId')}"
                if m not in models:
                    models.append(m)
            elif t != "message":
                continue
            msg = e.get("message") or {}
            role = msg.get("role")
            blocks = msg.get("content")
            if not isinstance(blocks, list):
                continue
            for b in blocks:
                if not isinstance(b, dict):
                    continue
                bt = b.get("type")
                if bt == "text" and role == "user":
                    txt = str(b.get("text", "")).strip()
                    if txt and not txt.startswith("/"):
                        user_texts.append(txt)
                elif bt == "toolCall":
                    name = str(b.get("name", "unknown"))
                    tools[name] += 1
                    cid = b.get("id")
                    if cid:
                        pending_calls[str(cid)] = name
                    args = b.get("arguments") or {}
                    for key in ("path", "file", "filePath", "target"):
                        val = args.get(key)
                        if isinstance(val, str) and val and not val.startswith("http"):
                            files.add(val.strip())
                elif bt == "text" and role == "toolResult":
                    cid = str(msg.get("toolCallId", ""))
                    if msg.get("isError") is True:
                        tool_name = pending_calls.get(cid, msg.get("toolName", "?"))
                        snippet = str(b.get("text", "")).strip().replace("\n", " ")
                        errors.append((str(tool_name), snippet[:CAP_ERROR]))

    return {
        "session_id": session_id,
        "started_at": started_at,
        "cwd": cwd,
        "models": models,
        "user_texts": user_texts,
        "tools": tools,
        "files": files,
        "errors": errors,
    }


def _truncate(s: str, n: int) -> str:
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def render(sig: dict, out_path: Path) -> None:
    date = (sig["started_at"] or datetime.now(timezone.utc).isoformat())[:10]
    short = sig["session_id"][:8] or "unknown"
    intent = _truncate(sig["user_texts"][0], CAP_INTENT) if sig["user_texts"] else "(no free-form user intent captured)"
    top_tools = [f"{n} x{c}" for n, c in sig["tools"].most_common(TOP_TOOLS)]
    top_files = sorted(f for f in sig["files"] if not f.startswith(("http",)))[:TOP_FILES]
    errs = sig["errors"][:TOP_ERRORS]

    lines: list[str] = []
    lines += [
        "---",
        f"id: sess_{short}",
        f"session: {sig['session_id']}",
        f"date: {date}",
        f"project: {os.path.basename(sig['cwd']) if sig['cwd'] else 'unknown'}",
        f"model: {', '.join(sig['models']) if sig['models'] else 'unknown'}",
        "status: candidate",
        "source: scripts/export_session_reflection.py",
        "---",
        "",
        f"# Session reflection — {date} ({short})",
        "",
        f"## Intent\n{intent}\n",
        "## Activity",
        f"- user turns captured: {len(sig['user_texts'])}",
        f"- tools: {', '.join(top_tools) if top_tools else 'none'}",
        f"- files touched: {len(top_files)} listed (top {len(top_files)})",
    ]
    for f in top_files:
        lines.append(f"  - {_truncate(f, CAP_FILE)}")
    lines += ["", "## Errors & scars (failure triples)"]
    if errs:
        for tool, snippet in errs:
            lines.append(f"- **{tool}**: {_truncate(snippet, CAP_ERROR)} — *fix: [reflection pass fills]*")
    else:
        lines.append("- (none recorded)")
    lines += [
        "",
        "## Distillation questions",
        "1. Which decision in this session was load-bearing and should become a rule with an eviction predicate?",
        "2. Which error triple (failed state / cause / fix) is reusable across sessions?",
        "3. What should be evicted from `reflection/memory.md` that this session falsified?",
        "",
        "## Eviction predicate",
        f"This file may be moved to `reflection/stale/` when a newer session supersedes it, when its distillation questions are answered in `memory.md`, or when `memory_evict` marks its rules decayed (max {MAX_OUT_LINES} lines enforced at write).",
    ]
    # Hard bound: never exceed MAX_OUT_LINES
    if len(lines) > MAX_OUT_LINES:
        keep = lines[: MAX_OUT_LINES - 1]
        keep.append(f"… truncated to {MAX_OUT_LINES} lines (bounded-reflection rule)")
        lines = keep
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PI_SESSION_FILE", "")
    if not arg or not os.path.exists(arg):
        print(f"usage: export_session_reflection.py [session.jsonl]  (no file at: {arg or '(unset PI_SESSION_FILE)'})")
        raise SystemExit(1)
    repo = Path(__file__).resolve().parent.parent
    sig = parse_session(arg)
    out = repo / "reflection" / "sessions" / f"{(sig['started_at'] or 'unknown')[:10]}_{sig['session_id'][:8]}.md"
    render(sig, out)
    print(f"wrote {out} ({out.stat().st_size} bytes, session {sig['session_id'][:12]}…, {len(sig['errors'])} errors, {len(sig['tools'])} tool types)")


if __name__ == "__main__":
    main()
