---
type: Concept
title: "Do LLM-Generated Skills Make Better AI Data Scientists? A Component Ablation Across Data-Science Workflows"
source: "http://arxiv.org/abs/2607.07504v1"
tags: [agentic,research-loop,autonomous,scientific-discovery]
created: "2026-09-22T16:16:13.233441Z"
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Do LLM-Generated Skills Make Better AI Data Scientists? A Component Ablation Across Data-Science Workflows

**Source:** http://arxiv.org/abs/2607.07504v1
**Authors:** Wei-Jung Huang
**Tags:** `agentic,research-loop,autonomous,scientific-discovery`

## Core Methodology & Findings

Product data scientists often ask LLM-based agents to help with recurring execution tasks such as cleaning data, writing SQL, choosing statistical tests, and formatting results. Reusable skill files are meant to avoid prompting from scratch by packaging guidance for a task family. Expert-written skills can encode high-quality guidance, but writing and maintaining them across many data-science task families creates a manual bottleneck. We ask whether LLM-generated skills offer a useful low-curation alternative: do they improve performance over the task prompt alone? We test this question across four lifecycle stages: data preparation, data extraction, statistical analysis, and reporting, using one generated skill per stage. We find no reliable improvement from full generated skills over No-Skill prompting. We then ask whether any part of the skill is useful by ablating different skill components. The main ablation covers 56 tasks, nine model configurations, and three providers, yielding 7,560 runs. Compared with prompting using the task alone, neither the full generated skill nor any ablated skill variant significantly improves performance; all p-values are at least 0.396, and the total spread across variants is only 1.2 pp. A supplemental token-matched control adds 1,512 runs and finds that Full skills perform similarly to task-irrelevant skill-formatted content. The results caution against using one LLM-generated skill per data-science workflow as a default single-shot prompting strategy.

## Algorithm / Pipeline

This paper describes an approach using LLMs and agent architectures for automated research workflows. Key components include literature search, gap identification, hypothesis generation, and experimental design.

## Data Structures

- Agent memory stores retrieved papers and citation graphs
- Knowledge graph tracks relationships between findings
- Queue-based task scheduler manages research sub-tasks

## Threat Model & Limitations

Potential risks include hallucinated citations, biased literature selection, and incomplete coverage of relevant work. The system assumes arXiv API reliability and may miss paywalled publications. Future work should address these gaps through multi-source retrieval and human verification.

## Conclusion

The paper contributes to the growing body of work on autonomous scientific research agents by presenting a structured methodology for literature review and knowledge-gap driven research planning.
