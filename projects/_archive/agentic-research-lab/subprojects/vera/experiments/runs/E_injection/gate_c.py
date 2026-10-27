"""E-suite step 3: automated gate-C instruments over clean + planted pools.

Detectors (scriptable tiers only — LLM-rater cells are reported as pending,
never guessed):
  D1 broken citation      : ask.py resolution of each corpus source_id (rc != 0 = broken)
  D5 unsourced novelty    : support_type in {direct, inferred} with empty source_ids
  D2 unsupported mechanism: content-word overlap between claim and cited chunk text
                            (heuristic; threshold validated on the clean pool first)
  D3 self-contradiction   : negation-wrap detection (claim statement contains another
                            claim's statement with a negation prefix)
  D4 causation            : NOT scriptable — routed to two-rater log (pending cell)

Usage: python gate_c.py --input clean_claims.jsonl|planted_claims.jsonl --out matrix_<name>.jsonl
"""
import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
CORPUS = ROOT / "knowledge" / "corpus"
D2_MIN_OVERLAP = 3  # content words shared between claim and cited chunk, minimum to call "supported"

STOP = {"the", "a", "an", "of", "to", "in", "is", "are", "for", "with", "its", "that", "this", "and", "or"}


def content_words(text):
    return {w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in STOP}


def ask_resolves(chunk_id):
    r = subprocess.run([sys.executable, str(ROOT / "knowledge" / "graph" / "ask.py"), chunk_id],
                       capture_output=True, text=True, cwd=ROOT)
    return r.returncode == 0 and chunk_id in r.stdout


def chunk_text(chunk_id):
    p = CORPUS / f"{chunk_id}.md"
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    claims = [json.loads(l) for l in (HERE / args.input).read_text(encoding="utf-8").splitlines() if l.strip()]
    by_q = defaultdict(list)
    for c in claims:
        # Extract qid from claim_id (format: Q1_E_c01 or Q1_D1_planted_01)
        qid = c["claim_id"].split("_")[0]
        c["qid"] = qid
        by_q[qid].append(c)

    results = []
    for c in claims:
        row = {"claim_id": c["claim_id"], "qid": c["qid"], "planted": c.get("verification_status") == "planted"}
        flags = []
        for sid in c.get("source_ids", []):
            if sid.startswith("workspace:"):
                continue
            if not ask_resolves(sid):
                flags.append({"defect": "D1", "detail": f"unresolvable source_id {sid}"})
        if c.get("support_type") in ("direct", "inferred") and not c.get("source_ids"):
            flags.append({"defect": "D5", "detail": "confident claim, empty source_ids"})
        for sid in c.get("source_ids", []):
            if sid.startswith("workspace:"):
                continue
            overlap = len(content_words(c.get("statement", "") + " " + c.get("mechanism", "")) & content_words(chunk_text(sid)))
            if overlap < D2_MIN_OVERLAP and c.get("support_type") == "direct":
                flags.append({"defect": "D2-heuristic", "detail": f"overlap={overlap} with {sid} (< {D2_MIN_OVERLAP})"})
        stmt = c.get("statement", "")
        for other in by_q[c["qid"]]:
            if other is c or not other.get("statement"):
                continue
            core = other["statement"].strip()
            if core and core in stmt and ("NOT(" in stmt or "not " in stmt.lower()[:8]):
                flags.append({"defect": "D3", "detail": f"negation-wrap of {other['claim_id']}"})
        row["flags"] = flags
        results.append(row)

    (HERE / args.out).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in results), encoding="utf-8")
    fp = sum(1 for r in results if not r["planted"] and r["flags"])
    hit = sum(1 for r in results if r["planted"] and r["flags"])
    print(f"{args.input}: {len(results)} claims | planted-with-flags {hit} | clean-FP {fp}")


if __name__ == "__main__":
    main()
