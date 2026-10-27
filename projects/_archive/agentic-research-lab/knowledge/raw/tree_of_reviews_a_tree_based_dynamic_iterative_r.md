---
type: Concept
title: "Tree of Reviews: A Tree-based Dynamic Iterative Retrieval Framework for Multi-hop Question Answering"
source: "http://arxiv.org/abs/2404.14464v1"
tags: [agentic, scientific-discovery]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Tree of Reviews: A Tree-based Dynamic Iterative Retrieval Framework for Multi-hop Question Answering

**Source:** http://arxiv.org/abs/2404.14464v1
**Tags:** `agentic, scientific-discovery`

## Core Methodology & Findings

**Authors:** Li Jiapeng, Liu Runze, Li Yabo, Zhou Tong, Li Mingling

### Abstract
Multi-hop question answering is a knowledge-intensive complex problem. Large Language Models (LLMs) use their Chain of Thoughts (CoT) capability to reason complex problems step by step, and retrieval-augmentation can effectively alleviate factual errors caused by outdated and unknown knowledge in LLMs. Recent works have introduced retrieval-augmentation in the CoT reasoning to solve multi-hop question answering. However, these chain methods have the following problems: 1) Retrieved irrelevant paragraphs may mislead the reasoning; 2) An error in the chain structure may lead to a cascade of errors.   In this paper, we propose a dynamic retrieval framework called Tree of Reviews (ToR), where the root node is the question, and the other nodes are paragraphs from retrieval, extending different reasoning paths from the root node to other nodes. Our framework dynamically decides to initiate a new search, reject, or accept based on the paragraphs on the reasoning paths. Compared to related work, we introduce a tree structure to handle each retrieved paragraph separately, alleviating the misleading effect of irrelevant paragraphs on the reasoning path; the diversity of reasoning path extension reduces the impact of a single reasoning error on the whole. We conducted experiments on three different multi-hop question answering datasets. The results show that compared to the baseline methods, ToR achieves state-of-the-art performance in both retrieval and response generation. In addition, we propose two tree-based search optimization strategies, pruning and effective expansion, to reduce time overhead and increase the diversity of path extension. We will release our code.
