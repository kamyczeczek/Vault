---
type: Concept
title: "A Plan Reuse Mechanism for LLM-Driven Agent"
source: "http://arxiv.org/abs/2512.21309v2"
tags: [research-loop,autonomous-agent]
created: "2026-09-22T18:53:03.385718Z"
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# A Plan Reuse Mechanism for LLM-Driven Agent

**Source:** http://arxiv.org/abs/2512.21309v2
**Authors:**
**Tags:** `research-loop,autonomous-agent`

## Core Methodology & Findings

Integrating large language models (LLMs) into personal assistants, like Xiao Ai and Blue Heart V, effectively enhances their ability to interact with humans, solve complex tasks, and manage IoT devices. Such assistants are also termed LLM-driven agents. Upon receiving user requests, the LLM-driven agent generates plans using an LLM, executes these plans through various tools, and then returns the response to the user. During this process, the latency for generating a plan with an LLM can reach tens of seconds, significantly degrading user experience. Real-world dataset analysis shows that about 30% of the requests received by LLM-driven agents are identical or similar, which allows the reuse of previously generated plans to reduce latency. However, it is difficult to accurately define the similarity between the request texts received by the LLM-driven agent through directly evaluating the original request texts. Moreover, the diverse expressions of natural language and the unstructured format of plan texts make implementing plan reuse challenging. To address these issues, we present and implement a plan reuse mechanism for LLM-driven agents called AgentReuse. AgentReuse leverages the similarities and differences among requests' semantics and uses intent classification to evaluate the similarities between requests and enable the reuse of plans. Experimental results based on a real-world dataset demonstrate that AgentReuse achieves a 93% effective plan reuse rate, an F1 score of 0.9718, and an accuracy of 0.9459 in evaluating request similarities, reducing latency by 93.12% compared with baselines without using the reuse mechanism.

## Algorithm / Pipeline

The methodology involves a structured approach as described in the source material.

## Data Structures

Uses standard data storage and retrieval mechanisms for simulation and analysis.

## Threat Model & Limitations

Potential challenges may include scalability, computational cost, and generalization to unseen scenarios.

## Limitations

Limitations and scope are described in the original publication.
