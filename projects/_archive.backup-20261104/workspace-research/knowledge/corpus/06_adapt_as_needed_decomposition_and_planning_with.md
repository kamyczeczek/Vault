---
type: Concept
id: 06_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 7/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

1 2 3
Value of dmax in ADaPT
20
40
60Success Rate
ALFWorld WebShop T extCraft
Figure 4: Success rate of ADAPT increases with the
maximum depth dmax for all datasets (dev splits).
yields 14.1% points higher overall success rate
than Reflexion, despite the latter having access
to dedicated memory and natural language feed-
back. Specifically, we find baselines yield poor
results on ‘pick2’ tasks ( < 12% success rate) as
they require the agent to compose two ‘pick’-style
tasks involving a longer action history. However,
ADAPT yields significant improvements (by over
a factor of 4×) for this type of tasks.
WebShop. Table 2 shows a similar trend with
ADAPT surpassing all baselines and achieving
the highest success rate. ADAPT outperforms Re-
Act, Plan-and-Execute, and Try-Again baselines
by up to 27% points. We corroborate the findings
of Shinn et al. (2023) and observe that natural lan-
guage feedback offers limited gains in performance,
as compared to ADAPT (which surpasses Reflex-
ion by 9% points). Additionally, we compare with
a recent search-based baseline LATS (Zhou et al.,
2023) and find that ADAPT outperforms the suc-
cess rate of LATS by 6% points.
TextCraft. Our results on TextCraft are summa-
rized in Table 2. First, we observe that ADAPT
achieves an improvement of 33% compared to the
ReAct executor. In contrast to Plan-and-Execute,
i.e., starting with a fixed plan, having the dynamic
ability to adapt to complex sub-tasks (in this case,
crafting complex ingredients) in ADAPT improves
performance by 25% points. Lastly, ADAPT out-
performs Reflexion by 20% points, highlighting
the importance of adaptive and as-needed planning.
We hypothesize that ADAPT consistently outper-
forms Reflexion across datasets as the latter relies
on generating feedback based on errors in the entire
trajectory. In contrast, due its design, ADAPT of-
ten handle failures of small sub-tasks and redirects
more resources in the form of calling the planner
T ask-Specific Hybrid Atomic
Executor Setting
0
20
40
60Success Rate
Executor-Only ADaPT (dmax=3)
Figure 5: ADAPT improves success rates across varying
settings capturing different executor capabilities (i.e.,
executor-only performance) on ALFWorld (dev).
and decomposition to the challenging sub-tasks.
6 Analysis and Discussion
We analyze ADAPT in detail by addressing the
following research questions on dev data splits.
6.1 How does performance of AD APT scale
with the depth of decomposition?
Setup. To assess the impact of adaptive decom-
position, we study ADAPT under three settings
with increasing maximum depth dmax ∈ {1, 2, 3}
for ALFWorld, WebShop, and TextCraft. Note
that dmax = 1setting corresponds to the iterative
executor-only baseline (ReAct).
Results. Fig. 4 shows that across all datasets, per-
formance of ADAPT scales with increasing the
maximum depth dmax. Consistently, we find a sig-
nificant improvement in success rates as we move
from dmax = 1to dmax = 2, i.e., adding the planner
to decompose a complex task when executor fails
proves to be effective. Finally, the performance
increase from dmax = 2to dmax = 3validates our
hypothesis that some sub-tasks are difficult for the
LLM to directly execute successfully, and decom-
posing these further boosts overall performance.
6.2 Does AD APT cater to different execution
capabilities of LLMs?
Same LLM, different execution capabilities.
We run ADAPT on three different executor
prompts on ALFWorld: (i) task-specific gold tra-
jectories, (ii) atomic skills and common gold-
trajectories for 2 tasks used in Sec. 5 (hybrid), and
(iii) only atomic skills. Using gold trajectories
aligns closely with the task at inference-time and
thus, should exhibit high performance. In contrast,
7
