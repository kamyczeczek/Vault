---
type: Concept
id: 28_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 29/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

"task": "take notes on the problem specification file",
"effect": "notes contain the information from the problem specification
file",,→
"effect_files": {
"file1": "files/problem_specification.txt",
"file2": "files/notes.txt"
}
},
"method5": {
"task": "take notes on user request",
"effect": "notes contain the information from the user request",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/notes.txt"
}
},
"method6": {
"task": "take notes on user request and problem specification",
"effect": "notes contain information from the user request and problem
specification files",,→
"effect_files": {
"file1": "files/request.txt",
"file2": "files/problem_specification.txt",
"file3": "files/notes.txt"
}
}
}
D.3 Blocks World
{
"method1": {
"task": "process user request",
"subtasks": {
"subtask1": "take notes on problem specification",
"subtask2": "take notes on user request",
"subtask3": "unstack all blocks"
},
"effect": "answer.txt contains a solution to the user request in the
correct format",,→
"effect_files": {
"file1": "files/problem_specification.txt",
"file2": "files/request.txt",
"file3": "answer.txt"
}
},
"method2": {
"task": "take notes on problem specification",
"effect": "notes contain the information from the problem specification
file",,→
"effect_files": {
"file1": "files/problem_specification.txt",
33

"file2": "files/notes.txt"
}
},
"method3": {
"task": "solve the user request",
"effect": "notes contain steps to solve the user request",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/problem_specification.txt",
"file3": "files/notes.txt"
}
},
"method4": {
"task": "unstack all blocks",
"effect": "notes contain the intermediate steps to unstack all blocks
such that they are all clear and no blocks are being held",,→
"effect_files": {
"file1": "files/request.txt",
"file2": "files/problem_specification.txt",
"file3": "files/notes.txt"
}
},
"method5": {
"task": "take notes on user request",
"effect": "notes contain a copy of the user request about the initial
condition and goal",,→
"effect_files": {
"file1": "files/request.txt",
"file2": "files/notes.txt"
}
}
}
D.4 Unit Movement
{
"method1": {
"task": "process user request",
"subtasks": {
"subtask1": "take notes on problem specification",
"subtask2": "take notes on user request",
"subtask3": "group units",
"subtask4": "move units"
},
"effect": "the answer to the user request can be found in answer.txt in
the correct format",,→
"effect_files": {
"file1": "answer.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method2": {
34
