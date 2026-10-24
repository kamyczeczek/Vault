#!/usr/bin/env python3
"""Regression tests for agent_sessions.py.

Guards the bug: `--days` filtered correctly, but forgot the `continue`
statement, so the filtered out sessions were still yielded.
(In the current implementation, this is handled by get_all_sessions filtering logic).
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# Mock loading to test get_all_sessions without real DBs
import agent_sessions
from agent_sessions import SessionItem, get_all_sessions

def test_filter_by_days():
    failures = []

    now = datetime.now()
    old = (now - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')
    recent = (now - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')

    s_old = SessionItem(agent="test", id="old", title="Old", directory="", created_at=old, updated_at=old, message_count=1, model="", raw_path="")
    s_recent = SessionItem(agent="test", id="new", title="New", directory="", created_at=recent, updated_at=recent, message_count=1, model="", raw_path="")

    # Mock loaders
    agent_sessions.load_opencode_sessions = lambda limit: [s_old, s_recent]
    agent_sessions.load_goose_sessions = lambda limit: []
    agent_sessions.load_hermes_sessions = lambda limit: []
    agent_sessions.load_pi_sessions = lambda limit: []
    agent_sessions.load_omp_sessions = lambda limit: []
    agent_sessions.load_jcode_sessions = lambda limit: []
    agent_sessions.load_antigravity_sessions = lambda limit: []

    # Test --days 5
    filtered = get_all_sessions(agent_filter="opencode", limit_per_agent=50, days=5)
    if len(filtered) != 1 or filtered[0].id != "new":
        failures.append(f"Expected 1 recent session, got {[s.id for s in filtered]}")

    # Test --days None (all)
    filtered_all = get_all_sessions(agent_filter="opencode", limit_per_agent=50, days=None)
    if len(filtered_all) != 2:
        failures.append(f"Expected 2 sessions with days=None, got {len(filtered_all)}")

    if failures:
        print("FAIL: test_agent_sessions.py", file=sys.stderr)
        for f in failures:
            print("  -", f, file=sys.stderr)
        sys.exit(1)
    else:
        print("test_agent_sessions.py: filter tests passed.")


def test_safe_name_and_collision_export():
    """`last --out-dir` must write one file per session, newest first, across
    agents, with a clean folder and Windows-legal filenames.

    The clean step is the part that cannot be seen in a passing export: without
    it a shrinking --count leaves stale files behind, so the folder stops being
    "the N newest" and becomes a growing union of every run.
    """
    import shutil
    import tempfile

    from agent_sessions import _safe_name, main

    failures = []
    tmp = Path(tempfile.mkdtemp())
    out_dir = tmp / "last_sessions"

    # Two sessions from different agents plus a deliberate title collision:
    # same agent, same title, different ids -> two distinct files, no loss.
    now = datetime.now()
    def ts(delta_min):
        return (now - timedelta(minutes=delta_min)).strftime("%Y-%m-%d %H:%M:%S")

    sessions = [
        SessionItem(agent="droid", id="aaaa1111", title="newest / illegal: name",
                    directory="", created_at=ts(0), updated_at=ts(0),
                    message_count=3, model="m", raw_path="r", text_markdown="BODY-A"),
        SessionItem(agent="opencode", id="bbbb2222", title="dup",
                    directory="", created_at=ts(5), updated_at=ts(5),
                    message_count=2, model="m", raw_path="r", text_markdown="BODY-B"),
        SessionItem(agent="opencode", id="cccc3333", title="dup",
                    directory="", created_at=ts(9), updated_at=ts(9),
                    message_count=1, model="m", raw_path="r", text_markdown="BODY-C"),
    ]

    # A stale file from a previous run: it must be gone after the export.
    out_dir.mkdir(parents=True)
    (out_dir / "STALE_from_previous_run.md").write_text("stale", encoding="utf-8")

    for loader in ("load_opencode_sessions", "load_goose_sessions", "load_hermes_sessions",
                   "load_pi_sessions", "load_omp_sessions", "load_jcode_sessions", "load_antigravity_sessions",
                   "load_cursor_sessions", "load_droid_sessions"):
        setattr(agent_sessions, loader, lambda limit: [])
    agent_sessions.load_opencode_sessions = lambda limit: [sessions[1], sessions[2]]
    agent_sessions.load_droid_sessions = lambda limit: [sessions[0]]

    argv = sys.argv
    sys.argv = ["agent_sessions.py", "last", "--agent", "all", "--count", "3",
                "--out-dir", str(out_dir)]
    try:
        main()
    except SystemExit as e:
        if e.code not in (0, None):
            failures.append(f"export exited {e.code}")
    finally:
        sys.argv = argv

    files = sorted(p.name for p in out_dir.iterdir())
    if len(files) != 3:
        failures.append(f"expected 3 files after clean, got {files}")
    if any("STALE" in f for f in files):
        failures.append(f"stale file survived the clean: {files}")

    # newest first: index 01 must be the droid session (0 min old), 03 the oldest
    for i, expect_agent in enumerate(["droid", "opencode", "opencode"], 1):
        hit = [p for p in out_dir.iterdir() if p.name.startswith(f"{i:02d}_")]
        if len(hit) != 1 or not hit[0].name.startswith(f"{i:02d}_{expect_agent}_"):
            failures.append(f"slot {i} should be {expect_agent}, got {[p.name for p in hit]}")

    # the colliding pair must both survive, and both bodies be present
    bodies = "".join(p.read_text(encoding="utf-8") for p in out_dir.iterdir())
    for marker in ("BODY-A", "BODY-B", "BODY-C"):
        if marker not in bodies:
            failures.append(f"{marker} missing from export (collision overwrote a file)")

    # illegal characters must not reach the filesystem
    for p in out_dir.iterdir():
        for bad in '<>:"/\\|?*':
            if bad in p.name:
                failures.append(f"illegal char {bad!r} in filename {p.name!r}")
                break

    if _safe_name(sessions[0]) != "newest___illegal__name":
        failures.append(f"_safe_name did not sanitise: {_safe_name(sessions[0])!r}")

    shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print("FAIL: test_agent_sessions.py", file=sys.stderr)
        for f in failures:
            print("  -", f, file=sys.stderr)
        sys.exit(1)
    else:
        print("test_agent_sessions.py: folder export tests passed.")


def test_empty_dir_locked_fallback():
    """`last --out-dir` must survive a locked folder (WinError 32).

    On Windows rmtree fails when Explorer/indexer holds the directory open.
    _empty_dir must then empty the contents in place instead of crashing.
    """
    import shutil
    import tempfile

    from agent_sessions import _empty_dir

    failures = []
    tmp = Path(tempfile.mkdtemp())
    target = tmp / "locked"
    target.mkdir()
    (target / "old1.md").write_text("stale", encoding="utf-8")
    (target / "sub").mkdir()
    (target / "sub" / "old2.md").write_text("stale", encoding="utf-8")

    real_rmtree = shutil.rmtree
    def locked_rmtree(path, *a, **k):
        if Path(path) == target:
            raise PermissionError(32, "being used by another process")
        return real_rmtree(path, *a, **k)
    shutil.rmtree = locked_rmtree
    try:
        _empty_dir(target)
    finally:
        shutil.rmtree = real_rmtree

    leftovers = list(target.iterdir())
    if leftovers:
        failures.append(f"locked dir not emptied in place: {[p.name for p in leftovers]}")

    shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print("FAIL: test_agent_sessions.py", file=sys.stderr)
        for f in failures:
            print("  -", f, file=sys.stderr)
        sys.exit(1)
    else:
        print("test_agent_sessions.py: locked-dir fallback tests passed.")


def test_no_clean_keeps_stale():
    """`--no-clean` must keep pre-existing files (the flag was silently ignored)."""
    import shutil
    import tempfile
    from datetime import datetime, timedelta

    from agent_sessions import SessionItem, main

    failures = []
    tmp = Path(tempfile.mkdtemp())
    out_dir = tmp / "keep"
    out_dir.mkdir()
    (out_dir / "STALE.md").write_text("stale", encoding="utf-8")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    s = SessionItem(agent="opencode", id="x" * 8, title="t", directory="",
                    created_at=now, updated_at=now, message_count=1,
                    model="", raw_path="r", text_markdown="BODY")

    for loader in ("load_opencode_sessions", "load_goose_sessions", "load_hermes_sessions",
                   "load_pi_sessions", "load_omp_sessions", "load_jcode_sessions",
                   "load_antigravity_sessions", "load_cursor_sessions",
                   "load_droid_sessions", "load_deepseek_sessions"):
        setattr(agent_sessions, loader, lambda limit: [])
    agent_sessions.load_opencode_sessions = lambda limit: [s]

    argv = sys.argv
    sys.argv = ["agent_sessions.py", "last", "--agent", "opencode", "--count", "1",
                "--out-dir", str(out_dir), "--no-clean"]
    try:
        main()
    except SystemExit as e:
        if e.code not in (0, None):
            failures.append(f"export exited {e.code}")
    finally:
        sys.argv = argv

    names = [p.name for p in out_dir.iterdir()]
    if "STALE.md" not in names:
        failures.append(f"--no-clean deleted the stale file: {names}")
    if len(names) != 2:
        failures.append(f"expected stale + 1 export, got {names}")

    shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print("FAIL: test_agent_sessions.py", file=sys.stderr)
        for f in failures:
            print("  -", f, file=sys.stderr)
        sys.exit(1)
    else:
        print("test_agent_sessions.py: no-clean tests passed.")


def test_header_normalisation_and_harness_filter():
    """One provenance header, no harness sections, optional reasoning strip."""
    import agent_sessions as a

    failures = []

    native = (
        "# [opencode] Test\n\n"
        "- **Agent**: `opencode`\n"
        "- **ID**: `ses_x`\n\n"
        "## [user]\nhello\n\n"
        "## [idle]\n\n"
        "## [model-switched]\n\n"
        "## [assistant]\n"
        '<details><summary>reasoning</summary>\n\nsecret\n\n</details>\nworld\n'
    )
    if a.strip_native_header(native).startswith("# ["):
        failures.append("strip_native_header left the native H1")

    s = SessionItem(agent="opencode", id="ses_x", title="Test", directory="",
                    created_at="2026-01-01", updated_at="2026-01-01",
                    message_count=3, model="m", raw_path="r", text_markdown=native)
    body = a.render_session_body(s)
    if "# [opencode]" in body:
        failures.append("render_session_body kept the native header")
    if "## [user]" not in body or "## [assistant]" not in body:
        failures.append("render_session_body dropped a conversational turn")
    if "## [idle]" in body or "## [model-switched]" in body:
        failures.append("render_session_body kept harness events")

    no_reasoning = a.render_session_body(s, include_reasoning=False)
    if "secret" in no_reasoning:
        failures.append("include_reasoning=False kept a reasoning block")
    if "world" not in no_reasoning:
        failures.append("include_reasoning=False dropped normal text")

    # A part cut mid-stream has an unclosed <details>; it must end at the next
    # heading, not swallow the rest of the transcript.
    unclosed = (
        "# [opencode] Y\n\n"
        "- **Agent**: `opencode`\n"
        "- **ID**: `ses_y`\n\n"
        "## [assistant]\n"
        "<details><summary>reasoning</summary>\nleaked trace\n\n"
        "## [tool]\nkept line\n")
    s_unclosed = SessionItem(agent="opencode", id="ses_y", title="Y", directory="",
                             created_at="2026-01-01", updated_at="2026-01-01",
                             message_count=2, model="m", raw_path="r",
                             text_markdown=unclosed)
    trimmed = a.render_session_body(s_unclosed, include_reasoning=False)
    if "leaked trace" in trimmed:
        failures.append("unclosed reasoning block leaked into the export")
    if "kept line" not in trimmed:
        failures.append("unclosed reasoning strip ate the next section")

    hdr = a._session_header(s, 1, 2, sha256="abc123")
    if "abc123" not in hdr:
        failures.append("_session_header ignored sha256")

    if failures:
        print("FAIL: test_agent_sessions.py", file=sys.stderr)
        for f in failures:
            print("  -", f, file=sys.stderr)
        sys.exit(1)
    print("test_agent_sessions.py: header normalisation tests passed.")


def test_opencode_v2_filters_harness_and_formats_model():
    """Harness rows must not appear as turns or inflate the message count."""
    import json
    import sqlite3

    import agent_sessions as a

    failures = []
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.execute("create table session_message "
              "(session_id text, seq int, time_created int, id text, type text, data text)")
    rows = [
        ("s", 1, 1, "m1", "user", json.dumps({"text": "hello"})),
        ("s", 2, 2, "m2", "idle", "{}"),
        ("s", 3, 3, "m3", "model-switched", "{}"),
        ("s", 4, 4, "m4", "assistant",
         json.dumps({"content": [{"type": "text", "text": "hi"}]})),
        ("s", 5, 5, "m5", "compaction", "{}"),
    ]
    c.executemany("insert into session_message values (?,?,?,?,?,?)", rows)
    lines, count = a._render_opencode_v2(c, "s")
    text = "\n".join(lines)

    if count != 2:
        failures.append(f"message count includes harness rows: {count}")
    if "## [idle]" in text or "## [model-switched]" in text or "## [compaction]" in text:
        failures.append("harness row rendered as a turn")
    if "## [user]" not in text or "## [assistant]" not in text:
        failures.append("conversational rows missing")
    if "Pominiete zdarzenia harnessu" not in text:
        failures.append("harness summary missing")

    if a._format_model('{"id":"gpt","providerID":"acme"}') != "acme/gpt":
        failures.append("_format_model did not flatten a dict")
    if a._format_model("plain-model") != "plain-model":
        failures.append("_format_model changed a plain string")

    if failures:
        print("FAIL: test_agent_sessions.py", file=sys.stderr)
        for f in failures:
            print("  -", f, file=sys.stderr)
        sys.exit(1)
    print("test_agent_sessions.py: opencode v2 rendering tests passed.")


def test_opencode_legacy_filters_harness_and_keeps_system_text():
    """Pre-2.0 renderer: harness rows are events, not turns; system text survives."""
    import json
    import sqlite3

    import agent_sessions as a

    failures = []
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.execute("create table message "
              "(session_id text, id text, time_created int, data text)")
    c.execute("create table part "
              "(message_id text, id text, time_created int, data text)")
    messages = [
        ("s", "m1", 1, json.dumps({"role": "user"})),
        ("s", "m2", 2, json.dumps({"role": "idle"})),
        ("s", "m3", 3, json.dumps({"role": "system"})),
        ("s", "m4", 4, json.dumps({"role": "assistant"})),
    ]
    c.executemany("insert into message values (?,?,?,?)", messages)
    parts = [
        ("m1", "p1", 1, json.dumps({"type": "text", "text": "hello"})),
        ("m2", "p2", 2, json.dumps({"type": "text", "text": "idle tick"})),
        ("m3", "p3", 3, json.dumps({"type": "text", "text": "tools reloaded"})),
        ("m4", "p4", 4, json.dumps({"type": "text", "text": "answer"})),
    ]
    c.executemany("insert into part values (?,?,?,?)", parts)

    lines, count = a._render_opencode_legacy(c, "s")
    text = "\n".join(lines)

    if count != 2:
        failures.append(f"legacy count includes harness rows: {count}")
    if "## [idle]" in text or "## [system]" in text:
        failures.append("legacy harness row rendered as a turn")
    if "## [user]" not in text or "## [assistant]" not in text:
        failures.append("legacy conversational rows missing")
    if "idle tick" in text:
        failures.append("legacy idle text leaked into the transcript")
    if "tools reloaded" not in text:
        failures.append("legacy system text was dropped instead of collapsed")
    if "<details><summary>Zdarzenia harnessu" not in text:
        failures.append("legacy harness summary missing")

    if failures:
        print("FAIL: test_agent_sessions.py", file=sys.stderr)
        for f in failures:
            print("  -", f, file=sys.stderr)
        sys.exit(1)
    print("test_agent_sessions.py: opencode legacy rendering tests passed.")


def test_reasoning_strip_handles_quoted_headings_and_nesting():
    """A quoted `## [x]` or a nested <details> must not cut reasoning short."""
    import agent_sessions as a

    failures = []

    quoted = (
        "## [assistant]\n"
        "<details><summary>reasoning</summary>\n\n"
        "Consider this dump:\n"
        "## [not-a-turn]\n"
        "still reasoning\n"
        "</details>\n"
        "visible answer\n"
    )
    out = a.strip_reasoning_blocks(quoted)
    if "## [not-a-turn]" in out:
        failures.append("quoted heading leaked out of a reasoning strip")
    if "still reasoning" in out:
        failures.append("reasoning was cut short at a quoted heading")
    if "visible answer" not in out:
        failures.append("text after the reasoning block was dropped")

    nested = (
        "## [assistant]\n"
        "<details><summary>reasoning</summary>\n"
        "outer trace\n"
        "<details><summary>inner</summary>\n"
        "inner trace\n"
        "</details>\n"
        "more outer trace\n"
        "</details>\n"
        "kept answer\n"
    )
    out = a.strip_reasoning_blocks(nested)
    if "outer trace" in out or "inner trace" in out or "more outer" in out:
        failures.append("nested reasoning leaked into the export")
    if "kept answer" not in out:
        failures.append("nested reasoning strip ate the following turn")

    # An unclosed reasoning block must end at a real `## [message]` boundary
    # (the default role several loaders use), or it eats the next turn.
    unclosed = (
        "## [assistant]\n"
        "<details><summary>reasoning</summary>\n"
        "leaked trace\n\n"
        "## [message]\nkept turn\n"
    )
    out = a.strip_reasoning_blocks(unclosed)
    if "leaked trace" in out:
        failures.append("unclosed reasoning leaked into the export")
    if "## [message]" not in out or "kept turn" not in out:
        failures.append("unclosed reasoning strip ate the `## [message]` turn")

    # The full pipeline (default: reasoning off) must not turn a quoted heading
    # inside reasoning into a rendered turn.
    native = ("# [opencode] Q\n\n- **Agent**: `opencode`\n- **ID**: `q`\n\n"
              + quoted)
    s = SessionItem(agent="opencode", id="q", title="Q", directory="",
                    created_at="2026-01-01", updated_at="2026-01-01",
                    message_count=1, model="m", raw_path="r", text_markdown=native)
    body = a.render_session_body(s, include_reasoning=False)
    if "## [not-a-turn]" in body:
        failures.append("render_session_body rendered a quoted heading as a turn")
    if "visible answer" not in body:
        failures.append("render_session_body dropped the answer")

    if failures:
        print("FAIL: test_agent_sessions.py", file=sys.stderr)
        for f in failures:
            print("  -", f, file=sys.stderr)
        sys.exit(1)
    print("test_agent_sessions.py: reasoning edge-case tests passed.")


if __name__ == "__main__":
    test_filter_by_days()
    test_safe_name_and_collision_export()
    test_empty_dir_locked_fallback()
    test_no_clean_keeps_stale()
    test_header_normalisation_and_harness_filter()
    test_opencode_v2_filters_harness_and_formats_model()
    test_opencode_legacy_filters_harness_and_keeps_system_text()
    test_reasoning_strip_handles_quoted_headings_and_nesting()
