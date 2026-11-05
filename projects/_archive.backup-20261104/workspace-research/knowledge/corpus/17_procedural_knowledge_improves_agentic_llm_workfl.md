---
type: Concept
id: 17_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 18/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

{
"observation": "Having read the request file (files/request.txt), I've
obtained additional context: a 3-day trip from Missoula to Dallas (March
23rd-25th, 2022) with a budget of $1,900. This aligns with my initial
notes but adds a budget constraint. My current understanding is that I
need to use Flights.py for flights and Accommodations.py for lodging
within this budget. However, I still lack detailed insights from the
problem specification file beyond the initial notes. To ensure
completeness, I'll append these new details to notes.txt.",
,→
,→
,→
,→
,→
,→
,→
"thought": "With the request's context in mind, particularly the budget, my
next steps should involve utilizing the specified tools (Flights.py and
Accommodations.py) while considering the $1,900 budget. Before executing
code, it's prudent to update my notes with the latest understanding,
including the budget constraint, to maintain a comprehensive record of my
approach.",
,→
,→
,→
,→
,→
"action": {
"name": "Append",
"action_arg1": "files/notes.txt",
"action_arg2": "Additional context from request file: Budget for Missoula to
Dallas trip (March 23rd-25th, 2022) is $1,900. Next steps involve using
Flights.py and Accommodations.py with budget consideration."
,→
,→
}
}
{
"observation": "Read the problem specification which defines the allowed
actions and required output format. Notes provide the initial state, goal
state, and a sequence to unstack all blocks to the table. To achieve the
goal, we will first execute the unstack/put sequence to clear the table,
then pick and stack blocks in the order required by the goal: cyan at
bottom, then blue, orange, green, yellow, purple. This yields a complete
plan using only pick, put, unstack, and stack actions.",
,→
,→
,→
,→
,→
,→
"thought": "Construct a plan consisting of the 8 unstack/put steps from the
notes, followed by pick/stack steps to build the goal tower. Write this
plan to answer.txt in the exact line-by-line format required.",
,→
,→
"action": {
"name": "Write",
"action_arg1": "answer.txt",
"action_arg2": "unstack black green\nput black\nunstack green cyan\nput
green\nunstack cyan blue\nput cyan\nunstack blue purple\nput blue\npick
blue\nstack blue cyan\npick orange\nstack orange blue\npick green\nstack
green orange\npick yellow\nstack yellow green\npick purple\nstack purple
yellow"
,→
,→
,→
,→
}
}
21
