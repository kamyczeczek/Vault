---
type: Concept
id: 01_agent_error_taxonomy_debugging_web_research
title: "Agent Error Taxonomy and Debugging Frameworks (part 2/2)"
source: "agent_error_taxonomy_debugging_web_research.md"
tags: [agentic, agents, context-engineering, memory, planning, reflection]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

**Abstraction ordering:** pattern > rule > instance. Recurrence prevention scales with abstraction level of the stored unit.

---

## Implicit vs Explicit Mistake Learning (Alazraki et al., 2025)

**Paper:** *No Need for Explanations: LLMs can implicitly learn from mistakes in-context* — Lisa Alazraki et al., arXiv:2502.08550, 2025.

**Counterintuitive finding:** LLMs perform better in math reasoning when incorrect answers are shown *without* explicit corrective rationales. Models infer the mistake themselves.

**Why explicit rationales hurt:** they over-constrain the model, limiting the benefits of seeing incorrect answers. Evidence of overfitting to in-context rationales when provided.

**Practical implication:** when injecting error examples into context, prefer raw incorrect answers or minimal failure signatures over fully explained corrections.
