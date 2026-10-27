---
type: Concept
id: 11_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 12/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Figure 4: A comparison of average runtime statistics for GPT-oss across different benchmarks (BW -
BlocksWorld, TP - Travel Planner, UM - Unit Movement). (See Fig. A.2 for full details)
ProcLLM uses a file system as the environment, this framework could be applied to employ LLM agents
in more general MDP domains (e.g., games, control problems).
We demonstrated on four benchmarks that the HTN decomposition in ProcLLM significantly increased
task success in difficult multi-step agentic tasks. This is effective regardless of the base LLM. This
improvement uses natural language descriptions; ProcLLM does not require translation to a planning
formalism (e.g., PDDL, HDDL). Using natural language allows a flexible and natural tradeoff in the level
of abstraction for HTN planning. The high-level planning afforded by the task planner increases the
likelihood of completing long, complex tasks and also reduces the probability of many common agentic
LLM issues, such as action looping, that are exacerbated by a deficiency in implicit task planning.
LLM generated task networks sometimes do well, but they seem to generally lack the specificity of
human generated networks. In future work, it would be interesting to see if LLMs can build task
networks from the ground up in a curriculum learning fashion, starting with simple tasks that gradually
become more complex. Also, it would be interesting to explore an equivalent approach in (3) where an
LLM transforms the HTN recipe into code for speed and consistent replicability. Finally, procedures are
frequently codified into documents as recipes, checklists, or standard operating procedures. Beyond
learning networks through curriculum learning, we could explore methods for using RAG (e.g., (22)) or
fine-tuning (e.g., (30)) to improve the distillation of task networks from domain documents
Acknowledgments
We thank NRL for funding this research.
13
