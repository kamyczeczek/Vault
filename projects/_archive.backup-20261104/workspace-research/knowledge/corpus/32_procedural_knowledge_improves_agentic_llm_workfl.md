---
type: Concept
id: 32_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 33/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

E.3 Prompt for generating task networks
The following prompt was used as input to Gemini 2.5 Pro to generate the two LLM-generated task
networks above. The empty section labeled task specification is filled with the Problem Spec file for the
domain being tested.
There is a system that processes commands in order to solve a given task. The
task is specified in the problem specification document and the task
instance in the request file. An agent is given the following actions to
perform:
,→
,→
,→
1. Read: reads [action_arg1]. Line numbers will be displayed.
Read [action_arg1]
2. Write: overwrites text file [action_arg1] with [action_arg2].
Write [action_arg1] [action_arg2]
3. Append: appends the text file [action_arg1] with [action_arg2].
Append [action_arg1] [action_arg2]
4. Verify: Send a request to check if current task has been achieved.
Verify
The agent is allowed to read and write the following file (r/w):
files/notes.txt (r/w): the contents of this file will always be displayed in the
notes section down below.,→
answer.txt (r/w): a file to hold the final answer to user request
The agent is allowed to access the following read-only files (r):
files/request.txt (r): the user request
files/problem_specification.txt (r): a problem specification document
The agent can only see the contents of the last action it performed (e.g.
observations are Markovian), so the agent needs to take frequent notes. The
agent will follow a task network with nodes of the form:
,→
,→
{
"method1": {
"task": "process user request",
"subtasks": {
"subtask1": "[other subtask]",
"subtask2": "[other subtask]"
},
"effect": "the answer to the user request can be found in answer.txt in
the correct format",,→
"effect_files": {
"file1": "answer.txt",
"file2": "files/request.txt",
"file3": "files/problem_specification.txt"
}
},
....
"method7": {
"task": "take notes on [example1] and [example2]",
"subtasks": {
"subtask1": "[other subtask]",
"subtask2": "[other subtask]"
40
