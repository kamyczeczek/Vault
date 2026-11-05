---
type: Concept
title: "Agent Error Taxonomy and Debugging Frameworks"
source: "web: https://arxiv.org/abs/2509.25370 + https://arxiv.org/abs/2310.20689 + https://aclanthology.org/2024.findings-emnlp.46"
tags: [agentic, agents, reflection, planning, memory, prompt-engineering]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Agent Error Taxonomy and Debugging Frameworks

## AgentErrorBench and AgentDebug (Zhu et al., 2025)

**Paper:** *Where LLM Agents Fail and How They can Learn From Failures* — Kunlun Zhu et al., arXiv:2509.25370, 2025.

**Core contribution:** a modular failure taxonomy and a debugging framework that isolates root-cause failures and provides corrective feedback.

### AgentErrorTaxonomy
Classifies agent failures into five modules:
- **Memory** — retrieval, persistence, eviction errors
- **Reflection** — ungrounded self-correction, confabulation, missing eviction
- **Planning** — plan-drift, incomplete decomposition, horizon collapse
- **Action** — tool misuse, parameter errors, sequencing faults
- **System** — liveness, consistency, resource exhaustion

**Why it matters:** current systems lack a comprehensive modular understanding of agent error, so they cannot detect cascading failures where one root-cause error propagates through subsequent decisions.

### AgentErrorBench
First dataset of systematically annotated failure trajectories from ALFWorld, GAIA, and WebShop. Each trajectory is annotated at the step level with failure module and root-cause attribution.

### AgentDebug framework
1. **Detect** — classify each error by taxonomy module
2. **Attribute** — identify the earliest step whose correction prevents final failure (counterfactual substitution)
3. **Correct** — generate targeted feedback for the root-cause step only, not every symptom

**Results:** +24% all-correct accuracy, +17% step accuracy, up to +26% relative improvement in task success across benchmarks.

**Key insight:** "Task division is already HTN-shaped and one-level adaptive, but route.py's ADAPT split triggers on cardinality while ADAPT triggers on the executor's observed inability. The proxy is wrong in the case that matters: a route returning many wrong chunks never triggers a split."

---

## LEMA: Learning From Mistakes Makes LLM Better Reasoner (An et al., 2023)

**Paper:** *Can LLMs Learn From Mistakes? An Empirical Study on Reasoning Tasks* — Shengnan An et al., EMNLP 2024 Findings, doi:10.18653/v1/2024.findings-emnlp.46.

**Method:** build mistake-correction datasets. GPT-4 identifies and corrects mistakes inside inaccurate chain-of-thought traces, producing `(wrong CoT, mistake location, corrected CoT)` triples. Fine-tune open-source LLMs on these triples.

**Three findings:**
1. LLMs can learn from mistakes — fine-tuning on mistake-correction data improves CoT reasoning accuracy.
2. Mistake-correction data beats ordinary CoT data for the same budget — it encodes *explanations and reasons for potential mistakes*, knowledge that correct-only data never contains.
3. Correction-centric evolution iteratively refining the mistake-correction data itself increases gains further.

**Transferable unit:** the `(failure condition → reason → correction)` triple, not the failed trajectory and not the corrected answer.

**Abstraction ordering:** pattern > rule > instance. Recurrence prevention scales with abstraction level of the stored unit.

---

## Implicit vs Explicit Mistake Learning (Alazraki et al., 2025)

**Paper:** *No Need for Explanations: LLMs can implicitly learn from mistakes in-context* — Lisa Alazraki et al., arXiv:2502.08550, 2025.

**Counterintuitive finding:** LLMs perform better in math reasoning when incorrect answers are shown *without* explicit corrective rationales. Models infer the mistake themselves.

**Why explicit rationales hurt:** they over-constrain the model, limiting the benefits of seeing incorrect answers. Evidence of overfitting to in-context rationales when provided.

**Practical implication:** when injecting error examples into context, prefer raw incorrect answers or minimal failure signatures over fully explained corrections.
