---
type: Concept
id: 08_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 9/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Table 1: Comparison: Mean success rate on subtasks in reduced Travel Planner benchmark (Verification
set from (33))
M odelFlight 1 Flight 2 Hotel
Nemotron 70bNo-TN0.023 0.0 0.0
Nemotron 70bHuman-TN0.535 0.419 0.116
GPT-oss 120bNo-TN0.0 0.0 0.0
GPT-oss 120bHuman-TN0.814 0.6050.395
problem instance; it functions similar to a vanilla reflexion agent (23). Experiments are performed on an
AMD EPYC 7H12 64 core CPU with the LLMs being served through ollama hosted on A100 GPUs.
Travel Planning. This tool-use problem is based on the TravelPlanner benchmark (33), where the agent
can access database APIs (FlightSearch, RestaurantSearch, etc.) to create an itinerary satisfying a
user request. The original benchmark contains very difficult multi-constraint tasks where GPT-4 had a
low 0.6% success rate (33). Although other works have claimed higher success rates on this benchmark,
they require considerable human-written code scaffolding (10) or they use a simplified version of this
benchmark (e.g., eliminating tool use in the case of (9)).
We use several simplifications so task completion is within reach of current models while keeping
success non-trivial. First, we filter the validation set of (33) to obtain single destination travel requests.
Second, we used a subset of the original benchmark: book a flight from origin to destination, book
accommodation, and book a return flight. This subtask benchmark remains sufficiently difficult. Request
is filled with a user request from the validation set of (33). ProblemSpec specifies that the agent should
only fulfill parts of the request in order (in contrast to (33)).
We created 43 problems to solve for TP . Table 1 shows the success rate for completing the taskup
to a given column. For example, for Flight 2, Nemotron with Human-TN chose correct departing and
returning flights in 41.9% of the requests. For both Nemotron and GPT-oss, Human-TN substantially
improves task success rate overNo-TN.
Recipe Generator (RG). In this tool use task, an agent is given a list of cooking ingredients and
asked to return a dish that can be made from these ingredients. To process user requests, the agent
uses two python functions: get_ingredient_from_dish(dish) returns the ingredients for a dish, and
get_dish_from_ingredient(ingredient) returns a list of dishes for an ingredient. verify succeeds for
any dish that can be made from any subset of ingredients, and the agent can write arbitrary python code
calling these functions.
Using GPT-4, we generated a database of ingredients and dishes. A problem instance is constructed by
randomly selecting a dish, extracting its ingredients, and augmenting this list with additional ingredients.
This process ensures solvable problems that are also challenging.
Over 20 problem instances (not shown for space reasons), a task network improves results. GPT-oss-
120b had a base success rate of 0% for No-TN and 25% for Human-TN. Because solutions to this task
may require algorithmic solutions (e.g. filtering api call results), we applied a coding fine-tuned LLM
Nemotron-70b, which averaged a success rate of 50% forNo-TNand 80% forHuman-TN.
Blocks World (BW). This problem adapts the BlocksWorld benchmark from PlanBench (28), where
GPT-4 succeeded on 34.3% problems. In PlanBench, problems have 3-5 blocks, and the LLM prompt
includes the rules of the task, an example problem, and a solution to the example problem.
We made several changes. ProblemSpec describes the problem and the acceptable solution format and
Request contains the initial state. However, these files provideno explicit solution example. To assess
the impact of problem complexity, we randomly choose b initial blocks that must be in a final stack of
heighth; a solution is correct for stackingh, regardless of other blocksb−h.
Fig 3 reveals a downward trend in task success as complexity increases (from b= 3 to b= 9). Either
task network (Human-TN or LLM-TN) greatly increases the success rate; the success rate of GPT-oss-120b
Human-TN remains 70% in contrast to GPT-oss-120b No-TN of below 5%. Furthermore, the smaller
GPT-oss-20bHuman-TNsignificantly outperforms GPT-oss-120b.
10
