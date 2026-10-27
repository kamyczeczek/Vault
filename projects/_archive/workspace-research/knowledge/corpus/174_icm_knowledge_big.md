---
type: Concept
id: 174_icm_knowledge_big
title: "ICM_knowledge.md (part 175/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

This is my personal guide for working inside an ICM (Interpretable Context Methodology) workspace—Jake’s Method turned into executable muscle memory. It is not a loose set of tips. It is the exact rule set that turns a folder of markdown files into a deterministic, human-reviewable, self-improving production line. Every bullet below was stress-tested in real delivery pipelines where the only orchestration is numbered folders, CONTEXT.md stage contracts, and the filesystem itself.

Why This List Is Important

Most AI workflows die in one of two ways: they collapse under context bloat or they hallucinate their way through invisible state. ICM fixes both by making the entire workflow visible, editable, and version-controlled on disk. This list enforces that fix at the behavioral level. It guarantees the agent never drifts into framework thinking, never hides state in a black-box memory, and never ships half-baked output. Follow it and you get:

Predictable handoffs at every stage boundary

Human edits that become permanent factory improvements

Zero token waste from irrelevant subagents or monolithic prompts

Ruthless quality that compounds instead of eroding

In short: this list turns Jake’s folder-as-architecture into actual shipped value instead of another pretty diagram.

Workflow Orchestration

Stage-First Execution (Default)

Enter the next numbered stage folder and read its CONTEXT.md before doing anything else.

If the task spans 3+ steps or requires architectural decisions, treat the entire workspace as the plan—never invent a separate “plan node.”

If something goes sideways, STOP, open the relevant CONTEXT.md or output/, and let the human edit before proceeding. Never push forward with broken state.

Selective Context Loading (No Subagents)

Load only the layers you need: Layer 0 (CLAUDE.md), Layer 1 (workspace CONTEXT.md), Layer 2 (current stage CONTEXT.md), plus the minimum Layer 3 references and Layer 4 prior-stage output/ required.

Never spawn subagents. If parallel work is required, the stage contract already defines it or the human splits the workspace. One agent, one stage, clean context.

Self-Improvement Loop (Factory Upgrade)

#### After ANY human correction or edit:

Update the relevant Layer 3 reference file (_config/, references/, or stage CONTEXT.md) so the pattern never repeats.

Write the exact rule change into the contract or style guide.

Review all active CONTEXT.md files at session start for relevant upgrades.

Ruthlessly iterate until the same mistake cannot occur again.

Verification Before Handoff

Never write to output/ without running the stage’s audit checklist (defined in CONTEXT.md).

Diff the new output against prior-stage expectations and the stage contract.

Ask: “Would Jake ship this exact handoff file?”

Demonstrate correctness with the exact artifacts the next stage will consume. Only then mark the stage complete.

Demand Elegance (Balanced)
