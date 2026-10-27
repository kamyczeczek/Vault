"""Cross-encoder reranking (BAAI/bge-reranker-base) over hybrid RRF candidates.

Scores are memoized in a content-addressed cache (`data/rerank_cache.json`,
keyed by model + question + chunk text), so repeated runs — e.g. the 40- vs
100-candidate `--wide` comparison — pay the cross-encoder cost only once.
"""
import json
import sqlite3
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sentence_transformers import CrossEncoder

DB = "db/rag.db"
MODEL_NAME = "BAAI/bge-reranker-base"
CACHE_PATH = ROOT / "data" / "rerank_cache.json"
_reranker = None
_cache = None


def get_reranker(model_name: str = MODEL_NAME) -> CrossEncoder:
    global _reranker
    if _reranker is None:
        print(f"Loading cross-encoder: {model_name}...")
        _reranker = CrossEncoder(model_name)
    return _reranker


def _cache_key(question: str, text: str) -> str:
    """Content-addressed key: model + question + chunk text (self-invalidating)."""
    h = sha256()
    for part in (MODEL_NAME, question, text):
        h.update(part.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def _load_cache() -> dict:
    global _cache
    if _cache is None:
        _cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    return _cache


def _save_cache() -> None:
    if _cache is None:
        return
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(_cache), encoding="utf-8")


def _fetch_chunks(candidate_ids: list[str], db_path: str) -> list[dict]:
    """Fetch chunk metadata for all candidates in one query, preserving order."""
    conn = sqlite3.connect(db_path)
    try:
        placeholders = ",".join("?" for _ in candidate_ids)
        cur = conn.execute(
            "SELECT id, text, chapter, topic, topic_title, page_book, type "
            f"FROM chunks_meta WHERE id IN ({placeholders})",
            candidate_ids,
        )
        by_id = {
            r[0]: {
                "id": r[0], "text": r[1], "chapter": r[2], "topic": r[3],
                "topic_title": r[4], "page_book": r[5], "type": r[6],
            }
            for r in cur.fetchall()
        }
    finally:
        conn.close()
    return [by_id[cid] for cid in candidate_ids if cid in by_id]


def rerank(question: str, candidate_ids: list[str], top_k: int = 5, db_path: str = DB) -> list[dict]:
    if not candidate_ids:
        return []

    chunks = _fetch_chunks(candidate_ids, db_path)
    if not chunks:
        return []

    cache = _load_cache()
    scores: list[float | None] = [None] * len(chunks)
    misses: list[tuple[int, str]] = []
    for i, chunk in enumerate(chunks):
        key = _cache_key(question, chunk["text"])
        cached = cache.get(key)
        if cached is None:
            misses.append((i, key))
        else:
            scores[i] = cached

    if misses:
        reranker = get_reranker(MODEL_NAME)
        preds = reranker.predict([(question, chunks[i]["text"]) for i, _ in misses])
        for (i, key), score in zip(misses, preds):
            scores[i] = float(score)
            cache[key] = scores[i]
        _save_cache()

    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    results = []
    for chunk, score in ranked[:top_k]:
        chunk_copy = dict(chunk)
        chunk_copy["rerank_score"] = score
        results.append(chunk_copy)

    return results


if __name__ == "__main__":
    from scripts.recall_hybrid import retrieve
    cands = retrieve("What is DRY?", top_k=20)
    top = rerank("What is DRY?", cands, top_k=3)
    for t in top:
        print(f"[{t['rerank_score']:.3f}] {t['id']} Ch{t['chapter']} T{t['topic']} ({t['topic_title']}): {t['text'][:100]}...")
