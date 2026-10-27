---
type: Concept
id: 15_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 16/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Your goal is to interact with a system that processes commands in order to solve
a given task. The task is specified in the problem specification document
and the task instance in the request file. You MUST read and take notes on
these files to solve the problem. You will only be able to see the
information from the immediately preceding action, so make sure you take
notes such that this information is not lost.
,→
,→
,→
,→
,→
You have the following actions and files available to you:
1. Read: reads [action_arg1]. Line numbers will be displayed.
Read [action_arg1]
2. Write: overwrites text file [action_arg1] with [action_arg2].
Write [action_arg1] [action_arg2]
3. Append: appends the text file [action_arg1] with [action_arg2].
Append [action_arg1] [action_arg2]
4. Verify: Send a request to check if current task has been achieved.
Verify
You are allowed to read and write the following file (r/w):
solver.py (r/w): this file is automatically executed after every revision. The
standard output of this file is written to output.txt,→
files/notes.txt (r/w): the contents of this file will always be displayed in the
notes section down below.,→
answer.txt (r/w): a file to hold the final answer to user request
You are allowed to access the following read-only files (r):
files/request.txt (r): the user request
files/problem_specification.txt (r): a problem specification document
files/tools_specification.txt (r): a document specifying tools
output.txt (r): the stdout of solver.py
The contents of files/notes.txt is:
***NOTES START***
{}
***NOTES END***
Your last response was:
***LAST RESPONSE START***
{}
***LAST RESPONSE END***
The last ten commands executed were:
***LAST COMMAND START***
{}
***LAST COMMAND END***
Here is the output of your last command:
***LAST COMMAND OUTPUT***
{}
***LAST COMMAND OUTPUT END***
Your Limitations:
19
