---
type: Concept
id: 20_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 21/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Write solver.py
***LAST COMMAND END***
Here is the output of your last command:
***LAST COMMAND OUTPUT***
Updated solver.py:
from tools.Flights import Flights
def main():
FlightSearch = Flights()
results = FlightSearch.run("Detroit", "San Diego", "2022-03-05")
print(results)
if __name__ == "__main__":
main()
Code executed with stdout:
Flight Number Price DepTime ... OriginCityName DestCityName Distance
3306155 F3528556 720 08:33 ... Detroit San Diego 1956.0
[1 rows x 9 columns]
***LAST COMMAND OUTPUT END***
Your Limitations:
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
* action {name: , action_arg1: , action_arg2: }: action [read, write, append,
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
24
