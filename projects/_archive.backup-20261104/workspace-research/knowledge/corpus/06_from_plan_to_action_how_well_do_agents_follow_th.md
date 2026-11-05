---
type: Concept
id: 06_from_plan_to_action_how_well_do_agents_follow_th
title: "From Plan to Action: How Well Do Agents Follow the Plan? (part 7/13)"
source: "From Plan to Action How Well Do Agents Follow the Plan"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

ASE ’26, October 12–16, 2026, Munich, Germany Shuyang Liu, Saman Dehghan, Jatin Ganhotra, Martin Hirzel, and Reyhaneh Jabbarvand
Data contamination and overfitting.Backbone LLMs may over-
fit to the workflow defined by the standard plan. There is also a
risk of data contamination when a successful trajectory for solving
individual problems in SWE-bench Verified is used to fine-tune
them [27, 32]. Therefore, plan compliance may not be rooted in
their ability to follow plan instructions [30] or the plan positively
impacting their reasoning to accomplish the task [18]. We will eval-
uate the impact of this factor by repeating the experiments on a
less contaminatedSWE-bench Pro dataset (§6.1).
4.2 RQ2. No Plan Setting
The previous research question shows a notable variance in compli-
ance with the Standard plan across agents. Given that the scaffold is
identical in all agents, two important factors influencing the obser-
vations are (1) the ability of specific LLMs to follow the instructed
plan, or (2) a conflict between following plan-prescribed phases
and training-prescribed workflows. We investigate the magnitude
of the former in §5. For the latter, we repeated the experiments
under aNo Plansetting to observe how agents perform without
any specific plan. We completely remove the default plan from the
system prompt of SWE-agent. Thereby, the agent only receives a
high-level guideline to fix the issue: given the issue description,
make changes to satisfy the issue description requirements4.
Figure 5 compares issue resolution on SWE-bench Verified with
and without the Standard Plan. The left bars show the total number
of instances resolved under each setting, while the top bars show the
number of instances in each intersection. The dot matrix indicates
the corresponding resolution set: black dots mark settings under
which the instances are resolved, and gray dots mark settings under
which they are unresolved. Thus, from left to right, the top bars
represent instances unresolved under both settings, resolved only
under the Standard Plan, resolved only under No Plan, and resolved
under both settings. Although the agent receives no plan instruction
under this setting, we further investigate if it exhibits any trace
ofStandard planin its trajectory. The rationale here is that the
backbone LLM of the agent may already have seen instructions
related to this task during training/fine-tuning. Figure 4 shows
phase flow analysis of trajectories under the No Plan setting.
Finding 5. Even when not explicitly instructed, agents follow
the Standard plan to a notable degree.The phase flow analysis
in Figure 4 shows that Devstral-small starts with Navigation , and
most trajectories still follow the Standard workflow N R P V ,
with some phases out of the Standard plan in between. Similarly,
GPT-5 mini trajectories also follow a subset of Standard plan, often
without Reproduction . In contrast, DeepSeek-V3 and DeepSeek-
R1 largely reduce their trajectories to N P patterns, skipping
Reproduction or Validation . This suggests that different models
internalize problem-solving processes differently, depending on
their training. In the absence of global plans, the encoded strategy
takes over the reasoning to solve the problem.
Finding 6. The success rate drops in the absence of the stan-
dard plan, although to different degrees across models and
4The system prompt for this experiment is available on the artifact website under
artifacts/plan-settings/no_plan/default.yaml
difficulty levels.Figure 5 shows that removing the plan consis-
tently reduces performance across all models. The majority of the
instances that SWE-agent resolved only under the Standard plan
setting are of Medium difficulty. Devstral-small and GPT-5 mini,
which exhibit problem-solving strategies similar to the Standard
plan, show only minor drops when the plan is removed. In contrast,
DeepSeek models, particularly DeepSeek-R1, experience a substan-
tial performance drop, despite showing lower compliance when the
plan is present. This indicates that the plan, even if not properly
followed, can positively impact the local reasoning of the agents,
guiding them toward their goal. Without it, reasoning becomes less
focused, often resulting in premature convergence: these models
demonstrate smallerGraphectorymetric values under the No
Plan setting, compared to the Standard plan.
Finding 7. Agents can fix previously unresolved issues under
no-plan setting.DeepSeek-V3, DeepSeek-R1, Devstral-small, and
GPT-5 mini each resolve additional instances that are not solved un-
der the default plan: 23, 11, 28, and 34, respectively. As we will show
later (§6.2), this is largely affected by the inherent nondeterminism
of LLM-based agents, with 4, 7, 16, and 4 instances deterministically
only resolved under the no-plan setting. Manual inspection of these
instances reveals a consistent trend across all models: The Stan-
dard plan instructs the model to reproduce the bug before the patch.
However, reproduction test generation is non-trivial [2, 3]. In the in-
stances studied, the models generated incorrect reproduction tests,
leading to repeated patch-test failure cycles without success. Under
the No Plan setting, the same model skipped the reproduction phase
and generated the correct patch. This is alarming but interesting:
the solution under No Plan can be due to data contamination [27].
5 Plan Variations
RQ2 shows that agents, even if not explicitly instructed to follow the
standard plan, still incorporate it in their problem-solving strategy.
As discussed, this is likely due to the training objectives of backbone
LLMs. For a more controlled plan compliance analysis, we create
variations of the Standard plan with small changes (removing one
plan phase in §5.1 or adding one phase outside of the Standard plan
in §5.2). We then investigate compliance with the mutated plan and
the impact of isolated plan changes on success rate.
5.1 RQ3. Reduced Plan Settings
We study two reduced plan variations by removing either the
Reproduction or the Validation phase. Removing Navigation
and Patching is unlikely to reveal notable observations, as these
two phases are essential and consistently appear in agent trajecto-
ries from observations in the No Plan setting.
5.1.1 RQ3.1. No Reproduction Setting.Figures 6–8 illustrate the
results underL★(Φ)= N P V . Devstral-small and GPT-5 mini
achieve lower scores on𝑃𝑃𝐹 , since Reproduction is encoded in
their internal problem-solving strategy. They also achieve near-
perfect compliance for 𝑃𝑃𝐶 and 𝑃𝑂𝐶 , i.e., follow all other plan
phases in proper order. Phase flow analysis (Figure 6) shows an inter-
esting observation about the impact of the plan on their trajectory:
in the absence of plan, these two models include Reproduction
more consistently in their trajectories compared to when the plan
excludes only that phase (compare Figure 6 with Figure 4). This,
