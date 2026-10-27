---
type: Concept
id: 10_from_plan_to_action_how_well_do_agents_follow_th
title: "From Plan to Action: How Well Do Agents Follow the Plan? (part 11/13)"
source: "From Plan to Action How Well Do Agents Follow the Plan"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

ASE ’26, October 12–16, 2026, Munich, Germany Shuyang Liu, Saman Dehghan, Jatin Ganhotra, Martin Hirzel, and Reyhaneh JabbarvandReordered
Reminded
Devstral-small GPT5-mini DeepSeek-V3 DeepSeek-R1
Figure 14: Phase flow analysis under Reordered (L ★(Φ)= N P R V ) and Reminded setting (L ★(Φ)= N R P V ).
(a) (b)
Figure 15: Impact of Reordered plan (a) and Reminded plan (b) on the success rate.
Figure 16: Reordered plan compliance metrics.
Figure 17: Reminded plan compliance metrics.
rates in many instances. To obtain more meaningful comparisons,
we selected instances thatat least oneof the LLMs could resolve
under the Standard plan settings, leaving us with 31 instances.
Figure 19b shows the plan compliance (𝑃𝐶) values of studied
agents under all plan settings. We observe that plan compliance
drops by 13% on average across all agents. The phase flow analysis
in Figure 18 demonstrates a different trend under the Standard plan
setting in SWE-bench Pro compared to SWE-bench Verified (Fig-
ure 3), specifically for DeepSeek-V3 and DeepSeek-R1. This is likely
because SWE-bench Pro instances are more challenging and most
of the problem-solving effort goes into repetitive Navigation and
Patching , without reaching Validation . Similar to SWE-bench
Verified, the majority of the agents still skip Reproduction , achiev-
ing relatively high𝑃𝐶scores on theNo Reproductionsetting.
6.2 RQ7. Impact of Nondeterminism
To mitigate any bias due to agents’ inherent nondeterminism, we
repeated the experiments under the Standard plan three times. Pair-
wise McNemar tests [24] show statistically significant differences
across runs, confirming the non-determinism. We then identify in-
stances that are consistently resolved or unresolved across Standard
plan runs and evaluate the remaining plan variants on this repro-
ducible subset (GPT-5 mini: 401, Devstral-small: 308, DeepSeek-V3:
323, and DeepSeek-R1: 287). Figure 19a reports the plan compliance
𝑃𝐶, remaining nearly identical to that observed on the full bench-
mark. The results are consistent with our earlier findings: plan
reduction, augmentation, and reordering affect models differently
depending on their underlying problem-solving strategies, as re-
flected in the No Plan setting. Periodic plan reminders consistently
improve performance by maintaining focus on the core task.
7 Related Work
Planning has become a central mechanism for improving the
reliability of agents, especially for long-horizon and tool-using
tasks. Several studies focus on constructing and refining plans in
single- and multi-agent systems. Agent-Oriented Planning [17] and
PMC [40] decompose complex tasks into structured subtasks and co-
ordinate multiple agents to satisfy constraints, while EAGLET [33]
and Plan-and-Act [9] separate planning and execution into distinct
LLMs to improve long-horizon reasoning. ReWoo took an extreme
stance, planning all actions up-front [37]. Liu et al. [21] introduce
process-centric metrics, but as we saw in Finding 3 (§4.1), those
alone are insufficient to understand plan compliance.
