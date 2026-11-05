#!/usr/bin/env python3
"""Workspace-Research knowledge graph builder.

Scans knowledge/corpus/*.md, extracts front-matter chunks, indexes them into a
FTS5-backed SQLite graph, and writes a hash-gated digest. Faithful to the
proven ts-research pattern (corpus markdown is source of truth; brain is a
derived index), extended with full-text body search so the seed PDF/markdown
knowledge is actually retrievable by content, not just titles/tags.

Zero native deps (stdlib + sqlite3 FTS5, which ships with CPython).
"""
import hashlib
import json
import os
import re
import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "knowledge" / "corpus"
DB = Path(__file__).with_name("graph.db")
DIGEST = Path(__file__).with_name("GRAPH-DIGEST.md")
INDEX = Path(__file__).with_name("graph_index.json")
STATE = Path(__file__).with_name(".graph_fingerprint")

CHUNK_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)
H_RE = re.compile(r"^#{1,4}\s+(.+)$", re.MULTILINE)
TAG_RE = re.compile(r"#(\w[\w\-]*)")
REF_RE = re.compile(r"knowledge/corpus/\d+_\w+\.md")
# A tag that cannot discriminate between chunks is not a tag: bare numbers are
# OCR/section-number residue from seed PDFs, and hex runs collide with the
# 12-hex fingerprint namespace. Excluded from edges only (kept on nodes so
# exact-tag routing and topics.md stay byte-stable).
JUNK_TAG_RE = re.compile(r"^\d+$|^[a-f0-9]{8,}$")

def fingerprint() -> str:
    h = hashlib.sha256()
    for p in sorted(CORPUS.glob("*.md")):
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def parse_chunk(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    meta, body = {}, text
    m = CHUNK_RE.match(text)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2)
    headings = [h.group(1).strip() for h in H_RE.finditer(body)]
    raw_tags = meta.get("tags", "")
    if raw_tags.startswith("[") and raw_tags.endswith("]"):
        raw_tags = raw_tags[1:-1]
    tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    # hashtag tags embedded in body (handy for seed chunks from raw notes)
    tags.extend(t for t in TAG_RE.findall(body) if t not in tags)
    # Identity invariant: the corpus `id` field MUST equal the filename stem.
    # ask.py returns ids and spawn_recursive resolves them back to files by stem;
    # a drift makes cited chunks unopenable and silently drops them from the
    # candidates' evidence. Fail here, at the build, not at the citation.
    declared = meta.get("id", path.stem)
    if declared != path.stem:
        raise ValueError(f"{path.name}: front-matter id `{declared}` != filename stem `{path.stem}` — rename the file or fix the id")
    return {
        "id": path.stem,
        "title": meta.get("title", path.stem),
        "tags": tags,
        "headings": headings,
        "path": str(path.relative_to(ROOT)),
        "body": body.strip(),
        "size": len(text),
    }



def _fill(conn, nodes, edges) -> None:
    """Insert every node + its FTS row + every edge into a fresh connection."""
    for n in nodes:
        conn.execute("INSERT INTO nodes VALUES(?,?,?,?,?,?)",
                     (n["id"], n["title"], n["path"], json.dumps(n["tags"]),
                      json.dumps(n["headings"]), n["body"]))
        conn.execute("INSERT INTO fts VALUES(?,?,?,?)",
                     (n["id"], n["title"], json.dumps(n["tags"]), n["body"]))
    for e in edges:
        conn.execute("INSERT INTO edges VALUES(?,?,?,?,?)",
                     (e["src"], e["dst"], e["kind"], e["conf"], e.get("tag")))


def _atomic_replace(src: Path, dst: Path) -> bool:
    """os.replace is atomic on Windows and needs no delete permission on `dst`.

    Returns False only when the destination is held open in a way that also blocks
    rename (kernel oplock / filter driver), so the caller can fall back to an
    in-place rebuild instead of failing the whole build.
    """
    for _ in range(10):
        try:
            os.replace(src, dst)
            return True
        except PermissionError:
            time.sleep(0.5)
    return False


def build() -> dict:
    nodes = []
    for p in sorted(CORPUS.glob("*.md")):
        nodes.append(parse_chunk(p))

    edges = []
    by_path = {n["path"]: n["id"] for n in nodes}
    id_by_id = {n["id"]: n for n in nodes}
    # REFERS_TO via explicit corpus path links
    for n in nodes:
        for rm in REF_RE.finditer(n["body"]):
            ref = rm.group(0)
            if ref in by_path:
                edges.append({"src": n["id"], "dst": by_path[ref], "kind": "REFERS_TO", "conf": 1.0})
    # SHARES_TAG edges. Two invariants, both for the one consumer of this table
    # (route.py / spawn_recursive.py one-hop expansion, which collapses to a set):
    #   1. junk tags are skipped — they matched ~everything, so 3 nodes carried
    #      4527 edges each and a 4-seed expansion returned 15,190 rows.
    #   2. one row per (src,dst) pair, carrying the alphabetically-first shared
    #      tag. Duplicate rows carried no extra information: 177,280 of 177,304
    #      pairs were multi-edges (max 59 repeats), i.e. 1.6M rows for 177k pairs.
    tag_map: dict[str, list[str]] = {}
    for n in nodes:
        for t in n["tags"]:
            if JUNK_TAG_RE.match(t):
                continue
            tag_map.setdefault(t, []).append(n["id"])
    seen: set[tuple[str, str]] = set()
    for t, ids in sorted(tag_map.items()):
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                key = (ids[i], ids[j])
                if key in seen:
                    continue
                seen.add(key)
                edges.append({"src": ids[i], "dst": ids[j], "kind": "SHARES_TAG", "conf": 0.5, "tag": t})

    index = {"fingerprint": fingerprint(), "nodes": [ {k: v for k, v in n.items() if k != "body"} for n in nodes ],
             "edges": edges, "counts": {"nodes": len(nodes), "edges": len(edges)}}

    # Win32-safe cutover: rebuild into a temp DB, then atomically replace the live one.
    # Deleting the live DB (the old `DB.unlink()`) fails with WinError 32 whenever any
    # reader has it open (a shell, an agent, or the Search indexer). os.replace is atomic
    # and needs no delete permission; only if it is denied do we fall back to an in-place
    # rebuild (same schema, rows overwritten in place — no delete needed at all).
    tmp = DB.with_suffix(DB.suffix + ".new")
    if tmp.exists():
        tmp.unlink()
    conn = sqlite3.connect(tmp)
    conn.execute("CREATE TABLE nodes(id TEXT PRIMARY KEY, title TEXT, path TEXT, tags TEXT, headings TEXT, body TEXT)")
    conn.execute("CREATE TABLE edges(src TEXT, dst TEXT, kind TEXT, conf REAL, tag TEXT)")
    conn.execute("CREATE VIRTUAL TABLE fts USING fts5(id, title, tags, body)")
    _fill(conn, nodes, edges)
    conn.commit()
    conn.close()

    swapped = _atomic_replace(tmp, DB)
    if not swapped:
        # Locked open (oplock / filter driver / stale agent). Overwrite rows in place instead.
        tmp.unlink(missing_ok=True)
        conn = sqlite3.connect(DB)
        conn.execute("DELETE FROM nodes")
        conn.execute("DELETE FROM edges")
        conn.execute("DELETE FROM fts")
        _fill(conn, nodes, edges)
        conn.commit()
        conn.close()
        print("[build] live DB locked open — rebuilt in place")

    # digest
    lines = ["# Workspace-Research Knowledge Graph Digest", "",
             f"fingerprint: {index['fingerprint']}  nodes: {len(nodes)}  edges: {len(edges)}", "",
             "## Chunks (auto-injected into agents)", ""]
    for n in nodes:
        lines.append(f"- **{n['title']}** (`{n['id']}`) tags={n['tags']}")
        if n["headings"]:
            lines.append(f"  - sections: {', '.join(n['headings'][:6])}")
    DIGEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    INDEX.write_text(json.dumps(index, indent=2), encoding="utf-8")
    STATE.write_text(index["fingerprint"])
    return index


def main() -> int:
    idx = build()
    print(f"built: fingerprint {idx['fingerprint']} nodes {idx['counts']['nodes']} edges {idx['counts']['edges']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
