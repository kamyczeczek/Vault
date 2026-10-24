import sys
import json
import tempfile
from pathlib import Path

import pytest

# Ensure forge-guardrails scripts directory is in sys.path
GUARD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(GUARD_DIR))

import forge_hook


def test_active_recall_blocks_write_when_not_done(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        forge_dir = root / ".forge"
        forge_dir.mkdir()

        # state with recall_done = False
        state = {
            "task": "test",
            "current_step": "implement",
            "completed_steps": ["read_repo_rules", "understand_task", "write_test", "verify_test_fails"],
            "recall_done": False
        }
        (forge_dir / "state.json").write_text(json.dumps(state), encoding="utf-8")
        (forge_dir / "policy.yaml").write_text("rules:\n  git:\n    forbid_destructive_commands: false\n", encoding="utf-8")

        payload = {
            "working_dir": str(root),
            "tool_name": "write",
            "tool_input": {"path": "foo.py", "content": "print('hello')"}
        }

        exc_info = None
        try:
            forge_hook.cmd_pre_tool(payload)
        except SystemExit as e:
            exc_info = e

        assert exc_info is not None
        assert exc_info.code == 2

        captured = capsys.readouterr()
        out_json = json.loads(captured.out.strip().splitlines()[-1])
        assert out_json["decision"] == "block"
        assert "RECALL" in out_json["reason"]


def test_active_recall_allows_write_when_done(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        forge_dir = root / ".forge"
        forge_dir.mkdir()

        state = {
            "task": "test",
            "current_step": "implement",
            "completed_steps": ["read_repo_rules", "understand_task", "write_test", "verify_test_fails"],
            "recall_done": True
        }
        (forge_dir / "state.json").write_text(json.dumps(state), encoding="utf-8")
        (forge_dir / "policy.yaml").write_text("rules:\n  git:\n    forbid_destructive_commands: false\n", encoding="utf-8")

        payload = {
            "working_dir": str(root),
            "tool_name": "write",
            "tool_input": {"path": "foo.py", "content": "print('hello')"}
        }

        # Should not raise SystemExit due to RECALL (might raise due to step enforcement, but not RECALL block)
        # NOTE: no SystemExit at all is OK — write with recall_done:true is not
        # blocked by RECALL; step-enforcement may be inactive when state steps are complete.
        exc_info = None
        try:
            forge_hook.cmd_pre_tool(payload)
        except SystemExit as e:
            exc_info = e

        captured = capsys.readouterr()
        if exc_info is not None:
            # If it blocked, ensure it's NOT a RECALL block.
            # The last stdout line is the JSON verdict — if it doesn't parse,
            # the test must FAIL (no silent pass on undecodable output).
            lines = [l for l in captured.out.strip().splitlines() if l.strip()]
            assert lines, "SystemExit raised but no stdout verdict to inspect"
            out_json = json.loads(lines[-1])
            assert "RECALL" not in out_json.get("reason", "")


def test_active_recall_does_not_block_read_tool(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        forge_dir = root / ".forge"
        forge_dir.mkdir()

        state = {
            "task": "test",
            "current_step": "read_repo_rules",
            "completed_steps": [],
            "recall_done": False
        }
        (forge_dir / "state.json").write_text(json.dumps(state), encoding="utf-8")
        (forge_dir / "policy.yaml").write_text("", encoding="utf-8")

        payload = {
            "working_dir": str(root),
            "tool_name": "read",
            "tool_input": {"path": "README.md"}
        }

        try:
            forge_hook.cmd_pre_tool(payload)
        except SystemExit as e:
            pytest.fail(f"Read tool should not be blocked by RECALL, but got SystemExit({e.code})")
