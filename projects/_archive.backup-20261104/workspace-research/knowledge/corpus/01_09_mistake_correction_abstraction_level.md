---
type: Concept
id: 01_09_mistake_correction_abstraction_level
title: "Mistake-correction as training signal: lessons must be *reusable*, not just recorded (part 2/2)"
source: "09_mistake_correction_abstraction_level.md"
tags: [agentic, agents, context-engineering, memory, planning]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

**Why this is distinct from grounding.** Huang et al. / CRITIC concern **whether the diagnosis is true**
(needs an external channel). This paper concerns **whether a true diagnosis is useful** (needs the right
representation). Both are required: a grounded but instance-level lesson (`03_agentdebug`'s "fix step `t*` of
*this* trajectory") prevents recurrence only for near-identical tasks; an abstract but ungrounded lesson is
ExpeL's lucky-success insight or Honest Lying's confabulation. Grounding and abstraction are **orthogonal
axes**, and the corpus needs both to describe a complete recurrence-prevention mechanism.

**Design rule derived.** When documenting an error, store the failure **condition** (what about the
situation triggered the mistake), the **reason** (why the chosen action was wrong), and the **correction**
(what to do instead) — as a triple, not as a corrected artifact. A bare "fixed" diff or a bare failure log
each discards one of the two axes that make the lesson apply to the next, different task.

**Cross-references:** `01_reflexion_verbal_reinforcement` (instance-level lesson, bounded memory Ω=1–3),
`02_expel_experiential_insight_extraction` (rule-level, voting ledger), `03_agentdebug_root_cause_attribution`
(root cause via counterfactual — the condition/reason extraction, at trajectory scope),
`06_self_correction_grounding_requirement` (grounding axis), `07_critic_external_tool_verification`
(external channel axis).
