#!/usr/bin/env python3
"""brain.py — the door to the curated brain layer: "what is the rule about X?"

Answers from `brain/brain.db`, the *curated reference* layer:

    problems   <- SCARS.md      "this broke, here is the rule that came out of it"
    decisions  <- DECISIONS.md  "we chose this, here is why"
    lessons    <- brain/lessons.md  "this pattern of failure, and its mechanical fix"

It does NOT answer "did I try this before, and how did it break?" — that question is
session memory, and it lives in a different store with a different door:
`python.exe scripts/memory_index.py query "<text>"` over `sessions`. The layers are
complementary, not substitutes: the brain holds ~one line per rule for the whole
workspace, session memory holds what an agent actually did and hit, per transcript.
Keeping them separate is deliberate; do not merge them.

The retrieval is `scripts/memory/retrieval_v1.py` unchanged — the validated lexical
config. Its docstring carries the measured numbers (family_recall@5, refusal, MRR).
No vectors, no reranker: on this corpus there is no measured insufficiency that
would justify them.

Usage:
    python.exe scripts/brain.py "<topic>" [--limit 5] [--all] [--json]

`--all` prints decision hits in full; the default truncates them. Scars and lessons
are always printed in full.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from memory import retrieval_v1  # noqa: E402

ROW_SQL = {
    "problems": ("SELECT title, root_cause, fix, scar, gate FROM problems WHERE id = ?",
                 ("title", "symptom", "rule", "scar", "gate")),
    "decisions": ("SELECT title, content FROM decisions WHERE id = ?", ("title", "body")),
    "lessons": ("SELECT content FROM lessons WHERE id = ?", ("lesson",)),
}


def load_row(con: sqlite3.Connection, table: str, row_id: int) -> dict[str, str]:
    sql, names = ROW_SQL[table]
    row = con.execute(sql, (row_id,)).fetchone()
    if not row:
        return {}
    return {n: " ".join((v or "").split()) for n, v in zip(names, row) if v}


def main() -> int:
    ap = argparse.ArgumentParser(prog="brain", add_help=True)
    ap.add_argument("query", nargs="*", help='the topic, e.g. "kasowanie katalogów w root"')
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--all", action="store_true", help="print full rule text for every hit")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.query:
        print(__doc__.strip().splitlines()[0])
        print('usage: python.exe scripts/brain.py "<topic>" [--limit 5] [--all] [--json]')
        return 2

    query = " ".join(args.query)
    result = retrieval_v1.search(query, limit=args.limit)
    con = retrieval_v1.connect()
    try:
        for hit in result["hits"]:
            hit["row"] = load_row(con, hit["table"], hit["id"])
    finally:
        con.close()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"query : {query}")
    print(f"tokens: {result['tokens']}")
    if not result["hits"]:
        print("hits  : []  -> no rule, scar or decision in the curated layer matches this topic.")
        print("        The layer holds ~one line per rule, so a miss is normal for anything")
        print("        the workspace has not written down. Try the session door next:")
        print('        python.exe scripts/memory_index.py query "<topic>"')
        return 0

    for i, hit in enumerate(result["hits"], 1):
        row = hit["row"]
        label = {"problems": "scar", "decisions": "decision", "lessons": "lesson"}[hit["table"]]
        print(f"\n{i}. {hit['table']}:{hit['id']}  [{label}]  rank={hit['rank']:.3f}")
        if hit["table"] == "problems":
            print(f"   {row.get('title', '')}")
            if row.get("symptom") and row["symptom"] != row.get("title"):
                print(f"   symptom: {row['symptom']}")
            if row.get("rule") and row["rule"] != row.get("title"):
                print(f"   rule   : {row['rule']}")
            elif not row.get("symptom") or row["symptom"] == row.get("title"):
                print("   (one-line scar: the title is the whole scar)")
            if row.get("gate"):
                print(f"   gate   : {row['gate']}")
        elif hit["table"] == "decisions":
            print(f"   {row.get('title', '')}")
            body = row.get("body", "")
            print(f"   {body if args.all else body[:400] + ('…' if len(body) > 400 else '')}")
        else:
            print(f"   {row.get('lesson', '')}")

    print("\nsource: brain/brain.db (curated layer — SCARS.md / DECISIONS.md / brain/lessons.md)")
    print("for 'did I try this, and how did it break?' use the session door: "
          "python.exe scripts/memory_index.py query \"<topic>\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
