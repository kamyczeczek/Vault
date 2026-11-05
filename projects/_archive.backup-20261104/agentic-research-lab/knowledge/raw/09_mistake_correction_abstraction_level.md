---
type: Concept
title: 09_mistake_correction_abstraction_level
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Mistake-correction as training signal: lessons must be *reusable*, not just recorded

**Core claim:** an error becomes durable prevention only when the correction is extracted into a form that
**generalizes beyond the trajectory it came from**. Recording "this trajectory failed at step k" prevents
nothing on its own — the question is whether the failure converts into transferable knowledge. This paper
supplies the positive counterpart to the grounding requirement: with the right representation, mistakes
carry **more** transferable knowledge than correct solutions do.

**Paper:** *Can LLMs Learn From Mistakes? An Empirical Study on Reasoning Tasks* — An, Ma, Cai, Lin, Zheng,
Lou, Chen (Xi'an Jiaotong / Microsoft Research), Findings of EMNLP 2024, pp. 833–854,
doi:10.18653/v1/2024.findings-emnlp.46.

**Method.** The authors build **mistake-correction datasets**: GPT-4 identifies and corrects mistakes inside
inaccurate chain-of-thought traces, producing `(wrong CoT, mistake location, corrected CoT)` triples. These
are then used to **fine-tune** open-source LLMs — a parametric path, distinct from the in-context memory of
Reflexion/ExpeL, so the comparison isolates *representation*, not *where the knowledge lives*.

**Three findings, and the second one is the one that matters here.**
1. **LLMs can learn from mistakes** — fine-tuning on mistake-correction data improves CoT reasoning
   accuracy. Mistakes are usable training signal, not noise to be filtered out.
2. **Mistake-correction data beats ordinary CoT data** for the same budget. Because: it encodes the
   *explanations and reasons for potential mistakes*, knowledge that correct-only data never contains. A
   correct solution demonstrates one way to be right; a corrected mistake documents an entire **failure
   mode** — the conditions under which the model tends to go wrong. This is the mechanism-level reason to
   document errors: they are the only training signal that carries negative knowledge.
3. **Correction-centric evolution** (iteratively refining the mistake-correction data itself) increases the
   gains further — the quality of the extracted lesson compounds under refinement, like ExpeL's voting.

**What makes a lesson transfer (the general principle).** The transferable unit is not the failed trajectory
and not the corrected answer — it is the **(failure condition → reason → correction) triple**. Reflexion's
`sr_t` is instance-level ("action `a_i` was wrong, take `a_i'`"); ExpeL's insights are rule-level; this
paper's triples are pattern-level. Recurrence prevention scales with the **abstraction level** of the stored
unit, and the empirical ordering across the corpus is consistent: pattern > rule > instance.

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
