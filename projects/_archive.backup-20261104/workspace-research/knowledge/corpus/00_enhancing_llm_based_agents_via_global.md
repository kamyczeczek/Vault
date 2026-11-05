---
type: Concept
id: 00_enhancing_llm_based_agents_via_global
title: "Enhancing LLM-Based Agents via Global (part 1/13)"
source: "Enhancing LLM-Based Agents via Global.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Enhancing LLM-Based Agents via Global
Planning and Hierarchical Execution
Junjie Chen1, Haitao Li1, Jingli Yang, Yiqun Liu1, Qingyao Ai1*
1DCST, Tsinghua University, Beijing, 100084, China.
*Corresponding author(s). E-mail(s): aiqingyao@gmail.com;
Abstract
Intelligent agent systems based on Large Language Models (LLMs) have shown
great potential in real-world applications. However, existing agent frameworks
still face critical limitations in task planning and execution, restricting their
effectiveness and generalizability. Specifically, current planning methods often
lack clear global goals—leading agents to get stuck in local branches—or pro-
duce non-executable plans. Meanwhile, existing execution mechanisms struggle
to balance complexity and stability, and their limited action space restricts
their ability to handle diverse real-world tasks. To address these limitations,
we propose GoalAct, a novel agent framework that introduces a continuously
updated global planning mechanism and integrates a hierarchical execu-
tion strategy. GoalAct decomposes task execution into high-level skills, including
searching, coding, writing and more, thereby reducing planning complexity while
enhancing the agents’ adaptability across diverse task scenarios. We evaluate
GoalAct on LegalAgentBench, a benchmark with multiple types of legal tasks
that require the use of multiple types of tools. Experimental results demonstrate
that GoalAct achieves state-of-the-art (SOTA) performance, with an average
improvement of 12.22% in success rate. These findings highlight GoalAct’s poten-
tial to drive the development of more advanced intelligent agent systems, making
them more effective across complex real-world applications. Our code can be
found at https://github.com/cjj826/GoalAct.
Keywords: Large Language Model, Agent, Global Planning, Hierarchical Execution
1
arXiv:2504.16563v3  [cs.IR]  29 Apr 2025
