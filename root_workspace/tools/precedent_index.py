#!/usr/bin/env python3
"""precedent_index — maly indeks precedensow architektonicznych (ADR + scars).

Kontrakt wiersza (precedent.json) — jedyny format wymiany miedzy narzedziami:
  {"id","kind","title","quote","source_path","date"}
kind: adr | scar | pattern. Narzedzia-konsumenci czytaja ten JSON;
nie wiedza, ze ten plik istnieje.

Uzycie:
  python tools/precedent_index.py index
  python tools/precedent_index.py query --kind adr "session store"
  python tools/precedent_index.py query --json "gate"
  python tools/precedent_index.py show adr-0001
  python tools/precedent_index.py --selftest

Stdlib only. Read-only wobec archiwum ARL (najpierw _archive, potem research).
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABS = [ROOT / "projects" / "_archive" / "agentic-research-lab",
        ROOT / "projects" / "research" / "agentic-research-lab"]
OUT_DB = ROOT / "tools" / "out" / "precedents.db"
DATE_RE = re.compile(r"Date:\s*(\d{4}-\d{2}-\d{2})")


def find_lab() -> Path:
    for lab in LABS:
        if (lab / "docs" / "adr").is_dir():
            return lab
    sys.exit("precedent_index: no ARL adr dir in " + ", ".join(str(p) for p in LABS))


def parse_adr(path: Path, lab: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    title = next((ln.lstrip("# ").strip() for ln in text.splitlines()
                  if ln.startswith("#")), path.stem)
    body = [ln.strip() for ln in text.splitlines()
            if ln.strip() and not ln.startswith("#") and not ln.startswith("- ")]
    quote = (body[0] if body else title)[:280]
    m = DATE_RE.search(text)
    num = path.stem.split("-")[0]
    return {"id": f"adr-{num}", "kind": "adr", "title": title, "quote": quote,
            "source_path": path.relative_to(ROOT).as_posix(),
            "date": m.group(1) if m else ""}


def parse_scars() -> list[dict]:
    scars = ROOT / "SCARS.md"
    if not scars.is_file():
        return []
    out, n = [], 0
    for ln in scars.read_text(encoding="utf-8", errors="replace").splitlines():
        s = ln.strip()
        if s.startswith("- ") and len(s) > 10:
            n += 1
            out.append({"id": f"scar-{n:04d}", "kind": "scar",
                        "title": s[2:62].rstrip(), "quote": s[2:282],
                        "source_path": "SCARS.md", "date": ""})
    return out


def collect() -> list[dict]:
    lab = find_lab()
    rows = [parse_adr(p, lab) for p in sorted((lab / "docs" / "adr").glob("*.md"))]
    return rows + parse_scars()


def cmd_index(db: Path) -> int:
    rows = collect()
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db)
    con.execute("DROP TABLE IF EXISTS precedents")
    con.execute("CREATE TABLE precedents(id TEXT PRIMARY KEY, kind TEXT,"
                " title TEXT, quote TEXT, source_path TEXT, date TEXT)")
    con.executemany("INSERT INTO precedents VALUES"
                    "(:id,:kind,:title,:quote,:source_path,:date)", rows)
    con.commit()
    adrs = sum(1 for r in rows if r["kind"] == "adr")
    print(f"indexed {len(rows)} precedents ({adrs} adr) -> {db.relative_to(ROOT)}")
    con.close()
    return 0


def load(db: Path) -> list[dict]:
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM precedents")]
    con.close()
    return rows


def rank(rows: list[dict], text: str, kind: str) -> list[dict]:
    toks = [t.lower() for t in re.findall(r"[a-zA-Z0-9_]+", text) if len(t) > 2]
    scored = []
    for r in rows:
        if kind != "all" and r["kind"] != kind:
            continue
        hay = (r["title"] + " " + r["quote"]).lower()
        s = sum(hay.count(t) for t in toks)
        if s:
            scored.append((s, r))
    return [r for _, r in sorted(scored, key=lambda x: -x[0])]


def cmd_query(db: Path, text: str, kind: str, as_json: bool, top: int) -> int:
    if not db.is_file():
        sys.exit("precedent_index: no db — run `index` first")
    hits = rank(load(db), text, kind)[:top]
    if as_json:
        print(json.dumps(hits, ensure_ascii=False, indent=1))
    else:
        for h in hits:
            print(f"[{h['id']}] ({h['kind']}) {h['title']}\n  \"{h['quote']}\"\n  {h['source_path']}")
    return 0


def cmd_show(db: Path, pid: str) -> int:
    for r in load(db):
        if r["id"] == pid:
            print(json.dumps(r, ensure_ascii=False, indent=1))
            return 0
    sys.exit(f"precedent_index: unknown id {pid!r}")


def selftest() -> int:
    fails = []
    cmd_index(OUT_DB)
    rows = load(OUT_DB)
    adrs = [r for r in rows if r["kind"] == "adr"]
    if len(adrs) < 5:
        fails.append(f"want >=5 adr, got {len(adrs)}")
    for r in adrs:
        if not all(r[k] for k in ("id", "kind", "quote", "source_path")):
            fails.append(f"incomplete row {r['id']}")
    top3 = [h["id"] for h in rank(rows, "session store", "adr")[:3]]
    if "adr-0001" not in top3:
        fails.append(f"adr-0001 not in top3 for 'session store': {top3}")
    if not rank(rows, "whitespace", "scar"):
        fails.append("no scar hit for 'whitespace'")
    if fails:
        print("SELFTEST FAIL:\n- " + "\n- ".join(fails))
        return 1
    print(f"SELFTEST PASS: {len(adrs)} adr + {len(rows)-len(adrs)} scar, "
          f"fields ok, ranking ok, kind filter ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="precedent_index")
    ap.add_argument("--db", default=str(OUT_DB))
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("index")
    q = sub.add_parser("query")
    q.add_argument("text")
    q.add_argument("--kind", default="all", choices=["all", "adr", "scar", "pattern"])
    q.add_argument("--json", action="store_true")
    q.add_argument("--top", type=int, default=5)
    s = sub.add_parser("show")
    s.add_argument("id")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    db = Path(a.db)
    if a.cmd == "index":
        return cmd_index(db)
    if a.cmd == "query":
        return cmd_query(db, a.text, a.kind, a.json, a.top)
    if a.cmd == "show":
        return cmd_show(db, a.id)
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
