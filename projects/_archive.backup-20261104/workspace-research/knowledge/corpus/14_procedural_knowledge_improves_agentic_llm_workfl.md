---
type: Concept
id: 14_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 15/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

[37] Wentao Zhang, Ce Cui, Yilei Zhao, Rui Hu, Yang Liu, Yahui Zhou, and Bo An. 2025. Agen-
torchestra: A hierarchical multi-agent framework for general-purpose task solving.arXiv preprint
arXiv:2506.12508(2025).
[38] Andrew Zhao, Daniel Huang, Quentin Xu, Matthieu Lin, Yong-Jin Liu, and Gao Huang. 2024.
Expel: Llm agents are experiential learners. InProceedings of the AAAI Conference on Artificial
Intelligence, Vol. 38. 19632–19642.
[39] Zhehua Zhou, Jiayang Song, Kunpeng Yao, Zhan Shu, and Lei Ma. 2024. Isr-llm: Iterative self-
refined large language model for long-horizon sequential task planning. In2024 IEEE International
Conference on Robotics and Automation (ICRA). IEEE, 2081–2088.
16

Figure A.1: An example problem instance for the unit movement domain showing the initial starting
position (blue circles) and a valid solution (red circles).
A Additional Figures
17

Figure A.2: A comparison of average runtime statistics for GPT-oss 120b across different benchmarks
(BW - BlocksWorld, TP - Travel Planner, UM - Unit Movement).
B Prompts
B.1 Standard Agent Prompt
This prompt is given to the agent at each iteration for all domains. Only the content of the read and
writeable files may differ across domains.
18
