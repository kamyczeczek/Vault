"""Grounded review gate for reflect.py (candidate entropy-001-peer-review-graph).

After the improvement, reflect.py verifies cited chunk ids against the corpus
BEFORE writing digest/candidates (fail closed on ungrounded citations) and
records the review/accepted/rejected decision points in reflection/decision_points.jsonl
(ADR-007-style decision record: state + question + answer + context).
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
def isolated(tmp_path, monkeypatch):
    """Redirect trace ledger, decision ledger, and corpus to tmp_path; stub endpoint."""
    monkeypatch.setattr(agent_trace, "TRACE_DIR", tmp_path)
    monkeypatch.setattr(agent_trace, "TRACE_FILE", tmp_path / "events.jsonl")
    monkeypatch.setattr(agent_trace, "CONTEXT_FILE", tmp_path / "current_run.json")
    monkeypatch.setattr(reflect, "DECISION_LEDGER", tmp_path / "decision_points.jsonl")
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    monkeypatch.setattr(reflect, "CORPUS_DIR", corpus)
    monkeypatch.setattr(reflect, "_resolve_endpoint", lambda: ("key", "http://localhost", "model"))
    monkeypatch.setattr(
        reflect, "_build_evidence_packet",
        lambda tag_sets, limit=12, max_chunks=12: ([], {"queries": []}),
    )
    monkeypatch.setattr(reflect, "_write_digest", lambda *a, **k: None)
    return {"ledger": tmp_path / "decision_points.jsonl", "corpus": corpus}


def _ledger_records(ledger: Path) -> list[dict]:
    if not ledger.exists():
        return []
    return [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]


def _valid_llm_output(cited: list[str]) -> str:
    """Schema-valid reflection output citing the given chunk ids."""
    claims = [{"claim": "c", "evidence": list(cited), "decision": "d", "next_bet": "b"}]
    cands = [{
        "id": "entropy-001-test", "state": "proposed", "type": "candidate",
        "date": "2026-10-03", "Rule": "r", "Evidence": "`, ".join(cited),
        "Target": "t", "Action": "a", "Condition": "cond", "Reason": "why",
        "Correction": "corr",
    }]
    return json.dumps({"claims": claims, "candidates": cands, "next_bets": []})


def test_ungrounded_citation_rejected(isolated, monkeypatch):
    """BEFORE the fix: a ghost chunk id was silently shipped into the digest.
    AFTER: the run fails closed and the rejection is recorded in the ledger."""
    (isolated["corpus"] / "00_real_chunk.md").write_text("---\nid: 00_real_chunk\n---\nbody\n", encoding="utf-8")
    monkeypatch.setattr(
        reflect, "_call_model",
        lambda m, k, b, i: _valid_llm_output(["00_real_chunk", "99_ghost_chunk"]),
    )

    with pytest.raises(SystemExit):
        reflect.reflect_topic("refl-ground-fail", scratch=True)

    states = [r["state"] for r in _ledger_records(isolated["ledger"])]
    assert "review" in states
    assert "rejected" in states
    assert "accepted" not in states
    rejected = next(r for r in _ledger_records(isolated["ledger"]) if r["state"] == "rejected")
    assert rejected["detail"]["ungrounded_chunks"] == ["99_ghost_chunk"]


def test_grounded_citation_accepted(isolated, monkeypatch):
    """Fully grounded citations pass the gate; review+accepted are recorded in order."""
    (isolated["corpus"] / "00_real_chunk.md").write_text("---\nid: 00_real_chunk\n---\nbody\n", encoding="utf-8")
    monkeypatch.setattr(
        reflect, "_call_model",
        lambda m, k, b, i: _valid_llm_output(["00_real_chunk"]),
    )

    rc = reflect.reflect_topic("refl-ground-ok", scratch=True)
    assert rc == 0

    records = _ledger_records(isolated["ledger"])
    assert [r["state"] for r in records] == ["review", "accepted"]
    assert records[0]["topic"] == "refl-ground-ok"
    assert records[1]["detail"]["grounded_chunks"] == ["00_real_chunk"]
