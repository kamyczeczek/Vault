---
type: Concept
id: 03_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 4/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

[LLM] Think:  Input assumption: I am carrying a
mug. Now I need to verify this.
[LLM]> inventory
[LLM]> go to sinkbasin 1
[LLM]> clean mug 1 with sinkbasin 1
[LLM] Think: I cleaned the mug.Task completed!
ADaPT(Task, k)
Executor(Task)
Success?
Planner(Task)
Step 2
Step 1
Step 3
ADaPT(Step1,k+1)
ADaPT(Step2,k+1)
ADaPT(Step3,k+1)
Task: Put a clean mug on desk
True
False
Logic
True
False
Clean the mugExecutor(           )
OK.
You are carrying: a mug 1
You reached loc 13, you see ...
You clean mug 1
# Think: To do this task, I first need to find a
mug, then clean, it and put it on the desk. I
need to perform these tasks sequentially.
Step 1: Find and take a mug AND
# Think: Now I found a mug, I will clean it.
Step 2: Clean the mug with sinkbasin AND
# Think: Now I cleaned the mug, I will put
the clean mug on the desk.
Step 3: Put clean mug on desk
 LLM
Planner(           )Put a clean
mug on desk
Controller
AND
Figure 2: Block diagram of the ADAPT pipeline with an example from ALFWorld. Left: Use of LLM as an
executor to interact iteratively with the environment along with an example execution trajectory.Middle: Overall
recursive algorithm (depth k ≤ dmax) that embeds the executor and planner, refer to Algorithm 1 for details. Right:
Outline of using LLM as a planner to generate sub-tasks (steps) and logical operators combining them.
skill). An advanced executor could combine “find-
ing a mug” with the “cleaning” skill to accomplish
“find a clean mug” without an explicit planner.
Self-generated Success Heuristic. In order to
decompose based on the abilities of the executor,
we need to determine whether the executor is capa-
ble of finishing the given (sub-)task independently
or if further decomposition is required. To this
end, we employ the executor LLM to determine
the completion of the (sub-)task without relying
on the environment for obtaining gold rewards for
(sub-)tasks. We include a simple instruction in the
executor prompt to output“task completed” if it de-
termines it has succeeded, otherwise output “task
failed” in case it cannot proceed. Refer to example
in Fig. 2 (left). Our success heuristic aligns with bi-
nary classification models employed in Shinn et al.
(2023), providing a way to simulate intermediate
rewards, which complements end-of-task environ-
ment rewards (Rengarajan et al., 2022). We study
this LLM-generated heuristic in Appendix F and
show that it closely matches the gold reward.
3.2 LLM as a Planner
Overview. The objective of the planner is to
break down complex tasks into smaller sub-tasks.
To achieve this, we instruct the LLM to generate
a concise yet comprehensive plan consisting of a
few steps, typically 3-5, as shown in Fig. 2 (right).
We opt for shorter, more abstract plans because ex-
pecting a detailed, fine-grained plan upfront can be
impractical, especially in unexplored environments.
E.g., devising a 10-step plan to put a clean mug
on a desk without prior knowledge of the mug’s
location can lead to cascading errors due to incor-
rect assumptions. Therefore, we task the LLM to
generate short plans, with the flexibility to decom-
pose further in subsequent iterations, based on the
executor’s capabilities.
Composition Logic for Sub-tasks. Along with
the sub-tasks, we prompt the planner to generate
logical operators to combine various sub-tasks in
the plan to accomplish the task. We allow for two
logical operators: “ AND” and “ OR”. Sub-tasks
are linked using AND when they must be executed
sequentially for the task to succeed. However, in
cases requiring exploration, such as finding an item
in an unknown room, we employ the OR operator
to simulate conditional checks. Here, the task suc-
ceeds if any of the sub-tasks are successful. For
instance, in Fig. 1, the plan to “find a mug” would
be to “find a mug on the countertop” OR “find a
mug in the cabinet” . We execute the latter only
if the agent has not found the mug yet. While ex-
amples in Figs. 1 and 2 show homogeneous logic,
ADAPT can handle complex logical expressions
as described in Appendix B.
3.3 Controller – LLM Program
Overall Pipeline. Thus far, we describe two
LLM-based modules that can perform the roles
of low-level execution and high-level planning. We
incorporate these modules into ADAPT via the
controller which is a pre-determined and recursive
algorithm – making the overall pipeline of ADAPT
an LLM program (Schlag et al., 2023; Dohan et al.,
2022), shown in Algorithm 1. The overall flow of
the controller program is as follows: (i) given an
input task, the controller calls the executor to check
if it can succeed in performing the task directly; (ii)
4
