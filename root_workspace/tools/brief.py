#!/usr/bin/env python3
"""brief — pytanie decyzyjne -> 4-sekcyjny brief-konteksowy (<=8K), zero rekomendacji.

Wejscie: pytanie + precedents.db (kontrakt precedent.json, nie ten modul).
Wyjscie: brief.md na stdout (lub --out). 4 sekcje, cytaty [id] "quote".
Celowo bez werdyktu: brief uzbraja decydenta, nie decyduje za niego.

  python tools/brief.py "Czy wyodrebnic nowy projekt?" --top 4
  python tools/brief.py "Czy ..." --out tools/out/brief.md
  python tools/brief.py --selftest
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "tools" / "out" / "precedents.db"
LIMIT = 8000
BANNED = ["powiniene", "powinien", "rozwa", "zalecan", "rekomend",
          "should", "consider", "recommend"]
SECTIONS = ["Pytanie", "Precedensy", "Paralele z precedensami", "Pytania otwarte"]


def load(db: Path) -> list[dict]:
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM precedents")]
    con.close()
    return rows


def rank(rows: list[dict], question: str, top: int) -> list[dict]:
    toks = [t.lower() for t in re.findall(r"[a-zA-Z0-9_]+", question) if len(t) > 2]
    scored = []
    for r in rows:
        hay = (r["title"] + " " + r["quote"]).lower()
        s = sum(hay.count(t) for t in toks)
        scored.append((s, len(r["quote"]), r))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [r for _, _, r in scored[:top]]


def render(question: str, hits: list[dict]) -> str:
    L = [f"## 1. {SECTIONS[0]}", "", question.strip(), "",
         f"## 2. {SECTIONS[1]}", ""]
    for h in hits:
        L += [f"[{h['id']}] ({h['kind']}) {h['title']}",
              f"\"{h['quote']}\" — {h['source_path']}", ""]
    L += [f"## 3. {SECTIONS[2]}", ""]
    for h in hits:
        L += [f"- Precedens [{h['id']}] opisuje: \"{h['quote'][:160]}\"",
              f"  Powiazanie z pytaniem wynika z tresci cytatu, nie z oceny.", ""]
    L += [f"## 4. {SECTIONS[3]}", "",
          "- Ktorego precedensu dotyczy najblizszy analogiczny przypadek?",
          "- Jakich danych brakuje, aby rozstrzygnac miedzy precedensami?",
          "- Co uniewazniloby przytoczone analogie?"]
    return "\n".join(L)[:LIMIT]


def selftest() -> int:
    fails = []
    if not DB.is_file():
        fails.append("no db — run precedent_index.py index first")
        print("SELFTEST FAIL:\n- " + "\n- ".join(fails))
        return 1
    brief = render("Czy korpus trzymac w repozytorium?", load(DB)[:5] and rank(load(DB), "korpus repozytorium", 4))
    if len(brief) > LIMIT:
        fails.append(f"brief {len(brief)} chars > {LIMIT}")
    heads = re.findall(r"^## \d\. ", brief, re.M)
    if len(heads) != 4:
        fails.append(f"want 4 sections, got {len(heads)}")
    low = brief.lower()
    hit = [b for b in BANNED if b in low]
    if hit:
        fails.append(f"banned stems in brief: {hit}")
    if "[adr-" not in brief and "[scar-" not in brief:
        fails.append("no [id] citations")
    if fails:
        print("SELFTEST FAIL:\n- " + "\n- ".join(fails))
        return 1
    print(f"SELFTEST PASS: {len(brief)} chars, 4 sections, citations ok, no banned stems")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="brief")
    ap.add_argument("question", nargs="*")
    ap.add_argument("--db", default=str(DB))
    ap.add_argument("--out")
    ap.add_argument("--top", type=int, default=4)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.question:
        ap.print_help()
        return 2
    brief = render(" ".join(a.question), rank(load(Path(a.db)), " ".join(a.question), a.top))
    if a.out:
        Path(a.out).write_text(brief, encoding="utf-8")
        print(f"wrote {a.out} ({len(brief)} chars)")
    else:
        print(brief)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
