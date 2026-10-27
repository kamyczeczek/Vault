---
type: Concept
title: 07_critic_external_tool_verification
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
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

**Design rules derived.**
1. The critique must be **observable output from the environment**, concatenated verbatim into the context —
   not the model's summary of what a tool would say. This is what makes the correction evidence rather than
   opinion; it is also what makes the loop reproducible.
2. Corrections should be **targeted at known-bad outputs**. A blanket revise-everything policy pays the
   oracle gap; a cheap external gate that decides *whether to correct* recovers most of the headroom.
3. Iterate with a stop condition on unchanged output, not a fixed round count — unbounded revision rounds
   re-expose correct answers to critique noise.

**Why it completes the picture.** Reflexion documents errors into memory; AgentDebug finds the root cause;
Honest Lying shows stored diagnoses can be confabulated; Huang et al. shows ungrounded correction is
net-negative. CRITIC is the constructive counterpart: **the environment, not the agent, is the author of the
critique**, and the ablation measures exactly what that is worth.
