#!/usr/bin/env python3
"""Contract tests for the Ralph loop controller."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def run_ralph(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    script = Path(__file__).parent.parent / "scripts" / "ralph.py"
    return subprocess.run(
        [sys.executable, str(script)] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def read_state(ralph_dir: Path) -> dict:
    path = ralph_dir / "STATE.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def stamp_handoff(project: Path, when: str = "2026-01-01T00:00:00+00:00") -> Path:
    state = read_state(project / ".ralph")
    run_dir = project / ".ralph" / "runs" / state["run"].replace(".ralph\\runs\\", "").replace(".ralph/runs/", "")
    handoff = run_dir / "HANDOFF.md"
    handoff.write_text(f"---\nupdated: {when}\n---\n\n# Handoff\n\nNext session: continue the run.\n", encoding="utf-8")
    return handoff


def test_init_creates_skeleton(tmp_path: Path) -> None:
    cwd = Path(__file__).parent.parent.parent
    project = tmp_path / "example-project"
    project.mkdir(exist_ok=True)

    result = run_ralph(
        [
            "--project",
            str(project),
            "--workspace",
            str(tmp_path),
            "init",
            "test-feature",
            "add unit tests",
            "tests passing",
            "--frontier",
            "D-001",
        ],
        cwd=cwd,
    )
    assert result.returncode == 0, result.stderr

    state = read_state(project / ".ralph")
    assert state["status"] == "READY"
    assert state["iteration"] == 0
    assert state["next_frontier"] == "D-001"
    assert "run" in state

    run_dir = project / ".ralph" / "runs" / state["run"].replace(".ralph\\runs\\", "").replace(".ralph/runs/", "")
    assert run_dir.exists()

    # REQUEST.md
    assert (run_dir / "REQUEST.md").exists()
    # PLAN.md
    assert (run_dir / "PLAN.md").exists()
    # decisions/D-001.md
    assert (run_dir / "decisions" / "D-001.md").exists()
    # iterations/ directory
    assert (run_dir / "iterations").is_dir()
    # HANDOFF.md
    assert (run_dir / "HANDOFF.md").exists()
    # GATES.md
    assert (run_dir / "GATES.md").exists()
    # LEARNINGS.md
    assert (run_dir / "LEARNINGS.md").exists()


def test_status_transitions(tmp_path: Path) -> None:
    cwd = Path(__file__).parent.parent.parent
    project = tmp_path / "example-project2"
    project.mkdir(exist_ok=True)

    run_ralph(["--project", str(project), "init", "feat", "intent", "dest"], cwd=cwd)

    # set-status WAITING_FOR_CONFIRMATION
    result = run_ralph(
        ["--project", str(project), "set-status", "WAITING_FOR_CONFIRMATION", "--frontier", "D-002"],
        cwd=cwd,
    )
    assert result.returncode == 0
    state = read_state(project / ".ralph")
    assert state["status"] == "WAITING_FOR_CONFIRMATION"
    assert state["next_frontier"] == "D-002"
    assert state["iteration"] == 0

    # approve -> iteration increments
    result = run_ralph(["--project", str(project), "approve", "--frontier", "D-003"], cwd=cwd)
    assert result.returncode == 0
    state = read_state(project / ".ralph")
    assert state["status"] == "APPROVED"
    assert state["iteration"] == 1
    assert state["next_frontier"] == "D-003"


def test_index_generation(tmp_path: Path) -> None:
    cwd = Path(__file__).parent.parent.parent
    project1 = tmp_path / "index-proj1"
    project2 = tmp_path / "index-proj2"
    project1.mkdir(exist_ok=True)
    project2.mkdir(exist_ok=True)

    run_ralph(["--project", str(project1), "--workspace", str(tmp_path), "init", "a", "i1", "d1"], cwd=cwd)
    run_ralph(["--project", str(project2), "--workspace", str(tmp_path), "init", "b", "i2", "d2"], cwd=cwd)

    run_ralph(["--project", str(project1), "--workspace", str(tmp_path), "index"], cwd=cwd)

    index = tmp_path / ".ralph" / "INDEX.md"
    assert index.exists()
    content = index.read_text(encoding="utf-8")
    assert "index-proj1" in content
    assert "index-proj2" in content

    registry = tmp_path / ".ralph" / "registry.json"
    assert registry.exists()
    data = json.loads(registry.read_text(encoding="utf-8"))
    assert len(data["entries"]) == 2


def test_invalid_status_rejected(tmp_path: Path) -> None:
    cwd = Path(__file__).parent.parent.parent
    project = tmp_path / "example-project3"
    project.mkdir(exist_ok=True)

    run_ralph(["--project", str(project), "init", "feat", "intent", "dest"], cwd=cwd)

    result = run_ralph(["--project", str(project), "set-status", "INVALID"], cwd=cwd)
    assert result.returncode != 0


def test_history_append_only(tmp_path: Path) -> None:
    cwd = Path(__file__).parent.parent.parent
    project = tmp_path / "example-project4"
    project.mkdir(exist_ok=True)

    run_ralph(["--project", str(project), "init", "feat", "intent", "dest"], cwd=cwd)
    run_ralph(["--project", str(project), "set-status", "WORKING"], cwd=cwd)

    history = project / ".ralph" / "history.jsonl"
    lines = history.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 2
    for line in lines:
        event = json.loads(line)
        assert "event" in event


def test_record_iteration(tmp_path: Path) -> None:
    cwd = Path(__file__).parent.parent.parent
    project = tmp_path / "example-project5"
    project.mkdir(exist_ok=True)

    run_ralph(["--project", str(project), "init", "feat", "intent", "dest"], cwd=cwd)
    run_ralph(["--project", str(project), "set-status", "WORKING"], cwd=cwd)

    # Unstamped handoff: the iteration must be refused.
    result = run_ralph([
        "--project", str(project), "record-iteration",
        "--decision", "D-001", "--title", "first iteration", "--intent", "add tests",
        "--outcome", "CONTINUE", "--next-frontier", "D-002",
    ], cwd=cwd)
    assert result.returncode != 0
    assert "HANDOFF" in result.stderr

    stamp_handoff(project)

    result = run_ralph([
        "--project", str(project), "record-iteration",
        "--decision", "D-001",
        "--title", "first iteration",
        "--intent", "add tests",
        "--outcome", "CONTINUE",
        "--next-frontier", "D-002",
    ], cwd=cwd)
    assert result.returncode == 0, result.stderr

    state = read_state(project / ".ralph")
    assert state["status"] == "WAITING_FOR_CONFIRMATION"
    assert state["last_iteration"] == "I-001"
    assert state["last_decision"] == "D-001"
    assert state["next_frontier"] == "D-002"
    assert state["handoff_at"] == "2026-01-01T00:00:00+00:00"

    run_dir = project / ".ralph" / "runs" / state["run"].replace(".ralph\\runs\\", "").replace(".ralph/runs/", "")
    iteration_file = run_dir / "iterations" / "I-001.md"
    assert iteration_file.exists()
    content = iteration_file.read_text(encoding="utf-8")
    assert "D-001" in content
    assert "first iteration" in content
    assert "CONTINUE" in content
    assert "D-002" in content


def test_done_blocked_by_unmet_gates(tmp_path: Path) -> None:
    cwd = Path(__file__).parent.parent.parent
    project = tmp_path / "example-project6"
    project.mkdir(exist_ok=True)

    run_ralph(["--project", str(project), "init", "feat", "intent", "dest"], cwd=cwd)
    run_ralph(["--project", str(project), "set-status", "WORKING"], cwd=cwd)
    stamp_handoff(project)

    # init copies a GATES.md with two open placeholder gates -> DONE must be refused.
    result = run_ralph([
        "--project", str(project), "record-iteration",
        "--decision", "D-001", "--title", "t", "--intent", "i",
        "--outcome", "DONE",
    ], cwd=cwd)
    assert result.returncode != 0
    assert "DONE blocked" in result.stderr

    gates = run_ralph(["--project", str(project), "gates"], cwd=cwd)
    assert gates.returncode == 0
    report = json.loads(gates.stdout)
    assert report["unmet"] == 2 and report["abandoned"] == 0 and report["ok"] is False

    # No-observable-outcome run: declare `GATES: none` and drop the placeholders.
    state = read_state(project / ".ralph")
    run_dir = project / ".ralph" / "runs" / state["run"].replace(".ralph\\runs\\", "").replace(".ralph/runs/", "")
    (run_dir / "GATES.md").write_text("# Gates\n\nGATES: none\n", encoding="utf-8")

    result = run_ralph([
        "--project", str(project), "record-iteration",
        "--decision", "D-001", "--title", "t", "--intent", "i",
        "--outcome", "DONE",
    ], cwd=cwd)
    assert result.returncode == 0, result.stderr
    assert read_state(project / ".ralph")["status"] == "WAITING_FOR_CONFIRMATION"


def test_resume_and_gates(tmp_path: Path) -> None:
    cwd = Path(__file__).parent.parent.parent
    project = tmp_path / "example-project7"
    project.mkdir(exist_ok=True)

    run_ralph(["--project", str(project), "init", "feat", "intent", "dest", "--frontier", "D-001"], cwd=cwd)
    result = run_ralph(["--project", str(project), "resume"], cwd=cwd)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "READY"
    assert payload["next_frontier"] == "D-001"
    assert payload["handoff_at"] is None  # init template is a placeholder, not a stamp
    assert payload["gates"]["unmet"] == 2
    assert any(p.endswith("HANDOFF.md") for p in payload["read_next"])
    assert any(p.endswith("D-001.md") for p in payload["read_next"])

    result = run_ralph(["--project", str(project), "gates"], cwd=cwd)
    assert result.returncode == 0
    assert json.loads(result.stdout)["present"] is True


if __name__ == "__main__":
    for test_func in [test_init_creates_skeleton, test_status_transitions, test_index_generation, test_invalid_status_rejected, test_history_append_only, test_record_iteration, test_done_blocked_by_unmet_gates, test_resume_and_gates]:
        with TemporaryDirectory() as td:
            test_func(Path(td))
    print("ALL TESTS PASS")