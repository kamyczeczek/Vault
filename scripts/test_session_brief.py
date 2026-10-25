#!/usr/bin/env python3
"""Focused, stdlib-only tests for scripts/session_brief.py.

Run:
    python.exe scripts/test_session_brief.py
Exit 0 = all pass. Exit 1 = at least one failure on stderr.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import session_brief as sb  # noqa: E402

failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        msg = f"FAIL: {name}"
        if detail:
            msg += f" - {detail}"
        failures.append(msg)
        print(msg, file=sys.stderr)


def card(**overrides):
    base = {
        "session_id": "ses_test",
        "stable_key": "opencode:ses_test",
        "agent": "opencode",
        "model": "m",
        "date": "2026-01-01 10:00:00",
        "duration": "10m",
        "micro": False,
        "goal": {"kind": "prompt", "text": "goal"},
        "ending": {"kind": "quote", "text": "done"},
        "commits": [],
        "files": [],
        "flags": [],
        "flags_missing": [],
        "tests": [],
    }
    base.update(overrides)
    return base


def tool(name: str, inp=None, out: str = ""):
    return {
        "kind": "tool",
        "name": name,
        "status": "completed",
        "input": json.dumps(inp or {}),
        "output": out,
    }


def text(role: str, value: str):
    return {"kind": "text", "role": role, "text": value}


check("truncate: short text unchanged", sb.truncate("abc", 10) == "abc")
check("truncate: head marker", "chars" in sb.truncate("a" * 100, 20))
check("truncate: tail marker", sb.truncate("a" * 100, 20, tail=True).endswith("a" * 20))
check("hard_truncate: byte budget", sb._blen(sb.hard_truncate("ż" * 2000, 100)) <= 100)

status = tool("bash", {"command": "git status"})
pytest = tool("bash", {"command": "python -m pytest -q"})
commit = tool("bash", {"command": "git commit -m x"})
write = tool("write", {"filePath": "a.py", "content": "x = 1"})
read = tool("read", {"filePath": "a.py"})

check("bash: status noise", sb.bash_is_noise(status))
check("bash: null redirect noise", sb.bash_is_noise(tool("bash", {"command": "rg foo 2>$null"})))
check("bash: help noise", sb.bash_is_noise(tool("bash", {"command": "python scripts/x.py --help 2>&1"})))
check("bash: version noise", sb.bash_is_noise(tool("bash", {"command": "python --version; python -c \"print(1)\""})))
check("bash: get-command noise", sb.bash_is_noise(tool("bash", {"command": "Get-Command git"})))
check("bash: pytest mutating", not sb.bash_is_noise(pytest))
check("bash: commit mutating", not sb.bash_is_noise(commit))
check("bash: quoted redirect noise", sb.bash_is_noise(tool("bash", {"command": 'Select-String -Path x -Pattern "> tool"'})))
check("bash: quoted caret noise", sb.bash_is_noise(tool("bash", {"command": "Select-String -Path x -Pattern '^<!-- s -->'"})))
check("bash: unquoted redirect mutating", not sb.bash_is_noise(tool("bash", {"command": "Get-Content x > out.txt"})))
check("bash: git-rm token noise", sb.bash_is_noise(tool("bash", {"command": "ls handoff/flags | Select-String git-rm"})))
check("bash: rm command mutating", not sb.bash_is_noise(tool("bash", {"command": "rm -rf out"})))
check("path: temp noise", sb.is_noise_path(r"C:\Users\x\AppData\Local\Temp\a.py"))
check("path: workspace kept", not sb.is_noise_path("scripts/session_brief.py"))
check("tool: temp write dropped", not sb.tool_is_mutating(tool("write", {"filePath": r"C:\Users\x\AppData\Local\Temp\a.py"})))
check("tool: write mutating", sb.tool_is_mutating(write))
check("tool: read not mutating", not sb.tool_is_mutating(read))
check("tool: status bash not mutating", not sb.tool_is_mutating(status))
check("tool: skill not mutating", not sb.tool_is_mutating(tool("skill", {"skill": "tdd"})))

events = [
    text("user", "do it"),
    read,
    write,
    tool("edit", {"filePath": "b.py", "oldString": "a", "newString": "b"}),
    status,
    pytest,
    tool("question", {"question": "ok?"}, "yes"),
    tool("skill", {"skill": "tdd"}),
    tool("write", {"filePath": "c.py"}),
    tool("write", {"filePath": "d.py"}),
]
actions = sb.select_actions(events, 8)
names = [event["name"] for event in actions]
check("actions: limit", len(actions) <= 8, str(len(actions)))
check("actions: write/edit kept", names.count("write") == 2 and "edit" in names, str(names))
check("actions: pytest kept", "bash" in names and any("pytest" in (sb._bash_command(e) or "") for e in actions))
check("actions: noise dropped", "git status" not in " ".join(sb._bash_command(e) for e in actions))
check("actions: read dropped", "read" not in names)
check("actions: chronological", [events.index(e) for e in actions] == sorted(events.index(e) for e in actions))

excluded = next(iter(sb.memory.EXCLUDED_SESSION_IDS))
ok, reason = sb.value_reason(card(session_id=excluded), [])
check("value: meta dropped", not ok and reason == "meta", reason)
ok, reason = sb.value_reason(card(micro=True, goal={"kind": "none", "text": ""}), [text("user", "hi")])
check("value: micro dropped", not ok and reason == "micro", reason)
ok, reason = sb.value_reason(card(micro=True), [write])
check("value: micro with write kept", ok and reason == "ok", reason)
ok, reason = sb.value_reason(card(), [read])
check("value: read-only dropped", not ok and reason == "no_delta", reason)
ok, reason = sb.value_reason(card(), [status])
check("value: status-only dropped", not ok and reason == "no_delta", reason)
check("delta: absent flag separated", sb.delta_text({"flags": ["a-2026-01-01", "b-2026-01-02"], "flags_missing": ["a-2026-01-01"]}) == "flags: `b-2026-01-02`; flags absent now: `a-2026-01-01`")
check("delta: only absent flags", sb.delta_text({"flags": ["a-2026-01-01"], "flags_missing": ["a-2026-01-01"]}) == "flags absent now: `a-2026-01-01`")
ok, reason = sb.value_reason(card(), [pytest])
check("value: pytest kept", ok and reason == "ok", reason)
ok, reason = sb.value_reason(card(commits=["abc123"]), [])
check("value: commit kept", ok and reason == "ok", reason)

session = SimpleNamespace(
    agent="opencode",
    id="ses_test",
    title="Test\nsession",
    model="m",
    created_at="2026-01-01 10:00:00",
    updated_at="2026-01-01 10:10:00",
    message_count=10,
)
rendered = sb.render_session(
    1,
    session,
    card(
        commits=["abc123"],
        files=["a.py"],
        flags=["handoff/flags/x.md"],
        tests=["2 passed"],
        ending={"kind": "quote", "text": "Completed the change and verified the tests."},
    ),
    events,
    8,
    8,
)
check("render: header", "## 1. Test session" in rendered)
check("render: goal", "**Goal**: goal" in rendered)
check("render: delta", "abc123" in rendered and "2 passed" in rendered)
check("render: write action", "**write**" in rendered and "a.py" in rendered)
check("render: pytest action", "**bash**" in rendered and "pytest" in rendered)
check("render: noise absent", "git status" not in rendered)
check("render: ending", "Completed the change" in rendered)
check("render: evidence command", "agent_sessions.py export opencode ses_test" in rendered)
tight = sb.render_session(1, session, card(commits=["abc123"]), events, 1, 8)
check("render: per-session budget", sb._blen(tight) <= 1024, str(sb._blen(tight)))

check("goal fallback", sb.goal_text(card(goal={"kind": "none", "text": ""}), [text("user", "hello")]) == "hello")
check(
    "ending fallback",
    sb.ending_text(card(ending={"kind": "none"}), [text("assistant", "bye now, the task is complete")])
    == "bye now, the task is complete",
)
check(
    "ending trivial fallback",
    sb.ending_text(card(ending={"kind": "quote", "text": "."}), [text("assistant", "a real summary of the change")])
    == "a real summary of the change",
)

if failures:
    print(f"\nFAILED {len(failures)}", file=sys.stderr)
    raise SystemExit(1)
print("OK session_brief")
