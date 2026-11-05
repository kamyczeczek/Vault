---
type: Concept
id: 22_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 23/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Prompt Template for WORLDEVOLVER
You are a world model for the {env_name} environment. Given the agent’s current observation, its proposed action, and
the task goal, predict what the agent will observe next.
If a “## Frame Axioms and Persistence Rules” section appears above, treat each rule as a constraint: do not predict any
change to a property the rules say does not change for the action being taken.
If a “## Retrieved similar past transitions” section is provided, use those transitions as analogies for what can change
after this action. Let the retrieved transitions guide what changes, and use the frame axioms / persistence rules to filter
out spurious changes.
Output format:a single paragraph starting with “Prediction:” describing the next observation in the style of the
environment’s own text output.
Grounding blocks (Semantic above, Episodic below):
## Frame Axioms and Persistence Rules
{rules fromM S}
## Retrieved similar past transitions
{kME transitions fromM E}
Figure 23: WORLDEVOLVERworld model prompt combining Episodic and Semantic Memory grounding blocks,
withforesight-based confidence filtering applied post-generation without modifying the prompt.
Prompt Template for Observation Factorizer
System message:
You extract compact world-state triples from text observations. Return only valid JSON; do
not explain.
User message:
Extract (subject, predicate, object) triples that describe the world state from the observation
below. Output ONLY a JSON array of triples, each triple as a 3-element array of strings.
Environment: {env}
Observation: {obs}
Respond with JSON array only, no other text. Example output format:
[[“fridge 1”, “is”, “open”], [“mug 1”, “on”, “countertop 2”], [“water 1”, “state”, “liquid”]]
Figure 24: Observation factorizer prompt, converting predicted and gold observations into factorized triples whose
set difference determines whether Semantic Memory identifies a mismatch.
24
