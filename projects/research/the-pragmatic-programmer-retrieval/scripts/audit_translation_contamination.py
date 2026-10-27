#!/usr/bin/env python3
"""Session 5 FAZA 4: translation contamination audit (diagnostic, no repair).

For each EN question: tokenize (lowercase, strip punctuation), extract 3-grams
(consecutive triplets). Check each unique 3-gram verbatim against:
  A = gold chunk text — chunks whose topic is in the question's gold topics
      (conservative superset: results.json stores topics only, not chunk ids;
       a gold-topic chunk at rank 8+ is included -> biases toward flagging)
  B = reference_answer of the PL gold set (contains English book quotes)
  C = neither.
Flag: >= 30% of unique 3-grams in A or B (threshold pre-registered in session
brief: 30%).
Sanity: q001 (plain translation) expected <= 20%.
Interpretation: <=3 flagged = clean; 4-10 = partial; >10 = blind re-translation.
"""
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
GOLD_PL = PROJECT / "eval" / "gold_set_extended.json"
GOLD_EN = PROJECT / "eval" / "gold_set_extended_en.json"
CHUNKS = PROJECT / "data" / "chunks.json"
OUT = PROJECT / "handoff" / "session-5-contamination-audit.json"
FLAG_T = 0.30

TOK = re.compile(r"[a-z']+")


def ngrams(text: str, n: int = 3):
    toks = TOK.findall(text.lower())
    return {" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def main() -> int:
    gold_en = json.loads(GOLD_EN.read_text(encoding="utf-8"))["questions"]
    gold_pl = {q["id"]: q for q in json.loads(GOLD_PL.read_text(encoding="utf-8"))["questions"]}
    chunks = json.loads(CHUNKS.read_text(encoding="utf-8"))
    gold_text_by_topic: dict[int, str] = {}
    for c in chunks:
        gold_text_by_topic.setdefault(c["topic"], "")
        gold_text_by_topic[c["topic"]] += "\n" + c["text"]
    # pre-tokenized 3-gram set per topic + per reference_answer
    topic_g = {t: ngrams(txt) for t, txt in gold_text_by_topic.items()}
    ref_g = {qid: ngrams(gold_pl[qid].get("reference_answer", "") or "")
             for qid in gold_pl}

    rows = []
    for q in gold_en:
        if q["id"].startswith("u"):
            continue
        qg = set(ngrams(q["question"]))
        ng = len(qg)
        a = sum(1 for g in qg if any(g in topic_g.get(t, set()) for t in q["topics"]))
        b = sum(1 for g in qg if g in ref_g[q["id"]])
        # exact disjoint counts:
        in_a = {g for g in qg if any(g in topic_g.get(t, set()) for t in q["topics"])}
        in_b = {g for g in qg if g in ref_g[q["id"]]}
        a2, b2 = len(in_a - in_b), len(in_b - in_a)
        ab = len(in_a & in_b)
        row = {
            "id": q["id"], "n_3grams": ng,
            "in_A": a2, "in_B": b2, "in_AB_both": ab,
            "pct_w_A": round(100 * (a2 + ab) / ng, 1) if ng else 0,
            "pct_w_B": round(100 * b2 / ng, 1) if ng else 0,
            "pct_w_AuB": round(100 * len(in_a | in_b) / ng, 1) if ng else 0,
            "flag": ng and len(in_a | in_b) / ng >= FLAG_T,
        }
        row["examples_gram"] = sorted(in_a | in_b)[:3] if row["flag"] else []
        rows.append(row)
    rows.sort(key=lambda r: -(r["pct_w_A"] + r["pct_w_B"]))
    flagged = [r for r in rows if r["flag"]]
    print(f"answerable questions: {len(rows)}; flagged (>=30% 3-grams in A u B): {len(flagged)}")
    print("id | n_3grams | %A | %B | %AuB | flag")
    for r in rows[:15]:
        print(f"{r['id']} | {r['n_3grams']} | {r['pct_w_A']} | {r['pct_w_B']} | {r['pct_w_AuB']} | {r['flag']}")
    print("--- flagged_ids ---")
    print([r["id"] for r in flagged])
    print("--- flagged examples ---")
    for r in flagged:
        print(f"{r['id']}: {r['examples_gram']}")
    q1 = next(r for r in rows if r["id"] == "q001")
    print(f"sanity q001: pct_w_AuB = {q1['pct_w_AuB']} (expected <= 20)")
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"saved {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
