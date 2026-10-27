---
type: Concept
id: 162_icm_knowledge_big
title: "ICM_knowledge.md (part 163/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Cover the edge, not just the center. One ambiguous or adversarial input → the correct handling. Examples that only show easy cases leave the hard ones to improvisation.

Rule of thumb: if rules is the law, examples is the case law. Rules state the principle; examples show how it's been applied — and applied wrongly. Agents, like junior hires, learn the job faster from worked cases than from the statute.

#### How to build a multi-agent system (several specialists working together):

When one expert isn't enough, you connect specialists through an orchestrator and a shared contract.

your-system/

├── manifest.yaml ← the contract: the exact data shape every handoff must use

├── AGENTS.md ← entry point + "how to activate" guide

├── 0-orchestrator/ ← routes work; never does the work itself

├── 1-specialist-a/

└── 2-specialist-b/

The orchestrator routes, it never answers. It identifies intent, packages the request (always including the user's original words verbatim), and sends it to the right specialist. If unsure, it asks one clarifying question.

manifest.yaml is the single source of truth for data shape. Every specialist's handoff references it. Golden rule: never change a handoff format without updating the manifest first — that's the #1 cause of silent breakage ("schema drift").

#### Two orchestrator styles:

Relay (lead → research → offer → close): work flows stage to stage.

Assess-and-decide (score one thing across several dimensions, then rule on it): the orchestrator needs a binding decision table (e.g. SHIP / FIX / ESCALATE), evidence-over-memory discipline, and an adversarial "try to break this" gate before it commits. It returns a decision, never a question.

Because it's all files, a brand-new agent can be operational in ~30 minutes by reading four files. The filesystem is the language; the files are the code.

#### How to keep it alive (updating without rotting):

#### A "living agent reference" stays useful only with maintenance discipline:

Routers stay routers. The moment a router file starts containing content instead of pointers, that's the signal to break out a subfolder with its own router.

Identity stays under a page. If it's growing, content is leaking in from a subfolder — move it down.

State is separate from identity. Update state every session; never touch identity to record "what I did today."

Length limits as smoke alarms: routers < ~80 lines, reference files < ~200 lines (split if longer), identity < ~50 lines. When a file blows its limit, that's a structural problem to fix, not a number to ignore.

Match constraints to symptoms, don't load the library. Each workspace's router lists only the one or two protocols likely to bite there — not all of them. Context overload defeats the whole purpose.

#### The discipline (the unbreakable rules):

These are the cultural rules that make the whole thing work. Generalize them to any team:
