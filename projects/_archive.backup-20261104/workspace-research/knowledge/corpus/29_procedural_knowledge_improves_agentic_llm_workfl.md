---
type: Concept
id: 29_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 30/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

"task": "move units",
"subtasks": {
"subtask1": "move group 1",
"subtask2": "move group 2",
"subtask3": "move group 3"
},
"effect": "notes contain movement actions to achieve the user request",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/problem_specification.txt",
"file3": "files/notes.txt"
}
},
"method3": {
"task": "move group 1",
"effect": "notes contain moves for units in group 1",
"effect_files": {
"file1": "files/notes.txt"
}
},
"method4": {
"task": "move group 2",
"effect": "notes contain moves for units in group 2",
"effect_files": {
"file1": "files/notes.txt"
}
},
"method5": {
"task": "move group 3",
"effect": "notes contain moves for units in group 3",
"effect_files": {
"file1": "files/notes.txt"
}
},
"method6": {
"task": "group units",
"effect": "notes contain a grouping of units into three distinct groups
and a group level strategy for moving each group to achieve the
request goal",
,→
,→
"effect_files": {
"file1": "files/request.txt",
"file2": "files/notes.txt"
}
},
"method7": {
"task": "take notes on user request and problem specification",
"effect": "notes contain information from the user request and problem
specification files",,→
"effect_files": {
"file1": "files/request.txt",
"file2": "files/problem_specification.txt",
"file3": "files/notes.txt"
}
},
"method8": {
35

"task": "take notes on user request",
"effect": "notes contain information from the user request file",
"effect_files": {
"file1": "files/request.txt",
"file2": "files/notes.txt"
}
},
"method9": {
"task": "take notes on problem specification",
"effect": "notes contain information from the problem specification
file",,→
"effect_files": {
"file1": "files/problem_specification.txt",
"file2": "files/notes.txt"
}
}
}
E LLM-generated Task Networks
E.1 Blocks World
{
"method1": {
"task": "process user request",
"subtasks": {
"subtask1": "formulate plan",
"subtask2": "write final plan to answer.txt"
},
"effect": "the answer to the user request can be found in answer.txt in the
correct format",,→
"effect_files": {
"file1": "answer.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method2": {
"task": "formulate plan",
"subtasks": {
"subtask1": "take notes on problem and request",
"subtask2": "generate plan to clear misplaced blocks",
"subtask3": "generate plan to build goal stacks"
},
"effect": "the full plan to solve the blocksworld problem is stored in
notes.txt",,→
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt"
}
},
"method3": {
"task": "take notes on problem and request",
36
