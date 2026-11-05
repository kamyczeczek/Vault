"""reflect.py failure visibility: a failed run must leave a trace record.

Defect recorded as the G12 follow-up open work: on failure reflect.py used to
write no artifact — a failed run was indistinguishable from a never-run one.
The fix emits run/failure trace events into the agent_trace ledger
(reflection/trace/events.jsonl), the same ledger spawn.py's failure paths use.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REFLECT_DIR = ROOT / "pipeline" / "06_reflect"
for p in (str(REFLECT_DIR), str(ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import agent_trace  # noqa: E402
import reflect  # noqa: E402


@pytest.fixture
def trace_file(tmp_path, monkeypatch):
    """Point the agent_trace ledger at tmp_path so tests never pollute the real events.jsonl."""
    monkeypatch.setattr(agent_trace, "TRACE_DIR", tmp_path)
    monkeypatch.setattr(agent_trace, "TRACE_FILE", tmp_path / "events.jsonl")
    monkeypatch.setattr(agent_trace, "CONTEXT_FILE", tmp_path / "current_run.json")
    return tmp_path / "events.jsonl"


def _events(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _stub_retrieval(monkeypatch) -> None:
    """Cut the run off from the real graph and endpoint so tests are zero-cost."""
    monkeypatch.setattr(
        reflect, "_build_evidence_packet",
        lambda tag_sets, limit=12, max_chunks=12: ([], {"queries": []}),
    )
    monkeypatch.setattr(reflect, "_resolve_endpoint", lambda: ("key", "http://localhost", "model"))
    # the grounded review gate logs decision points; keep the real ledger clean
    import tempfile
    monkeypatch.setattr(reflect, "DECISION_LEDGER", Path(tempfile.gettempdir()) / "reflect_test_decision_points.jsonl")


def test_failed_model_call_writes_failure_trace(trace_file, monkeypatch):
    _stub_retrieval(monkeypatch)

    def broken_model(messages, api_key, base_url, model_id):
        raise OSError("endpoint down")

    monkeypatch.setattr(reflect, "_call_model", broken_model)

    with pytest.raises(OSError):
        reflect.reflect_topic("refl-fail-model", scratch=True)

    events = _events(trace_file)
    failure = next(e for e in events if e["kind"] == "failure")
    assert failure["status"] == "failed"
    assert failure["failure_kind"] == "OSError"
    assert failure["topic"] == "refl-fail-model"
    assert failure["runner"] == "reflect.py"
    assert failure["artifact"] == "reflection/scratch/digests/refl-fail-model.md"
    started = next(e for e in events if e["kind"] == "run" and e["status"] == "started")
    assert started["run_id"] == failure["run_id"]


def test_bad_json_writes_failure_trace(trace_file, monkeypatch):
    _stub_retrieval(monkeypatch)
    monkeypatch.setattr(reflect, "_call_model", lambda m, k, b, i: "{not json")

    with pytest.raises(SystemExit):
        reflect.reflect_topic("refl-fail-json", scratch=True)

    failure = next(e for e in _events(trace_file) if e["kind"] == "failure")
    assert failure["failure_kind"] == "bad_json"
    assert failure["condition"].startswith("LLM output not valid JSON")


def test_missing_key_writes_failure_trace(trace_file, monkeypatch):
    _stub_retrieval(monkeypatch)
    monkeypatch.setattr(
        reflect, "_call_model",
        lambda m, k, b, i: json.dumps({"claims": []}),  # no candidates/next_bets
    )

    with pytest.raises(SystemExit):
        reflect.reflect_topic("refl-fail-key", scratch=True)

    failure = next(e for e in _events(trace_file) if e["kind"] == "failure")
    assert failure["failure_kind"] == "missing_key"


def test_success_run_writes_completed_trace(trace_file, monkeypatch):
    _stub_retrieval(monkeypatch)
    monkeypatch.setattr(
        reflect, "_call_model",
        lambda m, k, b, i: json.dumps(
            {"claims": [], "candidates": [], "next_bets": []}
        ),
    )
    # No real digest/candidate writes: the success test asserts the ledger, not the artifacts.
    monkeypatch.setattr(reflect, "_write_digest", lambda *a, **k: None)

    rc = reflect.reflect_topic("refl-ok", scratch=True)
    assert rc == 0

    statuses = [e["status"] for e in _events(trace_file) if e["kind"] == "run"]
    assert "started" in statuses
    assert "completed" in statuses
    assert not any(e["kind"] == "failure" for e in _events(trace_file))
