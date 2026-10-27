---
type: Concept
id: 05_self_debug_rubber_duck
title: "Teaching Large Language Models to Self-Debug"
source: "arxiv 2304.05128 (Chen et al., 2023)"
tags: [reflection, agents, self-evolution, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Self-Debug — document the error by explaining the code, with no external feedback at all

**Core claim:** an agent can find its own errors with **zero external feedback** — no error messages, no
unit-test results, no human correction. The technique is *rubber duck debugging*: the model explains its own
generated code in natural language, then inspects the explanation for mistakes.

**The documenting mechanism is the explanation itself.** The model reads its output, describes what it does
line by line, and by articulating the intent-vs-actual gap, locates the mismatch. On Spider (text-to-SQL,
where there are no unit tests to verify correctness) explanation alone improved the baseline by 2–3% and
improved hardest-level accuracy by 9%. On TransCoder and MBPP, where unit tests *are* available, improvement
reached 12%.

**Reusing failed predictions is the recurrence lever.** Self-Debugging feeds the failed attempt back in
rather than discarding it. This is what makes it sample-efficient: it matched or outperformed baselines that
generated more than 10× the candidate programs.

**Two failure modes distinguished (this is the subtle part):**
- with **unit tests available** — the error is documented by the environment; the fix loop is grounded;
- **without** them — the only evidence is the model's own explanation, which is unverified. The 2–3% Spider
  gain vs the 12% TransCoder/MBPP gain is the measured cost of an ungrounded diagnosis.

**Why it completes the picture:** this paper is the pure endogenous case. Reflexion needs an evaluator;
AgentDebug needs a taxonomy and counterfactual rollouts; Self-Debug needs nothing but the agent re-reading
its own output. It establishes that the *documentation act* — forcing the agent to articulate what it did —
has standalone value even with no external signal at all, while also showing the ceiling on that value.
