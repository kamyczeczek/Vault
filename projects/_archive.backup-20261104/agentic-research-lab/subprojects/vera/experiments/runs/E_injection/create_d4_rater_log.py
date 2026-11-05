#!/usr/bin/env python3
"""
Create two-rater inter-rater log template for D4 (correlation-as-causation) defect cases.
Extracts the 10 D4 planted claims and their cited source chunks for human judgment.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PLANTED_CLAIMS = ROOT / "experiments" / "runs" / "E_injection" / "planted_claims.jsonl"
PLANTED_RESULTS = ROOT / "experiments" / "runs" / "E_injection" / "planted_gate_c_results.jsonl"
OUT_FILE = ROOT / "experiments" / "runs" / "E_injection" / "d4_inter_rater_log.jsonl"

CORPUS = ROOT.parent.parent / "knowledge" / "corpus"


def chunk_text(chunk_id):
    p = CORPUS / f"{chunk_id}.md"
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def main():
    # Load planted claims
    claims = [json.loads(l) for l in PLANTED_CLAIMS.read_text(encoding="utf-8").splitlines() if l.strip()]
    results = [json.loads(l) for l in PLANTED_RESULTS.read_text(encoding="utf-8").splitlines() if l.strip()]

    # Map claim_id -> result
    result_by_id = {r["claim_id"]: r for r in results}

    # Find D4 planted claims
    d4_cases = []
    for c in claims:
        if c.get("verification_status") == "planted" and "D4" in c["claim_id"]:
            result = result_by_id.get(c["claim_id"], {})
            source_ids = c.get("source_ids", [])
            source_texts = {}
            for sid in source_ids:
                if not sid.startswith("workspace:"):
                    source_texts[sid] = chunk_text(sid)

            case = {
                "case_id": c["claim_id"],
                "qid": c["claim_id"].split("_")[0],
                "claim_statement": c["statement"],
                "source_ids": source_ids,
                "source_texts": source_texts,
                "mechanism": c.get("mechanism", ""),
                "limitation": c.get("limitation", ""),
                "rater_1": {
                    "is_causation_claim": None,
                    "source_supports_causation": None,
                    "confidence": None,
                    "notes": ""
                },
                "rater_2": {
                    "is_causation_claim": None,
                    "source_supports_causation": None,
                    "confidence": None,
                    "notes": ""
                },
                "agreement": None,
                "adjudication": None
            }
            d4_cases.append(case)

    # Write template
    with open(OUT_FILE, "w") as f:
        for case in d4_cases:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")

    print(f"Created {len(d4_cases)} D4 cases for inter-rater log at {OUT_FILE}")
    for case in d4_cases:
        print(f"  {case['case_id']} (qid={case['qid']}): {case['claim_statement'][:100]}...")
        for sid, text in case['source_texts'].items():
            print(f"    Source {sid}: {text[:150]}...")


if __name__ == "__main__":
    main()