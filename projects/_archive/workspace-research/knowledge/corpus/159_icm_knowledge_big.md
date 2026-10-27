---
type: Concept
id: 159_icm_knowledge_big
title: "ICM_knowledge.md (part 160/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Layer 3 — Reference: Stable knowledge — standards, templates, domain facts. Set once, reused. Lifespan: stable. Size: load only what's needed.

Layer 4 — Output: The artifacts a step produces. A human reviews these before the next step runs. Lifespan: per run. Size: varies.

Layer 3 is the factory. Layer 4 is the product. Knowledge stays stable and gets reused; output is fresh each run and always gets a human's eyes before the workflow advances.

#### How the system is organized (the six functional layers):

At the top level the toolkit is split by function, not by topic. Each folder has its own small router file.

├── README / map ← the system map; always read first

├── constraints/ ← Problem-solving protocols. Short, standalone rules

│ you load one or two of when a specific failure shows up

│ (e.g. "AI output sounds generic," "agent wandered out of scope").

├── skills/ ← Reusable techniques, model-agnostic. Each is a self-contained

│ folder (e.g. "audit X," "delegate heavy coding," "fix generic prose").

│ Flat namespace — pick one off the shelf.

├── workflows/ ← Active multi-step pipelines. Numbered stages that run in order.

│ This is where real multi-step work executes.

├── knowledge/ ← The persistent reference layer. Naming rules, methodology docs,

│ templates. Everything points here; it never points back out.

│ ├── _config/ ← global settings shared by every stage (the system's /etc)

│ ├── references/ ← the methodology, guides, patterns

│ └── templates/ ← reusable blank forms

├── scaffold/ ← Starters + builders for spinning up a brand-new project,

│ plus read-only "teaching" examples.

└── runtime/ ← The front door at run time: a boundary gate, a small memory

service, and the deterministic scripts (lint, scaffold, migrate).

The placement law: subject first, type second. A document about a particular skill lives inside that skill's folder — not in a generic "all plans" bucket. Type-buckets are a last resort for things that genuinely belong to no single subject. This is what keeps the system navigable as it grows.

#### The four routing documents (the "living" part):

This is ICM's filescope principle, customized into the toolkit's daily driver. Three or four tiny files do all the steering. These are what make it a living agent reference rather than a static doc — an agent re-reads them every session, so updating a file instantly changes how every future agent behaves.

Identity file (Layer 0): Who this folder is. Identity only — if it's getting long, content is hiding that belongs in a subfolder. Limit: ~50 lines.

Router file (Layer 1): Pointers only. "For this task → that file." No actual content. Limit: ~80 lines.

Values / Rules file: The non-negotiables and the why behind them. The system's conscience. Limit: short.

State file: Current session status — what's in progress, what's next. Kept separate from identity so it can change every session without churning the permanent files. Limit: short.
