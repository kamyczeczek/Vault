---
type: Concept
id: 160_icm_knowledge_big
title: "ICM_knowledge.md (part 161/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Filescope (the recursive principle): every router/identity file describes only its own folder. A subfolder's detail lives in the subfolder's own file, never copied up into the parent. So an agent entering the "monitoring" subfolder loads 30 lines of monitoring rules — not 400 lines of everything in the project. This is the single trick that keeps each step small and cheap.

#### How a workflow actually runs: the Unix-pipe principle:

A workflow is numbered stages that hand off through a single channel.

01-research/output/ → read by 02-draft

02-draft/output/ → read by 03-review

03-review/output/ → delivered

#### Three iron rules:

The handoff channel is output/, nothing else. Stage 2 reads stage 1's output/ folder — never stage 1's scratch/working files.

Adjacent only. Stage 3 reads stage 2, never stage 1. If stage 3 needs something from stage 1, stage 2 must copy it forward into its own output. ("Embed, don't reach.")

Config is always available. The global _config/ (voice rules, standards) is like system settings — any stage may read it without "breaking the chain."

Because each stage only cares about the shape of the output it receives, you can rewrite stage 1 entirely without touching stage 2. Stages are independently testable and swappable, exactly like Unix pipes (cmd1 | cmd2 | cmd3).

Each stage is defined by a stage contract — just three sections: Inputs (what to load and why), Process (ordered steps), Outputs (what to write, where). That's it. Same contract shape regardless of subject, tool, or AI.

Design tip: write each stage's output to be interrogated later, not just consumed once. A well-structured output can be pulled into a fresh session weeks later and questioned ("show me where the earlier step flagged X"). A raw dump can't.

#### How to build a specialist (a single expert agent):

A "specialist" is a folder that turns an AI into one focused expert. The discipline is a five-file pattern:

identity — Holds a philosophy, not a persona. Named principles with a defensible reason to exist. The test: "I catch what the writer missed, because writers can't review their own work" (philosophy) — not "I'm a helpful reviewer" (persona).

rules — Behavioral constraints only: how it responds, what it never does, how it self-corrects. The test: every rule must be falsifiable — a judge could read one output and mark it pass/fail. "Be thorough" fails this test; "every finding must state where, how to reproduce, and why — or be discarded" passes.

reference — The protocols, schemas, templates, ordered question-lists. The test: if a section describes a sequence or a schema rather than a behavior, it belongs here, not in rules.

workflow — The resumability layer: a Pick-Up state (how to resume mid-task) and a Drop state (done-when criteria + where to route next). The test: a new session can inherit a half-finished job and continue.
