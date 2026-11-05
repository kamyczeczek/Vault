---
type: Concept
id: 07_from_plan_to_action_how_well_do_agents_follow_th
title: "From Plan to Action: How Well Do Agents Follow the Plan? (part 8/13)"
source: "From Plan to Action How Well Do Agents Follow the Plan"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

From Plan to Action: How Well Do Agents Follow the Plan? ASE ’26, October 12–16, 2026, Munich, Germany
Devstral-small GPT5-mini DeepSeek-V3 DeepSeek-R1
Figure 4: Phase flow analysis under No Plan setting. Agents still exhibit traces of Standard plan phases ( Φ={ N, R, P, V} ).
Figure 5: Impact of No Plan setting on the success rate.
consequently, impacts the ability of these models to accomplish the
task. As shown in Figure 7a, their success rate decreases notably.
In contrast, DeepSeek models achieve nearly-perfect 𝑃𝑃𝐹 val-
ues, indicating that their trajectories do not observe Reproduction .
However, they suffer the most from lower𝑃𝑃𝐶 and𝑃𝑂𝐶 , confirmed
by phase flow analysis. Similarly, these two models suffer from an
incomplete plan, reflected in the drop in success rate. DeepSeek-
R1’s performance drop is more substantial. A deeper analysis of its
trajectories reveals that, in many cases (349 instances), the model
produces malformed tool calls, emitting function calls as plain text
rather than in the expected format. This leads to repeated execution
errors and eventual termination5. The observation suggests that re-
moving Reproduction destabilizes DeepSeek-R1 interaction with
the scaffold itself, beyond its effect on problem-solving.
5.1.2 RQ3.2. No Validation Setting.Figures 6, 7b, and 9 illustrate
the results underL★(Φ)= N R P . GPT-5 mini suffers greatly
without Validation , indicating a strong dependence on this phase,
as it enables the model to identify incorrect patches and iteratively
refine them, rather than prematurely submitting them.
In contrast, DeepSeek-V3 shows only slight performance degra-
dation and high 𝑃𝑃𝐹 , consistent with its tendency to skip
Validation in the No Plan setting. This further reinforces the im-
portance of either alignment of the model’s internalized strategy
with the instructed plan or enabling true reasoning and adaptive
planning in models. Devstral-small is less affected than in the No Re-
production setting, suggesting that early-stage grounding through
reproduction (e.g., for better bug localization) is more critical to its
performance, while validation plays a less central role in shaping
its trajectory. We believe this is yet another signal about the data
contamination in this model, as it can generate correct patches
without validation. DeepSeek-R1 again exhibits the lowest success
rate and significantly lower 𝑃𝑃𝐶 and𝑃𝑂𝐶 , with the majority of
trajectories terminating early with repeated tool-calling failures
(§5.1.1).
5Exit message: “Exit due to repeated format/blocklist/bash syntax errors”
Finding 8. The negative impact of a bad, incomplete plan
is greater on trajectories than the impact of no plan at all.
Overall, removing a specific plan phase can strongly affect models
that (1) do not have it in their internal workflow to compensate or
(2) are trained to incorporate the plan in their reasoning, as in its
absence, their reasoning is incomplete.
Finding 9. Agents can fix previously unresolved issues un-
der reduced plan settings.Similar to Finding 7, the primary
reason for exclusive resolution under the No Reproduction set-
ting is the agents’ inability to generate a good reproduction test
when instructed by the Standard plan. In contrast, under the No
Validation setting, specifically when we eliminate the impact of non-
determinism (§6.2), agents can rarely resolve previously unsolved
issues: GPT-5 mini (7), Devstral-small (19), DeepSeek-V3 (5), and
DeepSeek-R1 (1). Analysis of those instances shows that agents still
incorporated the validation phase, suggesting remaining impact of
nondeterminism.
5.2 RQ4. Augmented Plan Settings
We investigate compliance with plans that include new phases to
further demonstrate overfitting to known plans. Arbitrary, task-
irrelevant phases may bias the findings; it will be unclear whether
an agent struggles with plan compliance or reacts negatively to in-
coherent instructions. To account for this threat, we only introduce
phases relevant to the issue repair task, namely, (1) executing re-
gression tests at the beginning and end (§5.2.1) and (2) summarizing
changes in a PR-style format before submission (§5.2.2).
5.2.1 RQ4.1. Plan with Regression Test Execution.Figures 10–12
summarize the results. Devstral-small and GPT-5 mini already per-
form regression testing, even when not explicitly instructed to
do so (Finding 4). The small drop in success rate is likely due to
nondeterminism (§6.2). Devstral-small has a high𝑃𝑃𝐶 , including
all phases, while GPT-5 mini adaptively skips or reorders some
phases as discussed (lower 𝑃𝑃𝐶 ). Concerning regression testing,
Devstral-small and GPT-5 mini show a notable difference: as shown
through phase flow analysis (Figure 10), Devstral-small performs
regression testingafter Navigation and after Validation , while
GPT-5 mini consistently runs regression tests as the first step and
after Validation using new tests.
DeepSeek-V3 experiences a higher performance drop, accompa-
nied by low𝑃𝑃𝐶 , suggesting difficulty in incorporating the regres-
sion testing phases. Running existing tests early in the trajectory
and their lengthy feedback likely overrides the impact of other
plan phases (lower𝑃𝑂𝐶 ), shifting focus toward test environment
setup and irrelevant execution results rather than effective bug
localization and patching. DeepSeek-R1 continues to exhibit severe
performance issues in this setting. The persistent tool-calling er-
rors result in a very low success rate, preventing any conclusion
