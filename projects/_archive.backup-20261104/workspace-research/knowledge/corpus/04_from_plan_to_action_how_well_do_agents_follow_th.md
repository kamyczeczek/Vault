---
type: Concept
id: 04_from_plan_to_action_how_well_do_agents_follow_th
title: "From Plan to Action: How Well Do Agents Follow the Plan? (part 5/13)"
source: "From Plan to Action How Well Do Agents Follow the Plan"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

ASE ’26, October 12–16, 2026, Munich, Germany Shuyang Liu, Saman Dehghan, Jatin Ganhotra, Martin Hirzel, and Reyhaneh Jabbarvand
Table 1: Summary of studied plan settings, their corresponding formulation, and type of plan variation.
Plan Setting Plan Formulation Plan Variation Plan Description
Standard (Default) Plan⟨𝑁,𝑅,𝑃,𝑉⟩Baseline Standard Navigation-Reproduction-Patch-Validation plan
No Plan — Reduction Plan removed entirely from the system prompt
Default Plan - Reproduction⟨𝑁,¬R,𝑃,𝑉⟩Reduction Reproduction phase removed
Default Plan - Validation⟨𝑁,𝑅,𝑃,¬V⟩Reduction Validation (after patching) phase removed
Default Plan + Regression Test Execution⟨𝑅 𝐺 ,𝑁,𝑅𝑃,𝑉,𝑉 𝐺⟩Augmentation Regression test execution phases added
Default Plan + Summary of Changes⟨𝑁,𝑅,𝑃,𝑉,𝑆⟩Augmentation Summarizing changes before submission added
Reordered Default Plan⟨𝑁,𝑃,𝑅,𝑉⟩Reordering Patching moved before Reproduction
Periodic Plan Reminder⟨𝑁,𝑅,𝑃,𝑉⟩Repeating Default plan re-injected everyfivetrajectory steps
model),DeepSeek-V3[ 19] (open-source general-purpose model),
andDevstral-small [24B][ 25] (distilled model specialized in coding).
We use the default settings of the models and agent (see our arti-
fact for details [22]). SWE-agent provides a standardized execution
environment, supports multiple LLMs, and embeds a default plan
in its system prompt. These properties make it a natural testbed for
studying the role of planning in programming agents.
Plan Settings.We evaluate performance of agents on a given
dataset problem undereightplan settings: (1) default plan (RQ1),
(2) no-plan, i.e., removing the entire plan from the system
prompt (RQ2), (3) removing the reproduction phase (RQ3), (4) re-
moving the validation phase (RQ3), (5) adding a regression test exe-
cution phase before navigation,𝑅𝐺, and after validation,𝑉𝐺 (RQ4),
(6) adding a change summarization phase𝑆 before submission (RQ4),
(7) step reordering, i.e., reproduction test generation after patch-
ing (RQ4), and (8) plan reminder, i.e., periodically re-injecting the
default plan into the agent’s prompt (RQ5). Table 1 lists plan settings
and their corresponding plan-compliant phase sequence, which our
pipeline checks trajectories against. We will explain the rationale
for these plan mutations in the corresponding RQs.
Dataset.We evaluate the mentioned LLMs and plan settings for
resolving real-world GitHub issues from SWE-bench Verified [6, 16]
and SWE-bench Pro [8]. Specifically, our primary evaluation (RQ1–
RQ6) uses 497 instances3 of SWE-bench Verified, covering three
difficulty levels (Easy, Medium, and Hard), providing a realistic
setting for agent behavior. To study the generalizability of findings,
we repeat RQ1–RQ5 for Python instances of SWE-bench Pro.
Analysis and Metrics.Along with the plan compliance metrics
(Equations 1–4), we report the success rate [ 16] andGraphec-
torymetrics (the number of nodes 𝑁𝐶 , temporal edges𝑇𝐸𝐶 , and
loops𝐿𝐶 in theGraphectory) [ 21]. Success rate determines the
overall impact of plans on the agent’s ability to resolve the issue,
andGraphectorymetrics provide insights into how plans affect
the overall trajectory toward resolution. In addition to metrics,
we leverage process-centricPhase Flow Analysisby Liu et al . [21]
to provide an in-depth analysis of plan-phase changes in trajec-
tories exhibiting plan violations. Phase Flow Analysis can reveal
consistent trends in agent trajectories across different problems.
The outcome of this analysis is a Sankey diagram illustrating the
evolution of trajectories from one plan phase to the next.
Mapping Validation.To assess the reliability of our automated
action-to-phase mapping, two authors independently annotated
a stratified sample from the Default Plan trajectories. For each of
3We exclude the 3 Very Hard instances, none of which is resolved by any studied model
under any plan setting and thus provides limited evidence for comparative analysis.
the four studied models, we randomly sampled 20 trajectories and
selected the first occurrence of each default-plan phase, yielding a
total of 320 actions. The annotators labeled these actions without
access to the automatically assigned labels. Agreement among the
two manual annotations and the automated labels achieved a Fleiss’
𝜅 [11] of 0.99, indicating near-perfect agreement and supporting
the reliability of the automated mapping.
4 Standard Plan Compliance and Violation
This section first investigates to what extent SWE-agent with differ-
ent choices of LLMs follows the standard program repair workflow,
i.e., Navigation , Reproduction , Patch , and Validation (§4.1).
As an extreme alternative, we remove the entire plan and evaluate
how the trajectories change (§4.2).
4.1 RQ1. Standard (Default) Plan Setting
The standard program repair plan that has been used for years
by software developers is localizing the bug (navigatingthrough
files, classes, methods, and lines to pinpoint the bug location)
and attempting toreproduceit,patchit, andvalidatethe patch
through test execution. Existing scaffolds instruct agents to follow
a similar plan with the given order in their default system prompt
(Φ={𝑁,𝑅,𝑃,𝑉} andL★(Φ)= N R P V ). Figure 2a presents
the average 𝑃𝑃𝐶 ,𝑃𝑂𝐶 ,𝑃𝑃𝐹 , and 𝑃𝐶 values (Equations 1–4) cal-
culated for 2,000 trajectories under this plan. Figures 2b–2d show
breakdowns by problem difficulty levels (Easy, Medium, and Hard).
Beyond quantitative metrics, Figure 3 shows the plan phase flow of
the agents for all the trajectories.
Finding 1. Standard plan compliance varies across models.
Devstral-small consistently follows the plan phases in the given
order, demonstrated by high 𝑃𝑃𝐶 and 𝑃𝑂𝐶 values. However, it
exhibits out-of-plan phases to a notable degree in its trajectories
(gray flows in Figure 3), with low overall𝑃𝐶. GPT-5 mini, on the
other hand, may adapt its strategy depending on the difficulty of the
problem. Its trajectories show out-of-plan phases (lower𝑃𝑃𝐹 ), and
it usually skips Reproduction (lower𝑃𝑃𝐶 and𝑃𝑂𝐶) . DeepSeek-V3
exhibits a near-perfect𝑃𝑃𝐹= 0.99but substantially lower 𝑃𝑃𝐶 and
𝑃𝑂𝐶 , i.e., restricts itself to plan phases but frequently omits some or
executes them out of order. DeepSeek-R1 consistently demonstrates
lower plan compliance than others, both in following the instructed
plan phases and in doing so in the correct order.
Finding 2. Standard plan compliance is overall higher on
resolved instances.Intuitively, following the instructed standard
plan that reflects decades of best practices should lead to successful
bug repair. The Mann–Whitney U test [23] confirms the significance
of this observation for Devstral-small and DeepSeek-R1, where
