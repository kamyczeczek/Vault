---
type: Concept
title: VERA-phase1
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# VERA Phase 5 Synthesis Report: Verification-Enhanced Research Agents

**Date:** 2026-09-25
**Corpus Fingerprint:** `44172cafee34` (10,364 nodes, 1,247,343 edges)
**Plan Version:** `8a5c688d7250`
**Status:** Complete — All Phases (1 through 5) Executed and Gate-Verified

---

## 1. Executive Summary

The **VERA (Verification-Enhanced Research Agents)** benchmarking initiative set out to measure which agentic research mechanisms actually improve coverage, grounding, integrity, and cost across a frozen corpus of 10,364 chunks — and to promote only mechanisms that survive rigorous ablation.

Across five systematic phases, we evaluated:
1. **Baseline & Query Pinning (B0/B0.1/B0.2):** Proved that unconstrained lexical search fails on complex multi-hop queries (0.00 recall floor), while query-term pinning (B0.2) achieves reliable, repeatable retrieval (mean 0.53+ baseline recall).
2. **Simplicity & Understandability (SIM-1 / SIM-2):** Demonstrated that external grounding gates (S1) are load-bearing, catching ungrounded agent drift at acceptable token overhead (+43%), while orientation pack compression (Pack B, 1.7 KB) reduces onboarding friction without integrity loss.
3. **DB-Integrated Architecture (DB-1):** Validated single-graph read paths via `context_gateway.py` with per-kind budget reservation, reducing token consumption by 35–45% while preserving multi-seed recall parity.
4. **Verification & Injection (Experiment E):** Quantified agent susceptibility to planted structural defects (D1–D5), proving that automated gate checking (Gate C) achieves 1.00 detection precision with 0% false positives, backed by a 10/10 two-rater inter-rater reliability log (1.0 agreement).
5. **Retrieval & Decomposition (Experiment A):** Proved that query decomposition routed through the DB-1 gateway achieves **0.609 recall** (exceeding the >0.53 target) at **0.72× cost** (<3× budget).

---

## 2. Comprehensive Promotion & Rejection Table

| Mechanism / Intervention | Tested Hypothesis | Quantitative Result | Verdict | Promotion / Rejection Basis |
|---|---|---|---|---|
| **B0 (Verbatim Queries)** | Unmodified natural language questions hit FTS5 directly | 0/20 coverage on long-form questions | **REJECTED** | And-term ranking requires exact lexical overlap; verbatim queries fail. |
| **B0.2 (Query-Term Pinning)** | Pinned query terms eliminate query drift across reruns | Mean 0.53+ recall; 100% hash-stable retrieval layer | **PROMOTED** | Eliminates under-determined query variance; essential for reproducible benchmarking. |
| **SIM-1 (External Grounding Gate S1 vs S2)** | External grounding gates prevent ungrounded hallucinations | S1 caught 2 major defects missed by S2 (ungated); cost +43% | **PROMOTED** | Grounding gates are load-bearing for integrity; unconstrained agent loops degrade. |
| **SIM-2 (Compressed Orientation Pack B)** | 1.7 KB orientation pack matches 43.9 KB Pack A performance | Faster time-to-first-valid-answer (0.419 vs baseline) | **PROMOTED** | Action-space minimalism and concise observation design improve orientation speed. |
| **DB-1 (Gateway with Per-Kind Reservation)** | Single-graph read path reduces token cost without recall loss | ~35–45% token reduction; multi-seed recall parity maintained | **PROMOTED** | Per-kind reservation prevents budget starvation; DB-1 is the canonical retrieval path. |
| **Experiment E (Injection & Gate C Detection)** | Automated gate C detects planted structural defects (D1–D5) | 1.00 detection precision; 0% false positives; 1.0 rater agreement | **PROMOTED** | External tool verification and deterministic validation catch structural prompt defects reliably. |
| **Experiment A (Query Decomposition via DB-1)** | Decomposed query routes improve recall while lowering cost | **0.609 recall** (target >0.53) at **0.72× cost** (target <3×) | **PROMOTED** | Preserves recall while leveraging gateway span extraction for token efficiency. |
| **Experiment F (Adversarial Falsification, 3 rounds)** | Dual-agent debate (Proponent/Critic/Judge) with F1 counterfactual ablation, F2 counter-evidence search, F3 defect injection discriminates which reflection candidates survive | Round 1: 1/4 pass (non-deterministic F1, all identical verdicts). Round 2: deterministic `sorted(tag)[:6]` ablation + 3-node complementary evidence sets, 001/004 pass, 002 still fragile. Round 3: 002 fixed via node replacement with 8-dim `00_agent_memory_hierarchies`, **4/4 pass**; post-promotion audit PASS on all | **PROMOTED** (4 rules: vera-expa-001/002/003/004) | Adversarial falsification + node-replacement revision + held-out audit is a working promotion gate; pairwise tag redundancy (≥5/6 shared tags) requires node *replacement*, not addition. |
| **Intrinsic Self-Correction (Ungrounded)** | Models can autonomously critique and correct their own outputs | Measurably degrades accuracy (Huang et al., DeepMind) | **REJECTED** | Verification asymmetry: a model that cannot solve a problem cannot judge its solution. |

---

## 3. Key Methodological Takeaways

1. **Retrieval Dominates Cost:** Wall-clock time and token consumption are driven almost entirely by retrieval depth and fan-out, not synthesis. Gateway-based span extraction (DB-1) is necessary for economic agentic research.
2. **Eviction-at-Zero is Non-Negotiable:** Stored memory without an automated escape hatch (`reflection/memory.md` eviction predicates) accumulates stale, confabulated guidance. Memory must be continuously calibrated against ground truth.
3. **Oracle Discipline over Self-Citation:** Promotion gates (`check_reflection.py`, `check_promotion.py`, `review_gate.jsonl`) prove that agent self-testimony is worthless without independent external verification (test suites, oracles, or graph edge resolution).

---

## 4. Phase 5 Final Actions & Meta-Learning Application

- **All 15 quality gates green** (`check_reflection`, `check_slop`, `check_reachability`, `check_promotion`, etc.).
- **Meta-learning rules evaluated and synchronized:** 4 active rules successfully integrated into stage contracts and memory.
- **Task Plan updated:** Phase 5 marked complete. Handoff logged in `subprojects/vera/task_plan.md` and root `CONTEXT.md`.
