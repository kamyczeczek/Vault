---
type: Concept
id: 124_icm_knowledge_big
title: "ICM_knowledge.md (part 125/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

— This is where content gets built. If you are making animations (like the pipeline in

Section 2.6

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=3a82e3222c2c4cbc9d07c6f9f6d4265a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

), this is where your briefs, specs, and build files live. If you are making simple videos, this might be where your shot lists, thumbnails, and description templates go. The CONTEXT.md here describes your production process, your tools, your visual standards.

Distribution

— This is where finished content goes out. Platform-specific formatting (what works on Instagram vs LinkedIn vs YouTube), scheduling, repurposing long content into short clips. The CONTEXT.md describes your platforms, posting cadence, and any rules about how content should be adapted per channel.

#### What the CLAUDE.md looks like:

Your top-level file tells Claude what this project is and how to route between the three workspaces. Something like:

# My Content Project

I create [TYPE OF CONTENT] for [AUDIENCE].

## Workspaces

\-    /script-lab — Idea development, writing, drafts

\-    /production — Building and producing content

\-    /distribution — Publishing, scheduling, repurposing

## Routing

| **Task**             | **Go to**     | **Read**   |
| -------------------- | ------------- | ---------- |
| Write or brainstorm  | /script-lab   | CONTEXT.md |
| Build or produce     | /production   | CONTEXT.md |
| Publish or repurpose | /distribution | CONTEXT.md |

## Naming conventions

\-    Drafts: topic-name_draft.md

\-    Final scripts: topic-name_final.md

\-    Published: YYYY-MM-platform-topic.md

------

Example 2: Freelancer / Consultant

You work with multiple clients. Each engagement has a lifecycle: intake, scoping, delivery, follow-up. You need Claude to shift between clients without bleeding context. You also need your own internal workspace for business development, templates, and admin.

#### Your workspaces:

my-consulting-practice/ ├── CLAUDE.md ├── client-alpha/ │  ├── CONTEXT.md │  ├── intake/ │  ├── deliverables/ │  └── communications/ ├── client-beta/ │  ├── CONTEXT.md │  ├── intake/ │  ├── deliverables/ │  └── communications/ ├── templates/ │  ├── CONTEXT.md │  ├── proposals/ │  ├── reports/ │  └── frameworks/ └── business-dev/ ├── CONTEXT.md ├── pipeline/ ├── outreach/ └── case-studies/

#### What each workspace does:

Client workspaces

(one per client) — Each client gets their own folder with their own CONTEXT.md. That file describes who the client is, what the engagement is, what phase you are in, what the deliverables are, and any client-specific rules (tone of voice, terminology they use, things to avoid). When you tell Claude "let's work on Alpha," it reads Alpha's context and nothing from Beta. No bleed. No confusion.
