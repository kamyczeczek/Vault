---
type: Concept
id: 00_07_critic_external_tool_verification
title: "CRITIC — verify-then-correct with external tools: the ablation that quantifies grounding (part 1/2)"
source: "07_critic_external_tool_verification.md"
tags: [agentic, agents, context-engineering, memory, prompt-engineering]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# CRITIC — verify-then-correct with external tools: the ablation that quantifies grounding

**Core claim:** self-correction works reliably when the critique is produced by **interacting with external
tools** rather than by the model reasoning about its own output. CRITIC supplies the missing half of the
corpus's grounding story: not the claim that external feedback helps (Huang et al. establishes the negative
side), but the **measured size of the gap** between tool-grounded and self-generated critiques.

**Paper:** *CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing* — Gou, Shao,
Gong, Shen, Yang, Duan, Chen (Microsoft Research Asia / Tsinghua), arXiv:2305.11738v2, ICLR 2024.

**Mechanism (Algorithm 1).** `generate → verify-with-tools → correct`, iterable to a fixed `n`:
1. The model produces an initial output from parametric knowledge.
2. It interacts with text-to-text external tools — **Google search** for factual verification, **code
   interpreter** for program correctness — to produce critiques `c_i`. Tool outputs are concatenated into the
   critique text; they are not paraphrased by the model.
3. It revises conditioned on `input ⊕ previous output ⊕ critique`.
4. Stop when the critique indicates correctness, or `n` rounds elapse (`n=3`; early stop if the answer is
   unchanged across two consecutive corrections).

**The ablation — `CRITIC w/o Tool`.** Remove the search API; the model generates the "evidence" itself with
the prompt otherwise unchanged. Result: the model's own critiques contribute **−0.03 and +2.33 F1** on the
two LLMs tested. On one LLM the self-critique version scores *below the initial output*. This is the same
effect as Huang et al.'s intrinsic self-correction, isolated inside an otherwise-identical pipeline — the
single variable is whether the critique originates outside the model.

**With tools restored (ChatGPT, free-form QA).**
- CRITIC: **+7.7** average F1 across AmbigNQ / TriviaQA / HotpotQA over the CoT baseline.
- CRITIC* (oracle — correction applied only to samples that are actually wrong): **+12.4** F1 average.
- The oracle gap quantifies wasted revisions: correcting already-correct answers moves them toward the
  critique's errors. **Knowing which answers to correct is half the gain** — an untargeted correction loop
  spends most of its budget damaging correct outputs.
- Outperforms ReAct (retrieval only, no verify-correct loop) by 5.1–8.2 average F1 on two LLMs.
- Additional domain: **79.2% reduction in toxicity probability** on toxicity reduction — the grounding
  requirement generalizes beyond factual correctness to safety constraints.

**Tool choice is task-dependent and must be matched to the failure mode being prevented.** QA → search engine
(grounding facts); code → interpreter (grounding execution); toxicity → an external detector. A tool that
cannot actually observe the failure supplies no evidence and the loop collapses to intrinsic self-correction.
