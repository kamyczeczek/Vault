---
type: Concept
id: 04_enhancing_llm_based_agents_via_global
title: "Enhancing LLM-Based Agents via Global (part 5/13)"
source: "Enhancing LLM-Based Agents via Global.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Compared to existing methods, GoalAct tightly integrates global planning with
execution through the continuously updated global plan. By dynamically adjusting
the plan based on real-time feedback, it ensures both a coherent overall strategy and
practical executability, ultimately enhancing the agents across diverse scenarios.
3.2 Hierarchical Execution
To reduce the complexity of considering executable actions within global planning and
to enable the agent to flexibly adapt its action complexity based on task difficulty,
we introduce a hierarchical execution framework. As stated in section 1, we argue
that existing single-stage execution methods struggle to manage real-world action
complexity, as they require agents to simultaneously determine appropriate skills or
techniques, select tools and configure them. Inspired by human action processes—first
identifying necessary skills, then selecting appropriate tools, and finally fine-tuning
execution parameters—our framework firstly structures execution into distinct skills,
allowing global planning to focus on high-level skills rather than low-level details, while
maintaining flexibility and extensibility, thereby ensuring a well-organized execution
process and enhancing the agents. Next, we will introduce several representative skills:
Searching: This skill primarily functions as a tool invocation mechanism for infor-
mation retrieval, utilizing a text or json formats similar to the ReAct. Its key advantage
lies in its simplicity and stability in complex external environments, where simpler
probing strategies tend to be more effective, as they facilitate error analysis and behav-
ioral refinement. However, its major limitation is its restricted expressiveness, as it
cannot handle complex tool calls or data processing logic, such as conditional branches
and loops. Nevertheless, this approach remains valuable in some simpler scenarios.
Coding: This skill leverages python code to invoke tools and process data. Its
strength lies in its ability to efficiently implement complex logic, including branch-
ing and looping, thereby expanding the agent’s action space and enhancing execution
efficiency. However, this increased action space comes at the cost of greater complex-
ity. While ongoing research [20] aims to enable agents to generate more robust code,
external environments remain inherently unpredictable, and even the most sophisti-
cated code can produce unforeseen bugs. In such cases, a simpler Searching approach
often serves as a more effective exploration method.
W riting: In real-world applications, many specialized tasks , which involve specific
and intricate logic, cannot be effectively addressed through either Searching or Coding.
For example, writing legal documents typically requires gathering legal articles, legal
knowledge, and similar cases, followed by composing a preliminary draft and finally
structuring the output according to specific format requirements. In such scenarios,
although coding excels in handling complex branching and conditional logic, it does
not directly contribute to completing the task.
Beyond these skills, expanding the skill pack according to task-specific require-
ments is essential. For instance, reasoning tasks may require specialized reasoning
skills, scientific research tasks may demand research skills, and artistic creation tasks
may call for creative skills. Notably, this expansion process is easy and highly iterative,
enabling continuous adaptation and refinement to meet evolving task demands.
5
