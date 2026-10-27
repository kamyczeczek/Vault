"""Build hybrid index (SQLite FTS5 BM25 + FastEmbed ONNX vectors).

Phase 1.1 of book retrieval pipeline.
Produces db/rag.db with tables: chunks_fts, chunks_meta, vectors.
Target checkpoint: 855 rows in each table.
"""
from __future__ import annotations

import json
import sqlite3
import struct
from pathlib import Path
from fastembed import TextEmbedding

DB = "db/rag.db"
CHUNKS = "data/chunks.json"


def build_hybrid_index(chunks_path: str = CHUNKS, db_path: str = DB):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with open(chunks_path, encoding="utf-8") as f:
        chunks = json.load(f)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS chunks_fts;
    DROP TABLE IF EXISTS chunks_meta;
    DROP TABLE IF EXISTS vectors;

    CREATE VIRTUAL TABLE chunks_fts USING fts5(
        id UNINDEXED,
        text,
        chapter UNINDEXED,
        topic UNINDEXED,
        topic_title,
        type UNINDEXED,
        tokenize='unicode61'
    );

    CREATE TABLE chunks_meta (
        id TEXT PRIMARY KEY,
        text TEXT,
        chapter INTEGER,
        topic INTEGER,
        topic_title TEXT,
        type TEXT,
        page_book INTEGER
    );

    CREATE TABLE vectors (
        id TEXT PRIMARY KEY,
        vec BLOB
    );
    """)

    print(f"Indexing FTS5 and metadata for {len(chunks)} chunks...")
    for c in chunks:
        cur.execute(
            "INSERT INTO chunks_fts (id, text, chapter, topic, topic_title, type) VALUES (?, ?, ?, ?, ?, ?)",
            (c["id"], c["text"], str(c["chapter"]), str(c["topic"]), c["topic_title"], c["type"])
        )
        cur.execute(
            "INSERT INTO chunks_meta (id, text, chapter, topic, topic_title, type, page_book) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (c["id"], c["text"], c["chapter"], c["topic"], c["topic_title"], c["type"], c["page_book"])
        )

    print("Computing FastEmbed dense embeddings (default: BAAI/bge-small-en-v1.5)...")
    model = TextEmbedding()
    texts = [c["text"] for c in chunks]
    vecs = list(model.embed(texts))

    print(f"Storing {len(vecs)} dense vectors into SQLite...")
    for c, vec in zip(chunks, vecs):
        blob = struct.pack(f"{len(vec)}f", *vec)
        cur.execute("INSERT INTO vectors (id, vec) VALUES (?, ?)", (c["id"], blob))

    conn.commit()
    conn.close()
    print(f"Zaindeksowano {len(chunks)} chunków w {db_path}.")


if __name__ == "__main__":
    build_hybrid_index()
