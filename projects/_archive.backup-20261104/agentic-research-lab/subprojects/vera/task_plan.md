---
type: Concept
title: task_plan
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Task Plan: vera (Verification-Enhanced Research Agents)

Goal: Turn this workspace into an experimental platform that measures which agentic-research mechanisms (retrieval, verification, falsification, multi-agent) actually improve coverage, grounding, integrity, and cost — and promote only mechanisms that survive ablation.

Wayfinder framing: each phase is a question whose resolution is a decision. `research` tickets may run in parallel; all others one-per-session.

## Destination

A lab-about-the-lab report: "We tested N verification mechanisms on M frozen-corpus questions; here is what measurably works and what is ceremony." Results feed `stages/06_meta_evolve` with hard numbers.

## Decisions so far

- 2026-09-24: Hard experiment ordering A→E→D→reproducibility→F; multi-agent debate (F) gated on E results
- 2026-09-24: Claim-level (not document-level) is the unit of evaluation
- 2026-09-24: Corpus fingerprint frozen for the study duration; every result row logs it
- 2026-09-24: Gate set is difficulty-tier dependent (from L4 gate ablation): S1 (retrieve→answer→1
  grounding gate) for L1–L2; S0 full protocol (rerun diff + negative controls) for L3–L5
- 2026-09-24: Query-term pinning (B0.2) validated: 0.00 → 0.33–1.00 recall lift on pinned questions;
  v1 pin failures documented, pins are versioned (v2)
- 2026-09-25: Two-rater W-DEEP inter-rater log completed: 10/10 D4 cases scored, perfect agreement (1.0), all confirmed as correlation-as-causation defects (runs/E_injection/d4_inter_rater_log.jsonl); gate-ablation results now final
- 2026-09-25: F meta-findings (vera-expf-rev-001/002 + final-001) all passed F pipeline + post-promotion audit, promoted to accepted (memory.md now 12 rules); propagated to stages/04_reflect/CONTEXT.md via apply_meta_learning.py (15/15 gates green)
- 2026-09-25: Reachability seeds for the 3 new meta-rules deferred (UNREACHABLE on frozen corpus — meta-concepts not ingested); re-add after next ingest + graph rebuild
- 2026-09-25: SIM-2b (Q22 causal-chain follow-up, pre-registered protocol + harness) verdict **PASS**: B wins on Q22 — all 4 rules hold at median (reorient_cum B=1 ≤ A=2; ttfva B=2 ≤ A=3; ungrounded B=1 = A=1; control spike C=3 > B=1). Resolves v1 INCONCLUSIVE (Q1 too narrow); Q1 verdict stays null. Pre-run refinements R-rc/R-tt/R-c3/R-ct/R-db logged in protocol; runs/sim2_q22_results.md + 12 session JSONs survived on main tree. Worktrees removed post-run.

## Phases

- [x] Phase 1: Benchmark + baseline green
  - Status: complete
  - Owner: agent
  - Evidence: V1–V5 + V-N1 closed in gates.md; reports/B0.1_phase1.md
- [x] Phase 1b: B0.2 pinning pass + L2/L3 runs
  - Status: complete
  - Owner: agent
  - Evidence: pinned query terms in QUESTIONS.md; Q5–Q12 scorecard rows; Q6 pin v3 closes DB1-F3
- [x] Phase 2: Simplicity & understandability (SIM-1, SIM-2) per researcher direction
  - Status: complete (SIM-1); SIM-2 INCONCLUSIVE
  - Owner: agent
  - Evidence: SIM-1 arms S0/S1/S2 in phase2_simplicity_db.md; SIM-2 pack B (1.7 KB) written and measured; cold-start runbook executed (runs/sim2_results.md) — verdict INCONCLUSIVE: B faster ttfva (0.419 ≤ 0.7×0.640) but reorient NOT ≤ A (0.163 > 0.125); C control did not spike (0.119 < 0.163); follow-up: raise task to Q22 or increase sample size
- [x] Phase 3: DB-integrated workflow (DB-1 single-graph read path)
  - Status: complete
  - Owner: agent
  - Evidence: runs/DB1_arms.md — D1 ADOPTED for L1-L2 pinned-pool retrieval via gateway; per-kind reservation fix resolves DB1-F2; Q6 pin v3 closes DB1-F3
- [x] Phase 4: Experiments A, C, E (retrieval, graph edges, verification/injection)
  - Status: complete
  - Owner: agent
  - Evidence: E-suite injection test complete (RESULTS.md); Experiment A complete (0.609 recall at 0.72× cost, report: runs/EXPA_query_decomp_20260925_031137.json); Experiment C complete (graph edge expansion lifts overall recall from 0.5806 to 0.6129, +0.0323 delta, report: runs/EXPC_graph_expansion_20260925_050904.json)
- [x] Phase 5: Synthesis report → promotion candidates → apply_meta_learning --dry-run
  - Status: complete
  - Owner: agent
  - Evidence: `reports/VERA-phase1.md` with promotion/rejection table and applied meta-learning rules
- [x] Phase 6: Experiment F — Multi-Agent Adversarial Falsification
  - Status: complete (3 rounds)
  - Owner: agent
  - Evidence: Round 1: 1/4 pass (003 accepted). Round 2: deterministic F1 + 3-node evidence sets, 001/004 pass, 002 still fragile (pairwise tag redundancy). Round 3: 002 fixed via node replacement with 00_agent_memory_hierarchies (8-dim), all 4 accepted. Runs: EXPF_adversarial_falsification_20260925_200556.json, EXPF_adversarial_falsification_20260925_201528.json; audits: EXPF_audit_experimental_20260925_201813.json; digests: vera_expf_findings.md, vera_expf_revision_findings.md, vera_expf_final_round.md. memory.md: 9 accepted rules.
  - Meta-findings: vera-expf-rev-001 (3-node complementary sets), vera-expf-rev-002 (pairwise redundancy requires replacement, not addition), vera-expf-final-001 (batch acceptance pattern)
  - Next: closed. apply_meta_learning.py propagated the 4 new rules into stage contracts; W7 loop-closure (D+A+B+C) wires them into code enforcement (Phase 7).

- [x] Phase 8: SIM-2b Q22 cold-start follow-up (resolves SIM-2 v1 INCONCLUSIVE)
  - Status: complete — verdict PASS (B wins on Q22)
  - Owner: agent
  - Evidence: pre-registered protocol experiments/sim2_q22_protocol.md (verdict rule frozen; refinements R-rc seed-valid reorient_cum, R-tt cumulative-union ttfva, R-c3 3-call C control, R-ct two-tier contamination, R-db graph.db hardlink into worktrees); harness experiments/sim2_q22.py; 12 sessions in 3 isolated worktrees (interleaved 5A/5B/2C); per-session logs + summary in runs/sim2_q22_*.json; report runs/sim2_q22_results.md — all 4 pre-registered rules pass, 0 trivialization hits; caveats logged (pack A carries VERA lab-state tokens; scripted-simulation class, fresh-LLM run remains next class)
- Whether an external (outside-workspace) question set is needed to fight benchmark leak
## Out of scope

- Corpus ingestion during the study (frozen corpus only)
- New provider/model swaps mid-study (sampling variance must be isolatable)
- Publishing; the report is an internal artifact until promoted

## Abandonment protocol

ABANDON: <id> <non-empty reason> — handoff recorded in progress.md or GATES.md
