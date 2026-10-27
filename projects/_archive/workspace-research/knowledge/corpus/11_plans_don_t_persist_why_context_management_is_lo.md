---
type: Concept
id: 11_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 12/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Preprint.
Graded probe per-class.4-way classifier at L32, 5-fold CV , 80/class. Precision/recall/F1:
step+1 0.988/1.000/0.994; step+2 0.876/0.888/0.882; step+3 0.728/0.738/0.733; step+5
0.857/0.825/0.841. Errors are strictly monotonic on adjacent decay classes.
Cross-domain calibration.Isotonic regression fit on a 10-task HotpotQA calibration split (93
steps), evaluated on 20 held-out tasks (145 steps); splits fixed and disjoint from ALFWorld
training.
Strict stripping (reasoning models).All complete <think>. . .</think> blocks are removed
from each prior assistant turn in condition B. Content after </think> (Thought: and Action:
lines) is kept so B sees the same external action-observation sequence as A. The protocol is a
no-op (+4.8%, within noise) on Llama-3.1-70B, which emits no<think>content.
Intervention harness.The intervention harness uses ALFWorld in standard DQN evaluation
mode and reports task success via info["won"]. The probe is queried at the last-token
position of each step. A re-anchoring intervention fires when the predicted plan signal falls
below τ= 0.10. A worked example on pick_heat_then_place: the probe fires at step 5
(0.041 <τ ), the re-anchoring intervention is applied, and the trajectory ends with won=True
at step 7.
Judge.Behavioral alignment scoring uses a single LLM judge (Claude Opus 4 family) at
temperature 0; alignment threshold for “deviation” set at 0.3 on the[0, 1]scale.
Cross-model scope (negative result).Archival hidden states from Phi-3-Medium and
Qwen2.5-72B were collected in a single-run regime where step-level activations are bit-
identical across re-runs of the same question. Plan signal is a paired contrast, so it is
undefined on those data, and we make no claim about non-Llama architectures from
existing corpora. The most informative next experiments are replay-paired collection on
a mixture-of-experts model and on an RL-tuned reasoning model. Both need fresh data
collection per architecture.
A.1 Layer Profile and Task-Type Decay
The layer profile and per-task-type decay curves are promoted to Figure 2 in the main
text because they show the core robustness check: the peak is localized at L32, and all six
ALFWorld task types show nearly identical decay dynamics regardless of plan length.
A.2 Probe Validity Controls and Leakage Analysis
Because plan signal is by construction maximal at step +1 and minimal at later steps, a
probe trained on this contrast risks learning “which step is this” rather than “how much plan
is present.” Table 2 reports two controls: a shuffled-label control (breaks the real relationship
while keeping the step structure) and a step-index regressor (predicts step index from the
same hidden states). At L8, real binary AUROC is 1.000 but shuffled AUROC drops to
0.2971 and the step-index regressor reachesR2 = 0.998, so L8 representations carry nearly all
step-index information for a trivial classifier. AtL32 the step-index R2 is still high (0.978), but
the regression target (plan-signal magnitude) has graded structure (0.453, 0.110, 0.060, 0.027
at steps +1, +2, +3, +5) that step index alone does not predict. The probe’s residual fit
(R2 =0.875) is the non-trivial component.
A.3 Graded Probe Confusion Matrix
The 4-class probe ({+1, +2, +3, +5}) at L32, trained with 5-fold CV on 80 examples per class,
attains overall accuracy 0.863, macro F1 = 0.862, macro AUROC 0.976 (Table 3). Confusion
is monotonic: errors concentrate on adjacent steps, never on distant ones, consistent with a
one-dimensional plan-presence quantity that the probe orders correctly.
1Below 0.5 reflects small-sample 5-fold CV variance under shuffling; the relevant comparison is the
drop from 1.000.
12
