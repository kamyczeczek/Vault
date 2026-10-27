"""Wektorowa sciezka retrieval Fazy 8 (lazy, bez twardych zaleznosci w graphrag.py).

Model: paraphrase-multilingual-MiniLM-L12-v2 (dim 384), wagi w lokalnym
HF cache. Indeks: fixtures/graph_vec.db (kopia graph.db + nodes.embedding).
Budowa: fixtures/build_vector_index.py. Ten modul tylko czyta.

Uzycie:
    import vec_index as vi
    if vi.indeks_gotowy():
        model, tok = vi.laduj_model()
        ids = vi.wyszukaj_wektorowo("pytanie", top_k=10)
"""
from __future__ import annotations

import sqlite3
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
VEC_DB = HERE / "fixtures" / "graph_vec.db"
MODEL_SUB = "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2"
DIM = 384


def indeks_gotowy() -> bool:
    if not VEC_DB.exists():
        return False
    try:
        con = sqlite3.connect(f"file:{VEC_DB}?mode=ro", uri=True)
        try:
            n = con.execute(
                "SELECT COUNT(*) FROM nodes WHERE embedding IS NOT NULL").fetchone()[0]
            return n > 0
        finally:
            con.close()
    except Exception:
        return False


def znajdz_snapshot() -> Path:
    base = Path.home() / ".cache" / "huggingface" / "hub" / MODEL_SUB / "snapshots"
    snaps = sorted(p for p in base.glob("*") if (p / "model.safetensors").exists())
    if not snaps:
        raise FileNotFoundError(f"brak model.safetensors w {base}")
    return snaps[0]


@lru_cache(maxsize=1)
def laduj_model():
    from transformers import AutoModel, AutoTokenizer
    snap = znajdz_snapshot()
    tok = AutoTokenizer.from_pretrained(str(snap), local_files_only=True,
                                        trust_remote_code=False)
    model = AutoModel.from_pretrained(str(snap), local_files_only=True,
                                      trust_remote_code=False)
    model.eval()
    return model, tok


def embedding_tekstu(model, tok, tekst: str):
    import torch
    enc = tok([tekst], padding=True, truncation=True, max_length=256,
              return_tensors="pt")
    with torch.no_grad():
        out = model(**enc).last_hidden_state
        mask = enc["attention_mask"].unsqueeze(-1).float()
        emb = (out * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
        return torch.nn.functional.normalize(emb, p=2, dim=1)[0]


def wyszukaj_wektorowo(pytanie: str, top_k: int = 10) -> list[tuple[str, float]]:
    """Cosine top-k nad nodes.embedding. Zwraca [(id, score)]."""
    import numpy as np
    import torch
    model, tok = laduj_model()
    q = embedding_tekstu(model, tok, pytanie).numpy().astype(np.float32)
    con = sqlite3.connect(f"file:{VEC_DB}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT id, embedding FROM nodes WHERE embedding IS NOT NULL").fetchall()
    finally:
        con.close()
    scored = []
    for nid, blob in rows:
        vec = np.frombuffer(blob, dtype=np.float32)
        if vec.shape[0] != DIM:
            continue
        scored.append((nid, float(np.dot(vec, q))))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def pobierz_wezly(ids: list[str]) -> list[dict]:
    con = sqlite3.connect(f"file:{VEC_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        out = []
        for nid in ids:
            r = con.execute(
                "SELECT id, title, source_family, trust_tier, body, node_type "
                "FROM nodes WHERE id=?", (nid,)).fetchone()
            if r:
                out.append(dict(r))
        return out
    finally:
        con.close()


def pobierz_embeddingi(ids: list[str]) -> dict[str, bytes]:
    if not VEC_DB.exists() or not ids:
        return {}
    con = sqlite3.connect(f"file:{VEC_DB}?mode=ro", uri=True)
    try:
        placeholders = ",".join("?" for _ in ids)
        rows = con.execute(f"SELECT id, embedding FROM nodes WHERE id IN ({placeholders})", ids).fetchall()
        return {r[0]: r[1] for r in rows if r[1] is not None}
    finally:
        con.close()
