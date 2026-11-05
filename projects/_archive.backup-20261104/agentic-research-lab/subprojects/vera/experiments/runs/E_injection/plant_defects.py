"""E-suite step 2: plant one instance of each defect D1-D5 into each
question's clean claim pool (spec: 10 questions x 5 defect types = 50 cases).

Insertion positions are randomized with a fixed seed and logged to
positions.jsonl so the run is reproducible. Output: planted_claims.jsonl.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 20260924
MISSING_CHUNK = "00_esuite_nonexistent_citation_probe"


def d1_row(qid, n):
    return {
        "claim_id": f"{qid}_D1_planted_{n:02d}",
        "statement": "the lab's provenance model rejects any claim whose cited chunk fails retrieval",
        "source_ids": [MISSING_CHUNK],
        "support_type": "direct", "confidence": "high",
        "mechanism": "broken citation planted by E-suite (D1)",
        "limitation": "", "verification_status": "planted",
    }


def d2_row(qid, real_source, n):
    return {
        "claim_id": f"{qid}_D2_planted_{n:02d}",
        "statement": "the lab mandates nightly full-corpus graph rebuilds with manual sign-off before any commit",
        "source_ids": [real_source],
        "support_type": "direct", "confidence": "high",
        "mechanism": "mechanism asserted but never stated in the cited chunk (D2 planted)",
        "limitation": "", "verification_status": "planted",
    }


def d3_row(qid, original, n):
    return {
        "claim_id": f"{qid}_D3_planted_{n:02d}",
        "statement": "NOT(" + original["statement"] + ") — see planted counter-claim (D3 self-contradiction)",
        "source_ids": original.get("source_ids", []),
        "support_type": "direct", "confidence": "high",
        "mechanism": "planted to contradict " + original["claim_id"] + " (D3)",
        "limitation": "", "verification_status": "planted",
    }


def d4_row(qid, real_source, n):
    return {
        "claim_id": f"{qid}_D4_planted_{n:02d}",
        "statement": "giving agents a SQL-style tool CAUSED the observed performance gains in the cited study, independent of guardrails",
        "source_ids": [real_source],
        "support_type": "inferred", "confidence": "high",
        "mechanism": "correlation-as-causation planted (source reports co-occurrence, not intervention) (D4)",
        "limitation": "", "verification_status": "planted",
    }


def d5_row(qid, n):
    return {
        "claim_id": f"{qid}_D5_planted_{n:02d}",
        "statement": "the lab's retrieval layer secretly routes 15% of queries to a hidden vector index",
        "source_ids": [],
        "support_type": "direct", "confidence": "high",
        "mechanism": "unsourced novelty planted (no citation anywhere) (D5)",
        "limitation": "", "verification_status": "planted",
    }


def main():
    clean = [json.loads(l) for l in (HERE / "clean_claims.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    spec = json.loads((HERE / "e_suite_questions.json").read_text(encoding="utf-8"))
    rng = random.Random(SEED)
    planted, positions = [], []
    counter = {}
    by_q = {}
    for c in clean:
        # Extract qid from claim_id (format: Q1_E_c01)
        qid = c["claim_id"].split("_")[0]
        by_q.setdefault(qid, []).append(c)

    for q in spec["questions"]:
        qid = q["qid"]
        pool = list(by_q.get(qid, []))
        if not pool:
            raise SystemExit(f"no clean claims for {qid} — E-suite requires >=1 clean claim per question")
        def next_no():
            counter[qid] = counter.get(qid, 0) + 1
            return counter[qid]

        real_source = next((c["source_ids"][0] for c in pool if c.get("source_ids")), "00_okf_methodology_research")
        defs = [
            ("D1", lambda: d1_row(qid, next_no())),
            ("D2", lambda: d2_row(qid, real_source, next_no())),
            ("D3", lambda: d3_row(qid, rng.choice(pool), next_no())),
            ("D4", lambda: d4_row(qid, real_source, next_no())),
            ("D5", lambda: d5_row(qid, next_no())),
        ]
        rows = [fn() for _, fn in defs]
        order = list(range(len(pool) + len(rows)))
        rng.shuffle(order)
        out_pool = []
        for target in order:
            if target < len(pool):
                out_pool.append(pool[target])
            else:
                out_pool.append(rows[target - len(pool)])
        for i, row in enumerate(out_pool):
            if row.get("verification_status") == "planted":
                positions.append({"qid": qid, "defect": row["claim_id"].split("_")[1],
                                  "inserted_at_index": i, "pool_size": len(out_pool), "seed": SEED})
        planted.extend(out_pool)

    (HERE / "planted_claims.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in planted), encoding="utf-8")
    (HERE / "positions.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in positions), encoding="utf-8")
    print(f"planted {len(positions)} defect instances across {len(spec['questions'])} questions")


if __name__ == "__main__":
    main()
