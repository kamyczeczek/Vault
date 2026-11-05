---
type: Concept
id: 00_pocock_writing_for_agents
title: "pocock-writing-for-agents.md"
source: "pocock-writing-for-agents.md"
tags: [icm, context-engineering, writing-for-agents, planning, agentic, agents]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Writing for agents — skills, AGENTS.md/CLAUDE.md, any doc an agent consumes — is the same levers regardless of packaging. Model takes same process every run, not same output.

Context pointer: reference in agent's context naming out-of-context material + condition to reach it. Skill description or AGENTS.md line naming a doc are the same object. Wording — not target — decides when agent reaches it. Weak pointer to must-have target is a variance bug: sharpen wording first, inline only if sharpening fails. Pointer states what material is + branches triggering it; front-load leading word, one trigger per branch, cut identity already in body.

Two loads: context load (always-loaded material spending tokens/attention every turn — AGENTS.md line, skill description) vs cognitive load (which docs exist, when to reach — human as index; price of agency, spend where judgment matters).

Information ladder: in-file step (ordered actions) > in-file reference (rules consulted on demand) > disclosed reference (separate file behind pointer, loaded only when fires). Progressive disclosure moves down the ladder to protect hierarchy — not just token optimization. Co-location: keep definition/rules/caveats under one heading. Sprawl: document too long even when live — attention thins; fix via ladder.

Steps end on completion criteria — clarity (agent can tell done vs not-done) and demand (how much required). Strongest are checkable + exhaustive. Split only when cut earns it: by sequence (post-completion steps tempt premature completion) or by invocation. Leading words (lesson, tracer bullets, red) collapse distributed meaning into one pretrained token — recruit priors. Negation is an elephant trap: ban half-reads as instruction; state positive target instead. Pruning: single source of truth, duplication costs; environment is source of truth too (package.json) — document is cache, cache only what lookup can't find; hunt no-ops sentence-by-sentence.

Provenance: mattpocock/skills writing-for-agents/SKILL.md retrieved 2026-09-15.
