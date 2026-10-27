---
type: Concept
id: 18_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 19/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

AlfWorld WebShop T extCraft
0
20
40
60
80Success Rate
Gold Environment Reward
Self-generated Success Heuristic
Figure 12: Comparison of LLM-generated success
heuristic with gold environment rewards to compute
success rates for all datasets.
able context size. Note that we do not provide the
list of valid get commands as that can be inferred
from the craft commands.
F Evaluation of Success Heuristic
In Sec. 3.1, we describe the executor module used
in ADAPT. For tasks assigned to the executor,
we prompt the LLM to generate a binary success
heuristic. We use this heuristic repeatedly to evalu-
ate if the (sub-)task needs to be decomposed further.
We now study the ability of LLMs to generate this
success heuristic on all our datasets. To this end,
we run ADAPT and in the end compare the success
rate when using the LLM’s self-assessed task suc-
cess with the gold reward from the environment in
Fig. 12. On ALFWorld and TextCraft, we find the
LLM slightly over-estimates its overall task suc-
cess. This is to be expected as the underlying tasks
involve minimal subjectivity (e.g., the agent either
has an item on its inventory or not). However, on
WebShop, where a product can match the user crite-
ria to different degrees (partially or fully), we find
that the LLM’s assessment is significantly inflated
compared to the environment reward (> 30 points).
This imperfect feedback affects downstream per-
formance of ADAPT, as the algorithm terminates
even though further decomposition is needed. We
leave it to future work to address the shortcomings
of self-evaluation with LLMs (Huang et al., 2023a;
Stechly et al., 2023).
G Prompts
We provide all the prompts used in our planner and
executor modules for ALFWorld, WebShop, and
TextCraft datasets in the following pages.
18
