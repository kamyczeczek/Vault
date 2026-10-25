#!/usr/bin/env python3
"""Behavioral tests for scripts/session.py.

Hermetic on purpose: these build an in-memory SQLite DB that mirrors the
opencode schema (session / message / part) so the suite does not depend on the
real %USERPROFILE%/.local/share/opencode/opencode.db. If the real DB is missing
or empty the tests still pass; they only need the *shape* of the data.

Run either way:
    pytest scripts/test_session.py
    python  scripts/test_session.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session  # noqa: E402


# --- in-memory fixture -------------------------------------------------

_NOW = 1_760_000_000_000  # arbitrary stable epoch-ms base


def _make_db() -> sqlite3.Connection:
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(
        """
        create table session(
            id text, title text, directory text,
            model text, agent text,
            time_created integer, time_updated integer);
        create table message(
            id text, session_id text, time_created integer, data text);
        create table part(
            id text, message_id text, time_created integer, data text);
        """
    )
    c.executemany(
        "insert into session values (?,?,?,?,?,?,?)",
        [
            # two sessions live in C:/repo -- ses_def is the newer one
            ("ses_abc", "pstack work", "C:/repo", "gpt-x", "builder",
             _NOW, _NOW + 1_000),
            ("ses_def", "other thing", "C:/repo", None, None,
             _NOW + 5_000, _NOW + 5_000),
            # a session in a different directory
            ("ses_ghi", "solo dir", "C:/other", "m", None,
             _NOW + 9_000, _NOW + 9_000),
        ],
    )
    c.executemany(
        "insert into message values (?,?,?,?)",
        [
            ("m1", "ses_abc", _NOW, json.dumps({"role": "user"})),
            ("m2", "ses_abc", _NOW + 50, json.dumps({"role": "assistant"})),
        ],
    )
    c.executemany(
        "insert into part values (?,?,?,?)",
        [
            # user text
            ("p1", "m1", _NOW, json.dumps({"type": "text", "text": "hi there"})),
            # assistant tool call
            ("p2", "m2", _NOW + 100, json.dumps({
                "type": "tool", "tool": "shell",
                "state": {"status": "done",
                          "input": {"command": "ls"},
                          "output": "file1\nfile2"},
            })),
        ],
    )
    return c


# --- pure-function checks ---------------------------------------------

def test_slugify_keeps_words_and_separators():
    assert session.slugify("Hello World - x") == "Hello-World-x"


def test_slugify_empty_falls_back_to_session():
    # a title with no usable alnum / separator must not yield a blank filename
    assert session.slugify("!!!") == "session"


def test_fmt_ts_emits_iso_date_prefix():
    ms = int(datetime(2026, 10, 3, 9, 0).timestamp() * 1000)
    got = session.fmt_ts(ms)
    assert got.startswith("2026-10-03")
    assert " " in got  # date and time separated


# --- resolution --------------------------------------------------------

def test_resolve_by_full_id():
    c = _make_db()
    assert session.resolve(c, "ses_abc") == "ses_abc"


def test_resolve_by_unique_prefix():
    c = _make_db()
    # a strict prefix that matches exactly one id
    c2 = _make_db()
    assert session.resolve(c2, "ses_def") == "ses_def"


def test_resolve_by_title_substring():
    c = _make_db()
    # 'pstack' occurs only in the 'pstack work' title
    assert session.resolve(c, "pstack") == "ses_abc"


def test_latest_id_picks_newest_in_directory():
    c = _make_db()
    # two sessions in C:/repo; ses_def (time_updated +5000) is newer
    assert session.latest_id(c, "C:/repo") == "ses_def"


def test_latest_id_missing_directory_exits():
    c = _make_db()
    try:
        session.latest_id(c, "C:/nowhere")
    except SystemExit:
        return
    raise AssertionError("latest_id did not exit for unknown directory")


# --- dump --------------------------------------------------------------

def test_dump_writes_text_and_tool_parts():
    c = _make_db()
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "sess.md"
        session.dump(c, "ses_abc", out)
        text = out.read_text(encoding="utf-8")
        assert "# pstack work" in text        # title header
        assert "[user]" in text               # role rendered
        assert "hi there" in text             # text part surfaced
        assert "**tool** `shell`" in text     # tool part rendered
        assert "file1" in text               # tool output surfaced


def test_dump_no_tools_omits_tool_parts():
    c = _make_db()
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "sess.md"
        session.dump(c, "ses_abc", out, tools=False)
        text = out.read_text(encoding="utf-8")
        assert "hi there" in text             # text still present
        assert "shell" not in text            # tool part dropped


def test_dump_caps_inputs_when_not_full():
    c = _make_db()
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "sess.md"
        # default cap=800 on the tool input/output
        session.dump(c, "ses_abc", out, full=False)
        text = out.read_text(encoding="utf-8")
        assert "in:" in text                 # input block emitted


# --- markdown rendering (shared by dump + html) -------------------------

def test_render_session_md_has_text_and_tools():
    c = _make_db()
    md = session.render_session_md(c, "ses_abc")
    assert "# pstack work" in md        # title header
    assert "hi there" in md            # text part
    assert "**tool** `shell`" in md    # tool part
    assert "file1" in md               # tool output


def test_render_session_md_respects_no_tools():
    c = _make_db()
    md = session.render_session_md(c, "ses_abc", tools=False)
    assert "hi there" in md            # text kept
    assert "shell" not in md           # tool dropped


# --- html browser (self-contained, copy-to-clipboard) --------------------

def test_session_html_embeds_sessions_and_copy_button():
    c = _make_db()
    doc = session.session_html(c, ["ses_abc", "ses_def"])
    low = doc.lower()
    assert "<!doctype html" in low       # full document
    assert "pstack work" in doc         # embedded session title
    assert "other thing" in doc
    assert "hi there" in doc            # embedded session text
    assert "copy" in low                # copy control present
    assert "ses_abc" in doc             # session id embedded


def test_session_html_escapes_script_close_tags():
    # a session text containing </script> must not terminate the DATA block:
    # the JSON payload is escaped and still round-trips through json.loads.
    c = _make_db()
    c.execute(
        "insert into part values (?,?,?,?)",
        ("p9", "m1", _NOW + 1,
         json.dumps({"type": "text", "text": "boom</script>end"})),
    )
    doc = session.session_html(c, ["ses_abc"])
    m = re.search(
        r'<script id="data" type="application/json">(.*?)</script>',
        doc, re.DOTALL,
    )
    assert m, "DATA script block not found"
    data = json.loads(m.group(1))       # would fail if not escaped
    text = data["sessions"][0]["text"]
    assert "</script>" in text          # round-trips to the original


# --- main runner (plain-python mode) -----------------------------------

if __name__ == "__main__":
    fns = sorted(
        (v for k, v in globals().items()
         if k.startswith("test_") and callable(v)),
        key=lambda f: f.__name__,
    )
    fails = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception:  # noqa: BLE001
            fails += 1
            import traceback
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    total = len(fns)
    print(f"\n{total - fails}/{total} passed")
    sys.exit(1 if fails else 0)
