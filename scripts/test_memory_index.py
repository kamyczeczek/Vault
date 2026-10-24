#!/usr/bin/env python3
"""Regression tests for memory_index.py.

Each test guards one specific bug that was found and fixed during the
memory-index build sessions. If any of these regresses, the test fails
with a message naming the original defect.

Requires: stdlib only (no pytest). Run:
    python.exe scripts/test_memory_index.py
Exit 0 = all pass. Exit 1 = at least one failure, printed to stderr.
"""
from __future__ import annotations

import contextlib
import io
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import memory_index as mi
from agent_sessions import SessionItem
from memory_index import (
    _classify_chunk,
    _sanitize_fts_term,
    _build_fts_query,
    format_results,
    format_brief,
    query_memory,
    get_chunk,
    freshness,
    log_usage,
    print_usage,
    DDL,
)


failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        msg = f"FAIL: {name}"
        if detail:
            msg += f" — {detail}"
        failures.append(msg)
        print(msg, file=sys.stderr)


# -----------------------------------------------------------------------
# 1. _classify_chunk: reasoning blocks must NOT trigger "decision"
# -----------------------------------------------------------------------
# Bug: _DECISION_RE matched "decided" inside <details><summary>reasoning —
# tagging internal model monologue as an architectural decision.
# Measured: 54% FP before fix.

REASONING_ONLY = (
    '<details><summary>reasoning</summary>\n'
    'I decided to read the file first. Let me reconsider the approach.\n'
    '</details>\n'
)
check(
    "classify: reasoning-only block → content, not decision",
    _classify_chunk(REASONING_ONLY) == "content",
    f"got {_classify_chunk(REASONING_ONLY)!r}",
)

# A real decision outside reasoning should still be tagged.
REAL_DECISION = (
    "## Decision\n"
    "We decided to use FTS5 with unicode61 tokenizer because it handles\n"
    "diacritics and is stdlib-only.\n"
)
check(
    "classify: explicit decision heading → decision",
    _classify_chunk(REAL_DECISION) == "decision",
    f"got {_classify_chunk(REAL_DECISION)!r}",
)

# -----------------------------------------------------------------------
# 2. _classify_chunk: tool output blocks must NOT trigger "decision"
# -----------------------------------------------------------------------
# Bug: `> **tool** bash` output containing "implemented" or "fixed" in
# command text was tagged as decision.

TOOL_BLOCK = (
    '> **tool** `bash` · completed\n'
    '> in: `{"command": "git diff --cached --check"}`\n'
    '> out: `fixed whitespace in line 42, implemented the solution`\n'
)
check(
    "classify: tool output with decision words → not decision",
    _classify_chunk(TOOL_BLOCK) != "decision",
    f"got {_classify_chunk(TOOL_BLOCK)!r}",
)

# -----------------------------------------------------------------------
# 3. _classify_chunk: error asymmetry is intentional
# -----------------------------------------------------------------------
# Error is more permissive (searches original text as fallback).
# A reasoning block with "error" should still be tagged as error.

REASONING_WITH_ERROR = (
    '<details><summary>reasoning</summary>\n'
    'There was a traceback error in the pipeline.\n'
    '</details>\n'
)
check(
    "classify: reasoning with error word → error (permissive)",
    _classify_chunk(REASONING_WITH_ERROR) == "error",
    f"got {_classify_chunk(REASONING_WITH_ERROR)!r}",
)

# -----------------------------------------------------------------------
# 4. _sanitize_fts_term: FTS5 syntax chars are stripped
# -----------------------------------------------------------------------
# Bug potential: unescaped quotes, parens, etc. cause sqlite3.OperationalError.

check(
    "sanitize: strips double quotes",
    '"' not in _sanitize_fts_term('"hello"').replace('"hello"', ''),
)
check(
    "sanitize: empty input → empty output",
    _sanitize_fts_term("") == "",
)
check(
    "sanitize: pure punctuation → empty",
    _sanitize_fts_term("***") == "",
)

# -----------------------------------------------------------------------
# 5. _sanitize_fts_term: compound identifiers stay as phrase match
# -----------------------------------------------------------------------
# Bug: splitting check_workspace_integrity into subtokens degraded
# precision from 35% to 25%. Reverted. The term must stay intact.

result = _sanitize_fts_term("check_workspace_integrity")
check(
    "sanitize: compound identifier is NOT split into subtokens",
    "AND" not in result,
    f"got {result!r} — splitting was reverted because it degraded eval from 35% to 25%",
)

# Alphanumeric terms get prefix match.
check(
    "sanitize: alphanumeric term gets prefix *",
    _sanitize_fts_term("whitespace") == '"whitespace"*',
    f"got {_sanitize_fts_term('whitespace')!r}",
)

# Short terms don't get prefix.
check(
    "sanitize: 2-char term gets no prefix",
    _sanitize_fts_term("py") == '"py"',
    f"got {_sanitize_fts_term('py')!r}",
)

# -----------------------------------------------------------------------
# 6. format_results: chunk_id is present in --full output
# -----------------------------------------------------------------------
# Bug: format_results omitted chunk_id, making brief-then-drill impossible.

fake_results = [{
    "chunk_id": "opencode::ses_abc12345::7",
    "agent": "opencode",
    "session_id": "ses_abc12345",
    "session_title": "Test Session",
    "session_date": "2026-10-01 12:00:00",
    "raw_path": "/fake/path",
    "chunk_type": "error",
    "heading": "Something broke",
    "snippet": "error traceback here",
    "score": -5.0,
}]
full_output = format_results(fake_results, "test query")
check(
    "format_results: chunk_id appears in output",
    "opencode::ses_abc12345::7" in full_output,
    "chunk_id missing from --full output — breaks drill-down",
)
check(
    "format_results: Chunk label line present",
    "Chunk  :" in full_output,
    "Chunk label line missing",
)

# -----------------------------------------------------------------------
# 7. format_brief: context indicator visible without --full
# -----------------------------------------------------------------------
# Bug: --with-context computed context chunks but format_brief didn't
# show them, so the flag was invisible in the default (brief) view.

fake_with_ctx = [{
    "chunk_id": "pi::ses_xyz::10",
    "agent": "pi",
    "session_id": "ses_xyz",
    "session_title": "Context Test",
    "session_date": "2026-10-02 14:00:00",
    "raw_path": "/fake",
    "chunk_type": "error",
    "heading": "gate failed",
    "snippet": "exit code 1",
    "score": -3.0,
    "context": [
        {"chunk_id": "pi::ses_xyz::11", "chunk_type": "content", "heading": "next step"},
    ],
}]
brief_output = format_brief(fake_with_ctx, "test")
check(
    "format_brief: context indicator (+Nctx) shown",
    "(+1ctx)" in brief_output,
    f"context indicator missing from brief output:\n{brief_output}",
)

# Without context, no tag should appear.
fake_no_ctx = [{
    "chunk_id": "pi::ses_xyz::10",
    "agent": "pi",
    "session_id": "ses_xyz",
    "session_title": "No Context",
    "session_date": "2026-10-02 14:00:00",
    "raw_path": "/fake",
    "chunk_type": "error",
    "heading": "gate failed",
    "snippet": "exit code 1",
    "score": -3.0,
}]
brief_no_ctx = format_brief(fake_no_ctx, "test")
check(
    "format_brief: no spurious ctx tag without context",
    "ctx)" not in brief_no_ctx,
    f"spurious context tag in output:\n{brief_no_ctx}",
)

# -----------------------------------------------------------------------
# 8. _build_fts_query: AND-first, not OR-only
# -----------------------------------------------------------------------
# Bug: original query_memory used OR for all terms, creating noise.

and_query = _build_fts_query(["git", "diff", "check"], op="AND")
check(
    "build_fts_query: AND joins terms",
    " AND " in and_query,
    f"got {and_query!r}",
)

or_query = _build_fts_query(["git", "diff"], op="OR")
check(
    "build_fts_query: OR mode works as fallback",
    " OR " in or_query,
    f"got {or_query!r}",
)

# -----------------------------------------------------------------------
# 9. query_memory: AND-first, OR only when AND is empty
# -----------------------------------------------------------------------
# Bug: OR-only MATCH returned every chunk that held *any* term. The contract
# is "more words = narrower"; OR is a fallback so a too-specific AND is not
# a false "nobody has hit this".


def _fts_con() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.executescript(DDL)
    return con


def _put(con: sqlite3.Connection, chunk_id: str, body: str, session_id: str) -> None:
    agent = chunk_id.split("::", 1)[0]
    con.execute(
        "INSERT INTO memory_fts VALUES (?,?,?,?,?,?,?,?,?)",
        (
            chunk_id,
            agent,
            session_id,
            "title",
            "2026-10-01 00:00:00",
            "/x",
            "content",
            "heading",
            body,
        ),
    )
    con.commit()


and_con = _fts_con()
_put(and_con, "opencode::ses_andbothxx::0", "git diff whitespace check failed", "ses_andbothxx")
_put(and_con, "opencode::ses_gitalone::0", "git repository clone succeeded", "ses_gitalone")
and_hits = query_memory(and_con, "git whitespace")
and_ids = [r["chunk_id"] for r in and_hits]
check(
    "query_memory: AND keeps only chunks that hold every term",
    and_ids == ["opencode::ses_andbothxx::0"],
    f"got {and_ids!r}",
)
and_con.close()

or_con = _fts_con()
_put(or_con, "opencode::ses_alphaaaaaa::0", "alpha unique token here", "ses_alphaaaaaa")
_put(or_con, "opencode::ses_betabbbbbb::0", "beta other token there", "ses_betabbbbbb")
or_hits = query_memory(or_con, "alpha beta")
or_ids = sorted(r["chunk_id"] for r in or_hits)
check(
    "query_memory: OR fallback when AND matches nothing",
    or_ids == ["opencode::ses_alphaaaaaa::0", "opencode::ses_betabbbbbb::0"],
    f"got {or_ids!r} — AND miss must not look like an empty index",
)
or_con.close()

# -----------------------------------------------------------------------
# 10. get_chunk: miss is None (caller exits 1); hit prints the body
# -----------------------------------------------------------------------
# Bug: get returned 0 on a bad id, so a miss and an empty body were the
# same to anyone reading only the exit code.

get_con = _fts_con()
_put(get_con, "opencode::ses_getbodyxx::0", "the full chunk body", "ses_getbodyxx")
miss = get_chunk(get_con, "opencode::ses_missingx::0")
check("get_chunk: unknown id → None", miss is None, f"got {miss!r}")
hit = get_chunk(get_con, "opencode::ses_getbodyxx::0")
check(
    "get_chunk: hit includes the body",
    hit is not None and "the full chunk body" in hit,
    f"got {hit!r}",
)

old_open = mi.open_db
old_argv = sys.argv
mi.open_db = lambda: get_con
sys.argv = ["memory_index.py", "get", "opencode::ses_nosuchxx::0"]
err = io.StringIO()
try:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        try:
            get_rc = mi.main()
        except SystemExit as exc:
            get_rc = exc.code if isinstance(exc.code, int) else 1
finally:
    mi.open_db = old_open
    sys.argv = old_argv
    get_con.close()
check(
    "get CLI: miss exits 1",
    get_rc == 1,
    f"got rc={get_rc} — a bad id used to look like success",
)

# -----------------------------------------------------------------------
# 11. freshness: cannot-compare is UNVERIFIED, not a green OK
# -----------------------------------------------------------------------
# Bug: WSL python3 saw no Windows agent stores and printed
# `OK — no agent stores readable` with rc=0. An index that exists but
# cannot be compared is a failed check, not a skipped one.


def _session(stamp: str) -> SessionItem:
    return SessionItem(
        agent="opencode",
        id="ses_freshness1",
        title="t",
        directory="/x",
        created_at=stamp,
        updated_at=stamp,
        message_count=1,
        model="",
        raw_path="/x.json",
    )


def _run_freshness(db_path: Path, sessions: list) -> tuple[int, str]:
    old_path = mi.DB_PATH
    old_gas = mi.get_all_sessions
    mi.DB_PATH = db_path
    mi.get_all_sessions = lambda *a, **k: sessions
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = freshness()
    finally:
        mi.DB_PATH = old_path
        mi.get_all_sessions = old_gas
    return rc, buf.getvalue()


with tempfile.TemporaryDirectory() as td:
    td_path = Path(td)
    missing = td_path / "no.db"
    rc_ok, out_ok = _run_freshness(missing, [])
    check(
        "freshness: no index and no stores → OK",
        rc_ok == 0 and out_ok.startswith("OK"),
        f"rc={rc_ok} out={out_ok!r}",
    )
    rc_stale, out_stale = _run_freshness(missing, [_session("2026-10-01 00:00:00")])
    check(
        "freshness: no index but stores exist → STALE rc=1",
        rc_stale == 1 and "STALE" in out_stale,
        f"rc={rc_stale} out={out_stale!r}",
    )

    present = td_path / "memory.db"
    seeded = sqlite3.connect(present)
    seeded.executescript(DDL)
    seeded.execute(
        "INSERT INTO sessions_meta VALUES (?,?,?,?,?,?)",
        ("ses_freshness1", "opencode", "t", "2026-10-01 00:00:00", "/x", "now"),
    )
    seeded.commit()
    seeded.close()
    rc_unv, out_unv = _run_freshness(present, [])
    check(
        "freshness: index exists, stores unreadable → UNVERIFIED rc=1",
        rc_unv == 1 and out_unv.startswith("UNVERIFIED"),
        f"rc={rc_unv} out={out_unv!r}",
    )

# -----------------------------------------------------------------------
# 12. Usage telemetry: query/get append to queries.jsonl; stats --usage
# -----------------------------------------------------------------------
# False success (2026-10-05, session-memory review loop): "Level 1
# telemetry implemented" was reported while memory_index.py held no
# trace of it, and the next session ground ~17 re-reads of one file
# reconciling the report with the worktree. These checks pin the real
# thing: the log exists, query/get write it, misses are logged, and
# stats --usage reads it back.


def _seed_telemetry(directory: Path, events: list[dict]) -> Path:
    path = directory / "queries.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for event in events:
            fh.write(json.dumps(event) + "\n")
    return path


old_tp = mi.TELEMETRY_PATH
old_open_db = mi.open_db
old_argv = sys.argv
with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    mi.TELEMETRY_PATH = tmp / "queries.jsonl"

    # 12.1 append semantics: one JSON line per event, earlier lines survive.
    log_usage({"cmd": "query", "query": "git whitespace", "hits": 1})
    log_usage({"cmd": "get", "chunk_id": "opencode::ses_ab::0", "found": False})
    lines = [l for l in (tmp / "queries.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    check(
        "telemetry: query and get each append one JSON line",
        len(lines) == 2
        and json.loads(lines[0])["cmd"] == "query"
        and json.loads(lines[0]).get("ts"),
        f"got {lines!r}",
    )

    # 12.2 a failed append warns on stderr and never raises —
    # telemetry must not break the very query it records.
    mi.TELEMETRY_PATH = tmp  # a directory, not a file
    err_buf = io.StringIO()
    raised = False
    try:
        with contextlib.redirect_stderr(err_buf):
            log_usage({"cmd": "query", "query": "x", "hits": 0})
    except OSError:
        raised = True
    check(
        "telemetry: failed append warns, does not raise",
        not raised and "usage telemetry" in err_buf.getvalue(),
        f"raised={raised} stderr={err_buf.getvalue()!r}",
    )

    # 12.3 stats --usage on a missing file says so, with no crash.
    mi.TELEMETRY_PATH = tmp / "absent.jsonl"
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        print_usage()
    check(
        "usage: missing file → 'no events yet'",
        "no events yet" in out.getvalue(),
        f"got {out.getvalue()!r}",
    )

    # 12.4 seeded events: counts, zero-hit rate, window, top terms.
    mi.TELEMETRY_PATH = _seed_telemetry(
        tmp,
        [
            {"ts": "2026-10-05T09:00:00", "cmd": "query", "query": "git diff", "hits": 3},
            {"ts": "2026-10-05T10:00:00", "cmd": "query", "query": "gate exit 1", "hits": 0},
            {"ts": "2026-10-05T11:00:00", "cmd": "get", "chunk_id": "opencode::ses_ab::0", "found": True},
        ],
    )
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        print_usage()
    usage_out = out.getvalue()
    check(
        "usage: event counts split by command",
        "query 2" in usage_out and "get 1" in usage_out,
        f"got {usage_out!r}",
    )
    check(
        "usage: zero-hit queries counted",
        "1/2" in usage_out,
        f"got {usage_out!r}",
    )
    check(
        "usage: top terms from query text",
        "git" in usage_out and "diff" in usage_out,
        f"got {usage_out!r}",
    )

    # 12.5 end to end through the CLI: query logs its hits, a get miss
    # still exits 1 but is logged, and stats --usage renders the log.
    def _seeded_open_db() -> sqlite3.Connection:
        c = _fts_con()
        _put(c, "opencode::ses_telemxx::0", "git diff whitespace check", "ses_telemxx")
        return c

    mi.open_db = _seeded_open_db
    e2e_log = _seed_telemetry(tmp, [])
    mi.TELEMETRY_PATH = e2e_log

    sys.argv = ["memory_index.py", "query", "git", "whitespace"]
    with contextlib.redirect_stdout(io.StringIO()):
        mi.main()
    logged = [json.loads(l) for l in e2e_log.read_text(encoding="utf-8").splitlines() if l.strip()]
    check(
        "CLI query: appends a telemetry line with the hit count",
        bool(logged) and logged[-1]["cmd"] == "query" and logged[-1]["hits"] == 1,
        f"got {logged!r}",
    )

    sys.argv = ["memory_index.py", "get", "opencode::ses_missing2::0"]
    get2_rc = 0
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            get2_rc = mi.main()
        except SystemExit as exc:
            get2_rc = exc.code if isinstance(exc.code, int) else 1
    logged = [json.loads(l) for l in e2e_log.read_text(encoding="utf-8").splitlines() if l.strip()]
    check(
        "CLI get miss: still exits 1 AND logs found=false",
        get2_rc == 1 and logged[-1]["cmd"] == "get" and logged[-1]["found"] is False,
        f"rc={get2_rc} got {logged!r}",
    )

    sys.argv = ["memory_index.py", "stats", "--usage"]
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        mi.main()
    check(
        "CLI stats --usage: renders the usage section",
        "Events" in out.getvalue() and "query 1" in out.getvalue(),
        f"got {out.getvalue()!r}",
    )

mi.TELEMETRY_PATH = old_tp
mi.open_db = old_open_db
sys.argv = old_argv

# -----------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------

total = 33  # manually counted checks above
passed = total - len(failures)
print(f"\n{'=' * 60}")
print(f"test_memory_index.py: {passed}/{total} passed")
if failures:
    print(f"  {len(failures)} FAILURE(S):", file=sys.stderr)
    for f in failures:
        print(f"    {f}", file=sys.stderr)
    sys.exit(1)
else:
    print("  All checks passed.")
    sys.exit(0)
