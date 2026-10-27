---
type: Concept
id: 10_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 11/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Interpretable Context Methodology: Folder Structure as Agent Architecture•11
Stage 2 (02_script) reads the research output and writes a script. The stage’s CONTEXT.md points the agent to
a voice guide and structural template in the _config/ folder. The script follows the user’s established tone and
format.
Stage 3 (03_production) reads the finished script and produces animation specifications and working Re-
motion6 code. The stage’s context includes design guidelines, color palettes, and animation conventions from
setup.
At each stage boundary, the human reviews the output. A research document that misses an important angle
gets edited before the script stage runs. A script that runs too long gets trimmed before the production stage sees
it. The agent at each stage works with whatever the human left in the previous output folder.
This workspace runs on a single Claude Code session. One orchestrating agent (Opus 4.6) manages the pipeline,
delegating sub-tasks within stages to faster sub-agents (Sonnet 4.6) as described in Section 4.1. The delegation is
itself driven by the folder structure: the orchestrating agent reads the stage’s CONTEXT.md to determine what
work to delegate and what context to provide. There is no separate orchestration framework. The same folder
hierarchy that tells the human what each stage does tells the agent how to coordinate its sub-agents. In compiler
terms, the workspace performs multi-pass compilation: the processing engine runs multiple times, producing a
different intermediate representation at each pass, with the folder structure determining which pass runs next.
4.3 Course Deck Production
A second workspace takes unstructured source material (PDFs, papers, lecture notes, rough outlines) and produces
polished PowerPoint slide decks through five stages: content extraction, structural planning, slide drafting, visual
design specification, and final assembly.
The five-stage structure matters because slide deck production is a process where human judgment is essential
at several points. The structural plan (stage 2 output) determines the entire arc of the presentation. Getting it
wrong means everything downstream is wrong. By surfacing the structural plan as an editable markdown file
before any slides are drafted, ICM lets the human course-correct at the point where correction is cheapest and
most effective.
4.4 Building New Workspaces
ICM includes a workspace-builder: a five-stage workspace whose output is a new workspace. It walks through
discovery (what is the domain, what is the workflow), stage mapping (where are the natural breakpoints),
scaffolding (creating the folder structure), questionnaire design (what setup questions should the workspace ask),
and validation (does the pipeline run end to end).
The workspace-builder itself follows ICM conventions. The workspaces it produces are consistent because the
builder enforces the same structural rules it was built with.
This means practitioners can create new workspaces for their own domains without understanding the
underlying conventions in detail. The builder encodes the conventions into its process. A marketing team can
build a workspace for campaign production. A research group can build one for literature review and synthesis.
A consultancy can build one for client deliverable pipelines. Each workspace is a folder they own and control.
ICM workspaces have been adopted by groups outside the author’s organization. Researchers at the University
of Edinburgh’s Neuropolitics Lab have built workspaces for their domain, and teams at ICR Research and the
Academy of International Affairs in Bonn are developing workspaces for their own workflows. The details of these
implementations are limited by nondisclosure agreements, but their existence is noted here because the reviewer’s
natural question, does ICM work when someone other than its designer builds and operates the workspace, has at
6Remotion is a React-based framework for creating videos programmatically.
