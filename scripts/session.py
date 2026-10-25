#!/usr/bin/env python3
"""Extract opencode session history to markdown.

Sessions live in SQLite, not markdown files:
  %USERPROFILE%/.local/share/opencode/opencode.db

Commands:
  list    [--limit N] [--dir PATH] [--since YYYY-MM-DD]
  dump    <id|prefix|title> [-o FILE] [--full] [--no-tools] [--no-reasoning] [--format md|json]
  latest  [--dir PATH] [-o FILE] [--full] [--no-tools] [--no-reasoning] [--format md|json]
  search  <text> [--limit N]

Default output: scripts/_scratch/sessions/<slug>-<date>.md (or .json with --format json)
"""
from __future__ import annotations
import argparse, json, sqlite3, sys
from datetime import datetime
from pathlib import Path

DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "scripts" / "_scratch" / "sessions"

def connect():
    if not DB.exists():
        sys.exit(f"opencode db not found: {DB}")
    c = sqlite3.connect(str(DB))
    c.row_factory = sqlite3.Row
    return c

def fmt_ts(ms):
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M")

def resolve(c, needle):
    r = c.execute("select id from session where id=?", (needle,)).fetchone()
    if r: return r["id"]
    rs = c.execute("select id,title from session where id like ? order by time_updated desc limit 5", (needle + "%",)).fetchall()
    if len(rs) == 1: return rs[0]["id"]
    if len(rs) > 1:
        for r in rs: print(f"  {r['id']}  {r['title']}", file=sys.stderr)
        sys.exit("ambiguous id prefix")
    rs = c.execute("select id,title from session where title like ? order by time_updated desc limit 5", (f"%{needle}%",)).fetchall()
    if len(rs) == 1: return rs[0]["id"]
    if len(rs) > 1:
        for r in rs: print(f"  {r['id']}  {r['title']}", file=sys.stderr)
        sys.exit("ambiguous title")
    sys.exit(f"no session matching {needle!r}")

def latest_id(c, directory):
    d = str(Path(directory).resolve()).replace("\\", "/")
    r = c.execute("select id from session where directory=? order by time_updated desc limit 1", (d,)).fetchone()
    if r: return r["id"]
    # the db keeps stale spellings of a worktree (renamed parent dir); fall back to
    # basename equality so `latest` keeps working instead of exiting "no session".
    base = d.rsplit("/", 1)[-1].lower()
    hits = [x for x in c.execute("select id,directory from session order by time_updated desc")
            if x["directory"].replace("\\", "/").rsplit("/", 1)[-1].lower() == base]
    if not hits: sys.exit(f"no session in {d}")
    print(f"  (no exact match; basename match: {hits[0]['directory']})", file=sys.stderr)
    return hits[0]["id"]

def slugify(title):
    # collapse runs of separators into a single "-", so "a  b - c" -> "a-b-c"
    out, prev = [], False
    for ch in title:
        if ch.isalnum():
            out.append(ch); prev = False
        elif ch in " -_":
            if not prev: out.append("-"); prev = True
    return "".join(out).strip("-")[:50] or "session"

def default_out(s, fmt="md"):
    date = datetime.fromtimestamp(s["time_created"] / 1000).strftime("%Y-%m-%d")
    return OUTDIR / f"{slugify(s['title'])}-{date}.{fmt}"

def dump_json(c, sid):
    """Full-fidelity JSON of one session: session row + messages + every part."""
    s = dict(c.execute("select * from session where id=?", (sid,)).fetchone())
    if s.get("model"):
        try: s["model"] = json.loads(s["model"])
        except (ValueError, TypeError): pass
    msgs = []
    for m in c.execute("select * from message where session_id=? order by time_created, id", (sid,)):
        m = dict(m)
        try: m["data"] = json.loads(m["data"]) if m["data"] else {}
        except (ValueError, TypeError): m["data"] = {}
        msgs.append(m)
    by_id = {m["id"]: m for m in msgs}
    for m in msgs: m["parts"] = []
    for p in c.execute("select * from part where session_id=? order by time_created, id", (sid,)):
        p = dict(p)
        try: p["data"] = json.loads(p["data"]) if p["data"] else {}
        except (ValueError, TypeError): p["data"] = {}
        if p["message_id"] in by_id: by_id[p["message_id"]]["parts"].append(p)
    return json.dumps({"session": s, "messages": msgs}, ensure_ascii=False, indent=2)

def render_session_md(c, sid, full=False, tools=True, reasoning=True):
    """Return the markdown text of one session (shared by dump + html)."""
    s = c.execute("select * from session where id=?", (sid,)).fetchone()
    msgs = c.execute("select id from message where session_id=? order by time_created, id", (sid,)).fetchall()
    lines = [
        f"# {s['title']}", "",
        f"- id: `{sid}`",
        f"- katalog: `{s['directory']}`",
        f"- model: `{s['model'] or '?'}`  agent: `{s['agent'] or '?'}`",
        f"- utworzona: {fmt_ts(s['time_created'])}  ·  ostatnia zmiana: {fmt_ts(s['time_updated'])}",
        f"- wiadomości: {len(msgs)}", "",
    ]
    cap = None if full else 800
    rcap = None if full else 2000
    for m in msgs:
        mrow = c.execute("select data from message where id=?", (m["id"],)).fetchone()
        try: mdata = json.loads(mrow["data"])
        except Exception: mdata = {}
        lines.append(f"## [{mdata.get('role','?')}]")
        for prow in c.execute("select data from part where message_id=? order by time_created, id", (m["id"],)).fetchall():
            try: p = json.loads(prow["data"])
            except Exception: continue
            t = p.get("type")
            if t == "text":
                lines.append(p.get("text", ""))
            elif t == "tool" and tools:
                st = p.get("state") or {}
                name = p.get("tool", "?")
                head = f"> **tool** `{name}` · {st.get('status','?')}"
                if st.get("title"): head += f" · {st['title']}"
                lines.append(head)
                inp = st.get("input") or p.get("input") or {}
                outp = st.get("output") or p.get("output") or ""
                if inp:
                    istr = json.dumps(inp, ensure_ascii=False)
                    lines.append(f"> in: `{istr[:cap] if cap else istr}`")
                if outp:
                    ostr = str(outp)
                    lines.append(f"> out: `{ostr[:cap] if cap else ostr}`")
            elif t == "reasoning" and reasoning:
                txt = p.get("text", "")
                if txt:
                    lines.append(f"<details><summary>reasoning</summary>\n\n{txt[:rcap] if rcap else txt}\n\n</details>")
            elif t == "step-finish" and full:
                tok = p.get("tokens") or {}
                lines.append(f"> _step-finish_ tokens={tok.get('total','?')} cost={p.get('cost')}")
        lines.append("")
    return "\n".join(lines)

def dump(c, sid, out, full=False, tools=True, reasoning=True):
    md = render_session_md(c, sid, full, tools, reasoning)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    n = c.execute("select count(*) from message where session_id=?", (sid,)).fetchone()[0]
    print(f"wrote {out}  ({n} msgs, {out.stat().st_size/1024:.1f} KB)")

BROWSE_CSS = (
    "body{font-family:Segoe UI,system-ui,sans-serif;margin:0;color:#1a1a1a;"
    "background:#fff;line-height:1.55}"
    ".top{padding:1em 1.5em;border-bottom:2px solid #333;display:flex;"
    "align-items:baseline;gap:1em}.top h1{margin:0;font-size:1.25em}"
    ".wrap{display:flex;min-height:calc(100vh - 4.5em)}"
    ".list{width:26em;min-width:20em;border-right:1px solid #ccc;"
    "overflow-y:auto;padding:.5em}"
    ".item{display:block;width:100%;text-align:left;background:none;border:none;"
    "border-bottom:1px solid #eee;padding:.6em;cursor:pointer;font:inherit}"
    ".item:hover{background:#f4f4f4}"
    ".item.active{background:#e8f0fe;border-left:3px solid #3478f6}"
    ".item .d{display:block;color:#666;font-size:.8em;overflow:hidden;"
    "text-overflow:ellipsis;white-space:nowrap}"
    ".view{flex:1;overflow:auto;padding:1em 1.5em}"
    ".meta{color:#666;font-size:.9em}"
    ".shead h2{margin:.2em 0 .4em;border-bottom:1px solid #ccc;padding-bottom:.3em}"
    "#copy{margin:.5em 0;background:#3478f6;color:#fff;border:none;"
    "padding:.5em 1em;border-radius:6px;cursor:pointer;font:inherit}"
    "#copy:hover{background:#2a63d0}"
    "pre.md{white-space:pre-wrap;word-break:break-word;background:#f4f4f4;"
    "padding:1em;border-radius:6px;font-size:.9em;line-height:1.5}"
    ".hidden{display:none}"
)

BROWSE_JS = (
    "(function(){var data=JSON.parse(document.getElementById('data').textContent);"
    "var list=document.getElementById('list'),view=document.getElementById('view');"
    "function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;}"
    "data.sessions.forEach(function(s,i){var b=document.createElement('button');"
    "b.className='item';b.innerHTML='<strong>'+esc(s.title||s.id)+'</strong>'"
    "'<span class=\"d\">'+esc(s.directory||'')+'</span>';b.onclick=function(){show(i);};list.appendChild(b);});"
    "function show(i){var s=data.sessions[i];"
    "document.querySelectorAll('.item').forEach(function(el,j){el.classList.toggle('active',i===j);});"
    "view.innerHTML='<div class=\"shead\"><h2>'+esc(s.title||s.id)+'</h2>'"
    "'<div class=\"meta\">'+esc(s.directory||'')+' · '+esc(s.created||'')+'</div></div>'"
    "'<button id=\"copy\">Kopiuj ca\\u0142a sesj\\u0119</button>'"
    "'<pre class=\"md\">'+esc(s.text||'')+'</pre>'"
    "'<div id=\"copied\" class=\"meta hidden\">skopiowano do schowka</div>';"
    "document.getElementById('copy').onclick=function(){var b=this;"
    "function done(){b.textContent='skopiowano \\u2713';setTimeout(function(){b.textContent='Kopiuj ca\\u0142a sesj\\u0119';},1500);}"
    "function fb(t){var a=document.createElement('textarea');a.value=t;a.style.position='fixed';a.style.opacity='0';"
    "document.body.appendChild(a);a.select();try{document.execCommand('copy');}catch(e){}document.body.removeChild(a);}"
    "if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(s.text).then(done,function(){fb(s.text);done();});}"
    "else{fb(s.text);done();};};"
    "if(data.sessions.length){show(0);}})();"
)

def session_html(c, sids, full=False, tools=True, reasoning=True,
                  title="opencode sessions"):
    """Build a self-contained, offline HTML session browser.

    Sessions are embedded as a JSON payload; the page lists them on the left
    and shows one on the right with a "copy whole session" button that writes
    the full markdown text to the clipboard. No server, no network.
    """
    sessions = []
    for sid in sids:
        s = c.execute("select * from session where id=?", (sid,)).fetchone()
        sessions.append({
            "id": sid,
            "title": s["title"],
            "directory": s["directory"],
            "created": fmt_ts(s["time_created"]),
            "model": s["model"],
            "text": render_session_md(c, sid, full, tools, reasoning),
        })
    payload = json.dumps({"title": title, "sessions": sessions},
                         ensure_ascii=False)
    # keep a literal "</script>" (from reasoning/details) from terminating
    # the DATA block; JSON.parse turns \/ back into /.
    payload = payload.replace("</", "<\\/")
    doc = (
        "<!doctype html>\n<html lang=\"pl\"><head><meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{html_escape(title)}</title>\n"
        f"<style>{BROWSE_CSS}</style></head>\n<body>\n"
        "<header class=\"top\"><h1>"
        f"{html_escape(title)}</h1>"
        f"<span class=\"meta\">{len(sessions)} sesji</span></header>\n"
        "<div class=\"wrap\"><nav id=\"list\" class=\"list\"></nav>"
        "<main id=\"view\" class=\"view\"></main></div>\n"
        f"<script id=\"data\" type=\"application/json\">{payload}</script>\n"
        f"<script>{BROWSE_JS}</script>\n</body></html>\n"
    )
    return doc

def html_escape(s):
    import html as _html
    return _html.escape(str(s))

def select_ids(c, directory=None, since=None, limit=20):
    """Return session ids, newest first, optionally scoped by dir/date."""
    q = "select id from session"
    w, params = [], []
    if directory:
        d = str(Path(directory).resolve()).replace("\\", "/")
        w.append("directory=?"); params.append(d)
    if since:
        w.append("time_updated>=?")
        params.append(int(datetime.fromisoformat(since).timestamp() * 1000))
    if w:
        q += " where " + " and ".join(w)
    q += " order by time_updated desc limit ?"
    params.append(limit)
    return [r["id"] for r in c.execute(q, params)]

def main():
    ap = argparse.ArgumentParser(prog="session.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list"); p.add_argument("--limit", type=int, default=20)
    p.add_argument("--dir"); p.add_argument("--since")

    for name in ("dump", "latest"):
        p = sub.add_parser(name)
        if name == "dump": p.add_argument("session")
        else: p.add_argument("--dir", default=".")
        p.add_argument("-o", "--out", type=Path)
        p.add_argument("--full", action="store_true")
        p.add_argument("--no-tools", action="store_true")
        p.add_argument("--no-reasoning", action="store_true")
        p.add_argument("--format", choices=("md", "json"), default="md")

    p = sub.add_parser("search"); p.add_argument("text"); p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("browse"); p.add_argument("--dir", default=".")
    p.add_argument("--since"); p.add_argument("--limit", type=int, default=50)
    p.add_argument("-o", "--out", type=Path)
    p.add_argument("--full", action="store_true")
    p.add_argument("--no-tools", action="store_true")
    p.add_argument("--no-reasoning", action="store_true")

    a = ap.parse_args()
    c = connect()

    if a.cmd == "list":
        q = "select id,title,directory,time_updated from session"
        w, params = [], []
        if a.dir:
            d = str(Path(a.dir).resolve()).replace("\\", "/")
            w.append("directory=?"); params.append(d)
        if a.since:
            w.append("time_updated>=?"); params.append(int(datetime.fromisoformat(a.since).timestamp()*1000))
        if w: q += " where " + " and ".join(w)
        q += " order by time_updated desc limit ?"; params.append(a.limit)
        for r in c.execute(q, params):
            print(f"{r['id']}  {fmt_ts(r['time_updated'])}  {r['title'][:70]}")
            print(f"    {r['directory']}")
    elif a.cmd in ("dump", "latest"):
        sid = resolve(c, a.session) if a.cmd == "dump" else latest_id(c, a.dir)
        s = c.execute("select * from session where id=?", (sid,)).fetchone()
        if a.format == "json":
            out = a.out or default_out(s, "json")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(dump_json(c, sid), encoding="utf-8")
            print(f"wrote {out}  ({out.stat().st_size/1024:.1f} KB)")
        else:
            dump(c, sid, a.out or default_out(s), a.full, not a.no_tools, not a.no_reasoning)
    elif a.cmd == "search":
        for r in c.execute("select id,title,directory,time_updated from session where title like ? order by time_updated desc limit ?", (f"%{a.text}%", a.limit)):
            print(f"{r['id']}  {fmt_ts(r['time_updated'])}  {r['title'][:70]}")
            print(f"    {r['directory']}")
    elif a.cmd == "browse":
        sids = select_ids(c, a.dir, a.since, a.limit)
        out = a.out or (OUTDIR / "browse.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(session_html(c, sids, a.full, not a.no_tools, not a.no_reasoning),
                       encoding="utf-8")
        print(f"wrote {out}  ({len(sids)} sesji, {out.stat().st_size/1024:.1f} KB)")

if __name__ == "__main__":
    main()
