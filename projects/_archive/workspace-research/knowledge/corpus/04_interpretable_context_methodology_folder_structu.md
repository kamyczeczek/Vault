---
type: Concept
id: 04_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 5/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Interpretable Context Methodology: Folder Structure as Agent Architecture•5
Layer 0:CLAUDE.md
Layer 1:CONTEXT.md
Layer 2:Stage CONTEXT.md
Layer 3:Reference material
Layer 4:Working artifacts
“Where am I?”
“Where do I go?”
“What do I do?”
“What rules apply?”
“What am I working with?”
⁄tildelow800 tok
⁄tildelow300 tok
200–500 tok
500–2k tok
varies
Structural
(routing)
Content
(factory / product)
Fig. 1. The five-layer context hierarchy. Layers 0–2 provide structural routing and stage instructions. Layers 3 and 4 carry
content: Layer 3 holds reference material (the factory), stable across runs; Layer 4 holds working artifacts (the product),
unique to each run.
3 Interpretable Context Methodology
3.1 Design Principles
ICM is built on five principles, each borrowed from established practice.
One stage, one job.Each stage in a workspace handles a single step of the workflow and writes its output to
its own folder. This follows McIlroy’s Unix principle and Parnas’s information-hiding criterion [1, 9]. A stage
that fetches data does not also filter it. A stage that filters does not also format the final output. Each stage reads
a defined input, transforms it, and writes a defined output, the same structure that governs individual passes in a
multi-pass compiler.
Plain text as the interface.Stages communicate through markdown and JSON files. No binary formats, no
database connections, no proprietary serialization. This follows Kernighan and Pike’s argument that text is the
universal interface [5]. Any tool that can read a text file can participate in the workflow. Any human who can
open a text editor can inspect or modify any artifact.
Layered context loading.Agents load only the context they need for the current stage, following the principle
that less irrelevant context means better model performance [25]. This is prevention rather than compression [31].
Within the content layers, ICM further distinguishes between reference material (stable rules and conventions
that persist across runs) and working artifacts (per-run content that changes every time). The model receives
these as structurally separate context, which matters because they require different kinds of attention: reference
material should be internalized as constraints, while working artifacts should be processed as input.
Every output is an edit surface.The intermediate output of each stage is a file a human can open, read, edit,
and save before the next stage runs. This implements Horvitz’s mixed-initiative principles [37] and Shneiderman’s
direct manipulation paradigm [46]: the human works with visible, manipulable objects, and the system picks up
whatever the human left there.
Configure the factory, not the product.A workspace is set up once with the user’s preferences, brand,
style, and structural decisions. After that, each run of the pipeline produces a new deliverable using the same
configuration. This follows the continuous delivery principle that production pipelines should be repeatable [15].
3.2 Architecture
An ICM workspace is a folder. Inside it, agents navigate a five-layer context hierarchy (Figure 1).
