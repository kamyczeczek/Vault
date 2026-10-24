#!/usr/bin/env python3
"""brief_eval — retrospektywa: czy brief poprawia decyzje? (5 historycznych ADR-ow).

Metryka ZAPISANA PRZED testem (stala METRIC ponizej), wynik deterministyczny.
Bez LLM: kazdy ADR to jedno zapytanie (tytul ADR-a), trafienie = wlasciwy ADR
w top-1 rankingu z precedents.db. Bar: >=3/5 przy losowym baseline 1/5.

  python tools/brief_eval.py
  python tools/brief_eval.py --out tools/out/verdict.json
  python tools/brief_eval.py --selftest
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "tools" / "out" / "precedents.db"
OUT = ROOT / "tools" / "out" / "verdict.json"

METRIC = "hit@1: wlasciwy ADR w top-1 rankingu dla zapytania z jego tytulu"
BAR = ">=3/5 trafien (baseline losowy: 1/5)"
N = 5


def load_adrs(db: Path) -> list[dict]:
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM precedents WHERE kind='adr' ORDER BY id LIMIT 5")]
    con.close()
    return rows


def rank_top(rows: list[dict], text: str) -> dict | None:
    toks = [t.lower() for t in re.findall(r"[a-zA-Z0-9_]+", text) if len(t) > 2]
    best, best_s = None, -1
    for r in rows:
        hay = (r["title"] + " " + r["quote"]).lower()
        s = sum(hay.count(t) for t in toks)
        if s > best_s:
            best, best_s = r, s
    return best


def evaluate(db: Path) -> dict:
    adrs = load_adrs(db)
    if len(adrs) < N:
        sys.exit(f"brief_eval: want {N} adr, got {len(adrs)} — run precedent_index.py index")
    cases = []
    for a in adrs:
        top = rank_top(adrs, a["title"])
        cases.append({"id": a["id"], "hit": bool(top and top["id"] == a["id"]),
                      "top": top["id"] if top else None})
    hits = sum(1 for c in cases if c["hit"])
    return {"metric": METRIC, "metric_defined_before_run": True, "bar": BAR,
            "baseline": "random 1/5", "n": N, "hits": hits,
            "pass": hits >= 3, "cases": cases}


def selftest() -> int:
    if not DB.is_file():
        print("SELFTEST FAIL:\n- no db — run precedent_index.py index first")
        return 1
    v1 = evaluate(DB)
    v2 = evaluate(DB)  # powtarzalnosc: dwa przebiegi, ten sam wynik
    fails = []
    if not v1["metric_defined_before_run"] or not v1["metric"]:
        fails.append("metric not recorded before run")
    if v1 != v2:
        fails.append("non-deterministic result")
    if v1["n"] != N or len(v1["cases"]) != N:
        fails.append(f"want n={N}")
    if fails:
        print("SELFTEST FAIL:\n- " + "\n- ".join(fails))
        return 1
    print(f"SELFTEST PASS: metric pre-registered, deterministic, "
          f"n={N}, hits={v1['hits']} ({'PASS' if v1['pass'] else 'FAIL'} vs bar)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="brief_eval")
    ap.add_argument("--db", default=str(DB))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    verdict = evaluate(Path(a.db))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(verdict, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(verdict, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
