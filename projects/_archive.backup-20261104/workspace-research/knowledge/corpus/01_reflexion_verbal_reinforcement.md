---
type: Concept
id: 01_reflexion_verbal_reinforcement
title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
source: "arxiv 2303.11366 (Shinn et al., NeurIPS 2023)"
tags: [reflection, agents, memory, self-evolution, benchmark, planning]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Reflexion — learn from failures by verbal reinforcement instead of weight updates

**Core claim:** an agent can learn from its own failures without any gradient update, by converting a sparse
environment signal into natural-language feedback and storing that feedback in an episodic memory buffer.
The paper calls this "verbal reinforcement": the *policy* is not the weights but the pairing
`θ = {M_a, mem}` — the actor model plus its memory of prior reflections.

**The four-part loop (Algorithm 1):**
1. Actor `M_a` generates a trajectory `τ_t` in the environment.
2. Evaluator `M_e` scores it (`r_t = M_e(τ_t)`), which may be a binary success flag, a heuristic, or an LLM judge.
3. Self-reflection model `M_sr` reads `{τ_t, r_t}` and produces a verbal summary `sr_t`.
4. `sr_t` is appended to `mem`, which conditions the next trial.

The mechanism that actually prevents recurrence: the reflection does credit assignment in language. Given a
binary failure signal plus the trajectory, the reflection model states *which* action `a_i` was wrong, what
`a_i'` should have been taken instead, and stores that. On the next trial the agent reads `mem` and chooses
`a_i'`. Recurrence prevention is therefore a retrieval problem, not a learning problem — the lesson is
looked up rather than learned into weights.

**Documenting the error is where the leverage is.** Reflexion explores three evaluator tiers, ordered by how
much they document: binary environment feedback (least — a bare success/fail), predefined heuristics for
common failure cases, and self-evaluation (an LLM judge, or self-written unit tests for code). Documented
signals — heuristics and self-evaluation — beat bare binary feedback because they tell the reflection model
*what* failed, not just *that* it failed.

**Memory is bounded to 1–3 stored experiences (Ω)** to fit the context window. This is the paper's own
admitted ceiling: reflection is valuable but short-ranged, and it cannot accumulate lessons across tasks.

**Results:** +22% absolute over baselines on AlfWorld sequential decision-making (12 iterative steps), +20%
HotPotQA reasoning, +11% HumanEval code; 91% pass@1 on HumanEval vs GPT-4's 80%.

**Documented weakness:** depends entirely on the LLM's self-evaluation quality; no formal guarantee of
success. The authors note reflection improves as base models improve — the failure mode is not the
mechanism but misdiagnosis by the reflector.
