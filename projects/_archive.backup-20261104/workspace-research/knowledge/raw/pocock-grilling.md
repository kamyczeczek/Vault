---
type: Concept
title: "Grilling: Design-Tree Frontier Questions Until Shared Understanding"
source: "https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grilling/SKILL.md"
tags: [context-engineering, icm, grilling, planning, reflection]
retrieved: 2026-09-15
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Grilling is the reusable interview primitive behind Pocock's `grill-me`, `grill-with-docs`, `wayfinder`, `triage`, `improve-codebase-architecture`. It interviews relentlessly until every branch of the design tree is visited — nothing left silently assumed; do not act until user confirms shared understanding.

Design tree: every decision branches into decisions hanging off it. Work it in rounds. Frontier = every decision whose prerequisites are already settled (questions you can ask now without guessing answers you haven't heard). Ask the whole frontier in one round, numbered with recommended answer:

❓ Q1 - <title>: <body, choices>
➡️ <recommended>

❓ Q2 ...

Waiting for user answers before next round. Each round reshapes the tree: settled decisions push the frontier outward, unblocking downstream questions; recompute frontier. A question depending on another still-open question belongs to a later round, not this one.

Finding facts is agent's job, never the user's. If a frontier question needs a filesystem/tool fact, dispatch a subagent — don't block the round; only downstream questions wait.

Provenance: mattpocock/skills grilling/SKILL.md retrieved 2026-09-15 via agent-reach Jina.
