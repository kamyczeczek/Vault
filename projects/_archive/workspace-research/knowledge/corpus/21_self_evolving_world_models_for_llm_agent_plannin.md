---
type: Concept
id: 21_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 22/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Prompt Template for ITP-I World Model
You are a world model for the {env_name} environment. Given an action/observation history, imagine the next few
steps, describing likely observations and key objects.
User message (one-step imagination contract for prediction; multi-step for planning):
Goal: {task_goal}
Current state: {observation}
Action: {action}
Prediction-evaluation cells restrict ITP-I to a single imagined step so all methods share the next-observation target.
Agent-planning cells let the world model select k∈ {0, . . . ,5}and return the corresponding k-step imagined future
enclosed by<Foresight>. . . </Foresight>.
Figure 20: ITP-I world model prompt following the Imagine-then-Plan (Liu et al., 2026) inference, with horizon k
fixed at1for World Model Prediction evaluation and selected by the model during Agent Planning.
Prompt Template for Episodic Memory World Model
You are a world model for the {env_name} environment. Given the agent’s current observation, its proposed action, and
the task goal, predict what the agent will observe next.
If a “## Retrieved similar past transitions” section is provided, use those transitions as analogies for what can change
after this action. Let the retrieved transitions guide what changes, but keep the prediction consistent with the current
observation and task goal.
Output format:a single paragraph starting with “Prediction:” describing the next observation in the style of the
environment’s own text output.
Grounding block (Episodic Memory):
## Retrieved similar past transitions
Transition 1:(State, Action, Observation)
. . .
Transitionk ME :(State, Action, Observation)
Figure 21: Episodic Memory world model prompt, augmented with top- kME action-keyed transitions retrieved
fromM E via Jaccard similarity over actions and prepended as a grounding block.
Prompt Template for Semantic Memory World Model
You are a world model for the {env_name} environment. Given the agent’s current observation, its proposed action, and
the task goal, predict what the agent will observe next.
If a “## Frame Axioms and Persistence Rules” section appears above, treat each rule as a constraint: do not predict any
change to a property the rules say does not change for the action being taken. Use the rules to filter out spurious changes.
Output format:a single paragraph starting with “Prediction:” describing the next observation in the style of the
environment’s own text output.
Grounding block (Semantic Memory):
## Frame Axioms and Persistence Rules
Rule 1:{rule_text} (evidencee 1)
. . .
Rule|M S|:{rule_text} (evidencee |MS |)
Figure 22: Semantic Memory world model prompt, grounded by mismatch-derived persistence rules from MS
rendered as frame axioms and ranked by accumulated evidence score.
23
