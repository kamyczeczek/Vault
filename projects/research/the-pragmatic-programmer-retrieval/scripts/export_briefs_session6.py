"""Export per-question brief files to Temp for answerpilot spawns (chunks verbatim from dump)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DUMP = json.loads((ROOT / "handoff" / "session-6" / "dumps" / "dump.json").read_text(encoding="utf-8"))["index"]
OUT = Path(r"C:\Users\Mateusz\Desktop\root_workspace\handoff\session-6-briefs")
OUT.mkdir(parents=True, exist_ok=True)

CANARY_CHUNKS = DUMP["q003"]["chunks"]
SPAWNS = {qid: DUMP[qid]["chunks"] for qid in DUMP if qid not in ("canary",)}
SPAWNS["canary"] = CANARY_CHUNKS

for qid, chunks in SPAWNS.items():
    if qid == "canary":
        question = DUMP["q001"]["question"]
    else:
        question = DUMP[qid]["question"]
    frags = "\n\n".join(
        f"--- Topic {m['topic']}: {m['topic_title']} (id {m['id']}) ---\n{m['text']}" for m in chunks
    )
    body = (
        "Answer in 1-3 sentences in English, based only on the fragments below. "
        "If the fragments do not contain the answer, write exactly: NOT IN THE BOOK\n\n"
        f"Question: {question}\n\nFragments:\n{frags}\n"
    )
    (OUT / f"{qid}.txt").write_text(body, encoding="utf-8")
print(f"exported {len(SPAWNS)} briefs to {OUT}")
