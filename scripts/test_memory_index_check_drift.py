#!/usr/bin/env python3
"""Regression tests for memory_index_check_drift.py (E1 / scar S68).

The E1 session proved the assertion with three one-off mutations recorded in
docs/wayfinder-brain-answers/E1-schema-drift.md. Those were a *study*, not a
*regression*: if a loader changes shape again, nothing re-runs that study. This
file pins the same cases (control PASS, shift FAIL, silent-skip FAIL) as
runnable fixtures — no real store, no real index, only monkeypatched
`agent_sessions` store dirs and a temp `memory.db`.

Two extra checks guard the R22 narrowing: staleness alone must NOT fail under
`drift_only`, and an absent store is skipped, never failed.

Requires: stdlib only (no pytest). Run:
    python.exe scripts/test_memory_index_check_drift.py
Exit 0 = all pass. Exit 1 = at least one failure, printed to stderr.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import agent_sessions  # noqa: E402
import memory_index as mi  # noqa: E402
import memory_index_check_drift as dc  # noqa: E402

failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        msg = f"FAIL: {name}"
        if detail:
            msg += f" — {detail}"
        failures.append(msg)
        print(msg, file=sys.stderr)


def _droid_file(path: Path, text: str) -> None:
    """A minimal valid droid session: one `type=message` user turn."""
    path.write_text(json.dumps({
        "type": "message",
        "message": {"role": "user", "content": [{"type": "text", "text": text}]},
    }) + "\n", encoding="utf-8")


def _index_with(db: Path, sessions: list) -> sqlite3.Connection:
    """A fixture index holding exactly `sessions` (same DDL as production)."""
    con = sqlite3.connect(db)
    con.executescript(mi.DDL)
    for s in sessions:
        mi.ingest_session(con, s)
    con.commit()
    return con


def _load(agent: str) -> list:
    """The production loader's view of one store, newest-first (like ingest)."""
    return agent_sessions.get_all_sessions(agent, limit_per_agent=500, days=0)


# -----------------------------------------------------------------------
# control + shift: a directory store, read by its real loader
# -----------------------------------------------------------------------
# Bug guarded (S68 deepseek shape, and its shift variant): a session the
# store *has on disk* must be in the index; a newer one the loader can see
# but the index lacks must FAIL, naming the store.

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    store = tmp / "droid"
    store.mkdir()
    old_droid = agent_sessions.DROID_SESSIONS_DIR
    agent_sessions.DROID_SESSIONS_DIR = store
    try:
        a = store / "aaa.jsonl"
        _droid_file(a, "session A")
        os.utime(a, (1_600_000_000, 1_600_000_000))
        sA = _load("droid")[0]
        con = _index_with(tmp / "memory.db", [sA])

        # 1. control: the newest session on disk is indexed → ok
        res = dc.evaluate(con, _load("droid"), agents=["droid"])
        check(
            "control: indexed newest → ok",
            res[0].status == "ok",
            f"got {res[0]!r}",
        )

        # 2. shift: add a newer session B but do not index it
        b = store / "bbb.jsonl"
        _droid_file(b, "session B, newer")
        os.utime(b, (1_700_000_000, 1_700_000_000))
        sessions = _load("droid")
        check(
            "shift: B is the newest loaded session",
            sessions and sessions[0].id == "bbb",
            f"got {[s.id for s in sessions]!r}",
        )
        res = dc.evaluate(con, sessions, agents=["droid"])
        check(
            "shift: newest not indexed → fail (drift)",
            res[0].status == "fail" and "drift" in res[0].detail,
            f"got {res[0]!r}",
        )

        # 3. drift_only: staleness alone must not fail (this is why R22 narrows)
        res = dc.evaluate(con, sessions, agents=["droid"], drift_only=True)
        check(
            "drift_only: staleness alone → not fail",
            res[0].status != "fail",
            f"got {res[0]!r}",
        )
        con.close()
    finally:
        agent_sessions.DROID_SESSIONS_DIR = old_droid


# -----------------------------------------------------------------------
# silent-skip: a store whose file the loader cannot parse
# -----------------------------------------------------------------------
# The S68 shape exactly: the store holds a record, but the loader's dispatch
# finds no events and moves on (`if not events: continue`). The assertion must
# FAIL loudly, not read the store as empty.

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    store = tmp / "deepseek"
    store.mkdir()
    dsh = tmp / "dsh"
    dsh.mkdir()
    old_ds = agent_sessions.DEEPSEEK_SESSIONS_DIR
    old_dsh = agent_sessions.DSH_SESSIONS_DIR
    agent_sessions.DEEPSEEK_SESSIONS_DIR = store
    agent_sessions.DSH_SESSIONS_DIR = dsh
    try:
        # No type/data/role keys → load_deepseek_sessions drops the file.
        (store / "migrated.jsonl").write_text(
            '{"kind":"newformat","payload":{"x":1}}\n', encoding="utf-8")
        con = _index_with(tmp / "memory.db", [])
        sessions = _load("deepseek")
        check(
            "silent-skip: the production loader returns 0 sessions",
            sessions == [],
            f"got {sessions!r}",
        )
        res = dc.evaluate(con, sessions, agents=["deepseek"])
        check(
            "silent-skip: raw>0 & loaded==0 → fail (not a quiet skip)",
            res[0].status == "fail" and "silent skip" in res[0].detail,
            f"got {res[0]!r}",
        )
        # drift_only keeps this failure: it IS the schema condition.
        res = dc.evaluate(con, sessions, agents=["deepseek"], drift_only=True)
        check(
            "silent-skip: drift_only still fails (schema condition)",
            res[0].status == "fail",
            f"got {res[0]!r}",
        )
        con.close()
    finally:
        agent_sessions.DEEPSEEK_SESSIONS_DIR = old_ds
        agent_sessions.DSH_SESSIONS_DIR = old_dsh


# -----------------------------------------------------------------------
# absent store → skip (a fresh clone has nothing to drift)
# -----------------------------------------------------------------------

with tempfile.TemporaryDirectory() as td:
    old_droid = agent_sessions.DROID_SESSIONS_DIR
    agent_sessions.DROID_SESSIONS_DIR = Path(td) / "does-not-exist"
    try:
        res = dc.evaluate(None, [], agents=["droid"])
        check(
            "absent store → skip, not fail",
            res[0].status == "skip",
            f"got {res[0]!r}",
        )
    finally:
        agent_sessions.DROID_SESSIONS_DIR = old_droid


# -----------------------------------------------------------------------
# durable exclusion: a meta-session kept out of the index is not drift
# -----------------------------------------------------------------------

excluded_id = next(iter(mi.EXCLUDED_SESSION_IDS))
meta = agent_sessions.SessionItem(
    agent="droid", id=excluded_id, title="meta", directory="/x",
    created_at="2026-10-23 00:00:00", updated_at="2026-10-23 00:00:00",
    message_count=1, model="", raw_path="/meta.jsonl")
visible = agent_sessions.SessionItem(
    agent="droid", id="droid-visible", title="real", directory="/x",
    created_at="2026-10-01 00:00:00", updated_at="2026-10-01 00:00:00",
    message_count=1, model="", raw_path="/visible.jsonl")
old_gas = dc.get_all_sessions
dc.get_all_sessions = lambda *a, **k: [meta, visible]
try:
    loaded = dc.load_sessions_like_ingest()
finally:
    dc.get_all_sessions = old_gas
check(
    "durable exclusion: load_sessions_like_ingest drops meta-session",
    [s.id for s in loaded] == ["droid-visible"],
    f"got {[s.id for s in loaded]!r}",
)


# -----------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------

total = 9  # manually counted checks above
passed = total - len(failures)
print(f"\n{'=' * 60}")
print(f"test_memory_index_check_drift.py: {passed}/{total} passed")
if failures:
    print(f"  {len(failures)} FAILURE(S):", file=sys.stderr)
    for f in failures:
        print(f"    {f}", file=sys.stderr)
    sys.exit(1)
print("  All checks passed.")
sys.exit(0)
