---
type: Concept
id: 23_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 24/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Prompt Template for Preservation-Rule Extractor
System message:
You are extracting PRESERVATION RULES for the {env} text environment from world model prediction
mismatches.
A preservation rule says what should stay the same after an action. Look for cases where the
prediction changed a fact, but the gold next observation shows that the fact did not change.
Return one JSON object per general rule:
- key: a short lowercase dot-separated name such as “examine.object_location”. Use the same
key for the same rule across different mismatches.
- text: one clear sentence stating the rule generically for this environment, not for one
specific object instance.
Example:
[{“key”:“examine.object_location”,“text”:“Examining an object does not move it.”}]
Only output rules about facts that should NOT have changed. If the batch does not show a
reusable preservation rule, output []. Do not invent rules to fill the list.
Output strict JSON only: a single list of objects with key and text fields. No markdown fences
and no commentary.
User message (rendered over a mismatch batch of sizek MS ):
Environment: {env}
From the following mismatches, extract preservation rules (what does NOT change after the
action). Return strict JSON only: a JSON list of objects.
Mismatch 1:
State: {state_1}
Action: {action_1}
Prediction: {prediction_1}
Gold next observation: {gold_next_1}
Mismatch 2:. . .
Figure 25: Preservation-rule extractor prompt, processing a batch of kMS mismatches per Semantic Memory update
and returning a JSON rule list appended toM S for use in WORLDEVOLVERgrounding.
25
