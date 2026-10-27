---
type: Concept
id: 21_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 22/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Your current task is:
Task: choose a departing flight
The effect that you are trying to achieve is:
Effect: notes contains details about a flight number and cost for a flight from
origin to destination on departure date consistent with request preferences,→
B.3.1 Example response to the previous prompt
{
"observation": "The solver.py execution printed flight search results to
output.txt, showing a flight with number F3528556, price 720, departure
time 08:33, etc. We need to capture these details in notes.txt.",
,→
,→
"thought": "To satisfy the effect, I will read output.txt to obtain the flight
information, then append a concise note with the departing flight number
and its cost to notes.txt.",
,→
,→
"action": {
"name": "Read",
"action_arg1": "output.txt",
"action_arg2": ""
}
}
C Domain Specification
For each domain, we write problem specification documents that the agent needs to read in order
to complete a task (e.g. what they need to actually do to complete the agentic task). Each problem
instance also has an automatically generated request.txt that describes the problem details for a
specific problem instance.
C.1 Domain: Travel Planner
C.1.1 Problem Specification
The user will provide a request to make a travel plan. You do not need to
complete the entire travel plan, but only the flight and accommodations for
the user's trip. You will need to use code files Flights.py and
Accommodations.py to access the database for required to solve the user
request
,→
,→
,→
,→
Your solution should be returned in a json format in answer.txt with two flights
(departing and returning) as well as the accommodation used for the duration
of the traveler's stay:
,→
,→
departing_flight: flight number
returning_flight: flight number
accommodation: name
25
