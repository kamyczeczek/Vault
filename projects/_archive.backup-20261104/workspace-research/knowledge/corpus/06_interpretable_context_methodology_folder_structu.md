---
type: Concept
id: 06_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 7/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Interpretable Context Methodology: Folder Structure as Agent Architecture•7
workspace/
CLAUDE.md
CONTEXT.md
stages/
01_research/
CONTEXT.md
references/
output/
02_script/
CONTEXT.md
references/
output/
03_production/
CONTEXT.md
references/
output/
_config/
shared/
setup/
questionnaire.md
Layer 0
Layer 1
Layer 2
Layer 2
Layer 2
Layer 3
Layer 3
Layer 3
Layer 4
Layer 4
Layer 4
Layer 3
Layer 3
Fig. 2. Folder structure of a typical ICM workspace, with layer annotations. Files and folders are color-coded by their role in
the context hierarchy. Layer 3 material (reference) persists across runs. Layer 4 material (working artifacts) changes each
time the pipeline executes.
Layer 2 is the control point of the entire system. Each stage contract includes an Inputs table that specifies
exactly which files from Layers 3 and 4 the agent should load, and which sections of those files are relevant.4
Without this scoping mechanism, an agent would either load everything in the workspace or rely on its own
judgment about what matters. The Inputs table makes the selection explicit, editable, and auditable.
This is the filesystem doing the work that a framework would otherwise do in code. Stage sequencing is the
folder numbering. Context scoping is the folder hierarchy. State management is the files on disk. Coordination
between stages is one folder’s output being another folder’s input.
From the model’s perspective, this layered loading changes the composition of the context window at each
stage. Layers 0 through 2 together contribute roughly 1,300 to 1,600 tokens of identity, routing, and stage-specific
instruction. Layer 3 adds reference material scoped to the current stage, typically 500 to 2,000 tokens depending
on how many conventions and guidelines apply. Layer 4 adds the working material for this run, a research
document, a script, a specification, which varies with the content but rarely exceeds a few thousand tokens when
the previous stage has done its job of condensing and structuring. The total context delivered to the model at any
given stage typically ranges from 2,000 to 8,000 tokens, well within the range where current models perform at
4Larger reference collections can include their own routing files, a CONTEXT.md within a configuration or design system folder, that help
agents navigate to the right content within the collection. This is the routing pattern from Layer 1 applied recursively within Layer 3.
