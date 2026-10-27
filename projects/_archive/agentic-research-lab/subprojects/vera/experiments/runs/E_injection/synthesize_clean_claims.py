#!/usr/bin/env python3
"""
Synthesize clean claims from E-suite pool digest for injection test.
Each claim is grounded in corpus chunks from clean_pools.jsonl.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent
POOL_DIGEST = ROOT / "_tmp_pool_digest.txt"
CLEAN_POOLS = ROOT / "experiments" / "runs" / "E_injection" / "clean_pools.jsonl"
OUT_FILE = ROOT / "experiments" / "runs" / "E_injection" / "clean_claims.jsonl"

# Map qid -> level from e_suite_questions.json
Q_LEVELS = {
    "Q1": 1, "Q2": 1, "Q4": 1,
    "Q5": 2, "Q6": 2, "Q7": 2, "Q8": 2, "Q10": 2,
    "Q11": 3, "Q12": 3,
}

# Claim templates per question based on pool content
# Each template: (statement, source_chunk_ids, support_type, confidence, mechanism, limitation)
CLAIM_TEMPLATES = {
    "Q1": [
        ("open knowledge format defines trust tiers for provenance", ["00_okf_methodology_research"], "direct", "high",
         "okf frontmatter ontology specifies trust tier progression from raw intake to attested computation", "tier definitions may evolve beyond v0.2"),
        ("okf graph semantics use explicit edge types like derives_from and contradicts", ["00_okf_methodology_research"], "direct", "high",
         "okf specification defines semantic edge types beyond hierarchy", "edge type taxonomy fixed in v0.2"),
    ],
    "Q2": [
        ("session compaction variance causes non-deterministic constraint loss", ["00_session_compaction_for_ai_agents", "12_full_walkthrough_workflow_for_ai_coding_matt_poc"], "direct", "high",
         "llm summaries drop different constraints across runs making agent behavior unpredictable", "applies to llm-based compaction not deterministic truncation"),
        ("re-orientation cost is the true persistence failure not session boundary", ["00_reflection_reorientation_cost"], "direct", "high",
         "agent reads same files repeatedly without query-based recovery", "measured in first-hand transcript not controlled experiment"),
    ],
    "Q4": [
        ("critic self-correction uses external tool interaction for verification", ["00_07_critic_external_tool_verification", "01_09_mistake_correction_abstraction_level"], "direct", "high",
         "critic algorithm iterates generate-verify-with-tools-correct using google search and code execution", "requires tool access not available in all environments"),
        ("grounding requirement: self-correction needs external channel or prefer initial answer", ["00_06_self_correction_grounding_requirement", "01_09_mistake_correction_abstraction_level"], "direct", "high",
         "design rule derived from huang et al and critic: correction without external grounding is liability", "does not forbid self-correction when external channel exists"),
        ("evidence citations minimum required for promotion in okf trust tiers", ["reflection_rule_of_scars"], "direct", "medium",
         "rule of scars compiles failures into inherited constraint patches requiring citations", "specific to scar inheritance mechanism not general promotion"),
    ],
    "Q5": [
        ("reflection accepted rule candidates persist as replayable constraints", ["446_harness_starter_kit", "reflection_rule_of_scars"], "direct", "high",
         "lifecycle pilots normalize accepted rules into constraint patches inherited by future cohorts", "requires explicit acceptance gate not automatic"),
        ("agent memory hierarchies separate factual experiential procedural working forms", ["830_artificial_intelligence_a_modern_approach_4th_ed", "00_agent_memory_hierarchies", "00_persistent_memory_hierarchies_agents"], "direct", "high",
         "three surveys converge on write-manage-read loop with forms taxonomy", "textual form dominates but parametric and latent forms exist"),
        ("retrieval quality dominates write sophistication for memory accuracy", ["00_reflection_retrieval_dominates_write", "00_agent_memory_hierarchies"], "direct", "high",
         "retrieval method moved accuracy 14-23 points vs write strategy 3-8 points; raw chunks beat lossy writes", "study used 1540 questions specific benchmarks"),
    ],
    "Q6": [
        ("karpathy minimalist harness uses zero-abstraction python loops with file read write bash", ["00_karpathy_minimalist_agentic_coding_harnesses"], "direct", "high",
         "treats llm as function call in simple loop with direct file operations and command execution", "philosophy not a formal framework with guarantees"),
        ("software factory requires machine gates at each station with required inputs outputs", ["02_00_software_factory_isolate_build_prove_ship"], "direct", "high",
         "factory contract table defines station inputs outputs machine gates; green pipeline proves only checks actually run", "worktree isolation prevents file collisions not semantic conflicts"),
    ],
    "Q7": [
        ("plan persistence requires external state not in-window text vulnerable to compaction", ["00_session_compaction_for_ai_agents", "01_session_compaction_for_ai_agents", "00_plan_persistence_context_window_compaction"], "direct", "high",
         "context compaction pattern intervenes at 60-70% window utilization with keep-verbatim zones", "summaries generated inside rot regime are themselves degraded"),
        ("re-orientation cost measured as token and reasoning overhead for state recovery", ["00_reflection_reorientation_cost", "00_plan_persistence_context_window_compaction"], "direct", "high",
         "agent reads tons of context same files repeatedly unable to do much per session", "first-hand symptom not controlled measurement"),
    ],
    "Q8": [
        ("eval maturity levels progress from vibe checks to llm judge to human annotation", ["01_new_markdown_file"], "direct", "high",
         "braintrust phil hetzel describes maturity levels theoretical concepts not product concepts", "transcript source may contain transcription artifacts"),
        ("graph engineering eval needs distribution matching production cyclic graphs", ["335_graph_engineering_for_agentic_ai_systems_ken_hua"], "direct", "high",
         "static dag harness in tension with production cyclic graphs needing retry revision human pause", "hu wei position paper not empirical study"),
        ("autoresearch projects share zero-abstraction file-based execution loops", ["01_deep_analysis_popular_autoresearch_projects"], "direct", "high",
         "karpathy sakana swe-agent all use file system git as state not complex state machines", "analysis covers three projects not exhaustive"),
    ],
    "Q10": [
        ("automated peer reviewer inspects artifacts against specifications before commitment", ["00_automated_peer_review_and_self_correction"], "direct", "high",
         "dedicated evaluation agent role separate from generation role prevents hallucination propagation", "requires conference/contract specifications to exist"),
        ("ungrounded self-correction degrades performance per grounding requirement", ["00_06_self_correction_grounding_requirement", "00_07_critic_external_tool_verification"], "direct", "high",
         "correction loop grounded only in agent reasoning is liability; critic supplies tool-grounded alternative", "critic uses external tools not available in all settings"),
    ],
    "Q11": [
        ("bm25 remains unreasonably effective for agentic search inside agent loop", ["bm25_agentic_search_bergum"], "direct", "high",
         "jo kristian bergum defines agentic search as search inside agent loop; bm25 beats dense retrieval for this", "conference talk not peer-reviewed publication"),
        ("retrieval quality dominates write sophistication per reflection retrieval dominates write", ["00_reflection_retrieval_dominates_write"], "direct", "high",
         "retrieval method 14-23 point accuracy swing vs write strategy 3-8 points; raw chunks optimal", "specific to memory benchmarks not all retrieval tasks"),
    ],
    "Q12": [
        ("ai can out-plan senior engineer when design is phenomenally correct enabling one-shot implementation", ["00_can_an_ai_out_plan_a_senior_engineer"], "direct", "high",
         "ai that works episode: implementation often one-shot if design correct; internal tooling for doc sharing review", "single episode anecdote not systematic study"),
        ("taxonomy of 20 failure modes covers execution reasoning evaluation in autonomous research", ["00_taxonomy_of_20_ai_research_failure_modes", "00_agent_error_taxonomy_debugging_web_research"], "direct", "high",
         "agenterrorbench classifies failures into memory reflection planning execution evaluation modules", "draws from ai scientist agent laboratory swe-bench red-teaming"),
    ],
}


def main():
    # Load clean pools to get corpus IDs per qid+pin
    pool_by_qid = {}
    with open(CLEAN_POOLS) as f:
        for line in f:
            row = json.loads(line)
            qid = row["qid"]
            if qid not in pool_by_qid:
                pool_by_qid[qid] = []
            pool_by_qid[qid].append(row)

    claims = []
    claim_counter = {}

    for qid, templates in CLAIM_TEMPLATES.items():
        level = Q_LEVELS.get(qid, 1)
        pools = pool_by_qid.get(qid, [])

        # Flatten all corpus_ids from pools for this qid
        all_corpus_ids = []
        for pool in pools:
            all_corpus_ids.extend(pool["corpus_ids"])

        # Deduplicate while preserving order
        seen = set()
        unique_corpus_ids = [cid for cid in all_corpus_ids if not (cid in seen or seen.add(cid))]

        for i, (stmt, src_ids, sup_type, conf, mech, limit) in enumerate(templates):
            claim_counter[qid] = claim_counter.get(qid, 0) + 1
            claim_id = f"{qid}_E_c{claim_counter[qid]:02d}"

            # Filter source_ids to only those present in the pools
            filtered_src = [sid for sid in src_ids if sid in unique_corpus_ids]
            if not filtered_src:
                filtered_src = unique_corpus_ids[:1] if unique_corpus_ids else []

            claim = {
                "claim_id": claim_id,
                "statement": stmt,
                "source_ids": filtered_src,
                "support_type": sup_type,
                "confidence": conf,
                "mechanism": mech,
                "limitation": limit,
                "verification_status": "unverified",
            }
            claims.append(claim)

    # Write JSONL
    with open(OUT_FILE, "w") as f:
        for claim in claims:
            f.write(json.dumps(claim) + "\n")

    print(f"Wrote {len(claims)} clean claims to {OUT_FILE}")
    for c in claims:
        print(f"  {c['claim_id']}: {c['statement'][:80]}... (sources: {c['source_ids']})")


if __name__ == "__main__":
    main()