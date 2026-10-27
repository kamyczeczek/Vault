---
type: Concept
title: "Learning Recovery Strategies for Dynamic Self-healing in Reactive Systems"
source: "http://arxiv.org/abs/2401.12405v1"
tags: [research-loop,autonomous-agent]
created: "2026-09-22T18:32:31.859255Z"
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Learning Recovery Strategies for Dynamic Self-healing in Reactive Systems

**Source:** http://arxiv.org/abs/2401.12405v1
**Authors:**
**Tags:** `research-loop,autonomous-agent`

## Core Methodology & Findings

Self-healing systems depend on following a set of predefined instructions to recover from a known failure state. Failure states are generally detected based on domain specific specialized metrics. Failure fixes are applied at predefined application hooks that are not sufficiently expressive to manage different failure types. Self-healing is usually applied in the context of distributed systems, where the detection of failures is constrained to communication problems, and resolution strategies often consist of replacing complete components. Our proposal targets complex reactive systems, defining monitors as predicates specifying satisfiability conditions of system properties. Such monitors are functionally expressive and can be defined at run time to detect failure states at any execution point. Once failure states are detected, we use a Reinforcement Learning-based technique to learn a recovery strategy based on users' corrective sequences. Finally, to execute the learned strategies, we extract them as COP variations that activate dynamically whenever the failure state is detected, overwriting the base system behavior with the recovery strategy for that state. We validate the feasibility and effectiveness of our framework through a prototypical reactive application for tracking mouse movements, and the DeltaIoT exemplar for self-healing systems. Our results demonstrate that with just the definition of monitors, the system is effective in detecting and recovering from failures between 55%-92% of the cases in the first application, and at par with the predefined strategies in the second application.

## Algorithm / Pipeline

The methodology involves a structured approach as described in the source material.

## Data Structures

Uses standard data storage and retrieval mechanisms for simulation and analysis.

## Threat Model & Limitations

Potential challenges may include scalability, computational cost, and generalization to unseen scenarios.

## Limitations

constrained to communication problems, and resolution strategies often consist of replacing complete components. Our proposal targets complex reactive
