---
type: Concept
id: 00_intelligent_skill_selection_workflow
title: "Intelligent Automatic Skill Selection Workflow for Agentic Research Workspaces"
source: "intelligent_skill_selection_workflow.md"
tags: [agentic, workflow-evolution, prompt-engineering, tool-use]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---
# Intelligent Automatic Skill Selection Workflow for Agentic Research Workspaces

## Core Methodology & Findings
To prevent manual skill overhead and ensure optimal task execution, agents must route incoming user intents through a deterministic, tag-indexed skill router (`skills/SKILLS.md` or automated skill selector script).
- **Intent-to-Skill Mapping:** Binds task classifications (e.g., literature expansion, code generation, test-driven validation, graph building) directly to `.omp` skills.
- **Automated Skill Triggering:** Inspects task semantics and automatically injects skill instructions into agent sub-tasks without requiring manual user invocation.
