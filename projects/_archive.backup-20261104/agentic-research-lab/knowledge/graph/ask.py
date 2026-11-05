#!/usr/bin/env python3
"""Query the Workspace-Research knowledge graph (graph.db, FTS5).

Usage: python knowledge/graph/ask.py "<question>" [--limit N] [--raw]
Returns ranked chunk ids with titles, paths, tags, and a matched snippet.
Extended with SCARRED_FROM neighbor filtering (hard-gate vs soft-guidance).
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = Path(__file__).with_name("graph.db")
ALIASES_PATH = Path(__file__).with_name("source_aliases.json")
QUARANTINE_PATH = Path(__file__).with_name("quarantine.json")


def quarantined_chunks() -> set[str]:
    """Chunk ids excluded from retrieval because extraction damaged their text.

    A quarantined chunk lost intra-word whitespace, so FTS5 cannot match terms
    inside the damaged run: it cannot be found by the words it is meant to
    contain. Excluding it is better than letting unsearchable text compete with
    searchable text, and the exclusion is per chunk because damage is
    concentrated in a few passages rather than spread across a source — a
    source-level cut discarded 417 clean chunks to hide 419 damaged ones.

    The corpus is never modified, so a re-ingested clean chunk is re-admitted
    automatically once `scripts/build_quarantine.py` is re-run.
    """
    if not QUARANTINE_PATH.exists():
        return set()
    try:
        payload = json.loads(QUARANTINE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    return set(payload.get("chunk_ids", {}))


def _evidence_spans(body: str, words: list[str], *, limit: int = 2,
                    max_chars: int = 1400) -> list[dict]:
    """Return small deterministic section/paragraph spans from a corpus body."""
    if not body or not words or limit < 1 or max_chars < 80:
        return []
    lines = body.splitlines()
    sections: list[tuple[str, list[str]]] = []
    heading = ""
    paragraph: list[str] = []

    def flush() -> None:
        nonlocal paragraph
        text = " ".join(line.strip() for line in paragraph if line.strip()).strip()
        if text:
            sections.append((heading, [text]))
        paragraph = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            flush()
            heading = stripped.lstrip("#").strip()
        elif stripped:
            paragraph.append(stripped)
        else:
            flush()
    flush()

    lowered = [w.lower() for w in words if len(w) > 2]
    ranked: list[tuple[int, int, str, str]] = []
    for ordinal, (section, texts) in enumerate(sections):
        text = texts[0]
        haystack = f"{section} {text}".lower()
        score = sum(haystack.count(word) for word in lowered)
        if score:
            ranked.append((score, -ordinal, section, text))
    ranked.sort(reverse=True)
    result = []
    for score, neg_ordinal, section, text in ranked[:limit]:
        prefix = f"{section}: " if section else ""
        available = max_chars - len(prefix)
        clipped = text if len(text) <= available else text[:max(0, available - 1)].rstrip() + "..."
        result.append({"section": section, "text": prefix + clipped, "score": score,
                       "ordinal": -neg_ordinal})
    return result


def evidence_spans(node_id: str, question: str, *, limit: int = 2,
                   max_chars: int = 1400) -> list[dict]:
    """Fetch bounded evidence spans for one node without exposing its full body."""
    if not DB.exists():
        return []
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT body FROM nodes WHERE id=?", (node_id,)).fetchone()
    conn.close()
    if not row:
        return []
    words = [word.lower() for word in re.findall(r"[A-Za-z0-9_]+", question)
             if len(word) > 2]
    return _evidence_spans(row["body"] or "", words, limit=limit, max_chars=max_chars)


def _alias_rows(conn, question, limit):
    try:
        aliases = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    q = question.lower()
    families = []
    for phrase, ids in aliases.items():
        if phrase.replace("-", " ") in q:
            families.extend(ids)
    families = list(dict.fromkeys(families))
    if not families:
        return []
    excluded = quarantined_chunks()
    clauses = " OR ".join("n.source_family LIKE ?" for _ in families)
    sql = (f"SELECT n.id,n.title,n.path,n.tags,n.body,n.source_family,NULL AS snip "
           f"FROM nodes n WHERE {clauses} ORDER BY n.id")
    try:
        rows = [_row_payload(r) for r in
                conn.execute(sql, tuple(x + "%" for x in families)).fetchall()]
    except sqlite3.OperationalError:
        return []
    if excluded:
        rows = [r for r in rows if r["id"] not in excluded]
    return rows[:limit]


def _row_payload(r, snippet="") -> dict:
    return {
        "id": r["id"], "title": r["title"], "path": r["path"],
        "source_family": r["source_family"] if "source_family" in r.keys() else "",
        "source": r["source"] if "source" in r.keys() else "",
        "trust_tier": r["trust_tier"] if "trust_tier" in r.keys() else None,
        "tags": r["tags"], "snippet": snippet or (r["snip"] or ""),
        "body": r["body"] or "",
    }


def _score_candidate(row: dict, query_words: list[str], phrase: str) -> float:
    """Compute fine-grained cross-matching score for a retrieved chunk."""
    title_lower = (row.get("title") or "").lower()
    body_lower = (row.get("body") or "").lower()
    family_lower = (row.get("source_family") or "").lower()
    combined = f"{title_lower} {body_lower}"

    score = 0.0
    # Exact full phrase match
    if phrase in combined:
        score += 8.0
    if phrase in title_lower:
        score += 5.0

    # Query term coverage & frequencies
    words_matched = 0
    for w in query_words:
        w_low = w.lower()
        if w_low in title_lower or w_low in family_lower:
            score += 4.0
            words_matched += 1
        elif w_low in body_lower:
            count = body_lower.count(w_low)
            score += min(3.0, 1.0 + 0.2 * count)
            words_matched += 1

    coverage_ratio = (words_matched / len(query_words)) if query_words else 0.0
    score += coverage_ratio * 6.0

    # Frontmatter / non-technical intro penalty if no substantive terms
    if any(intro in title_lower for intro in ["table of contents", "preface", "about the reviewers", "copyright"]):
        score -= 4.0

    return score


def _aggregate_families(rows: list[dict], limit: int, query_words: list[str] | None = None, phrase: str = "") -> list[dict]:
    """Return each source family's strongest chunk, ordered by intra-family rerank score."""
    best_by_family: dict[str, dict] = {}
    q_words = query_words or []
    for rank, row in enumerate(rows):
        family = row.get("source_family") or row["id"]
        row_score = _score_candidate(row, q_words, phrase) - (rank * 0.1)
        row["rerank_score"] = row_score
        current = best_by_family.get(family)
        if current is None or row_score > current["best"].get("rerank_score", -999.0):
            count = (current["count"] + 1) if current else 1
            best_by_family[family] = {"best": row, "rank": rank, "count": count, "score": row_score}
        else:
            current["count"] += 1

    ranked = sorted(best_by_family.values(),
                    key=lambda x: (-x["score"], x["rank"], x["best"]["id"]))
    return [x["best"] for x in ranked[:limit]]


def _rrf(rows_by_rank: list[list[dict]], limit: int) -> list[dict]:
    """Fuse ranked retrieval lists without mixing incompatible score scales."""
    scores: dict[str, float] = {}
    records: dict[str, dict] = {}
    for rows in rows_by_rank:
        for rank, row in enumerate(rows, 1):
            scores[row["id"]] = scores.get(row["id"], 0.0) + 1.0 / (60 + rank)
            records.setdefault(row["id"], row)
    ranked = sorted(records, key=lambda ident: (-scores[ident], ident))
    return [records[ident] for ident in ranked[:limit]]

def _fts_rows(conn, words: list[str], tag_sql: str, tag_params: list[str], limit: int,
              require_all: bool) -> list[dict]:
    if not words:
        return []
    match = (" AND ".join(words) if require_all else " OR ".join(words))
    where = "WHERE fts MATCH ?"
    params: list = [match]
    if tag_sql:
        where += f" AND ({tag_sql})"
        params.extend(tag_params)
    excluded = quarantined_chunks()
    if excluded:
        where += f" AND n.id NOT IN ({','.join('?' * len(excluded))})"
        params.extend(sorted(excluded))
    phrase = " ".join(words)
    sql = (f"SELECT n.id, n.title, n.path, n.tags, n.body, n.source_family, "
           f"snippet(fts, 2, '⟦', '⟧', '...', 12) AS snip, "
           f"CASE WHEN lower(n.source_family) LIKE '%' || ? || '%' THEN 3.0 ELSE 0.0 END + "
           f"CASE WHEN lower(n.title) LIKE '%' || ? || '%' THEN 2.0 ELSE 0.0 END + "
           f"CASE WHEN lower(n.body) LIKE '%' || ? || '%' THEN 0.5 ELSE 0.0 END AS source_boost "
           f"FROM fts JOIN nodes n ON n.id = fts.id {where} "
           f"ORDER BY source_boost DESC, bm25(fts), n.id LIMIT ?")
    try:
        return [_row_payload(r) for r in conn.execute(sql, (phrase, phrase, phrase, *params, limit)).fetchall()]
    except sqlite3.OperationalError:
        return []


def critic_verdict(rows: list[dict], limit: int) -> tuple[str, str]:
    """Cheap deterministic gate before neighbor expansion (CRAG pattern).

    Expansion costs a neighbor query per base hit and, past the limit, its
    results are cut unseen — so expanding an already-sufficient hit set is
    pure waste plus k-noise. Verdicts: `empty` (nothing to expand),
    `expand` (thin base or single-family concentration — neighbors diversify),
    `sufficient` (full limit across several families — skip the queries).
    Pure function of rows+limit: no LLM, no embeddings, same verdict for the
    same graph, so the determinism gate (Q17) cannot see it.
    """
    if not rows:
        return ("empty", "no base hits; nothing to expand")
    families = {r.get("source_family") or r["id"] for r in rows}
    if len(rows) < limit:
        return ("expand", f"thin base: {len(rows)} hits for limit {limit}")
    if len(families) == 1:
        return ("expand", "single-family concentration; neighbors diversify")
    return ("sufficient", f"{len(families)} families cover the query at full limit")


def query(question: str, limit: int = 5, tags: list[str] | None = None,
          expand: bool = False, recall: bool = False,
          verdict_out: list[dict] | None = None) -> list[dict]:
    if not DB.exists():
        print("Error: graph.db missing — run build_graph.py", file=sys.stderr)
        return []
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    stopwords = {"what", "how", "does", "do", "are", "is", "the", "a", "an", "for", "of", "in", "on", "to", "and", "or", "with", "across", "from", "this", "that"}
    words = [word.lower() for word in re.findall(r"[A-Za-z0-9_]+", question)
             if len(word) > 2 and word.lower() not in stopwords]
    original_words = list(words)
    # Deterministic domain aliases improve source-family recall without embeddings.
    aliases = {"causal": ["why"], "counterfactual": ["why"], "production": ["llms"],
               "memory": ["hierarchies"], "graph": ["databases"], "automated": ["machine"],
               "multiagent": ["systems"], "planning": ["thoughts"]}
    expanded_words = list(words)
    for word in words:
        expanded_words.extend(aliases.get(word, []))
    words = list(dict.fromkeys(expanded_words))
    tag_sql, tag_params = "", []
    if tags:
        tag_sql = " AND ".join(
            "n.id IN (SELECT nt.node_id FROM node_tags nt WHERE nt.tag=?)"
            for _ in tags
        )
        tag_params = list(tags)

    if words:
        precise = _fts_rows(conn, original_words, tag_sql, tag_params, max(limit * 4, 10), True)
        recall_rows = _fts_rows(conn, words, tag_sql, tag_params, max(limit * 8, 20), False)
        alias_rows = _alias_rows(conn, question, max(limit * 4, 10))
        ranked = [alias_rows, precise, recall_rows] if alias_rows else ([precise, recall_rows] if precise else [recall_rows])
        rows = _aggregate_families(_rrf(ranked, max(limit * 4, 10)), limit, original_words, question)
    elif tags:
        excluded = quarantined_chunks()
        sql = (f"SELECT n.id, n.title, n.path, n.tags, n.body, n.source_family, "
               f"n.source, n.trust_tier, NULL AS snip FROM nodes n "
               f"WHERE {tag_sql} ORDER BY n.id")
        rows = [_row_payload(r) for r in conn.execute(sql, tuple(tag_params)).fetchall()]
        if excluded:
            rows = [r for r in rows if r["id"] not in excluded][:limit]
        else:
            rows = rows[:limit]
    else:
        rows = []
    conn.close()

    if expand:
        verdict, reason = critic_verdict(rows, limit)
        if verdict_out is not None:
            verdict_out.append({"verdict": verdict, "reason": reason})
        if verdict != "sufficient":
            expanded = list(rows)
            seen = {r["id"] for r in expanded}
            for row in rows:
                for neighbor in get_neighbors(row["id"], limit=2):
                    if neighbor["id"] not in seen:
                        seen.add(neighbor["id"])
                        expanded.append({**neighbor, "snippet": "", "body": ""})
            rows = expanded[:limit]
    return rows


def get_neighbors(node_id: str, limit: int = 5, *, include_scar_type: str | None = None) -> list[dict]:
    """Retrieve graph neighbors, ordered by edge confidence.

    Hard-gate SCARRED_FROM edges rank above soft-guidance ones so safety-critical
    constraints surface first in retrieval. Pass ``include_scar_type='hard'`` or
    ``'soft'`` to filter to one class.
    """
    if not DB.exists():
        return []
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    scar_filter = ""
    params: list = [node_id, node_id, node_id]
    if include_scar_type == "hard":
        scar_filter = "AND (e.kind != 'SCARRED_FROM' OR e.tag = 'hard-gate')"
    elif include_scar_type == "soft":
        scar_filter = "AND (e.kind != 'SCARRED_FROM' OR e.tag = 'soft-guidance')"
    kind_order = ("CASE e.kind"
                  " WHEN 'REFERS_TO' THEN 0"
                  " WHEN 'DERIVES_FROM' THEN 1"
                  " WHEN 'SCARRED_FROM' AND e.tag='hard-gate' THEN 2"
                  " WHEN 'SUPPORTS' THEN 3"
                  " WHEN 'REFUTES' THEN 4"
                  " WHEN 'CONTRADICTS' THEN 5"
                  " WHEN 'EXTENDS' THEN 6"
                  " WHEN 'PART_OF' THEN 7"
                  " WHEN 'SEQUENCE' THEN 8"
                  " WHEN 'SCARRED_FROM' THEN 9"
                  " ELSE 10 END")
    sql = f"""
        SELECT n.id, n.title, n.path, e.kind, e.tag, e.conf
        FROM edges e
        JOIN nodes n ON n.id = (CASE WHEN e.src = ? THEN e.dst ELSE e.src END)
        WHERE e.src = ? OR e.dst = ?
          {scar_filter}
        ORDER BY {kind_order}, e.conf DESC, n.id
        LIMIT ?
    """
    rows = conn.execute(sql, (*params, limit)).fetchall()
    conn.close()
    return [{"id": r["id"], "title": r["title"], "path": r["path"],
             "kind": r["kind"], "tag": r["tag"], "conf": r["conf"]} for r in rows]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("question", nargs="?", default="")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--raw", action="store_true", help="print full body of each match")
    ap.add_argument("--tag", action="append", default=[], help="require tag (repeatable; intersection)")
    ap.add_argument("--neighbors", action="store_true", help="explore 1-hop graph neighbors for each match")
    ap.add_argument("--scar-type", choices=["hard", "soft"], default=None,
                    help="filter neighbor query to hard-gate or soft-guidance SCARRED_FROM edges")
    ap.add_argument("--expand", action="store_true", help="include graph neighbors in the result set")
    ap.add_argument("--recall", action="store_true", help="fuse an OR-term recall pass with precise retrieval")
    args = ap.parse_args()
    verdict_holder: list[dict] = []
    results = query(args.question, args.limit, args.tag, args.expand, args.recall,
                    verdict_out=verdict_holder if args.expand else None)
    if args.expand and verdict_holder:
        print(f"# critic: {verdict_holder[0]['verdict']} "
              f"({verdict_holder[0]['reason']})", file=sys.stderr)
    for r in results:
        print(f"\n# {r['id']} | {r['title']}")
        print(f"  path: {r['path']}")
        print(f"  tags: {r['tags']}")
        if args.raw:
            print(f"  ---\n{r['body']}")
        elif r["snippet"]:
            print(f"  match: {r['snippet']}")
        if args.neighbors:
            nbrs = get_neighbors(r["id"], include_scar_type=args.scar_type)
            if nbrs:
                print("  neighbors:")
                for n in nbrs:
                    tag_info = f" [{n['tag']}]" if n["tag"] else ""
                    print(f"    - {n['kind']}{tag_info} -> {n['id']} ({n['title']})")
    # A --tag intersection that matches nothing is a dead routing key: the prompt
    # author asked for a vocabulary term the corpus does not carry. Returning 0 with
    # no output made that silently mean "no principles apply" instead of "typo/stale
    # tag", so an audit prompt routed on a tag absent from knowledge/topics.md for
    # two sessions before anyone noticed (W-AUDIT-4). Fail loud instead.
    if args.tag and not results:
        print(f"Error: tag intersection {args.tag} matched no chunks — a requested tag "
              f"is absent from the corpus vocabulary (see knowledge/topics.md)",
              file=sys.stderr)
        return 2
    if not args.tag and not results and args.question:
        print(f"Error: no chunks matched the question {args.question!r}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
