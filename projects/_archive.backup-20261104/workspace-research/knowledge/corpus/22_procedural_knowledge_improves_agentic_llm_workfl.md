---
type: Concept
id: 22_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 23/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Be aware that the accommodations returned by the Accommodations tool may have
names that do not seem to correspond with the city that you used for the
search; this is expected behavior and you should proceed with the results
you obtained using the tools.
,→
,→
,→
C.1.2 Example User Request
Please create a travel plan for a 3-day trip from Missoula to Dallas scheduled
from March 23rd to March 25th, 2022. The budget for this trip is set at
$1,900.
,→
,→
C.2 Domain: Recipe Generator
C.2.1 Problem Specification
The user will provide a request containing a list of ingredients, your job is to
select a valid recipe using those ingredients.,→
You do not need to use all ingredients provided by the user. Any recipe that can
be made from the ingredients provided by the user is a valid recipe. For
example, if the user provides the ingredient list:
,→
,→
Chicken Breast
Tomatoes
Soy Sauce
Sesame Oil
Brown Sugar
Garlic
The following recipe:
Dish: Chicken and Tomato Stir Fry
Ingredients:
Chicken Breast
Tomatoes
Soy Sauce
Sesame Oil
is valid solution to the user request, and a valid final output is:
Chicken and Tomato Stir Fry
C.2.2 Example User Request
Hello, I'd like to request a recipe for the following ingredients:
Chicken Breast
Tomatoes
Soy Sauce
26
