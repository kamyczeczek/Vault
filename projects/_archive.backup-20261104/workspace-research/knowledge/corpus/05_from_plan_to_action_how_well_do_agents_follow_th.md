---
type: Concept
id: 05_from_plan_to_action_how_well_do_agents_follow_th
title: "From Plan to Action: How Well Do Agents Follow the Plan? (part 6/13)"
source: "From Plan to Action How Well Do Agents Follow the Plan"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

From Plan to Action: How Well Do Agents Follow the Plan? ASE ’26, October 12–16, 2026, Munich, Germany
(a) All (b) Easy (c) Medium (d) Hard
56.3
38.4
39.4
64.8
Success
Rate (%)
GPT5-mini
DeepSeek-V3
DeepSeek-R1
Devstral-small
Resolved
Unresolved
Resolved
Unresolved
Resolved
Unresolved
Resolved
Unresolved
Figure 2: Standard plan compliance metrics and success rate for studied trajectories across all models.
All
Easy
Medium
Hard
Devstral-small GPT5-mini DeepSeek-V3 DeepSeek-R1
Figure 3: Phase flow analysis under Standard plan (L ★(Φ)= N R P V ). Flow thickness notes the proportion of trajectories
going from one phase to another. The black bar indicates trajectory termination, and gray flows represent out-of-plan phases.
resolved instances consistently exhibit higher plan compliance (𝑝=
1𝑒−5and𝑝=0.032, respectively).
The correlation is positive for DeepSeek-V3, but with less statis-
tical significance (𝑝= 0.60). The exception is GPT-5 mini, where
unresolved trajectories are usually more compliant with the plan,
demonstrating negative correlation but with low statistical sig-
nificance (𝑝= 0.285). Phase flow analysis (Figure 3) demystifies
this observation: GPT-5 mini adapts its strategy based on problem
difficulty. For easier problems, where the issue description also
likely contains all the information to localize the bug, it often skips
Reproduction and transitions from navigation to patch. For harder
problems, it follows the instructed plan more closely, withthicker
Navigation -to- Reproduction flows in earlier phase changes.
Finding 3. Necessity for process-centric plan compliance
metrics.Graphectorymetrics <node count, edge count, loop
count> are in general higher for Devstral-small (<86,179,64>) and
GPT-5 mini (<38,49,18>) compared to DeepSeek-V3 (<15,27,4>) and
DeepSeek-R1 (<14,21,4>). Pearson correlation [ 29] shows a very
weak positive correlation (0 <𝑟≤ 0.2) between plan compliance
𝑃𝐶 andGraphectorymetrics. This confirms the need for a new
process-centric metric to specifically target plan compliance, as an
orthogonal factor to trajectory complexity.
Finding 4. The standard plan, in its current form, is incom-
plete.We observe that GPT-5 mini and Devstral-small,in addition
to creating and executing new tests as instructed by the plan, fre-
quently run existing tests in the repository (lower𝑃𝑃𝐹 compared to
other models). The practice is, in fact, useful for better reproduction
test generation and patch validation [ 5]. This finding motivates
augmenting existing plans with additional, relevant phases, and
assessing the impact of this plan on trajectories (§5.2).
4.1.1 Contributing Factors to Plan Compliance/Violation.Fine-
tuning paradigm.Depending on the LLM, agents may skip spe-
cific plan phases, perform them in a different order, or exhibit
out-of-plan actions. Except for Devstral-small, SWE-agent with
other LLMs tends toskip Reproduction (less presence in Figure 3).
SWE-agent with DeepSeek models often performs Reproduction
before Navigation . RQ2 (§4.2) investigates this under a controlled
setting. This also motivates modifying the plan by removing some
steps (§5.1) to further investigate plan compliance across models.
Context window pressure.As trajectories grow, the initial plan
must compete with an increasingly long history of thoughts, tool
calls, file contents, and error messages, which can make the plan
less salient later in execution. Deviation is further encouraged by
the agent’s locally-conditioned decision process, in which each
action is chosen primarily based on the current context and re-
cent tool feedback rather than explicit adherence to the original
global workflow. We further investigate this speculation in RQ5 by
frequent plan reminders (§5.3.2).
