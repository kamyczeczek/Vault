---
type: Concept
id: 170_icm_knowledge_big
title: "ICM_knowledge.md (part 171/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

final\_study\_notes.pdf

_config/    Layer 3, global rules

study-format.md

tone.md

pdf-format.md

shared/    Layer 3, shared rules/resources

glossary.md

naming-conventions.md

setup/

questionnaire.md

1. What each stage does

1. Key clarification

The CONTEXT.md of the next stage is not written by the previous stage. It already exists. It tells the agent which previous output to read, which references to use, and which new output to produce.

Layer 4 can be both output and input depending on the point of view: it is stored as the output of the stage that produced it, then read by the next stage as working material.

How the Stages Connect

The pipeline is visible because every handoff is a file in the filesystem.

1. Flow example

Source video / audio / raw transcript

01_ingest produces:

studio-video/stages/01_ingest/output/transcript_clean.md

02_synthesis reads that file and produces:

studio-video/stages/02_synthesis/output/study_notes.md

03_pdf reads that file and produces:

studio-video/stages/03_pdf/output/final_study_notes.pdf

Formula: each stage produces a Layer 4 file in its own output/ folder. The next stage reads that Layer 4 as working material and produces a new Layer 4.

1. Example: what     02_synthesis/CONTEXT.md says

studio-video/stages/01_ingest/output/transcript_clean.md

#### Use these references:

studio-video/_config/study-format.md

studio-video/stages/02_synthesis/references/synthesis-rules.md

studio-video/stages/02_synthesis/output/study_notes.md

1. Stage contract checklist

Inputs - what files or folders the stage reads. Always distinguish Layer 3 reference material from Layer 4 working artifacts.

Process - what the stage must do. Instructions should be concrete, checkable, and limited to one main job.

Outputs - what files the stage produces. Usually written in that stage output/ folder.

Review gate - before the next stage runs, the human reads, corrects, and approves the output.

1. When to use it

1. Golden rule

Correct the output to save the current run. If the same correction repeats, fix the source that caused the issue.

Single issue: edit the file in output/ and save the run.

Repeated issue in the same stage: fix Layer 2 if the issue is in that stage CONTEXT.md; fix Layer 3 if the issue is in a stable rule or reference file.

Improve the factory, not just the product.

------

Uncategorized\links.md

Undestand anything plungin for ai agent

https://understand-anything.com/

#### ICM Architect

\-    a Claude skill that turns a process, an idea, or a messy folder into an ICM workspace

https://github.com/RinDig/icm-architect

📦 What it does

🔨 Build. You describe your work and it pulls out the structure already sitting in how you talk about it. The stages, the points    where you stop and check, what stays the same every run versus what is new. Then it picks one of five proven forms and       scaffolds the smallest workspace that carries the job.
