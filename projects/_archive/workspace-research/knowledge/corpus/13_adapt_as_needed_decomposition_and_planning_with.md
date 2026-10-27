---
type: Concept
id: 13_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 14/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Method Pick Clean Heat Cool Look Pick2 All
ReAct 66.7 41.9 47.8 80.9 83.3 23.5 56.7
Plan-and-Execute 87.5 58.1 73.9 52.4 83.3 17.6 63.4
Try Again with ReAct 75.0 38.7 60.9 76.2 66.7 23.5 56.7
Reflexion 83.3 61.3 73.9 85.7 61.1 29.4 67.2
ADAPT (Ours) 91.7 67.7 78.3 81.0 100 64.7 79.8
Table 6: Comparison of success rates (%) achieved by ADAPT
and other baselines from prior work on ALFWorld (test split)
with executor used by Yao et al. (2023b)
Method Score Success Rate
Iterative Executor-Only 42.1 29.0
Static Decomposition 27.7 17.0
Retry Execution 45.4 30.0
Naive 58.3 24.0
Reflexion* 64.2 35.0
LATS (Zhou et al., 2023)* 75.9 38.0
ADAPT (Ours) 60.0 44.0
Table 7: Performance comparison of differ-
ent methods on WebShop.
Algorithm 1 Algorithm for ADAPT
1: function ADAPT(Task T , Current depth k)
2: // ADAPT(·) Generates success heuristic value
completed for the task T . Initialized with k = 1.
3: // Base case: terminate on reaching maximum depth
4: if k > dmax then return F alse
5: // Execute the task/sub-task to assess if the LLM can
directly perform it using LLM-generated success.
6: completed ← executorLLM (T )
7: // Plan only when the executor fails.
8: if completed is F alsethen
9: // Using the LLM, decompose the task into a set
of sub-tasks, P, and a Boolean function,logic(·),
that combines output of the sub-tasks.
10: P, logic← plannerLLM (T )
11: // Get the outputs for individual sub tasks
12: O = {ADAPT(Tsub, k+1)|Tsub ∈ P}
13: // Combine the outputs of the sub tasks
14: completed ← logic(O)
15: return completed
run to subsequent calls of the executor. Note that
information is only propagated from successful
sub-tasks. For sub-tasks connected via “ OR”,
each receives the same information from the con-
troller. Unlike Shinn et al. (2023), executor does
not get text feedback from prior failures.
• WebShop: We propagate the current page vis-
ible to the agent along with past unsuccessful
executor tasks to the planner (without any ratio-
nales). Once we find a matching product, we also
propagate the product ID in future executor calls.
• TextCraft: We propagate the current inventory
of the agent to the executor. This is akin to ex-
ecutors starting with the inventory command
as the first step to keep stock of which items are
missing and need to be fetched or crafted.
For partial rolled-out trajectories with ADAPT re-
fer to Figs. 9 to 11. Communication between plan-
ner and executor is highlighted in gray box(es) .
LLM-related Hyperparameters. Following pre-
vious works (Shinn et al., 2023; Liu et al., 2023)
we use text-davinci-003 from the OpenAI
API for ALFWorld. For WebShop, we use the
gpt-3.5-turbo models, and for TextCraft we use
the gpt-3.5-turbo-instruct models. All execu-
tors have a maximum budget of iterations to inter-
act with the environment and execute the task. We
set this budget to 20, 15, and 20 respectively for
ALFWorld, WebShop, and TextCraft respectively.
For try again with ReAct, we sample additional tra-
jectories with a temperature of 0.7. As discussed in
Sec. 4.2, we run the iterative executor-only baseline
for 60, 45, 60 iterations for ALFWorld, WebShop,
and TextCraft respectively. In Sec. 6.2, we use pub-
licly available checkpoints for LLaMA 70B7 and
Lemur 70B8 available on Huggingface (Wolf et al.,
2019). For both planner and executor modules, we
use a fixed prompt consisting of few in-context
examples (as described above) for each dataset.
We show all executor and planner prompts to the
LLM in Appendix G. Due to cost constraints, we
report success rates for a single run of each LLM
in Secs. 5 and 6.
B Handling Complex Logic in Plans
While the examples in Figs. 1 and 2 show homoge-
neous logic across sub-tasks in the plan, our con-
troller can handle complex logical expressions in-
cluding both “AND” and “OR” operators. Specif-
ically, we provide instructions to the planner to
output this logical expressing at the end of the plan
with a fixed prefix: Execution Order . We then
build a deterministic parser that can parse complex
logical expressions that the controller can process.
We do so by splitting the logical expression into a
series of homogeneous expression each passed to
ADAPT. Whenever the task given toADAPT com-
prises of multiple sub-tasks connected via (one)
logical operator, we automatically decompose this
task as per the logical expression. For example,
in Fig. 8, a detailed plans used by the plan-and-
execute baseline (discussed in Sec. 4.2) comprised
7https://huggingface.co/meta-llama/
Llama-2-70b-hf
8https://huggingface.co/OpenLemur/
lemur-70b-chat-v1
14
