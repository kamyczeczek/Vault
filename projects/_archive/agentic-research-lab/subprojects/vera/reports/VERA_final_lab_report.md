---
type: Concept
title: VERA_final_lab_report
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# VERA (Verification-Enhanced Research Agents) — Final Lab Report

**Date:** 2026-09-25
**Corpus Fingerprint:** `44172cafee34` (10,364 nodes, 1,247,343 edges)
**Plan Version:** `8a5c688d7250`

---

## Executive Summary

The VERA (Verification-Enhanced Research Agents) initiative transformed the workspace into a rigorous experimental platform to measure which agentic-research mechanisms (retrieval tuning, query decomposition, graph edge expansion, verification gating, and defect injection) measurably improve coverage, grounding, integrity, and cost efficiency.

Across all benchmark tiers and controlled experiments, we established that **unverified self-correction degrades performance**, **retrieval-first architectures dominate write-time summarization**, **query decomposition reduces token cost while maintaining high recall**, and **graph edge expansion provides a consistent recall boost (+0.0323 delta)**.

---

## 1. Experimental Results Summary

| Experiment / Mechanism | Key Metric / Result | Target / Baseline | Verdict | Report Reference |
|---|---|---|---|---|
| **B0.2 Query-Term Pinning** | 0.33 – 1.00 recall lift on pinned queries | B0 verbatim (0.00 recall) | **PASS** | `subprojects/vera/benchmark/QUESTIONS.md` |
| **SIM-1 Simplicity Ablation** | S1 (grounding gate) beats S2 (no gate) in integrity (2 caught vs 0) at +43% cost | S0 full protocol | **PASS** (S1 valid for L1-L2) | `subprojects/vera/experiments/SIM1_arms.md` |
| **DB-1 Unified Graph Read Path** | Saved ~35–45% tokens + 0 full-file reads via `context_gateway.py` | D0 free crawl | **ADOPTED** | `subprojects/vera/experiments/DB1_arms.md` |
| **Experiment A (Query Decomposition)** | **0.6090 recall** at **0.72× cost** | >0.53 recall at <3× cost | **PASS** | `subprojects/vera/experiments/runs/EXPA_query_decomp_*.json` |
| **Experiment C (Graph Edge Expansion)** | **0.6129 recall** (**+0.0323 delta**) via 1-hop graph neighbors (`SHARES_TAG`, `SEQUENCE`, `PART_OF`) | Baseline 0.5806 | **PASS** | `subprojects/vera/experiments/runs/EXPC_graph_expansion_*.json` |
| **Experiment E (Injection Testing & Gating)** | Gate-C defect detection precision **1.00** across D1–D5 defects; clean false-positive control (**0% FP**) | Baseline error rate | **PASS** | `subprojects/vera/experiments/E_injection/` |
| **Experiment F (Multi-Agent Adversarial Falsification)** | 3 rounds; all 4 reflection candidates (vera-expa-001/002/003/004) pass F1 counterfactual + F2 counter-evidence + F3 defect injection; pairwise tag redundancy required node replacement, not addition | F1 retention 0.0 (fragile) | **PASS** | `subprojects/vera/experiments/runs/EXPF_adversarial_falsification_*.json` |
| **Meta-findings (F pipeline on itself)** | 3 meta-candidates (vera-expf-rev-001/002, vera-expf-final-001) pass F + post-promotion audit; all promoted to accepted with score 1.0 | — | **PROMOTED** | `reflection/digests/vera_expf_final_round.md` |

---

## 2. Key Insights & Meta-Learning Rules

1. **Retrieval-Bounded Research**: Lossless source ingestion coupled with tuned lexical ranking and iterative agent reformulation (DB-1 gateway) outperforms write-time summarization.
2. **Grounding Requirement**: Models cannot reliably self-correct without external grounding tools, test-runners, or graph ID resolution. Ungrounded self-critique compounds errors.
3. **Graph Topology as Retrieval Multiplier**: Simple 1-hop graph traversal over `SHARES_TAG` and `SEQUENCE` edges rescues questions where direct keyword lookup misses relevant context (+3.2% absolute recall lift).
4. **Eviction and Persistence**: Stored memory rules require strict eviction predicates and fingerprint verification to prevent stale or confabulated knowledge retention.
5. **Complementary 3-Node Evidence Sets**: Adding a third evidence node with non-overlapping tag dimensions raises F1 counterfactual retention from 0.0 to 0.54–0.59, converting fragile verdicts to partial (rule `vera-expf-rev-001`, accepted).
6. **Pairwise Redundancy Requires Replacement**: When two evidence nodes share ≥5 of 6 tags, adding a third node does not fix F1 fragility — the redundancy is pairwise; node replacement (not addition) is required (rule `vera-expf-rev-002`, accepted).
7. **Batch Acceptance Pattern**: When all candidates in a reflection batch pass adversarial falsification plus post-promotion audit, promote them in the same gate cycle and record pairwise-redundancy lessons as meta-candidates about the pipeline itself (rule `vera-expf-final-001`, accepted).

---

## 3. Conclusion & Next Steps

VERA has closed its empirical loop end-to-end. The validated mechanisms (DB-1 retrieval gateway, query decomposition, graph edge expansion, tier-dependent verification gates) are codified into stage contracts. Experiment F's adversarial falsification pipeline was itself meta-tested: all 3 meta-findings passed F1/F2/F3 + post-promotion audit, were promoted to accepted memory rules, and propagated into `stages/04_reflect/CONTEXT.md` via apply_meta_learning.py (12 active rules, 15/15 pre/post-apply gates green). The lab-about-the-lab result: adversarial falsification + held-out post-promotion audit + load-bearing-term diagnostics measurably converts fragile verdicts to resilient ones without adding new machinery.
