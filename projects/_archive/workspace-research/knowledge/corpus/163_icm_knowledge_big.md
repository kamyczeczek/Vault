---
type: Concept
id: 163_icm_knowledge_big
title: "ICM_knowledge.md (part 164/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Navigate before reasoning. If a map/router file exists, read it first. Using AI to reconstruct what a file already states is pure waste.

Scripts automate, AI reasons. Honor the 60/30/10 split. Never route deterministic work through AI; never let a script make judgment calls.

Stay in scope. An agent works only in the folder it was pointed at. Wandering into sibling folders is a boundary failure, not initiative.

Stop and surface failures. When something fails, stop and report it. Don't silently retry — that hides the real problem and burns budget. A human picks the next move.

Complete answers, held under pressure. Give the full answer the first time; don't reverse a correct answer just because you were pushed, unless there's genuinely new evidence.

Human review gate between stages. Nothing advances until a person approves what landed in output/. This is what makes the workflow interruptible and auditable.

Brief before prompt. Define the outcome and the failure criteria before opening the AI. A thin brief earns generic output — correctly.

Quickstart: scaffold this into your subject

Hand an AI this whole document plus the steps below, and it can build the same ICM system for any domain — cooking, legal intake, research, a game, customer support, anything.

Pick the subject and name the end-to-end job.

("Take a raw customer email and produce a triaged, routed response.")

Find the natural stages already implicit in that job, in order.

Most workflows already have stages — you're just naming them.

→ 01-intake / 02-classify / 03-draft / 04-review

For each stage, write a one-page CONTRACT: Inputs · Process · Outputs.

Output of stage N is the ONLY thing stage N+1 reads.

Pull the stable stuff (standards, voice, templates, domain facts)

out of the stages into a shared reference/ + _config/ layer.

#### At the root, write three tiny files:

identity (who this project is — under a page)

router (pointers only — "for X go to stage 0Y")

rules (the non-negotiables + why)

#### If a stage needs a focused expert, build it as a specialist:

identity (philosophy) · rules (testable behavior) ·

reference (protocols/schemas) · workflow (pick-up/drop) ·

examples (annotated do/don't pairs — build this one hardest).

If multiple experts must coordinate, add a 0-orchestrator that

ROUTES (never answers) and a manifest defining the handoff shape.

Update the manifest BEFORE any handoff format ever changes.

#### Before automating anything, run the 60/30/10 test:

deterministic → script; rule-based → automation; judgment → AI.

Limits to hold: identity < 50 lines · routers < 80 lines ·

reference < 200 lines · each step's context 2,000–8,000 "words."

Every step ends in an output/ folder a human checks before advancing.

------

Uncategorized\Community Call ICM, AI Workflows, and Future Tools.md

Community Call: ICM, AI Workflows, and Future Tools

Introductions & Participants

Jacob – SEO & small business automations; looking to hire
