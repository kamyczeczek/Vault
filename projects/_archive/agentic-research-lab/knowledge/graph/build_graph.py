#!/usr/bin/env python3
"""Workspace-Research knowledge graph builder.

Scans knowledge/corpus/*.md, extracts front-matter chunks, indexes them into a
FTS5-backed SQLite graph, and writes a hash-gated digest. Faithful to the
proven ts-research pattern (corpus markdown is source of truth; brain is a
derived index), extended with full-text body search so the seed PDF/markdown
knowledge is actually retrievable by content, not just titles/tags.

Zero native deps (stdlib + sqlite3 FTS5, which ships with CPython).
Extended with SCARRED_FROM edges and hash-chain provenance from reflection system.
"""
import hashlib
import json
import math
import os
import re
import sqlite3
import time
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "knowledge" / "corpus"
DB = Path(__file__).with_name("graph.db")
DIGEST = Path(__file__).with_name("GRAPH-DIGEST.md")
INDEX = Path(__file__).with_name("graph_index.json")
GENERATION = Path(__file__).with_name("generation.json")

CHUNK_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)
H_RE = re.compile(r"^#{1,4}\s+(.+)$", re.MULTILINE)
TAG_RE = re.compile(r"#(\w[\w\-]*)")
REF_RE = re.compile(r"knowledge/corpus/\d+_\w+\.md")
JUNK_TAG_RE = re.compile(
    r"^\d+$"                       # bare integers
    r"|^(?=.*[0-9])(?=.*[A-Za-z])\w{3,}$"   # alphanumeric debris: x83db59, o377, bll001
    r"|^.{0,2}$"                   # one- and two-character noise ("b", "l", "x")
    r"|^C$"                        # preprocessor keyword
    ,
    re.IGNORECASE,
)


FTS_COLUMNS = ("id", "title", "body", "source_family")
"""FTS5 columns, in `snippet()`/`bm25()` index order.

Deliberately excludes `tags`. Indexing curation labels let a query match a label
the chunk never stated in prose: on this corpus `leak` appears in zero titles and
zero body tokens, yet `leakage` matched 7,824 rows via the `anti-leakage` tag,
and "how do agents avoid context leakage" returned 424 hits with tags against 0
without. Tag filtering belongs on the `node_tags` table, not in the text index.
"""


def _keep_tag(tag: str) -> bool:
    """Reject tags that cannot be a real topic label, by shape alone.

    Corpus frontmatter was auto-extracted from PDF text layers, so ~46% of
    chunks carry OCR debris. This layer catches the unambiguously malformed
    cases; letter-only book debris ("Msqrt", "SeismicEvents") is shaped like a
    word and is handled by `_drop_book_wide_tags` instead.
    """
    if not tag or JUNK_TAG_RE.match(tag):
        return False
    if not re.match(r"^[A-Za-z][A-Za-z0-9]*(-[A-Za-z0-9]+)*$", tag):
        return False
    return len(tag) > 2


def _registered_topics() -> set[str]:
    """Controlled vocabulary from knowledge/topics.md (unreserved section only)."""
    path = ROOT / "knowledge" / "topics.md"
    if not path.exists():
        return set()
    topics, reserved = set(), False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("## planned"):
            reserved = True
        if reserved or not stripped.startswith("- "):
            continue
        topics.add(stripped[2:].strip())
    return topics


def _drop_book_wide_tags(nodes: list[dict], min_sources: int = 3) -> dict:
    """Remove tags confined to one source, unless they are registered topics.

    Corpus frontmatter was extracted per-book, so one book's margin-note debris
    lands on every one of its chunks ("Msqrt" and "x83db59" on all 828 chunks of
    *Paradigms of AI Programming*; "SeismicEvents"/"LoginID" on all 1,123 chunks
    of *AIMA*). Such a tag cannot discriminate — filtering on it returns that one
    book, and its SHARES_TAG edges turn the book into a single clique.

    Source count alone is too blunt: `multi-agent` and `tool-use` are real
    registered topics that happen to live in one or two books, and dropping them
    silently unregistered 8 topics. Registered vocabulary is therefore exempt,
    and only unregistered single-source debris is removed.
    """
    registered = _registered_topics()
    sources_by_tag: dict[str, set] = {}
    for n in nodes:
        for t in set(n["tags"]):
            sources_by_tag.setdefault(t, set()).add(n.get("source") or n["id"])
    confined = {t for t, srcs in sources_by_tag.items()
                if len(srcs) < min_sources and t not in registered}
    if confined:
        for n in nodes:
            n["tags"] = [t for t in n["tags"] if t not in confined]
    return {"dropped_tag_types": len(confined),
            "exempt_registered": sorted(registered & set(sources_by_tag))[:12],
            "dropped_tag_types_sample": sorted(confined)[:10]}

# Reflection paths for provenance edges
REF_CANDIDATES = ROOT / "reflection" / "candidates"
REF_DIGESTS = ROOT / "reflection" / "digests"
REF_MEMORY = ROOT / "reflection" / "memory.md"

def fingerprint() -> str:
    h = hashlib.sha256()
    for p in sorted(CORPUS.glob("*.md")):
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def source_family(path: Path) -> str:
    """Collapse numbered chunks into a stable source identity."""
    return re.sub(r"^\d+_", "", path.stem)


def _frontmatter_list(value: str) -> list[str]:
    """Parse the deliberately small YAML subset used by corpus frontmatter."""
    value = (value or "").strip()
    if not value or value in ("[]", "null"):
        return []
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    return [item.strip().strip("\"'") for item in value.split(",") if item.strip()]


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
    tags = _frontmatter_list(meta.get("tags", ""))
    tags.extend(t for t in TAG_RE.findall(body) if t not in tags)
    tags = [t for t in tags if _keep_tag(t)]
    declared = meta.get("id", path.stem)
    if declared != path.stem:
        raise ValueError(f"{path.name}: front-matter id `{declared}` != filename stem `{path.stem}`")
    try:
        trust_tier = int(meta.get("trust_tier", "1"))
    except ValueError as exc:
        raise ValueError(f"{path.name}: trust_tier must be an integer from 0 to 3") from exc
    if trust_tier not in range(4):
        raise ValueError(f"{path.name}: trust_tier must be an integer from 0 to 3")
    semantic_edges = {}
    for kind in ("derives_from", "supports", "refutes", "contradicts", "extends"):
        targets = _frontmatter_list(meta.get(kind, ""))
        if targets:
            semantic_edges[kind.upper()] = targets
    return {
        "id": path.stem,
        "source_family": source_family(path),
        "title": meta.get("title", path.stem),
        "source": meta.get("source", ""),
        "trust_tier": trust_tier,
        "semantic_edges": semantic_edges,
        "tags": tags,
        "headings": headings,
        "path": str(path.relative_to(ROOT)),
        "body": body.strip(),
        "size": len(text),
        "node_type": "corpus",
    }


def _fill(conn, nodes, edges) -> None:
    """Insert every node + its FTS row + every edge into a fresh connection."""
    for n in nodes:
        conn.execute("INSERT INTO nodes VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                     (n["id"], n["title"], n["path"], json.dumps(n["tags"]),
                      json.dumps(n["headings"]), n["body"], n.get("node_type", "corpus"),
                      n["source_family"], n["source"], n["trust_tier"],
                      json.dumps(n["semantic_edges"])))
        conn.execute("INSERT INTO fts VALUES(?,?,?,?)",
                     (n["id"], n["title"], n["body"], n["source_family"]))
        conn.executemany("INSERT INTO node_tags(node_id, tag) VALUES(?, ?)",
                         ((n["id"], tag) for tag in sorted(set(n["tags"]))))
    for e in edges:
        conn.execute("INSERT INTO edges VALUES(?,?,?,?,?)",
                     (e["src"], e["dst"], e["kind"], e["conf"], e.get("tag")))


def _build_explicit_edges(nodes: list[dict]) -> list[dict]:
    """Materialize typed frontmatter references as graph edges."""
    ids = {n["id"] for n in nodes}
    edges = []
    for node in nodes:
        for kind, targets in node.get("semantic_edges", {}).items():
            for target in targets:
                if target in ids:
                    edges.append({"src": node["id"], "dst": target, "kind": kind, "conf": 1.0})
    return edges


def _atomic_replace(src: Path, dst: Path) -> bool:
    """os.replace is atomic on Windows and needs no delete permission on `dst`."""
    for _ in range(10):
        try:
            os.replace(src, dst)
            return True
        except PermissionError:
            time.sleep(0.5)
    return False


def _compute_tag_idf(nodes: list[dict]) -> dict[str, float]:
    """Compute normalized inverse document frequency for each tag, scaled to [0,1]."""
    doc_freq = Counter()
    total = len(nodes)
    for n in nodes:
        for t in set(n["tags"]):
            doc_freq[t] += 1
    max_idf = math.log(1 + total / (1 + 1))
    idf = {}
    for t, df in doc_freq.items():
        idf[t] = math.log(1 + total / (1 + df)) / max_idf
    return idf


def _build_provenance_edges(nodes: list[dict]) -> list[dict]:
    """Build DERIVED_FROM, PROMOTED_TO, and SCARRED_FROM edges from reflection system state."""
    edges = []
    id_set = {n["id"] for n in nodes}

    # DERIVED_FROM: candidates -> evidence chunks
    if REF_CANDIDATES.exists():
        for p in sorted(REF_CANDIDATES.glob("*.jsonl")):
            for line in p.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                cid = obj.get("id", "")
                if not cid:
                    continue
                evidence = obj.get("Evidence", obj.get("evidence", ""))
                if isinstance(evidence, str):
                    ids = re.findall(r"`([^`]+)`", evidence) or [evidence.strip()]
                elif isinstance(evidence, list):
                    ids = evidence
                else:
                    ids = []
                for ev in ids:
                    if isinstance(ev, str):
                        inner = re.findall(r"`([^`]+)`", ev) or [ev]
                        for eid in inner:
                            if eid in id_set:
                                edges.append({
                                    "src": cid,
                                    "dst": eid,
                                    "kind": "DERIVED_FROM",
                                    "conf": 1.0,
                                })

    # SCARRED_FROM: accepted reflection candidates -> evidence chunks
    if REF_CANDIDATES.exists():
        for p in sorted(REF_CANDIDATES.glob("*.jsonl")):
            for line in p.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("state") != "accepted":
                    continue
                cid = obj.get("id", p.stem)
                rule = obj.get("Rule", "")
                action = obj.get("Action", "")
                evidence_str = obj.get("Evidence", "")
                evidence_ids = re.findall(r"`([^`]+)`", evidence_str)
                if not evidence_ids:
                    continue

                # Classify strength for confidence weighting
                combined = (rule + " " + action).lower()
                hard_hits = sum(1 for pat in [r"\bblock\b", r"\bprevent\b", r"\bmust not\b",
                                               r"\bnever\b", r"\bgate\b", r"\bhardening\b",
                                               r"\bsandboxing\b", r"\binvariant\b", r"\bfail\s+loud\b"]
                                if re.search(pat, combined))
                conf = min(1.0, 0.5 + hard_hits * 0.1)
                type_label = "hard-gate" if hard_hits >= 2 else "soft-guidance"

                scar_id = f"scar:{cid}"
                for ev_id in evidence_ids:
                    if ev_id in id_set:
                        edges.append({
                            "src": scar_id,
                            "dst": ev_id,
                            "kind": "SCARRED_FROM",
                            "conf": conf,
                            "tag": type_label,
                        })

    # PROMOTED_TO: candidate IDs -> accepted rule identifiers in memory.md
    if REF_MEMORY.exists():
        mem_text = REF_MEMORY.read_text(encoding="utf-8")
        accepted_ids = re.findall(r"^###\s+(\S+)\s+—\s+accepted", mem_text, re.MULTILINE)
        for cid in accepted_ids:
            candidate_path = REF_CANDIDATES / f"{cid}.jsonl"
            if candidate_path.exists():
                edges.append({
                    "src": cid,
                    "dst": cid,
                    "kind": "PROMOTED_TO",
                    "conf": 1.0,
                })

    return edges


def _build_semantic_edges(nodes: list[dict]) -> list[dict]:
    """Build PART_OF and SEQUENCE edges from corpus structure."""
    edges = []
    by_id = {n["id"]: n for n in nodes}
    id_list = sorted(by_id.keys())

    seq_re = re.compile(r"^(\d+)_")
    series: dict[str, list[str]] = {}
    for nid in id_list:
        m = seq_re.match(nid)
        if m:
            series.setdefault(m.group(1), []).append(nid)
    for seq_ids in series.values():
        for i in range(len(seq_ids) - 1):
            edges.append({
                "src": seq_ids[i],
                "dst": seq_ids[i + 1],
                "kind": "SEQUENCE",
                "conf": 0.8,
            })

    heading_to_ids: dict[str, list[str]] = {}
    for n in nodes:
        for h in n["headings"]:
            heading_to_ids.setdefault(h.lower(), []).append(n["id"])

    seen = set()
    for n in nodes:
        body_lower = n["body"].lower()
        for h in n["headings"]:
            h_lower = h.lower()
            for other_id in heading_to_ids.get(h_lower, []):
                if other_id == n["id"]:
                    continue
                key = tuple(sorted([n["id"], other_id]))
                if key in seen:
                    continue
                seen.add(key)
                if len(n["title"]) < len(by_id[other_id]["title"]):
                    src, dst = n["id"], other_id
                else:
                    src, dst = other_id, n["id"]
                edges.append({
                    "src": src,
                    "dst": dst,
                    "kind": "PART_OF",
                    "conf": 0.6,
                })

    return edges


def _sync_reflection_routes(new_fp: str) -> None:
    """Automatically re-sync reflection routes and fingerprints when the graph is rebuilt."""
    try:
        import sys, json, re
        sys.path.insert(0, str(ROOT / "pipeline" / "06_reflect"))
        import route

        digests_dir = ROOT / "reflection" / "digests"
        candidates_dir = ROOT / "reflection" / "candidates"

        if not digests_dir.exists():
            return

        for md_path in digests_dir.glob("*.md"):
            text = md_path.read_text(encoding="utf-8")
            if "# Route metadata" not in text:
                continue
            lines = text.splitlines()
            tags, limit = [], 12
            in_meta = False
            for line in lines:
                if "# Route metadata" in line:
                    in_meta = True
                    continue
                if in_meta and line.startswith("#"):
                    break
                if in_meta:
                    if "tags:" in line:
                        raw_tags = line.split("tags:")[1].strip().strip("[]`")
                        tags = [t.strip("`' ") for t in raw_tags.split(",") if t.strip("`' ")]
                    elif "limit:" in line:
                        try:
                            limit = int(line.split("limit:")[1].strip("`' "))
                        except ValueError:
                            pass

            if tags:
                ids = route.query_ids(tags, limit)
                new_lines = []
                skip = False
                for line in lines:
                    if line.strip().startswith("returned_ids:"):
                        new_lines.append(line)
                        for i in ids:
                            new_lines.append(f"  - `{i}`")
                        skip = True
                        continue
                    if skip:
                        if line.strip().startswith("- `"):
                            continue
                        else:
                            skip = False
                    if not skip:
                        new_lines.append(line)
                text = "\n".join(new_lines) + "\n"

            text = re.sub(r'fingerprint: [a-f0-9]{12}', f'fingerprint: {new_fp}', text)
            md_path.write_text(text, encoding="utf-8")

            cand_path = candidates_dir / f"{md_path.stem}.jsonl"
            if cand_path.exists():
                clines = cand_path.read_text(encoding="utf-8").splitlines()
                c_new = []
                for line in clines:
                    if not line.strip():
                        continue
                    obj = json.loads(line)
                    if "provenance" in obj and isinstance(obj["provenance"], dict):
                        obj["provenance"]["fingerprint"] = new_fp
                        if "route" in obj["provenance"] and tags:
                            obj["provenance"]["route"]["returned_ids"] = ids
                    c_new.append(json.dumps(obj, ensure_ascii=False))
                cand_path.write_text("\n".join(c_new) + "\n", encoding="utf-8")
        print(f"[build] Automatically re-synced reflection routes and fingerprints to {new_fp}")
    except Exception as e:
        print(f"[build] Warning: reflection sync skipped ({e})")


def build() -> dict:
    nodes = []
    for p in sorted(CORPUS.glob("*.md")):
        nodes.append(parse_chunk(p))
    tag_filter_stats = _drop_book_wide_tags(nodes)

    edges = []
    by_path = {n["path"]: n["id"] for n in nodes}

    # REFERS_TO via explicit corpus path links
    for n in nodes:
        for rm in REF_RE.finditer(n["body"]):
            ref = rm.group(0)
            if ref in by_path:
                edges.append({"src": n["id"], "dst": by_path[ref], "kind": "REFERS_TO", "conf": 1.0})

    # SHARES_TAG edges with IDF-weighted confidence.
    tag_idf = _compute_tag_idf(nodes)
    total_nodes = len(nodes)
    tag_map: dict[str, list[str]] = {}
    for n in nodes:
        for t in n["tags"]:
            tag_map.setdefault(t, []).append(n["id"])
    seen: set[tuple[str, str]] = set()
    for t, ids in sorted(tag_map.items()):
        idf = tag_idf.get(t, 0.0)
        if len(ids) > total_nodes * 0.15 or idf < 0.3:
            continue
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                key = (ids[i], ids[j])
                if key in seen:
                    continue
                seen.add(key)
                edges.append({
                    "src": ids[i],
                    "dst": ids[j],
                    "kind": "SHARES_TAG",
                    "conf": round(idf, 3),
                    "tag": t,
                })

    # Explicit semantic edges declared in frontmatter.
    edges.extend(_build_explicit_edges(nodes))

    # Semantic edges (PART_OF, SEQUENCE)
    edges.extend(_build_semantic_edges(nodes))

    # Provenance edges (DERIVED_FROM, SCARRED_FROM, PROMOTED_TO)
    edges.extend(_build_provenance_edges(nodes))

    index = {
        "fingerprint": fingerprint(),
        "nodes": [{k: v for k, v in n.items() if k != "body"} for n in nodes],
        "edges": edges,
        "counts": {"nodes": len(nodes), "edges": len(edges)},
    }

    # Win32-safe cutover: rebuild into a temp DB, then atomically replace.
    tmp = DB.with_suffix(DB.suffix + ".new")
    if tmp.exists():
        tmp.unlink()
    conn = sqlite3.connect(tmp)
    conn.execute("CREATE TABLE nodes(id TEXT PRIMARY KEY, title TEXT, path TEXT, tags TEXT, headings TEXT, body TEXT, node_type TEXT, source_family TEXT, source TEXT, trust_tier INTEGER, semantic_edges TEXT)")
    conn.execute("CREATE TABLE edges(src TEXT, dst TEXT, kind TEXT, conf REAL, tag TEXT)")
    conn.execute("CREATE TABLE node_tags(node_id TEXT NOT NULL REFERENCES nodes(id), tag TEXT NOT NULL, PRIMARY KEY(node_id, tag))")
    conn.execute(f"CREATE VIRTUAL TABLE fts USING fts5({', '.join(FTS_COLUMNS)})")
    _fill(conn, nodes, edges)
    conn.execute("CREATE INDEX nodes_source_family ON nodes(source_family)")
    conn.execute("CREATE INDEX node_tags_tag_node ON node_tags(tag, node_id)")
    conn.execute("CREATE INDEX edges_src_conf ON edges(src, conf DESC, dst)")
    conn.execute("CREATE INDEX edges_dst_conf ON edges(dst, conf DESC, src)")
    conn.execute("CREATE INDEX edges_kind_conf ON edges(kind, conf DESC, src, dst)")
    conn.commit()
    conn.close()

    swapped = _atomic_replace(tmp, DB)
    if not swapped:
        tmp.unlink(missing_ok=True)
        conn = sqlite3.connect(DB)
        conn.execute("DELETE FROM nodes")
        conn.execute("DELETE FROM edges")
        conn.execute("DELETE FROM fts")
        conn.execute("DROP TABLE IF EXISTS node_tags")
        conn.execute("CREATE TABLE node_tags(node_id TEXT NOT NULL REFERENCES nodes(id), tag TEXT NOT NULL, PRIMARY KEY(node_id, tag))")
        _fill(conn, nodes, edges)
        conn.execute("CREATE INDEX IF NOT EXISTS nodes_source_family ON nodes(source_family)")
        conn.execute("CREATE INDEX IF NOT EXISTS node_tags_tag_node ON node_tags(tag, node_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS edges_src_conf ON edges(src, conf DESC, dst)")
        conn.execute("CREATE INDEX IF NOT EXISTS edges_dst_conf ON edges(dst, conf DESC, src)")
        conn.execute("CREATE INDEX IF NOT EXISTS edges_kind_conf ON edges(kind, conf DESC, src, dst)")
        conn.commit()
        conn.close()
        print("[build] live DB locked open — rebuilt in place")

    # digest
    lines = ["# Workspace-Research Knowledge Graph Digest", "",
             f"fingerprint: {index['fingerprint']}  nodes: {len(nodes)}  edges: {len(edges)}", "",
             "## Chunks (auto-injected into agents)", ""]
    for n in nodes:
        lines.append(f"- **{n['title']}** (`{n['id']}`) type={n['node_type']} tags={n['tags']}")
        if n["headings"]:
            lines.append(f"  - sections: {', '.join(n['headings'][:6])}")
    DIGEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    INDEX.write_text(json.dumps(index, indent=2), encoding="utf-8")
    generation = {
        "schema_version": 2,
        "generation_id": index["fingerprint"],
        "corpus_fingerprint": index["fingerprint"],
        "nodes": len(nodes),
        "edges": len(edges),
        "created_at": time.time(),
        "tag_filter": tag_filter_stats,
    }
    (Path(__file__).with_name(".graph_fingerprint")).write_text(index["fingerprint"], encoding="utf-8")
    GENERATION.write_text(json.dumps(generation, indent=2) + "\n", encoding="utf-8")
    # Reflections are derived artifacts. Do not rewrite them during graph build.
    # repair_graph_state.py is responsible for replay, quarantine, and regeneration.
    return index


def main() -> int:
    idx = build()
    kinds = Counter(e["kind"] for e in idx["edges"])
    print(f"built: fingerprint {idx['fingerprint']} nodes {idx['counts']['nodes']} edges {idx['counts']['edges']}")
    print(f"  kinds: {dict(kinds)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
