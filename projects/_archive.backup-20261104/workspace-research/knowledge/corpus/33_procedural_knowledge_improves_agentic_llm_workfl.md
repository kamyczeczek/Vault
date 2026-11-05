---
type: Concept
id: 33_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 34/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

},
"effect": "notes contain information from [example1] and [example2]
documents",,→
"effect_files": {
"file1": "files/[example1].txt",
"file2": "files/[example2].txt",
"file3": "files/notes.txt"
}
}
}
which specify the name of the task, the effect of the task, the files that can
be used to confirm the result of the task and possibly a list of subtasks
that may need to be completed. For the following problem, please write a
task network for nodes of the above format to assist the agent in solving
the task.
,→
,→
,→
,→
General instructions:
1. Please respond only with the task network and no additional text.
2. The agent will need to use the verify action to move onto the next task, so
no verification subtasks are needed.,→
3. Make sure that the keys for subtasks are numbered backwards in the order that
the agent should complete the task in.,→
4. All subtasks should have a corresponding task node. The subtasks component is
not needed for leaf nodes of the task network.,→
5. The values in the subtask list "[other subtask]" should correspond to the
name of the subtask it is referring to (e.g. "take notes on xyz").,→
6. The top level task should be called "process user request".
7. Effect files denote the files needed for the verifier to check if a given
task node is completed (e.g. if the task is to write an answer, the problem
specification and request should be included as effect files so the answer
can be checked against it).
,→
,→
,→
8. Make sure each task is numbered task[number].
The task specification:
*** TASK SPEC START ***
{}
*** TASK SPEC END ***
F Verification
To verify whether an agent LLM has successfully completed a task, we send a request to a verifier LLM
to check if the the effect of the task network node has been satisfied. Only the contents of the effect files
for a given task node are placed into the context of the verifier LLM. This allows for more consistent
evaluation (and alleviates long context issues in using smaller LLMs for verification).
F.1 Verification Code (success checking in Fig 2)
with open('verification_prompt.txt') as f:
lines = f.readlines()
prompt = "".join(lines)
task_specification = get_current_task_network_node(current_task)
41
