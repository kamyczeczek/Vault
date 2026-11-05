---
type: Concept
id: 26_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 27/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Infantry (Mike_11) at (Prairie)
Infantry (Mike_12) at (Pineside)
Infantry (Mike_13) at (Summit)
Infantry (Mike_14) at (Summit)
Location Network (location - neighbors):
Eastfield - ['Seabreeze', 'Skyline', 'Moonlight', 'Centerville']
Seabreeze - ['Eastfield', 'Meadow', 'Hillcrest', 'Crestview']
Skyline - ['Eastfield', 'Townsend', 'Bayview', 'Creekbend']
Moonlight - ['Eastfield', 'Summit', 'Pineside', 'Prairie']
Centerville - ['Eastfield', 'Riverbend', 'Lakeside', 'Sunnyside']
Meadow - ['Seabreeze', 'Lakeside', 'Prairie']
Hillcrest - ['Seabreeze', 'Sunnyside', 'Creekbend']
Crestview - ['Seabreeze']
Townsend - ['Skyline', 'Bayview']
Bayview - ['Skyline', 'Pineside', 'Lakeside', 'Riverbend', 'Townsend']
Creekbend - ['Skyline', 'Hillcrest']
Summit - ['Moonlight', 'Pineside']
Pineside - ['Moonlight', 'Summit', 'Bayview']
Prairie - ['Moonlight', 'Meadow']
Riverbend - ['Centerville', 'Bayview']
Lakeside - ['Centerville', 'Bayview', 'Meadow']
Sunnyside - ['Centerville', 'Hillcrest']
D Methods
D.1 Travel Planner
{
"method1": {
"task": "process user request",
"subtasks": {
"subtask1": "take notes on origin, destination, departure date,
returning date and other preferences",,→
"subtask2": "choose a departing flight",
"subtask3": "choose a returning flight",
"subtask4": "choose an accommodation"
},
"effect": "answer.txt contains a solution in the correct format that
follows the problem specification",,→
"effect_files": {
"file1": "answer.txt",
"file2": "files/problem_specification.txt"
}
},
"method2": {
"task": "take notes on origin, destination, departure date, returning
date and other preferences",,→
"subtasks": {
"subtask1": "take notes on the problem specification file"
},
30
