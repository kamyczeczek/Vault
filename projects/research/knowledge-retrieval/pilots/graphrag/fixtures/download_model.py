"""Pobranie wag modelu multilingual do lokalnego HF cache (Krok 2, wybor A).

Uruchamiac OD detached (Start-Process), bo transfer trwa minuty:
    Start-Process python.exe -ArgumentList "projects/research/knowledge-retrieval/pilots/graphrag/fixtures/download_model.py"
Postep w fixtures/download_model.log, koniec = linia DOWNLOAD_DONE.
Sciaga tylko wagi + drobne configi (tokenizer juz jest w cache).
"""
import os
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "download_model.log"
MID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
ALLOW = ["model.safetensors", "*.json", "*.txt",
         "1_Pooling/config.json", "modules.json"]


def main() -> int:
    from huggingface_hub import snapshot_download
    with open(LOG, "w", encoding="utf-8") as f:
        try:
            f.write("START " + MID + "\n")
            f.flush()
            path = snapshot_download(repo_id=MID, allow_patterns=ALLOW)
            f.write("SNAPSHOT " + path + "\n")
            total = sum(p.stat().st_size for p in Path(path).rglob("*") if p.is_file())
            f.write(f"SNAPSHOT_BYTES={total}\n")
            f.write("DOWNLOAD_DONE\n")
        except Exception:
            traceback.print_exc(file=f)
            f.write("DOWNLOAD_FAIL\n")
            return 1
    print("download_model: zakonczony, zobacz", LOG)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
