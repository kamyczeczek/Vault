---
type: Concept
id: 169_icm_knowledge_big
title: "ICM_knowledge.md (part 170/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

. Break any project into the smallest interpretable units (“atoms”) with clear contracts—inputs, outputs, decision points, handoffs. Wire those atoms into deterministic “molecules” that have one job, one failure mode, and a transparent structure. That skeleton, stored as plain markdown files on your filesystem, becomes a persistent, version-controlled context layer—an “organism” that evolves without drift. Only then do you prompt AI surgically against that skeleton, eliminating the cycle of vibe-coded slop, endless debugging, and overcorrection. The filesystem

the architecture; ownership of the context layer is the leverage. It’s high-discipline upfront but pays compounding ROI in consistency, auditability, and trust.

------

Uncategorized\icm_operational_notes_studio_video-2026-07-23_07-58-00.md

ICM Operational Notes

A practical study summary for understanding folder structure as agent architecture.

Personal notes, not official ICM material. The goal is operational clarity, not memorization.

1. ICM in one sentence

ICM orchestrates sequential AI workflows through the filesystem: numbered folders act as stages, markdown files carry prompts and context, outputs become reviewable handoffs, local scripts handle mechanical work, and one agent reads the right files at the right moment.

1. The five principles

One stage, one job - Each stage takes a defined input, performs one main transformation, and writes a defined output.

Plain text as interface - Markdown and JSON are readable, editable, portable, and versionable.

Layered context loading - The agent loads only the context needed for the current stage. Less noise, more control.

Every output is an edit surface - Each intermediate output is a file the human can read, correct, and approve.

Configure the factory, not the product - Stable rules live in the factory. Each run creates a new product using those rules.

1. The five layers

Mental model: stages are the machine. Layer 3 is the machine rules. Layer 4 is the concrete material that enters, changes, and is produced during each run.

1. Clean workspace     structure

ICM Example: Studio-video Workspace

Hypothetical workspace for turning a technical video into reviewable study notes and a final PDF.

1. Studio-video folder     structure

studio-video/

CLAUDE.md    Layer 0, shared by the whole workspace

CONTEXT.md    Layer 1, shared by the whole workspace

stages/

01_ingest/

CONTEXT.md  Layer 2, contract for stage 01

references/  Layer 3, stable rules specific to stage 01

ingest-rules.md

output/   Layer 4, concrete run material/output

transcript\_clean.md

02_synthesis/

CONTEXT.md  Layer 2, contract for stage 02

references/  Layer 3, stable rules specific to stage 02

synthesis-rules.md

output/   Layer 4, concrete run material/output

study\_notes.md

03_pdf/

CONTEXT.md  Layer 2, contract for stage 03

references/  Layer 3, stable rules specific to stage 03

pdf-rules.md

output/   Layer 4, concrete run material/output
