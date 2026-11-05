---
type: Concept
title: "FactPICO: Factuality Evaluation for Plain Language Summarization of Medical Evidence"
source: "http://arxiv.org/abs/2402.11456v2"
tags: [prompt-engineering]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# FactPICO: Factuality Evaluation for Plain Language Summarization of Medical Evidence

**Source:** http://arxiv.org/abs/2402.11456v2
**Tags:** `prompt-engineering`

## Core Methodology & Findings

# FactPICO: Factuality Evaluation for Plain Language Summarization of Medical Evidence

- source: http://arxiv.org/abs/2402.11456v2
- authors: , , ,

## Abstract
Plain language summarization with LLMs can be useful for improving textual accessibility of technical content. But how factual are these summaries in a high-stakes domain like medicine? This paper presents FactPICO, a factuality benchmark for plain language summarization of medical texts describing randomized controlled trials (RCTs), which are the basis of evidence-based medicine and can directly inform patient treatment. FactPICO consists of 345 plain language summaries of RCT abstracts generated from three LLMs (i.e., GPT-4, Llama-2, and Alpaca), with fine-grained evaluation and natural language rationales from experts. We assess the factuality of critical elements of RCTs in those summaries: Populations, Interventions, Comparators, Outcomes (PICO), as well as the reported findings concerning these. We also evaluate the correctness of the extra information (e.g., explanations) added by LLMs. Using FactPICO, we benchmark a range of existing factuality metrics, including the newly devised ones based on LLMs. We find that plain language summarization of medical evidence is still challenging, especially when balancing between simplicity and factuality, and that existing metrics correlate poorly with expert judgments on the instance level.

## Research question context
Deposited 2026-10-01 for the open question: agent output in
plain, comprehensible language (style mechanisms vs meter choice).
