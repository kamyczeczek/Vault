---
type: Concept
id: 19_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 20/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Prompt Template for ReAct Agent (ALFWorld)
Your task is to interact with a virtual household simulator to accomplish a specific task. With each interaction, you will
receive an observation. Your role is to decide on an action based on the observation. Please ensure that any objects
({obj}) and receptacles ({recep}) you mention in your response are present in the observation provided.
Available actions:
take {obj} from {recep} put {obj} in/on {recep} open {recep} close {recep} toggle
{obj}/{recep} clean {obj} using {recep} cool {obj} using {recep} heat {obj} using
{recep} inventory examine {recep}/{obj} go to {recep}
For each of your turns, you will be given the observation of the last turn. You should first think about what to do, and
then output the action for this turn.
Response format:
Thought: <your thought>
Action: <your next action>
Return exactly one line. Do not begin with a newline, blank line, space, markdown, or any text before “Thought:” or
“Action:”.
Figure 14: ReAct agent prompt for ALFWorld, with placeholders for available actions and the response format.
Prompt Template for ReflAct Agent (ALFWorld)
Your task is to interact with a virtual household simulator to accomplish a specific task. With each interaction, you
will receive an observation. Your role is to decide on an action based on the observation. The available actions and
object/receptacle constraints match the ReAct prompt above (Figure 14).
For each of your turns, you should first reflect in one sentence on the agent’s state in relation to the task goal, and then
output the action for this turn.
Response format:
Reflection: <your reflection>
Action: <your next action>
Return exactly one line. Do not begin with a newline, blank line, space, markdown, or any text before “Reflection:” or
“Action:”.
Figure 15: ReflAct agent prompt for ALFWorld, replacing the ReActThoughtwithReflection.
Prompt Template for ReAct Agent (ScienceWorld)
You are an agent in a virtual science school environment, tasked to interact with various elements.
Available commands:
Manipulation:open/close {OBJ}, pick up {OBJ}, put down {OBJ}, move {OBJ} to {OBJ}, pour {OBJ}
into {OBJ}, dunk {OBJ} into {OBJ}, mix {OBJ}.
Inspection:look around, look at {OBJ}, look in {OBJ}, read {OBJ}.
Device Operations:activate {OBJ}, deactivate {OBJ}, use {OBJ} [on {OBJ}].
Movement:go to {LOC}.
Miscellaneous:eat {OBJ}, flush {OBJ}, focus on {OBJ}, wait [DURATION].
Information:task, inventory.
where{OBJ}is an object,{LOC}a location, and[DURATION]a specified time.
For each of your turns, you will be given the observation of the last turn. You should first think about what to do, and
then output the action for this turn.
Response format:
Thought: <your thought>
Action: <your next action>
Figure 16: ReAct agent prompt for ScienceWorld, enumerating six command groups (Manipulation, Inspection,
Device Operations, Movement, Miscellaneous, Information) and a per-turnThought/Actionresponse format.
21
