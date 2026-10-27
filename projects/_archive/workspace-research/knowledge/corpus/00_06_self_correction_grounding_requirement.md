---
type: Concept
id: 00_06_self_correction_grounding_requirement
title: "Ungrounded self-correction is not neutral — it measurably degrades performance (part 1/2)"
source: "06_self_correction_grounding_requirement.md"
tags: [agentic, agents, memory, planning, prompt-engineering, reflection]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Ungrounded self-correction is not neutral — it measurably degrades performance

**Core claim (the counter-evidence the corpus needs):** intrinsic self-correction — an LLM critiquing and
revising its own output with **no external feedback** — does not merely fail to help. On reasoning tasks it
**degrades** performance. This inverts the naive reading of Reflexion (`01_reflexion_verbal_reinforcement`):
the documentation act has standalone value, but an *unverified* diagnosis is worse than no diagnosis, because
the revised answer is conditioned on a critique that may be wrong with the same confidence it applies to a
correct one.

**Paper:** *Large Language Models Cannot Self-Correct Reasoning Yet* — Huang, Chen, Mishra, Zheng, Yu, Song,
Zhou (Google DeepMind), arXiv:2310.01798, Oct 2023.

**Why it fails — the verification asymmetry.** The authors' mechanism: a model that cannot reliably solve a
problem also cannot reliably judge whether its solution is correct, because judgement is the same
capability applied to its own output. Self-correction therefore lacks an independent error signal. Where the
critique and the error come from the same distribution, a confident-sounding critique carries no evidence
about its own correctness. The failure is not effort or prompt design; it is the absence of an independent
ground-truth channel.

**Setup.** Intrinsic self-correction applied to three reasoning benchmarks (GSM8K math, CommonSenseQA, and a
third reasoning task) across GPT-4 and PaLM-2. No tools, no unit tests, no external judge — the model
generates an answer, critiques it, and revises.

**Result.** Accuracy **drops** after intrinsic self-correction rounds, versus the initial answer. The drop is
the finding: a correction loop with no external grounding actively moves the model away from its initial
(better) answer, because the revision is driven by a critique that is itself unverified.

**The ceiling this puts on the corpus's positive results.**
- `05_self_debug_rubber_duck` (Self-Debug, 2304.05128): **+2–3%** on Spider where there is *no* verifier
  (explanation only), versus **+12%** on TransCoder/MBPP where unit tests exist. Huang et al. explains the
  4× gap — the Spider gain rides the small end of what endogenous articulation can do, and Self-Debug's
  own measured delta is the same effect this paper names as a failure mode.
- `04_honest_lying_memory_confabulation` (2605.29463): confabulated reflections persisted across trials.
  Same mechanism, larger dose — the unverified critique gets *stored* and re-read, compounding instead of
  just degrading one answer.
- `01_reflexion_verbal_reinforcement` (2303.11366) requires an evaluator `M_e` external to the actor for
  exactly this reason; where `M_e` is the same model self-evaluating, it inherits this failure mode.
