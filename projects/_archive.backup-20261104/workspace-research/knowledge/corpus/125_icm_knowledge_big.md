---
type: Concept
id: 125_icm_knowledge_big
title: "ICM_knowledge.md (part 126/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

— Your reusable frameworks. Proposal templates, report structures, analysis frameworks. The CONTEXT.md here describes what each template is for and how to use it. When you start a new engagement, you pull from templates into the client folder and customize.

Business Dev

— Pipeline tracking, outreach drafts, case studies from past work. The CONTEXT.md describes your ideal client, your services, your positioning. When you need Claude to help draft an outreach email or build a case study, it reads this context.

#### What the CLAUDE.md looks like:

# My Consulting Practice

I am a [TYPE] consultant working with [TYPES OF CLIENTS].

## Active Clients

\-    /client-alpha — [One-line description of engagement]

\-    /client-beta — [One-line description of engagement]

## Internal

\-    /templates — Reusable proposals, reports, frameworks

\-    /business-dev — Pipeline, outreach, case studies

## Routing

| **Task**              | **Go to**     | **Read**                       |
| --------------------- | ------------- | ------------------------------ |
| Client work for Alpha | /client-alpha | CONTEXT.md                     |
| Client work for Beta  | /client-beta  | CONTEXT.md                     |
| Build a new proposal  | /templates    | CONTEXT.md, then client folder |
| Outreach or pipeline  | /business-dev | CONTEXT.md                     |

## Rules

\-    Never reference one client's information in another client's workspace

\-    Proposals always start from /templates and get customized in the client folder

\-    Deliverables go in /client-[name]/deliverables, drafts stay in working folders

The key for freelancers: the client folders multiply. When you onboard a new client, you copy the structure, write a new CONTEXT.md, and Claude is ready. The CLAUDE.md at the top gets one new line in the routing table. That is it.

------

Example 3: Developer

You build software. You might work on one project or several. Your work involves planning, writing code, testing, deploying, and documenting. You probably already have opinions about folder structure. The difference here is that Claude reads it.

#### Your workspaces:

my-app/ ├── CLAUDE.md ├── planning/ │  ├── CONTEXT.md │  ├── specs/ │  ├── architecture/ │  └── decisions/ ├── src/ │  ├── CONTEXT.md │  ├── components/ │  ├── services/ │  ├── utils/ │  └── tests/ ├── docs/ │  ├── CONTEXT.md │  ├── api/ │  ├── guides/ │  └── changelog/ └── ops/ ├── CONTEXT.md ├── deploy/ ├── monitoring/ └── scripts/

#### What each workspace does:

— Specs, architecture decisions, design docs. The CONTEXT.md describes the app, the tech stack, the current priorities, and any architectural principles you follow. When you tell Claude to help you spec a new feature, it reads this context and works within your existing architecture.
