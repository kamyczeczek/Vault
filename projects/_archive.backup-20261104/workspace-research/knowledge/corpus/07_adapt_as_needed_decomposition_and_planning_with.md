---
type: Concept
id: 07_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 8/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

AlfWorld WebShop T extCraft
20
40
60
80
100Success Rate
GPT-3.5 GPT-4 Lemur LLaMA with ADaPT
Figure 6: AD APT improves (test) performance of GPT-3.5, GPT-4, LLaMA, and Lemur LLMs across datasets.
executor using only atomic skills relies on the in-
herent composition abilities of the LLM, yielding
weaker performance. Here we examine if ADAPT
can improve success rates for all three settings.
Results. In Fig. 5, we observe that ADAPT con-
sistently improves over the executor-only baseline
for all diverse executor settings. As expected, the
executor prompted with task-specific trajectories
performs the best (left), while the executor with
only atomic skills performs the worst (right). No-
tably, ADAPT substantially improves performance
of the relatively weak executor, improving success
rate from 3.3% to 41.7%.
ADAPT with different LLMs. We study the
ability of ADAPT to improve performance across
different LLMs (as planners and executors): (i)
GPT-3.5, (ii) GPT-4 (OpenAI, 2023), (iii) LLaMA-
2 70B (Touvron et al., 2023), and (iv) Lemur
70B (Xu et al., 2023) on test splits of all datasets.
Results. Fig. 6 shows that ADAPT consistently
improves downstream performance for all models
across all three datasets. Consistent with Liu et al.
(2023), we find that the gated GPT models outper-
form the open-source models based on absolute
success rates. Nevertheless, ADAPT is effective
across LLMs and improves performance of GPT-
4, the strongest LLM, by up to 37%, as well as
LLaMA, the least performant LLM, by up to 15%
on the TextCraft dataset.
6.3 Does AD APT handle task complexity?
Setup. By the compositional design of TextCraft,
complexity of each task in the dataset can be de-
fined with respect to the depth of the crafting recipe,
i.e., recipes with higher depth would be more com-
plex to craft. We evaluate efficacy of ADAPT
and the ReAct baseline on the test set of TextCraft
Method Recipe Depth kmax Success Rate
ReAct 2 1.0 26.9
ADAPT (dmax = 4) 2 1.9 78.2
ReAct 3 1.0 1.8
ADAPT (dmax = 4) 3 2.8 38.7
Table 3: ADAPT improves TextCraft (test) performance
even as recipe depth increases. The maximum decom-
position depth used by ADAPT to succeed at the task
(kmax) also scales with the recipe depth.
with increasing recipe depth.6 Furthermore, while
we provide ADAPT with a maximum budget of
dmax = 4, we study how the maximum decompo-
sition depth utilized by ADAPT to succeed (kmax)
varies with task complexity.
Results. In Table 3 we observe that ADAPT im-
proves success rates for games with recipe depth of
2 from 26.9% to 78.2%, and of depth 3 from 1.8%
to 38.7% as compared to the ReAct baseline. As
expected, the executor alone is unable to handle
complex recipes with depth ≥ 3, but with the help
of ADAPT the performance improves significantly.
Additionally, given the same budget dmax = 4, as
the recipe depth (complexity) increases from 2 to
3, ADAPT’s level of decomposition ( kmax) also
increases from 1.9 to 2.8. This showcases that
ADAPT leverages as-needed decomposition in or-
der to handle task complexity.
6.4 Can we use different planner and executor
LLMs within ADAPT?
Setup. The planner and executor modules of
ADAPT do not need to necessarily use the same
underlying model. Following, Lin et al. (2023) we
explore if a relatively smaller LLM can be used to
perform local actions in the executor and a more
6As we have only 11 tasks with recipe depth of 4, we
exclude them from this analysis.
8
