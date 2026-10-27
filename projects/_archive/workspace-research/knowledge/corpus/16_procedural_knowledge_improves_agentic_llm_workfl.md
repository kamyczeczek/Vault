---
type: Concept
id: 16_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 17/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

1. Do not attempt to read or write to any files not listed. This will result in
a file access denied error.,→
2. You can only open one file at a time.
3. If you get a file access denied error, make sure you use the correct path and
extension.,→
General Instructions:
1. Your response should be in a json format (formatted with newlines) and
include the following components:,→
* observation: a detailed observation about the current state of the task and
what you have done so far,→
* thought: reasoning about what next steps are valid and how to proceed
* action {{name: , action_arg1: , action_arg2: }}: action [read, write, append,
or verify] and arguments for the action,→
2. There is no limit on how long your json can be, but do not include additional
nested components.,→
3. If you receive a JSONDecode error, this means your json response is
improperly formatted.,→
4. Think step by step. Justify each step with something from existing notes or
previous responses.,→
5. Respond only with your json action. Use an empty string if any arguments are
unneeded.,→
6. A task planner will give you a task to follow with an effect. Focus on
achieving this effect.,→
7. Call the verify action when the current effect is satisfied to move onto the
next task.,→
8. You MUST take notes to solve the problem. Make sure to take notes after a
read.,→
9. Do not include section headings (e.g. ***) in your response.
Your current task is:
Task: {}
The effect that you are trying to achieve is:
Effect: {}
B.2 Agent Action Examples
The agent is expected to respond with a JSON that will be parsed and processed as an action. Here are
some examples:
{
"observation": "Currently, no notes have been taken and no files have been
read. The task is to take notes on the problem specification file.",,→
"thought": "To achieve the effect of having notes contain the information from
the problem specification file, I first need to read the problem
specification file. Then, I will append the contents of this file to the
notes.txt file to ensure persistence of the information.",
,→
,→
,→
"action": {
"name": "Read",
"action_arg1": "files/problem_specification.txt",
"action_arg2": ""
}
}
20
