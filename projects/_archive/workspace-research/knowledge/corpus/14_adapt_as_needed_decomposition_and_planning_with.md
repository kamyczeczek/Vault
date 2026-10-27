---
type: Concept
id: 14_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 15/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Plan: Put a clean mug on desk
# Think: To do this task, ....
Step 1: Find and take the mug AND
# Think: Now that I have found it, ....
Step 2: Clean the mug using sinkbasin AND
# Think: Now that I have cleaned ....
Step 3: Put clean mug on desk
Plan: Find and take the mug
# Think: To do this task, ....
Step 1: Find and take mug from countertop OR
# Think: If I do not find the mug, ....
Step 2: Find and take mug from cabinet OR
# Think: If I do not find the mug, ....
Step 3: Find and take mug from drawer
Plan: Put a clean mug on desk
# Think: To do this task, ....
Step 1: Find and take mug from
countertop OR
# Think: If I do not find the mug, ....
Step 2: Find and take mug from cabinet OR
# Think: If I do not find the mug, ....
Step 3: Find and take mug from drawer AND
# Think: Now that I have found it, ....
Step 4: Clean the mug using sinkbasin AND
# Think: Now that I have cleaned ....
Step 5: Put clean mug on desk
Logic: ((Step 1 OR Step 2 OR Step 3) AND
Step 4 AND Step 5)
Adaptive Multi-level Plans in ADaPT
Detailed Plans in Plan-and-Execute
Figure 8: Illustration of how multiple levels of plans
from ADAPT, can be collapsed into one detailed plan
in non-adaptive settings as used in the plan-and-execute
baseline (Sec. 4.2). Our controller can handle complex
(non-homogeneous) logical expressions.
of logical expressions using both AND, and OR
operators. Therefore, the parser will break auto-
matically break this into multiple levels, i.e., Step
6 = Step 1 OR Step 2 OR Step 3, followed by Step
6 AND Step 4 AND Step 5. While such complex
logical expressions are mostly associated with the
plan-and-execute baseline, they can be easily used
within the ADAPT framework. Furthermore, this
allows the plan-and-execute baseline to simulate
a multi-level planning structure via detailed plans
without being adaptive to the executor.
C Task-specific Executors in ALFWorld
In Table 1, we use a standardized executor with
in-context demonstrations of atomic skills and two
gold trajectories. While this allows for a common
executor across different sub-tasks, task-specific
executors yield higher performance on the specific
sub-tasks. We now show ADAPT can also be used
on top of task-specific executors used by Yao et al.
(2023b). The results are shown in Table 6. First,
Method #Products Success Rate
ReAct 3 27.5
ADAPT (dmax = 3) 3 47.5
ReAct 10 20.0
ADAPT (dmax = 3) 10 42.5
Table 8: ADAPT improves WebShop (dev) performance
irrespective of how many products (3 or 10) are chosen
from the search page.
we observe that ADAPT yields the overall success
rate by up to 23.1% points and also surpasses base-
lines on all but 1 task types. Interestingly, we find
strong performance of the plan-and-execute base-
line when using a stronger executor (as compared
to Table 1) possibly as such an executor can handle
complex sub-tasks better. Consistent with Table 1,
ADAPT outperforms Reflexion by 12.6% points
despite lack of dedicated memory and natural lan-
guage feedback.
D Additional WebShop Experiments
Evaluation Metrics. We focus on success rate
and not the (soft) score as the primary metric for
this task because it is possible to get a non-zero
score by naively buying a product. To this effect,
we construct a naive executor that inputs the user
query in the search bar and buys the first available
product. Table 7 shows that while this baseline
yields the lowest success rate, it surprisingly yields
a high success rate of 58.3. In contrast, our ex-
ecutors often do not buy products especially when
the previous sub-goals fail which can adversely im-
pact scores even though the success rate remains
unaffected. Therefore, we argue for optimizing the
success rate instead of the score as opposed to prior
works (Zhou et al., 2023).
ADAPT accommodating task complexity. By
default, Yao et al. (2023b) use a search page with
only the top-3 search results displayed. Intuitively,
increasing the number of products on the search
page requires the model to choose from a wider
array of products and track all their information to
determine the best fit to the user query, making the
overall task harder. Therefore, we apply ADAPT
on Webshop in two settings with 3, and 10 products
per search page.
Results. From Table 8, we observe that ADAPT
effectively improves success rate by 20.0% and
22.5% for 3 and 10 products respectively over the
15
