---
type: Concept
title: karpathy_minimalist_agentic_coding_harnesses
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Karpathy Methods and Minimalist Agentic Coding Harnesses

**Source:** https://github.com/karpathy/llm.c / Andrej Karpathy LLM Agent Architecture Notes
**Tags:** `agentic, code-generation, prompt-engineering, tool-use`

## Core Methodology & Findings

### Summary
Andrej Karpathy's philosophy on agentic coding and LLM workflows emphasizes simplicity, file-based interfaces, direct script execution, and avoiding bloated framework abstractions (e.g. heavy LangChain/AutoGPT abstractions) in favor of simple Python loops, grep/read primitives, and clean unit tests.

### Key Contributions to Agentic Research
- **Zero-Abstraction Principle:** Treat the LLM as a function call inside a simple loop, with direct file read/write and bash execution rather than complex state graphs.
- **Test-Driven Iteration:** Agents should write minimal, testable scripts and run them immediately via command-line tools to verify correctness.
- **Context Hygiene:** Keep prompts short, exact, and focused on local file contexts rather than expansive global state.
