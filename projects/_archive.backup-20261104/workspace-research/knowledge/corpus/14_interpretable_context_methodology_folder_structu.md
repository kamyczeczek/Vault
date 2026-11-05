---
type: Concept
id: 14_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 15/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Interpretable Context Methodology: Folder Structure as Agent Architecture•15
specific regulatory requirements is a legal question this paper does not attempt to answer, but the structural
alignment is worth noting.
5.4 Implications for Intelligent System Design
The discussion so far has focused on how ICM structures the human side of human-AI interaction: edit surfaces,
review gates, observability. But the architecture also has implications for how the intelligent system itself performs,
and these are worth examining.
The core mechanism is context scoping. By delivering different context to the same model at each stage, ICM
changes the task the model is performing. A model that receives research instructions, source material, and a
topic brief behaves differently from the same model receiving a script template, a voice guide, and a research
summary. The model’s capabilities do not change between stages. What changes is the information it has available
when generating output. This is context engineering in practice: the performance of the system depends on what
context is delivered, in what structure, and at what moment.
The Layer 3/Layer 4 distinction adds a further dimension. Reference material (Layer 3) and working artifacts
(Layer 4) ask different things of the model. Reference material says: here are the rules, follow them. Working
artifacts say: here is the input, transform it. Delivering these as structurally separate context, rather than mixing
them in a single undifferentiated prompt, gives the model clearer signals about which information constrains its
behavior and which information it should act on. Whether this structural separation measurably improves output
quality compared to a flat context of equivalent content is an open empirical question, but early practitioner
experience suggests that stages where reference and working material are clearly separated produce more
consistent adherence to style and format guidelines.
This raises a question about the relationship between context structure and output quality. In early use, a
pattern emerged: stages with tightly scoped context (clear instructions, limited reference material, a specific
output format) produced more consistent results than stages with broad context (open-ended instructions, large
volumes of reference material, loosely defined output expectations). This is consistent with the “lost in the middle”
findings [25] and with the chain-of-thought literature showing that decomposed tasks outperform monolithic
ones [27], but it suggests something more specific. The structure of the context delivery, how information is
organized and bounded, may matter as much as the content of the context itself. ICM’s folder-based scoping
enforces this structure by default: each stage folder contains only what that stage needs, and the boundaries are
visible and editable.
There are open questions here that the current work does not answer. First, does the five-layer hierarchy
(workspace identity, task routing, stage contracts, reference material, working artifacts) generalize across model
families, or is it tuned to the specific attention patterns of the models tested? The protocol is designed to be
model-agnostic (Section 4.1), but all current testing has been conducted on a single model family. Cross-model
evaluation, running the same workspace on Claude, GPT, Gemini, and open-weight models such as Llama, is a
clear next step. This paper scopes that question as future work because the present contribution is the architectural
pattern and its interaction properties, not a model-specific performance claim. Second, as context windows grow
larger, does selective loading become less important? If a model can reliably attend to 200,000 tokens without
degradation, the engineering argument for ICM’s scoping weakens, though the human-interaction arguments
(observability, editability, review gates) remain. Third, how sensitive is stage output quality to the ordering and
formatting of context within a layer? The current protocol specifies what files a stage should load but does not
prescribe the order in which they appear in the context window. Whether ordering matters at the scale of ICM’s
typical context sizes (2,000 to 8,000 tokens per stage) is an empirical question worth investigating.
These questions point toward a research program that sits at the intersection of context engineering and
interaction design: understanding how the structure of information delivery to language models affects both the
