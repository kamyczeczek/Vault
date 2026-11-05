---
type: Concept
id: 01_enhancing_llm_based_agents_via_global
title: "Enhancing LLM-Based Agents via Global (part 2/13)"
source: "Enhancing LLM-Based Agents via Global.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

1 Introduction
In recent years, intelligent agent systems based on Large Language Models (LLMs)
have shown remarkable potential in practical applications [1, 2]. This advancement
comes mainly from two aspects: (1) LLMs have continuously improved their core
capabilities, such as instruction-following, tool utilization, programming, writing, and
logical reasoning [3–5]; (2) the ongoing advancement of agent frameworks (e.g., Plan-
and-Solve [6], ReAct [7], CodeAct [8]) has enabled agents to autonomously perform
task planning (what to do) and task execution (how to do), facilitating the achievement
of target objectives through interactions with the environment.
Although existing agent frameworks demonstrate a certain level of autonomy in
task planning and execution , substantial limitations remain within these two
critical stages:
Firstly, at the planning level, current methods either lack clear global goals or
generate plans that are hard to execute. Some frameworks, such as ReAct, adopt an
incremental reasoning approach of “Thought-Action-Observation”, focusing only on
the immediate step without a comprehensive global perspective. Consequently, these
frameworks frequently become stuck in local optima during tasks involving multiple
branches. In contrast, methods like Plan-and-Execute [9] attempt to enhance task-
solving capabilities by first generating a global plan and subsequently executing it,
while dynamically adjusting the plan based on feedback obtained during execution.
However, such methods often fail to effectively integrate concrete executable actions
into the global plan, resulting in plans that exceed the agents’ action space.
Secondly, at the execution level, existing methods face a trade-off between complex-
ity and stability, while also being constrained by a limited action space. Frameworks
like ReAct primarily rely on text or json formats to invoke external tools. While
these formats offer a straightforward mechanism for tool interaction, they lack the
capability to handle complex logic structures, such as loops and conditional branches.
CodeAct attempts to unify the agent’s action space using python code, allowing for
more sophisticated tool invocation logic. However, despite its greater expressive power,
it increases execution complexity. In real-world scenarios where tool invocation out-
comes are inherently unpredictable, highly complex invocation logic is more prone to
errors, making the system less stable. Moreover, not all tasks can be effectively solved
using code alone, such as advanced writing tasks (e.g., legal document generation [10])
and logical/mathematical reasoning (e.g., Lateral Thinking Puzzles [11]).
These limitations lead to discrepancies between the agents’ intended decisions and
their actual executed behaviors, thereby constraining both the effectiveness and gen-
eralizability of these agents when addressing complex real-world tasks. To address
the above issues, we propose the GoalAct framework, aiming to enhance LLM-based
agents via global planning and hierarchical execution:
• Global planning: we introduce a continuously updatable global planning mech-
anism that tightly couples planning and execution, enabling agents to establish
clearer long-term goals while ensuring the feasibility of plans.
• Hierarchical execution: we argue that the complexity of real-world actions can-
not be effectively managed by existing single-stage execution methods , which
2
