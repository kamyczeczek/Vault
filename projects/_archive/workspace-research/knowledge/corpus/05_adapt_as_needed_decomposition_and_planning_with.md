---
type: Concept
id: 05_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 6/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Method (dmax = 3) Pick Clean Heat Cool Look Pick2 All
ReAct 33.3 67.7 43.5 33.3 55.6 11.8 43.3
Plan-and-Execute 29.2 61.3 47.8 38.1 61.1 11.8 43.3
Try Again with ReAct 50.0 51.6 60.8 47.6 61.1 5.9 47.8
Reflexion 70.8 61.3 61.0 66.7 61.1 5.9 57.5
ADAPT (Ours) 87.5 80.6 60.8 76.2 61.1 52.9 71.6
Table 1: ADAPT yields the highest the overall success rates (%)
compared to baselines from prior work (discussed in Sec. 4.2) on
ALFWorld (test split). Best (highest) success rates are highlighted
in bold and second-highest rates are underlined.
Method WebShop TextCraft
ReAct 32.0 19.0
Plan-and-Execute 17.0 27.0
Try Again with ReAct 30.0 15.0
Reflexion 35.0 † 32.0
LATS (Zhou et al., 2023) 38.0 † −
ADAPT (Ours) 44.0 52.0
Table 2: ADAPT yields the highest success
rate on WebShop and TextCraft (test split) with
dmax = 3 and 4 respectively. †Performance
reported by Zhou et al. (2023)
items with recipe tree depth of 3 (123 tasks), depth
of 4 (11 tasks) and depth of 2 (77 out of 297) in
our test set, and the rest of depth 2 tasks constitute
the dev set. Additional details about creating the
environment are present in Appendix E.
4.2 Baseline Approaches
We compare ADAPT with four classes of baseline
approaches described below.
Iterative Executor-Only (ReAct). In this setting,
we employ the executor to interact iteratively with
the environment, adopting the think-act-observe
prompting style from ReAct (Yao et al., 2023b). All
methods discussed below, includingADAPT, share
the same executor, ensuring a standardized impact
of the executor’s strength and design choices when
comparing relative performance in Sec. 5. When
dmax = 1, ADAPT solely relies on this executor.
Plan-and-Execute. As shown in Fig. 1, in this
setting, we generate a plan first and then assign
each sub-task to the executor. This approach only
plans once and as a result has a non-adaptive struc-
ture (consistent with Wang et al. (2023b); Yang
et al. (2023); Sun et al. (2023)). To ensure each
plan step is executable without further decompo-
sition, we design new prompts with more detailed
plans. Note that ADAPT with dmax = 2 differs
from plan-and-execute as it is adaptive, i.e., de-
composes only when executor fails and generates
relatively shorter plans (refer to Appendix B).
Try Again with ReAct. By design, ADAPT
makes multiple calls to the executor module, al-
beit with different (sub-)tasks. Like Yang et al.
(2023), we design a simple controller that requests
the executor to retry the task in a total of dmax
separate trials and then uses the trial with the best
performance for each task instance.
Reflexion. Shinn et al. (2023) execute the en-
tire task first, and if unsuccessful, reflect and store
feedback in memory for subsequent dmax −1 trials.
While adaptive, this approach repeats the entire
trial even if a single sub-task fails, redundantly
re-executing previously successful sub-tasks.
ADAPT and Shared Implementation Details.
Following (Yao et al., 2023b; Shinn et al., 2023;
Zhou et al., 2023), by default, we use the GPT-
3.5 (Ouyang et al., 2022) LLM for both planning
and execution in ADAPT and other baselines. We
use the completion-based models for ALFWorld
and TextCraft and the chat-based model for Web-
Shop.5 Further, we use ADAPT (and other base-
lines) with dmax = 3for ALFWorld, and WebShop
and increase to dmax = 4for TextCraft to accommo-
date recipes with a depth of 4 (Sec. 4.1). For addi-
tional details, refer to Appendix A. We increase the
maximum number of iterations for the ReAct base-
line by a factor of dmax and ensure all baselines
use a comparable number of LLM calls (Sec. 6.5).
5 Main Results
Using GPT-3.5 as the underlying LLM, in this sec-
tion, we show that ADAPT yields the highest suc-
cess rate compared to baselines from prior work on
ALFWorld, WebShop, and TextCraft datasets.
ALFWorld. In Table 1, we observe that ADAPT
achieves the highest overall success rate , while
using ReAct alone results in the lowest overall
performance. By leveraging adaptive decomposi-
tion, ADAPT improves over ReAct’s performance
by 28.3% points (absolute) as well as over Plan-
and-Execute and Try Again by 28.3% and 23.8%
points, respectively. Lastly, we find that ADAPT
5We use the completion model as chat variants of GPT-3.5
consistently underperform their completion counterparts (Liu
et al., 2023; Yang et al., 2023). We discuss the effectiveness
of ADAPT different LLMs in Sec. 6.2.
6
