---
type: Concept
id: 01_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 2/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

> Go to countertop 1.
You reached loc 1...
> Go to cabinet 12.
...
> Think: Mug not found.
Task failed!
You reached loc 20 ...
Iterative Executor (ReAct)
Plan:
Step 1: Find and
take the mug AND
Step 2: Clean the
mug AND
Step 3: Put the
clean mug on desk
Plan-and-Execute
   ADaPT (Recursive Decomposition, As-needed)
Task: Put a clean mug on desk.
Not Executed
Execute: Task
Plan:
Step 1: Find and take the mug AND
Step 2: Clean the mug AND
Step 3: Put the clean mug on desk
Execute: Step 1
Plan:
Step 1a: Find and take the mug from countertops OR
Step 1b: Find and take the mug from cabinets OR
Execute: Step 1a
Execute: Step 1b
Execute: Step 3
Execute: Step 2
 ...
On execution failure,
decompose further
Successful sub-task allows
execution to resume
Execute:
Step 1
Execute:
Step 2
Execute:
Step 3
OR
ADaPT(Task)
ADaPT(Step1)
Figure 1: Top-Left: Iterative executors such as Re-
Act (Yao et al., 2023b) interact directly with the envi-
ronment, performing planning implicitly. Top-Right:
Plan-and-Execute, e.g., Yang et al. (2023), creates a
fixed plan for the task, without accounting for complex-
ity in executing step 1. Bottom: ADAPT dynamically
decomposes based on success of the executor.
household is too complex for the model, leading to
failure of the iterative executor. While a plan-and-
execute-style approach initially breaks down the
task into three sub-tasks, it falls short in accounting
for the complexity in finding a mug. Moreover, it is
challenging to anticipate the difficulty of such a sub-
task in advance, as the executor could find a mug
in the first attempt or in an obscure location. There-
fore, ADAPT employs its recursive structure to
dynamically adapt to execution failures (assessed
by LLMs), by further decomposing the complex
sub-task of finding a mug via the planner.
Empirically, we demonstrate the effectiveness
of ADAPT on three datasets involving interactive
environments: ALFWorld (Shridhar et al., 2021),
WebShop (Yao et al., 2022), and a new compo-
sitional text game for crafting Minecraft recipes
called TextCraft (Sec. 4.1). Using GPT-3.5 as the
underlying LLM, ADAPT outperforms strong base-
lines (discussed in Sec. 4.2) such as ReAct (Yao
et al., 2023b), and Plan-and-Solve (Wang et al.,
2023b) by up to 28.3%, 27%, and 33% absolute
points on ALFWorld, WebShop, and TextCraft re-
spectively (Sec. 5). Compared to Reflexion (Shinn
et al., 2023), an adaptive approach that addresses
failures in the full task trajectory, ADAPT yields
higher success rates by 14.1%, 9%, and 20% on
ALFWorld, WebShop, and TextCraft respectively.
Through extensive analysis of ADAPT, we es-
tablish the importance of recursive decomposi-
tion (Sec. 6.1) and showcase dynamic adaptation
to the capabilities of the executor LLM includ-
ing open-source models such LLaMA-2 (Touvron
et al., 2023) and Lemur (Xu et al., 2023) in Sec. 6.2.
Lastly, we demonstrate that ADAPT incorporates
task complexity (Sec. 6.3), where the extent of re-
cursive decomposition aligns with the inherent task
complexity. To summarize, our contributions are:
1. We present ADAPT, a recursive algorithm that
dynamically decomposes complex sub-tasks on
an as-needed basis, i.e., intervening only if the
task is too complex for the executor.
2. On three diverse datasets, ALFWorld, WebShop,
and TextCraft, ADAPT improves success rate
of GPT-3.5 over previous approaches by up to
28.3%, 27%, and 33% points respectively.
3. Analysis of ADAPT underscores the signifi-
cance of recursive decomposition and the ability
to adapt dynamically to varying LLM execution
capabilities and task complexities.
2 Related Work
LLMs for Decision-Making. LLMs have been
successfully used as agents to perform a wide vari-
ety of decision-making tasks such as robotic nav-
igation (Ahn et al., 2022; Huang et al., 2023b;
Singh et al., 2023), complex multi-modal games
like Minecraft (Fan et al., 2022; Wang et al., 2023a),
text-based environments (Shridhar et al., 2021; Liu
et al., 2023). While most of these works focus
on learning from trajectories, ReAct (Yao et al.,
2023b) uses few-shot prompting to build an agent
that reasons about the current state (thoughts) and
generates the next action in the environment, given
prior actions and observations. Their iterative ap-
proach (shown in Fig. 1; top-left) can handle fail-
ures, but they have to keep track of the entire plan
implicitly while deciding every local action (c.f.
ADAPT in Fig. 9 of Appendix A). By incorporat-
ing planning and execution into separate modules
and enabling dynamic adaptation we are able to
achieve higher success rates (refer to Sec. 5).
2
