#!/usr/bin/env python3
"""
ask.py — Unified project brain query tool.

Consolidates prior brains:
- ts_brain: SQLite RAG + graph.db
- reflection_brain: reflection JSON index + journals
- graph_brain: workspace graph queries
- skills_brain: skills index

Usage:
    python ask.py "<question>" [--limit N] [--raw]
    python ask.py list
    python ask.py show <stem-or-fragment> [P#]
    python ask.py --fingerprint
    python ask.py --check-stale
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAG_DB = ROOT / "rag.db"
GRAPH_DB = ROOT / "graph.db"
REFLECTION_INDEX = ROOT / "reflection_index.json"
SKILLS_INDEX = ROOT / "skills_index.json"
REFLECT_DIR = ROOT.parents[1] / "MONITORING" / "reflection"
HEAL = ("python brain/build_reflection_index.py && "
        "python brain/gen_digest.py")


def _rag_query(question: str, limit: int = 5) -> list[dict]:
    if not RAG_DB.exists():
        return []
    conn = sqlite3.connect(RAG_DB)
    conn.row_factory = sqlite3.Row
    words = [w.strip().lower() for w in question.split() if len(w.strip()) > 2]
    if not words:
        words = [question.strip().lower()]
    clause = " AND ".join(["(LOWER(title) LIKE ? OR LOWER(content) LIKE ?)"] * len(words))
    params: list[str] = []
    for w in words:
        params.extend([f"%{w}%", f"%{w}%"])
    sql = (
        "SELECT id, title, path, NULL AS source, "
        "CASE WHEN content LIKE ? THEN 2 ELSE 1 END AS rank, "
        "substr(content, 1, 400) AS snippet "
        "FROM chunks WHERE " + clause + " ORDER BY rank DESC, id LIMIT ?"
    )
    params_extended = [question] + params + [limit]
    rows = conn.execute(sql, params_extended).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _graph_query(question: str, limit: int = 5) -> list[dict]:
    if not GRAPH_DB.exists():
        return []
    conn = sqlite3.connect(GRAPH_DB)
    conn.row_factory = sqlite3.Row
    words = [w.lower() for w in question.replace("/", " ").split() if len(w) > 2]
    sql = "SELECT id, title, path, tags, body, NULL AS snip, 0 AS rank FROM nodes WHERE "
    params: list[str] = []
    if words:
        sql += " AND ".join(["body LIKE ?"] * len(words))
        params.extend([f"%{w}%" for w in words])
    else:
        sql = "SELECT id, title, path, tags, body, NULL AS snip, 0 AS rank FROM nodes"
    sql += " ORDER BY id LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _reflection_query(question: str, limit: int = 5) -> list[dict]:
    if not REFLECTION_INDEX.exists():
        return []
    data = json.loads(REFLECTION_INDEX.read_text(encoding="utf-8"))
    scored = []
    for key, entry in data.items():
        text = json.dumps(entry, ensure_ascii=False)
        score = 0
        for w in [w.strip().lower() for w in question.split() if len(w.strip()) > 2]:
            if w in text.lower():
                score += 1
        if score > 0:
            scored.append((score, key, entry))
    scored.sort(key=lambda x: (-x[0], x[1]))
    out = []
    for score, key, entry in scored[:limit]:
        out.append({
            "id": key,
            "title": entry.get("title", key),
            "source": "reflection",
            "rank": score,
            "snippet": str(entry)[:400],
        })
    return out


def _skills_query(question: str, limit: int = 5) -> list[dict]:
    if not SKILLS_INDEX.exists():
        return []
    data = json.loads(SKILLS_INDEX.read_text(encoding="utf-8"))
    scored = []
    for skill in data.get("skills", []):
        text = json.dumps(skill, ensure_ascii=False)
        score = 0
        for w in [w.strip().lower() for w in question.split() if len(w.strip()) > 2]:
            if w in text.lower():
                score += 1
        if score > 0:
            scored.append((score, skill.get("name"), skill))
    scored.sort(key=lambda x: (-x[0], x[1]))
    out = []
    for score, name, skill in scored[:limit]:
        out.append({
            "id": name,
            "title": name,
            "source": "skill",
            "rank": score,
            "snippet": str(skill)[:400],
        })
    return out


def query(question: str, limit: int = 5) -> list[dict]:
    combined = []
    for fn in (_rag_query, _graph_query, _reflection_query, _skills_query):
        try:
            combined.extend(fn(question, limit=limit))
        except Exception:
            continue
    combined.sort(key=lambda x: (-x.get("rank", 0), x.get("id", "")))
    return combined[:limit]


def list_scars() -> int:
    if not REFLECTION_INDEX.exists():
        print("reflection_index missing")
        return 1
    data = json.loads(REFLECTION_INDEX.read_text(encoding="utf-8"))
    for key in sorted(data):
        print(key)
    return 0


def show_scar(query: str) -> int:
    if not REFLECTION_INDEX.exists():
        print("reflection_index missing")
        return 1
    data = json.loads(REFLECTION_INDEX.read_text(encoding="utf-8"))
    keys = sorted(data)
    matches = [k for k in keys if query.lower() in k.lower()]
    if not matches:
        print(f"No scar matches: {query}")
        return 1
    for key in matches:
        print(f"## {key}")
        print(json.dumps(data[key], ensure_ascii=False, indent=2))
    return 0


def fingerprint() -> str:
    blob = b""
    for p in sorted(ROOT.glob("corpus/*.md")):
        blob += p.name.encode() + p.read_bytes()
    if RAG_DB.exists():
        blob += RAG_DB.read_bytes()
    if GRAPH_DB.exists():
        blob += GRAPH_DB.read_bytes()
    if REFLECTION_INDEX.exists():
        blob += REFLECTION_INDEX.read_bytes()
    return hashlib.sha256(blob).hexdigest()[:12]


def check_stale() -> int:
    print("check-stale: TODO")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Unified project brain query")
    ap.add_argument("question", nargs="?", default="")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--fingerprint", action="store_true")
    ap.add_argument("--check-stale", action="store_true")
    args = ap.parse_args()

    if args.fingerprint:
        print(fingerprint())
        return 0

    if args.check_stale:
        return check_stale()

    if args.question == "list":
        return list_scars()

    if args.question.startswith("show "):
        return show_scar(args.question[5:].strip())

    if not args.question:
        ap.print_help()
        return 1

    results = query(args.question, limit=args.limit)
    if args.raw:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    for i, r in enumerate(results, 1):
        source = r.get("source", "")
        title = r.get("title", r.get("id", ""))
        print(f"[{i}] {title} ({source})")
        snippet = r.get("snippet") or ""
        print(snippet[:400].replace("\n", " "))
        print("---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
