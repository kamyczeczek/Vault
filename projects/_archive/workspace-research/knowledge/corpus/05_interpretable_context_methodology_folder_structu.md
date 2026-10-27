---
type: Concept
id: 05_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 6/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

6•Jake Van Clief, David McDermott
Table 2. Layer 3 (reference material) versus Layer 4 (working artifacts).
Layer 3: Reference Layer 4: Working
Changes between runs No Yes
Example files voice.md, design-system.md, con-
ventions.md
research-output.md, script-
draft.md
Model should Internalize as constraints Process as input
Configured during Workspace setup (once) Pipeline execution (each run)
Folder locationreferences/ , _config/,
shared/
output/
Analogy The recipe The ingredients
Layer 0 is the global identity file. It tells the agent which workspace it is in, what the folder structure contains,
and where to find things. Layer 1 is workspace-level task routing: given what the user wants to do, which stage
handles it, and what shared resources exist across stages. Layer 2 is stage-specific: the contract that defines inputs,
process, and outputs for one step of the workflow.
Layers 3 and 4 are both content that the agent loads while executing a stage, but they represent fundamentally
different kinds of context.
Layer 3 is reference material: design systems, voice rules, build conventions, style guides, domain knowledge
bundled as skill files. These files are configured once during workspace setup and remain stable across every run
of the pipeline. They are the factory.3 Layer 4 is working artifacts: the output of the previous stage, user-provided
source material, anything specific to this particular run of the pipeline. These files are produced and consumed
during execution and change every time.
The distinction matters for how the model processes context. Layer 3 material needs to be internalized as
constraints and patterns: the model should writelike this, usethese colors, followthese conventions. Layer 4
material needs to be processed as input: the model should transformthis researchinto a script, or convertthis
scriptinto a visual specification. Mixing persistent rules with per-run artifacts in an undifferentiated context
window forces the model to sort them on its own. Separating them in the folder structure means the model
receives already-organized context.
A rendering agent might only need Layers 0 through 2. A script-writing agent reads down to Layer 4 to access
both the voice rules (Layer 3) and the source material (Layer 4). No agent reads everything. This keeps token cost
low and context focused, and it avoids the degradation that Liu et al. documented when models process long
contexts full of irrelevant material [25].
The folder structure for a typical workspace is shown in Figure 2.
The numbering encodes execution order. The folder boundaries enforce separation of concerns. The output/
directories are the Layer 4 handoff points: the output of stage 01 becomes available as input to stage 02. If a
human edits a file in 01_research/output/ before running stage 02, the agent picks up the edited version. The
references/directories and_config/folder hold Layer 3 material: the stable knowledge and constraints that
persist across runs.
3This connects to the fifth design principle: configure the factory, not the product. Layer 3 is the factory configuration. Layer 4 is what the
factory produces each time it runs.
