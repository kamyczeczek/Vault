---
type: Concept
id: 20_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 21/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Prompt Template for ReflAct Agent (ScienceWorld)
You are an agent in a virtual science school environment, tasked to interact with various elements. The available
commands match the ReAct prompt above (Figure 16).
For each of your turns, you should first reflect in one sentence on the agent’s state in relation to the task goal, and then
output the action for this turn.
Response format:
Reflection: <your reflection>
Action: <your next action>
Figure 17: ReflAct agent prompt for ScienceWorld, inheriting the six ScienceWorld command groups.
Prompt Template for Zero-Shot World Model
You are a world model for the {env_name} environment. Given the agent’s current observation, its proposed action, and
the task goal, predict what the agent will observe next.
Output format:a single paragraph starting with “Prediction:” describing the next observation in the style of the
environment’s own text output.
User message:
Task goal: {task_goal}
Current observation: {observation}
Proposed action: {action}
Figure 18: Zero-Shot world model prompt.
Prompt Template for RA WM-ϕWorld Model
You are a world model. Given the agent’s current state and proposed action, predict what the agent will observe next.
Output format:a single paragraph starting with “Prediction:” describing the next observation in the style of the
environment’s own text output.
System-prompt block (retrieved transitions, prepended above the output directive):
## Retrieved similar past transitions
Transition 1:
State: {state_1}
Action: {action_1}
Observation: {observation_1}
Transition 2:. . .
Figure 19: RAWM-ϕ (Yang et al., 2025) world model prompt, augmented with top-k transitions retrieved by cosine
similarity overQwen3-Embedding-8Bembeddings of the live(s t, at)query against the fixed Word2World corpus.
22
