"""Print gold-topic chunks from answer_pilot dumps (parent grading helper)."""
import json
import re
from pathlib import Path

base = Path(__file__).resolve().parent.parent / "handoff" / "pilot-answer-layer-2026-10-18" / "dumps"
gold_path = Path(__file__).resolve().parent.parent / "eval" / "gold_set_extended.json"
refs = {q["id"]: q for q in json.loads(gold_path.read_text(encoding="utf-8"))["questions"]}

for qp in sorted(base.glob("*.json")):
    d = json.loads(qp.read_text(encoding="utf-8"))
    if d["id"].startswith("u") or d["id"] == "canary":
        continue
    gt = set(d["gold_topics"])
    print("=" * 20, d["id"], d["type"], "gold_topics", d["gold_topics"])
    print("Q:", d["question"][:140])
    print("REF:", re.sub(r"\s+", " ", refs[d["id"]]["reference_answer"])[:260])
    for i, c in enumerate(d["chunks"]):
        if c["topic"] in gt:
            t = re.sub(r"\s+", " ", c["text"])
            print("  [#%d] T%d: %s" % (i, c["topic"], t[:480]))
