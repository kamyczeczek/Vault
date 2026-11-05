---
type: Concept
id: 00_from_plan_to_action_how_well_do_agents_follow_th
title: "From Plan to Action: How Well Do Agents Follow the Plan? (part 1/13)"
source: "From Plan to Action How Well Do Agents Follow the Plan"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

From Plan to Action: How Well Do Agents Follow the Plan?
Shuyang Liu∗
University of Illinois
Urbana-Champaign
Urbana, USA
sl225@illinois.edu
Saman Dehghan∗
University of Illinois
Urbana-Champaign
Urbana, USA
samand2@illinois.edu
Jatin Ganhotra
IBM
New York, USA
jatinganhotra@us.ibm.com
Martin Hirzel
IBM
New York, USA
hirzel@us.ibm.com
Reyhaneh Jabbarvand✉
University of Illinois
Urbana-Champaign
Urbana, USA
reyhaneh@illinois.edu
Abstract
Agents are commonly instructed to follow a task-specificplanfor
guidance. However, it is unknown to what extent agents actually
follow instructed plans. Without such an analysis—determining the
extent agentscomplywith a given plan—it is impossible to assess
whether a solution was reached through correct strategic reasoning
or through other means, e.g., data contamination or overfitting to a
benchmark. This paper presents the first extensive, systematic anal-
ysis ofplan compliancein programming agents, examining 21,120
trajectories from SWE-agent across four LLMs on SWE-bench Veri-
fied and SWE-bench Pro under eight plan variations. Without an
explicit plan, agents fall back on internalized workflows during
training, which are often incomplete, overfit, or inconsistently ap-
plied. Providing the standard plan improves issue resolution, and
we observe that periodic plan reminders can mitigate plan viola-
tions and improve task success. A subpar plan hurts performance
even more than no plan at all. Surprisingly, inserting additional
task-relevant phases in the early stage can degrade performance,
particularly when these phases do not align with the model’s in-
ternal problem-solving strategy. These findings call for fine-tuning
paradigms that teach models to follow instructed plans, rather than
encoding task-specific plans in them, so that they reason and act
adaptively, rather than memorizing workflows.
CCS Concepts
•Software and its engineering→ Software maintenance tools;
•Computing methodologies→Machine learning approaches.
Keywords
Programming Agents, Process-Centric Analysis, Agent Planning
ACM Reference Format:
Shuyang Liu, Saman Dehghan, Jatin Ganhotra, Martin Hirzel, and Reyhaneh
Jabbarvand. 2026. From Plan to Action: How Well Do Agents Follow the
∗Both authors contributed equally to this work.
This work is licensed under a Creative Commons Attribution 4.0 International License.
ASE ’26, Munich, Germany
©2026 Copyright held by the owner/author(s).
ACM ISBN 979-8-4007-2882-2/2026/10
https://doi.org/10.1145/3832783.3834400
Plan?. InProceedings of the 41st IEEE/ACM International Conference on Auto-
mated Software Engineering (ASE ’26), October 12–16, 2026, Munich, Germany.
ACM, New York, NY, USA, 12 pages. https://doi.org/10.1145/3832783.3834400
1 Introduction
Agents have emerged as a promising paradigm for automating
software engineering tasks, from code synthesis and translation to
end-to-end issue resolution [14, 36, 38]. Central to these systems is
the use ofstructured instructions, a.k.a. aplan, which decomposes
a high-level objective of a given task into an ordered sequence of
steps that the agent can follow to accomplish the task successfully.
In theory, a plan can help reduce cognitive load for reasoning about
future steps in the local reason-act-observe loop [39]. As a result,
planning is commonly used in agentic frameworks, usually encoded
as step-by-step instructions in the system prompt [1, 4, 28, 34]. For
example, a plan for fixing GitHub issues will instruct the agent to
navigate to a potential bug location (based on the issue description),
reproduce the bug to ensure correct localization, patch the bug, and
validate the patch’s correctness.
In practice, the plan is onlyadvisoryand without enforcement.
At each trajectory step, the model performs local reasoning over its
current context, and its actions may or may not align with the plan.
As the trajectory grows and the context fills with error messages,
file contents, and prior reasoning, the plan’s influence may dimin-
ish, consistent with the known limitations of LLMs in attending
to earlier context [20]. Therefore, whether agents truly follow the
instructed plan remains an open question. Evaluating plan com-
pliance can reveal whether the agent accomplishes a task through
correct strategic reasoning or through overfitting to benchmark
trajectories or data contamination.
This paper presents a large-scale evaluation of plan compliance
in programming agents. The analysis leverages a novel plan compli-
ance metric, measured across three dimensions: Plan Phase Compli-
ance, Plan Order Compliance, and Plan Phase Fidelity (§2). We evalu-
ate 21,120 SWE-agent trajectories, generated to resolve instances of
two popular benchmarks (SWE-bench Verified [6] and SWE-bench
Pro [8]), using four backbone LLMs (GPT-5 mini, DeepSeek-V3,
DeepSeek-R1, and Devstral-small), under eight plan settings: the
standard navigate-reproduce-patch-validation plan, no specified
plan, and six variations of the standard plan, obtained by remov-
ing, adding, and re-ordering plan phases. Our study answers the
following research questions:
arXiv:2604.12147v3  [cs.SE]  7 Aug 2026
