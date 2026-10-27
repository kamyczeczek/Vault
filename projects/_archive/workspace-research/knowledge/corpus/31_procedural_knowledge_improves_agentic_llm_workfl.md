---
type: Concept
id: 31_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 32/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

"file1": "files/request.txt"
}
},
"method5": {
"task": "read problem specification",
"effect": "the contents of files/problem_specification.txt have been read
and can be used for note taking",,→
"effect_files": {
"file1": "files/problem_specification.txt"
}
},
"method6": {
"task": "write notes",
"effect": "files/notes.txt now contains extracted information from the
request and specification",,→
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method7": {
"task": "plan strategy",
"effect": "files/notes.txt is updated with a high-level movement strategy
for the infantry units",,→
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method8": {
"task": "write actions to notes",
"effect": "files/notes.txt now contains the final JSON list of unit
actions",,→
"effect_files": {
"file1": "files/notes.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
"method9": {
"task": "write answer file",
"effect": "answer.txt contains the JSON list of unit actions in the required
format",,→
"effect_files": {
"file1": "answer.txt",
"file2": "files/notes.txt",
"file3": "files/request.txt",
"file4": "files/problem_specification.txt"
}
}
}
39
