---
type: Concept
id: 27_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 28/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

"effect": "notes contains same details as request and contains origin,
destination, departure date and returning date for the trip",,→
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt"
}
},
"method3": {
"task": "choose a departing flight",
"effect": "notes contains details about a flight number and cost for a
flight from origin to destination on departure date consistent with
request preferences",
,→
,→
"subtasks": {
"subtask1": "understand flights tool"
},
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/problem_specification.txt",
"file3": "files/request.txt"
}
},
"method4": {
"task": "choose a returning flight",
"effect": "notes contains details about a flight number and cost for a
returning flight consistent with request preferences",,→
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/problem_specification.txt",
"file3": "files/request.txt"
}
},
"method5": {
"task": "choose an accommodation",
"effect": "notes contains details about an accomodation consistent with
request preferences",,→
"subtasks": {
"subtask1": "understand accommodation tool"
},
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/problem_specification.txt",
"file3": "files/request.txt"
}
},
"method6": {
"task": "understand flights tool",
"effect": "notes contains details about flights tool methods inputs and
outputs",,→
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/tools_specification.txt"
}
},
"method7": {
"task": "understand accommodation tool",
31

"effect": "notes contains details about accommodation tool methods
inputs and outputs",,→
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/tools_specification.txt"
}
},
"method8": {
"task": "take notes on the problem specification file",
"effect": "notes contain the information from the problem specification
file",,→
"effect_files": {
"file1": "files/problem_specification.txt",
"file2": "files/notes.txt"
}
}
}
D.2 Recipe Generator
{
"method1": {
"task": "process user request",
"subtasks": {
"subtask1": "take notes on user request and problem specification",
"subtask2": "understand the tools specification"
},
"effect": "the answer to the user request can be found in answer.txt",
"effect_files": {
"file1": "answer.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method2": {
"task": "solve user request",
"effect": "a valid recipe is chosen",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/problem_specification.txt",
"file3": "files/notes.txt"
}
},
"method3": {
"task": "understand the tools specification",
"effect": "details of provided tools and correct module import path are
recorded in notes",,→
"effect_files": {
"file1": "files/tools_specification.txt",
"file2": "files/notes.txt"
}
},
"method4": {
32
