---
type: Concept
title: "Harness Engineering for Agentic AI Coding Tools: An Exploratory Study"
source: "http://arxiv.org/abs/2602.14690v5"
tags: [agentic, scientific-discovery]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Harness Engineering for Agentic AI Coding Tools: An Exploratory Study

**Source:** http://arxiv.org/abs/2602.14690v5
**Tags:** `agentic, scientific-discovery`

## Core Methodology & Findings

**Authors:** Matthias Galster, Seyedmoein Mohsenimofidi, Jai Lal Lulla, Muhammad Auwal Abubakar, Christoph Treude

### Abstract
Agentic AI coding tools increasingly automate software development tasks. Developers can configure these tools through versioned repository-level artifacts such as Markdown and JSON files. We present a systematic analysis of configuration mechanisms for agentic AI coding tools, covering Claude Code, GitHub Copilot, Cursor, Gemini, and Codex. We identify eight configuration mechanisms spanning from static context to executable and external integrations and, in an empirical study of 2,853 GitHub repositories, examine whether and how they are adopted, with a detailed analysis of Context Files, Skills, and Subagents. First, Context Files dominate the configuration landscape and are often the sole mechanism in a repository, with AGENTS$.$md emerging as an interoperable standard across tools. Second, few repositories adopt advanced mechanisms such as Skills and Subagents. Skills predominantly rely on static instructions rather than executable scripts. Third, distinct configuration practices are forming around different tools, with Claude Code users employing the broadest range of mechanisms. These findings establish an empirical baseline for understanding how developers configure agentic tools, suggest that AGENTS$.$md serves as a natural starting point, and motivate longitudinal and experimental research on how configuration strategies evolve and affect agent performance.
