---
type: Concept
id: 05_enhancing_llm_based_agents_via_global
title: "Enhancing LLM-Based Agents via Global (part 6/13)"
source: "Enhancing LLM-Based Agents via Global.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

T able 1Detailed Statistics of LegalAgentBench Tasks.
Attribute 1-hop 2-hop 3-hop 4-hop 5-hop Writing ALL
# Task 80 80 60 40 20 20 300
Avg. length per query 88.29 87.90 99.37 118.33 110.25 1059.95 160.65
Avg. length per answer 74.20 40.84 45.53 63.48 86.20 678.75 99.24
# Avg. key answer per query 1.88 1.44 1.20 1.40 2.25 10.25 2.14
Avg. length of key answer 10.59 5.94 6.07 6.59 6.93 12.58 9.28
# Avg. key middle per query 0.13 1.45 2.87 4.78 5.60 6.20 2.42
Avg. length of key middle 9.20 9.72 10.95 11.35 11.25 7.21 10.24
4 Experiment
4.1 Experimental Setup
4.1.1 T asks Selection
To validate the effectiveness of GoalAct, it is essential to ensure the reliability of the
evaluation benchmark. However, existing well-known datasets may have already been
used in training, posing a risk of data leakage. Moreover, we aim to assess the agent’s
performance in an unfamiliar environment. Therefore, we select LegalAgentBench
[12] as our benchmark. As a newly released dataset, it eliminates the risk of data
leakage while covering a comprehensive range of task difficulties. Additionally, solving
its tasks requires external data and legal knowledge, making it a suitable and robust
test for the capabilities of agents.
The data in LegalAgentBench has been meticulously verified by human experts
and includes a total of 300 tasks across six different types . Table 1 presents
the detailed statistics of these tasks. Among them, 1-hop to 5-hop tasks represent
logical reasoning problems with varying solution path lengths, where a higher hop
count indicates increased task complexity. Beyond logical reasoning tasks, the dataset
also features a writing category, specifically writing a defense document . In this
scenario, the agent must query basic information about the plaintiff, defendant, and
their lawyer, while simultaneously retrieving relevant legal knowledge and relevant
articles to construct a defense against the complaint.
4.1.2 Baselines
We evaluated three well-known LLMs on LegalAgentBench: GLM-4-Plus [13], Qwen-
max [15], GPT-4o-mini [22] (gpt-4o-mini-2024-07-18). All LLMs are evaluated through
API calls. To ensure the reproducibility of the results, we set the temperature to 0.
For each LLM, we implemented four different methods. (1)Plan-and-Solve: Out-
line a complete plan and execute it step by step. (2) Plan-and-Execute: Develop a
multi-step plan and complete it sequentially. After completing a task, the LLM can
reassess the plan and make appropriate adjustments. (3) ReAct: Perform reasoning
incrementally through the “thought-action-observation” process, integrating reason-
ing and tool usage. (4) CodeAct: Utilize Python code as the agent’s action space,
enabling the invocation of multiple tools within a single execution.
6
