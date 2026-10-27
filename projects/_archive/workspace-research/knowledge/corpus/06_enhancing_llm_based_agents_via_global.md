---
type: Concept
id: 06_enhancing_llm_based_agents_via_global
title: "Enhancing LLM-Based Agents via Global (part 7/13)"
source: "Enhancing LLM-Based Agents via Global.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

T able 2The success rate of different methods on LegalAgentBench. P-S represents the Plan-and-Solve
method, and P-E represents the Plan-and-Execute method. The best results are highlighted in bold.
Model Method 1-hop 2-hop 3-hop 4-hop 5-hop Writing ALL
GPT-4o-mini
P-S 0.7117 0.3375 0.2750 0.2583 0.1250 0.6314 0.4196
P-E 0.7444 0.3771 0.3250 0.2417 0.1417 0.6681 0.4503
ReAct 0.9333 0.6500 0.4000 0.4208 0.2583 0.6087 0.6161
CodeAct 0.9058 0.7938 0.4167 0.3875 0.1683 0.4202 0.6275
GoalAct 0.9556 0.8771 0.6250 0.5625 0.4517 0.7981 0.7720
Qwen-max
P-S 0.8469 0.4958 0.4083 0.3792 0.2333 0.4836 0.5381
P-E 0.8594 0.5896 0.3583 0.4083 0.3017 0.5539 0.5695
ReAct 0.9062 0.7917 0.6333 0.5833 0.6083 0.6662 0.7422
CodeAct 0.8442 0.8583 0.6333 0.7583 0.5117 0.6522 0.7594
GoalAct 0.9531 0.9062 0.8167 0.7917 0.6117 0.8220 0.8603
GLM-4-Plus
P-S 0.8519 0.4667 0.4167 0.3583 0.1167 0.7522 0.5406
P-E 0.8419 0.5000 0.3667 0.3458 0.1167 0.7679 0.5363
ReAct 0.9131 0.8104 0.6417 0.6167 0.4300 0.7659 0.7499
CodeAct 0.9221 0.7812 0.4167 0.5458 0.2333 0.5836 0.6648
GoalAct 0.9506 0.9187 0.8500 0.7375 0.6983 0.8643 0.8710
When given a task, the model first determines which tools are needed, and then
uses the selected tools to gradually solve the task. When the LLM outputs Finish or
reaches the maximum iteration limit T = 10, it summarizes the current trajectory
and provides the final answer. We include two examples for each process to guide the
model in using the tools and following the specified output format.
4.1.3 Metrics
We use Success Rate as the metric, which measures the proportion of key answer
elements included in the LLM’s output. Assume a dataset D consisting of N data
points, where each data point includes a keyword set Ki and a model output Oi. The
success rate si for the i-th data point is computed as Equation 4 shows:
si = |Mi|
|Ki| (4)
where Mi = {k ∈ Ki | k appears in Oi}. The notation | · |represents the number of
elements in a set. We report the average success rate across all tasks in the results.
4.2 Experimental Results
4.2.1 Main Results
Table 2 presents the results of different methods on LegalAgentBench, from which we
draw the following conclusions:
• GoalAct achieves SOT A performance across different LLM series and
varying task difficulties. Compared to the second-best method, GoalAct
7
