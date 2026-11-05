---
type: Concept
id: 15_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 16/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Preprint.
Table 7: Cross-model plan signal. Llama-3.1-70B: 80 ALFWorld tasks. Llama-3.1-8B: 20 tasks.
Phi-3 / Qwen2.5: not replay-paired (archival-only data; plan signal undefined).
Model Step+1 Residual Decay Peak layer
Llama-3.1-70B 0.453∼0.027 4.1×L 32 (40%)
Llama-3.1-8B 0.382∼0.035 10.9×L 12/32 (∼37%)
Phi-3-MediumN/A (not replay-paired)
Qwen2.5-72BN/A (not replay-paired)
countertop 1, you see a tomato 1.”) are directly relevant to the plan (“go to countertop,
pick up tomato, heat it”), so plan-relevant features stay in the residual stream across steps.
HotpotQA observations (Wikipedia passages about unrelated entities) are informationally
orthogonal to the plan (“search for X, retrieve Y”), which allows faster representational
overwrite. If this account is right, plan-decay rate should correlate with the semantic overlap
between plan content and observation content. This is a testable hypothesis for future work.
B Phase 1 Cross-Condition Plan-Signal Post-Processing
The Phase 1 cross-model sweep (Section 7) uses an independent-trajectory architecture. Each
of the six conditions (r1_raw, r1_strict, qwen3_think_raw, qwen3_think_strict, llama_70b,
qwen3_nothink) runs its own forward agent loop on each task ( nruns = 3 for reasoning
conditions, nruns = 1 for non-reasoning baselines). The behavioral task-success results are in
Table 8. The 5+5 paired-trajectory replay-pair semantics from Section 7, in which condition
B replays the actions and observations of condition A token-for-token, do not port directly
to Phase 1, because no two Phase 1 conditions are paired by construction.
Table 8: Phase 1 behavioral task success ( n=25 ALFWorld tasks). Strict stripping moves
Qwen3-thinking from 0% to 8%, matching its no-thinking baseline, but does not move
R1-Distill-Llama-70B.
Condition Solved Task SR
Non-reasoning baselines
llama_70b3/25 12.0%
qwen3_nothink2/25 8.0%
Qwen3-thinking family
qwen3_think_raw0/25 0.0%
qwen3_think_strict2/258.0%
R1-Distill-Llama family
r1_raw0/25 0.0%
r1_strict0/25 0.0%
To compute strict-strip recovery on Phase 1 data we use a cross-condition post-processor. For
each (task, r, t) with matching run index r and step t, we load the saved hidden-state arrays
from the matched raw and strict directories (r1_raw/task_NNN/run_RR/hs_step_TT.npy vs.
r1_strict/task_NNN/run_RR/hs_step_TT.npy) and compute per-layer cosine distance:
PlanSignal(task,r,t,ℓ)
1 =1−cos

hraw
(task,r,t,ℓ) ,h strict
(task,r,t,ℓ)

. (2)
This measures the same conceptual quantity as the paired-trajectory plan signal (the rep-
resentational change attributable to whether the contamination correction is applied), at
the cost that the two trajectories are not action-replay-paired. We restrict comparisons to
(task, r, t) cells where both the raw and strict trajectories executed the same step count
without environment truncation, and report cross-task mean signal only over those cells.
Within-model strict-vs-raw recovery is evaluated with paired permutation tests across the
matched per-task means. The paired-trajectory +163% headline number is unaffected by
this post-processor and remains the principal evidence for the methodological claim.
16
