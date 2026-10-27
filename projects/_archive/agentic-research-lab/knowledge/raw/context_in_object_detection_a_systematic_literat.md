---
type: Concept
title: "Context in object detection: a systematic literature review"
source: "http://arxiv.org/abs/2503.23249v1"
tags: [agentic,research-loop,autonomous,scientific-discovery]
created: "2026-09-22T16:16:14.042867Z"
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Context in object detection: a systematic literature review

**Source:** http://arxiv.org/abs/2503.23249v1
**Authors:** Mahtab Jamali, Paul Davidsson, Reza Khoshkangini, Martin Georg Ljungqvist, Radu-Casian Mihailescu
**Tags:** `agentic,research-loop,autonomous,scientific-discovery`

## Core Methodology & Findings

Context is an important factor in computer vision as it offers valuable information to clarify and analyze visual data. Utilizing the contextual information inherent in an image or a video can improve the precision and effectiveness of object detectors. For example, where recognizing an isolated object might be challenging, context information can improve comprehension of the scene. This study explores the impact of various context-based approaches to object detection. Initially, we investigate the role of context in object detection and survey it from several perspectives. We then review and discuss the most recent context-based object detection approaches and compare them. Finally, we conclude by addressing research questions and identifying gaps for further studies. More than 265 publications are included in this survey, covering different aspects of context in different categories of object detection, including general object detection, video object detection, small object detection, camouflaged object detection, zero-shot, one-shot, and few-shot object detection. This literature review presents a comprehensive overview of the latest advancements in context-based object detection, providing valuable contributions such as a thorough understanding of contextual information and effective methods for integrating various context types into object detection, thus benefiting researchers.

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
