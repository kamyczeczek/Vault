---
type: Concept
id: 34_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 35/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

check = task_specification["effect"]
files_to_check = ""
counter = 1
while "file" + str(counter) in task_specification["effect_files"]:
file_to_check = task_specification["effect_files"]["file" + str(counter)]
files_to_check += "## Here are the contents of " + file_to_check[:-4] + ":
\n",→
with open(files_directory + "/" + file_to_check) as f:
lines = f.readlines()
files_to_check += "".join(lines) + "\n"
counter += 1
prompt = prompt.format(check, files_to_check)
last_output = llm_model.instruct_query(prompt)
success = True if "PASS: TRUE" in last_output else False
if success:
predicates.add(stack[-1][0])
stack = stack[:-1]
if len(stack) == 0:
break
current_task = update_task()
F.2 Verification Prompt
This verification prompt was tuned with meta-prompting on GPT-4.
**Here is your task:**
Your goal is to determine if the provided files satisfy the specified effect.
Follow these steps carefully:,→
### **Task Specification**
The effect that needs to be satisfied is:
{}
### **File Contents**
Here are the contents of the files provided:
{}
### **Instructions**
1. **Understand the Effect:** Carefully read the effect and identify its
conditions.,→
2. **Analyze the File Contents:** Compare the file contents explicitly against
the conditions of the effect.,→
- Break down the effect into specific criteria (e.g., "summarized version"
means the main ideas in "request" should be present in "notes").,→
- Check whether these criteria are satisfied in the files.
3. **Provide a Detailed Analysis:** State which criteria are satisfied and which
are not, with reasons based on the file contents.,→
### **Your Response Format**
Begin your response with:
42

```
ANALYSIS:
<Your detailed analysis of whether the files satisfy the effect, with explicit
reasoning.>,→
```
End your response with one of the following lines:
```
PASS: TRUE
```
*only if all conditions of the effect are satisfied.*
```
PASS: FALSE
```
*if any condition of the effect is not satisfied.*
---
43
