#!/usr/bin/env python
"""Generate an EXACT (no truncation) transcript of the last N agent sessions.

Sources: opencode (sqlite) + omp (jsonl). No use of agent_sessions renderers (they truncate).
Output: one markdown file, streaming.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "scripts" / "_scratch" / "sessions" / "02_products"
OC_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
OMP_DIR = Path.home() / ".omp" / "agent" / "sessions"


def load_oc_sessions(limit):
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("agent_sessions", ROOT / "scripts" / "agent_sessions.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["agent_sessions"] = m
    spec.loader.exec_module(m)
    return m.load_opencode_sessions(limit)


def load_omp_sessions(limit):
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("agent_sessions", ROOT / "scripts" / "agent_sessions.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["agent_sessions"] = m
    spec.loader.exec_module(m)
    return m.load_omp_sessions(limit)


def render_oc(session, f):
    f.write(f"## Sesja oc — {session.title}\n")
    f.write(f"- agent/model: {session.agent}/{session.model}\n")
    f.write(f"- msgs: {session.message_count} · czas: {session.created_at} → {session.updated_at}\n")
    f.write(f"- id: {session.id}\n\n")
    if not OC_DB.is_file():
        f.write("*[brak opencode.db]*\n\n---\n\n")
        return
    conn = sqlite3.connect(str(OC_DB))
    conn.row_factory = sqlite3.Row
    # detect v2
    v2_rows = conn.execute(
        "select count(*) from session_message where session_id=?", (session.id,)
    ).fetchone()[0]
    if v2_rows:
        msgs = conn.execute(
            "select type, data from session_message where session_id=? order by seq, time_created, id",
            (session.id,),
        ).fetchall()
        for m in msgs:
            try:
                data = json.loads(m["data"]) if m["data"] else {}
            except Exception:
                data = {}
            if not isinstance(data, dict):
                data = {}
            role = m["type"] or "user"
            if role in ("system", "synthetic", "developer", "idle", "compaction"):
                # harness-ish: render as note
                txt = data.get("text")
                if txt:
                    f.write(f"### [harness:{role}]\n{txt}\n\n")
                continue
            f.write(f"### [{role}]\n")
            if role == "user":
                txt = data.get("text", "")
                if txt:
                    f.write(txt + "\n\n")
            else:
                for b in (data.get("content") or []):
                    t = b.get("type")
                    if t == "text":
                        f.write((b.get("text") or "") + "\n\n")
                    elif t == "reasoning":
                        txt = b.get("text", "")
                        if txt:
                            f.write(f"<details><summary>reasoning</summary>\n\n{txt}\n\n</details>\n\n")
                    elif t == "tool":
                        st = b.get("state") or {}
                        name = b.get("name") or b.get("tool") or "?"
                        status = st.get("status", "?")
                        f.write(f"#### [tool: {name} · {status}]\n")
                        inp = st.get("input")
                        if inp is not None:
                            f.write("args:\n```\n" + json.dumps(inp, ensure_ascii=False, indent=2) + "\n```\n")
                        outp = st.get("content") or st.get("output") or ""
                        if isinstance(outp, list):
                            outp = "\n".join(x.get("text", "") for x in outp if isinstance(x, dict))
                        if outp:
                            f.write("output:\n```\n" + str(outp) + "\n```\n")
                        f.write("\n")
            f.write("\n")
    else:
        msgs = conn.execute(
            "select id from message where session_id=? order by time_created, id", (session.id,)
        ).fetchall()
        for m in msgs:
            mrow = conn.execute("select data from message where id=?", (m["id"],)).fetchone()
            try:
                mdata = json.loads(mrow["data"]) if mrow and mrow["data"] else {}
            except Exception:
                mdata = {}
            role = mdata.get("role", "user")
            if role in ("system", "synthetic", "developer"):
                # render text if present
                for prow in conn.execute("select data from part where message_id=? order by time_created, id", (m["id"],)):
                    try:
                        p = json.loads(prow["data"])
                    except Exception:
                        continue
                    if p.get("type") == "text" and p.get("text"):
                        f.write(f"### [harness:{role}]\n{p.get('text')}\n\n")
                continue
            f.write(f"### [{role}]\n")
            for prow in conn.execute("select data from part where message_id=? order by time_created, id", (m["id"],)):
                try:
                    p = json.loads(prow["data"])
                except Exception:
                    continue
                t = p.get("type")
                if t == "text":
                    f.write((p.get("text") or "") + "\n")
                elif t == "reasoning":
                    txt = p.get("text", "")
                    if txt:
                        f.write(f"<details><summary>reasoning</summary>\n\n{txt}\n\n</details>\n")
                elif t == "tool":
                    st = p.get("state") or {}
                    name = p.get("tool", "?")
                    status = st.get("status", "?")
                    f.write(f"#### [tool: {name} · {status}]\n")
                    inp = st.get("input") or p.get("input") or {}
                    if inp:
                        f.write("args:\n```\n" + json.dumps(inp, ensure_ascii=False, indent=2) + "\n```\n")
                    outp = st.get("output") or p.get("output") or ""
                    if outp:
                        f.write("output:\n```\n" + str(outp) + "\n```\n")
            f.write("\n")
    conn.close()
    f.write("---\n\n")


def render_omp(path: Path, f):
    lines = path.read_text(encoding="utf-8").splitlines()
    # parse session header
    sid = path.stem
    title = ""
    model = ""
    cwd = ""
    for l in lines:
        try:
            o = json.loads(l)
        except Exception:
            continue
        if o.get("type") == "session":
            sid = o.get("id", sid)
            cwd = o.get("cwd", "")
        elif o.get("type") == "title":
            title = o.get("title", "") or title
        elif o.get("type") == "model_change":
            model = o.get("model", model)
    f.write(f"## Sesja omp — {title or sid}\n")
    f.write(f"- agent/model: omp/{model}\n")
    f.write(f"- cwd: {cwd}\n")
    f.write(f"- id: {sid}\n")
    f.write(f"- file: {path}\n\n")

    # index tool results by toolCallId
    tool_results = {}
    for l in lines:
        try:
            o = json.loads(l)
        except Exception:
            continue
        if o.get("type") == "message" and (o.get("message") or {}).get("role") == "toolResult":
            m = o["message"]
            tid = m.get("toolCallId")
            content = m.get("content")
            if isinstance(content, list):
                content = "\n".join(x.get("text", "") for x in content if isinstance(x, dict))
            tool_results[tid] = (m.get("toolName"), content, m.get("isError"))

    for l in lines:
        try:
            o = json.loads(l)
        except Exception:
            continue
        if o.get("type") != "message":
            continue
        m = o.get("message") or {}
        role = m.get("role")
        if role == "user":
            content = m.get("content")
            if isinstance(content, list):
                content = "\n".join(x.get("text", "") for x in content if isinstance(x, dict))
            f.write("### [user]\n" + str(content or "") + "\n\n")
        elif role == "assistant":
            for c in (m.get("content") or []):
                if c.get("type") == "text":
                    f.write("### [assistant]\n" + (c.get("text") or "") + "\n\n")
                elif c.get("type") in ("toolCall", "tool_call", "toolUse"):
                    name = c.get("name", "?")
                    args = c.get("arguments") or c.get("args") or {}
                    tid = c.get("id")
                    f.write(f"#### [tool: {name}]\n")
                    f.write("args:\n```\n" + json.dumps(args, ensure_ascii=False, indent=2) + "\n```\n")
                    tr = tool_results.get(tid)
                    if tr:
                        tname, content, iserr = tr
                        if iserr:
                            f.write(f"*[error]*\n")
                        if content is not None:
                            f.write("output:\n```\n" + str(content) + "\n```\n")
                    f.write("\n")
        elif role == "toolResult":
            pass  # already paired
    f.write("---\n\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("-o", "--out", type=Path, default=None)
    args = ap.parse_args()
    out = args.out or (OUTDIR / "last_sessions_exact.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("agent_sessions", ROOT / "scripts" / "agent_sessions.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["agent_sessions"] = m
    spec.loader.exec_module(m)

    oc = m.load_opencode_sessions(max(args.count, 10))
    omp_paths = sorted(OMP_DIR.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[: max(args.count, 10)]
    omp_sessions = []
    for p in omp_paths:
        # wrap as lightweight object
        class S:
            pass
        s = S()
        s.agent = "omp"
        s.title = p.stem
        s.model = ""
        s.message_count = 0
        s.created_at = ""
        s.updated_at = ""
        s.id = p.stem
        s._path = p
        omp_sessions.append(s)

    # sort combined by mtime proxy: opencode by updated_at desc already; omp by file mtime desc
    # We'll just render opencode first then omp, total N
    combined = []
    for s in oc[: args.count]:
        combined.append(("oc", s))
    remaining = args.count - len(combined)
    if remaining > 0:
        for s in omp_sessions[:remaining]:
            combined.append(("omp", s))

    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Exact sessions — last {len(combined)}\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for kind, s in combined:
            if kind == "oc":
                render_oc(s, f)
            else:
                render_omp(s._path, f)
    print(f"Wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
