---
type: Concept
id: 09_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 10/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Figure 3: Success rates for BlockWorld and Unit Movement domains, evaluated across increasing
problem complexity (b starting blocks and h final stack height for BW , number of unitsn for UM). Bars
show mean success rates, with 95% Wilson confidence intervals.
Unit Movement (UM). In this task, for each problem instance we generate a graphG with the following
properties (Figure A.1 shows an example problem). Atarget node vT ∈G is adjacent tofour neighbors
vad j, each with an edge (vad j, vT ). Each neighbor has threeouter neighbors; that is, for each node
vad j
i , there are at least 3 outer nodes vout with an edge (vad j
i , vout). After generating the above node sets,
we add 12 more random edges between neighboring nodes (excluding the target vT ). For three of the
sections of the graph we place n units to random nodes in each section. We randomly name each node
(e.g. Seaside, Canyon, Gardens) and each unit based on their section (e.g. Bravo_0, Alpha_1). The goal
of the task is to move units so that the target is surrounded from three neighbors with at least least k
units at each node.
We varied problem complexity by the number ofnunits per group and the numberkunits required for
surrounding. Figure 3 reveals two insights. First, Human-TN increases the task success rate regardless
of the base capability of the LLM used in the system; at ( n= 10, k= 6 ), the 20b model Human-TN
outperforms 120b No-TN. Second, higher (n, k)values seem show a non-linear correlation with task
difficulty; future work should explore whether the LLM is exploiting problem structure to solve larger
problems.
6 Discussion
The evaluation of ProcLLM shows thatHuman-TN andLLM-TN improve task success rate, often significantly
and even across No-TN success capability and different benchmarks. We also varied problem complexity
and showed that, in BW and UM, the LLM system with a task planner seems to have a slower decrease
11
