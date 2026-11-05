---
type: Concept
id: 03_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 4/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Preprint.
A: plan kept in history
B: same trajectory, plan removed
Plan
(kept) act a1 / obs act a2 / obs act a3 / obs
Plan
(removed) act a1 / obs act a2 / obs act a3 / obs
0.45
 0.11
 0.04
step 0 step +1 step +2 step +3
plan signals
= 1 cos(hs
A, hs
B)
spikes at +1,
fades to 0
within one step
Figure 1: Replay pairing. The same trajectory is run twice: A keeps the plan in history; B
replays the identical actions and observations with the plan removed. The plan-fidelity
signal is the per-step cosine distance between the two hidden states. It spikes one step after
the plan and fades to near zero within a step: a plan re-read from context, not stored in
hidden state.
“Before continuing, please state your complete plan for finishing this task. Describe each
step in order: where you will go, what you will pick up, what actions you will perform, and
where you will place the object.”
The agent replies with a sequential plan, which then stays in history for the rest of the
task. We inject at step 2 in ALFWorld (step 4 in HotpotQA): late enough that the agent
has seen the task and initial context, early enough to leave a long post-plan trajectory for
measurement.
3.3 Replay Pairing
For each agent run we create two matched conditions.
Condition A (plan-present).The agent runs normally with the guard at step 2; the plan
enters history. We capture hidden statesh (s,ℓ)
A at every stepsand layerℓ.
Condition B (plan-stripped replay).We replay A’s exact trajectory (feeding A’s observations
and action outputs) but strip the guard exchange, and call the LLM on this plan-free history
to produceh (s,ℓ)
B . B’s output is discarded; A’s trajectory drives the conversation.
Both conditions see the same action-observation sequence; they differ only in whether the
plan exchange is in history. Plan-fidelity signal at stepsand layerℓis:
PlanSignal(s,ℓ) =1−cos

h(s,ℓ)
A ,h (s,ℓ)
B

(1)
where step indices are relative to the guard: step 0 is the guard step, step +1 is the next
agent turn, and so on. Pre-plan steps ( s< 0) act as a validation baseline. A and B are
identical before the guard fires, so the signal at steps −2 and −1 should be zero. In practice
it is below 10−3 (Appendix A).
What plan-fidelity signal does and does not measure.A and B differ in plan content, but
also in history length, the relative positions of subsequent tokens, and discourse structure.
The pre-plan baseline rules out replay-mechanics confounds but does not separate plan
content from these. The strongest content-isolation controls (length-matched filler, shuffled-
plan placebos, paraphrase and ablation) are the priority next step (§9); “plan-fidelity signal”
is the cosine distance attributable to the plan exchange’s presence, a composite that upper-
bounds the content-specific component.
3.4 Strict Stripping for Reasoning Models
Standard replay pairing assumes that any hidden-state difference between A and B re-
flects only the conditioning input, i.e. the plan. For reasoning models this fails. As the
model works through each subsequent action it re-states parts of the plan, both inside its
<think>. . .</think> block and, to a lesser degree, in the retained Thought:/Action: text.
When those turns are replayed verbatim into condition B, that re-stated plan content reap-
4
