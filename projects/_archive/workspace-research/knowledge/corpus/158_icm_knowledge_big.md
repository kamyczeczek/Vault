---
type: Concept
id: 158_icm_knowledge_big
title: "ICM_knowledge.md (part 159/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Does it genuinely need judgment across messy information? (synthesis, writing, analysis, design) → now use AI.

The name "60/30/10" is the effort budget for any system you build — the rough share of the work each layer should own:

60% — Deterministic (scripts, data, established tools). Anything with one right answer that can be calculated, looked up, or formatted to spec: scripts, database/SQL queries, spreadsheet formulas, file operations, APIs with predictable responses. This is the stable foundation — reliable, fast, auditable, cheap to run. It doesn't drift, hallucinate, or cost tokens. A VLOOKUP does not hallucinate.

30% — Rule-based routing & layering (AI navigates, scripts execute). The "which path do we take" decisions that have clear criteria: if/then routing, branching, known-category classification, template selection, threshold checks. The AI may decide which route applies, but a script or automation does the deterministic step. This is the orchestration band — predictable, still drift-free, and the layer that decides which of the 60% gets called.

10% — AI judgment (logic, synthesis, analysis). The slice that genuinely can't be reduced to a rule: writing, analysis of unstructured text, fuzzy categorization, creative work, noticing the pattern in messy data. This is the only place a language model earns its cost.

The deeper truth: the real divide is 90 vs 10, not 60 vs 30. Infrastructure (60%) and orchestration (30%) are both deterministic work — they differ in complexity, not in kind. So when something breaks, the operative question is simply: did something that belongs in the 90% end up running on the 10%? It almost always did.

The endstate — AI as director, not middle management. Once the right scripts exist, the AI's 10% collapses to one job: selecting and calling the deterministic 90% correctly. Judgment in routing, not in doing. A smart director calling solid scripts beats a bloated orchestration layer that hard-codes every path. And it ages well: the 10% (prompts, model choices) decays as models change; the 90% (folder structure, pipelines, routing conventions) survives every tool swap. Patterns last. Tools don't.

The trap this prevents: routing a math problem or a file rename through an AI. It's slow, expensive, and gives a slightly different answer each run. Scripts automate. AI reasons. Never make them compete.

#### The mental model: five context layers:

This is ICM's core model — the toolkit is built directly on top of it. Everything in the system is one of five "layers." Think of it as a factory and its products.

Layer 0 — Identity: "Who is this project, what agents exist, where do I start?" Lifespan: permanent. Size: ~1 page.

Layer 1 — Directory / Router: A signpost. No content, only "for X go here, for Y go there." Lifespan: permanent. Size: short.

Layer 2 — Stage contract: One step's rules — what to load, what to do, what to produce. Lifespan: per step. Size: short.
