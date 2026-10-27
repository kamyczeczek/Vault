"""Hybrid retrieval pipeline using SQLite FTS5 (BM25) + FastEmbed (Cosine/Dot) + RRF.

Phase 1.2 of book retrieval pipeline.
"""
from __future__ import annotations

import sqlite3
import struct
from fastembed import TextEmbedding

from pathlib import Path

DB = str(Path(__file__).resolve().parent.parent / "db" / "rag.db")
K_RRF = 60

_model = None


def get_embedding_model():
    global _model
    if _model is None:
        _model = TextEmbedding()
    return _model


def fts_search(query: str, top_k: int = 40, db_path: str = DB) -> list[str]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Clean query for FTS5 syntax
    # Remove special characters that break FTS5 MATCH
    clean_q = "".join(c if c.isalnum() or c.isspace() else " " for c in query).strip()
    if not clean_q:
        conn.close()
        return []

    words = clean_q.split()
    # Match any word (OR) or phrase for recall
    fts_expr = " OR ".join(f'"{w}"' for w in words if len(w) > 2)
    if not fts_expr:
        fts_expr = clean_q

    try:
        cur.execute("""
            SELECT id FROM chunks_fts
            WHERE chunks_fts MATCH ?
            ORDER BY bm25(chunks_fts)
            LIMIT ?
        """, (fts_expr, top_k))
        results = [r[0] for r in cur.fetchall()]
    except sqlite3.OperationalError:
        results = []

    conn.close()
    return results


def vector_search(query: str, top_k: int = 40, db_path: str = DB) -> list[str]:
    model = get_embedding_model()
    qvec = list(model.embed([query]))[0]

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, vec FROM vectors")

    results = []
    for cid, blob in cur.fetchall():
        vec = struct.unpack(f"{len(blob)//4}f", blob)
        score = sum(a * b for a, b in zip(qvec, vec))
        results.append((cid, score))

    conn.close()
    results.sort(key=lambda x: x[1], reverse=True)
    return [cid for cid, _ in results[:top_k]]


def rrf_fuse(rankings: list[list[str]], k: int = K_RRF) -> list[str]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)


def retrieve(query: str, top_k: int = 40, db_path: str = DB) -> list[str]:
    fts = fts_search(query, top_k=top_k, db_path=db_path)
    vec = vector_search(query, top_k=top_k, db_path=db_path)
    fused = rrf_fuse([fts, vec], k=K_RRF)
    return fused[:top_k]


def get_chunks_meta(chunk_ids: list[str], db_path: str = DB) -> list[dict]:
    if not chunk_ids:
        return []
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    placeholders = ",".join("?" for _ in chunk_ids)
    cur.execute(
        f"SELECT id, text, chapter, topic, topic_title, page_book, type FROM chunks_meta WHERE id IN ({placeholders})",
        chunk_ids
    )
    rows = {r[0]: {
        "id": r[0], "text": r[1], "chapter": r[2], "topic": r[3],
        "topic_title": r[4], "page_book": r[5], "type": r[6]
    } for r in cur.fetchall()}
    conn.close()
    return [rows[cid] for cid in chunk_ids if cid in rows]


def full_retrieve(question: str, top_k: int = 5, db_path: str = DB, wide: bool = False) -> list[dict]:
    from scripts.rerank import rerank
    cand_count = 100 if wide else 40
    candidates = retrieve(question, top_k=cand_count, db_path=db_path)
    return rerank(question, candidates, top_k=top_k, db_path=db_path)


if __name__ == "__main__":
    results = retrieve("What is DRY?")
    print("Top-5 candidate IDs for 'What is DRY?':", results[:5])
    meta = get_chunks_meta(results[:5])
    for m in meta:
        print(f"  {m['id']} (Ch{m['chapter']} T{m['topic']}: {m['topic_title']}): {m['text'][:100]}...")
