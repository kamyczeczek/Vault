---
type: Concept
id: 24_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 25/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

C.3.2 Example User Request(n= 9, k= 6)
As initial conditions I have that:
the blue block is on the table
the gray block is on top of the blue block
the red block is on top of the gray block
the orange block is on top of the red block
the yellow block is on top of the orange block
the black block is on top of the yellow block
the cyan block is clear
the cyan block is on top of the black block
the purple block is clear
the purple block is on the table
the green block is clear
the green block is on the table
My goal is to have that:
the orange block is on top of the gray block
the blue block is on top of the orange block
the black block is on top of the blue block
the yellow block is on top of the black block
the red block is on top of the yellow block
C.4 Domain: Unit Movement
C.4.1 Problem Specification
You are an AI strategist tasked with controlling a team of infantry units in a
wargame. You are given the current game state and must output a list of
actions for your units to execute in a single turn.
,→
,→
Game State:
The game is played on a network. Units have location, and a unit ID.
Example unit:
{"unit_id": "Eagle_0", "location": "Westwood"},
Available Actions:
* Move:
{"unit_id": "unit_id", "action_type": "move", "location": target_location}
The unit will move to target_location.
Output Format:
Each action must be a valid JSON object as described above in a list. Do not
include any other text besides the JSON list.,→
Example Output for two units:
[
{"unit_id": "Blue_0", "action_type": "move", "location": "Village"},
{"unit_id": "Blue_1", "action_type": "move", "location": "Southshore"}
]
28
