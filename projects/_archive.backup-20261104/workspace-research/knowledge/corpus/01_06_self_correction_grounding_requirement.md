---
type: Concept
id: 01_06_self_correction_grounding_requirement
title: "Ungrounded self-correction is not neutral — it measurably degrades performance (part 2/2)"
source: "06_self_correction_grounding_requirement.md"
tags: [agentic, agents, memory, planning, prompt-engineering, reflection]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

**Design rule derived.** Every self-correction or error-logging mechanism needs an **external grounding
channel** — unit tests, tool feedback, a judge distinct from the actor, or environment-derived signal. A
correction loop grounded only in the agent's own reasoning is a **liability**, not a neutral fallback.
Practical implication: when you cannot supply an external channel, prefer the initial answer over a
self-critique-revised one.
