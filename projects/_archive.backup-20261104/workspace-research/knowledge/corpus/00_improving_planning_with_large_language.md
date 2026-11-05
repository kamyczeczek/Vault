---
type: Concept
id: 00_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 1/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
IMPROVINGPLANNING WITHLARGELANGUAGE
MODELS: A MODULARAGENTICARCHITECTURE
Shanka Subhra Mondal *†
Princeton University
Princeton, NJ
smondal@princeton.edu
Taylor W. Webb *
Microsoft Research
New York, NY
taylor.w.webb@gmail.com
Ida Momennejad
Microsoft Research
New York, NY
idamo@microsoft.com
ABSTRACT
Large language models (LLMs) demonstrate impressive performance on a wide
variety of tasks, but they often struggle with tasks that require multi-step rea-
soning or goal-directed planning. Both cognitive neuroscience and reinforcement
learning (RL) have proposed a number of interacting functional components that
together implement search and evaluation in multi-step decision making. These
components include conflict monitoring, state prediction, state evaluation, task
decomposition, and orchestration. To improve planning with LLMs, we propose
an agentic architecture, the Modular Agentic Planner (MAP), in which planning is
accomplished via the recurrent interaction of the specialized modules mentioned
above, each implemented using an LLM. MAP improves planning through the in-
teraction of specialized modules that break down a larger problem into multiple
brief automated calls to the LLM. We evaluate MAP on three challenging plan-
ning tasks – graph traversal, Tower of Hanoi, and the PlanBench benchmark –
as well as an NLP task requiring multi-step reasoning (strategyQA). We find that
MAP yields significant improvements over both standard LLM methods (zero-
shot prompting, in-context learning) and competitive baselines (chain-of-thought,
multi-agent debate, and tree-of-thought), can be effectively combined with smaller
and more cost-efficient LLMs (Llama3-70B), and displays superior transfer across
tasks. These results suggest the benefit of a modular and multi-agent approach to
planning with LLMs.
1 INTRODUCTION
Large Language Models (LLMs) (Devlin et al., 2019; Brown et al., 2020) have become widely
accepted as highly capable generalist systems with a surprising range of emergent capacities (Sri-
vastava et al., 2022; Wei et al., 2022a; Webb et al., 2023). They have also sparked broad controversy,
with some suggesting that they are approaching general intelligence (Bubeck et al., 2023), and others
noting a number of significant deficiencies (Mahowald et al., 2023). A particularly notable short-
coming is their poor ability to plan or perform faithful multi-step reasoning (Valmeekam et al., 2023;
Dziri et al., 2023). Recent work (Momennejad et al., 2023) has evaluated the extent to which LLMs
might possess an emergent capacity for planning and exploitingcognitive maps, the relational struc-
tures that humans and other animals utilize to perform planning (Tolman, 1948; Tavares et al., 2015;
Behrens et al., 2018). This work found that LLMs displayed systematic shortcomings in planning
tasks that suggested an inability to reason about cognitive maps. Common failure modes included
a tendency to ‘hallucinate’ (e.g., to use non-existent transitions and paths), and to fall into loops.
*Equal contribution. Co-first author order is arbitrary and may be swapped when citing this work.
†Work performed during internship at Microsoft Research.
1
arXiv:2310.00194v5  [cs.AI]  14 Oct 2025
