---
type: Concept
id: 30_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 31/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

"subtasks": {
"subtask1": "take notes on problem specification",
"subtask2": "take notes on user request"
},
"effect": "notes contain the initial state, goal state, and rules of the
problem",,→
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method4": {
"task": "take notes on problem specification",
"effect": "notes contain the rules of the blocksworld problem",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/problem_specification.txt"
}
},
"method5": {
"task": "take notes on user request",
"effect": "notes contain the initial and goal block configurations",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt"
}
},
"method6": {
"task": "generate plan to clear misplaced blocks",
"effect": "notes contains the sequence of unstack and put actions to move
all misplaced blocks to the table",,→
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt"
}
},
"method7": {
"task": "generate plan to build goal stacks",
"effect": "notes contains the sequence of pick and stack actions to build
the goal configuration from the blocks on the table",,→
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt"
}
},
"method8": {
"task": "write final plan to answer.txt",
"effect": "the final, combined plan from notes.txt is written to answer.txt
in the correct format",,→
"effect_files": {
"file1": "answer.txt",
"file2": "files/notes.txt"
}
}
37

}
E.2 Unit Movement
{
"method1": {
"task": "process user request",
"effect": "the answer to the user request can be found in answer.txt in the
correct format",,→
"effect_files": {
"file1": "answer.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
},
"subtasks": {
"subtask1": "compose actions",
"subtask2": "write answer file"
}
},
"method2": {
"task": "compose actions",
"effect": "notes.txt contains the JSON list of unit actions for the turn",
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
},
"subtasks": {
"subtask1": "take notes on request and spec",
"subtask2": "plan strategy",
"subtask3": "write actions to notes"
}
},
"method3": {
"task": "take notes on request and spec",
"effect": "notes.txt contains relevant information extracted from the
request and problem specification",,→
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
},
"subtasks": {
"subtask1": "read request",
"subtask2": "read problem specification",
"subtask3": "write notes"
}
},
"method4": {
"task": "read request",
"effect": "the contents of files/request.txt have been read and can be used
for note taking",,→
"effect_files": {
38
