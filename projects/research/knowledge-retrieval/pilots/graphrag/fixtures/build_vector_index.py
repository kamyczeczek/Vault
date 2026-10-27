"""Budowa indeksu wektorowego Fazy 8 na KOPII graph.db (oryginal zawsze read-only).

Kopia: fixtures/graph_vec.db (gitignored: fixtures/.gitignore -> *.db).
Doklada: kolumna nodes.embedding BLOB (float32, L2-normalized, dim 384)
+ tabela vec_meta (model, dim, built_at, n_nodes).

Uzycie (detached, bo ~10-20 min na CPU, 10373 nodes):
    Start-Process python.exe -ArgumentList "projects/research/knowledge-retrieval/pilots/graphrag/fixtures/build_vector_index.py"
Postep w fixtures/build_vector_index.log, koniec = linia INDEX_DONE.
Idempotentny: jesli vec_meta istnieje i zgadza sie model -> konczy od razu.
"""
import shutil
import sqlite3
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "build_vector_index.log"
SRC = HERE.parent.parent.parent.parent.parent / "_archive" / "agentic-research-lab" \
    / "knowledge" / "graph" / "graph.db"
DST = HERE / "graph_vec.db"
MODEL_SUB = "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2"
MODEL_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DIM = 384
BATCH = 64
MAXLEN = 256


def znajdz_snapshot() -> Path:
    base = Path.home() / ".cache" / "huggingface" / "hub" / MODEL_SUB / "snapshots"
    snaps = sorted(p for p in base.glob("*") if (p / "model.safetensors").exists())
    if not snaps:
        raise FileNotFoundError(f"brak model.safetensors w {base}")
    return snaps[0]


def main() -> int:
    import numpy as np
    import torch
    from transformers import AutoModel, AutoTokenizer
    with open(LOG, "w", encoding="utf-8") as f:
        try:
            if DST.exists():
                con0 = sqlite3.connect(f"file:{DST}?mode=ro", uri=True)
                try:
                    meta = con0.execute(
                        "SELECT model FROM vec_meta LIMIT 1").fetchone()
                    if meta and meta[0] == MODEL_ID:
                        f.write("INDEX_EXISTS model zgodny, nic do roboty\nINDEX_DONE\n")
                        return 0
                except Exception:
                    pass
                finally:
                    con0.close()
                DST.unlink()
            f.write(f"COPY {SRC} -> {DST}\n")
            f.flush()
            shutil.copy2(SRC, DST)
            snap = znajdz_snapshot()
            f.write(f"SNAPSHOT {snap}\n")
            f.flush()
            tok = AutoTokenizer.from_pretrained(str(snap), local_files_only=True,
                                                trust_remote_code=False)
            model = AutoModel.from_pretrained(str(snap), local_files_only=True,
                                              trust_remote_code=False)
            model.eval()
            con = sqlite3.connect(DST)
            try:
                rows = con.execute(
                    "SELECT id, title, substr(body,1,512) FROM nodes ORDER BY id").fetchall()
                f.write(f"NODES {len(rows)}\n")
                f.flush()
                con.execute("ALTER TABLE nodes ADD COLUMN embedding BLOB")
                con.execute("CREATE TABLE vec_meta (model TEXT, dim INTEGER, "
                            "built_at TEXT, n_nodes INTEGER)")
                upd = []
                with torch.no_grad():
                    for i in range(0, len(rows), BATCH):
                        chunk = rows[i:i + BATCH]
                        texts = [(t or "") + " " + (b or "") for _, t, b in chunk]
                        enc = tok(texts, padding=True, truncation=True,
                                  max_length=MAXLEN, return_tensors="pt")
                        out = model(**enc).last_hidden_state
                        mask = enc["attention_mask"].unsqueeze(-1).float()
                        emb = (out * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
                        emb = torch.nn.functional.normalize(emb, p=2, dim=1)
                        arr = emb.numpy().astype(np.float32)
                        for (nid, _, _), vec in zip(chunk, arr):
                            upd.append((vec.tobytes(), nid))
                        if (i // BATCH) % 10 == 0:
                            f.write(f"BATCH {i}/{len(rows)}\n")
                            f.flush()
                con.executemany("UPDATE nodes SET embedding=? WHERE id=?", upd)
                con.execute("INSERT INTO vec_meta VALUES (?,?,?,?)",
                            (MODEL_ID, DIM,
                             datetime.now(timezone.utc).isoformat(), len(rows)))
                con.commit()
                f.write(f"INDEX_DONE nodes={len(rows)} dim={DIM} model={MODEL_ID}\n")
            finally:
                con.close()
        except Exception:
            traceback.print_exc(file=f)
            f.write("INDEX_FAIL\n")
            return 1
    print("build_vector_index: zakonczony, zobacz", LOG)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
