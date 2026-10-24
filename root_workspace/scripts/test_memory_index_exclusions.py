#!/usr/bin/env python3
"""Regression tests for the durable meta-session exclusions (2026-10-23).

A removed four meta-sessions from the derived memory store, but the next
`ingest` re-added them because `--exclude-session-id` is per-run; the retrieval
eval fell 15/15 -> 13/15. B makes the list checked-in and authoritative:
`ingest` skips and purges them, `freshness` and the drift checker do not read
them as "on disk".

Requires: stdlib only (no pytest). Run:
    python.exe scripts/test_memory_index_exclusions.py
Exit 0 = all pass. Exit 1 = at least one failure, printed to stderr.
"""
from __future__ import annotations

import contextlib
import io
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import memory_index as mi  # noqa: E402
from agent_sessions import SessionItem  # noqa: E402

failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        msg = f"FAIL: {name}"
        if detail:
            msg += f" — {detail}"
        failures.append(msg)
        print(msg, file=sys.stderr)


def _session(stamp: str, session_id: str = "ses_real",
             text_markdown: str = "# Real\nreal body") -> SessionItem:
    return SessionItem(
        agent="opencode",
        id=session_id,
        title="t",
        directory="/x",
        created_at=stamp,
        updated_at=stamp,
        message_count=1,
        model="",
        raw_path=f"/{session_id}.json",
        text_markdown=text_markdown,
    )


def _run_freshness(db_path: Path, sessions: list) -> tuple[int, str]:
    old_path = mi.DB_PATH
    old_gas = mi.get_all_sessions
    mi.DB_PATH = db_path
    mi.get_all_sessions = lambda *a, **k: sessions
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = mi.freshness()
    finally:
        mi.DB_PATH = old_path
        mi.get_all_sessions = old_gas
    return rc, buf.getvalue()


# -----------------------------------------------------------------------
# 1. The list and the filter
# -----------------------------------------------------------------------

excluded_ids = set(mi.EXCLUDED_SESSION_IDS)
excluded_id = next(iter(excluded_ids))
check(
    "exclusions: at least the four 2026-10-23 ids are checked in",
    len(excluded_ids) >= 4,
    f"got {sorted(excluded_ids)!r}",
)
check(
    "exclusions: is_excluded accepts list ids and rejects a normal id",
    all(mi.is_excluded(i) for i in excluded_ids)
    and not mi.is_excluded("ses_not_a_meta_session"),
)

meta = _session("2026-10-23 00:00:00", session_id=excluded_id,
                text_markdown="# Meta\nmeta body")
kept = _session("2026-10-01 00:00:00")
check(
    "exclusions: filter_excluded drops only the meta-session",
    [s.id for s in mi.filter_excluded([kept, meta])] == ["ses_real"],
    f"got {[s.id for s in mi.filter_excluded([kept, meta])]!r}",
)

# -----------------------------------------------------------------------
# 2. Purge makes the list authoritative over an existing derived store
# -----------------------------------------------------------------------

with tempfile.TemporaryDirectory() as td:
    db = Path(td) / "memory.db"
    con = sqlite3.connect(db)
    con.executescript(mi.DDL)
    mi.ingest_session(con, kept)
    mi.ingest_session(con, meta)
    before_meta = con.execute("SELECT COUNT(*) FROM sessions_meta").fetchone()[0]
    purged = mi.purge_excluded(con)
    after_meta = con.execute("SELECT COUNT(*) FROM sessions_meta").fetchone()[0]
    meta_chunks = con.execute(
        "SELECT COUNT(*) FROM memory_fts WHERE session_id=?", (excluded_id,)
    ).fetchone()[0]
    kept_chunks = con.execute(
        "SELECT COUNT(*) FROM memory_fts WHERE session_id=?", ("ses_real",)
    ).fetchone()[0]
    purged_again = mi.purge_excluded(con)
    con.close()
    check(
        "exclusions: purge_excluded removes the meta row and its chunks",
        before_meta == 2 and purged == 1 and after_meta == 1
        and meta_chunks == 0 and kept_chunks >= 1,
        f"meta {before_meta}->{after_meta}, purged={purged}, "
        f"chunks meta={meta_chunks} kept={kept_chunks}",
    )
    check(
        "exclusions: purge_excluded is idempotent",
        purged_again == 0,
        f"second purge returned {purged_again}",
    )

# -----------------------------------------------------------------------
# 3. Freshness must not read an excluded newest session as lag
# -----------------------------------------------------------------------

with tempfile.TemporaryDirectory() as td:
    db = Path(td) / "memory.db"
    con = sqlite3.connect(db)
    con.executescript(mi.DDL)
    mi.ingest_session(con, kept)
    con.commit()
    con.close()
    rc_exc, out_exc = _run_freshness(db, [kept, meta])
    check(
        "exclusions: excluded newest session is not a freshness failure",
        rc_exc == 0 and out_exc.startswith("OK"),
        f"rc={rc_exc} out={out_exc!r}",
    )

# -----------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------

total = 5
passed = total - len(failures)
print(f"\n{'=' * 60}")
print(f"test_memory_index_exclusions.py: {passed}/{total} passed")
if failures:
    print(f"  {len(failures)} FAILURE(S):", file=sys.stderr)
    for f in failures:
        print(f"    {f}", file=sys.stderr)
    sys.exit(1)
print("  All checks passed.")
sys.exit(0)
