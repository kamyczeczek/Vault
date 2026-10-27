#!/usr/bin/env python3
"""
ingest.py — Turn raw INBOX material into .brain/corpus/ chunks and update FTS5 graph DB.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "INBOX"
CORPUS = ROOT / ".brain" / "corpus"
RAW = INBOX / "raw"
GRAPH_DIR = ROOT / ".brain" / "graph"

CHUNK_CHARS = 3000
SLUG_RE = re.compile(r"[^a-z0-9]+")

DOMAIN_TAGS = {
    "context": ["context-engineering"],
    "agent": ["agents", "agentic"],
    "plan": ["planning"],
    "memory": ["memory"],
    "icm": ["icm"],
    "mutation": ["mutation"],
    "benchmark": ["benchmark"],
    "time_series": ["time-series"],
}

def is_pdf(path: Path) -> bool:
    if path.suffix.lower() == ".pdf":
        return True
    try:
        return path.read_bytes()[:5] == b"%PDF-"
    except Exception:
        return False

def slugify(s: str, maxlen: int = 48) -> str:
    s = s.lower()
    s = re.sub(r"\.pdf$|\.md$|\.txt$|\.epub$", "", s)
    s = SLUG_RE.sub("_", s).strip("_")
    return s[:maxlen].strip("_") or "doc"

def extract_text(path: Path) -> tuple[str, str]:
    name = path.name
    if is_pdf(path):
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            chunks = [pg.extract_text() or "" for pg in reader.pages]
            body = "\n\n".join(chunks).strip()
            first = next((l.strip() for l in body.splitlines() if l.strip()), name)
            return first[:120], body
        except Exception as e:
            return name, f"[pdf extraction failed: {e}]"
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".md":
        fm = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
        body = text[fm.end():] if fm else text
        m = re.search(r"^#{1,2}\s+(.+)$", body, re.MULTILINE)
        title = m.group(1).strip() if m else name
        return title, body
    first = next((l.strip() for l in text.splitlines() if l.strip()), name)
    return first[:120], text

def infer_tags(title: str, body: str) -> list[str]:
    text = (title + "\n" + body).lower()
    tags: set[str] = set()
    for kw, t in DOMAIN_TAGS.items():
        if kw in text:
            tags.update(t)
    for h in re.findall(r"#(\w[\w\-]*)", body):
        tags.add(h)
    return sorted(tags)

def split_sections(body: str, size: int = CHUNK_CHARS) -> list[str]:
    paras = re.split(r"\n\s*\n", body)
    sections: list[str] = []
    cur: list[str] = []
    n = 0
    for p in paras:
        p = p.strip()
        if not p:
            continue
        if n + len(p) > size and cur:
            sections.append("\n\n".join(cur))
            cur = []
            n = 0
        cur.append(p)
        n += len(p) + 2
    if cur:
        sections.append("\n\n".join(cur))
    return sections or [body]

def write_chunk(idx: int, total: int, source: str, title: str, tags: list[str], body: str) -> str:
    slug = slugify(source)
    seq = f"{idx:02d}" if total > 1 else "00"
    cid = f"{seq}_{slug}"
    title_disp = f"{title} (part {idx+1}/{total})" if total > 1 else title
    head = "---\n"
    head += f"id: {cid}\n"
    head += f'title: "{title_disp.replace(chr(34), chr(39))}"\n'
    head += f"source: \"{source}\"\n"
    head += f"tags: [{', '.join(tags)}]\n"
    head += "---\n\n"
    out = head + body.strip() + "\n"
    target = CORPUS / f"{cid}.md"
    CORPUS.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    return cid

def compute_corpus_fingerprint() -> str:
    """Compute SHA256 over all corpus chunks for state fingerprinting."""
    import hashlib
    h = hashlib.sha256()
    if CORPUS.exists():
        for p in sorted(CORPUS.glob("*.md")):
            h.update(p.name.encode("utf-8"))
            h.update(p.read_bytes())
    return h.hexdigest()

def rebuild_graph() -> int:
    db_path = GRAPH_DIR / "graph.db"
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.execute("CREATE VIRTUAL TABLE nodes USING fts5(id, title, content, tags, path)")

    count = 0
    for chunk_path in sorted(CORPUS.glob("*.md")):
        text = chunk_path.read_text(encoding="utf-8", errors="ignore")
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1]
            body = parts[2]
        else:
            fm = ""
            body = text

        title_match = re.search(r'title:\s*"(.*?)"', fm)
        title = title_match.group(1) if title_match else chunk_path.stem
        tags_match = re.search(r'tags:\s*\[(.*?)\]', fm)
        tags_str = tags_match.group(1) if tags_match else ""
        id_match = re.search(r'id:\s*(.*)', fm)
        cid = id_match.group(1).strip() if id_match else chunk_path.stem

        conn.execute(
            "INSERT INTO nodes(id, title, content, tags, path) VALUES (?, ?, ?, ?, ?)",
            (cid, title, body, tags_str, str(chunk_path))
        )
        count += 1
    conn.commit()
    conn.close()

    # Write fingerprint
    fp = compute_corpus_fingerprint()
    (GRAPH_DIR / ".graph_fingerprint").write_text(fp, encoding="utf-8")
    return count
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry", action="store_true", help="preview ingestion")
    ap.add_argument("--file", help="ingest single file from INBOX")
    args = ap.parse_args()

    if not INBOX.exists():
        INBOX.mkdir(parents=True, exist_ok=True)
        print(f"Created INBOX directory at {INBOX}")

    if args.file:
        cand = INBOX / args.file
        files = [cand if cand.is_file() else Path(args.file)]
    else:
        files = sorted(p for p in INBOX.iterdir() if p.is_file() and (is_pdf(p) or p.suffix.lower() in {".md", ".txt", ".epub"}))

    if not files:
        print(f"No valid files found in {INBOX}. Drop research papers or markdown notes into INBOX/ and re-run.")
        return 0

    RAW.mkdir(parents=True, exist_ok=True)

    total = 0
    for f in files:
        title, body = extract_text(f)
        sections = split_sections(body)
        tags = infer_tags(title, body)
        if not tags:
            tags = ["inbox", slugify(f.stem, 16)]

        written = []
        for i, sec in enumerate(sections):
            cid = write_chunk(i, len(sections), f.name, title, tags, sec)
            written.append(cid)
        total += len(written)
        print(f"[ingest] {f.name}: {len(written)} chunk(s) -> {', '.join(written)}")

        if not args.dry:
            shutil.move(str(f), str(RAW / f.name))

    if not args.dry and total > 0:
        num_nodes = rebuild_graph()
        print(f"SUCCESS: Rebuilt FTS5 knowledge graph at {GRAPH_DIR / 'graph.db'} with {num_nodes} total nodes.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
