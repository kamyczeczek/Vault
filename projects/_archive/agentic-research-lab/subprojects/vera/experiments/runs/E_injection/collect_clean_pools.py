"""E-suite step 1: collect clean D1 gateway pools for the 10-question E-suite.

Writes clean_pools.jsonl (one row per (qid, pin)) and cost rows for the
E-suite pool budget. No corpus file reads — everything via context_gateway.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4] / "knowledge" / "graph"))
from context_gateway import context_packet  # noqa: E402


def main():
    spec = json.loads((HERE / "e_suite_questions.json").read_text(encoding="utf-8"))
    out = HERE / "clean_pools.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for q in spec["questions"]:
            for pin in q["pinned_queries"]:
                pkt = context_packet(pin, mode="fast", limit=5)
                row = {
                    "qid": q["qid"],
                    "level": q["level"],
                    "pin": pin,
                    "fingerprint": spec["fingerprint"],
                    "estimated_tokens": pkt.get("estimated_tokens"),
                    "truncated": pkt.get("truncated"),
                    "corpus_ids": [it.get("id") for it in pkt.get("items", [])
                                   if it.get("kind") == "corpus"],
                    "other_kinds": [it.get("kind") for it in pkt.get("items", [])
                                    if it.get("kind") != "corpus"],
                    "full_file_reads": 0,
                }
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
