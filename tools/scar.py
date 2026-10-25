#!/usr/bin/env python3
"""scar — append/query dla trybow porazek (failure modes). Najmniejsze narzedzie.

  python tools/scar.py add "cytat z metryki przechodzi, meritum nie" --tag metric
  python tools/scar.py query "metryka przechodzi"
  python tools/scar.py list
  python tools/scar.py --selftest

Plik: tools/out/scars.jsonl (jeden JSON na linie, append-only).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "tools" / "out" / "scars.jsonl"


def read_all() -> list[dict]:
    if not STORE.is_file():
        return []
    return [json.loads(ln) for ln in STORE.read_text(encoding="utf-8").splitlines() if ln.strip()]


def cmd_add(text: str, tags: list[str]) -> int:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    rows = read_all()
    row = {"id": f"scar-loc-{len(rows)+1:04d}", "text": text,
           "tags": tags, "date": date.today().isoformat()}
    with STORE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(row["id"])
    return 0


def score(row: dict, toks: list[str]) -> int:
    hay = (row["text"] + " " + " ".join(row["tags"])).lower()
    return sum(hay.count(t) for t in toks)


def cmd_query(text: str, as_json: bool, top: int) -> int:
    toks = [t.lower() for t in re.findall(r"[a-zA-Z0-9_]+", text) if len(t) > 2]
    hits = sorted(((score(r, toks), r) for r in read_all()),
                  key=lambda x: -x[0])
    hits = [r for s, r in hits if s][:top]
    if as_json:
        print(json.dumps(hits, ensure_ascii=False, indent=1))
    else:
        for h in hits:
            print(f"[{h['id']}] {h['text']}  ({','.join(h['tags'])})")
    return 0


def selftest() -> int:
    probe = "selftest-probe-blad-pomiaru"
    if not any(probe in r["text"] for r in read_all()):
        cmd_add(f"{probe}: metryka przechodzi, meritum nie", ["selftest"])
    hits = [r for r in read_all() if probe in r["text"]]
    if not hits:
        print("SELFTEST FAIL:\n- add+query round-trip broken")
        return 1
    toks = [t.lower() for t in re.findall(r"[a-zA-Z0-9_]+", probe) if len(t) > 2]
    ranked = sorted(read_all(), key=lambda r: -score(r, toks))
    if probe not in ranked[0]["text"]:
        print("SELFTEST FAIL:\n- probe not top-1")
        return 1
    print(f"SELFTEST PASS: round-trip ok ({hits[0]['id']}), query ranks probe top-1")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="scar")
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("add")
    a.add_argument("text")
    a.add_argument("--tag", action="append", default=[])
    q = sub.add_parser("query")
    q.add_argument("text")
    q.add_argument("--json", action="store_true")
    q.add_argument("--top", type=int, default=5)
    sub.add_parser("list")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.cmd == "add":
        return cmd_add(args.text, args.tag)
    if args.cmd == "query":
        return cmd_query(args.text, args.json, args.top)
    if args.cmd == "list":
        return cmd_query("a e i o", False, 100)
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
