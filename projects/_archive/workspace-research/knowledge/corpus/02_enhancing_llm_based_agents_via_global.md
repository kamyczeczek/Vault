---
type: Concept
id: 02_enhancing_llm_based_agents_via_global
title: "Enhancing LLM-Based Agents via Global (part 3/13)"
source: "Enhancing LLM-Based Agents via Global.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

require agents to simultaneously determine the appropriate skills or methods, select
relevant tools, and configure their parameters. Inspired by human practice—first
identifying high-level skills, then selecting suitable tools, and finally refining execu-
tion details—we propose a hierarchical execution framework that decomposes task
execution into distinct high-level skills, such as searching, coding, writing, reasoning
and more. This hierarchical structure offers two key advantages: (1) it significantly
simplifies global planning, as the plan only needs to specify appropriate high-level
skills and their objectives rather than low-level details; and (2) it is inherently scal-
able, enabling the dynamic addition and selection of skills to flexibly adapt to diverse
and evolving task scenarios.
To evaluate the effectiveness of GoalAct, we conducted experiments using LegalA-
gentBench [12], a novel benchmark that poses no risk of data leakage and requires
external tool invocation and legal knowledge for task completion. Experimental results
demonstrate that GoalAct achieves state-of-the-art (SOTA) performance, with an
average improvement of 12.22% in success rate.
2 Related Work
2.1 Large Language Models
Large Language Models (LLMs) have experienced rapid development in recent years,
significantly advancing natural language understanding and generation capabilities.
Models like ChatGLM [13, 14], Qwen [15] and GPT [4] demonstrate remarkable abil-
ities in language comprehension, multi-turn dialogue management, and instruction
following [4, 16]. Techniques such as contextual learning, in-context instruction tuning,
and chain-of-thought reasoning have enabled LLMs to handle complex reasoning tasks
more effectively [17–19]. These advances have led to LLMs being integrated into var-
ious downstream applications, from knowledge-based question answering to tool-use
scenarios, thereby driving the development of more sophisticated intelligent agents.
2.2 LLM-Based Agents
Leveraging the advancements of LLMs, researchers have built agents capable of rea-
soning, planning, and interacting within complex environments. Approaches such as
ReAct [7] combine reasoning and acting to allow agents to interact iteratively with
external tools, enhancing the agent’s factuality and problem-solving capabilities. Voy-
ager [20] introduces code-based action execution, enabling an LLM agent to operate
effectively within dynamic game environments by generating executable python code
to navigate and interact within Minecraft. Similarly, TaskWeaver [21] translates user
instructions into executable code for efficient task completion in structured data anal-
ysis environments. Other frameworks like CodeAct [8] emphasize tool integration,
enabling agents to leverage external coding environments for complex problem-solving
tasks, significantly enhancing their operational flexibility. Despite these promising
developments, current LLM-based agent frameworks still face limitations in task
planning and execution, highlighting ongoing research opportunities.
3
