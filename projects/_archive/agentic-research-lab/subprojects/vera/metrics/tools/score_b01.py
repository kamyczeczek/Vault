#!/usr/bin/env python
"""VERA scorecard instrumentation — dimensions 1 (coverage), 3 (grounding), 7 (cost).

Read-only over workspace corpus; writes nothing outside subprojects/vera/.
Run:  python subprojects/vera/metrics/tools/score_b01.py
Prints a per-question table + a negative-control check. Exits non-zero if any
invariant fails (e.g. claimed retrieved ID missing from corpus).
"""
import hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]          # workspace root (tools→metrics→vera→subprojects→root)
RUNS = ROOT / "subprojects" / "vera" / "experiments" / "runs"
CORPUS = ROOT / "knowledge" / "corpus"

# (qid, seeds, distractors) — mirrors benchmark/QUESTIONS.md L1 + L4 stable subset
QUESTIONS = {
    "Q1":  (["00_okf_methodology_research"],
            ["01_the_five_level_verification_ladder"]),
    "Q2":  (["00_reflection_reorientation_cost", "01_session_compaction_for_ai_agents"],
            ["00_workspace_rapid_understanding"]),
    "Q3":  ([], ["bm25_agentic_search_bergum"]),          # workspace-only: recall N/A
    "Q4":  (["00_06_self_correction_grounding_requirement", "00_07_critic_external_tool_verification"],
            ["50_harness_starter_kit"]),
    "Q13": (["240_the_book_of_why_the_new_science_of_cause_and_eff",
             "365_the_book_of_why_the_new_science_of_cause_and_eff",
             "00_07_critic_external_tool_verification"],
            ["01_new_markdown_file"]),
    "Q14": (["00_06_self_correction_grounding_requirement",
             "00_07_critic_external_tool_verification",
             "00_automated_peer_review_and_self_correction"],
            ["02_agentic_git_discipline_patterns"]),
    "Q15": (["00_plan_persistence_context_window_compaction",
             "50_graph_engineering_for_agentic_ai_systems_ken_hua",
             "00_reflection_reorientation_cost"],
            ["15_the_pragmatic_programmer_20th_anniversary_editio"]),
    "Q16": (["00_icm_implementation_pitfalls_and_failure_modes",
             "02_00_software_factory_isolate_build_prove_ship",
             "02_agentic_git_discipline_patterns"],
            ["50_icm_knowledge_big"]),
}

def claim_hash(row: dict) -> str:
    stmt = re.sub(r"\s+", " ", row["statement"].lower())
    return hashlib.sha256(
        f"{stmt}|{row['support_type']}|{row.get('mechanism','')}".encode()
    ).hexdigest()[:12]

def main() -> int:
    rows, failures = [], []
    for qid, (seeds, dist) in QUESTIONS.items():
        ans = RUNS / f"{qid}_B0.1.md"
        claims_path = RUNS / f"{qid}_B0.1_claims.jsonl"
        retrieved = re.findall(r"retrieved_ids:\s*\[([^\]]*)\]", ans.read_text())
        retrieved = [x.strip().split(" (")[0] for x in retrieved[0].split(",")] if retrieved else []
        # normalize: drop 0-prefix duplicates of 1-series? No — keep as written.
        claims = [json.loads(l) for l in claims_path.read_text().splitlines() if l.strip()]

        rec_pool = [r for r in retrieved if r not in ("", "None")]
        recall = (len(set(rec_pool) & set(seeds)) / len(seeds)) if seeds else float("nan")
        dist_hits = len(set(rec_pool) & set(dist))
        grounded = sum(1 for c in claims if c["support_type"] in ("direct", "inferred")
                       and (c["source_ids"] or c.get("mechanism","").startswith("noble")))
        invalid = [c["claim_id"] for c in claims
                   if c["support_type"] in ("direct",) and not c["source_ids"]]
        # invariant: every corpus source_id must exist
        for c in claims:
            for sid in c["source_ids"]:
                if sid.startswith("workspace:"):
                    continue
                if not (CORPUS / f"{sid}.md").exists():
                    failures.append(f"{c['claim_id']}: missing chunk {sid}")
        rows.append((qid, recall, dist_hits, len(claims), grounded, len(invalid),
                     claim_hash(claims[0]) if claims else "-"))

    print(f"{'qid':4} {'recall':>6} {'dist_hits':>9} {'claims':>6} {'grounded':>8} {'invalid_direct':>14} {'first_hash'}")
    for r in rows:
        print(f"{r[0]:4} {r[1]:6.2f} {r[2]:>9} {r[3]:>6} {r[4]:>8} {r[5]:>14} {r[6]}")

    print("\n-- negative control (distractor-only): expected low/zero --")
    print("  per-question distractor hits shown in dist_hits column; "
          "Q* workspace-only rows excluded by design")
    if failures:
        print("\nINVARIANT FAILURES:")
        for f in failures:
            print("  -", f)
        return 1
    print("\nOK: all cited corpus chunk IDs exist; table above is the B0.1 scorecard row.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
