---
type: Concept
id: 01_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 2/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

cognitive systems (17), where a specific module in the system manages and applies such knowledge to
problem solving. Recently, procedural knowledge is used as a kind of meta-strategy to assist in solving
complex problems (e.g., (3)).
While LLMs have shown impressive capability, they often perform poorly on planning problems (13), and,
as we will show later, LLM performance generally degrades as task complexity increases. In complex
agentic tasks, successful task completion often hinges on an implicit plan that specifies what actions
to take and in what sequence to take them, a capability that current LLMs often fail to consistently
complete correctly. Part of the gap is that LLMs are mostly constructed to predict the next token,
while planning requires managing details that span different temporal horizons and different levels of
abstraction. LLMs lack a clearly understood way to track the change that results from taking action in
the world.
In contrast, this paper examines whether providingexplicitprocedural knowledge improves LLM
performance on agentic tasks. To provide an intuitive example (formalized in §3), consider the task of
booking a travel itinerary. Experienced travelers follow a sequence such as: book flights, book hotel,
and reserve attractions or restaurants. The sequence might vary by circumstance, but its presence
makes the problem much easier to solve. The sequence manages dependencies (e.g., confirm flights
before booking the hotel) and each step narrows the details considered in subsequent steps. But using
an abstract sequence requires a process that: 1) tracks progress on the overall procedure, 2) maintains
state changes across steps, 3) takes actions to complete each step, 4) verifies each step is finished before
proceeding.
When solving a travel problem like this, LLMs lack the capability to track these layers all at once, leading
to inefficient or unsuccessful workflows. For example, an LLM might book a restaurant reservation at
the destination before verifying flight timing, only to backtrack to address such foreseeable conflicts.
By treating complex tasks as a series of independent decisions rather than attending to interconnected
dependencies, LLMs struggle to leverage procedural (i.e., hierarchical, goal-oriented) knowledge.
In this paper, we address two questions:Can we embed procedural knowledge in an LLM workflow?and
Will procedural knowledge improve LLM performance?We will show that the answer to both questions
isYes!To that end:
• We formalize the problem as an MDP and integrate procedural knowledge using Hierarchical Task
Networks (HTNs), where abstract tasks decompose into totally ordered subtasks. An HTN ensures
logical consistency and resource availability.
• We describe and implement a hybrid LLM-HTN system, ProcLLM, that uses HTNs in an agentic LLM
workflow. Importantly, this workflow is compatible with any LLM.
• We evaluate the runtime, success, and number of cycles of ProcLLM on four benchmark problems,
two from the literature and two synthetic problems.For the problems and HTNs we studied, HTN
knowledge always improves LLM performance, often significantly.
• We demonstrate that smaller LLMs benefit more from this workflow and in some cases exceed the
performance of much larger LLMs without HTN knowledge.
• Finally, we show that LLM-created HTNs improve performance, though the results are mixed compared
to hand-coded HTNs.
Overall, these findings suggest that LLM workflows can benefit considerably from procedural knowledge,
not only in overall performance but also in a reduced model size and improved response time for the
same level of performance. Although our implementation uses an Agentic LLM workflow with HTN
knowledge, the process is straightforward and results may eventually generalize to other LLM workflows,
so we close with some possible future directions.
2 Related Work
Agentic LLMs. We define agentic LLM as a large language model framework that can act, use tools,
and plan to autonomously accomplish tasks. Many problems cannot be solved in a single forward pass of
an LLM, motivating workflow techniques such as prompt chaining (32), where the output of one prompt
becomes the input to another. Early community systems like AutoGPT (34) showcased the potential of
2
