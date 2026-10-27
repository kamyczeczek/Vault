---
type: Concept
id: 04_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 5/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Preprint.
pears even though the original plan exchange was stripped, so both conditions still encode
the plan and the cosine distance under-counts the true plan-following signal.
Strict stripping is a small change to the protocol. In addition to removing the plan exchange
from B’s history, also remove every complete <think>. . .</think> block from each prior
assistant turn. Content after </think> (Thought: and Action: lines) is kept so that B still sees
the same external action-observation sequence as A. The protocol has two sanity checks,
both tested in Section 7: on models that emit no <think> content it should be a no-op, and
on reasoning models the strict-stripped plan signal should exceed the standard plan signal.
What strict-stripping controls do not yet establish.The operator is asymmetric (applied to
B only) and removes whole <think> blocks rather than only plan-relevant spans. The recov-
ered signal could therefore reflect removal of plan-content contamination (our hypothesis),
removal of generic reasoning-history content, or an asymmetry-induced shift in B’s local
distribution. The Llama no-op (+4.8%; §7) rules out the generic-reasoning mechanism but
not the asymmetry one. Three controls would settle it: strip both A and B, replace blocks
with length-matched neutral text, or redact only plan spans. These are listed in §9.
3.5 Probe and Task Partitioning
To turn plan signal into a detector we train a Ridge regression probe on plan-present
hidden states at the peak layer ℓ∗ (Section 4), regressing the scalar plan-signal magnitude
y(s) =PlanSignal (s,ℓ∗); a threshold τ converts predictions to a fire/no-fire decision. We use
regression rather than binary classification because step index alone is trivially decodable
from the residual stream (Appendix A). We collect plan-signal data from 80 ALFWorld tasks
(50 train, 30 held out), 30 HotpotQA pairs, and 5+5 R1-Distill-70B ALFWorld tasks for the
contamination analysis; all splits are disjoint (Appendix A).
4 Experiments: Plan Signal Decay
4.1 Overall Decay Curve
Figure 3 shows plan signal vs. step offset from the guard on ALFWorld (80 tasks). Pre-plan
steps are a sanity check: A and B are identical before the guard, and we observe mean signal
< 10−8 at steps −2, −1 (floating-point noise), confirming the replay pairing is correct. At
step +1 plan signal jumps to 0.453 ± 0.039, drops to 0.110 ± 0.032 at step +2 (4.1× in one
cycle), and settles to ∼ 0.027 by step +5. The initial magnitude nearly matches HotpotQA
(0.453 vs. 0.445) though HotpotQA decays faster (12.4×; §6). In context-management terms:
the plan’s footprint in hidden state is nearly gone within one step, so anything downstream
that needs the plan must read it back from the window.
4.2 Layer and Task-Type Profile
Step +1 plan signal peaks sharply at layer 32 (signal 0.686 ± 0.024), with L28/L36 forming
a broad mid-network peak; early and late layers are lower. We useL32 as ℓ∗. Stratified by
task type, all six ALFWorld types show closely matched spikes (0.445-0.474) and decay rates
(4.0-4.4×): complex plans (6-8 steps) decay as fully as simple ones (3-4), so the dynamics are
architectural, not task-level (Figure 2).
5 Detection: Probe for Plan Decay
5.1 Probe Performance
We train a Ridge regression probe on layer-ℓ∗ hidden states from 80 ALFWorld tasks (1360
post-plan steps) using 5-fold stratified cross-validation. The probe regresses plan-signal
magnitude. A threshold τ converts predictions to a binary fire/no-fire decision. Table 1
reports results atℓ ∗ =32 together with zero-shot transfer to HotpotQA.
5
