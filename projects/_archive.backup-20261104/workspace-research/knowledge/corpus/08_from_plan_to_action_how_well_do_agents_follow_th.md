---
type: Concept
id: 08_from_plan_to_action_how_well_do_agents_follow_th
title: "From Plan to Action: How Well Do Agents Follow the Plan? (part 9/13)"
source: "From Plan to Action How Well Do Agents Follow the Plan"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

ASE ’26, October 12–16, 2026, Munich, Germany Shuyang Liu, Saman Dehghan, Jatin Ganhotra, Martin Hirzel, and Reyhaneh JabbarvandNo Reproduce
No Validation
Devstral-small GPT5-mini DeepSeek-V3 DeepSeek-R1
Figure 6: Phase flow analysis under No Reproduction (L★(Φ)= N P V ) and No Validation plan setting (L★(Φ)= N R P ).
Trajectories still show traces of removed phases from the Standard plan.
(a) (b)
Figure 7: Impact of No Reproduction plan (a) and No Validation plan (b) on the success rate.
Figure 8: No Reproduction plan compliance metrics.
Figure 9: No Validation plan compliance metrics.
regarding plan compliance. We speculate that this behavior is due
to optimization for short-term reward [12], which is a known issue
in DeepSeek-R1 and specifically in reinforcement learning [10, 31].
5.2.2 RQ4.2. Plan with Change Summary.Adding a summary phase,
which is independent of the core repair process, yields minimal
behavioral changes across most models. The overall plan compli-
ance (𝑃𝐶) for Devstral-small, GPT-5 mini, and DeepSeek-V3 remains
nearly unchanged from the Standard setting (Figure 13). The suc-
cess rates are also largely unaffected (Figure 11b), as the summary
phase typically occurs at the end of the trajectory and does not
impact intermediate reasoning. DeepSeek-R1, however, exhibits
a substantial performance drop, with pervasive tool-calling fail-
ures observed in413instances. This suggests that even orthogonal
additions to the plan can destabilize this model’s reasoning.
Finding 10. Plan augmentation highlights plan overfitting,
and is effective only when aligned with a model’s internal
strategy.Introducing additional phases provides limited benefit
and can degrade performance if the model does not naturally em-
ploy those steps. Adding early phases can introduce unnecessary
overhead or distract the model if phases are not well internalized.
5.3 RQ5. Reordered and Reminded Plan Settings
5.3.1 RQ5.1. Reordered Plan Setting.Previous settings challenge
agents to achieve highplan phase compliance( 𝑃𝑃𝐶 ) andPlan Phase
Fidelity( 𝑃𝑃𝐹 ). Challengingplan order compliance( 𝑃𝑂𝐶 ) in-
volves reordering phases and investigating plan compliance. As
in augmented plan settings, to avoid bias or noise, we reorder the
phases so that the new plan remains relevant to the task. Specifically,
we instruct the agent to patch the bug immediately after navigation
and to postpone generating the reproduction test after patching,
primarily for patch validation rather than bug localization.
The reordered plan (L★(Φ)= N P R V ) slightly impacts
agents’ behavior. Phase flow analysis (Figure 14) shows that
DeepSeek-V3 often proceeds directly from navigation to patch-
ing, consistent with the modified plan. As shown in Figure 15a,
this slightly improves its success rate (from 191 resolved under the
default plan to 196). In contrast, Devstral-small performs reproduc-
tion before patching despite the reordered instruction, resulting in
a lower𝑃𝑂𝐶 as reflected in Figure 16. For models that rely on repro-
duction, executing it before patching remains preferred, as it helps
confirm the bug and improve the overall process. The reordering
